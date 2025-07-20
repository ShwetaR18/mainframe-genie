import threading
from functools import lru_cache
import time
import random

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        if isinstance(node, Node):
            self.children.append(node)

class TreeAnalyzer:
    def __init__(self, root):
        self.root = root
        self.lock = threading.Lock()

    def _analyze_node(self, node, depth=0):
        time.sleep(random.uniform(0.01, 0.1))
        with self.lock:
            print(f"{' ' * depth * 2}Analyzing: {node.value}")
        for child in node.children:
            self._analyze_node(child, depth + 1)

    def start_analysis(self):
        thread = threading.Thread(target=self._analyze_node, args=(self.root,))
        thread.start()
        thread.join()

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def deep_logic_controller():
    def step_a():
        print("Step A initiated.")
        if random.choice([True, False]):
            print("Step A branching to B")
            return step_b()
        else:
            print("Step A branching to C")
            return step_c()

    def step_b():
        print("Running Step B")
        for i in range(5):
            print(f"Fib({i}) = {fibonacci(i)}")
        return "B Done"

    def step_c():
        print("Running Step C")
        total = 0
        for i in range(100):
            if i % 2 == 0:
                total += i
            elif i % 3 == 0:
                total -= i
            else:
                total += i ** 0.5
        return f"C Done with total = {total}"

    return step_a()

def complex_generator(n):
    for i in range(n):
        yield (i, i*i, fibonacci(i))

def main():
    print("=== Starting Tree Analysis ===")
    root = Node("Root")
    child1 = Node("Child 1")
    child2 = Node("Child 2")
    child1.add_child(Node("Child 1.1"))
    child1.add_child(Node("Child 1.2"))
    child2.add_child(Node("Child 2.1"))
    root.add_child(child1)
    root.add_child(child2)

    analyzer = TreeAnalyzer(root)
    analyzer.start_analysis()

    print("\n=== Running Deep Logic ===")
    result = deep_logic_controller()
    print("Deep Logic Result:", result)

    print("\n=== Generator Output ===")
    for val in complex_generator(10):
        print(val)

if __name__ == "__main__":
    main()
