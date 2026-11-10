# Work writing review policy

Apply this policy to PR descriptions and longer work documents. It is review guidance,
not a required boilerplate template, a claim verification source, or a mechanical
"contains TL;DR = safe" check.

## PRs and reports

- Put a short TL;DR at the top, usually a few concise bullets (about 40–60 words is a
  guide, not an arithmetic or authorship gate). A reader should quickly learn the
  problem or user impact, proposed change, and important decision or risk.
- Put attribution in a footer. Keep supporting sections concise and useful: concrete
  example, scope and behavior, why the change is needed, alternatives or workarounds
  when supplied, test or measurement evidence, risks, rollout, and open questions.
- Anticipate the product question (who is blocked, why is this needed, what changes or
  is limited?) and the staff or developer question (root cause, approach, alternatives,
  compatibility, tests, failures, permissions, and rollout risk). Answer only from the
  supplied source. Keep unknowns as questions or explicitly unverified items; do not
  invent urgency, business impact, benchmarks, or missing rationale.
- Give each paragraph one main idea. Split dense blocks even when they are grammatical.
  Use bullets for parallel facts. Do not force a three-item rhythm or remove meaningful
  technical detail merely to shorten the document.

When reviewing a work document, issue a `fix` finding (therefore FAIL under the existing
contract) when the supported lead is buried, opening paragraphs are dense or jargon-heavy,
or a necessary explanation for the proposed change is absent despite source support.
Quote the actual opening or dense passage and its rewrite line. For missing rationale,
quote the relevant proposal passage; never fabricate a quote for absent text. If the
source does not supply the rationale or context, request clarification in the finding
instead of inventing an answer.

## Short comments and prose

- A short comment starts with its answer or action and usually makes one point or a small
  set of bullets. Do not require a TL;DR heading.
- Pure prose can preserve its intended voice and format. Do not force every document
  into headings, bullets, or boilerplate.

## Type selection

The grader's `--document-type` values are `auto`, `comment`, `pr`, `report`, and `prose`.
`auto` uses the original input's word count: 80 words or fewer selects `comment`; longer
input selects `report`. This heuristic is a convenience, not a reliable inference for
every document. Use the override when the document's purpose differs. `pr` and `report`
use the work-document guidance; `comment` and `prose` use the corresponding policies above.
