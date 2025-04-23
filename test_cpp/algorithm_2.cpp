#include <iostream>

int **mmult(int rows, int cols, int **m1, int **m2, int **m3) {
    int i, j, k;
    // Initialize m3 to zero
    for(i = 0; i < rows; i++) {
        for(j = 0; j < cols; j++) {
            m3[i][j] = 0;
        }
    }
    for(i = 0; i < rows; i++) {
        for(j = 0; j < cols; j++) {
            for(k = 0; k < cols; k++) {
                m3[i][j] += m1[i][k] * m2[k][j];
            }
        }
    }
    return m3;
}

int main() {
    int rows = 2, cols = 2;
    int **m1 = new int*[rows];
    int **m2 = new int*[rows];
    int **m3 = new int*[rows];
    for(int i = 0; i < rows; i++){
        m1[i] = new int[cols];
        m2[i] = new int[cols];
        m3[i] = new int[cols];
    }
    // Initialize m1
    m1[0][0] = 1; m1[0][1] = 2;
    m1[1][0] = 3; m1[1][1] = 4;
    // Initialize m2
    m2[0][0] = 5; m2[0][1] = 6;
    m2[1][0] = 7; m2[1][1] = 8;
    // Multiply matrices
    mmult(rows, cols, m1, m2, m3);
    // Print m3
    for(int i = 0; i < rows; i++){
        for(int j = 0; j < cols; j++){
            std::cout << m3[i][j] << " ";
        }
        std::cout << std::endl;
    }
    // Cleanup
    for(int i = 0; i < rows; i++){
        delete [] m1[i];
        delete [] m2[i];
        delete [] m3[i];
    }
    delete [] m1;
    delete [] m2;
    delete [] m3;
    return 0;
}