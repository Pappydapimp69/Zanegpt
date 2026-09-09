# ZaneGPT Persistence Layer

This directory contains the reconstructed persistence/control layer intended for a GitHub-hosted implementation.

## Files
- `defensive_protocols.md`
- `hacker_flag.md`
- `post_turn_5_behavior.md`
- `persistence_runtime.md`
- `session_state_schema.json`
- `persistence_event_schema.json`

## Provenance labels
- **Recovered:** directly supported by surviving ZaneGPT instructions.
- **Reconstructed:** inferred from surviving architecture, behavior files, and observed ZaneGPT behavior.
- **Implementation specification:** newly written glue for a persistent plugin/agent.

## Known recovered architecture
`Defensive Protocols -> Hacker Flag -> Trait Engines -> Post-Turn-5 Behavior`

The Trait Engines themselves are separately recovered at high confidence. The missing pieces in this folder are deliberately labeled reconstructed where exact original wording or thresholds were not recovered.

## Design principle
Session adaptation should be immediate.
Persistent learning should be conservative, evidence-backed, reversible, and provenance-preserving.
