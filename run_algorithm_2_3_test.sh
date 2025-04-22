#!/bin/bash
# filepath: /home/leroy/projects_new/TMA_customized_RISCV_SPEC_CPU_2006/run_algorithm_2_3_test.sh
# ...existing code...
# Define directories and file paths
ALG_DIR="$(dirname "$0")/algorithms_test"
ALGO2="${ALG_DIR}/algorithm_2.cpp"
ALGO3="${ALG_DIR}/algotithm_3.cpp"  # note: filename matches the provided file
OUTPUT_LOG="$(dirname "$0")/simulation_output.log"

# Compile algorithm_2.cpp
clang++ -std=c++11 "$ALGO2" -o "${ALG_DIR}/algorithm_2.out"
if [ $? -ne 0 ]; then
    echo "Compilation of algorithm_2.cpp failed." >&2
    exit 1
fi

# Compile algorithm_3.cpp
clang++ -std=c++11 "$ALGO3" -o "${ALG_DIR}/algorithm_3.out"
if [ $? -ne 0 ]; then
    echo "Compilation of algorithm_3.cpp failed." >&2
    exit 1
fi

# Run executables and record simulation output
{
    echo "---- Output from algorithm_2 ----"
    "${ALG_DIR}/algorithm_2.out"
    echo ""
    echo "---- Output from algorithm_3 ----"
    "${ALG_DIR}/algorithm_3.out"
} | tee "$OUTPUT_LOG"