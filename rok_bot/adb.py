import subprocess
import time
import logging

import config

log = logging.getLogger(__name__)


class ADB:
    def __init__(self, host=None, port=None):
        self.address = f"{host or config.ADB_HOST}:{port or config.ADB_PORT}"
        self._connected = False

    def connect(self):
        result = self._run(["adb", "connect", self.address])
        if "connected" in result.lower():
            self._connected = True
            log.info("Connected to %s", self.address)
            return True
        log.error("Failed to connect: %s", result)
        return False

    def disconnect(self):
        self._run(["adb", "disconnect", self.address])
        self._connected = False

    def screenshot(self) -> bytes:
        proc = subprocess.run(
            ["adb", "-s", self.address, "exec-out", "screencap", "-p"],
            capture_output=True,
        )
        if proc.returncode != 0:
            log.error("Screenshot failed: %s", proc.stderr.decode(errors="replace"))
            return b""
        return proc.stdout

    def tap(self, x: int, y: int):
        log.debug("tap(%d, %d)", x, y)
        self._shell(f"input tap {x} {y}")
        time.sleep(config.DELAYS["tap"])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500):
        log.debug("swipe(%d,%d -> %d,%d)", x1, y1, x2, y2)
        self._shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    def key(self, keycode: int):
        self._shell(f"input keyevent {keycode}")

    def text(self, s: str):
        self._shell(f"input text '{s}'")

    def _shell(self, cmd: str):
        self._run(["adb", "-s", self.address, "shell", cmd])

    def _run(self, cmd: list[str]) -> str:
        proc = subprocess.run(cmd, capture_output=True, timeout=10)
        return proc.stdout.decode(errors="replace").strip()
