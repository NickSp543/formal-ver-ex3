# ROBDD Implementation
# Nick 213529522, Amalya Reiss 216229526
# Formal Verification and Synthesis - Exercise 3

class Node:
    """
    Represents a single node in the BDD.

    Two types of nodes:
    1. Terminal: represents final value (True/False), has no children
    2. Decision: represents a variable, has low (0) and high (1) children
    """

    def __init__(self, variable=None, low_child=None, high_child=None, terminal_value=None):
        # For decision nodes: which variable this node tests
        self.variable = variable

        # Child node indices (only for decision nodes)
        self.low_child = low_child    # edge taken when variable = 0
        self.high_child = high_child  # edge taken when variable = 1

        # For terminal nodes: the final Boolean value
        self.terminal_value = terminal_value

    def is_terminal(self):
        """Check if this is a terminal (leaf) node"""
        return self.terminal_value is not None

    def __eq__(self, other):
        """Two nodes are equal if all their attributes match"""
        if not isinstance(other, Node):
            return False
        return (self.variable == other.variable and
                self.low_child == other.low_child and
                self.high_child == other.high_child and
                self.terminal_value == other.terminal_value)

    def __hash__(self):
        """Hash for using nodes in dictionaries/sets"""
        return hash((self.variable, self.low_child, self.high_child, self.terminal_value))

    def __repr__(self):
        """String representation for debugging"""
        if self.is_terminal():
            return f"Terminal({self.terminal_value})"
        return f"Node({self.variable}, low={self.low_child}, high={self.high_child})"


class BDDManager:
    """
    Manages the construction and operations of a Reduced Ordered BDD.

    Key responsibilities:
    - Maintain a list of all nodes
    - Ensure no duplicate nodes (reduction rule 2)
    - Ensure no redundant nodes (reduction rule 1)
    - Provide operations: AND, OR, NOT, etc.
    """

    def __init__(self, variable_ordering):
        """
        Initialize the BDD manager.

        Args:
            variable_ordering: List of variable names in order (e.g., ['x', 'y', 'z'])
                              Variables earlier in list appear higher in BDD
        """
        self.variable_ordering = variable_ordering

        # Map variable name to its level (position in ordering)
        self.var_level = {}
        for level, var_name in enumerate(variable_ordering):
            self.var_level[var_name] = level

        # Storage for all nodes (index -> Node)
        self.node_list = []

        # Quick lookup: Node -> index (to avoid duplicates)
        self.node_to_index = {}

        # Create the two terminal nodes (always index 0 and 1)
        self.FALSE = self._add_node(Node(terminal_value=False))  # index 0
        self.TRUE = self._add_node(Node(terminal_value=True))    # index 1

    def _add_node(self, node):
        """
        Add a node to storage if it doesn't exist.
        Returns the index of the node.
        """
        # Check if this exact node already exists
        if node in self.node_to_index:
            return self.node_to_index[node]

        # Assign new index and store
        new_index = len(self.node_list)
        self.node_list.append(node)
        self.node_to_index[node] = new_index
        return new_index

    def get_node(self, index):
        """Get a node by its index"""
        return self.node_list[index]

    def make(self, variable, low_idx, high_idx):
        """
        Create a decision node with given variable and children.
        Applies reduction rules automatically.

        Args:
            variable: The variable name for this node
            low_idx: Index of the low (0) child
            high_idx: Index of the high (1) child

        Returns:
            Index of the resulting node
        """
        # REDUCTION RULE 1: If both children are the same, skip this node
        if low_idx == high_idx:
            return low_idx

        # Create the node and add it (handles duplicates automatically)
        new_node = Node(variable=variable, low_child=low_idx, high_child=high_idx)
        return self._add_node(new_node)

    def create_variable(self, var_name):
        """
        Create a BDD for a single variable.
        x is TRUE when x=1, FALSE when x=0
        """
        if var_name not in self.var_level:
            raise ValueError(f"Unknown variable: {var_name}. Valid variables: {self.variable_ordering}")
        return self.make(var_name, self.FALSE, self.TRUE)

    # ==================== BOOLEAN OPERATIONS ====================

    def apply_not(self, node_idx):
        """
        Compute NOT of a BDD.
        Recursively swaps TRUE and FALSE terminals.
        """
        node = self.get_node(node_idx)

        # Base case: flip terminal values
        if node.is_terminal():
            if node.terminal_value:
                return self.FALSE
            else:
                return self.TRUE

        # Recursive case: apply NOT to both children
        new_low = self.apply_not(node.low_child)
        new_high = self.apply_not(node.high_child)
        return self.make(node.variable, new_low, new_high)

    def apply_and(self, idx1, idx2):
        """
        Compute AND of two BDDs using the Apply algorithm.
        """
        node1 = self.get_node(idx1)
        node2 = self.get_node(idx2)

        # Terminal cases for AND
        if idx1 == self.FALSE or idx2 == self.FALSE:
            return self.FALSE
        if idx1 == self.TRUE:
            return idx2
        if idx2 == self.TRUE:
            return idx1

        # Both are decision nodes - find which variable comes first
        level1 = self.var_level.get(node1.variable, float('inf'))
        level2 = self.var_level.get(node2.variable, float('inf'))

        if level1 == level2:
            # Same variable: recurse on both children
            var = node1.variable
            new_low = self.apply_and(node1.low_child, node2.low_child)
            new_high = self.apply_and(node1.high_child, node2.high_child)
        elif level1 < level2:
            # node1's variable comes first
            var = node1.variable
            new_low = self.apply_and(node1.low_child, idx2)
            new_high = self.apply_and(node1.high_child, idx2)
        else:
            # node2's variable comes first
            var = node2.variable
            new_low = self.apply_and(idx1, node2.low_child)
            new_high = self.apply_and(idx1, node2.high_child)

        return self.make(var, new_low, new_high)

    def apply_or(self, idx1, idx2):
        """
        Compute OR of two BDDs.
        Uses De Morgan's law: A OR B = NOT(NOT A AND NOT B)
        """
        not_1 = self.apply_not(idx1)
        not_2 = self.apply_not(idx2)
        and_result = self.apply_and(not_1, not_2)
        return self.apply_not(and_result)

    def apply_xor(self, idx1, idx2):
        """
        Compute XOR of two BDDs.
        A XOR B = (A AND NOT B) OR (NOT A AND B)
        """
        a_and_not_b = self.apply_and(idx1, self.apply_not(idx2))
        not_a_and_b = self.apply_and(self.apply_not(idx1), idx2)
        return self.apply_or(a_and_not_b, not_a_and_b)

    def apply_implies(self, idx1, idx2):
        """
        Compute IMPLIES of two BDDs.
        A -> B = NOT A OR B
        """
        not_a = self.apply_not(idx1)
        return self.apply_or(not_a, idx2)

    def apply_iff(self, idx1, idx2):
        """
        Compute IFF (bi-implication) of two BDDs.
        A <-> B = (A -> B) AND (B -> A)
        """
        a_implies_b = self.apply_implies(idx1, idx2)
        b_implies_a = self.apply_implies(idx2, idx1)
        return self.apply_and(a_implies_b, b_implies_a)

    # ==================== FORMULA PARSER ====================

    def parse(self, formula_string):
        """
        Parse a Boolean formula string and build its BDD.

        Supported operators (in order of precedence, lowest to highest):
        - <-> : bi-implication (iff)
        - ->  : implication
        - ^   : xor
        - |   : or
        - &   : and
        - ~   : not (prefix)

        Examples:
            "(a & b) | c"
            "a -> b"
            "~(a & b)"
        """
        # Remove all whitespace
        formula_string = formula_string.replace(" ", "")

        # Tokenize the formula
        self._tokens = self._tokenize(formula_string)
        self._current_pos = 0

        # Parse using recursive descent
        result = self._parse_iff()

        # Make sure we consumed all tokens
        if self._current_pos < len(self._tokens):
            remaining = self._tokens[self._current_pos:]
            raise ValueError(f"Unexpected tokens at end: {remaining}")

        return result

    def _tokenize(self, formula):
        """Break formula string into tokens"""
        tokens = []
        i = 0

        while i < len(formula):
            ch = formula[i]

            # Single-character operators and parentheses
            if ch in "()&|~^":
                tokens.append(ch)
                i += 1

            # Two-character operator: ->
            elif formula[i:i+2] == "->":
                tokens.append("->")
                i += 2

            # Three-character operator: <->
            elif formula[i:i+3] == "<->":
                tokens.append("<->")
                i += 3

            # Variable names: alphanumeric and underscores
            elif ch.isalnum() or ch == "_":
                start = i
                while i < len(formula) and (formula[i].isalnum() or formula[i] == "_"):
                    i += 1
                tokens.append(formula[start:i])

            else:
                # Skip unknown characters
                i += 1

        return tokens

    def _peek(self):
        """Look at current token without consuming it"""
        if self._current_pos < len(self._tokens):
            return self._tokens[self._current_pos]
        return None

    def _consume(self):
        """Consume and return current token"""
        token = self._peek()
        self._current_pos += 1
        return token

    def _parse_iff(self):
        """Parse bi-implication (lowest precedence)"""
        left = self._parse_implies()

        while self._peek() == "<->":
            self._consume()
            right = self._parse_implies()
            left = self.apply_iff(left, right)

        return left

    def _parse_implies(self):
        """Parse implication"""
        left = self._parse_xor()

        while self._peek() == "->":
            self._consume()
            right = self._parse_xor()
            left = self.apply_implies(left, right)

        return left

    def _parse_xor(self):
        """Parse XOR"""
        left = self._parse_or()

        while self._peek() == "^":
            self._consume()
            right = self._parse_or()
            left = self.apply_xor(left, right)

        return left

    def _parse_or(self):
        """Parse OR"""
        left = self._parse_and()

        while self._peek() == "|":
            self._consume()
            right = self._parse_and()
            left = self.apply_or(left, right)

        return left

    def _parse_and(self):
        """Parse AND"""
        left = self._parse_not()

        while self._peek() == "&":
            self._consume()
            right = self._parse_not()
            left = self.apply_and(left, right)

        return left

    def _parse_not(self):
        """Parse NOT (prefix operator)"""
        if self._peek() == "~":
            self._consume()
            operand = self._parse_not()  # NOT is right-associative
            return self.apply_not(operand)

        return self._parse_primary()

    def _parse_primary(self):
        """Parse primary expressions: variables and parenthesized expressions"""
        token = self._peek()

        if token is None:
            raise ValueError("Unexpected end of formula")

        # Parenthesized expression
        if token == "(":
            self._consume()
            result = self._parse_iff()
            if self._peek() != ")":
                raise ValueError("Missing closing parenthesis")
            self._consume()
            return result

        # Variable name
        if token[0].isalnum() or token[0] == "_":
            self._consume()
            return self.create_variable(token)

        raise ValueError(f"Unexpected token: {token}")

    # ==================== EXPORT FUNCTIONS ====================

    def save_to_text(self, root_idx, filepath):
        """
        Save the BDD to a human-readable text file.

        Args:
            root_idx: Index of the root node
            filepath: Path to output file
        """
        with open(filepath, 'w') as f:
            f.write("=" * 50 + "\n")
            f.write("ROBDD Output\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Variable ordering: {self.variable_ordering}\n")
            f.write(f"Root node index: {root_idx}\n")
            f.write(f"Total nodes: {len(self.node_list)}\n\n")

            # Check if result is trivial
            if root_idx == self.TRUE:
                f.write("Result: TAUTOLOGY (always TRUE)\n\n")
            elif root_idx == self.FALSE:
                f.write("Result: CONTRADICTION (always FALSE)\n\n")

            f.write("Node listing:\n")
            f.write("-" * 40 + "\n")

            for idx, node in enumerate(self.node_list):
                if node.is_terminal():
                    val = "1 (TRUE)" if node.terminal_value else "0 (FALSE)"
                    f.write(f"  [{idx}] Terminal: {val}\n")
                else:
                    f.write(f"  [{idx}] Variable: {node.variable}\n")
                    f.write(f"        Low (0) -> {node.low_child}\n")
                    f.write(f"        High (1) -> {node.high_child}\n")

    def save_to_dot(self, root_idx, filepath):
        """
        Save the BDD to DOT format for graphviz visualization.

        Args:
            root_idx: Index of the root node
            filepath: Path to output file (should end in .dot)
        """
        with open(filepath, 'w') as f:
            f.write("digraph BDD {\n")
            f.write("    rankdir=TB;\n")  # Top to bottom layout
            f.write("    node [shape=circle];\n\n")

            # Style for terminal nodes (boxes)
            f.write("    // Terminal nodes\n")
            f.write('    0 [label="0", shape=box, style=filled, fillcolor="#ffcccc"];\n')
            f.write('    1 [label="1", shape=box, style=filled, fillcolor="#ccffcc"];\n\n')

            # Track which nodes we've visited (only draw reachable nodes)
            visited = set()

            def draw_node(idx):
                if idx in visited:
                    return
                visited.add(idx)

                node = self.get_node(idx)
                if node.is_terminal():
                    return  # Already drew terminal nodes above

                # Draw this decision node
                f.write(f'    {idx} [label="{node.variable}"];\n')

                # Draw edges
                # Low edge: dashed red line, labeled 0
                f.write(f'    {idx} -> {node.low_child} [style=dashed, color=red, label="0"];\n')
                # High edge: solid blue line, labeled 1
                f.write(f'    {idx} -> {node.high_child} [style=solid, color=blue, label="1"];\n')

                # Recurse to children
                draw_node(node.low_child)
                draw_node(node.high_child)

            f.write("    // Decision nodes and edges\n")
            draw_node(root_idx)

            f.write("}\n")

    def export(self, root_idx, base_filename):
        """
        Export BDD to both text and DOT formats.

        Args:
            root_idx: Index of the root node
            base_filename: Base name for output files (without extension)
        """
        self.save_to_text(root_idx, base_filename + ".txt")
        self.save_to_dot(root_idx, base_filename + ".dot")

        # Try to render PNG if graphviz is available
        try:
            import graphviz
            src = graphviz.Source.from_file(base_filename + ".dot")
            src.render(base_filename, format='png', cleanup=True)
            print(f"  Generated: {base_filename}.png")
        except ImportError:
            print(f"  Graphviz not installed. To generate PNG, run:")
            print(f"    dot -Tpng {base_filename}.dot -o {base_filename}.png")
        except Exception as e:
            print(f"  Could not generate PNG: {e}")
