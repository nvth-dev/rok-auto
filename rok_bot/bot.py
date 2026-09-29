import logging

from rok_bot.adb import ADB
from rok_bot.screen import Screen
from rok_bot.state_machine import StateMachine, StateResult
from rok_bot.states.farm_barb import (
    SearchBarb, TapAttack, SelectCommander, WaitMarch, SearchByCoord,
)

log = logging.getLogger(__name__)


class ROKBot:
    def __init__(self, host=None, port=None):
        self.adb = ADB(host, port)
        self.screen = Screen(self.adb)

    def connect(self) -> bool:
        return self.adb.connect()

    def disconnect(self):
        self.adb.disconnect()

    def farm_barb(self):
        sm = StateMachine(self)

        search = SearchBarb(self)
        attack = TapAttack(self)
        commander = SelectCommander(self)
        wait = WaitMarch(self)
        search_coord = SearchByCoord(self)

        sm.add_state(search, {
            StateResult.SUCCESS: "tap_attack",
            StateResult.FAIL: "search_by_coord",
        })
        sm.add_state(attack, {
            StateResult.SUCCESS: "select_commander",
            StateResult.FAIL: "search_barb",
        })
        sm.add_state(commander, {
            StateResult.SUCCESS: "wait_march",
            StateResult.FAIL: "search_barb",
        })
        sm.add_state(wait, {
            StateResult.SUCCESS: "search_barb",
        })
        sm.add_state(search_coord, {
            StateResult.SUCCESS: "search_barb",
            StateResult.FAIL: "search_barb",
        })

        log.info("=== Farm Barbarian started ===")
        sm.run()
