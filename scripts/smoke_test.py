"""Minimal end-to-end check of an installed pddlstream.

Exercises the two halves that packaging can break independently: the vendored Python
translator (PDDL -> SAS+) and the compiled FastDownward search binary. Deliberately uses
a trivial STRIPS domain so a failure means the install is wrong, not the planner.

Run it from a directory that is NOT a pddlstream checkout, otherwise a source tree on
sys.path can mask a broken install.
"""

import os
import sys

DOMAIN = """
(define (domain corridor)
  (:requirements :strips)
  (:predicates (at ?x) (connected ?x ?y))
  (:action move
    :parameters (?from ?to)
    :precondition (and (at ?from) (connected ?from ?to))
    :effect (and (at ?to) (not (at ?from)))))
"""

PROBLEM = """
(define (problem walk)
  (:domain corridor)
  (:objects a b c)
  (:init (at a) (connected a b) (connected b c))
  (:goal (at c)))
"""

EXPECTED = [("move", ("a", "b")), ("move", ("b", "c"))]

# Names upstream leaked into the global namespace by putting translate/ on sys.path.
LEAK_CANARIES = ["pddl", "options", "tools", "graph", "normalize", "instantiate"]


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    if os.path.isdir("pddlstream") and os.path.isdir("pddlstream/algorithms"):
        fail("run this from outside a pddlstream checkout; the source tree would mask "
             "whatever was installed")

    try:
        import pddlstream.algorithms.downward as downward
        from pddlstream.algorithms.search import solve_from_pddl
    except ImportError as exc:
        fail(f"could not import pddlstream: {exc}")

    print(f"pddlstream : {os.path.dirname(os.path.dirname(downward.__file__))}")
    print(f"FD_PATH    : {os.path.normpath(downward.FD_PATH)}")

    binary = os.path.join(downward.FD_BIN, "downward")
    if not os.path.exists(binary):
        fail(f"FastDownward binary missing at {binary}")
    print(f"FD binary  : {os.path.getsize(binary) / 1e6:.1f} MB")

    plan, cost = solve_from_pddl(DOMAIN, PROBLEM)
    if plan is None:
        fail("planner returned no plan")

    actual = [(action.name, action.args) for action in plan]
    if actual != EXPECTED:
        fail(f"wrong plan\n  expected {EXPECTED}\n  got      {actual}")
    print(f"plan       : {' -> '.join(a + str(g) for a, g in actual)}  (cost {cost})")

    leaked = [name for name in LEAK_CANARIES if name in sys.modules]
    if leaked:
        fail(f"translator leaked top-level names into sys.modules: {leaked}")
    print("namespace  : clean")

    print("\nPASS: translator and FastDownward search both work.")


if __name__ == "__main__":
    main()
