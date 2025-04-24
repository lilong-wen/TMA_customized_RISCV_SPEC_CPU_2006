"""
This example runs a RISC-V full system simulation using a customized SiFive out-of-order CPU
with a Ruby cache hierarchy.

Characteristics:
- Runs exclusively on the RISC-V ISA
- Uses the gem5 library
- Uses Ruby cache coherence protocol
- Includes a cache hierarchy (32KB, 4-way associative)
- SiFive out-of-order CPU running at 32.5MHz
"""

import argparse

from m5.objects import RiscvO3CPU

from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.utils.override import overrides

# Ruby-related imports
from gem5.components.cachehierarchies.ruby.mi_example_cache_hierarchy import (
    MIExampleCacheHierarchy,
)

# Run a check to ensure the right version of gem5 is being used
requires(isa_required=ISA.RISCV)

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

# Directly set the kernel and disk image using obtain_resource
board.set_kernel_disk_workload(
    kernel=obtain_resource("riscv-bootloader-vmlinux-5.10"),
    disk_image=obtain_resource("riscv-disk-img"),
)

# Create the simulator
simulator = Simulator(board=board)
print("Beginning simulation!")
simulator.run()


stats = board.get_stats()  # 获取统计数据

cycles = stats.get("cycles", 1)
pipeline_width = 3

decoded = stats.get("decoded_less_than_maximum_operations", 0)
bdir_mispred = stats.get("branch_direction_misprediction", 0)
ijtp_mispred = stats.get("ijtp_misprediction", 0)
ras_mispred = stats.get("ras_mispredicted_target", 0)
decode_stall = stats.get("instruction_decode_stall_from_recover", 0)
instructions = stats.get("Instructions", 0)

PARTIAL_SLOT_FACTOR = 2
FETCH_WAIT_CYCLE = 2
BPM_COST = 9

frontend_bound = (decoded * PARTIAL_SLOT_FACTOR + (bdir_mispred + ijtp_mispred + ras_mispred) * FETCH_WAIT_CYCLE * pipeline_width) / (cycles * pipeline_width)
bad_speculation = (((bdir_mispred + ijtp_mispred + ras_mispred) * BPM_COST * pipeline_width + decode_stall * pipeline_width)) / (cycles * pipeline_width)
retiring = instructions / (cycles * pipeline_width)
backend_bound = 1 - (frontend_bound + bad_speculation + retiring)
ipc = instructions / cycles

print("Metrics:")
print("Frontend Bound:", frontend_bound)
print("Bad Speculation:", bad_speculation)
print("Retiring:", retiring)
print("Backend Bound:", backend_bound)
print("IPC", ipc)