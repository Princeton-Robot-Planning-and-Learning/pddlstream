# Vendored FastDownward translator

Copied from `pddlstream/_downward/src/translate/`, which is
[caelan/downward](https://github.com/caelan/downward) at commit
`11e98c555c58a44d42a28a76174620d421de2d3b` — the revision the `downward` submodule
pinned before it was absorbed. All credit to the original authors.

## Why this exists

Upstream's `translate/` is designed to be put on `sys.path`, so its modules import each
other by bare name (`import pddl`, `import options`). Doing that from an installed
package leaks generic top-level names — `pddl`, `tools`, `options`, `graph`, `timers` —
into every process that imports pddlstream. `pddl` is also a real package on PyPI, so
the leak can shadow or be shadowed.

Making the directory a proper package removes the `sys.path` manipulation entirely.

## Modifications

* Added `__init__.py`.
* Rewrote sibling imports to absolute (`import pddlstream._translate.pddl as pddl`).
  `pddl/` and `pddl_parser/` already used relative imports internally and were left
  alone apart from three bare imports of top-level siblings.
* Removed `tests/` and `regression-tests/`.

Nothing else was touched — no behavior changes, no reformatting.

## Relationship to `_downward/src/translate/`

`_downward/src/translate/` is still the upstream source of truth and is what the CMake
build copies into `builds/release/bin/translate/`. pddlstream does not import from
there; it imports this package. The copy under `builds/` is inert, kept only so the
build stays identical to upstream.

## Re-vendoring

To move to a newer downward, update `_downward/`, then:

```bash
rm -rf pddlstream/_translate
cp -r pddlstream/_downward/src/translate pddlstream/_translate
rm -rf pddlstream/_translate/tests pddlstream/_translate/regression-tests
touch pddlstream/_translate/__init__.py
# then rewrite sibling imports to `pddlstream._translate.<module>`
```

Callers outside this package also import translator modules directly
(`pddlstream/algorithms/instantiate_task.py`, `scheduling/recover_axioms.py`,
`language/temporal.py`, and others) and use the same absolute form.
