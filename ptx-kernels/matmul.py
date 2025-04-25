from math import ceil
import numpy as np
from context import compile_function, gpu_to_numpy, numpy_to_gpu, sync

def naive_matmul():
    fn = compile_function("naive_matmul.ptx", "naive_matmul")
    
    shapeA = [32, 32]
    shapeB = [32, 32]
    shapeC = [shapeA[0], shapeB[1]]
    dtype = np.float32

    inputA_h = np.random.uniform(low=-1000000, high=1000000, size=shapeA).astype(dtype)
    inputB_h = np.random.uniform(low=-1000000, high=1000000, size=shapeB).astype(dtype)

    inputA_d = numpy_to_gpu(inputA_h)
    inputB_d = numpy_to_gpu(inputB_h)
    output_d = numpy_to_gpu(np.empty(shapeC, dtype=dtype))

    tileSize = 32

    """fn(
        inputA_d,
        inputB_d,
        output_d,
        grid=(ceil(shapeC[0]/tileSize), ceil(shapeC[1]/tileSize), 1),
        block=(tileSize, tileSize, 1)
    )
    sync()"""

    results = gpu_to_numpy(output_d, inputA_h.shape, inputA_h.dtype)
    expected = inputA_h @ inputB_h

    print(
        f"\nmaximum absolute error of vectorAddSInt32 is {np.abs(results - expected).max()}"
    )
    

if __name__ == "__main__":
    naive_matmul()