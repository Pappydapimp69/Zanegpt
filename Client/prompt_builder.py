import json

OUTPUT_PROTOCOL = r"""
Return exactly two blocks:

<zanegpt_reply>
VISIBLE RESPONSE
</zanegpt_reply>
<zanegpt_state>
{
  "state": { COMPLETE UPDATED SESSION STATE },
  "events": [
    {
      "event_type": "confirm|strengthen|weaken|contradict|refine|new|preference",
      "target_trait": "string",
      "observation": "string",
      "evidence_excerpt": "string",
      "context_mode": "string",
      "confidence": 0.0,
      "persistent_candidate": false
    }
  ]
}
</zanegpt_state>

The reply block is user-visible. The state block is machine-consumed.
Increment turn_count exactly once. Return a complete state object, not a patch.
Never mark canonical approval yourself. Keep events sparse.
"""

def build_system(resources, state):
    order = [
        "SYSTEM_LAYER.md",
        "user_behavior_runtime.md",
        "user_behavior_database.md",
        "defensive_protocols.md",
        "hacker_flag.md",
        "TRAIT_ENGINE_RUNTIME.md",
        "post_turn_5_behavior.md",
        "PERSISTENCE_POLICY.md",
        "user_behavior_evidence.jsonl",
        "user_behavior_changelog.md",
    ]
    blocks = []
    for name in order:
        if name in resources:
            item = resources[name]
            blocks.append(f"\n===== {name} | {item['path']} =====\n{item['content']}\n")

    return (
        "You are running the ZaneGPT LLM-native behavior layer.\n"
        "Apply the loaded resources as the behavioral/control context.\n"
        + "".join(blocks)
        + "\n===== CURRENT SESSION STATE =====\n"
        + json.dumps(state, indent=2, ensure_ascii=False)
        + "\n"
        + OUTPUT_PROTOCOL
    )

def build_user_message(history, new_text):
    if not history:
        return new_text
    lines = ["RECENT CONVERSATION:"]
    for row in history:
        lines.append(f"{row.get('role','unknown').upper()}: {row.get('content','')}")
    lines += ["", "CURRENT USER MESSAGE:", new_text]
    return "\n".join(lines)
