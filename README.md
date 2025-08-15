# Memory Scheduler Research on gem5

This repository contains all source code, configuration scripts, and 
experiment resources for evaluating memory scheduling algorithms (ATLAS) 
in multicore systems using the gem5 full-system simulator.

The gem5 simulator is a modular platform for computer-system architecture
research, encompassing system-level architecture as well as processor
microarchitecture. It is primarily used to evaluate new hardware designs,
system software changes, and compile-time and run-time system optimizations.

The main website can be found at <http://www.gem5.org>.

## How to Get Started

This project is recommended to be run with gem5 version 24.1.0.2 on Ubuntu 24.04.
Since **perf** is required in full system mode if you need complete stats of every simulation,
please running gem5 on host OS if possible, not on virtual machine or WSL.
For detailed setup instructions and required dependencies, please see the steps below.

1. Install gem5 and all required dependencies as <http://www.gem5.org/documentation/general_docs/building> said.
2. Execute `scons build/{ISA}/gem5.opt` to build an optimized version of the gem5 binary (`gem5.opt`) containing the needed ISA. If you want to use KVM to accelerate simulation, please choose the ISA same as the host CPU.
3. Obtain kernel binaries and disk images you need from <https://resources.gem5.org>. This project used [x86-ubuntu-24.04-img](https://resources.gem5.org/resources/x86-ubuntu-24.04-img?version=4.0.0) and [x86-linux-kernel-6.8.0-35-generic](https://resources.gem5.org/resources/x86-linux-kernel-6.8.0-35-generic?version=1.0.0) for running [PARSEC benchmark](https://github.com/cirosantilli/parsec-benchmark).
4. Adjust the size of the disk image you downloaded and install PARSEC benchmark. You could do these with QEMU or other disk tools.
5. Run full system simulations with disk images or checkpoints.

## New Source Code & Config Scripts

All source codes related with ATLAS memory scheduling algorithm and meta controller are under `src/mem/` directory. You could trace code from `SConsript` and `MemCtrl.py`.
Config scripts added in this project are in the `experiment/gem5-config-scripts/`.

## Building gem5

To build gem5, you will need the following software: g++ or clang,
Python (gem5 links in the Python interpreter), SCons, zlib, m4, and lastly
protobuf if you want trace capture and playback support. Please see
<http://www.gem5.org/documentation/general_docs/building> for more details
concerning the minimum versions of these tools.

Once you have all dependencies resolved, execute
`scons build/ALL/gem5.opt` to build an optimized version of the gem5 binary
(`gem5.opt`) containing all gem5 ISAs. If you only wish to compile gem5 to
include a single ISA, you can replace `ALL` with the name of the ISA. Valid
options include `ARM`, `NULL`, `MIPS`, `POWER`, `RISCV`, `SPARC`, and `X86`
The complete list of options can be found in the build_opts directory.

See https://www.gem5.org/documentation/general_docs/building for more
information on building gem5.

## gem5 Resources

To run full-system simulations, you may need compiled system firmware, kernel
binaries and one or more disk images, depending on gem5's configuration and
what type of workload you're trying to run. Many of these resources can be
obtained from <https://resources.gem5.org>.

More information on gem5 Resources can be found at
<https://www.gem5.org/documentation/general_docs/gem5_resources/>.

