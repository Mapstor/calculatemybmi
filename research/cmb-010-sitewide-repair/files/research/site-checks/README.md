# Site checks (chat-side, CMB-010)

Browser probes for what the impeccable detector cannot see. They need Python Playwright and Chromium,
which the box does not have; chat runs them (or the Mac). Serve the repo first: `python3 -m http.server 8000`.

| Script | What it finds |
|---|---|
| `text_probe.py BASE OUT.json PATH...` | cut sentences, glued words (needs `pip install wordfreq`), empty sections, title-only boxes, duplicate related links, emoji |
| `ui_probe.py BASE OUT.json PATH...` | call-to-action text with no link, unstyled buttons, broken images, raw entities, undefined/NaN after Calculate, dead links (set `PROBE_ROOT` to the repo) |
| `box_probe.py BASE PATH...` | visible empty boxes, before and after each calculator runs |
| `overflow_menu.py BASE PATH...` | any page wider than the screen at 360/390/1280 px; mobile menu opens and closes |
| `snap_results.py PORT REPO_ROOT` | saves each calculator page with its results open (`_snap/`), so the detector can audit the results panel |

The static half of these checks runs in the box on every page: `scripts/check_content_integrity.py`, imported by
`scripts/check_structure.py`. `patch_cmb010.py` is the CMB-010 build record.
