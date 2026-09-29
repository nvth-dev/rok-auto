import os
import logging

import cv2
import numpy as np

import config
from rok_bot.adb import ADB

log = logging.getLogger(__name__)


class Screen:
    def __init__(self, adb: ADB):
        self.adb = adb
        self._templates: dict[str, np.ndarray] = {}

    def capture(self) -> np.ndarray | None:
        raw = self.adb.screenshot()
        if not raw:
            return None
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        return img

    def find(self, template_name: str, screenshot: np.ndarray = None,
             threshold: float = None) -> tuple[int, int] | None:
        if screenshot is None:
            screenshot = self.capture()
            if screenshot is None:
                return None

        template = self._load_template(template_name)
        if template is None:
            return None

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        thresh = threshold or config.MATCH_THRESHOLD
        if max_val >= thresh:
            h, w = template.shape[:2]
            cx = max_loc[0] + w // 2
            cy = max_loc[1] + h // 2
            log.debug("Found '%s' at (%d, %d) conf=%.2f", template_name, cx, cy, max_val)
            return (cx, cy)

        log.debug("'%s' not found (best=%.2f < %.2f)", template_name, max_val, thresh)
        return None

    def find_all(self, template_name: str, screenshot: np.ndarray = None,
                 threshold: float = None) -> list[tuple[int, int]]:
        if screenshot is None:
            screenshot = self.capture()
            if screenshot is None:
                return []

        template = self._load_template(template_name)
        if template is None:
            return []

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        thresh = threshold or config.MATCH_THRESHOLD
        locations = np.where(result >= thresh)

        h, w = template.shape[:2]
        points = []
        for pt in zip(*locations[::-1]):
            cx, cy = pt[0] + w // 2, pt[1] + h // 2
            too_close = any(abs(cx - px) < w and abs(cy - py) < h for px, py in points)
            if not too_close:
                points.append((cx, cy))

        log.debug("Found %d instances of '%s'", len(points), template_name)
        return points

    def wait_for(self, template_name: str, timeout: float = 10.0,
                 interval: float = 0.5) -> tuple[int, int] | None:
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            pos = self.find(template_name)
            if pos:
                return pos
            time.sleep(interval)
        log.warning("Timeout waiting for '%s'", template_name)
        return None

    def _load_template(self, name: str) -> np.ndarray | None:
        if name in self._templates:
            return self._templates[name]

        path = os.path.join(config.IMAGES_DIR, f"{name}.png")
        if not os.path.exists(path):
            log.error("Template not found: %s", path)
            return None

        tmpl = cv2.imread(path, cv2.IMREAD_COLOR)
        self._templates[name] = tmpl
        return tmpl
