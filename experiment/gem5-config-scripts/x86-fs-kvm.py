import time

import m5
from m5.objects import Root

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory.multi_channel import (
    DualChannelDDR3_1600,
    DualChannelDDR4_2400,
)
from gem5.components.memory.single_channel import (
    SingleChannelDDR3_1600,
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

# from gem5.components.cachehierarchies.ruby.mesi_three_level_cache_hierarchy import(
#     MESIThreeLevelCacheHierarchy,
# )

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
    l1d_size="128KiB",
    l1d_assoc=8,
    l1i_size="256KiB",
    l1i_assoc=8,
    l2_size="16MiB",
    l2_assoc=16,
    num_l2_banks=2,
)

total_threads = 4
# Setup the system memory.
sing_dram = SingleChannelDDR4_2400(size="2GiB")
dual_dram = DualChannelDDR4_2400(size="2GiB")

# Here we setup the processor.
processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM,
    isa=ISA.X86,
    num_cores=total_threads,
)

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

# use_switch_processor = True
use_switch_processor = False

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="3GHz",
    # processor=processor,
    processor=switch_processor if use_switch_processor else processor,
    memory=sing_dram,
    # memory=dual_dram,
    # cache_hierarchy=pl1_pl2_walk_cache_hierarchy,
    cache_hierarchy=pl1_sl2_cache_hierarchy,
    # cache_hierarchy=mesi_two_level_cache_hierarchy,
)

sleep_time = 3
# command = "m5 exit;"


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
    # readfile_contents=command,
    # disk_device="/dev/sda2",
)


def exit_event_handler():
    if use_switch_processor:
        print("First exit: kernel booted")
        yield False  # gem5 is now executing systemd startup
        print("Done bootling Linux")

        print("Second exit: Started `after_boot.sh` script")
        # The after_boot.sh script is executed after the kernel and systemd have
        # booted.
        # Here we switch the CPU type to Timing.
        print("Switching to Timing CPU")
        print("Resetting stats at the start of ROI!")
        # switch_processor.switch()
        yield False  # gem5 is now executing the `after_boot.sh` script

        print("Third exit: Finished `after_boot.sh` script")
        # The after_boot.sh script will run a script if it is passed via
        # m5 readfile. This is the last exit event before the simulation exits.
        print("Dump stats at the end of the ROI!")
        m5.stats.dump()
        yield False
    else:
        print("m5 exit, end gem5.")
        yield False
        yield False
        yield False
        # yield False


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: exit_event_handler(),
    },
)

# We maintain the wall clock time.

globalStart = time.time()

print("Running the simulation")
print("Using KVM cpu")

m5.stats.reset()

# We start the simulation
simulator.run()

# We print the final simulation statistics.

# print("Done with the simulation")
# print()
# print("Performance statistics:")

# roi_begin_ticks = simulator.get_tick_stopwatch()[0][1]
# roi_end_ticks = simulator.get_tick_stopwatch()[1][1]

# print("roi simulated ticks: " + str(roi_end_ticks - roi_begin_ticks))

# print(
#     "Ran a total of", simulator.get_current_tick() / 1e12, "simulated seconds"
# )
# print(
#     "Total wallclock time: %.2fs, %.2f min"
#     % (time.time() - globalStart, (time.time() - globalStart) / 60)
# )
