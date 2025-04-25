__global__ void naive_matmul(char* aPtr, char* bPtr, char* cPtr, int m, int n, int k) \
{
    int y = threadIdx.y + blockIdx.y*blockDim.y;
    int x = threadIdx.x + blockIdx.x*blockDim.x;

    if (y >= m || x >= n) return;


    // precomputing values
    char* aValOffset = aPtr + y*k*4;
    char* bValOffset = bPtr + x*4;
    float cVal = 0;

    for (int i = 0; i < k; ++i) {
    
        float aVal = *(float*)aValOffset;
        float bVal = *(float*)bValOffset;

        cVal += aVal * bVal;

        aValOffset += 4;
        bValOffset += 4*n;
    }

    // set c value
    // compute linear offset
    char* outPtr = cPtr + (y*n + x)*4;
    *(float*)outPtr = cVal;
}