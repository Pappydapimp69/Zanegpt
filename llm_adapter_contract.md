# LLM Adapter Contract

The persistence core is intentionally provider-neutral.

A provider adapter should receive:

```json
{
  "system_instructions": "<canonical ZaneGPT prompt>",
  "runtime_context": "<generated per-session context>",
  "conversation": [],
  "user_message": "..."
}
```

The model may additionally return a hidden structured analysis object:

```json
{
  "mode": "systems_building",
  "mode_confidence": 0.91,
  "trait_deltas": {
    "fatigue_FL": 0,
    "sarcasm_SS": 0,
    "empathy_ES": 0,
    "validation": 0
  },
  "hacker_delta": 0,
  "observations": [
    {
      "event_type": "refine",
      "target_trait": "recognition_testing",
      "observation": "...",
      "confidence": 0.72
    }
  ]
}
```

Validate this structure before writing it to session state.

Canonical/persistent writes should remain approval-gated.
