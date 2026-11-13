# CLAUDE.md — calculatemybmi.net

Operational notes for Claude Code / chat sessions on this repo. The runtime truth lives in `DEVLOG.md`; this file holds the standing rules each session must follow.

## DEVLOG — mandatory
- Before any work: read `DEVLOG.md` §0–§5 + the last 10 §6 entries.
- After any task that changes files, data, config, deps or a decision: update `DEVLOG.md` per `.claude/skills/devlog/SKILL.md` and commit it with the work. Never push main. Push only `claude/` branches. A chat that does the work itself merges its own PR by DEVLOG D-24 (merge commit, after the tests and its Chrome check on the preview); otherwise the owner merges.
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
- R4 — After design work, mark layout `unverified` in `DEVLOG.md` until chat checks it in Claude in Chrome: the Vercel preview before the merge at desktop and phone width (D-25), the live page after it, on a few pages only because the site shows live ads. No owner phone test and no Mac detector run.
- R5 — No Impeccable self-updates inside a task (`impeccable update`, `npx impeccable update`, `install`). If impeccable context reports `UPDATE_AVAILABLE`, note it in `DEVLOG.md` §0 and carry on; the owner updates on the Mac, engines included.
