from math import ceil
import numpy as np
from context import compile_function, gpu_to_numpy, numpy_to_gpu, sync

def vector_add_int32():
    fn = compile_function("vector_add_int32.ptx", "vectorAddInt32")
    
    N = np.int32(10_000)

    inputA_h = np.random.randint(low=-1000000, high=1000000, size=[N], dtype=np.int32)
    inputB_h = np.random.randint(low=-1000000, high=1000000, size=[N], dtype=np.int32)

    inputA_d = numpy_to_gpu(inputA_h)
    inputB_d = numpy_to_gpu(inputB_h)
    output_d = numpy_to_gpu(inputB_h)

    blockSize = 1024

    fn(
        inputA_d,
        inputB_d,
        output_d,
        N,
        grid=(ceil(N/blockSize), 1, 1),
        block=(blockSize, 1, 1)
    )
    sync()

    results = gpu_to_numpy(output_d, inputA_h.shape, inputA_h.dtype)
    expected = inputA_h + inputB_h

    for i in range(5):
        print(f"idx: {i}    A: {inputA_h[i]}    B: {inputB_h[i]}    C: {results[i]}")

    print(
        f"\nmaximum absolute error of vectorAddSInt32 is {np.abs(results - expected).max()}"
    )
    

if __name__ == "__main__":
    vector_add_int32()