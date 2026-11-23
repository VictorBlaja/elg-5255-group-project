# Documentation

Project documentation for the ELG 5255 Ottawa electricity demand forecasting study.

| Document | Purpose |
|---|---|
| [PRD.md](PRD.md) | What the system must do: goals, scope, functional/non-functional requirements, success metrics, acceptance criteria |
| [DESIGN.md](DESIGN.md) | How it does it: architecture, data model, time alignment, evaluation protocol, and the decisions behind them |
| [adr/](adr/) | Architecture Decision Records — one file per irreversible or surprising choice |

## Reading order

1. **PRD** for the problem and the contract the system is held to.
2. **DESIGN** for the pipeline and the reasoning behind its shape.
3. **ADRs** for the specific alternatives that were rejected and why.

## Conventions

- Paths are relative to the repository root.
- Script names are given as `NN_name.py` and run in numeric order from `coding/`.
- All figures quoted in these documents were re-verified against the CSVs in
  `coding/data/processed/` on 2026-11-23, not copied from the project write-up
  (`coding/coding explainer or readme.docx`).
- Any statement that is an author's claim rather than a verified measurement is
  labelled as such.
