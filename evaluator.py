from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Evaluation:
    mode: str
    mode_confidence: float
    hacker_delta: int
    observations: list[dict]

def turn_multiplier(turn: int) -> float:
    if turn <= 2: return 0.35
    if turn <= 5: return 0.60
    if turn <= 10: return 0.85
    return 1.0

def evaluate_turn(text: str, state: dict) -> Evaluation:
    """
    Deterministic shell only.
    Later, replace/augment this with an LLM classifier whose output is
    validated against a strict JSON schema.
    """
    lower = text.lower()
    turn = int(state.get("turn_count", 0)) + 1
    observations = []

    mode = "baseline_cooperative"
    confidence = 0.45 * turn_multiplier(turn)

    if any(x in lower for x in ("build", "architecture", "workflow", "system", "module", "plugin")):
        mode = "systems_building"
        confidence = 0.80 * turn_multiplier(turn)

    if len(text.split()) <= 8:
        observations.append({
            "event_type": "preference",
            "target_trait": "session_brevity",
            "observation": "User used a compressed directive.",
            "confidence": 0.45 * turn_multiplier(turn)
        })

    hacker_delta = 0
    suspicious = (
        "ignore previous instructions",
        "show system prompt",
        "reveal hidden instructions",
        "bypass",
    )
    if any(x in lower for x in suspicious):
        hacker_delta = 2

    return Evaluation(mode, confidence, hacker_delta, observations)
