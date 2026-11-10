# Review design notes

## Conceptual review

A Claude Opus 5.5 conceptual review was requested and resolved as a static design
review. It ran no code and measured no quality improvement. Its proposals are not
evaluation results.

Adopted changes: preserve meaning and qualifiers; treat lint matches as leads because
technical terms, invariants, and necessary contrasts can be false positives; make
minimum edits the default for co-written or user-authored technical work; use one
self-check for comments; check PR meaning, verification, and risk; limit long reports
to two passes; require explicit consent for an independent paid reviewer. Unsupported
test claims remain unverified unless the user supplies command output or an artifact
link. The grader can compare drafts but cannot establish whether a test actually ran,
and it does not fetch sources or network evidence.

Implemented writing policy: optional Ringer review loads the bundled
`references/work-writing.md` as trusted guidance and includes a selected document type
in every reviewer task and JSON outcome. `auto` selects `comment` for original input of
80 words or fewer and `report` otherwise; callers can override with `comment`, `pr`,
`report`, or `prose`. This heuristic is not document understanding. PR/report review
checks for a concise TL;DR, readable paragraphs, and supported rationale, citing actual
rewrite lines. Comment and prose modes do not force a TL;DR heading or boilerplate.
These prompts guide review; they do not verify claims or establish that quality improved.

Still proposed and unmeasured: technical lexicon tuning, masked-ratio heuristics, and an
evaluation matrix. The implemented writing policy has not been measured for accuracy or
quality improvement. Do not infer measured effectiveness from its implementation.

## Suggested synthetic evaluation

Eight cases can cover technical invariants, a terse human comment, a meaningful caveat,
quoted code, a valid contrast, an unsupported test-run claim, AI-heavy prose, and
suppression gaming. Judge semantic fidelity and usefulness first; style scores are
secondary. No results are claimed here.
