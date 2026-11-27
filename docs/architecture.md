# Architecture

This document describes how ouroboros is meant to be structured. It's a design, not a description of existing code. Where a decision is still open, it says so.

## The core idea

A deployed model is a fixed function: the same compute graph and the same weights on every forward pass. General-purpose accelerators pay for flexibility a fixed model never uses, and they pay above all in data movement, streaming weights from off-chip memory on every generated token.

ouroboros splits a model into what's **static** and what's **dynamic**:

| Static (fixed at compile time) | Dynamic (changes at runtime) |
|---|---|
| Weights and biases | Activations |
| Compute graph | KV cache, recurrent state |
| Tensor shapes (mostly) | Sequence length, batch, concurrent sessions |
| Op sequence | Data-dependent routing (mixture of experts, early exit) |

The static part is compiled into the hardware itself. The dynamic part gets the smallest flexible machinery that can handle it.

## Pipeline

```
Frontend        ONNX · SafeTensors (+ HF config) · PyTorch export
   │
Model IR        graph · constant tensors · shapes · precision
   │            ── quantization, constant folding, fusion, sparsity
Hardware IR     tiles · ROM blocks · constant-multiplier networks · dataflow · schedule
   │            ── design-space search (area, power, timing, quality)
RTL             SystemVerilog · testbenches
   │
Backend         Yosys → OpenROAD / LibreLane → GDSII, reports
```

Every IR is serializable and inspectable. Researchers should be able to insert their own passes at any level (`CMP-13`).

## Three abstractions for extensibility

ouroboros aims to support **any architecture whose weights are fixed**, not one hardcoded model family. Generality comes from the data model, not a plugin framework. Three abstractions exist in the IR from day one, even before the early phases use all of them.

### 1. Op library

Every operation is a contract with three parts:

- **Golden model:** the exact numerical behaviour, in Python.
- **Lowering:** how it becomes hardware, either hardwired or as microcode for the programmable glue unit.
- **Cost model:** estimated area, latency and power for design-space search.

"Supports architecture X" means "X's graph uses only ops in the library." New ops plug in without touching the core.

### 2. State

Runtime state is a first-class object, because it is where architectures differ most:

- a plain MLP has none,
- a transformer has a KV cache that grows with context,
- a state-space model (Mamba-style) keeps a fixed-size recurrent state.

The compiler needs a **generator for state memories**, not a hardcoded KV cache.

### 3. Control

Data-dependent decisions about which hardware runs: the autoregressive decode loop, mixture-of-experts routing, early exit, variable sequence length. These need a small control fabric, not pure dataflow. The mixture-of-experts router itself is an ordinary fixed-weight linear layer.

## Hardwire the weights, keep the glue programmable

Nearly all fixed weights live in **linear operations**: matrix multiplications, projections, convolutions, embedding tables. That holds across MLPs, CNNs, transformers and state-space models. What makes architectures differ is mostly the **weight-free** part: norms, activations, attention scores, routing.

So the default design is hybrid:

- **Linear ops with fixed weights → hardwired.** The same problem in every architecture, and where the efficiency gains are.
- **Weight-free glue → a small programmable vector unit.** A small share of the compute. A new activation function is new microcode, not new silicon.

Hardwiring specific glue ops is still possible later as an optimization.

## Mapping: a dial, not a choice

Each layer sits somewhere on a spectrum:

| | Fully spatial | ROM + shared compute |
|---|---|---|
| Weights live as | Dedicated shift-add networks | Mask ROM bits next to multipliers |
| Cost per weight | ~100+ transistors (logic + accumulation) | A few transistors of storage, plus a shared multiplier |
| Speed | Highest | Lower, time-multiplexed |
| Good for | Small layers, small models | Large layers |

Neither involves fetching weights over a bus. In both, a weight is a local, single-cycle resource.

At scale ROM wins on density. For tiny models, fully spatial is simplest and fastest. The compiler chooses **per layer**, and where the crossover falls (as a function of model size, process node and concurrency) is an open research question this project means to measure.

### Utilization and autoregression

A fully spatial pipeline has a utilization problem in autoregressive decode: token *n+1* can't enter layer 1 until token *n* has left the last layer. Layer depth is an unbreakable dependency, while the autoregressive dependency comes from sampling. Causal attention isn't the obstacle: in a wavefront pipeline, the keys and values a token needs at layer *k* are already computed when it gets there.

Ways to fill the pipeline:

- **Prefill:** prompt tokens are known, so they go down the pipeline as a wavefront.
- **Concurrent sessions:** independent streams occupy different layers.
- **Speculative decoding:** a draft model (or multi-token prediction heads) proposes tokens that are verified in parallel. Wrong guesses cost energy, not latency.

## Backends

Backends are pluggable (`CMP-09`). Planned:

- **Simulation:** Verilator, with cocotb testbenches.
- **FPGA:** Yosys + nextpnr (Lattice ECP5 / iCE40).
- **ASIC, open PDKs:** sky130, GF180MCU and IHP SG13G2 through LibreLane / OpenROAD.
- **Later / research:** commercial PDKs (under NDA, out of tree), and analog backends where weights are conductances in resistive or one-time-programmed devices.

## IR framework

**Status: open.** Decided in Phase 0.

| Option | Pros | Cons |
|---|---|---|
| Standalone Python IR, direct SystemVerilog emission | Fastest to start, no dependencies | Not interoperable; reinvents what CIRCT already does |
| **xDSL dialects + CIRCT command-line backend** (leading option) | Python iteration speed; MLIR-compatible textual IR; CIRCT's `hw`/`comb`/`seq` dialects and ExportVerilog for free; ports to native MLIR later | Depends on xDSL ↔ CIRCT interop holding up; must be confirmed |
| Native MLIR / CIRCT in C++ | Most powerful, best performance, largest ecosystem | Heavy build, unstable APIs, steep learning curve, slow edit-compile loop |

The deciding experiment: round-trip a trivial `hw` module from xDSL through `circt-opt` to SystemVerilog.
