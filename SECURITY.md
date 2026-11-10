# Security and data handling

The sanitizer and linter operate locally and use only Python's standard library.
The optional review wrapper reads only the explicitly named original and rewrite,
`references/reviewer.md`, and the rewrite's local linter result. It does not add
credentials, source trees, or other files to its prompt.

## Optional Ringer review

A model review is never part of ordinary cleanup. The user must explicitly request
it and pass `--allow-model-review`, which acknowledges that Ringer sends prompts
to its configured provider and may retain prompts, logs, and artifacts. Those
records may be stored outside the grader's private 0700 run directory. Ringer
configuration and worker behavior are trusted user-controlled tooling, not a hard
security boundary; `redact_spec` does not remove raw worker output or guarantee
privacy. Review output remains untrusted until the wrapper validates its JSON
schema and quoted line evidence.

The wrapper stores private mode-0600 startup snapshots, validates evidence against
the captured rewrite, and rejects PASS verdicts containing blocking, fix, or
unverifiable findings. A schema-valid FAIL is a quality result (exit 1); malformed
worker output or execution failures exit 2.

The removed LiteLLM integration also removed this fork's credential-source
resolver, keychain and 1Password helper paths, saved grader setup, and direct
Sapling upload detector. The grader does not resolve, inspect, or transmit API
credentials itself. Configure provider access through the user's chosen Ringer
installation and worker tooling.

The wrapper retains its private temporary run directory for troubleshooting. It
contains the manifest, prompts, verdicts, and captured Ringer stdout/stderr. Remove
that directory when it is no longer needed. Ringer may create additional logs or
artifacts according to the user's configuration.
