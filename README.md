# TMA_customized_RISCV_SPEC_CPU_2006
Top-Down Microarchitecture Analysis on Customized Out-of-Order RISC-V CPU with SPEC CPU 2006

the SPEC CPU 2006 version: 1.0.1

working environment: Ubuntu24.04 (WSL2.4.12 on windows11) 

gem5 version: 24.1.0.2 

**Metrics**

| Metric          | Formula |
| --------------- | ------- |
| Frontend Bound  | (decoded_less_than_maximum_operations * $PARTIAL_SLOT_FACTOR + (branch_direction_misprediction + ijtp_misprediction + ras_mispredicted_target) * $FETCH_WAIT_CYCLE * $PIPELINE_WIDTH) / (cycles * $PIPELINE_WIDTH) |
| Bad Speculation | ((branch_direction misprediction + ijtp_misprediction + ras_mispredicted_target)* $BPM COST * $PIPELINE_WIDTH + instruction_decode_stall_from_rhf_recover) * $PIPELINE WIDTH) / (cycles * $PIPELINE WIDTH) |
| Backend Bound   | 1-(Frontend_Bound + Bad Speculation + Retiring) |
| Retiring        | Instructions / (cycles * $PIPELINE_WIDTH) |

**Constant Values**

| Constant            | Description                                                                 | Value |
| ------------------- | --------------------------------------------------------------------------- | ----- |
| BPM_COST            | The number of cycles of Branch misprediction Cost                           | 9     |
| PARTIAL_SLOT_FACTOR | Multiply cycles by this number for partial decode to represent partial slots. | 2     |
| FETCH_WAIT_CYCLE    | The number of cycles that the instruction queue waits for fetch after a flush. | 2     |
| PIPELINE_WIDTH      | The maximum number of instructions that the CPU can deliver to the Backend    | 3     |


## TODO
- [ ] Fix the warning "Address .... is outside os physical memory, stopping fetch"

## NOTICE

### 1.  riscv64-unknown-linux-gnu-g++/gcc/ar not found

When compiling m5, I keep encountering the following erros:

```bash
- 'sh: 1: riscv64-unknown-linux-gnu-g++: not found'
- 'sh: 1: riscv64-unknown-linux-gnu-gcc: not found'
- 'sh: 1: riscv64-unknown-linux-gnu-ar: not found'
```

Since the riscv64-linux-gnu-g++/gcc/ar seems to be the right tools, I create symlinks:
```bash
sudo ln -s /usr/bin/riscv64-linux-gnu-g++ /usr/bin/riscv64-unknown-linux-gnu-g++
sudo ln -s /usr/bin/riscv64-linux-gnu-gcc /usr/bin/riscv64-unknown-linux-gnu-gcc
sudo ln -s /usr/bin/riscv64-linux-gnu-ar /usr/bin/riscv64-unknown-linux-gnu-ar
```

### 2. Clang 18 is cross compilated on the host computer

To speed up the process, I compiled Clang 18 on the host machine in two steps, instead of directly compiling it on the target machine. Howerver, the cross-compilation process still costs me around 3 hours somehow (12th Intel(R) i9-12900H with 32GB memory).:

```bash
mkdir build-host
cd build-host
cmake -G Ninja ../llvm \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_PROJECTS="clang;lld" \
  -DLLVM_TARGETS_TO_BUILD="X86;RISCV"
```


```bash
mkdir build-riscv
cd build-riscv
cmake -G Ninja ../llvm \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=riscv64 \
  -DCMAKE_C_COMPILER=riscv64-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=riscv64-linux-gnu-g++ \
  -DLLVM_TARGETS_TO_BUILD="RISCV" \
  -DLLVM_ENABLE_PROJECTS="clang;lld" \
  -DLLVM_TABLEGEN_EXE=../build-host/bin/llvm-tblgen
  -DCLANG_TABLEGEN_EXE=../build-host/bin/clang-tblgen \
  -DLLVM_NATIVE_TOOL_DIR=../build-host/bin \
  -DLLVM_USE_HOST_TOOLS=ON \
  -DLLVM_BUILD_UTILS=OFF \
  -DLLVM_INCLUDE_UTILS=OFF \
  -DLLVM_BUILD_TOOLS=OFF \
  -DLLVM_INCLUDE_TOOLS=OFF \
  -DLLVM_INCLUDE_TESTS=OFF \
  -DLLVM_INCLUDE_EXAMPLES=OFF \
  -DLLVM_INCLUDE_DOCS=OFF
ninja
```

Then, mount the disk image using
```bash
sudo mount -o loop ~/.cache/gem5/riscv-disk-img /mnt/rootfs
```
and copy the compiled files to the target machine:
```bash
sudo cp -r build-riscv/bin/* /mnt/rootfs/usr/bin/
sudo cp -r build-riscv/lib/* /mnt/rootfs/usr/lib/
sudo cp -r build-riscv/include/* /mnt/rootfs/usr/include/
sudo cp -r build-riscv/share/* /mnt/rootfs/usr/share/
```
Before the copy process, I enlarge the disk to make sure that the target machine has enough space. 
```bash
sudo e2fsck -f ~/.cache/gem5/riscv-disk-img
dd if=/dev/zero bs=1M count=1024 >> ~/.cache/gem5/riscv-disk-img
resize2fs ~/.cache/gem5/riscv-disk-img  
``` 
### 3. Three-level cache problem

I tried to implement a three-level cache system with classic caches in Gem5 with 'riscv-fs-customized-cpu.py' and 'cache_helper.py', but I keep encountering the following error:
```bash
RuntimeError: Attempt to instantiate orphan node <orphan Cache>
```
I have no idea how to fix it and don't know if it's possible to implement a three-level cache system under classic caches system. Maybe I will solve this later.

For now, I wrote another script 'riscv-fs-customized-cpu-ruby.py' to implement a three-level cache system with ruby caches. 