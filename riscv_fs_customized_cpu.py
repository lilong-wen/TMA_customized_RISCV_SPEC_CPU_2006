# Parameters: Processor SiFive Performance™ P470, 32.5MHz, 
#           L1 I-Cache 32KB, 
#           L1 D-Cache 32KB, 
#           non L2 Cache, 
#           L3 Cache 2MB 
#           Memory 2GB 
#           Kernel Linux 6.7.9 
#           Benchmark SPEC 2006CPU v1.0.2 (not optimized version) 
#           Compiler SiFive internal clang (close to upstream clang 18)

import m5
from m5.objects import Root, Cache, SystemXBar, L2XBar, BadAddr

from gem5.components.boards.riscv_board import RiscvBoard
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.abstract_cache_hierarchy import AbstractCacheHierarchy
from gem5.components.cachehierarchies.classic.abstract_classic_cache_hierarchy import AbstractClassicCacheHierarchy
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.boards.abstract_board import AbstractBoard

# Import our cache helper functions
from cache_helper import create_l1_cache, create_l2_cache, create_l3_cache, create_cache, create_l1_cache_config, create_l2_cache_config, create_l3_cache_config

# Run a check to ensure the right version of gem5 is being used
requires(isa_required=ISA.RISCV)

class ThreeLevelCacheHierarchy(AbstractClassicCacheHierarchy):
    """Three-level cache hierarchy with 32kB L1i/d caches and 2MB L3 cache"""
    
    def __init__(self):
        super().__init__()
        self._l1i_size = "32kB"
        self._l1d_size = "32kB"
        self._l2_size = "4kB"
        self._l3_size = "2MiB"  # Changed from "2MB" to "2MiB" for consistency
        self._l3_assoc = 16
        
        # Create the memory bus early to make it available for port connections
        self.membus = SystemXBar()
        
        # Add BadAddr responder for unmapped memory addresses
        self.badaddr = BadAddr()
        self.membus.default = self.badaddr.pio
    
    def get_mem_side_port(self):
        return self.membus.mem_side_ports
        
    def get_cpu_side_port(self):
        return self.membus.cpu_side_ports

    def incorporate_cache(self, board):
        # Set up the system port for functional access from the simulator
        board.connect_system_port(self.membus.cpu_side_ports)
        
        # Connect memory ports
        for cntr in board.get_memory().get_memory_controllers():
            cntr.port = self.membus.mem_side_ports
            
        # Create the L3 bus
        self.l3bus = SystemXBar(parent=board)
        
        # For RISC-V boards, the I/O devices are already connected to the I/O bus
        # We need to use a bridge to connect the memory bus to these devices
        if isinstance(board, RiscvBoard) and board.has_io_bus():
            from m5.objects import Bridge
            # Create a bridge between memory bus and I/O bus
            self.io_bridge = Bridge(delay="50ns", parent=board)
            self.io_bridge.mem_side_port = board.get_io_bus().cpu_side_ports
            self.io_bridge.cpu_side_port = self.membus.mem_side_ports
            
            # If the board has coherent I/O, set it up
            if board.has_coherent_io():
                self._setup_io_cache(board)
        
        # Create the shared L3 cache using configurations
        l3_config = create_l3_cache_config(
            size=self._l3_size,
            assoc=self._l3_assoc
        )
        # Create L3 cache and properly parent it to this cache hierarchy
        self.l3_cache = Cache(parent=board, **l3_config)
        
        # Connect L3 cache between L3 bus and memory bus
        self.l3bus.mem_side_ports = self.l3_cache.cpu_side
        self.membus.cpu_side_ports = self.l3_cache.mem_side
        
        # Create L2 buses as named attributes
        for i in range(board.get_processor().get_num_cores()):
            l2bus_name = f"l2bus_{i}"
            setattr(self, l2bus_name, L2XBar(parent=board))
        
        # Create the individual caches for each core
        for i, cpu in enumerate(board.get_processor().get_cores()):
            # Get the L2 bus for this core
            l2bus = getattr(self, f"l2bus_{i}")
            
            # Create L2 cache with proper parameters and parent it
            l2_config = create_l2_cache_config(size=self._l2_size)
            l2_cache_name = f"l2_cache_{i}"
            setattr(self, l2_cache_name, Cache(parent=board, **l2_config))
            l2_cache = getattr(self, l2_cache_name)
            
            # Create L1 instruction cache and parent it
            l1i_config = create_l1_cache_config(size=self._l1i_size)
            l1i_cache_name = f"l1i_cache_{i}"
            setattr(self, l1i_cache_name, Cache(parent=board, **l1i_config))
            l1i_cache = getattr(self, l1i_cache_name)
            
            # Create L1 data cache and parent it
            l1d_config = create_l1_cache_config(size=self._l1d_size)
            l1d_cache_name = f"l1d_cache_{i}"
            setattr(self, l1d_cache_name, Cache(parent=board, **l1d_config))
            l1d_cache = getattr(self, l1d_cache_name)
            
            # Create MMU caches with parameters
            mmu_cache_config = {
                'size': "8KiB",
                'assoc': 4,
                'tag_latency': 1,
                'data_latency': 1,
                'response_latency': 1,
                'mshrs': 10,
                'tgts_per_mshr': 8
            }
            
            # Create instruction PTW cache
            iptw_name = f"iptw_cache_{i}"
            setattr(self, iptw_name, Cache(parent=board, **mmu_cache_config))
            iptw = getattr(self, iptw_name)
            
            # Create data PTW cache
            dptw_name = f"dptw_cache_{i}"
            setattr(self, dptw_name, Cache(parent=board, **mmu_cache_config))
            dptw = getattr(self, dptw_name)
            
            # Connect CPU to L1 caches
            cpu.connect_icache(l1i_cache.cpu_side)
            cpu.connect_dcache(l1d_cache.cpu_side)
            
            # Connect L1 caches to L2 bus
            l1i_cache.mem_side = l2bus.cpu_side_ports
            l1d_cache.mem_side = l2bus.cpu_side_ports
            
            # Connect MMU caches to L2 bus
            iptw.mem_side = l2bus.cpu_side_ports
            dptw.mem_side = l2bus.cpu_side_ports
            
            # Connect CPU's walker ports to MMU caches
            cpu.connect_walker_ports(iptw.cpu_side, dptw.cpu_side)
            
            # Connect L2 bus to L2 cache
            l2bus.mem_side_ports = l2_cache.cpu_side
            
            # Connect L2 cache to L3 bus
            l2_cache.mem_side = self.l3bus.cpu_side_ports
            
            # Connect interrupts based on ISA
            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()
        
        # Create coherent I/O if needed
        if board.has_coherent_io():
            self._setup_io_cache(board)
        
        # Make sure Boot ROM is connected to the membus
        if hasattr(board, 'boot_rom'):
            self.membus.mem_side_ports = board.boot_rom.port
            
    def _setup_io_cache(self, board):
        """Create a cache for coherent I/O connections"""
        # Create I/O cache
        self.io_cache = create_cache(
            size="1KiB",
            assoc=8,
            tag_latency=50,
            data_latency=50,
            response_latency=50,
            mshrs=20,
            tgts_per_mshr=12,
            parent=board  # Add parent parameter here
        )
        self.io_cache.mem_side = self.membus.cpu_side_ports
        self.io_cache.cpu_side = board.get_mem_side_coherent_io_port()

# Setup the system memory (8GiB to match device capacity)
memory = SingleChannelDDR3_1600(size="8GiB")

# Setup a single core O3 processor
processor = SimpleProcessor(
    cpu_type=CPUTypes.O3,
    isa=ISA.RISCV,
    num_cores=1,
)

# Setup the cache hierarchy
cache_hierarchy = ThreeLevelCacheHierarchy()

# Setup the board with 32.5MHz clock frequency
board = RiscvBoard(
    clk_freq="32.5MHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Set the Full System workload
board.set_kernel_disk_workload(
    kernel=obtain_resource("riscv-bootloader-vmlinux-5.10"),
    disk_image=obtain_resource("riscv-disk-img"),
)

# Setup the simulator and run the simulation
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