---
name: devlog
description: Per-site DEVLOG.md handoff log for website builds. Use when a DEVLOG.md is pasted or attached, on resume, checkpoint, handoff or new chat, and after every Claude Code task to update the log.
---

# devlog — per-site handoff log

`DEVLOG.md` at the repo root, committed with the code, is the single operational record of a site build. The bar: a fresh chat or Claude Code (CC) session that reads it continues the work without asking anything the file already answers. "The owner" below is the person named in §1 Owner: they run account steps and push.

## 1. The file

Fixed section order. Skeleton:

```markdown
# DEVLOG — example.com
> Handoff file. Read §0–§5 and the last 10 entries of §6 before any work. Rules: devlog skill (.claude/skills/devlog/SKILL.md).

## §0 Resume here
_last update: YYYY-MM-DD · ABC-NNN_
- Phase:
- Last confirmed: ID NAME — what — done|live (commit)
- In flight (handed, NOT confirmed): ID NAME — handed YYYY-MM-DD | none
- Next action: one concrete step (+ prompt ID)
- Waiting on owner: pushes, dashboard work, decisions | none
- Open questions:

## §1 Site card
- Domain · status (dev|live) · Raptive:
- Owner (pushes, runs account steps) · machine:
- Author (byline · credentials · sameAs):
- Repo origin · branch:
- Project folder · box project · preview port (.devcontainer/port):
- Stack · Node in box:
- Commands (dev / build / test / lint):
- Deploy (host, project, trigger; owner pushes):
- Analytics / Search Console / Bing:
- Data sources (or registry path):
- Key paths (pages, components, data/ETL, scripts):
- Skills in repo:
- Design system (DESIGN.md / PRODUCT.md):
- Other plans / ledgers:
- Prompt code: ABC

## §2 Decisions in force
- D-01 · YYYY-MM-DD · decision — why

## §3 Rejected — don't re-propose
- YYYY-MM-DD · idea — why

## §4 Gotchas & hard rules
- trap — what to do instead

## §5 Backlog (priority order)
- [P1] item

## §6 Log (append-only, newest at bottom)
### YYYY-MM-DD · ABC-001 NAME · CC|chat · status
- What:
- Files:
- Verified: exact commands + results; "unverified: …" for anything not run
- Commit: hash (pushed: no)
- Notes:

## §7 History & archive
- YYYY-MM · pre-log history from git log, one line per month
- YYYY-MM-DD · ABC-001…ABC-020 → DEVLOG-ARCHIVE.md · one-line summary
```

### Rules
- §0–§5 are current truth, rewritten in place; superseded lines are deleted there (the §6 entry records the change). §6 is append-only: never edit a past entry — correct it with a new one.
- Size: §0–§5 ≤ 200 lines; §6 ≤ 40 entries of ≤ 8 lines. Past 40, move the oldest 20 verbatim to `DEVLOG-ARCHIVE.md` (append-only) and add a §7 line. Nothing is ever deleted; git keeps every version.
- Absolute dates (YYYY-MM-DD) only.
- Every line must change what a future session does. No transcript, narrative or praise.
- Decisions and rejections always carry the why — without it the next session re-proposes them.
- Unknown = `?`. Never guess to fill a field.
- No secrets (keys, tokens, passwords, .env values). Name the variable, never the value.
- Box containers are ephemeral: record project names and ports, never container IDs.

### Status — the core rule
`planned` → `handed` → `done` → `live`, or `failed` / `blocked` (with the reason and what unblocks it).
- `handed` — prompt given to the owner, not known to have run. Treat as NOT done.
- `done` — CC ran it and the stated verification passed; carries the commit hash.
- `live` — pushed, deployed, checked on the production URL. Set only on the owner's word or a production check that actually ran.
- Chat never upgrades a status by itself. No CC output and no word from the owner = still `handed`.

### Prompt IDs
`ABC-NNN NAME` (e.g. `HWM-042 SCALEFIX`). ABC = the 2–4 letter site code in §1. Next number = highest ID in DEVLOG.md + 1 (the archive only holds older ones). One ID per CC prompt; a re-run gets a new ID that names the one it replaces.

## 2. In Claude Code (the box)

Session start: read §0–§5 and the last 10 §6 entries before touching anything. If this prompt's ID sits in §0 as `handed`, this run resolves it — update that line.

After every task that changed files, data, config, deps or a decision — before saying you're finished:
1. Append the §6 entry. `done` only if the stated verification ran and passed. Report skipped tests by count — a skip is not a pass. UI behaviour (hover, click, layout at a given width) is `unverified` unless a browser-based check actually ran.
2. Rewrite §0 to match reality. New decision → §2, killed idea → §3, new trap → §4, new or resolved issue → §5.
3. Apply the chat notes the prompt's DEVLOG step carried (decisions, rejections, handed items) to the right sections.
4. Commit DEVLOG.md with the work, or as an immediate follow-up commit. Never push — the owner pushes.
5. End the reply with the §6 entry, `git status --short` and `git log --oneline -3`.

Merge conflict in DEVLOG.md: keep every §6 entry from both sides in date order, then rebuild §0 from the merged file.

## 3. In chat (claude.ai)

### Resume — DEVLOG.md pasted or attached, or "resume <site>"
1. No DEVLOG.md in the conversation: if the repo is reachable from chat (GitHub access, a linked folder), read it there and name the commit you read; otherwise ask the owner to attach it, or on a Mac run inside the site's project folder `git pull && LANG=en_US.UTF-8 pbcopy < DEVLOG.md` and paste. If the repo has no DEVLOG.md yet, the first CC prompt is the bootstrap (section 4).
2. Read the whole file. If a memory file exists for the site, read it too and flag any conflict instead of silently picking one.
3. Open with ≤ 8 lines "Where we are": phase · last done/live · every `handed` item (unconfirmed) · next action · waiting on owner. Then continue with the next action.
4. Never build on a `handed` item before seeing its CC output.

### Working
- Every CC prompt gets the next ID, opens with the REPO GUARD line (sentinel: origin URL and DEVLOG.md §1 domain must both match) and ends with the DEVLOG step below.
- Decisions and rejections made in chat since the last prompt ride in that DEVLOG step — that is how chat-only knowledge reaches the repo.
- Chat never writes a full replacement DEVLOG.md: regenerating it from an old chat copy clobbers newer entries. Changes go to CC as notes, applied to the current file.
- CC's own §6 entry is the record; correct it through the next prompt if it's wrong.
- Design tasks: when §1 lists impeccable, name its command in the prompt (e.g. impeccable layout on app/page.tsx) and put the 390 px check from CLAUDE.md in the owner's manual steps.

### Checkpoint — "checkpoint", "handoff", "wrap up", "new chat" (offer one, once, when the chat has run long)
1. Emit an `ABC-NNN CHECKPOINT` CC prompt that writes into DEVLOG.md every chat decision/rejection not yet logged, every `handed` item with its date, the exact next action, open questions and the owner's pending manual steps. Deliver it as plain text at the top of the reply plus a .txt file.
2. Give the carry-over: run the checkpoint prompt → the owner pushes → new chat: paste or attach DEVLOG.md + "resume <site>".
3. Don't call the log updated until CC output shows the commit.

### DEVLOG step — append to every CC prompt
```
DEVLOG (last step): update DEVLOG.md per .claude/skills/devlog/SKILL.md for ID ABC-NNN NAME. Status done only if the verification ran and passed; skipped tests and UI behaviour count as unverified. Also record these chat notes: <decisions / rejections / handed items, or "none">. Commit DEVLOG.md with the work, don't push. End with the §6 entry + git status --short + git log --oneline -3.
```

## 4. Bootstrap (repo without DEVLOG.md)

Evidence only:
- Full `git log --date=short --format='%ad %h %s'` → §7 month-by-month history lines + one §6 bootstrap entry.
- README, CLAUDE.md, docs/, existing ledger/plan/progress/report files, package.json, next.config.*, vercel.json, .vercelignore, .devcontainer/ (port, Node version), .env.example (names only), `ls .claude/skills`, `node -v`.
- Owner and Author come from the prompt or the site's About page and Person schema; never invent credentials.
- Phase from evidence; every `?` field listed under §0 Open questions for the owner.
- Existing ledgers and plans stay where they are; link them from §1. Don't merge or delete them.
- Deploy exposure: if the host serves the repo root as static files (no framework build or output folder), its ignore file (.vercelignore on Vercel) must exclude DEVLOG.md, DEVLOG-ARCHIVE.md, CLAUDE.md, DESIGN.md, .claude/ and .impeccable/. Add missing patterns; never remove existing ones.
- Add this block to CLAUDE.md (create the file if missing; append; never duplicate):

```markdown
## DEVLOG — mandatory
- Before any work: read DEVLOG.md §0–§5 + the last 10 §6 entries.
- After any task that changes files, data, config, deps or a decision: update DEVLOG.md per .claude/skills/devlog/SKILL.md and commit it with the work. Never push.
- `done` only with verification that actually ran; skipped tests and UI behaviour = unverified. No secrets in DEVLOG.md.
```

- Commit `chore: add DEVLOG.md handoff log` (a setup prompt may bundle this with other setup). Don't push.
