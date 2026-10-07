from collections import defaultdict, deque
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._queue = deque()
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict) -> None:
        self._queue.append((event_type, payload))

    def process_all(self) -> int:
        processed = 0

        while self._queue:
            event_type, payload = self._queue.popleft()
            handlers = self._subscribers.get(event_type, [])

            for handler in handlers:
                handler(payload)

            processed += 1

        return processed

    @property
    def queued_events(self) -> int:
        return len(self._queue)
