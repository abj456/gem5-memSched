import argparse

import m5
import m5.simulate
from m5.objects import Root

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory.multi_channel import DualChannelDDR4_2400
from gem5.components.memory.single_channel import (
    DIMM_DDR5_4400,
    DIMM_DDR5_6400,
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

from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)

pl1_sl2_cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size="128KiB",
)

# Following are the input size.
size_choices = ["simsmall", "simmedium", "simlarge"]

parser = argparse.ArgumentParser(
    description="An example configuration script to run the parsec benchmarks."
)
# The arguments accepted are the simulation size.
parser.add_argument(
    "--size",
    type=str,
    required=True,
    help="Simulation size the benchmark program.",
    choices=size_choices,
)
parser.add_argument(
    "--heavy_threads",
    type=int,
    required=True,
    help="Threads number running the benchmark program.",
)
parser.add_argument(
    "--light_threads",
    type=int,
    required=True,
    help="Threads number running the benchmark program.",
)
parser.add_argument(
    "--kvm_ticks",
    type=str,
    default="0.5e12",
    help="Number of ticks to run the KVM simulation before switching to Timing.",
)
parser.add_argument(
    "--mem-model",
    type=str,
    default="DDR4",
    help="Memory model to use for the simulation.",
    choices=["SingDDR4", "DualDDR4", "DDR5_4400", "DDR5_6400"],
)
args = parser.parse_args()

total_threads = args.heavy_threads + args.light_threads
memory_size = "2GiB"
test_size = args.size
sleep_time = 2

# Setup the system memory.
sing_ddr4 = SingleChannelDDR4_2400(size=memory_size)
dual_ddr4 = DualChannelDDR4_2400(size=memory_size)
ddr5_4400 = DIMM_DDR5_4400(size=memory_size)
ddr5_6400 = DIMM_DDR5_6400(size=memory_size)

kvm_sim_ticks = int(float(args.kvm_ticks))

command = (
    # f"./remixed-parsec-workload.sh {test_size} {args.heavy_threads} {args.light_threads};"
    f"./run-{total_threads}core-parsec.sh {test_size};"
    + f"sleep {sleep_time};"
    + "m5 exit;"
)

# This is a switchable CPU. We first boot Ubuntu using KVM, then the guest
# will exit the simulation by calling "m5 exit" (see the `command` variable
# below, which contains the command to be run in the guest after booting).
# Upon exiting from the simulation, the Exit Event handler will switch the
# CPU type (see the ExitEvent.EXIT line below, which contains a map to
# a function to be called when an exit event happens).

simple_processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM,
    isa=ISA.X86,
    num_cores=total_threads,
)

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="5GHz",
    processor=simple_processor,
    # memory=sing_ddr4,
    # memory=dual_ddr4,
    # memory=ddr5_4400,
    # memory=ddr5_6400,
    memory=(
        sing_ddr4
        if args.mem_model == "SingDDR4"
        else (
            dual_ddr4
            if args.mem_model == "DualDDR4"
            else ddr5_4400 if args.mem_model == "DDR5_4400" else ddr5_6400
        )
    ),
    cache_hierarchy=pl1_sl2_cache_hierarchy,
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
)


def exit_event_handler():
    print("First exit: kernel booted")
    yield False  # gem5 is now executing systemd startup
    print("Done booting Linux")

    print("Second exit: Started `after_boot.sh` script")
    # The after_boot.sh script is executed after the kernel and systemd have
    # booted.
    # Here we switch the CPU type to Timing.
    m5.scheduleTickExitFromCurrent(kvm_sim_ticks)
    print("Scheduling exit event for KVM ticks:", args.kvm_ticks)
    yield False  # gem5 is now executing the `after_boot.sh` script

    print("Third exit: Finished `after_boot.sh` script")
    # The after_boot.sh script will run a script if it is passed via
    # m5 readfile. This is the last exit event before the simulation exits.
    yield True


def scheduled_tick_event_handler():
    print("Scheduled tick event handler FIRST called")
    print("Saveing checkpoint")
    simulator.save_checkpoint(
        f"/home/abj456/gem5/experiment/gem5-ckpts/{test_size}-checkpoint-{total_threads}-ckpt-{kvm_sim_ticks / 1e12}sec"
    )

    yield True  # End the simulation


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: exit_event_handler(),
        ExitEvent.SCHEDULED_TICK: scheduled_tick_event_handler(),
    },
)

print("Running the simulation")
print("Using KVM cpu")


# We start the simulation
simulator.run()

print("Simulation finished")
