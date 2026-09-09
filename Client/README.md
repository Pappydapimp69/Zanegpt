# ZaneGPT LLM Client

Thin host client for the LLM-native ZaneGPT package.

Each turn it loads ZaneGPT's instruction/behavior files and persistent session state,
sends them directly to the selected LLM, lets the LLM perform the behavioral inference,
then stores the returned state update and provisional observations.

No separate plugin server is required.

## Install

```bash
pip install -r requirements.txt
cp config.example.json config.json
```

Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

## Run

```bash
python zanegpt.py --repo /path/to/Zanegpt
```

The repository loader searches recursively, so your existing GitHub layout does not need
to be destroyed or reorganized.

Runtime state is stored under `<repo>/.zanegpt/`. Canonical knowledge is never silently rewritten.
