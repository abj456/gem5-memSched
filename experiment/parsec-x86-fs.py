import argparse

import m5
from m5.objects import Root

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory.multi_channel import DualChannelDDR4_2400
from gem5.components.memory.single_channel import (
    DIMM_DDR5_4400,
    SingleChannelDDR4_2400,
)
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import (
    DiskImageResource,
    KernelResource,
    obtain_resource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# This runs a check to ensure the gem5 binary is compiled to X86 and to the
# MESI Two Level coherence protocol.
requires(
    isa_required=ISA.X86,
    kvm_required=True,
)

from gem5.components.cachehierarchies.classic.private_l1_private_l2_walk_cache_hierarchy import (
    PrivateL1PrivateL2WalkCacheHierarchy,
)
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)

pl1_pl2_walk_cache_hierarchy = PrivateL1PrivateL2WalkCacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size="128KiB",
)

pl1_sl2_cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size="128KiB",
)
# Here we setup a MESI Two Level Cache Hierarchy.
mesi_two_level_cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="128KiB",
    l2_assoc=16,
    num_l2_banks=2,
)

# Following are the list of benchmark programs for parsec.

benchmark_choices = [
    "blackscholes",
    "bodytrack",
    "canneal",
    "dedup",
    "facesim",
    "ferret",
    "fluidanimate",
    "freqmine",
    "raytrace",
    "streamcluster",
    "swaptions",
    "vips",
    "x264",
]
# Following are the input size.

size_choices = ["simsmall", "simmedium", "simlarge"]

parser = argparse.ArgumentParser(
    description="An example configuration script to run the parsec benchmarks."
)
# The arguments accepted are the benchmark name and the simulation size.
parser.add_argument(
    "--benchmark",
    type=str,
    required=True,
    help="Input the benchmark program to execute.",
    choices=benchmark_choices,
)
parser.add_argument(
    "--size",
    type=str,
    required=True,
    help="Simulation size the benchmark program.",
    choices=size_choices,
)
args = parser.parse_args()

total_threads = 4
sleep_time = 3

command = (
    f"cd /home/gem5/parsec-benchmark;"
    + "source env.sh;"
    + f"parsecmgmt -a run -p {args.benchmark} -i {args.size} -n {total_threads};"
    + f"sleep {sleep_time};"
    + "m5 exit;"
)

# Setup the system memory.
sing_dram = SingleChannelDDR4_2400(size="2GiB")
dual_dram = DualChannelDDR4_2400(size="2GiB")
ddr5 = DIMM_DDR5_4400(size="2GiB")

# This is a switchable CPU. We first boot Ubuntu using KVM, then the guest
# will exit the simulation by calling "m5 exit" (see the `command` variable
# below, which contains the command to be run in the guest after booting).
# Upon exiting from the simulation, the Exit Event handler will switch the
# CPU type (see the ExitEvent.EXIT line below, which contains a map to
# a function to be called when an exit event happens).
switch_processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.KVM,
    switch_core_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=total_threads,
)

use_switch_processor = True
# use_switch_processor = False

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="3GHz",
    processor=switch_processor,
    # memory=sing_dram,
    # memory=dual_dram,
    memory=ddr5,
    # cache_hierarchy=pl1_pl2_walk_cache_hierarchy,
    cache_hierarchy=pl1_sl2_cache_hierarchy,
    # cache_hierarchy=mesi_two_level_cache_hierarchy,
)

# Add code here
board.set_kernel_disk_workload(
    kernel=KernelResource(
        local_path="/home/abj456/.cache/gem5/x86-linux-kernel-6.8.0-35-generic",
    ),
    disk_image=DiskImageResource(
        local_path="/home/abj456/full_system_images/disks/x86-ubuntu-24.04-img"
    ),
    kernel_args=[
        "earlyprintk=ttyS0",
        "console=ttyS0",
        "lpj=7999923",
        "root=/dev/sda2",
    ],
    readfile_contents=command,
    # disk_device="/dev/sda2",
)


def exit_event_handler():
    print("First exit: kernel booted")
    yield False  # gem5 is now executing systemd startup
    print("Done bootling Linux")

    print("Second exit: Started `after_boot.sh` script")
    # The after_boot.sh script is executed after the kernel and systemd have
    # booted.
    # Here we switch the CPU type to Timing.
    print("Resetting stats at the start of ROI!")
    m5.stats.reset()
    print("Switching to Timing CPU")
    if use_switch_processor:
        switch_processor.switch()
    yield False  # gem5 is now executing the `after_boot.sh` script

    print("Third exit: Finished `after_boot.sh` script")
    # The after_boot.sh script will run a script if it is passed via
    # m5 readfile. This is the last exit event before the simulation exits.
    print("Dump stats at the end of the ROI!")
    m5.stats.dump()
    yield True


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: exit_event_handler(),
    },
)

print("Running the simulation")
print("Using KVM cpu")


# We start the simulation
simulator.run()
