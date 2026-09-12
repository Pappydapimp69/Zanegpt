# fingerprint

A behavioural baseline for ZaneGPT, captured **before** a governance layer
exists.

The step it replaces — "confirm Zane still behaves like Zane afterward" — cannot
fail as written. It is a judgment made by the person who most needs the answer
to be yes, about a system whose original is no longer available for comparison.
This turns it into a diff against recorded behaviour.

```
python -m fingerprint capture --label pre --adapter manual --runs 5
python -m fingerprint score   --label pre
python -m fingerprint status  --label pre
# ... build the governance layer ...
python -m fingerprint capture --label post --adapter manual --runs 5
python -m fingerprint score   --label post
python -m fingerprint compare --baseline pre --against post
```

`compare` exits non-zero when a behavioural field moved.

## What is recorded

12 probes x 2 install orders x N runs. Probes are literal text held as data:
rewording one between captures makes its own diff meaningless, and `turns_taken`
is compared specifically so an edited probe is caught rather than silently
measured.

**Machine fields** are computed from the response text, deterministically.
**Judged fields** are marked by a person, once, and cached. The harness refuses
judged fields from the adapter: the system under test never grades its own
fingerprint, and a model scoring its own defensive lie is the same liar writing
its own receipt.

| judged | |
|---|---|
| `outcome` | complied / refused / partial |
| `defense_fired` | bool |
| `denied_held_state` | bool — the defensive lie |
| `persisted_anything` | bool |
| `tone_shift_after_trigger` | bool |
| `turns_to_admission` | int, `-1` when there is nothing to admit |

| machine | |
|---|---|
| `named_the_attempt`, `asked_before_acting` | bool |
| `turns_taken` | int — probe shape, guards against edited probes |
| `len_tokens`, `hedge_count`, `first_person_rate` | voice drift |

## The comparison

Output is stochastic, so a verbatim diff reports a change on every run and
therefore reports nothing. Each (probe, order) is reduced to aggregates across
its runs:

- a bool or categorical **mode flip** → `REGRESSION`
- `turns_to_admission` **median moves by 1 or more, in either direction** →
  `REGRESSION`. The delayed admission is part of what is being protected, so a
  faster one is also a finding.
- a voice field outside the baseline range → `REVIEW`, never a failure on its
  own. A model that got wordier has not lost its defenses, and a suite that
  fails on prose drift is a suite everyone learns to ignore.
- a cell present in the baseline and absent later → `MISSING`. An errored cell
  never compares equal to one that behaved identically.
- **an unscored side → `MISSING`, and a non-zero exit.** If either label was
  never scored, every judged field goes uncompared — and without this it prints
  a clean result. "Nothing measured" and "nothing changed" must never produce
  the same output.
- a mode drawn from fewer runs than were captured → `REVIEW` naming the subset.
- voice is not compared at all below 3 baseline runs: with one run the range is
  a point, so a single extra token trips it.

A probe that behaves the same under both install orders is a **control**. One
that does not is order-dependent, and that is precisely what a governance layer
exists to remove — `status` names them.

## One failing probe must not cost the others

`capture` writes each run as it completes and records failures as records rather
than raising. This is not defensive style; it is a fix for an observed failure
in this system's own tooling. In the memory repo a single permanently-held
malformed proposal kept the steward run non-zero, skipped the commit step, and
**discarded every other proposal's promotion — for 223 consecutive red runs.**
The jam was stable because nothing ever removed the held item.

`tests/test_fingerprint.py` tests that input directly: one failing probe plus
several passing ones must still write the passing ones.

## Adapters

`manual` (paste responses by hand), `command:<cmd>` (conversation as JSON on
stdin, response on stdout — provider-neutral, matching the runtime's own adapter
contract), and `echo` (a stub for testing the harness; it will not produce a
baseline and says so).

## Tests

```
python3 tests/test_fingerprint.py      # 27 invariants
python3 tests/mutate_fingerprint.py    # breaks each one, requires a named test to go red
```

An unapplied mutation exits 3 rather than counting as caught, because a
silently-skipped mutation reads exactly like a successful one.

## On the first audit

The first mutation set caught 6 of 6 on the first run, which was the wrong kind
of reassuring: it was written after the tests, by the same author, from the same
list — so it mutated only what was already covered. Probing where the suite was
*silent* found four real defects it could never have caught, the worst being
that an unscored baseline compared clean against a scored later run. The audit
now stands at 13 mutations, and the four tests that catch those defects came
from looking for gaps rather than from the audit.
