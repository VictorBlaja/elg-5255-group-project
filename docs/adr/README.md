# Architecture Decision Records

Each file records one decision that is expensive to reverse or surprising without
its context. The format is deliberately short: context, decision, consequences,
alternatives.

## Index

| ADR | Decision | Reversibility | Primary driver |
|---|---|---|---|
| [0001](0001-two-forecasting-tasks.md) | Two tasks: next-hour demand and next-day baseload | Expensive | Answers two distinct questions from one dataset |
| [0002](0002-chronological-evaluation-split.md) | Chronological 2020-23 / 2024 / 2025 split, no refitting | Expensive | Lag features make random splits leak |
| [0003](0003-exclude-imputed-observations.md) | Exclude imputed values and their full dependency closure | Moderate | Interpolated labels are trivially learnable |
| [0004](0004-hour-ending-timestamp-alignment.md) | Hour-ending EST demand joined to LST weather on one constructed timestamp | Moderate | Prevents a silent one-hour misalignment |
| [0005](0005-baseload-as-daily-minimum.md) | Baseload = daily minimum hourly demand | Cheap | Matches the plain meaning of baseload |
| [0006](0006-model-selection-and-no-hyperparameter-tuning.md) | Persistence + linear + forest, hyperparameters fixed | Cheap | Clean comparison without validation-set contamination |
| [0007](0007-annual-population-feature.md) | Optional annual population, reported both ways | Cheap | Tests whether structural growth adds skill |
| [0008](0008-file-based-numbered-script-pipeline.md) | Numbered scripts with CSV handoffs | Expensive | Rerunnable and inspectable without a toolchain |

"Reversibility" is the cost of changing the decision now: **cheap** means the
code change is local and the reported results would barely move; **moderate**
means results would change and the documentation would need a rewrite;
**expensive** means the study's conclusions or its evaluation protocol would have
to be redone.

## Adding a record

Create `NNNN-short-title.md` with:

```markdown
# ADR-NNNN — Title

| Field | Value |
|---|---|
| Status | Proposed / Accepted / Superseded by ADR-XXXX |
| Date | YYYY-MM-DD |
| Deciders | ... |
| Related | ... |

## Context
## Decision
## Consequences   (Positive / Negative)
## Alternatives considered
## References
```

Guidance:

- Record the decision **when it is made**, not retroactively, if possible. A
  retrospective record should say so in its date line.
- Write down the alternatives that were genuinely considered. An ADR with no
  rejected option is usually a justification, not a decision.
- Prefer concrete numbers over adjectives: "8 of 8,760 rows" beats "a few rows".
- If a later ADR changes this one, mark this file `Superseded by ADR-XXXX`
  rather than deleting it.

## Scope

ADRs here cover choices about the **problem framing, data handling, and
evaluation protocol**. Routine implementation details (variable names, print
formatting) do not need records.
