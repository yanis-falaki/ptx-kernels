# PTX ISA Notes
These are some notes I'm writing while reading through the PTX ISA.

# 3 Programming Model

## 3.1 A Set of SIMT Multiprocessors
A multiprocessor consists of multiple Scaller Processor (SP) cores, a multithreaded instruction unit, and on-chip shared memory.

Multiprocessor creates, manages, and executes concurrent threads in hardware with "zero scheduling overhead".

SM implements single-instruction barrier synchronization.

Each thread maps to one scalar processor core, each scalar core executes independently with its own instruction address and register state.

The multiprocessor SIMT unit creates, manages, schedules, and executes threads in groups of parallel threads called warps. Individual threads composing a warp start together but are free to branch off and execute independently. (If there is conditional branching, threads will "read" the instructions it doesnt use, but will be turned off - PMPP)

When an SM is given thread block(s) to execute, it splits them into warps that get scheduled by the SIMT unit.

At every instructuion issue time, the SIMT unit selects a warp that's ready to execute and issues the next instruction to the active threads of warps. Full efficiency is realized when all threads of a warp agree on execution time.

If threads of a warp diverge, warp serially executes each branch path taken, disabling threads not on the path. Branch divergence occurs only within a warp; different warps execute independently regardless of whether they are executing common or disjointed code paths.

Substantial performance improvements can be realized by making eliminating thread divergence within a warp.

How many blocks an SM can process at once depends on how many registers per thread and how much shared memory per block is required as recources are split among all threads of the batch of blocks. If there are not enough resources to process at least one block, the kernel will fail to launch.


# 4 Syntax
PTX programs are a collection of text source modules (files). PTX source modules have an assembly-language style syntax with instruction operation codes and operands. Pseudo-operations specify symbol and addressing management. The ptxas optimizing backend compiler optimizes and assembles PTX source modules to produce corresponding binary object files.

## 4.1 Source Format
Source modules are ASCII text. Lines are seperated by the newline character (\n).

All whitespace characters are equivalent; whitespace is ignored except for its use in seperating tokens in the language.

The C preprocessor cpp may be used to process PTX source modules. Lines beginning with # are preprocessor directives. The following are common preprocessor directives:

`#include`, `#define`, `#if`, `#ifdef`, `#else`, `#endif`, `#line`, `#file`

PTX is case sensitive and uses lowercase for keywords

Each PTX module must begin with a `.version` directive specyfying the PTX language version, followed by a `.target` directive specifying the target architecture assumed.

## 4.2 Comments
Comments follow C/C++ syntax, using non-nested /* and */ for comments that span multiple lines, and using // to begin a comment that extends up to the newline character.

## 4.3 Statements
A PTX statement is either a directive or an instruction. Statements begin with an optional label and end with a semiconlon

**Examples**
```
        .reg    .b32 r1, r2;    // declares two 32-bit registers: r1 and r2
        .global .f32 array[N]; // declares a global array of floats called array with N elements 

start:  mov.b32 r1, %tid.x;     // label start, moves thread's X index into register r1. Each thread has a unique tid.x in its block.
        sh1.b32 r1, r1, 2;      // shift thread id by 2 bits, multiplying by four. This is needed for indexing the float array where each element holds 4 bytes. Memory address is byte-based.
        ld.global.b32   32, array[r1]; // thread[tid] gets array[tid]
        add.f32 r2, 32, 0.5;    // add 1/2

```

Directive keywords begin with a dot, so no conflict is possible with user-defined identifiers.

### 4.3.2 Instruction Statements
Instructions are formed from an instruction opcode followed by a comma-seperated list of zero or more operands, and terminated with a semicolon. Operands may be register variables, constant expressions, address expressions, or label names. Instructions have na optional guard predicate which controls conditional execution. The guard predicate follows the optional label and precedes the opcode, and is written as @p, where p is a predicate register. The guard predicate may be optionally negated, written as @!p.

The destination operand is first, followed by source operands.

## 4.4 Identifiers
User-defined identifiers follow extended C++ rules:

They either start with a letter followed by zero or more letters, digits, undersroce, or dollar characters; or they start with an underscore, dollar, or percentage character followed by one or more letters, digits underscore or dollar characters;

```
followsym:  [a-zA-Z0-9_$]
identifier: [a-zA-Z]{followsym}* | {[_$%]{followsym}}+
```

Similar as many high level language such as C and C++, except that the percentage sign is not allowed. PTX allows the percentage sign as the first character of an identifier. The percentage sign can be used to avoid name conflicts,e e.g, between user-defined variable names and compiler-generated names.

PTX predefines one constant and a small number of special registers that begin with the percentage sign, listed in Table 3 (in pdf).

## 4.5 Constants
PTX supports integer and floating-point constants and constant expression. These constants may be used in data initialization and as operands to instructions. Type checking rules remain the same for integer, floating-point, and bit-size types. For predicate-type data and instructions, integer constants are allowed and are interpreted as in C, i.e., zero values are False and non-zero values are True.

### 4.5.1 Integer Constants

64-bits in size and are either signed or unsigned, i.e., every integer constant has type .s64 or .u64. the signed/unsigned nature of an integer constant is needed to correctly evaluate constant expressions containing operations such as division and ordered comparisons where the behaviour of the operation depends on the operand types. When used in an instruction or data initial-ization, each integer constant is casted to the appropriate size based on the data or instruction type at its use.

Integer literals may be written in decimal, hexadecimal, octal, or binary notation. The syntax follows that of C. Integer literals may be followed immediately by the letter U to indicated that the literal is unsigned.

### Floating-Point Constants
Floating-point constants are represented as 64-bit double-precision values, and all floating-point constant expressions are evaluated using 64-bit double precision arithmetic. The only exception is the 32-bit hex notation for expressing an exact single-precision floating point value; such values retain their exact 32-bit single-precision value and may not be used in constant expressions. Each 64-bit floating-point constant is converted to the appropriate floating-point size based on the data or in-struction type at its use.

PTX includes a second representation of floating-point constants for specifying the exact machine representation using a hexadecimal constant.

Constants that begin with `0d` or`0D` followed by 16 hex digits specify IEEE 754 double-precision floating point.

Constants that begin with `0f` or `0F` followed by 8 hex digits specify IEEE 754 single-precision floating point values.

```
0[fF]{hexdigit}{8}  // single-precision floating point
0[dD]{hexdigit}{16} // double-precision floating point
```

**Example**
```
mov.f32 $f3, 0F3f800000; // 1.0
```

# 5. State Spaces, Types, and Variables

## 5.1 State Spaces
A state space is a storage area with particular characteristics. All variables reside in some state space.

The characteristics of a state space include its size, addressability, access speed, access rights, and level of sharing between threads.

The state spaces defined in PTX are a byproduct of parallel programming and graphics programming. The list of state spaces is shown below:

- **.reg**: Registers, fast.
- **.sreg**: Special registers. Read-only; pre-defined; platform-specific.
- **.const**: Shared, read-only memory.
- **.global**: Global memory, shared by all threads.
- **.local**: Local memory, private to each thread.
- **.param**: Kernel parameters, defined per-grid; or Function or local parameters, defined per-thread.
- **.shared**: Addressable memory, defined per CTA (thread block), accessabled to all threads in the cluster throughout the lifetime of the CTA that defines it.
- **.tex**: Global texture memory (deprecated).

## 11.1 PTX Module directives
The following declare the PTX ISA version of the code in the module, the target architecture for which the code was generated, and the size of addresses within the PTX module.

- `.version`
- `.target_sm`
- `.address_size`

Each PTX module must begin with a `.version` directive and no other .version directive is allowed anywhere else in the code.

Target architectures with the suffix "a", such as sm_90a, include architecture-accelerated features that are supported on the specified architecture only.

## 11.2 Specifying Kernel Entry Points and Functions

The following directives specify kernel enrtry points and functions.

- `.entry`
- `.func`

### .entry
Kernel entry point and body, with optional parameters

**Syntax**

```
.entry kernel-name  ( param-list ) kernel-body
.entry kernel-name  kernel-body
```

Parameters are passed via `.param` space memory and are listed within an optional parenthesized parameter list. Parameters may be referenced by name within the kernel body and loaded into registers using ld.param{::entry} instructions.

The shape and size of the CTA executing the kernel are available in special registers.

At kernel launch, the kernel dimensions and properties are established and made available via special regisers, e.g.,%ntid, %nctaid, etc.

### .func
Function definition

**Syntax**

```
.func {.attribute(attr-list)} fname {.noreturn} function-body
.func {.attribute(attr-list)} fname (param-list) {.noreturn} function-body
.func {.attribute(attr-list)} (ret-param) fname (param-list) function-body
```

**Description**

Defines a function, including input and return parameters and optional function body.

Optional `.noreturn` directive indicates that the function does not return to the caller function. `.noreturn` directive cannot be specied on functions which have return parameters.

Optional `.attribute` directive specifies additional information associated with the function.
