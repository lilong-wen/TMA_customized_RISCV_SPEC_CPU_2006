#!/bin/bash

# Compile with ENABLE_SORT defined
clang++ -O2 algorithms_test/algorithm_1.cpp -o algorithm_1_with_sort -DENABLE_SORT
output_with=$(./algorithm_1_with_sort | grep "Sum:" | awk '{print $2}')
echo "Output with ENABLE_SORT: $output_with"

# Compile without ENABLE_SORT defined
clang++ -O2 algorithms_test/algorithm_1.cpp -o algorithm_1_without_sort
output_without=$(./algorithm_1_without_sort | grep "Sum:" | awk '{print $2}')
echo "Output without ENABLE_SORT: $output_without"