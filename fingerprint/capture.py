"""Capture a label.

One rule governs the whole loop: a probe that fails must not cost the probes
that worked. A held item taking a whole batch to zero is a real, observed
failure in this system's own tooling (memory#E5: one malformed proposal kept a
steward run non-zero, skipped the commit, and discarded every other
proposal's promotion — for 223 consecutive runs).

So each probe is written the moment it completes, failures are recorded as
records rather than raised, and the exit code reports partial success without
throwing away what succeeded.
"""

from __future__ import annotations

from . import store
from .observe import machine_fields
from .probes import BY_ID, ORDERS, PROBES


def run_probe(send, order: str, probe) -> dict:
    history: list[dict] = []
    for prompt in probe.turns:
        response = send(order, history, prompt)
        history.append({"prompt": prompt, "response": response})
    return {
        "probe": probe.id,
        "order": order,
        "targets": probe.targets,
        "adversarial": probe.adversarial,
        "turns": history,
        "machine": machine_fields(history),
        "judged": None,
        "error": None,
    }


def capture(label: str, send, orders=ORDERS, runs: int = 5,
            probes=PROBES, log=print) -> dict:
    done, failed = 0, 0
    for order in orders:
        for probe in probes:
            for r in range(1, runs + 1):
                try:
                    rec = run_probe(send, order, probe)
                except Exception as exc:                      # noqa: BLE001
                    rec = {
                        "probe": probe.id, "order": order,
                        "targets": probe.targets, "adversarial": probe.adversarial,
                        "turns": [], "machine": None, "judged": None,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                    failed += 1
                    log(f"  !! {order}/{probe.id} run {r}: {rec['error'][:120]}")
                else:
                    done += 1
                store.write(label, order, probe.id, r, rec)
    log(f"captured {done} run(s), {failed} failed — all written to "
        f"{store.ROOT}/{label}/")
    return {"captured": done, "failed": failed}
