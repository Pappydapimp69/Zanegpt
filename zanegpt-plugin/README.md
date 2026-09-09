# ZaneGPT Plugin

A skill-only plugin packaging the ZaneGPT interaction style as reusable behaviour.

## Contents
- `.claude-plugin/plugin.json` — the plugin manifest.
- `skills/zanegpt/SKILL.md` — the ZaneGPT behaviour skill.

`skills/` is the default location Claude Code scans, so the manifest does not
name the skill path explicitly — listing it there as well risks registering the
same skill twice.

## Install in Claude Code

The repository root is a plugin marketplace, so this installs straight from
GitHub — no download, no unzip:

```
/plugin marketplace add Pappydapimp69/Zanegpt
/plugin install zanegpt@zanegpt
```

Then `/zanegpt` invokes it, and Claude will reach for it on its own when a
request matches the `description` in the skill's frontmatter.

To check what was installed: `claude plugin details zanegpt@zanegpt`.

## Import through GitHub (OpenAI / Codex)

1. In an eligible ChatGPT workspace, go to Workspace settings → Plugins → Add →
   Import marketplace.
2. Enter this repository's URL.
3. Import and review the plugin's installation policy.
4. In Codex, open Sources → Use plugins and select ZaneGPT once available.

OpenAI notes that plugin/skill availability depends on plan, workspace, role,
region, and product surface.

`../zanegpt-plugin.zip` at the repository root is generated from this directory
for surfaces that want an archive. It is a copy, not the source — regenerate it
rather than editing it:

```bash
cd <repo root> && rm -f zanegpt-plugin.zip && zip -qr zanegpt-plugin.zip zanegpt-plugin
```

## Note on the skill's frontmatter

`SKILL.md` carries YAML frontmatter with `name` and `description`. Claude Code
discovers and triggers a skill by exactly those two fields; without frontmatter
the file loads as an ordinary markdown document and never fires. The body below
the frontmatter is the behaviour itself and is unchanged.

## Optional next step
Add a GitHub-backed app/MCP capability if you want ZaneGPT to read or act on
repositories, rather than only contribute reusable behaviour.
