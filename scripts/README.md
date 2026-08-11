# Install verification

Checks that this fork installs with pip and can actually plan — no manual clone, no
manual FastDownward build.

## Usage

```bash
./scripts/verify_install.sh              # install from git, branch `packaging`
./scripts/verify_install.sh <ref>        # any branch, tag or SHA
./scripts/verify_install.sh .            # a local checkout (fast, skips the clone)
```

Everything happens in a temporary virtualenv that is deleted on exit. Nothing touches
the active environment.

Point it elsewhere with `PDDLSTREAM_REPO=https://github.com/<owner>/pddlstream.git`.

## What it checks

| Check | Catches |
|---|---|
| `pip install` succeeds | build backend, `setup.py` FastDownward compile |
| `FD_PATH` resolves into site-packages | the path patch regressing to `../../downward/` |
| the `downward` binary exists and is ~3 MB | binary missing from the wheel, or shipped unstripped |
| a 2-step plan comes back correct | the vendored translator and the search binary both work |
| no top-level names in `sys.modules` | the translator leaking `pddl`, `options`, `tools`, ... |

The smoke test runs from a scratch directory so a stray checkout on `sys.path` cannot
mask a broken install. `smoke_test.py` can also be run on its own against an environment
that already has pddlstream.

## Requirements

`make` and a C++ compiler must be present. `cmake` does not — it is pulled in as a build
dependency from PyPI.

A full run takes well under a minute on a many-core machine — FastDownward compiles in
parallel. Installing from a git ref also pulls the `examples/pybullet/utils` submodule,
because pip runs `git submodule update --init --recursive` on any repository that has a
`.gitmodules`. That is ~400 MB of robot meshes but only a few seconds on a fast
connection; the local-checkout form skips it entirely.

Verified on Python 3.10 and 3.13. The script uses whichever `python3` is on `PATH`.
