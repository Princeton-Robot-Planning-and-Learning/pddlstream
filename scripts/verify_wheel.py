"""Check binary wheel metadata and payload: python scripts/verify_wheel.py WHEEL."""

import argparse
from email.parser import Parser
from pathlib import Path
from zipfile import ZipFile


def verify(path):
    with ZipFile(path) as wheel:
        names = wheel.namelist()
        metadata_paths = [name for name in names if name.endswith('.dist-info/WHEEL')]
        assert len(metadata_paths) == 1, metadata_paths
        metadata = Parser().parsestr(wheel.read(metadata_paths[0]).decode())
        assert metadata['Root-Is-Purelib'] == 'false', metadata
        tags = metadata.get_all('Tag')
        assert tags and all(tag.startswith('py3-none-') and not tag.endswith('-any')
                            for tag in tags), tags
        assert path.stem.endswith(tags[0]), (path.name, tags)

        binary = 'pddlstream/_downward/builds/release/bin/downward'
        assert binary in names, 'FastDownward executable missing'
        assert wheel.getinfo(binary).external_attr >> 16 & 0o111, 'not executable'
        assert wheel.getinfo(binary).file_size > 0, 'empty executable'
        allowed = {binary, 'pddlstream/_downward/LICENSE.md'}
        unexpected = [name for name in names
                      if name.startswith('pddlstream/_downward/') and name not in allowed]
        assert not unexpected, unexpected[:10]
        assert 'pddlstream/_downward/LICENSE.md' in names
        assert 'pddlstream/_translate/__init__.py' in names
        assert 'examples/blocksworld/domain.pddl' in names
        assert any(name.startswith('examples/pybullet/utils/models/')
                   and name.endswith('.urdf') for name in names), 'robot assets missing'
        assert not any('/CMakeFiles/' in name for name in names)
        print('PASS:', path.name, 'metadata, executable, translator, and example assets')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheel', type=Path)
    verify(parser.parse_args().wheel)
