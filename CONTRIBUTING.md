# Contributing to ouroboros

Thanks for your interest. ouroboros is in its design phase, so the most useful contributions right now are feedback on the design ([docs/](docs/)), corrections, and discussion in issues. Once code lands, this guide covers how changes get in.

## The one rule: verification decides when it's done

A compiler for hardware is only as trustworthy as its verification. Expect roughly 70% of the work here to be verification, not code.

A change is **done** when:

1. Every hardware output it affects is checked **bit-exact** against the golden model (see [docs/verification.md](docs/verification.md)).
2. Every transformation it adds or changes has a test that **would fail** if the transformation were wrong. A test that can't fail doesn't count.
3. Every pass that rewrites hardware is covered by an equivalence check between its input and output where feasible (Yosys EQY / SymbiYosys).
4. CI is green on the pinned toolchain.

"It synthesizes" and "the simulation finished" aren't correctness criteria.

## Adding an op

Ops are the main extension point. Adding an op means providing all three parts of its contract:

| Part | What it is |
|---|---|
| **Golden model** | A Python reference implementation following the numerics specification: exact rounding, saturation and widths |
| **Lowering** | How the op becomes hardware: a hardwired lowering, a microcode lowering for the programmable glue unit, or both |
| **Cost model** | An estimate of area, latency and power, so design-space search can reason about it |

Plus tests: golden model against a floating-point reference within documented tolerance, and hardware against the golden model bit-exact.

## Contributions written with AI agents

Agent-written code is welcome, and much of this project will be written that way. The bar is the same for everyone: the human who opens the PR is accountable for it, and the verification rules above apply in full. Agents are very good at producing code that passes weak tests, so reviewers will look hardest at the tests.

## Practical conventions

- **Language:** Python for the compiler (3.11+). Generated hardware is SystemVerilog.
- **Imports** go at the top of the file, never inline.
- **Commits:** small and focused, with a message explaining *why*.
- **Pull requests:** describe what changed, how it was verified, and link the requirement IDs ([docs/requirements.md](docs/requirements.md)) it touches.
- **Scope:** if a PR grows a "while I was here…" section, split it out. New ideas go in an issue labelled `idea`.

## Licensing

ouroboros is licensed under [Apache-2.0](LICENSE). By contributing, you agree that your contributions are licensed under the same terms (Apache-2.0, Section 5), including its patent grant.

## Reporting issues

Bugs, design questions and ideas all go in [GitHub Issues](https://github.com/ieepirzy/ouroboros/issues). For a wrong-output bug, include the model, the compiler configuration and the first point where hardware and golden model disagree.
