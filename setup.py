"""Build FastDownward as part of building the wheel.

pddlstream shells out to a compiled `downward` binary, so a plain source install is not
enough -- the binary has to exist under _downward/builds/release/bin/ by the time package
data is collected. Hooking build_py is what makes `pip install git+...` work unattended.
"""

import pathlib
import shutil
import subprocess
import sys

from setuptools import Distribution, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_py import build_py

DOWNWARD = pathlib.Path(__file__).parent.resolve() / "pddlstream" / "_downward"


class BuildFastDownward(build_py):
    """Compile FastDownward, then let build_py collect the result as package data."""

    def run(self):
        # Upstream's build.py locates its own root through __main__.__file__, so it has to
        # be run as a script path rather than imported.
        subprocess.check_call([sys.executable, str(DOWNWARD / "build.py")])

        # The binary carries ~120MB of debug symbols in the default release config.
        binary = DOWNWARD / "builds" / "release" / "bin" / "downward"
        strip = shutil.which("strip")
        if strip and binary.exists():
            subprocess.call([strip, str(binary)])

        super().run()


class PlatformDistribution(Distribution):
    """Install the bundled native executable into the platform library directory."""

    def has_ext_modules(self):
        return True


class PlatformWheel(bdist_wheel):
    """FastDownward depends on the platform, but not on the Python ABI."""

    def get_tag(self):
        _, _, platform = super().get_tag()
        return "py3", "none", platform


setup(
    distclass=PlatformDistribution,
    cmdclass={"build_py": BuildFastDownward, "bdist_wheel": PlatformWheel},
)
