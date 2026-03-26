"""Coordinator agent using LangGraph for orchestration."""

import ast
import time
from collections import defaultdict
from typing import Any, Callable

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import Annotated, TypedDict
import operator

from backend.models import (
    AgentCompletedEvent,
    AgentDelegatedEvent,
    AgentErrorEvent,
    AgentResult,
    AgentStartedEvent,
    AgentType,
    BaseEvent,
    Finding,
    FindingsConsolidatedEvent,
    FinalReportEvent,
    PlanCreatedEvent,
    Severity,
)
from backend.agents.base import BaseAgent


class CoordinatorState(TypedDict):
    """State for coordinator workflow."""

    code: str
    context: dict[str, Any]
    code_metadata: dict[str, Any]
    plan_steps: list[dict[str, Any]]
    specialist_results: Annotated[list[AgentResult], operator.add]  # Accumulates results
    consolidated_findings: list[Finding]
    conflicts_resolved: int
    error: str | None


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent using LangGraph for orchestration.

    Workflow:
    1. Parse code structure
    2. Create execution plan
    3. Delegate to specialist agents (parallel)
    4. Consolidate findings
    5. Generate final report
    """

    def __init__(self, specialists: list[BaseAgent] | None = None):
        """
        Initialize the coordinator agent.

        Args:
            specialists: List of specialist BaseAgent instances to delegate to.
        """
        super().__init__(AgentType.COORDINATOR)
        self.specialists = specialists or []

    async def analyze(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[BaseEvent], Any],
    ) -> AgentResult:
        """
        Orchestrate code review using LangGraph.

        Args:
            code: Python code to analyze
            context: Shared context (metadata, previous findings, etc.)
            event_callback: Callback to emit events

        Returns:
            AgentResult with consolidated findings
        """
        start_time = time.time()

        try:
            # Emit agent started
            await event_callback(
                AgentStartedEvent(agent_id=self.agent_id, data={})
            )

            # Build and compile the graph with event_callback captured in closure
            graph = self._build_graph(event_callback)
            compiled_graph = graph.compile()

            # Invoke the graph
            result = await compiled_graph.ainvoke(
                {
                    "code": code,
                    "context": context,
                    "code_metadata": {},
                    "plan_steps": [],
                    "specialist_results": [],
                    "consolidated_findings": [],
                    "conflicts_resolved": 0,
                    "error": None,
                }
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Emit agent completed
            await event_callback(
                AgentCompletedEvent(
                    agent_id=self.agent_id,
                    data={
                        "findings_count": len(result["consolidated_findings"]),
                        "duration_ms": duration_ms,
                    },
                )
            )

            return AgentResult(
                agent_id=self.agent_id,
                findings=result["consolidated_findings"],
                errors=[result["error"]] if result["error"] else [],
                metadata={
                    "code_lines": result["code_metadata"].get("lines", 0),
                    "functions": result["code_metadata"].get("functions", 0),
                    "classes": result["code_metadata"].get("classes", 0),
                    "conflicts_resolved": result["conflicts_resolved"],
                },
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Emit error
            await event_callback(
                AgentErrorEvent(
                    agent_id=self.agent_id,
                    data={"error": str(e), "traceback": repr(e)},
                )
            )

            return AgentResult(
                agent_id=self.agent_id,
                findings=[],
                errors=[str(e)],
                metadata={"duration_ms": duration_ms},
            )

    def _build_graph(self, event_callback: Callable) -> StateGraph:
        """Build the LangGraph for coordinator workflow."""

        async def parse_code_node(state: CoordinatorState) -> dict:
            """Parse code structure."""
            code_metadata = self._parse_code(state["code"])
            return {"code_metadata": code_metadata}

        async def create_plan_node(state: CoordinatorState) -> dict:
            """Create execution plan."""
            plan_steps = self._create_plan(state["code_metadata"])
            await event_callback(
                PlanCreatedEvent(
                    agent_id=self.agent_id,
                    data={"plan_steps": plan_steps},
                )
            )
            return {"plan_steps": plan_steps}

        def delegate_to_specialists(state: CoordinatorState) -> list[Send] | str:
            """Fan out to specialist agents using Send API, or skip if no specialists."""
            if not self.specialists:
                # No specialists — skip directly to consolidation
                return "consolidate"

            sends = []
            for specialist in self.specialists:
                sends.append(
                    Send(
                        "run_specialist",
                        {
                            "specialist": specialist,
                            "code": state["code"],
                            "context": state["context"],
                        },
                    )
                )
            return sends

        async def run_specialist(state: dict) -> dict:
            """Execute a single specialist agent."""
            specialist: BaseAgent = state["specialist"]
            code = state["code"]
            context = state["context"]

            # Emit delegation event
            await event_callback(
                AgentDelegatedEvent(
                    agent_id=self.agent_id,
                    data={
                        "delegated_to": specialist.agent_id.value,
                        "task": f"Perform {specialist.agent_id.value.replace('_agent', '')} analysis",
                    },
                )
            )

            # Run specialist and return result
            result = await specialist.analyze(code, context, event_callback)
            return {"specialist_results": [result]}

        async def consolidate_findings_node(state: CoordinatorState) -> dict:
            """Consolidate findings from all specialists."""
            consolidated, conflicts = self._consolidate_findings(
                state["specialist_results"]
            )

            by_severity = self._count_by_severity(consolidated)
            await event_callback(
                FindingsConsolidatedEvent(
                    agent_id=self.agent_id,
                    data={
                        "total_findings": len(consolidated),
                        "by_severity": by_severity,
                        "conflicts_resolved": conflicts,
                    },
                )
            )

            return {
                "consolidated_findings": consolidated,
                "conflicts_resolved": conflicts,
            }

        async def final_report_node(state: CoordinatorState) -> dict:
            """Generate final report."""
            consolidated = state["consolidated_findings"]
            critical = [f for f in consolidated if f.severity == Severity.CRITICAL]

            summary = f"Code review complete. Found {len(consolidated)} issues."
            if critical:
                summary += f" {len(critical)} critical."

            by_severity = self._count_by_severity(consolidated)

            await event_callback(
                FinalReportEvent(
                    agent_id=self.agent_id,
                    data={
                        "summary": summary,
                        "total_findings": len(consolidated),
                        "by_severity": by_severity,
                        "critical_findings": [
                            {
                                "finding_id": f.finding_id,
                                "category": f.category,
                                "severity": f.severity.value,
                                "line": f.line,
                                "description": f.description,
                            }
                            for f in critical
                        ],
                    },
                )
            )

            return {}

        # Build the graph
        graph = StateGraph(CoordinatorState)

        # Add nodes
        graph.add_node("parse_code", parse_code_node)
        graph.add_node("create_plan", create_plan_node)
        graph.add_node("run_specialist", run_specialist)
        graph.add_node("consolidate", consolidate_findings_node)
        graph.add_node("final_report", final_report_node)

        # Add edges
        graph.add_edge(START, "parse_code")
        graph.add_edge("parse_code", "create_plan")
        graph.add_conditional_edges(
            "create_plan", delegate_to_specialists, ["run_specialist", "consolidate"]
        )
        graph.add_edge("run_specialist", "consolidate")
        graph.add_edge("consolidate", "final_report")
        graph.add_edge("final_report", END)

        return graph

    def _parse_code(self, code: str) -> dict[str, Any]:
        """Parse code structure using AST."""
        try:
            tree = ast.parse(code)
            lines = len(code.splitlines())
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            imports = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            )
            return {
                "lines": lines,
                "functions": functions,
                "classes": classes,
                "imports": imports,
            }
        except SyntaxError:
            return {"lines": len(code.splitlines()), "functions": 0, "classes": 0, "imports": 0}

    def _create_plan(self, code_metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Create execution plan with steps."""
        plan = [
            {
                "step": 1,
                "action": "parse_code",
                "description": "Parse code structure",
            }
        ]

        for idx, specialist in enumerate(self.specialists, start=2):
            agent_name = specialist.agent_id.value.replace("_agent", "").replace("_", " ").title()
            plan.append(
                {
                    "step": idx,
                    "action": f"{specialist.agent_id.value}_analysis",
                    "description": f"Run {agent_name} analysis",
                    "parallel_with": [i for i in range(2, 2 + len(self.specialists)) if i != idx],
                }
            )

        plan.append(
            {
                "step": len(plan) + 1,
                "action": "consolidate",
                "description": "Consolidate findings",
            }
        )

        return plan

    def _consolidate_findings(
        self, specialist_results: list[AgentResult]
    ) -> tuple[list[Finding], int]:
        """Consolidate findings from specialists, deduplicating by (category, line)."""
        findings_by_key = {}
        conflicts_resolved = 0

        for result in specialist_results:
            for finding in result.findings:
                key = (finding.category, finding.line)

                if key in findings_by_key:
                    existing = findings_by_key[key]
                    if self._severity_rank(finding.severity) > self._severity_rank(existing.severity):
                        findings_by_key[key] = finding
                        conflicts_resolved += 1
                    else:
                        conflicts_resolved += 1
                else:
                    findings_by_key[key] = finding

        return list(findings_by_key.values()), conflicts_resolved

    def _severity_rank(self, severity: Severity) -> int:
        """Return numeric rank for severity (higher = more severe)."""
        rank = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        return rank.get(severity, 0)

    def _count_by_severity(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by severity level."""
        counts = defaultdict(int)
        for finding in findings:
            counts[finding.severity.value] += 1
        return {
            "critical": counts.get("critical", 0),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "info": counts.get("info", 0),
        }
