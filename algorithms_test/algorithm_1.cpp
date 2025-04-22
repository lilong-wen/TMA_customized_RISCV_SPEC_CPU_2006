#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <ctime>

int main() {
    std::srand(static_cast<unsigned>(std::time(0)));
    const unsigned arraySize = 32768;
    int data[arraySize];
    for (unsigned c = 0; c < arraySize; ++c)
        data[c] = std::rand() % 256;
    #ifdef ENABLE_SORT
    std::sort(data, data + arraySize);
    #endif
    long long sum = 0;
    for (unsigned i = 0; i < 1000; ++i) {
        for (unsigned c = 0; c < arraySize; ++c) {
            if (data[c] >= 128)
                sum += data[c];
        }
    }
    std::cout << "Sum: " << sum << std::endl;
    return 0;
}