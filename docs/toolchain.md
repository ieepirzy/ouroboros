# Toolchain

ouroboros builds on the free and open-source EDA ecosystem. This page lists the tools by pipeline stage, and what each is planned for.

## Synthesis

| Tool | Use |
|---|---|
| [Yosys](https://github.com/YosysHQ/yosys) (with ABC) | Logic synthesis, area estimates |
| [yosys-slang](https://github.com/povik/yosys-slang) / [sv2v](https://github.com/zachjs/sv2v) | SystemVerilog frontend support. Yosys's native SystemVerilog coverage is limited |

## Simulation and testbenches

| Tool | Use |
|---|---|
| [Verilator](https://github.com/verilator/verilator) | Main simulator: compiles RTL to fast C++ |
| [cocotb](https://github.com/cocotb/cocotb) | Python testbenches, driven by the golden model |
| [Icarus Verilog](https://github.com/steveicarus/iverilog) | Slower, forgiving simulator for debugging |

## Formal verification and equivalence

| Tool | Use |
|---|---|
| [EQY](https://github.com/YosysHQ/eqy) | Equivalence checking between pipeline stages |
| [SymbiYosys](https://github.com/YosysHQ/sby) | Formal property checking |
| Bitwuzla, Boolector, Z3 | SMT solvers used by the above |

## Physical design

| Tool | Use |
|---|---|
| [OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD) | Floorplanning, placement, clock tree synthesis, routing; OpenSTA for timing |
| [LibreLane](https://github.com/librelane/librelane) | Flow orchestration (the successor to OpenLane 2). A Python library, so ouroboros can drive flows programmatically. Apache-2.0 |
| [OpenROAD-flow-scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts) | Alternative, research-oriented flow |

## Physical verification and viewing

| Tool | Use |
|---|---|
| [Magic](https://github.com/RTimothyEdwards/magic) | DRC, parasitic extraction |
| [KLayout](https://github.com/KLayout/klayout) | Layout viewing, DRC/LVS decks, Python scripting |
| [Netgen](https://github.com/RTimothyEdwards/netgen) | LVS |

## Memory

| Tool | Use |
|---|---|
| [OpenRAM](https://github.com/VLSIDA/OpenRAM) | SRAM generation for activations and KV caches. ROM support still to be evaluated (`OPT-04`) |

## Compiler infrastructure

| Tool | Use |
|---|---|
| [xDSL](https://github.com/xdslproject/xdsl) | Python-native, MLIR-compatible framework for ouroboros's own dialects (pending the Phase 0 decision) |
| [CIRCT](https://github.com/llvm/circt) | Hardware dialects (`hw`, `comb`, `seq`, `sv`) and SystemVerilog export |
| [onnx](https://github.com/onnx/onnx) | Graph frontend |

## Open process design kits

| PDK | Node | Notes |
|---|---|---|
| SkyWater sky130 | 130 nm | Most mature, most examples. Phase I default |
| GF180MCU | 180 nm | Cheapest route to real chips today via wafer.space shuttles |
| IHP SG13G2 | 130 nm | Fabricated in Germany. Shuttle chips are loaned and shipped within the EU / Switzerland |

## FPGA

| Tool | Use |
|---|---|
| Yosys + [nextpnr](https://github.com/YosysHQ/nextpnr) | Fully open flow for Lattice iCE40 and ECP5 |

## Fabrication routes

- [Tiny Tapeout](https://tinytapeout.com): small tiles on shared shuttles (Sky, IHP, GF). Enough for a toy model.
- [wafer.space](https://wafer.space): GF180MCU shuttle runs with around a thousand chips of a full die per order.

## Environment

The whole toolchain is available through Nix (LibreLane's preferred route) or the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container. ouroboros pins one of these so every build is reproducible (`CMP-11`).
