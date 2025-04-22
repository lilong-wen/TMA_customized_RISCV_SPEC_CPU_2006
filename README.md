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

## Run Instructions

1. Run the risv-fs-customized-cpu.py script.
2. In the fs simulation, install clang 18 and the SPEC CPU2006 suite.
3. Run: gem5.opt riscv-fs-customized-cpu.py --script [script.sh]

## TODO
- [ ] Fix the warning "Address .... is outside os physical memory, stopping fetch"

## NOTICE

### riscv64-unknown-linux-gnu-g++/gcc/ar not found

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

### Clang 18 is cross compilated on the host computer

To speed up the process, I compiled Clang 18 on the host computer with:
```bash
cmake -G Ninja ../llvm \
  -DLLVM_TARGETS_TO_BUILD="RISCV" \
  -DLLVM_DEFAULT_TARGET_TRIPLE=riscv64-unknown-linux-gnu \
  -DCMAKE_C_COMPILER=riscv64-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=riscv64-linux-gnu-g++ \
  -DCMAKE_SYSROOT=/usr/riscv64-linux-gnu \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_PROJECTS="clang" \
  -DLLVM_ENABLE_TERMINFO=OFF \
  -DLLVM_ENABLE_ZLIB=OFF \
  -DLLVM_ENABLE_LIBXML2=OFF \
  -DLLVM_ENABLE_ASSERTIONS=OFF
```
