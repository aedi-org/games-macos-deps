#
#    Helper module to build macOS version of various source ports
#    Copyright (C) 2020-2026 Alexey Lysiuk
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
import shlex
import shutil
import subprocess

from aedi.state import BuildState
from aedi.target import base


class Bzip2Target(base.MakeTarget):
    def __init__(self):
        super().__init__('bzip2')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz',
            'ab5a03176ee106d3f0fa90e381da478ddae405918153cca248e682cd0c4a2269')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('bzlib.h')

    def configure(self, state: BuildState):
        super().configure(state)

        opts = state.options
        # Add explicit targets in order to skip testing step that is incompatible with cross-compilation
        opts['bzip2'] = None
        opts['bzip2recover'] = None
        # Copy compiler flags from environment to command line argument, they would be overridden by Makefile otherwise
        cflags = 'CFLAGS'
        opts[cflags] = state.environment[cflags] + ' -D_FILE_OFFSET_BITS=64 -O2'

    def post_build(self, state: BuildState):
        opts = state.options
        opts['install'] = None
        opts['PREFIX'] = state.install_path

        self.install(state, state.options)
        self.write_pc_file(state, description='bzip2 compression library', version='1.0.8', libs='-lbz2')


class DumbTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('dumb')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/kode54/dumb/archive/2.0.3.tar.gz',
            '99bfac926aeb8d476562303312d9f47fd05b43803050cd889b44da34a9b2a4f9')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('include/dumb.h')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_ALLEGRO4'] = 'NO'
        opts['BUILD_EXAMPLES'] = 'NO'

        super().configure(state)

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        return 'Libs: -L${libdir} -ldumb\n' if line.startswith('Libs:') else line


class FlacTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('flac')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/xiph/flac/releases/download/1.5.0/flac-1.5.0.tar.xz',
            'f2c1c76592a82ffff8413ba3c4a1299b6c7ab06c734dee03fd88630485c2b920')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_CXXLIBS'] = 'NO'
        opts['BUILD_EXAMPLES'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'

        super().configure(state)


class FluidSynthTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('fluidsynth')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/FluidSynth/fluidsynth/archive/refs/tags/v2.5.6.tar.gz',
            '0825f024c9cf7a18073739b83612d46542ecbfb349ae9147a1e9f08e2d524407',
            patches='fluidsynth-sf3-support')

    def configure(self, state: BuildState):
        opts = state.options
        opts['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'sndfile')
        opts['DEFAULT_SOUNDFONT'] = 'default.sf2'
        opts['enable-framework'] = 'NO'
        opts['enable-readline'] = 'NO'
        opts['osal'] = 'cpp11'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        module_path = state.install_path / 'lib/cmake/fluidsynth/FluidSynth-static-targets-release.cmake'

        with open(module_path) as f:
            toremove = (
                'set_target_properties(FluidSynth::fluidsynth PROPERTIES\n'
                '  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/fluidsynth"\n'
                '  )\n',
                'list(APPEND _cmake_import_check_files_for_FluidSynth::fluidsynth "${_IMPORT_PREFIX}/bin/fluidsynth" )\n'
            )

            module = f.read()

            for entry in toremove:
                module = module.replace(entry, '')

        with open(module_path, 'w') as f:
            f.write(module)


class FmtTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('fmt')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/fmtlib/fmt/releases/download/12.1.0/fmt-12.1.0.zip',
            '695fd197fa5aff8fc67b5f2bbc110490a875cdf7a41686ac8512fb480fa8ada7')

    def configure(self, state: BuildState):
        opts = state.options
        opts['FMT_DOC'] = 'NO'
        opts['FMT_TEST'] = 'NO'

        super().configure(state)


class FreeTypeTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('freetype')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/freetype/freetype2/2.13.2/freetype-2.13.2.tar.xz',
            '12991c4e55c506dd7f9b765933e62fd2be2e06d421505d7950a132e4f1bb484d')

    def post_build(self, state: BuildState):
        super().post_build(state)

        bin_path = state.install_path / 'bin'
        os.makedirs(bin_path)
        shutil.copy(state.patch_path / 'freetype-config', bin_path)

        def update_linker_flags(line: str):
            link_flags = '-lbz2 -lpng16 -lz'
            link_var = '  INTERFACE_LINK_LIBRARIES '

            return f'{link_var}"{link_flags}"\n' if line.startswith(link_var) else line

        cmake_module = state.install_path / 'lib/cmake/freetype/freetype-config.cmake'
        self.update_text_file(cmake_module, update_linker_flags)


class FtglTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('ftgl')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/ftgl/FTGL%20Source/2.1.3~rc5/ftgl-2.1.3-rc5.tar.gz',
            '5458d62122454869572d39f8aa85745fc05d5518001bcefa63bd6cbb8d26565b',
            patches='ftgl-support-arm64')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('ftgl.pc.in')

    def configure(self, state: BuildState):
        opts = state.options
        opts['--with-glut-inc'] = '/dev/null'
        opts['--with-glut-lib'] = '/dev/null'

        super().configure(state)


class GlewTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('glew')
        self.src_root = 'build/cmake'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/nigels-com/glew/releases/download/glew-2.2.0/glew-2.2.0.tgz',
            'd4fc82893cfb00109578d0a1a2337fb8ca335b3ceccf97b97e5cc7f08e4353e1')

    def configure(self, state: BuildState):
        state.options['BUILD_UTILS'] = 'NO'
        super().configure(state)

    LINKER_FLAGS = '-framework OpenGL'

    def post_build(self, state: BuildState):
        super().post_build(state)

        def update_linker_flags(line: str):
            link_var = '  INTERFACE_LINK_LIBRARIES '

            if line.startswith(link_var):
                return f'{link_var}"{GlewTarget.LINKER_FLAGS}"\n'

            return line

        cmake_module = state.install_path / 'lib/cmake/glew/glew-targets.cmake'
        self.update_text_file(cmake_module, update_linker_flags)

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        libs = 'Libs:'

        if line.startswith(libs):
            return libs + ' -L${libdir} -lGLEW ' + GlewTarget.LINKER_FLAGS + os.linesep

        return line


class GlibTarget(base.MesonStaticTarget):
    def __init__(self):
        super().__init__('glib')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://download.gnome.org/sources/glib/2.84/glib-2.84.1.tar.xz',
            '2b4bc2ec49611a5fc35f86aca855f2ed0196e69e53092bab6bb73396bf30789a',
            patches='glib-fix-paths')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('glib.doap')

    def configure(self, state: BuildState):
        opts = state.options
        opts['glib_assert'] = 'false'
        opts['glib_checks'] = 'false'
        opts['glib_debug'] = 'disabled'
        opts['tests'] = 'false'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        self.make_platform_header(state, '../lib/glib-2.0/include/glibconfig.h')

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        return 'exec_prefix=${prefix}\n' + line if line.startswith('libdir=') else line


class GmeTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('gme')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libgme/game-music-emu/archive/refs/tags/0.6.4.tar.gz',
            'f2360feb5a32ace226c583df4faf6eff74145c81264aaea11e17a1af2f6f101a')

    def configure(self, state: BuildState):
        state.options['GME_BUILD_EXAMPLES'] = 'NO'
        super().configure(state)


class HarfBuzzTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('harfbuzz')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/harfbuzz/harfbuzz/archive/refs/tags/2.8.2.tar.gz',
            '4164f68103e7b52757a732227cfa2a16cfa9984da513843bb4eb7669adc6f220')

    def configure(self, state: BuildState):
        state.options['HB_HAVE_FREETYPE'] = 'ON'
        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        def update_config_cmake(line: str):
            include_var = '  INTERFACE_INCLUDE_DIRECTORIES '
            link_var = '  INTERFACE_LINK_LIBRARIES '

            if line.startswith(include_var):
                return include_var + '"${_IMPORT_PREFIX}/include/harfbuzz"\n'
            if line.startswith(link_var):
                return link_var + '"-framework ApplicationServices"\n'

            return line

        config_path = state.install_path / 'lib/cmake/harfbuzz/harfbuzzConfig.cmake'
        self.update_text_file(config_path, update_config_cmake)

        self.write_pc_file(state, description='HarfBuzz text shaping library', version='2.8.2', libs='-lharfbuzz',
                           libs_private='-lc++ -framework CoreFoundation -framework CoreGraphics -framework CoreText')


class InstPatchTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('instpatch')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/swami/libinstpatch/archive/refs/tags/v1.1.7.tar.gz',
            'b388ab6f843559fc2da94837c37dfd4cf5973cf7cc2a0ce3cb33260b81377e9f')

    def configure(self, state: BuildState):
        # Workaround for riff_dump link errors
        state.options['CMAKE_EXE_LINKER_FLAGS'] = '-framework Foundation'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        # Remove extra directory from include path
        include_path = state.install_path / 'include'
        include_subpath = include_path / 'libinstpatch-2/libinstpatch'
        shutil.move(str(include_subpath), include_path)


class JpegTurboTarget(base.CMakeDependencyTarget):
    def __init__(self):
        super().__init__('jpeg-turbo')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/3.2.0/libjpeg-turbo-3.2.0.tar.gz',
            '6f30092cef9fb839779646608f4ee14ae3cbac989c47fa05e841b0841f09878e')

    def configure(self, state: BuildState):
        opts = state.options
        opts['ENABLE_SHARED'] = 'NO'
        opts['WITH_TURBOJPEG'] = 'NO'

        super().configure(state)


class LameTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('lame')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceforge.net/projects/lame/files/lame/3.100/lame-3.100.tar.gz',
            'ddfe36cab873794038ae2c1210557ad34857a4b6bdc515785d1da9e175b1da1e')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('lame.spec')


class MadTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('mad')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/mad/libmad/0.15.1b/libmad-0.15.1b.tar.gz',
            'bbfac3ed6bfbc2823d3775ebb931087371e142bb0e9bb1bee51a76a6e0078690',
            patches='mad-support-arm64')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('mad.h')

    def configure(self, state: BuildState):
        state.options['--enable-fpm'] = '64bit'
        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        self.write_pc_file(state, description='MPEG Audio Decoder', version='0.15.1b')


class MikmodTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('mikmod')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/mikmod/libmikmod/3.3.13/libmikmod-3.3.13.tar.gz',
            '9fc1799f7ea6a95c7c5882de98be85fc7d20ba0a4a6fcacae11c8c6b382bb207')

    def configure(self, state: BuildState):
        opts = state.options
        opts['ENABLE_DOC'] = 'NO'
        opts['ENABLE_SHARED'] = 'NO'

        super().configure(state)


class ModPlugTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('modplug')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/modplug-xmms/libmodplug/0.8.9.0/libmodplug-0.8.9.0.tar.gz',
            '457ca5a6c179656d66c01505c0d95fafaead4329b9dbaa0f997d00a3508ad9de')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libmodplug.pc.in')

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        libs_private = 'Libs.private:'

        if line.startswith(libs_private):
            return libs_private + ' -lc++\n'

        return line


class MoltenVKTarget(base.MakeTarget):
    def __init__(self):
        super().__init__('moltenvk')

        # Building for multiple architectures is handled internally
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/MoltenVK/archive/refs/tags/v1.4.1.tar.gz',
            '9985f141902a17de818e264d17c1ce334b748e499ee02fcb4703e4dc0038f89c')

    def initialize(self, state: BuildState):
        super().initialize(state)
        self._make_dylib(state)

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('MoltenVKPackaging.xcodeproj')

    def configure(self, state: BuildState):
        state.options['macos'] = None

        # Unset platform to avoid using specified macOS deployment target and SDK
        # MoltenVK defines minimal OS version itself, and usually, it requires the very recent SDK
        state.platform = None

        super().configure(state)

    def build(self, state: BuildState):
        args = ['./fetchDependencies', '--macos']
        if state.verbose:
            args.append('-v')
        subprocess.run(args, check=True, cwd=state.build_path, env=state.environment)

        super().build(state)

    def post_build(self, state: BuildState):
        if state.xcode:
            return

        include_path = state.install_path / 'include'
        os.makedirs(include_path)

        lib_path = state.install_path / 'lib'
        os.makedirs(lib_path)

        src_path = state.build_path / 'Package/Latest/MoltenVK'
        shutil.copytree(src_path / 'include/MoltenVK', include_path / 'MoltenVK')
        shutil.copy(state.build_path / 'LICENSE', state.install_path / 'apache2.txt')
        shutil.copy(
            src_path / 'static/MoltenVK.xcframework/macos-arm64_x86_64/libMoltenVK.a',
            lib_path / 'libMoltenVK.a')

        self._make_dylib(state)

    def _make_dylib(self, state: BuildState):
        lib_path = state.deps_path / self.name / 'lib'
        static_lib_path = lib_path / 'libMoltenVK.a'
        dynamic_lib_path = lib_path / 'libMoltenVK.dylib'

        static_lib_time = os.stat(static_lib_path).st_mtime
        dynamic_lib_time = os.stat(dynamic_lib_path).st_mtime if os.path.exists(dynamic_lib_path) else 0

        if static_lib_time != dynamic_lib_time:
            os.makedirs(state.lib_path, exist_ok=True)

            args = [
                'clang++',
                '-stdlib=libc++',
                '-dynamiclib',
                '-arch', 'arm64',
                '-arch', 'x86_64',
                '-mmacosx-version-min=11.0',
                '-compatibility_version', '1.0.0',
                '-current_version', '1.0.0',
                '-install_name', '@rpath/libMoltenVK.dylib',
                '-framework', 'Metal',
                '-framework', 'IOSurface',
                '-framework', 'AppKit',
                '-framework', 'QuartzCore',
                '-framework', 'CoreGraphics',
                '-framework', 'IOKit',
                '-framework', 'Foundation',
                '-o', dynamic_lib_path,
                '-force_load', static_lib_path
            ]
            args += shlex.split(state.linker_flags())

            subprocess.run(args, check=True, env=state.environment)
            os.utime(dynamic_lib_path, (static_lib_time, static_lib_time))


class Mpg123Target(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('mpg123')
        self.src_root = 'ports/cmake'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.mpg123.de/download/mpg123-1.33.5.tar.bz2',
            '0d7ebc8da0aff3ca383c8c6b5a6adbe402ee5bb256685b8c5499f3a739f9d6dd',
            patches=('mpg123-have-fpu', 'mpg123-no-syn123'))

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_LIBOUT123'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'

        super().configure(state)


class OggTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('ogg')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/xiph/ogg/releases/download/v1.3.6/libogg-1.3.6.tar.xz',
            '5c8253428e181840cd20d41f3ca16557a9cc04bad4a3d04cce84808677fa1061')


class OpusTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('opus')

    def prepare_source(self, state: BuildState):
        # Temporary solution for lack of TLSv1.3 support in Apple Python
        # The following URL cannot be retrieved using Python 3.9.6 from Xcode 26.x
        # https://downloads.xiph.org/releases/opus/opus-1.6.1.tar.gz
        # ssl.SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1129)
        # >>> import ssl; print(ssl.OPENSSL_VERSION, ssl.HAS_TLSv1_3)
        # LibreSSL 2.8.3 False
        # TODO: remove this workaround when TLSv1.3 will be available in Python shipped with Xcode
        state.download_source(
            'https://ftp.osuosl.org/pub/xiph/releases/opus/opus-1.6.1.tar.gz',
            '6ffcb593207be92584df15b32466ed64bbec99109f007c82205f0194572411a1')

    def configure(self, state: BuildState):
        state.options['PC_BUILD'] = 'floating-point'
        super().configure(state)

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        cflags = 'Cflags:'
        libs = 'Libs:'

        if line.startswith(cflags):
            return cflags + ' -I${includedir}/opus\n'
        if line.startswith(libs):
            return libs + ' -L${libdir} -lopus\n'

        return line


class OpusFileTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('opusfile')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.osuosl.org/pub/xiph/releases/opus/opusfile-0.12.tar.gz',
            '118d8601c12dd6a44f52423e68ca9083cc9f2bfe72da7a8c1acb22a80ae3550b')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('opusfile.pc.in')

    def configure(self, state: BuildState):
        state.options['--enable-http'] = 'no'
        super().configure(state)


class PcreTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('pcre')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/pcre/pcre/8.45/pcre-8.45.tar.bz2',
            '4dae6fdcd2bb0bb6c37b5f97c33c2be954da743985369cddac3546e3218bffb8')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('pcre.h.in')

    def configure(self, state: BuildState):
        opts = state.options
        opts['--enable-unicode-properties'] = 'yes'
        opts['--enable-cpp'] = 'no'

        super().configure(state)


class PngTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('png')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/libpng/libpng16/1.6.55/libpng-1.6.55.tar.xz',
            'd925722864837ad5ae2a82070d4b2e0603dc72af44bd457c3962298258b8e82d')

    def configure(self, state: BuildState):
        opts = state.options
        opts['PNG_FRAMEWORK'] = 'NO'
        opts['PNG_SHARED'] = 'NO'

        super().configure(state)


class PortMidiTarget(base.CMakeTarget):
    def __init__(self):
        super().__init__('portmidi')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/portmedia/portmidi/217/portmidi-src-217.zip',
            '08e9a892bd80bdb1115213fb72dc29a7bf2ff108b378180586aa65f3cfd42e0f',
            patches='portmidi-modernize-cmake')

    def post_build(self, state: BuildState):
        include_path = state.install_path / 'include'
        os.makedirs(include_path)
        shutil.copy(state.source / 'pm_common/portmidi.h', include_path)
        shutil.copy(state.source / 'porttime/porttime.h', include_path)

        lib_path = state.install_path / 'lib'
        os.makedirs(lib_path)
        shutil.copy(state.build_path / 'libportmidi_s.a', lib_path / 'libportmidi.a')


class SamplerateTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('samplerate')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsndfile/libsamplerate/releases/download/0.2.1/libsamplerate-0.2.1.tar.bz2',
            'f6323b5e234753579d70a0af27796dde4ebeddf58aae4be598e39b3cee00c90a')

    def post_build(self, state: BuildState):
        super().post_build(state)

        def update_linker_flags(line: str):
            link_var = '  INTERFACE_LINK_LIBRARIES '
            return None if line.startswith(link_var) else line

        cmake_module = state.install_path / 'lib/cmake/SampleRate/SampleRateTargets.cmake'
        self.update_text_file(cmake_module, update_linker_flags)


class Sdl2Target(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sdl2')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL/releases/download/release-2.32.10/SDL2-2.32.10.tar.gz',
            '5f5993c530f084535c65a6879e9b26ad441169b3e25d789d83287040a9ca5165')

    def configure(self, state: BuildState):
        opts = state.options
        opts['SDL_STATIC_PIC'] = 'YES'
        opts['SDL_TEST'] = 'NO'

        super().configure(state)


class Sdl2ImageTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sdl2_image')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL_image/releases/download/release-2.8.12/SDL2_image-2.8.12.tar.gz',
            '393f5efb50536ec13ca4f4affb69cc9966d3c3f969e6c5e701faddf9f9785381')

    def configure(self, state: BuildState):
        opts = state.options
        opts['SDL2IMAGE_WEBP'] = 'YES'
        opts['SDL2IMAGE_WEBP_SHARED'] = 'NO'

        super().configure(state)


class Sdl2MixerTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sdl2_mixer')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.8.2/SDL2_mixer-2.8.2.tar.gz',
            '938dff531d00ace2296557a6599abe6f34599e2f34f0a4a08a397e2ccac8b8f7')

    def configure(self, state: BuildState):
        opts = state.options
        opts['SDL2MIXER_DEPS_SHARED'] = 'NO'
        opts['SDL2MIXER_FLAC_LIBFLAC'] = 'YES'
        opts['SDL2MIXER_GME'] = 'YES'
        opts['SDL2MIXER_MOD_MODPLUG'] = 'YES'
        opts['SDL2MIXER_MP3_MPG123'] = 'YES'
        opts['SDL2MIXER_SAMPLES'] = 'NO'
        opts['SDL2MIXER_VORBIS'] = 'VORBISFILE'

        super().configure(state)


class Sdl2NetTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sdl2_net')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL_net/releases/download/release-2.4.0/SDL2_net-2.4.0.tar.gz',
            '9cbca2527feb3f1a622d48ba65cc7dee9b1e3f2c55ceafb7d7720bb058aafb30')


class Sdl2TtfTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sdl2_ttf')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.15.tar.gz',
            'a9eceb1ad88c1f1545cd7bd28e7cbc0b2c14191d40238f531a15b01b1b22cd33',
            patches='sdl2_ttf-fix-cmake')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('SDL2_ttf.pc.in')

    def configure(self, state: BuildState):
        state.options['VERSION'] = '2.0.15'
        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        shutil.move(state.install_path / 'SDL2_ttf.framework/Resources', state.install_path / 'lib/cmake/SDL2_ttf')

    @staticmethod
    def _process_pkg_config(_, line: str) -> str:
        return line + 'Requires.private: freetype2\n' if line.startswith('Requires:') else line


class SfmlTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sfml')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.sfml-dev.org/files/SFML-2.5.1-sources.zip',
            'bf1e0643acb92369b24572b703473af60bac82caf5af61e77c063b779471bb7f',
            patches='sfml-support-arm64')

    def configure(self, state: BuildState):
        opts = state.options
        opts['CMAKE_OSX_ARCHITECTURES'] = state.architecture()
        opts['SFML_USE_SYSTEM_DEPS'] = 'YES'
        opts['SFML_MISC_INSTALL_PREFIX'] = state.install_path / 'share/SFML'
        # Use OpenAL Soft instead of Apple's framework
        opts['OPENAL_INCLUDE_DIR'] = state.include_path / 'AL'
        opts['OPENAL_LIBRARY'] = state.lib_path / 'libopenal.a'

        super().configure(state)


class SndFileTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sndfile')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsndfile/libsndfile/releases/download/1.2.2/libsndfile-1.2.2.tar.xz',
            '3799ca9924d3125038880367bf1468e53a1b7e3686a934f098b7e1d286cdb80e')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_EXAMPLES'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'
        opts['ENABLE_CPACK'] = 'NO'

        super().configure(state)


class SodiumTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('sodium')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/jedisct1/libsodium/releases/download/1.0.20-RELEASE/libsodium-1.0.20.tar.gz',
            'ebb65ef6ca439333c2bb41a0c1990587288da07f6c7fd07cb3a18cc18d30ce19')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libsodium.pc.in')


class VorbisTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('vorbis')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.osuosl.org/pub/xiph/releases/vorbis/libvorbis-1.3.7.tar.xz',
            'b33cc4934322bcbf6efcbacf49e3ca01aadbea4114ec9589d1b1e9d20f72954b')


class VulkanHeadersTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('vulkan-headers')
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/Vulkan-Headers/archive/refs/tags/v1.4.325.tar.gz',
            '5743da4e203456ef0a0d17950d448b4f70e93a19abdc547aa33c15482b4fec17')


class VulkanLoaderTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('vulkan-loader')
        self.version = '1.4.313'

    def prepare_source(self, state: BuildState):
        state.download_source(
            f'https://github.com/KhronosGroup/Vulkan-Loader/archive/refs/tags/v{self.version}.tar.gz',
            '0c2436993597f5bd0ee420b6b27632758ed3ab439043d251795fd13d4e70a2f3')

    def configure(self, state: BuildState):
        state.options['APPLE_STATIC_LOADER'] = 'YES'
        super().configure(state)

    def post_build(self, state: BuildState):
        lib_path = state.install_path / 'lib'
        os.makedirs(lib_path, exist_ok=True)
        shutil.copy(state.build_path / 'loader/libvulkan.a', lib_path)

        self.write_pc_file(state, filename='vulkan.pc',
                           name='Vulkan-Loader', description='Vulkan Loader', version=self.version,
                           libs='-lvulkan', libs_private='-lc++ -framework CoreFoundation')


class WavPackTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('wavpack')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/dbry/WavPack/releases/download/5.8.1/wavpack-5.8.1.tar.xz',
            '7322775498602c8850afcfc1ae38f99df4cbcd51386e873d6b0f8047e55c0c26')

    def configure(self, state: BuildState):
        opts = state.options
        opts['WAVPACK_BUILD_PROGRAMS'] = 'NO'
        opts['WAVPACK_ENABLE_LEGACY'] = 'YES'
        opts['WAVPACK_INSTALL_DOCS'] = 'NO'

        super().configure(state)


class WebpTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('webp')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.6.0.tar.gz',
            'e4ab7009bf0629fd11982d4c2aa83964cf244cffba7347ecd39019a9e38c4564')

    def configure(self, state: BuildState):
        option_suffices = (
            'ANIM_UTILS', 'CWEBP', 'DWEBP', 'EXTRAS', 'GIF2WEBP', 'IMG2WEBP', 'VWEBP', 'WEBPINFO', 'WEBPMUX',
        )

        for suffix in option_suffices:
            state.options[f'WEBP_BUILD_{suffix}'] = 'NO'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        shutil.copytree(state.install_path / 'share/WebP/cmake', state.install_path / 'lib/cmake/WebP')


class XmpTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('xmp')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libxmp/libxmp/releases/download/libxmp-4.7.0/libxmp-4.7.0.tar.gz',
            'b6251de1859352c6988752563d60983cb8aa9fd7dfe9f81b8bc6688da47f3464')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_SHARED'] = 'NO'
        opts['LIBXMP_PIC'] = 'YES'

        super().configure(state)


class ZlibNgTarget(base.CMakeStaticDependencyTarget):
    def __init__(self):
        super().__init__('zlib-ng')

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.3.3.tar.gz',
            'f9c65aa9c852eb8255b636fd9f07ce1c406f061ec19a2e7d508b318ca0c907d1')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('zlib-ng.h')

    def configure(self, state: BuildState):
        opts = state.options
        opts['WITH_GTEST'] = 'NO'
        opts['WITH_SANITIZER'] = 'NO'
        opts['ZLIB_COMPAT'] = 'YES'

        super().configure(state)
