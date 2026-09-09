import json, re

R_REPLY = re.compile(r"<zanegpt_reply>\s*(.*?)\s*</zanegpt_reply>", re.S)
R_STATE = re.compile(r"<zanegpt_state>\s*(.*?)\s*</zanegpt_state>", re.S)

def parse_envelope(text):
    a, b = R_REPLY.search(text), R_STATE.search(text)
    if not a or not b:
        raise ValueError("Missing ZaneGPT response envelope.")
    raw = re.sub(r"^```(?:json)?\s*", "", b.group(1).strip())
    raw = re.sub(r"\s*```$", "", raw)
    payload = json.loads(raw)
    if not isinstance(payload.get("state"), dict):
        raise ValueError("Missing complete state object.")
    payload.setdefault("events", [])
    return a.group(1).strip(), payload
