# Test Script for ROBDD Implementation
# Nick 213529522, Amalya Reiss 216229526
# Formal Verification and Synthesis - Exercise 3

import os
import shutil
from bdd import BDDManager


def test_formula(name, formula, variables, output_dir):
    """
    Build a BDD for the given formula and export results.

    Args:
        name: Name for this test (used in output filename)
        formula: Boolean formula string
        variables: List of variables in desired order
        output_dir: Directory to save outputs
    """
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"Formula: {formula}")
    print(f"Variables: {variables}")
    print(f"{'='*60}")

    # Create BDD manager with given variable ordering
    manager = BDDManager(variables)

    # Parse and build the BDD
    root = manager.parse(formula)

    # Report results
    print(f"  Root node: {root}")
    print(f"  Total nodes: {len(manager.node_list)}")

    if root == manager.TRUE:
        print("  Result: TAUTOLOGY (always true)")
    elif root == manager.FALSE:
        print("  Result: CONTRADICTION (always false)")

    # Export to files
    safe_name = name.replace(" ", "_")
    output_path = os.path.join(output_dir, safe_name)
    manager.export(root, output_path)
    print(f"  Saved: {output_path}.txt, {output_path}.dot")


def main():
    # Setup output directory
    output_dir = "outputs"

    # Clean previous outputs
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    print("ROBDD Test Suite")
    print("================")
    print(f"Output directory: {output_dir}/")

    # ============================================================
    # FORMULA 1: (a AND NOT c) OR (b XOR d)
    # ============================================================
    test_formula(
        name="Formula1_XOR",
        formula="(a & ~c) | (b ^ d)",
        variables=["a", "b", "c", "d"],
        output_dir=output_dir
    )

    # ============================================================
    # FORMULA 2: At least 3 of 5 variables are TRUE
    # This is a threshold/majority function
    # ============================================================
    # Build formula: all combinations where 3, 4, or 5 variables are true
    at_least_3 = (
        # Exactly 3 true (C(5,3) = 10 terms)
        "(x1 & x2 & x3 & ~x4 & ~x5) | "
        "(x1 & x2 & ~x3 & x4 & ~x5) | "
        "(x1 & x2 & ~x3 & ~x4 & x5) | "
        "(x1 & ~x2 & x3 & x4 & ~x5) | "
        "(x1 & ~x2 & x3 & ~x4 & x5) | "
        "(x1 & ~x2 & ~x3 & x4 & x5) | "
        "(~x1 & x2 & x3 & x4 & ~x5) | "
        "(~x1 & x2 & x3 & ~x4 & x5) | "
        "(~x1 & x2 & ~x3 & x4 & x5) | "
        "(~x1 & ~x2 & x3 & x4 & x5) | "
        # Exactly 4 true (C(5,4) = 5 terms)
        "(x1 & x2 & x3 & x4 & ~x5) | "
        "(x1 & x2 & x3 & ~x4 & x5) | "
        "(x1 & x2 & ~x3 & x4 & x5) | "
        "(x1 & ~x2 & x3 & x4 & x5) | "
        "(~x1 & x2 & x3 & x4 & x5) | "
        # All 5 true (1 term)
        "(x1 & x2 & x3 & x4 & x5)"
    )

    test_formula(
        name="Formula2_AtLeast3of5",
        formula=at_least_3,
        variables=["x1", "x2", "x3", "x4", "x5"],
        output_dir=output_dir
    )

    # ============================================================
    # FORMULA 3: 3-bit comparison (x > y)
    # x = x1*4 + x2*2 + x3 (x1 is MSB)
    # y = y1*4 + y2*2 + y3 (y1 is MSB)
    # ============================================================
    # x > y when:
    #   x1 > y1, OR
    #   x1 == y1 AND x2 > y2, OR
    #   x1 == y1 AND x2 == y2 AND x3 > y3
    comparison = (
        "(x1 & ~y1) | "
        "((~(x1 ^ y1)) & x2 & ~y2) | "
        "((~(x1 ^ y1)) & (~(x2 ^ y2)) & x3 & ~y3)"
    )

    test_formula(
        name="Formula3_Comparison",
        formula=comparison,
        variables=["x1", "y1", "x2", "y2", "x3", "y3"],
        output_dir=output_dir
    )

    # ============================================================
    # CUSTOM FORMULA: Your own choice
    # Transitivity: (A->B) & (B->C) -> (A->C)
    # This should be a TAUTOLOGY
    # ============================================================
    test_formula(
        name="Custom_Transitivity",
        formula="((A -> B) & (B -> C)) -> (A -> C)",
        variables=["A", "B", "C"],
        output_dir=output_dir
    )

    # ============================================================
    # SIMPLE TESTS FOR VERIFICATION
    # ============================================================
    test_formula(
        name="Simple_AND",
        formula="a & b",
        variables=["a", "b"],
        output_dir=output_dir
    )

    test_formula(
        name="Simple_OR",
        formula="a | b",
        variables=["a", "b"],
        output_dir=output_dir
    )

    test_formula(
        name="Simple_XOR",
        formula="a ^ b",
        variables=["a", "b"],
        output_dir=output_dir
    )

    print("\n" + "="*60)
    print("All tests completed!")
    print(f"Check the '{output_dir}/' folder for output files.")
    print("="*60)


if __name__ == "__main__":
    main()
