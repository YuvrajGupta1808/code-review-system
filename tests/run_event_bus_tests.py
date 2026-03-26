"""Simple async tests for the event bus (no pytest required)."""

import asyncio

from backend.event_bus import EventBus
from backend.models import (
    AgentCompletedEvent,
    AgentStartedEvent,
    AgentType,
    EventType,
    ThinkingEvent,
)


async def test_basic_publish_subscribe():
    """Test basic publish and subscribe."""
    print("Test: Basic publish/subscribe...")
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

    assert len(events_received) == 2, f"Expected 2 events, got {len(events_received)}"
    assert (
        events_received[0].event_type == EventType.AGENT_STARTED
    ), f"Expected AGENT_STARTED, got {events_received[0].event_type}"
    assert (
        events_received[1].event_type == EventType.AGENT_COMPLETED
    ), f"Expected AGENT_COMPLETED, got {events_received[1].event_type}"
    print("  ✓ PASSED")


async def test_multiple_subscribers():
    """Test that multiple subscribers each get all events."""
    print("Test: Multiple subscribers...")
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

    assert len(results["sub1"]) == 3
    assert len(results["sub2"]) == 3

    for i in range(3):
        assert (
            results["sub1"][i].data["content"]
            == results["sub2"][i].data["content"]
            == f"Thinking message {i}"
        )
    print("  ✓ PASSED")


async def test_concurrent_publishers():
    """Test concurrent publishers produce ordered events per publisher."""
    print("Test: Concurrent publishers...")
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
            await asyncio.sleep(0.001)

    sub_task = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

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

    print("  ✓ PASSED")


async def test_no_events_dropped():
    """Test that no events are dropped under load."""
    print("Test: No events dropped...")
    bus = EventBus()
    events_received = []
    total_events = 100

    async def subscriber():
        async for event in bus.subscribe():
            events_received.append(event)

    sub_task = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

    for i in range(total_events):
        event = ThinkingEvent(
            agent_id=AgentType.COORDINATOR,
            data={"content": str(i)},
        )
        await bus.publish(event)

    await asyncio.sleep(0.1)

    sub_task.cancel()
    try:
        await sub_task
    except asyncio.CancelledError:
        pass

    assert len(events_received) == total_events, f"Expected {total_events}, got {len(events_received)}"
    print("  ✓ PASSED")


async def test_subscriber_count():
    """Test subscriber count tracking."""
    print("Test: Subscriber count tracking...")
    bus = EventBus()

    assert bus.subscriber_count() == 0

    async def subscriber():
        async for _ in bus.subscribe():
            pass

    task1 = asyncio.create_task(subscriber())
    task2 = asyncio.create_task(subscriber())

    await asyncio.sleep(0.01)

    assert bus.subscriber_count() == 2, f"Expected 2 subscribers, got {bus.subscriber_count()}"

    task1.cancel()
    task2.cancel()

    try:
        await asyncio.gather(task1, task2)
    except asyncio.CancelledError:
        pass

    await asyncio.sleep(0.01)
    assert bus.subscriber_count() == 0, f"Expected 0 subscribers, got {bus.subscriber_count()}"
    print("  ✓ PASSED")


async def main():
    """Run all tests."""
    print("\n=== Event Bus Tests ===\n")

    try:
        await test_basic_publish_subscribe()
        await test_multiple_subscribers()
        await test_concurrent_publishers()
        await test_no_events_dropped()
        await test_subscriber_count()

        print("\n✓ All tests passed!\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
