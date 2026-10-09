---
name: anti-slop-prose
description: Edit pass that strips AI-writing tells from page copy, articles, FAQ answers, meta text and site prose without breaking the content-page structure. Use when drafting, editing or reviewing site text.
---

# anti-slop-prose — edit pass for site prose

Goal: copy that reads like a knowledgeable person wrote it for one reader. Removes the patterns readers, Raptive reviewers and search raters recognize as machine defaults. Never changes a fact, number, unit, source, link or claim, and never adds one.

## Precedence
1. Data integrity (every number traces to the verified registry) and google-ai-content-policy. This pass never touches them.
2. content-page: structure, intro formula, direct-answer block, bold skim layer, stat callouts, FAQ, voice. This pass edits sentences inside that structure and never removes a required element.
3. This skill. On any conflict, the higher level wins.

## Where it runs
- After drafting or editing any page section or site copy, before content-page's pre-publish gate.
- On request: "slop check", "de-slop", "humanize this", or a page review.
- Scope: body prose, intros, direct-answer blocks, FAQ answers, tool-result explanations, meta titles and descriptions, alt text, UI microcopy.
- Out of scope: code, data-table cell values, quotations from sources, proper names and titles, citations, legal pages (privacy, terms).

## Exempt — never "fix" these
- Question headings and FAQ questions: they are the searcher's own words.
- The pain hook's question phrasing taken from the keyword deep-dive.
- Stat callout boxes: quotable by design.
- The bold skim layer (about one bolded phrase per paragraph). Strip bold only past that budget or on generic words.
- Number ranges with an en dash (1991–2020, 40–60 °F) and unit notation.
- Watch-words used literally: robust standard error, map key, gate valve, landscape orientation.
- The single promise line in the intro ("Below: …").

## The pass — strongest tells first

A. Staging instead of stating
1. Not-X-but-Y ("it's not just X, it's Y", "not only … but also") → state Y.
2. Dramatic one-line closers and fragments ("And that changes everything.") → cut, or merge into the previous sentence.
3. Throat-clearing run-ups: "Here's the thing", "Here's why", "It's worth noting", "It's important to note", "When it comes to", "In today's …", "Let's dive in", "The truth is" → open with the point.
4. Pull-quote sayings that sound deep and say nothing → cut.
5. Arguing with no one ("You might think … but") → keep only for a real misconception from the deep-dive.

B. Rhythm by rule
6. Forced triads: three adjectives or benefits by habit → keep only the ones with content. Two is fine.
7. Same opening word or same length for three sentences in a row → vary.
8. Em dashes: at most one per ~300 words of body prose; none in the direct-answer block, meta descriptions, FAQ answers or alt text. Use a comma, colon, parentheses or a new sentence. (Portfolio default; change it here if the rule should be stricter or looser.)
9. Stacked hedges ("may potentially", "can help to", "generally tends to") → one qualifier, only where the uncertainty is real, and say what drives it.
10. Passive voice that hides the actor → name it ("USGS measured …"). Passive stays where the actor doesn't matter (methodology steps).

C. Inflation and borrowed authority
11. AI vocabulary → plain words: delve, tapestry, testament, pivotal, crucial, intricate, meticulous, seamless, robust (figurative), leverage, harness, unlock, elevate, empower, foster, garner, bolster, showcase, underscore / highlight (as verbs), interplay, realm, landscape (abstract), navigate (figurative), vibrant, game-changer, cutting-edge, ever-evolving, "a wide range of", "plays a vital role". Sentence-opening Additionally / Moreover / Furthermore / Notably → "also", or nothing.
12. Inflated significance ("stands as a testament", "marks a pivotal moment") → the plain fact plus its number.
13. Shallow -ing riders (", highlighting the importance of …", ", ensuring …", ", reflecting …") → cut, or turn into a real sentence that carries a fact.
14. Sales language (amazing, incredible, stunning, powerful, effortless, ultimate guide, everything you need to know) → specifics.
15. Vague authority ("experts say", "studies show", "it is widely believed") → name the registry source, or cut.
16. Vague declaratives ("The implications are significant") → name the implication, with the number.
17. Avoiding is / are / has ("serves as", "stands as", "boasts", "features") → is, are, has.

D. Formatting by rule
18. A bold label and colon on every list item → keep the labels only where they carry information; otherwise a plain list or prose.
19. Headings: one case style per site, applied consistently. No emojis, arrows or decorative symbols in headings or body text.
20. Generic endings ("In conclusion", "Overall", "Ultimately" plus a recap) → end on the last useful fact or the next action. No recap section unless content-page asks for one.

E. Leftovers
21. Chat residue: "Certainly!", "Great question", "I hope this helps", "Let me know if", "Sure, here's" → delete.
22. Knowledge-limit hedges ("as of my last update", "while specific details are limited") → state the data date from the registry, or disclose the gap the data-sourcing way.
23. Writing about the page instead of its subject ("This article will explore", "In this guide we'll cover") → cut. The single promise line is the exception.
24. A heading repeated in the section's first sentence, or re-explaining what the reader already has → cut.

## Keep — signals of a real writer
- Specific, local, unusual details; exact numbers with units; named places and sources.
- Contractions, "you" and "we" (content-page voice).
- A parenthetical aside that adds a fact.
- First-person experience only where it is true and Marko has stated it. Never invent anecdotes, tests or experience.

## Output
- Editing: return the revised text, then one line: "anti-slop: N fixes (top types: …)". No commentary inside the text.
- Reviewing: list each hit as pattern number · quote · fix, then tells per 1,000 words. Target: 2 or fewer in body prose.
- In the box: put the fix count in the task's DEVLOG entry when the repo has one.
- Never rewrite a heading's keyword away. Rewrite around it.

## Language
English copy gets the full pass. Slovene copy: apply sections A, B, D and E only; the vocabulary list in C is English.

## Source
Adapted from stop-slop (MIT, © 2025 Hardik Pandya) and humanizer v3.1.0 (MIT, © 2025 Siqi Chen), which draws on Wikipedia's "Signs of AI writing".
