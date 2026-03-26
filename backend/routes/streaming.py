"""Real-time event streaming endpoints (WebSocket and SSE)."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from backend.event_bus import EventBus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/review")
async def websocket_review(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time review events.

    Client flow:
    1. Connect to /ws/review
    2. Optionally send code as first message (B5 stub)
    3. Receive streaming events as JSON

    Each event from the bus is sent immediately as JSON without batching.
    """
    await websocket.accept()
    bus: EventBus = websocket.app.state.bus

    try:
        # B5 stub: accept optional code submission in background
        # Don't block on receiving code - start streaming events immediately
        async def receive_code():
            try:
                code = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                logger.debug(f"Received code submission ({len(code)} chars) via WebSocket")
            except asyncio.TimeoutError:
                logger.debug("No code submission received on WebSocket")
            except Exception:
                pass  # Client may have disconnected

        # Start code receive in background (non-blocking)
        asyncio.create_task(receive_code())

        # Subscribe to bus and stream events
        async with bus.subscription_context() as events:
            async for event in events:
                await websocket.send_json(event.to_dict())

    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass  # Already closed or other error


@router.get("/stream/review")
async def sse_review(
    request: Request,
    # EventSource supports GET-only. The simplest way to start a review is via a query param.
    # Note: very large source code may exceed URL length limits.
    code: str | None = Query(default=None, description="Python code to analyze"),
) -> StreamingResponse:
    """Server-Sent Events endpoint for real-time review events.

    Returns a text/event-stream response that streams each event as:
    data: <json>\n\n

    Client can use EventSource API to consume.
    """
    bus: EventBus = request.app.state.bus
    settings = request.app.state.settings

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE-formatted events from the bus."""
        async with bus.subscription_context() as events:
            # Start the review once per SSE connection (if code is provided).
            if code and code.strip():

                async def run_review() -> None:
                    from backend.agents.coordinator import CoordinatorAgent
                    from backend.agents.bug import BugAgent
                    from backend.agents.security import SecurityAgent
                    from backend.llm_client import LLMClient

                    llm_client = LLMClient(
                        base_url=settings.openai_base_url,
                        api_key=settings.openai_api_key,
                    )
                    coordinator = CoordinatorAgent(
                        specialists=[
                            SecurityAgent(llm_client=llm_client),
                            BugAgent(llm_client=llm_client),
                        ]
                    )

                    async def event_callback(event) -> None:
                        # Fan-out all agent events through the shared event bus.
                        await bus.publish(event)

                    # Fire the review; events will stream via the subscription below.
                    await coordinator.analyze(code, context={}, event_callback=event_callback)

                asyncio.create_task(run_review())

            async for event in events:
                # Check if client disconnected before yielding
                if await request.is_disconnected():
                    logger.debug("SSE client disconnected")
                    break
                # Format as SSE: data: <json>\n\n
                payload = json.dumps(event.to_dict())
                yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
