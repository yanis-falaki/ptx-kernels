from math import ceil
import numpy as np
from context import compile_function, gpu_to_numpy, numpy_to_gpu, sync

def naive_matmul(print_matrices=True):
    fn = compile_function("naive_matmul.ptx", "naive_matmul")
    
    shapeA = [200, 1000]
    shapeB = [1000, 200]
    assert shapeA[1] == shapeB[0], "Rows in A must equal columns in B"
    shapeC = [shapeA[0], shapeB[1]]
    dtype = np.float32

    inputA_h = np.random.uniform(low=-10, high=10, size=shapeA).astype(dtype)
    inputB_h = np.random.uniform(low=-10, high=10, size=shapeB).astype(dtype)

    inputA_d = numpy_to_gpu(inputA_h)
    inputB_d = numpy_to_gpu(inputB_h)
    output_d = numpy_to_gpu(np.empty(shapeC, dtype=dtype))

    tileSize = 32

    fn(
        inputA_d,
        inputB_d,
        output_d,
        np.uint32(shapeC[0]),
        np.uint32(shapeC[1]),
        np.uint32(shapeA[1]),
        grid=(ceil(shapeC[0]/tileSize), ceil(shapeC[1]/tileSize), 1),
        block=(tileSize, tileSize, 1)
    )
    sync()

    results = gpu_to_numpy(output_d, shapeC, inputA_h.dtype)
    expected = inputA_h @ inputB_h

    if (print_matrices):
        print(f"\nA:\n{inputA_h}")
        print(f"\nB:\n{inputB_h}")
        print(f"\nCalculated C:\n{results}")
        print(f"\nExpected C:\n{expected}")

    print(
        f"\nmaximum absolute error of naive_matmul is {np.abs(results - expected).max()}"
    )
    

if __name__ == "__main__":
    naive_matmul(print_matrices=False)