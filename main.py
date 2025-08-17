import asyncio
import os
import signal
from concurrent.futures import ProcessPoolExecutor

from dotenv import find_dotenv, load_dotenv
from libs.colors import Colors
from metrics.exporter import MetricsExporter


load_dotenv(find_dotenv())

def sighandler(signum: int, frame):
    match signum:
        case signal.SIGTERM:
            print(Colors.colorize(Colors.FGYELLOW, "<SIGTERM received>"))
        case signal.SIGINT:
            print(Colors.colorize(Colors.FGYELLOW, "<SIGINT received>"))

    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(loop.stop)


async def exporter():
    try:
        EXPORTER_ENABLED = os.environ.get("MAE_CONFIG_METRICS_ENABLED", "false").lower() == "true"
        if EXPORTER_ENABLED:
            exporter = MetricsExporter()

            await exporter.run()
        else:
            print(Colors.colorize(Colors.FGYELLOW, "<Metrics exporter disabled>"))
    except KeyboardInterrupt:
        print(Colors.colorize(Colors.FGYELLOW, "<KeyboardInterrupt received>"))
        exit(0)


def run_exporter_sync():
    asyncio.run(exporter())


if __name__ == '__main__':
    # Explicitly create and set the event loop to avoid DeprecationWarning
    # in Python 3.10+ when no current event loop exists in this thread.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    exporter_future = None
    try:
        signal.signal(signal.SIGTERM, sighandler)
        signal.signal(signal.SIGINT, sighandler)

        executor = ProcessPoolExecutor(2)
        exporter_future = loop.run_in_executor(executor, run_exporter_sync)
        loop.run_forever()
    except KeyboardInterrupt:
        print(Colors.colorize(Colors.FGYELLOW, "<KeyboardInterrupt received>"))
        pass
    finally:
        if exporter_future and not exporter_future.done():
            exporter_future.cancel()
            try:
                loop.run_until_complete(exporter_future)
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        executor.shutdown(wait=True)
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        try:
            loop.run_until_complete(loop.shutdown_default_executor())
        except Exception:
            pass

        loop.close()
        try:
            from libs.mongodb.MongoClientSingleton import MongoClientSingleton
            MongoClientSingleton().close_client()
        except ImportError:
            pass
