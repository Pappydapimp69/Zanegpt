# Suggested GitHub Layout

Add this client as a new `client/` folder. Keep all existing reconstructed/canonical files.

```text
Zanegpt/
├─ knowledge/
├─ persistence/
├─ plugin/
└─ client/
   ├─ zanegpt.py
   ├─ adapters.py
   ├─ repo_loader.py
   ├─ state_store.py
   ├─ prompt_builder.py
   ├─ envelope.py
   ├─ requirements.txt
   └─ config.example.json
```

The loader searches recursively, so exact existing folder names are optional.

Add `.zanegpt/`, `config.json`, and `.env` to `.gitignore` unless you intentionally want to version local runtime state.
