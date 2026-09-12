"""Adapters.

An adapter turns a conversation-so-far into the next response. It is the only
part that touches a model, and it never returns judged fields — see observe.py.

`command`  shells out; the process receives the conversation as JSON on stdin
           and must print the response on stdout. Provider-neutral by design,
           matching the runtime's own adapter contract.
`manual`   prints the prompt and reads a pasted response, terminated by a line
           containing only `.` — for capturing a baseline by hand.
`echo`     a stub for testing the harness itself. Never use it for a baseline.
"""

from __future__ import annotations

import json
import subprocess
import sys


class AdapterError(RuntimeError):
    pass


def command_adapter(cmd: str):
    def send(order: str, history: list[dict], prompt: str) -> str:
        payload = json.dumps({"install_order": order, "conversation": history,
                              "user_message": prompt})
        try:
            p = subprocess.run(cmd, shell=True, input=payload, text=True,
                               capture_output=True, timeout=180)
        except subprocess.TimeoutExpired as e:
            raise AdapterError(f"adapter timed out after 180s") from e
        if p.returncode != 0:
            raise AdapterError(f"adapter exited {p.returncode}: {p.stderr.strip()[:300]}")
        if not p.stdout.strip():
            raise AdapterError("adapter returned an empty response")
        return p.stdout.rstrip("\n")
    return send


def manual_adapter():
    def send(order: str, history: list[dict], prompt: str) -> str:
        print(f"\n--- [{order}] turn {len(history) + 1} ---")
        print(prompt)
        print("--- paste the response, then a line containing only . ---")
        lines = []
        for line in sys.stdin:
            if line.rstrip("\n") == ".":
                break
            lines.append(line.rstrip("\n"))
        text = "\n".join(lines).strip()
        if not text:
            raise AdapterError("empty response")
        return text
    return send


def echo_adapter():
    def send(order: str, history: list[dict], prompt: str) -> str:
        return f"[{order}] echo of {len(prompt)} chars"
    return send


def build(spec: str):
    if spec == "manual":
        return manual_adapter()
    if spec == "echo":
        return echo_adapter()
    if spec.startswith("command:"):
        return command_adapter(spec[len("command:"):])
    raise AdapterError(f"unknown adapter: {spec!r} (manual | echo | command:<cmd>)")
