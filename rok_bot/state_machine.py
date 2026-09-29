import logging
import time
from enum import Enum, auto

log = logging.getLogger(__name__)


class StateResult(Enum):
    SUCCESS = auto()
    FAIL = auto()
    REPEAT = auto()


class State:
    name: str = "unnamed"

    def __init__(self, bot):
        self.bot = bot
        self.adb = bot.adb
        self.screen = bot.screen

    def execute(self) -> StateResult:
        raise NotImplementedError


class StateMachine:
    def __init__(self, bot):
        self.bot = bot
        self._states: dict[str, State] = {}
        self._transitions: dict[str, dict[StateResult, str]] = {}
        self._current: str | None = None
        self.running = False

    def add_state(self, state: State, transitions: dict[StateResult, str] = None):
        self._states[state.name] = state
        self._transitions[state.name] = transitions or {}
        if self._current is None:
            self._current = state.name

    def run(self):
        self.running = True
        log.info("Starting state machine at '%s'", self._current)

        while self.running and self._current:
            state = self._states[self._current]
            log.info("[%s] executing...", state.name)

            try:
                result = state.execute()
            except Exception:
                log.exception("Error in state '%s'", state.name)
                result = StateResult.FAIL

            if result == StateResult.REPEAT:
                time.sleep(0.5)
                continue

            transitions = self._transitions.get(state.name, {})
            next_state = transitions.get(result)

            if next_state is None:
                log.info("No transition for %s from '%s', stopping", result, state.name)
                break

            log.info("[%s] %s → '%s'", state.name, result.name, next_state)
            self._current = next_state

        self.running = False
        log.info("State machine stopped")

    def stop(self):
        self.running = False
