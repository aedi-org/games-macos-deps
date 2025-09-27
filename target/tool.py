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

import os
import subprocess

from aedi.state import BuildState
from aedi.target import base


class DosBoxXTarget(base.ConfigureMakeDependencyTarget):
    # Depends on autoconf, automake, freetype
    # TODO: fix absolute paths in bin/* and share/autoconf/autom4te.cfg
    def __init__(self):
        super().__init__('dosbox-x')

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
    def __init__(self):
        super().__init__('dzip')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/kugelrund/dzip/archive/refs/tags/v3.2.tar.gz',
            '7f7b80c3393232735a57cde0243e00923bbc16ea07daaa308e0ce1e3641bb93a')


class EricWToolsTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('ericw-tools')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/ericwa/ericw-tools/archive/refs/tags/v0.18.1.tar.gz',
            '97790e742d4c06f2e4285d96ada597bb3c95a2623b8c5e67a14753d9735d4564',
            patches='ericw-tools-hardcode-version')


class GlslangTarget(base.CMakeSharedDependencyTarget):
    def __init__(self):
        super().__init__('glslang')
        self.prerequisites = 'spirv-tools'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/glslang/archive/refs/tags/16.0.0.tar.gz',
            '172385478520335147d3b03a1587424af0935398184095f24beab128a254ecc7')

    def configure(self, state: BuildState):
        args = ('python3', 'update_glslang_sources.py')
        subprocess.run(args, check=True, cwd=state.source, env=state.environment)

        opts = state.options
        opts['ENABLE_CTEST'] = 'NO'
        opts['SPIRV_TOOLS_BUILD_STATIC'] = 'NO'

        super().configure(state)


class JpegoptimTarget(base.CMakeTarget):
    def __init__(self):
        super().__init__('jpegoptim')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/tjko/jpegoptim/archive/refs/tags/v1.5.5.tar.gz',
            '90a309d1c092de358bb411d702281ac3039b489d03adb0bc3c4ef04cf0067d38')

    def configure(self, state: BuildState):
        state.options['USE_MOZJPEG'] = 'NO'
        super().configure(state)

    def post_build(self, state: BuildState):
        self.copy_to_bin(state)


class OptiPngTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('optipng')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceforge.net/projects/optipng/files/OptiPNG/optipng-7.9.1/optipng-7.9.1.tar.gz',
            'c2579be58c2c66dae9d63154edcb3d427fef64cb00ec0aff079c9d156ec46f29')

    def configure(self, state: BuildState):
        opts = state.options
        opts['MINITIFF_BUILD_TESTS'] = 'NO'
        opts['GIFREAD_BUILD_TESTS'] = 'NO'
        opts['OPTIPNG_BUILD_TESTS'] = 'NO'
        opts['OPTIPNG_USE_SYSTEM_LIBS'] = 'YES'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        # Executable permissions were lost during install phase
        os.chmod(state.install_path / 'bin/optipng', 0o757)


class QPakManTarget(base.CMakeTarget):
    def __init__(self):
        super().__init__('qpakman')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/bunder/qpakman/archive/refs/tags/v0.67.tar.gz',
            '0b2cfc0e66a6ea3f0e332409254e06f78f5bb9b47f6b134b90681468d701d421')

    def post_build(self, state: BuildState):
        self.copy_to_bin(state)


class SpirvToolsTarget(base.CMakeSharedDependencyTarget):
    def __init__(self):
        super().__init__('spirv-tools')
        self.prerequisites = 'spirv-headers'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/SPIRV-Tools/archive/refs/tags/vulkan-sdk-1.4.321.0.tar.gz',
            '8327fb8f3e9472346a004c91dbb83a6e5f3b36c3846c142cf8c0dc8fac8710f3')

    def configure(self, state: BuildState):
        external_path = state.build_path / 'external'

        if not external_path.exists():
            external_path.mkdir(parents=True)

            headers_path = external_path / 'spirv-headers'
            headers_path.symlink_to(state.deps_path / 'spirv-headers')

        opts = state.options
        opts['ENABLE_CTEST'] = 'NO'
        opts['SPIRV_TOOLS_BUILD_STATIC'] = 'NO'

        super().configure(state)
