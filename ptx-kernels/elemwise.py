from math import ceil
import numpy as np
from context import compile_function, gpu_to_numpy, numpy_to_gpu, sync

def sqrt_example():
    fn = compile_function("elemwise_sqrt.ptx", "sqrtElements")
    inputs = np.abs(np.random.normal(size=[10000]).astype(np.float32))
    input_buf = numpy_to_gpu(inputs)
    output_buf = numpy_to_gpu(inputs)
    block_size = 1024
    fn(
        input_buf,
        output_buf,
        np.int32(len(inputs) - 10),
        grid=(ceil(len(inputs) / block_size), 1, 1),
        block=(block_size, 1, 1),
    )
    sync()
    results = gpu_to_numpy(output_buf, inputs.shape, inputs.dtype)
    expected = np.sqrt(inputs.astype(np.float32))
    print(
        f"\nmaximum absolute error of sqrt is {np.abs(results[:-10] - expected[:-10]).max()}"
    )
    print(
        f"maximum absolute error masked is {np.abs(results[-10:] - inputs[-10:]).max()}"
    )

    print("")
    print("Inputs:", inputs[-10:], '\n\n', "Expected:", expected[-10:], '\n\n', "Results of Masked:", results[-10:])
    print("")

    bad_idx = np.argmax(np.abs(expected[:-10] - results[:-10]))
    print(f"Max Error Idx: {bad_idx}, Input: {inputs[bad_idx]}, CPU sqrt: {expected[bad_idx]}, GPU sqrt: {results[bad_idx]}")

    example_idx = 9000
    print(f"Idx: {example_idx}, Input: {inputs[example_idx]}, CPU sqrt: {expected[example_idx]}, GPU sqrt: {results[example_idx]}")


if __name__ == "__main__":
    sqrt_example()