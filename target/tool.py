#
#    Helper module to build macOS version of various source ports
#    Copyright (C) 2020-2025 Alexey Lysiuk
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import subprocess

import aedi.target.base as base
from aedi.state import BuildState


class DosBoxXTarget(base.ConfigureMakeDependencyTarget):
    # Depends on autoconf, automake, freetype
    # TODO: fix absolute paths in bin/* and share/autoconf/autom4te.cfg
    def __init__(self, name='dosbox-x'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/joncampbell123/dosbox-x/archive/refs/tags/dosbox-x-v2023.10.06.tar.gz',
            '65f756e29f9c9b898fdbd22b0cb9b3b24c6e3becb5dcda588aa20a3fde9539a5')

    def configure(self, state: BuildState):
        # Invoke MakeTarget.configure() explicitly to create symlinks needed for autoconf
        base.MakeTarget.configure(self, state)

        # Generate configure script with autoconf
        work_path = state.build_path / self.src_root
        subprocess.run(('./autogen.sh',), check=True, cwd=work_path, env=state.environment)

        opts = state.options
        opts['--disable-libfluidsynth'] = None  # TODO: Resolve conflict with internal FLAC codec
        opts['--disable-libslirp'] = None  # TODO: Add slirp target
        opts['--enable-sdl2'] = None

        # Run generated configure script
        super().configure(state)


class DzipTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='dzip'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/kugelrund/dzip/archive/refs/tags/v3.1.tar.gz',
            '9f057e35ef5ddda1a0911b8f877a41b2934669377cb053b45364ddb72716b520')


class EricWToolsTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='ericw-tools'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/ericwa/ericw-tools/archive/refs/tags/v0.18.1.tar.gz',
            '97790e742d4c06f2e4285d96ada597bb3c95a2623b8c5e67a14753d9735d4564',
            patches='ericw-tools-hardcode-version')


class GlslangTarget(base.CMakeSharedDependencyTarget):
    def __init__(self, name='glslang'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/glslang/archive/refs/tags/15.3.0.tar.gz',
            'c6c21fe1873c37e639a6a9ac72d857ab63a5be6893a589f34e09a6c757174201')

    def configure(self, state: BuildState):
        args = ('python3', 'update_glslang_sources.py')
        subprocess.run(args, check=True, cwd=state.source, env=state.environment)

        opts = state.options
        opts['ENABLE_CTEST'] = 'NO'
        opts['SPIRV_TOOLS_BUILD_STATIC'] = 'NO'

        super().configure(state)


class QPakManTarget(base.CMakeTarget):
    def __init__(self, name='qpakman'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/bunder/qpakman/archive/refs/tags/v0.67.tar.gz',
            '0b2cfc0e66a6ea3f0e332409254e06f78f5bb9b47f6b134b90681468d701d421')

    def post_build(self, state: BuildState):
        self.copy_to_bin(state)
