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

Proposed but not implemented or measured: technical profiles, masked-ratio heuristics,
and an evaluation matrix. Do not infer measured accuracy from the review.

## Suggested synthetic evaluation

Eight cases can cover technical invariants, a terse human comment, a meaningful caveat,
quoted code, a valid contrast, an unsupported test-run claim, AI-heavy prose, and
suppression gaming. Judge semantic fidelity and usefulness first; style scores are
secondary. No results are claimed here.
