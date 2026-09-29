import time
import logging

import config
from rok_bot.state_machine import State, StateResult

log = logging.getLogger(__name__)


class SearchBarb(State):
    """Tìm barbarian trên map. Nếu không thấy, kéo map rồi tìm lại."""
    name = "search_barb"

    def __init__(self, bot):
        super().__init__(bot)
        self._search_attempts = 0
        self._max_attempts = 4

    def execute(self) -> StateResult:
        screenshot = self.screen.capture()
        if screenshot is None:
            return StateResult.REPEAT

        pos = self.screen.find("barb_icon", screenshot)
        if pos:
            self.adb.tap(*pos)
            self._search_attempts = 0
            time.sleep(config.DELAYS["after_tap"])
            return StateResult.SUCCESS

        self._search_attempts += 1
        if self._search_attempts >= self._max_attempts:
            log.warning("Cannot find barbarian after %d attempts, using search", self._max_attempts)
            self._search_attempts = 0
            return StateResult.FAIL

        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2
        self.adb.swipe(cx, cy, cx - 300, cy, 500)
        time.sleep(config.DELAYS["search_enemy"])
        return StateResult.REPEAT


class TapAttack(State):
    """Click nút Attack sau khi chọn barbarian."""
    name = "tap_attack"

    def execute(self) -> StateResult:
        pos = self.screen.wait_for("btn_attack", timeout=5)
        if pos:
            self.adb.tap(*pos)
            time.sleep(config.DELAYS["after_tap"])
            return StateResult.SUCCESS
        log.warning("Attack button not found")
        return StateResult.FAIL


class SelectCommander(State):
    """Chờ màn hình chọn commander, chọn march."""
    name = "select_commander"

    def execute(self) -> StateResult:
        pos = self.screen.wait_for("btn_march", timeout=5)
        if pos:
            self.adb.tap(*pos)
            time.sleep(config.DELAYS["after_tap"])
            return StateResult.SUCCESS
        log.warning("March button not found")
        return StateResult.FAIL


class WaitMarch(State):
    """Chờ quân march xong rồi quay về."""
    name = "wait_march"

    def execute(self) -> StateResult:
        log.info("Waiting for march to complete...")
        time.sleep(config.DELAYS["march_wait"])

        for _ in range(60):
            screenshot = self.screen.capture()
            if screenshot is None:
                time.sleep(2)
                continue
            if self.screen.find("icon_idle_commander", screenshot):
                log.info("Commander returned, ready for next barb")
                return StateResult.SUCCESS
            time.sleep(2)

        log.warning("Timeout waiting for commander to return")
        return StateResult.SUCCESS


class SearchByCoord(State):
    """Dùng tính năng search in-game để tìm barb khi swipe không thấy."""
    name = "search_by_coord"

    def execute(self) -> StateResult:
        pos = self.screen.find("btn_search")
        if pos:
            self.adb.tap(*pos)
            time.sleep(config.DELAYS["after_tap"])

        pos = self.screen.wait_for("tab_barbarian", timeout=5)
        if pos:
            self.adb.tap(*pos)
            time.sleep(config.DELAYS["after_tap"])

        pos = self.screen.wait_for("btn_search_go", timeout=5)
        if pos:
            self.adb.tap(*pos)
            time.sleep(config.DELAYS["after_tap"])
            return StateResult.SUCCESS

        log.warning("Could not use search")
        return StateResult.FAIL
