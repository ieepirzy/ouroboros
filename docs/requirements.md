# Requirements

Numbered requirements for ouroboros. The **Phase** column refers to [ROADMAP.md](../ROADMAP.md). IDs are stable: reference them in issues and pull requests.

The guiding constraint: **the compiler must exploit fixed model weights, not merely produce a conventional programmable accelerator.** The long-term optimization target is useful intelligence per joule and per euro, not raw arithmetic throughput.

## Compiler (`CMP`)

| ID | Requirement | Phase |
|---|---|---|
| CMP-01 | Import Hugging Face model configurations and SafeTensors checkpoints. A checkpoint holds weights and a config, not a graph, so this means one importer per architecture family. | II |
| CMP-02 | Accept ONNX as a general-purpose graph input. | I |
| CMP-03 | Produce a normalized model intermediate representation. | I |
| CMP-04 | Distinguish compile-time constants (weights) from runtime state (activations, KV cache, recurrent state). | I |
| CMP-05 | Support configurable weight and activation quantization. | I |
| CMP-06 | Perform constant folding, sparsity exploitation and operator fusion. | I |
| CMP-07 | Produce hardware-specific intermediate representations. | I |
| CMP-08 | Produce synthesizable SystemVerilog. | I |
| CMP-09 | Support pluggable semiconductor process backends. | I (open PDKs), III (commercial) |
| CMP-10 | Produce physical layouts suitable for fabrication. | I |
| CMP-11 | Produce reproducible, versioned build artifacts from a pinned toolchain. | 0 |
| CMP-12 | Produce simulation and hardware verification suites. | I |
| CMP-13 | Expose every intermediate representation so researchers can implement and benchmark their own passes. | I |

## Hardware optimization (`OPT`)

| ID | Requirement | Phase |
|---|---|---|
| OPT-01 | Constant-coefficient arithmetic (shift-add networks, e.g. canonical signed digit encoding). | I |
| OPT-02 | Shared partial-product computation (multiple constant multiplication). | I |
| OPT-03 | Zero-weight connection elimination. | I |
| OPT-04 | Mask ROM generation. | I.5 |
| OPT-05 | Compute-memory colocation. | I.5 |
| OPT-06 | Automatic compute tile sizing. | I.5 |
| OPT-07 | Pipeline optimization. | II |
| OPT-08 | Physical interconnect optimization. | II |
| OPT-09 | Automated design-space exploration. | I.5 |
| OPT-10 | Pareto optimization across power, performance, area **and model quality** (see `QUA-01`). | I.5 |
| OPT-11 | Multi-die model partitioning. | III |
| OPT-12 | Metal-layer-only model specialization where the process supports it. | III |

## Numerics (`NUM`)

Without exact numerics there is nothing precise to verify against. These come first.

| ID | Requirement | Phase |
|---|---|---|
| NUM-01 | An executable golden model is the single source of truth for numerical behaviour. | 0 |
| NUM-02 | Document integer and floating-point formats, rounding modes and saturation versus wrap-around for every op. | 0 |
| NUM-03 | Document accumulator widths, and how they're derived from weight and activation widths. | 0 |
| NUM-04 | Specify approximations of nonlinear functions (exp, reciprocal, rsqrt, …) bit-exactly, with documented error bounds. | II |

## Verification (`VER`)

| ID | Requirement | Phase |
|---|---|---|
| VER-01 | Hardware outputs match the golden model bit-exactly for every compiled design. | I |
| VER-02 | Python testbenches (cocotb) drive simulated hardware from the golden model. | I |
| VER-03 | Equivalence checking between pipeline stages where feasible. | I |
| VER-04 | Fault-injection hooks in the golden model and in simulation (weights and activations separately). | I.5 |

## Quality (`QUA`)

| ID | Requirement | Phase |
|---|---|---|
| QUA-01 | Measure model quality (accuracy, perplexity) for every quantized or approximated design and report it next to power, performance and area. | I |

## Baseline (`BASE`)

| ID | Requirement | Phase |
|---|---|---|
| BASE-01 | Generate a conventional design for the same model (weights in SRAM, generic MAC array) through the same flow, so every gain is measured against a real reference. | I |

## Interfaces and test (`IF`, `DFT`)

| ID | Requirement | Phase |
|---|---|---|
| IF-01 | A defined host interface for streaming inputs and outputs. For language models: tokens in, tokens out, tokenizer off-chip. | II |
| DFT-01 | Design-for-test structures (scan chains, ROM self-test) in fabrication-bound designs. | III |

## Architecture support

| Phase | Operations |
|---|---|
| **I: Prototype** | Matrix-vector multiplication, linear layers and biases, activation functions, MLPs, INT4 / INT8 arithmetic |
| **II: Small LLMs** | RMSNorm and LayerNorm, RoPE, multi-head and grouped-query attention, softmax and SwiGLU, dynamic KV cache, autoregressive generation, FP4 / FP8 arithmetic |
| **III: Industrial scale** | Mixture-of-experts routing, multi-head latent attention, expert parallelism, cross-die execution, programmable LoRA adapters, long-context inference, concurrent inference sessions |
