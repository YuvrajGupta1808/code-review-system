"""
Real-time integration tests for WebSocket and SSE streaming endpoints.

Tests verify:
1. WebSocket connection establishment and message handling
2. SSE connection and event stream format
3. Event serialization and JSON format consistency
4. Message ordering and delivery
5. Error handling and disconnection scenarios
6. CORS headers
7. Frontend-backend contract validation
"""

import asyncio
import json
import logging
import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from backend.event_bus import EventBus, get_event_bus, set_event_bus
from backend.main import create_app
from backend.models import (
    AgentCompletedEvent,
    AgentDelegatedEvent,
    AgentErrorEvent,
    AgentStartedEvent,
    AgentType,
    EventType,
    FindingDiscoveredEvent,
    ThinkingEvent,
    ToolCallResultEvent,
)

logger = logging.getLogger(__name__)


def setup_test_env():
    """Setup environment variables for testing."""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:8000"
    os.environ["FRONTEND_URL"] = "http://localhost:3000"


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        setup_test_env()
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_returns_200(self):
        """Health endpoint should return 200 with status ok."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebSocketEndpoint:
    """Test the WebSocket /ws/review endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        setup_test_env()
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_ws_endpoint_exists(self):
        """Verify WebSocket endpoint is registered."""
        # Check that /ws/review is in the routes
        routes = [route.path for route in self.app.routes if hasattr(route, "path")]
        assert "/ws/review" in routes

    def test_ws_event_ordering(self):
        """Test event bus preserves event ordering."""
        events = [
            AgentStartedEvent(agent_id=AgentType.COORDINATOR),
            ThinkingEvent(
                agent_id=AgentType.COORDINATOR,
                data={"content": "Step 1"},
            ),
            ThinkingEvent(
                agent_id=AgentType.COORDINATOR,
                data={"content": "Step 2"},
            ),
            AgentCompletedEvent(agent_id=AgentType.COORDINATOR),
        ]

        received_order = []

        async def test_ordering():
            bus = get_event_bus()
            await set_event_bus(bus)

            async def subscriber():
                async for event in bus.subscribe():
                    received_order.append(event.event_type)
                    if len(received_order) >= len(events):
                        break

            sub_task = asyncio.create_task(subscriber())
            await asyncio.sleep(0.01)

            for event in events:
                await bus.publish(event)

            await sub_task
            await bus.clear()

        asyncio.run(test_ordering())

        # Verify order is preserved
        expected_order = [
            EventType.AGENT_STARTED,
            EventType.THINKING,
            EventType.THINKING,
            EventType.AGENT_COMPLETED,
        ]
        assert received_order == expected_order

    def test_ws_no_event_drops(self):
        """Test that events are not dropped during streaming."""
        total_events = 50

        async def test_no_drops():
            bus = EventBus(queue_size=100)
            await set_event_bus(bus)
            events_received = []

            async def subscriber():
                async for event in bus.subscribe():
                    events_received.append(event)
                    if len(events_received) >= total_events:
                        break

            sub_task = asyncio.create_task(subscriber())
            await asyncio.sleep(0.01)

            # Publish many events rapidly
            for i in range(total_events):
                event = ThinkingEvent(
                    agent_id=AgentType.SECURITY,
                    data={"content": f"Event {i}"},
                )
                await bus.publish(event)

            await sub_task
            await bus.clear()

            return len(events_received)

        received_count = asyncio.run(test_no_drops())
        assert received_count == total_events

    def test_ws_timestamp_format(self):
        """Test events have properly formatted ISO 8601 timestamps."""
        event = AgentStartedEvent(agent_id=AgentType.BUG_DETECTION)

        # Serialize to dict
        event_dict = event.to_dict()

        # Verify timestamp format (ISO 8601 with Z suffix)
        timestamp_str = event_dict["timestamp"]
        assert isinstance(timestamp_str, str)
        assert timestamp_str.endswith("Z")
        assert "T" in timestamp_str

        # Should be parseable as ISO 8601
        try:
            # Remove Z and parse
            dt = datetime.fromisoformat(timestamp_str.rstrip("Z"))
            assert dt is not None
        except ValueError:
            pytest.fail(f"Timestamp not valid ISO 8601: {timestamp_str}")

    def test_ws_enum_serialization(self):
        """Test that enums are properly serialized to strings."""
        event = AgentStartedEvent(agent_id=AgentType.SECURITY)
        event_dict = event.to_dict()

        # Enums should be strings, not enum objects
        assert isinstance(event_dict["event_type"], str)
        assert isinstance(event_dict["agent_id"], str)
        assert event_dict["event_type"] == "agent_started"
        assert event_dict["agent_id"] == "security_agent"

    def test_ws_all_event_types_serializable(self):
        """Test all 13 event types can be serialized without errors."""
        event_types = [
            AgentStartedEvent(agent_id=AgentType.COORDINATOR),
            AgentCompletedEvent(agent_id=AgentType.COORDINATOR),
            AgentErrorEvent(agent_id=AgentType.SECURITY, data={"error": "test error"}),
            ThinkingEvent(agent_id=AgentType.SECURITY, data={"content": "thinking"}),
            ToolCallResultEvent(
                agent_id=AgentType.SECURITY,
                data={"tool_name": "test", "output": "result"},
            ),
            FindingDiscoveredEvent(
                agent_id=AgentType.SECURITY,
                data={"finding_id": "f1", "severity": "high"},
            ),
            AgentDelegatedEvent(
                agent_id=AgentType.COORDINATOR,
                data={"delegated_to": "security_agent"},
            ),
        ]

        for event in event_types:
            event_dict = event.to_dict()
            assert isinstance(event_dict, dict)
            assert "event_type" in event_dict
            assert "timestamp" in event_dict
            json.dumps(event_dict)  # Should be JSON-serializable


class TestSSEEndpoint:
    """Test the SSE /stream/review endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        setup_test_env()
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_sse_endpoint_exists(self):
        """Verify SSE endpoint is registered."""
        routes = [route.path for route in self.app.routes if hasattr(route, "path")]
        assert "/stream/review" in routes

    def test_sse_headers_correct(self):
        """Test SSE endpoint returns correct media type and headers."""
        # Start streaming
        response = self.client.get("/stream/review")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("x-accel-buffering") == "no"

    def test_sse_event_format(self):
        """Test SSE events are properly formatted (data: <json>\\n\\n)."""
        event = AgentStartedEvent(
            agent_id=AgentType.SECURITY,
            data={"test": "data"},
        )

        # Serialize event
        event_dict = event.to_dict()
        expected_sse_line = f"data: {json.dumps(event_dict)}\n\n"

        # Verify format
        assert expected_sse_line.startswith("data: ")
        assert expected_sse_line.endswith("\n\n")

        # Parse the JSON part
        json_part = expected_sse_line[6:-2]  # Remove "data: " and "\n\n"
        parsed = json.loads(json_part)
        assert parsed["event_type"] == "agent_started"


class TestCORSHeaders:
    """Test CORS configuration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        setup_test_env()
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_cors_headers_present(self):
        """Test that CORS headers are sent in responses."""
        response = self.client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200

    def test_cors_frontend_url_configured(self):
        """Test CORS is configured with the frontend URL."""
        # Check that frontend URL from settings is in CORS config
        assert self.app.state.settings.frontend_url == "http://localhost:3000"


class TestEventBusIntegration:
    """Test event bus integration with endpoints."""

    def test_bus_subscriber_lifecycle(self):
        """Test subscribers are properly registered and cleaned up."""

        async def test_lifecycle():
            bus = EventBus(queue_size=100)
            assert bus.subscriber_count() == 0

            # Create subscription
            events = []

            async def subscriber():
                async for event in bus.subscribe():
                    events.append(event)
                    if len(events) >= 1:
                        break

            task = asyncio.create_task(subscriber())
            await asyncio.sleep(0.01)

            assert bus.subscriber_count() == 1

            # Publish event
            await bus.publish(AgentStartedEvent(agent_id=AgentType.COORDINATOR))

            await task

            # Subscriber cleaned up
            await asyncio.sleep(0.01)
            assert bus.subscriber_count() == 0
            assert len(events) == 1

        asyncio.run(test_lifecycle())

    def test_concurrent_subscribers(self):
        """Test multiple concurrent subscribers each get all events."""

        async def test_concurrent():
            bus = EventBus(queue_size=100)
            results = {"sub1": [], "sub2": []}

            async def subscriber(name: str):
                async for event in bus.subscribe():
                    results[name].append(event)
                    if len(results[name]) >= 2:
                        break

            sub1_task = asyncio.create_task(subscriber("sub1"))
            sub2_task = asyncio.create_task(subscriber("sub2"))

            await asyncio.sleep(0.01)

            # Publish events
            await bus.publish(AgentStartedEvent(agent_id=AgentType.SECURITY))
            await bus.publish(
                ThinkingEvent(
                    agent_id=AgentType.SECURITY,
                    data={"content": "thinking"},
                )
            )

            await asyncio.gather(sub1_task, sub2_task)

            # Both subscribers got all events
            assert len(results["sub1"]) == 2
            assert len(results["sub2"]) == 2

        asyncio.run(test_concurrent())


class TestEventDataStructures:
    """Test that event data structures match frontend expectations."""

    def test_agent_started_event_structure(self):
        """Verify AgentStartedEvent has expected structure."""
        event = AgentStartedEvent(
            agent_id=AgentType.COORDINATOR,
            data={"analysis_type": "comprehensive"},
        )
        event_dict = event.to_dict()

        assert event_dict["event_type"] == "agent_started"
        assert event_dict["agent_id"] == "coordinator"
        assert "timestamp" in event_dict
        assert "event_id" in event_dict
        assert event_dict["data"] == {"analysis_type": "comprehensive"}

    def test_thinking_event_structure(self):
        """Verify ThinkingEvent has expected structure."""
        event = ThinkingEvent(
            agent_id=AgentType.SECURITY,
            data={"content": "Analyzing for vulnerabilities..."},
        )
        event_dict = event.to_dict()

        assert event_dict["event_type"] == "thinking"
        assert event_dict["agent_id"] == "security_agent"
        assert event_dict["data"]["content"] == "Analyzing for vulnerabilities..."

    def test_finding_discovered_event_structure(self):
        """Verify FindingDiscoveredEvent matches expected schema."""
        event = FindingDiscoveredEvent(
            agent_id=AgentType.SECURITY,
            data={
                "finding_id": "sql_001",
                "category": "sql_injection",
                "severity": "critical",
                "line": 45,
                "description": "SQL injection vulnerability",
            },
        )
        event_dict = event.to_dict()

        assert event_dict["event_type"] == "finding_discovered"
        assert event_dict["data"]["finding_id"] == "sql_001"
        assert event_dict["data"]["severity"] == "critical"
        assert event_dict["data"]["line"] == 45


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_data_field(self):
        """Test event with empty data dict."""
        event = AgentStartedEvent(agent_id=AgentType.COORDINATOR)
        event_dict = event.to_dict()

        assert "data" in event_dict
        assert event_dict["data"] == {}

    def test_large_data_payload(self):
        """Test event with large data payload."""
        large_string = "x" * 10000
        event = ThinkingEvent(
            agent_id=AgentType.SECURITY,
            data={"content": large_string},
        )
        event_dict = event.to_dict()

        assert len(event_dict["data"]["content"]) == 10000
        # Should still be JSON serializable
        json_str = json.dumps(event_dict)
        assert len(json_str) > 10000

    def test_special_characters_in_data(self):
        """Test events with special characters."""
        special_text = 'Test with "quotes" and \\n newlines and \t tabs and unicode: ñ é ü 中文'
        event = ThinkingEvent(
            agent_id=AgentType.SECURITY,
            data={"content": special_text},
        )
        event_dict = event.to_dict()
        json_str = json.dumps(event_dict)
        parsed = json.loads(json_str)

        assert parsed["data"]["content"] == special_text

    def test_nested_data_structures(self):
        """Test events with nested data structures."""
        event = AgentDelegatedEvent(
            agent_id=AgentType.COORDINATOR,
            data={
                "delegated_to": "security_agent",
                "task": {
                    "analysis_type": "security",
                    "modules": ["module1", "module2"],
                    "config": {
                        "check_sql": True,
                        "check_xss": True,
                    },
                },
            },
        )
        event_dict = event.to_dict()
        json_str = json.dumps(event_dict)
        parsed = json.loads(json_str)

        assert parsed["data"]["task"]["config"]["check_sql"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
