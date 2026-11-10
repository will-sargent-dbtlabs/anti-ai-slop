# Human drafts

Load this when the draft is the user's own writing rather than a model's, or when
they say the piece already sounds like them and they only want the AI residue out.

The default scrub assumes there is no voice to protect and cuts accordingly. That
assumption is wrong here, and applying it produces a draft that is clean, correct,
and no longer belongs to anyone.

## What changes

**Make the minimum effective edit.** Fix the AI patterns, the errors, and the
passages that are genuinely hard to follow. Leave everything else. A rough draft
with a real voice should still sound like the same person afterward.

**Read for voice before you touch anything.** Note the writer's vocabulary,
sentence cadence, bluntness, humor, uncertainty, digressions, and how polished
they are trying to be. Those are the traits to keep. Hold them in mind while you
edit rather than writing them down for the user.

**Keep the edge.** Strong opinions, blunt language, profanity, self-interruptions,
and honest admissions belong to the writer. Do not round them off into something
more professional. If the user wanted safe, they would not be asking for this.

**Keep the shape.** Preserve their progression and their detours. If you reorganize
anything, say why in the summary rather than doing it silently.

**Do not tidy uniformly.** Making every paragraph equally polished is its own tell.
Uneven polish is what human drafts look like.

## Where the lists still apply

The vocabulary, phrase, and template rules hold. A human writer who leaned on
"delve" or closed on a fake-profound kicker still wants those gone.

What softens is the empty-word list. "Just," "honestly," "actually," and "I think"
are often filler, but in a person's writing they carry spoken rhythm, hedging they
meant, or self-awareness. Cut them where they delay the point. Keep them where
they sound like the writer talking.

Same for fragments, long spoken sentences, and abrupt changes in pace. Fix those
when they obscure the meaning. Keep them when they are how this person writes.

## The gate still runs

Run the linter and one self-check; a subagent or repeated rewrite is not required.
Use an independent reviewer only when requested. If used, ask it to check whether
the edit erased the writer. Tell it the draft is
human-written and ask it to flag any line where the rewrite sounds more like a
competent stranger than like the original author.

Expect a lower linter score than a full scrub produces, and accept it. Suppress
the findings you are deliberately keeping with a rule ID, such as `<!-- slop-ignore W1 -->`, and explain the reason separately.
A draft at 82 that still sounds like the person who wrote it beats a 100 that
does not.

## The test

Read the edited draft and the original side by side. Would the writer recognize
the edit as their own sentences, tightened? If it reads as someone else's cleaner
version of their point, you cut too much.
## Work writing

For PR descriptions and longer work documents, lead with a concise TL;DR at the top:
the problem or user impact, the proposed change, and the main decision or risk. Keep it
short enough to scan in about ten seconds; a few bullets and roughly 40–60 words are
guides, not strict gates. Put attribution in a footer.

Then answer likely product and reviewer questions using supplied evidence: who is blocked,
why the change is needed, what changes, root cause, alternatives, compatibility, tests,
failures, permissions, and rollout risk. Leave unsupported answers as questions or mark
them unverified. Give each paragraph one idea, split dense blocks, and use bullets for
parallel facts. Preserve meaningful technical terms and avoid forced three-item lists.

Short comments start with the answer or action. Pure prose keeps its intended voice and
format; neither needs a mandatory TL;DR heading.

Generic example:

> **TL;DR**
> - The import currently drops empty records.
> - Preserve them and add a regression check.
> - Confirm downstream consumers accept the change before rollout.
>
> The parser skips records with no fields. The source does not say whether consumers
> rely on that behavior, so compatibility needs confirmation.
