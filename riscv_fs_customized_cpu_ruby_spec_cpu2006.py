"""
This script runs SPEC CPU2006 benchmarks on a RISC-V full system simulation using 
a customized SiFive out-of-order CPU with a Ruby cache hierarchy.

Characteristics:
- Runs exclusively on the RISC-V ISA
- Uses Ruby cache coherence protocol
- SiFive out-of-order CPU configuration
- SPEC CPU2006 benchmark support

Usage:
------

```
scons build/RISCV/gem5.opt
./build/RISCV/gem5.opt configs/tutorial/riscv_sifive_ruby_spec.py \
    --image <full_path_to_the_spec-2006_disk_image> \
    --partition <root_partition_to_mount> \
    --benchmark <benchmark_name> \
    --size <simulation_size>
```
"""

import argparse
import os
import time

import m5
from m5.objects import RiscvO3CPU
from m5.stats.gem5stats import get_simstat
from m5.util import warn

from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource, DiskImageResource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.utils.requires import requires

# Ruby-related import
from gem5.components.cachehierarchies.ruby.mi_example_cache_hierarchy import (
    MIExampleCacheHierarchy,
)

# Run a check to ensure the right version of gem5 is being used
requires(isa_required=ISA.RISCV)

# Define SPEC CPU2006 benchmark choices
benchmark_choices = [
    "400.perlbench",
    "401.bzip2",
    "403.gcc",
    "410.bwaves",
    "416.gamess",
    "429.mcf",
    "433.milc",
    "435.gromacs",
    "436.cactusADM",
    "437.leslie3d",
    "444.namd",
    "445.gobmk",
    "447.dealII",
    "450.soplex",
    "453.povray",
    "454.calculix",
    "456.hmmer",
    "458.sjeng",
    "459.GemsFDTD",
    "462.libquantum",
    "464.h264ref",
    "465.tonto",
    "470.lbm",
    "471.omnetpp",
    "473.astar",
    "481.wrf",
    "482.sphinx3",
    "483.xalancbmk",
    "998.specrand",
    "999.specrand",
]

# Input size choices
size_choices = ["test", "train", "ref"]

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Configuration script to run SPEC CPU2006 benchmarks on a RISC-V system"
)

parser.add_argument(
    "--image",
    type=str,
    required=True,
    help="Input the full path to the built spec-2006 disk-image",
)

parser.add_argument(
    "--partition",
    type=str,
    required=False,
    default=None,
    help='Input the root partition of the SPEC disk-image. If the disk is not partitioned, then pass ""',
)

parser.add_argument(
    "--benchmark",
    type=str,
    required=True,
    help="Input the benchmark program to execute",
    choices=benchmark_choices,
)

parser.add_argument(
    "--size",
    type=str,
    required=True,
    help="Simulation size for the benchmark program",
    choices=size_choices,
)

args = parser.parse_args()

# Validate disk image path
if args.image[0] != "/":
    # Get the absolute path if not already provided
    args.image = os.path.abspath(args.image)

if not os.path.exists(args.image):
    warn("Disk image not found!")
    print("Please provide a valid path to the SPEC CPU2006 disk image")
    exit(1)

# Create output directory for benchmark results
output_dir = f"speclogs_{args.benchmark}_{args.size}_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
try:
    os.makedirs(os.path.join(m5.options.outdir, output_dir))
except FileExistsError:
    warn("output directory already exists!")

class SiFiveO3Core(BaseCPUCore):
    """
    Custom SiFive out-of-order core configuration with specified frequency
    """
    
    def __init__(self, cpu_id: int):
        sifive_core = RiscvO3CPU(cpu_id=cpu_id)
        
        # Configure the core to match SiFive design
        # Adjust parameters to match SiFive performance characteristics
        sifive_core.fetchWidth = 4
        sifive_core.decodeWidth = 4
        sifive_core.renameWidth = 4
        sifive_core.dispatchWidth = 4
        sifive_core.issueWidth = 4
        sifive_core.wbWidth = 4
        sifive_core.commitWidth = 4
        
        # Set up branch predictor
        sifive_core.LQEntries = 32
        sifive_core.SQEntries = 32
        sifive_core.LSQDepCheckShift = 0
        sifive_core.LSQCheckLoads = True
        
        # ROB sizing
        sifive_core.numROBEntries = 128
        
        # Configure other core parameters
        sifive_core.numPhysIntRegs = 128
        sifive_core.numPhysFloatRegs = 128
        sifive_core.numIQEntries = 64
        
        super().__init__(core=sifive_core, isa=ISA.RISCV)

# Setup the cache hierarchy (Ruby with MI protocol)
cache_hierarchy = MIExampleCacheHierarchy(
    size="32kB", 
    assoc=4
)

# Setup the system memory
memory = SingleChannelDDR3_1600()

# Create a custom processor with SiFive O3 CPU
processor = BaseCPUProcessor(
    cores=[SiFiveO3Core(cpu_id=0)]  # Single core configuration
)

# Setup the board
board = RiscvBoard(
    clk_freq="32.5MHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Setup benchmark command to run
command = f"{args.benchmark} {args.size} {output_dir}"

# Set up the disk image and kernel
board.set_kernel_disk_workload(
    kernel=obtain_resource("riscv-bootloader-vmlinux-5.10"),
    disk_image=DiskImageResource(args.image, root_partition=args.partition),
    readfile_contents=command,
)

# Define ROI exit handler
def handle_exit():
    print("Done booting Linux")
    print("Resetting stats at the start of ROI!")
    m5.stats.reset()
    yield False  # Continue the simulation
    print("Dump stats at the end of the ROI!")
    m5.stats.dump()
    yield True  # Stop the simulation

# Create the simulator with exit handler
simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: handle_exit(),
    },
)

# Record simulation start time
global_start_time = time.time()

print(f"Running benchmark: {args.benchmark} with {args.size} input")
print("Beginning simulation!")

# Reset stats at the start
m5.stats.reset()

# Run the simulation
simulator.run()

# Print performance statistics
print("All simulation events were successful.")
print("Performance statistics:")

roi_begin_ticks = simulator.get_tick_stopwatch()[0][1]
roi_end_ticks = simulator.get_tick_stopwatch()[1][1]

print(f"ROI simulated ticks: {roi_end_ticks - roi_begin_ticks}")
print(f"Ran a total of {simulator.get_current_tick() / 1e12} simulated seconds")

# Print elapsed time
elapsed_time = time.time() - global_start_time
print(f"Total wallclock time: {elapsed_time:.2f}s, {elapsed_time / 60:.2f} min")