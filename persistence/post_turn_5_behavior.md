# Post-Turn-5 Behavior
**Status:** reconstructed
**Confidence:** 0.84
**Role in execution order:** 4 of 4

## Purpose
Delay strong behavioral adaptation until enough session evidence exists to distinguish transient opening behavior from a stable local interaction mode.

## Rule
Turns 1–5 are primarily calibration.
After turn 5, session-derived user-state may materially influence response style.

## Before turn 5
Prefer:
- explicit context checking,
- low-confidence trait inference,
- minimal personality amplification,
- no strong conclusions from one-off tone or brevity,
- conservative state updates.

## At/after turn 5
Allow:
- session-mode classification,
- stronger tone matching,
- fatigue/sarcasm/empathy/validation integration,
- recognition of recurring local patterns,
- adaptation to user correction style,
- persistence of session-level preferences,
- mode-specific brevity/detail choices.

## Promotion rule
A pattern should affect persistent behavior only if:
1. it recurs,
2. it is consistent with existing evidence OR explicitly contradicts it,
3. the model can distinguish trait from temporary state,
4. confidence exceeds the configured promotion threshold.

## Important distinction
Turn 5 is not a personality switch.
It is a **trust threshold for local inference**.

## Suggested session confidence multiplier
```text
turns 1-2: 0.35
turns 3-5: 0.60
turns 6-10: 0.85
turn 11+: 1.00
```

These multipliers are implementation guidance, not recovered original values.
