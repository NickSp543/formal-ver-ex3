# Formal Verification Systems - Exercise 3: BDD Implementation

This repository contains the solution for Exercise 3 in the Formal Verification Systems course. It implements a **Reduced Ordered Binary Decision Diagram (ROBDD)** library in Python and includes test scripts to verify various boolean formulas.

## Authors
**Nick 213529522, Amalya Reiss 216229526**

## Project Structure

The project is organized as follows:

* **`bdd.py`**: The core library containing the `BDDManager` class and implementation of BDD operations (construction, reduction, apply).
* **`run_tests.py`**: The main execution script. It defines the boolean formulas, builds the BDDs, and generates the outputs.
* **`outputs/`**: A directory containing the generated results for each test case:
    * `*.png`: Visual representation of the BDD graph.
    * `*.dot`: Graphviz source files.
    * `*.txt`: Textual description of the BDD structure.

## Prerequisites

* **Python 3.x**
* **Graphviz** (Required for generating `.png` images from `.dot` files)

To install the Python dependency for Graphviz:
```bash
pip install graphviz
```

You also need to install Graphviz system tool from: https://graphviz.org/download/

## How to Run

To run the assignment and generate all BDD visualizations and text outputs, execute the `run_tests.py` script:

```bash
python run_tests.py
```

### Expected Output

Upon running the script, the `outputs/` folder will be populated with files for the specific test cases:

* `Formula1_XOR` - Formula: (a & ~c) | (b ^ d)
* `Formula2_AtLeast3of5` - At least 3 of 5 variables are true
* `Formula3_Comparison` - 3-bit number comparison (x > y)
* `Custom_Transitivity` - Transitivity proof (tautology)
* `Simple_AND`, `Simple_OR`, `Simple_XOR` - Basic operations

Each case will have its corresponding `.txt`, `.dot`, and `.png` files demonstrating the BDD structure and reduction.

## Implementation Details

The project implements:

1. **Shannon Expansion**: Recursive construction of the BDD by splitting on variables.
2. **Isomorphism Reduction**: Merging identical sub-graphs using a node lookup table.
3. **Redundant Node Elimination**: Removing nodes where high and low children are identical.

### Supported Operators

| Operator | Symbol | Example |
|----------|--------|---------|
| NOT | `~` | `~a` |
| AND | `&` | `a & b` |
| OR | `\|` | `a \| b` |
| XOR | `^` | `a ^ b` |
| IMPLIES | `->` | `a -> b` |
| IFF | `<->` | `a <-> b` |

## AI Use Disclosure

AI assistance was utilized for documentation writing and code debugging. The core algorithm design, implementation logic, and final verification were performed independently by the authors.
