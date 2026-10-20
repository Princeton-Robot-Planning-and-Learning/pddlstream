# PDDLStream pip installable

This is a fork of [caelan/pddlstream](https://github.com/caelan/pddlstream), branched at
[`2c7d6f5`](https://github.com/caelan/pddlstream/commit/2c7d6f514b07ed018e18710192aa0f91c2e70ee2),
that installs with `pip`. Led by [@Minseo10](https://github.com/Minseo10).

Three things differ from upstream:

- **FastDownward is vendored and built at install time.** It lives at
  `pddlstream/_downward` (not in a `downward` submodule), and is compiled during the
  build. The platform-specific wheel includes the stripped search binary (~3 MB).
- **The PDDL translator is vendored at `pddlstream/_translate`.** Upstream reaches it
  by appending the FastDownward build directory to `sys.path`, which puts `pddl`,
  `options`, `tools`, `normalize`, and `instantiate` on the top-level namespace of
  anything that imports pddlstream. Here it is imported under its own package name.
  See [`pddlstream/_translate/README.md`](pddlstream/_translate/README.md).
- **FastDownward is located relative to the installed package** instead of relative
  to a source checkout, with an `FD_PATH` environment variable to override it.

The planner, algorithms, language, and examples are unchanged. For the original
project documentation, publications, and example descriptions, see
[upstream PDDLStream](https://github.com/caelan/pddlstream).

## Installation

### Default installation

```bash
python -m pip install git+https://github.com/Princeton-Robot-Planning-and-Learning/pddlstream.git@v0.2.0
```

Requires Python 3.8+, Git, `make`, and a C++ compiler; pip supplies CMake
automatically. FastDownward is compiled during the build.

The installation includes the example code and robot assets and uses approximately
400 MB, mostly meshes under
`examples/pybullet/utils/models`.

For reproducible CI installs, replace `v0.2.0` with a full 40-character commit SHA.

Run a basic planning example after installation:

```bash
python -m examples.blocksworld.run
```

Run this outside a source checkout to exercise the installed package.

### Installation with PyBullet

```bash
python -m pip install "pddlstream[pybullet] @ git+https://github.com/Princeton-Robot-Planning-and-Learning/pddlstream.git@v0.2.0"
```

This adds `pybullet` and `scipy`. The example code and robot assets are included in
both installations. Interactive examples require a graphical display. Optional
IKFast extensions are not compiled by this pip install; see the
[robot library's instructions](https://github.com/caelan/ss-pybullet#ikfast-compilation).

Depending on your Python/build environment, compiling these optional bindings
may require a one-line header fix in the `examples/pybullet/utils` submodule
([caelan/ss-pybullet](https://github.com/caelan/ss-pybullet)). If compilation fails
because `python2.7/Python.h` is missing, edit
`examples/pybullet/utils/pybullet_tools/ikfast/ikfast.h`:

```diff
-#include "python2.7/Python.h"
+#include "Python.h"
```

### Verifying an install

From a checkout of this repository:

```bash
./scripts/verify_install.sh v0.2.0
```

This installs the release into a temporary virtual environment, solves a small
problem end to end, and checks that the search binary shipped and the translator
leaked no top-level module names. The temporary environment is removed afterward.
See [scripts/README.md](scripts/README.md) for details, including how to test an
existing installation.

### Working from a checkout

To install this source tree, including fixes not yet in the `v0.2.0` release:

```bash
git clone --recursive https://github.com/Princeton-Robot-Planning-and-Learning/pddlstream.git
cd pddlstream
python -m pip install ".[pybullet]"
python -m examples.blocksworld.run
```

Use `python -m pip install .` if you do not need PyBullet. Installing from the
checkout builds FastDownward in place and installs the Python dependencies.

A checkout shadows the installed package on `sys.path`. If you only clone the
repository after installing a wheel, either build FastDownward in that checkout
or set `FD_PATH` to the installed `site-packages/pddlstream/_downward` directory.
Running `python pddlstream/_downward/build.py` directly requires CMake on `PATH`;
the isolated CMake dependency used by pip is not retained in your environment.
