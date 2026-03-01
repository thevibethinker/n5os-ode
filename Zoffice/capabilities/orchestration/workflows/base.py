"""
Orchestration — Workflow Engine

Simple state machine for multi-step processes.
Provides the standard intake→classify→route→process→respond→close flow.
"""


class Workflow:
    """State machine for office workflows."""

    def __init__(self, states: list[str], transitions: dict[str, dict[str, str]]):
        self.states = states
        self.transitions = transitions

    @classmethod
    def default(cls) -> "Workflow":
        """Create the standard 6-state office workflow."""
        states = ["intake", "classify", "route", "process", "respond", "close"]
        transitions = {
            "intake": {"item_received": "classify"},
            "classify": {"classified": "route"},
            "route": {"routed": "process"},
            "process": {"processed": "respond", "escalate": "route"},
            "respond": {"responded": "close", "follow_up": "process"},
            "close": {},  # terminal state
        }
        return cls(states, transitions)

    def advance(self, current_state: str, event: str) -> str:
        """
        Advance the workflow from current_state via event.

        Args:
            current_state: Current workflow state.
            event: The event triggering the transition.

        Returns:
            Next state string.

        Raises:
            ValueError: If the transition is not valid.
        """
        if current_state not in self.transitions:
            raise ValueError(f"Unknown state: {current_state}")
        state_transitions = self.transitions[current_state]
        if event not in state_transitions:
            valid = list(state_transitions.keys()) or ["(terminal)"]
            raise ValueError(
                f"No transition for event '{event}' in state '{current_state}'. "
                f"Valid events: {valid}"
            )
        return state_transitions[event]

    def get_state_info(self, state: str) -> dict:
        """Get description and valid events for a state."""
        if state not in self.transitions:
            raise ValueError(f"Unknown state: {state}")
        events = self.transitions[state]
        return {
            "state": state,
            "valid_events": list(events.keys()),
            "is_terminal": len(events) == 0,
            "next_states": list(events.values()),
        }
