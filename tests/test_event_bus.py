"""Tests for the event bus implementation."""

import asyncio

import pytest

from backend.event_bus import EventBus
from backend.models import (
    AgentCompletedEvent,
    AgentStartedEvent,
    AgentType,
    EventType,
    ThinkingEvent,
)


@pytest.mark.asyncio
async def test_basic_publish_subscribe():
    """Test basic publish and subscribe."""
    bus = EventBus()
    events_received = []

    async def subscriber():
        async for event in bus.subscribe():
            events_received.append(event)
            if len(events_received) >= 2:
                break

    sub_task = asyncio.create_task(subscriber())

    # Give subscriber time to start
    await asyncio.sleep(0.01)

    event1 = AgentStartedEvent(agent_id=AgentType.COORDINATOR)
    event2 = AgentCompletedEvent(agent_id=AgentType.COORDINATOR)

    await bus.publish(event1)
    await bus.publish(event2)

    await sub_task

    assert len(events_received) == 2
    assert events_received[0].event_type == EventType.AGENT_STARTED
    assert events_received[1].event_type == EventType.AGENT_COMPLETED


@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test that multiple subscribers each get all events."""
    bus = EventBus()
    results = {"sub1": [], "sub2": []}

    async def subscriber(name: str):
        async for event in bus.subscribe():
            results[name].append(event)
            if len(results[name]) >= 3:
                break

    # Start two subscribers
    sub1_task = asyncio.create_task(subscriber("sub1"))
    sub2_task = asyncio.create_task(subscriber("sub2"))

    await asyncio.sleep(0.01)

    # Publish 3 events
    for i in range(3):
        event = ThinkingEvent(
            agent_id=AgentType.SECURITY,
            data={"content": f"Thinking message {i}"},
        )
        await bus.publish(event)

    await asyncio.gather(sub1_task, sub2_task)

    # Both subscribers should get all events in order
    assert len(results["sub1"]) == 3
    assert len(results["sub2"]) == 3

    for i in range(3):
        assert (
            results["sub1"][i].data["content"]
            == results["sub2"][i].data["content"]
            == f"Thinking message {i}"
        )


@pytest.mark.asyncio
async def test_concurrent_publishers():
    """Test concurrent publishers produce ordered events per publisher."""
    bus = EventBus()
    events_received = []

    async def subscriber():
        async for event in bus.subscribe():
            events_received.append(event)
            if len(events_received) >= 6:
                break

    async def publisher(agent: AgentType, count: int):
        for i in range(count):
            event = ThinkingEvent(
                agent_id=agent,
                data={"content": f"{agent}_message_{i}"},
            )
            await bus.publish(event)
            await asyncio.sleep(0.001)  # Small delay to allow interleaving

    sub_task = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

    # Publish from two agents concurrently
    await asyncio.gather(
        publisher(AgentType.SECURITY, 3),
        publisher(AgentType.BUG_DETECTION, 3),
    )

    await sub_task

    assert len(events_received) == 6

    # Verify each agent's events are in order
    security_events = [e for e in events_received if e.agent_id == AgentType.SECURITY]
    bug_events = [e for e in events_received if e.agent_id == AgentType.BUG_DETECTION]

    assert len(security_events) == 3
    assert len(bug_events) == 3

    # Check ordering within each agent
    for i, event in enumerate(security_events):
        assert event.data["content"] == f"{AgentType.SECURITY}_message_{i}"

    for i, event in enumerate(bug_events):
        assert event.data["content"] == f"{AgentType.BUG_DETECTION}_message_{i}"


@pytest.mark.asyncio
async def test_no_events_dropped():
    """Test that no events are dropped under load."""
    bus = EventBus()
    events_received = []
    total_events = 100

    async def subscriber():
        async for event in bus.subscribe():
            events_received.append(event)

    sub_task = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

    # Publish many events
    for i in range(total_events):
        event = ThinkingEvent(
            agent_id=AgentType.COORDINATOR,
            data={"content": str(i)},
        )
        await bus.publish(event)

    # Give subscriber time to process
    await asyncio.sleep(0.1)

    # Cancel subscriber
    sub_task.cancel()
    try:
        await sub_task
    except asyncio.CancelledError:
        pass

    assert len(events_received) == total_events


@pytest.mark.asyncio
async def test_subscription_context():
    """Test subscription context manager."""
    bus = EventBus()

    event1 = AgentStartedEvent(agent_id=AgentType.COORDINATOR)

    async def publisher():
        await asyncio.sleep(0.01)
        await bus.publish(event1)

    events = []

    pub_task = asyncio.create_task(publisher())

    async with bus.subscription_context() as subscription:
        async for event in subscription:
            events.append(event)
            break

    await pub_task

    assert len(events) == 1
    assert events[0].event_type == EventType.AGENT_STARTED


@pytest.mark.asyncio
async def test_subscriber_count():
    """Test subscriber count tracking."""
    bus = EventBus()

    assert bus.subscriber_count() == 0

    async def subscriber():
        async for _ in bus.subscribe():
            pass

    task1 = asyncio.create_task(subscriber())
    task2 = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

    assert bus.subscriber_count() == 2

    task1.cancel()
    task2.cancel()

    try:
        await asyncio.gather(task1, task2)
    except asyncio.CancelledError:
        pass

    await asyncio.sleep(0.01)
    assert bus.subscriber_count() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
