# python
# app/src/core/simple_worker.py
import asyncio
import json
import threading
from typing import Any, Awaitable, Callable, Dict, Optional

from app.src.core.db import get_session_maker
from app.src.core.pubsub.subscriber import PubSubSubscriber
from app.src.core.pubsub.publisher import PubSubPublisher

AsyncHandler = Callable[[Dict[str, Any], Any, PubSubPublisher], Awaitable[None]]


class SimpleWorker:
    def __init__(
        self,
        subscription: str,
        handler: AsyncHandler,
        *,
        publisher: Optional[PubSubPublisher] = None,
        max_concurrency: int = 4,
    ) -> None:
        self.subscription = subscription
        self.handler = handler
        self.publisher = publisher or PubSubPublisher()
        self._subscriber = PubSubSubscriber(subscription)

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._session_maker = None
        self._sem: Optional[asyncio.Semaphore] = None
        self._max_concurrency = max(1, int(max_concurrency))

    def _start_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._session_maker = get_session_maker()
        self._sem = asyncio.Semaphore(self._max_concurrency)
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for t in pending:
                t.cancel()
            if pending:
                self._loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            self._loop.close()

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._start_loop, name=f"loop:{self.subscription}", daemon=True
        )
        self._thread.start()

        def on_message(message) -> None:
            try:
                data = json.loads(message.data.decode("utf-8"))
            except Exception:
                # Bad payload; drop it
                try:
                    message.ack()
                except Exception:
                    pass
                return

            async def run_one():
                assert self._sem is not None
                async with self._sem:
                    await self.handler(data, self._session_maker, self.publisher)

            fut = asyncio.run_coroutine_threadsafe(run_one(), self._loop)

            def done(f):
                try:
                    f.result()
                    message.ack()
                except Exception:
                    try:
                        message.nack()
                    except Exception:
                        pass

            fut.add_done_callback(done)

        self._subscriber.start(on_message)

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5)
