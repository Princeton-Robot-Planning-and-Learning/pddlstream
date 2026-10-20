# Install verification

Checks that this fork installs with pip and can actually plan.

## Usage

```bash
./scripts/verify_install.sh              # this repository, branch `main`
./scripts/verify_install.sh v0.2.0       # any branch, tag or SHA
./scripts/verify_install.sh .            # a local checkout (fast, skips the clone)
```

Point it at a different repository with
`PDDLSTREAM_REPO=https://github.com/<owner>/pddlstream.git`.

## What it checks

| Check | Catches |
|---|---|
| `pip install` succeeds | build backend, `setup.py` FastDownward compile |
| `FD_PATH` resolves into site-packages | the path patch regressing to `../../downward/` |
| the `downward` binary exists and is ~3 MB | binary missing from the wheel, or shipped unstripped |
| a 2-step plan comes back correct | the vendored translator and the search binary both work |
| no top-level names in `sys.modules` | the translator leaking `pddl`, `options`, `tools`, ... |

- The smoke test runs from a scratch directory so a stray checkout on `sys.path` cannot
mask a broken install. `smoke_test.py` can also be run on its own against an environment
that already has pddlstream.

- The `installed` line reports only `site-packages/pddlstream` (~9 MB). The examples and
their robot models add roughly another 390 MB.

## Requirements

- `make` and a C++ compiler must be present. `cmake` does not — it is pulled in as a build
dependency from PyPI.
- Verified on Python 3.10 and 3.13. The script uses whichever `python3` is on `PATH`.

## Packaging regression checks

From the repository root, build and inspect a wheel:

```bash
python -m pip wheel --no-deps --wheel-dir dist .
python scripts/verify_wheel.py dist/pddlstream-0.2.0-py3-none-linux_x86_64.whl
```

Use the filename produced by the build on your platform. This checks the platform
and Python ABI tags, executable permissions, absence of FastDownward build/source
files, and inclusion of the translator and example assets. Repeating the build
without cleaning the checkout should also succeed.

Compile and run the optional-reference regression check with GCC 12 or GCC 15:

```bash
"${CXX:-c++}" -std=c++11 scripts/test_optional_ref.cpp -o /tmp/pddlstream-optional-test
/tmp/pddlstream-optional-test
```

Compiling that test with `-DTEST_REJECT_TEMPORARY` must fail: an optional reference
must reject a temporary object instead of retaining a dangling reference.
