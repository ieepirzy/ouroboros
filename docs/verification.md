# Verification

ouroboros produces hardware. Hardware bugs are expensive: on silicon they're permanent. So verification isn't a phase at the end. It's most of the project, and every other part is built around it.

## Principles

1. **One source of truth for numbers.** The golden model defines what every op computes, bit for bit. The hardware must match it exactly, not approximately.
2. **Every stage is checked.** A bug should surface at the pass that introduced it, not three stages later as wrong output.
3. **Tests must be able to fail.** A test that would pass on a broken implementation is worse than no test, because it creates false confidence.
4. **Measure after routing.** Logic-level estimates of area and power can mislead badly for designs dominated by wiring. Claims about efficiency are made from post-routing numbers.

## The golden model

An executable Python implementation of every op, following the numerics specification (`NUM-01`–`NUM-04`):

- exact integer and floating-point formats,
- rounding modes and saturation versus wrap-around,
- accumulator widths,
- bit-exact approximations of nonlinear functions.

The golden model is itself checked against a floating-point reference (PyTorch) within documented, quantization-derived tolerances. Hardware is checked against the golden model with **zero** tolerance.

## Layers of checking

| Layer | Checks | Tooling |
|---|---|---|
| Golden model vs float reference | Quantization semantics are what we think they are | PyTorch, pytest |
| IR passes | Each transformation preserves the computed function | IR-level interpreters, property tests |
| RTL vs golden model | Bit-exact outputs on test vectors and randomized inputs | Verilator + cocotb |
| Netlist vs RTL | Synthesis and hardware-rewriting passes preserve behaviour | Yosys EQY, SymbiYosys |
| Post-route | Timing closes; results in the place-and-route reports | OpenROAD / OpenSTA |
| Model quality | Accuracy or perplexity of the compiled design on a held-out set | Evaluation harness, golden-model driven |

## Fault injection

The golden model and the simulation flow support injecting faults (`VER-04`):

- stuck-at faults and bit flips in **weights** (as manufacturing defects would cause),
- bit flips in **activations and state** (as soft errors in SRAM would cause),

reported as model accuracy versus fault rate. This lets design decisions account for reliability, and makes hardwired weights' resistance to soft errors measurable.

## Measurement

Every compiled design reports, next to each other:

- area, timing and power **after place-and-route**, plus the synthesis-level estimate for comparison,
- model quality,
- the same metrics for the conventional baseline design (`BASE-01`).

A claimed improvement without the baseline next to it isn't a result.

## Reproducibility

Builds run on a pinned toolchain (`CMP-11`). Place-and-route is sensitive to tool versions and random seeds. Seeds are fixed and recorded, and every reported number can be regenerated from the repository with one command.
