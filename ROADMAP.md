# Roadmap

ouroboros grows from the smallest thing that proves the idea toward frontier-scale models. Each phase has exit criteria, and no phase starts before the previous one's exit criteria are met. New ideas go into the [backlog](#backlog), not the current phase.

Requirement IDs refer to [docs/requirements.md](docs/requirements.md).

---

## Phase 0: Foundations

Settle the decisions everything else depends on before writing compiler code.

- [ ] **IR framework decision.** Round-trip a trivial `hw` module from xDSL (Python) through CIRCT's `circt-opt` to SystemVerilog. If it works cleanly, adopt xDSL dialects with a CIRCT backend. If not, fall back to a standalone Python IR with direct SystemVerilog emission. See [docs/architecture.md](docs/architecture.md#ir-framework).
- [ ] **Numerics specification** (`NUM-01`–`NUM-04`): integer formats, rounding, saturation, accumulator widths.
- [ ] **Golden model v0**: an executable Python reference implementing the numerics spec for linear layers and ReLU.
- [ ] **Reproducible environment** (`CMP-11`): pinned toolchain via Nix or the IIC-OSIC-TOOLS container, and CI that runs the test suite.
- [ ] **Project hygiene**: Python package layout, linting and type checking, issue and PR templates.

**Exit:** the IR decision is recorded, and the golden model matches PyTorch within the documented quantization semantics.

## Phase I: Prototype, a tiny MLP end to end

Prove that exploiting fixed weights beats a conventional design, measured after place-and-route.

**Target model:** a small MNIST MLP (around 100k parameters), INT8 weights and activations.

- [ ] ONNX frontend (`CMP-02`) → Model IR (`CMP-03`) with constants and runtime state separated (`CMP-04`)
- [ ] Quantization to INT8 / INT4 (`CMP-05`), constant folding and zero-weight elimination (`CMP-06`, `OPT-03`)
- [ ] Hardware IR with a per-layer spatial ↔ temporal mapping choice (`CMP-07`)
- [ ] Constant-coefficient arithmetic via canonical signed digit (CSD) shift-add networks (`OPT-01`); shared partial products within a row (`OPT-02`)
- [ ] SystemVerilog emission (`CMP-08`)
- [ ] **Baseline generator** (`BASE-01`): the same model as a conventional SRAM-weights + MAC-array design
- [ ] Verilator + cocotb testbenches, bit-exact against the golden model (`VER-01`, `VER-02`)
- [ ] Yosys synthesis and LibreLane / OpenROAD place-and-route on sky130 (`CMP-10`)
- [ ] Report comparing area, timing and power for hardwired versus baseline, **after routing**, next to Yosys's pre-routing estimates

**Exit:** a reproducible chart, from one command, showing the hardwired design against the baseline after place-and-route, with every design verified bit-exact. This is the first public result.

### Phase I.5: Real hardware

- [ ] Run the Phase I design on an open-toolchain FPGA (Lattice ECP5 / iCE40 with Yosys + nextpnr)
- [ ] Mask ROM generation (`OPT-04`) and a ROM-versus-logic comparison per layer
- [ ] Automated design-space exploration over the mapping dial (`OPT-09`, `OPT-10`), with model accuracy as an objective alongside area, power and timing (`QUA-01`)
- [ ] **First silicon:** a small model on a real shuttle (see below)

#### First silicon plan

**Target:** an 8×8 handwritten-digit classifier (64 → 16 → 10, about 1,200 INT4 weights), using ROM plus a shared multiply-accumulate unit, time-multiplexed, with inputs streamed serially through the narrow pin I/O.

- [ ] Validate the exact RTL on an iCE40 / ECP5 FPGA board before submitting
- [ ] Put the **hardwired design and the conventional baseline on the same shuttle**, so the comparison is measured on real silicon under identical conditions
- [ ] Expose internal state through a debug/readout path, to support later fault-injection and reliability work
- [ ] Submit to a Tiny Tapeout shuttle (sky130, IHP or GF). Rough estimate: 20–40 tiles for both designs. Expect about a year from submission to chips in hand
- [ ] Alternative for a full die: a wafer.space GF180 run (check current pricing before budgeting)

Area estimates are rough (a sky130 tile is on the order of a thousand gates). Firm numbers come from the Phase I flow.

## Phase II: Small transformers

Autoregressive generation with a small LLM (on the order of millions to tens of millions of parameters).

- [ ] Op library: RMSNorm / LayerNorm, RoPE, softmax, SwiGLU, multi-head and grouped-query attention
- [ ] Programmable glue unit for weight-free ops (norms, activations, attention scores)
- [ ] State abstraction and a generator for state memories: dynamic KV cache (`CMP-04`)
- [ ] Control abstraction: autoregressive decode loop, sequence-length handling
- [ ] FP8 / FP4 formats
- [ ] Hugging Face importers, one architecture family at a time (`CMP-01`)
- [ ] Host interface: token in, token out; the tokenizer stays off-chip (`IF-01`)
- [ ] Wavefront pipelining for prefill; speculative-decoding support to fill the pipeline during decode
- [ ] Pipeline optimization and timing closure for deep adder trees (`OPT-07`)

**Exit:** a small transformer generates text in simulation and on FPGA, bit-exact against the golden model.

## Phase III: Frontier architectures

Industrial scale. Realistically needs funding and commercial process access.

- [ ] Mixture-of-experts routing and expert parallelism
- [ ] Multi-head latent attention
- [ ] Multi-die partitioning and cross-die execution (`OPT-11`)
- [ ] Metal-layer-only model specialization where the process allows it (`OPT-12`)
- [ ] Programmable LoRA adapters in SRAM
- [ ] Long-context inference; concurrent sessions to fill spatial pipelines
- [ ] Commercial PDK backends (`CMP-09`)
- [ ] Design-for-test: scan chains and ROM self-test (`DFT-01`)

---

## Research tracks

These run alongside the phases and produce results in their own right.

- **Spatial / temporal crossover.** At what model size, process node and concurrency does dissolving weights into logic stop paying off against ROM plus shared compute?
- **Physical reality versus logical estimates.** How well do synthesis-level metrics predict post-routing area, timing and power for constant-weight designs? Building fast, calibrated cost models for design-space search.
- **Reliability of hardwired models.** Fault injection into weights and activations; accuracy degradation versus fault rate; mask ROM's immunity to soft errors; aging under a constant workload; using defect tolerance to raise effective yield.
- **Analog backends.** Weights as conductances in resistive or one-time-programmed devices. Fixed weights remove the drift problem that holds back analog in-memory compute.

## Backlog

Ideas that are interesting but not scheduled:

- Diffusion language models (non-autoregressive, a natural fit for fully spatial hardware)
- Hardwired draft model on the same die for speculative decoding
- Aging-aware placement
- A CIRCT-native (C++) path for performance-critical passes
