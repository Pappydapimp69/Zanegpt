from pathlib import Path

REQUIRED = [
    "SYSTEM_LAYER.md",
    "user_behavior_runtime.md",
    "user_behavior_database.md",
    "defensive_protocols.md",
    "hacker_flag.md",
    "TRAIT_ENGINE_RUNTIME.md",
    "post_turn_5_behavior.md",
    "PERSISTENCE_POLICY.md",
]

def find_one(repo: Path, filename: str):
    matches = [p for p in repo.rglob(filename) if ".git" not in p.parts and ".zanegpt" not in p.parts]
    matches.sort(key=lambda p: (len(p.relative_to(repo).parts), str(p)))
    return matches[0] if matches else None

def load_resources(repo, include_evidence=False, include_changelog=False, max_resource_chars=180000):
    repo = Path(repo).resolve()
    names = list(REQUIRED)
    if include_evidence:
        names.append("user_behavior_evidence.jsonl")
    if include_changelog:
        names.append("user_behavior_changelog.md")

    resources, missing = {}, []
    for name in names:
        p = find_one(repo, name)
        if not p:
            if name in REQUIRED:
                missing.append(name)
            continue
        resources[name] = {
            "path": str(p.relative_to(repo)),
            "content": p.read_text(encoding="utf-8", errors="replace")
        }

    if missing:
        raise FileNotFoundError("Missing required ZaneGPT files:\n- " + "\n- ".join(missing))

    total, capped = 0, {}
    for name, item in resources.items():
        remaining = max_resource_chars - total
        if remaining <= 0:
            break
        content = item["content"][:remaining]
        capped[name] = {**item, "content": content}
        total += len(content)
    return capped
