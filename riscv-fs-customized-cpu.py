# Parameters: Processor SiFive Performance™ P470, 32.5MHz, 
#           L1 I-Cache 32KB, 
#           L1 D-Cache 32KB, 
#           non L2 Cache, 
#           L3 Cache 2MB 
#           Memory 2GB 
#           Kernel Linux 6.7.9 
#           Benchmark SPEC 2006CPU v1.0.2 (not optimized version) 
#           Compiler SiFive internal clang (close to upstream clang 18)

from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

from gem5.components.cachehierarchies.abstract_three_level_cache_hierarchy import AbstractThreeLevelCacheHierarchy
from gem5.components.cachehierarchies.classic.no_cache import NoCache

import os

# Run a check to ensure the right version of gem5 is being used.
requires(isa_required=ISA.RISCV)

# Use NoCache as a placeholder for the required parameter
cache_hierarchy = NoCache()

# Setup the system memory with 2GB capacity.
memory = SingleChannelDDR3_1600(size="2GiB")

# Setup a single core Out-of-Order Processor.
processor = SimpleProcessor(cpu_type=CPUTypes.O3, num_cores=1, isa=ISA.RISCV)

# First create the board with processor, memory, and cache hierarchy
board = RiscvBoard(
    clk_freq="32.5MHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy
)

# Set the Full System workload with Linux 6.7.9 kernel.
board.set_kernel_disk_workload(
    # kernel=obtain_resource("riscv-bootloader-vmlinux-6.7.9", resource_version="1.0.0"),
    # kernel=obtain_resource(os.path.dirname(__file__) + "/" + "bootloader-vmlinux-5.10", resource_version="1.0.0"),
    kernel=obtain_resource("riscv-bootloader-vmlinux-5.10", resource_version="1.0.0"),
    disk_image=obtain_resource("riscv-disk-img", resource_version="1.0.0")
)

simulator = Simulator(board=board)
print("Beginning simulation!")
simulator.run()

# 添加代码来记录SPEC CPU2006测试期间的metrics
# 假设board.get_stats()返回包含所有计数的字典，实际API请根据实际情况调整
stats = board.get_stats()  # 获取统计数据

cycles = stats.get("cycles", 1)
pipeline_width = 3

decoded = stats.get("decoded_less_than_maximum_operations", 0)
bdir_mispred = stats.get("branch_direction_misprediction", 0)
ijtp_mispred = stats.get("ijtp_misprediction", 0)
ras_mispred = stats.get("ras_mispredicted_target", 0)
decode_stall = stats.get("instruction_decode_stall_from_rhf_recover", 0)
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