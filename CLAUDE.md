# CLAUDE.md — calculatemybmi.net

Operational notes for Claude Code / chat sessions on this repo. The runtime truth lives in `DEVLOG.md`; this file holds the standing rules each session must follow.

## DEVLOG — mandatory
- Before any work: read `DEVLOG.md` §0–§5 + the last 10 §6 entries.
- After any task that changes files, data, config, deps or a decision: update `DEVLOG.md` per `.claude/skills/devlog/SKILL.md` and commit it with the work. Never push.
- `done` only with verification that actually ran; skipped tests and UI behaviour = unverified. No secrets in `DEVLOG.md`.

## Prose — anti-slop
- After drafting or editing any page prose, run the anti-slop-prose pass (`.claude/skills/anti-slop-prose/SKILL.md`) before publishing.
- Data rules (every number traces to the verified registry) and the decisions in `DEVLOG.md` §2 win on any conflict with the anti-slop pass.
- The fix count from the pass goes in that task's `DEVLOG.md` §6 entry.

## Content batches
- Chat delivers content changes as `research/<batch>/` packages (zip extracted to `research/<batch>/` with `FIX.md`, `apply_build.py`, `files/`, `manifest.json`).
- Only `apply_build.py` writes files; replacements are hash-guarded so a hand-edited file blocks the next run.
- In batch prompts, no file is edited by hand except `DEVLOG.md` in the final DEVLOG step.

## Design — Impeccable
- R1 — Layout, spacing, alignment, typography and responsive work go through the `impeccable` skill (`layout`, `typeset`, `polish`, `adapt`, `audit`).
- R2 — Refine inside the current look. Never change brand fonts, colors, logo or Raptive ad containers; add no motion or effects (`animate`, `delight`, `overdrive`, `bolder`) unless the prompt asks. The skill's go-bold defaults apply only to an explicitly requested redesign or new page.
- R3 — An intentional choice the detector flags gets a recorded exception (`.claude/skills/impeccable/scripts/impeccable ignores add-value RULE VALUE --reason "WHY"`), never a silent workaround.
- R4 — This box has no browser. After design work, mark layout `unverified` in `DEVLOG.md` and give Marko this Mac 2 check: `cd ~/dev/calculatemybmi && .claude/skills/impeccable/scripts/impeccable detect --viewport 390x844 URL`. For live pages, `URL` is `https://calculatemybmi.net/PATH/`; for unpushed work, `URL` is `http://localhost:8000/PATH/` while `python3 -m http.server 8000` runs in that folder. His result is the verification.
