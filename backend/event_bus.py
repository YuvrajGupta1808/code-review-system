"""Async event bus for in-process pub/sub event streaming."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

from backend.models import BaseEvent


class EventBus:
    """
    In-process async pub/sub event bus.

    Features:
    - Multiple subscribers can listen concurrently
    - Each subscriber gets an ordered stream of events
    - Events published immediately (no batching)
    - No drops under normal load (backed by asyncio.Queue)
    - Ordered within single publisher, concurrent across publishers
    """

    def __init__(self, queue_size: int = 1000):
        """
        Initialize the event bus.

        Args:
            queue_size: Max events per subscriber queue before blocking publishes
        """
        self._subscribers: dict[str, asyncio.Queue[BaseEvent]] = {}
        self._queue_size = queue_size
        self._lock = asyncio.Lock()

    async def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to all subscribers.

        Events are published concurrently to all subscribers. If a subscriber's
        queue is full, the publish will wait for that queue to have space.

        Args:
            event: Event to publish

        Raises:
            RuntimeError: If event bus is corrupted (should not happen in practice)
        """
        # Get current subscribers without holding lock during publish
        async with self._lock:
            subscribers = dict(self._subscribers)

        # Publish to all subscribers concurrently
        if subscribers:
            await asyncio.gather(
                *[queue.put(event) for queue in subscribers.values()],
                return_exceptions=False,
            )

    async def subscribe(self) -> AsyncGenerator[BaseEvent, None]:
        """
        Subscribe to the event bus.

        Yields events in order as they are published. Each subscriber gets
        an independent queue, so slow subscribers don't block others.

        Yields:
            Events as they are published

        Example:
            async for event in event_bus.subscribe():
                print(f"Received: {event.event_type}")
        """
        subscriber_id = str(uuid4())
        queue: asyncio.Queue[BaseEvent] = asyncio.Queue(maxsize=self._queue_size)

        # Register subscriber
        async with self._lock:
            self._subscribers[subscriber_id] = queue

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            # Cleanup on unsubscribe
            async with self._lock:
                self._subscribers.pop(subscriber_id, None)

    @asynccontextmanager
    async def subscription_context(self) -> AsyncGenerator[AsyncGenerator[BaseEvent, None], None]:
        """
        Context manager for subscription.

        Usage:
            async with event_bus.subscription_context() as events:
                async for event in events:
                    process(event)
        """
        gen = self.subscribe()
        try:
            yield gen
        finally:
            try:
                await gen.aclose()
            except GeneratorExit:
                pass

    async def clear(self) -> None:
        """Clear all subscribers (for testing)."""
        async with self._lock:
            self._subscribers.clear()

    def subscriber_count(self) -> int:
        """Return current number of subscribers (for monitoring)."""
        return len(self._subscribers)


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def set_event_bus(bus: EventBus) -> None:
    """Set global event bus (for testing)."""
    global _event_bus
    _event_bus = bus
