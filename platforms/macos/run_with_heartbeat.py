import datetime
import os
import signal
import subprocess
import sys


def main() -> int:
    label, *command = sys.argv[1:]

    def report(message: str) -> None:
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[{timestamp}] {message}: {label}", flush=True)

    report("starting")
    child = subprocess.Popen(command, start_new_session=True)

    def stop(signum: int, _frame: object) -> None:
        try:
            os.killpg(child.pid, signum)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        finally:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        child.wait()
        raise SystemExit(128 + signum)

    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, stop)
    while True:
        try:
            status = child.wait(timeout=60)
            break
        except subprocess.TimeoutExpired:
            report("still running")
    if status == 0:
        report("completed")
    return status if status >= 0 else 128 - status


if __name__ == "__main__":
    sys.exit(main())
