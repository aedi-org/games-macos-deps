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
import shutil
import subprocess
from pathlib import Path

import aedi.target.base as base
from aedi.state import BuildState


class DumbTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='dumb'):
        super().__init__(name)

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
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return 'Libs: -L${libdir} -ldumb\n' if line.startswith('Libs:') else line


class FlacTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='flac'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/xiph/flac/releases/download/1.5.0/flac-1.5.0.tar.xz',
            'f2c1c76592a82ffff8413ba3c4a1299b6c7ab06c734dee03fd88630485c2b920')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_CXXLIBS'] = 'NO'
        opts['BUILD_EXAMPLES'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'
        opts['BUILD_TESTING'] = 'NO'

        super().configure(state)


class FluidSynthTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='fluidsynth'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/FluidSynth/fluidsynth/archive/refs/tags/v2.4.6.tar.gz',
            'a6be90fd4842b9e7246500597180af5cf213c11bfa3998a3236dd8ff47961ea8',
            patches='fluidsynth-sf3-support')

    def configure(self, state: BuildState):
        opts = state.options
        opts['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'sndfile')
        opts['DEFAULT_SOUNDFONT'] = 'default.sf2'
        opts['enable-framework'] = 'NO'
        opts['enable-readline'] = 'NO'
        opts['enable-sdl2'] = 'NO'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        self.keep_module_target(state, 'FluidSynth::libfluidsynth')


class FmtTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='fmt'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/fmtlib/fmt/releases/download/11.2.0/fmt-11.2.0.zip',
            '203eb4e8aa0d746c62d8f903df58e0419e3751591bb53ff971096eaa0ebd4ec3')

    def configure(self, state: BuildState):
        opts = state.options
        opts['FMT_DOC'] = 'NO'
        opts['FMT_TEST'] = 'NO'

        super().configure(state)


class FreeTypeTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='freetype'):
        super().__init__(name)

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
    def __init__(self, name='ftgl'):
        super().__init__(name)

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
    def __init__(self, name='glew'):
        super().__init__(name)
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
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        libs = 'Libs:'

        if line.startswith(libs):
            return libs + ' -L${libdir} -lGLEW ' + GlewTarget.LINKER_FLAGS + os.linesep

        return line


class GlibTarget(base.MesonStaticTarget):
    def __init__(self, name='glib'):
        super().__init__(name)

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
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return 'exec_prefix=${prefix}\n' + line if line.startswith('libdir=') else line


class GmeTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='gme'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libgme/game-music-emu/archive/refs/tags/0.6.4.tar.gz',
            'f2360feb5a32ace226c583df4faf6eff74145c81264aaea11e17a1af2f6f101a')

    def configure(self, state: BuildState):
        state.options['GME_BUILD_EXAMPLES'] = 'NO'
        super().configure(state)


class HarfBuzzTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='harfbuzz'):
        super().__init__(name)

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
            elif line.startswith(link_var):
                return link_var + '"-framework ApplicationServices"\n'

            return line

        config_path = state.install_path / 'lib/cmake/harfbuzz/harfbuzzConfig.cmake'
        self.update_text_file(config_path, update_config_cmake)

        self.write_pc_file(state, description='HarfBuzz text shaping library', version='2.8.2', libs='-lharfbuzz',
                           libs_private='-lc++ -framework CoreFoundation -framework CoreGraphics -framework CoreText')


class InstPatchTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='instpatch'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/swami/libinstpatch/archive/v1.1.6.tar.gz',
            '8e9861b04ede275d712242664dab6ffa9166c7940fea3b017638681d25e10299')

    def configure(self, state: BuildState):
        state.options['LIB_SUFFIX'] = None

        # Workaround for missing frameworks in dependencies, no clue what's wrong at the moment
        state.environment['LDFLAGS'] = '-framework CoreFoundation -framework Foundation'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        # Remove extra directory from include path
        include_path = state.install_path / 'include'
        include_subpath = include_path / 'libinstpatch-2/libinstpatch'
        shutil.move(str(include_subpath), include_path)


class LameTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='lame'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceforge.net/projects/lame/files/lame/3.100/lame-3.100.tar.gz',
            'ddfe36cab873794038ae2c1210557ad34857a4b6bdc515785d1da9e175b1da1e')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('lame.spec')


class MadTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='mad'):
        super().__init__(name)

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
    def __init__(self, name='mikmod'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/mikmod/libmikmod/3.3.13/libmikmod-3.3.13.tar.gz',
            '9fc1799f7ea6a95c7c5882de98be85fc7d20ba0a4a6fcacae11c8c6b382bb207')

    def configure(self, state: BuildState):
        opts = state.options
        opts['ENABLE_DOC'] = 'NO'
        opts['ENABLE_SHARED'] = 'NO'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)

        def fix_path(_, line):
            return line.replace(str(state.install_path), '${exec_prefix}') \
                if line.startswith('\t\techo -L') else line

        self.update_config_script(state.install_path / 'bin/libmikmod-config', fix_path)


class ModPlugTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='modplug'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/modplug-xmms/libmodplug/0.8.9.0/libmodplug-0.8.9.0.tar.gz',
            '457ca5a6c179656d66c01505c0d95fafaead4329b9dbaa0f997d00a3508ad9de')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libmodplug.pc.in')

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        libs_private = 'Libs.private:'

        if line.startswith(libs_private):
            return libs_private + ' -lc++\n'

        return line


class MoltenVKTarget(base.MakeTarget):
    def __init__(self, name='moltenvk'):
        super().__init__(name)

        # Building for multiple architectures is handled internally
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/KhronosGroup/MoltenVK/archive/refs/tags/v1.3.0.tar.gz',
            '9476033d49ef02776ebab288fffae3e28fd627a3e29b7ae5975a1e1c785bf912')

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
        shutil.copy(src_path / 'dynamic/dylib/macOS/libMoltenVK.dylib', lib_path)
        shutil.copy(
            src_path / 'static/MoltenVK.xcframework/macos-arm64_x86_64/libMoltenVK.a',
            lib_path / 'libMoltenVK-static.a')


class Mpg123Target(base.CMakeStaticDependencyTarget):
    def __init__(self, name='mpg123'):
        super().__init__(name)
        self.src_root = 'ports/cmake'

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://www.mpg123.de/download/mpg123-1.32.10.tar.bz2',
            '87b2c17fe0c979d3ef38eeceff6362b35b28ac8589fbf1854b5be75c9ab6557c',
            patches=('mpg123-have-fpu', 'mpg123-no-syn123'))

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_LIBOUT123'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'

        super().configure(state)


class OggTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='ogg'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/xiph/ogg/releases/download/v1.3.5/libogg-1.3.5.tar.xz',
            'c4d91be36fc8e54deae7575241e03f4211eb102afb3fc0775fbbc1b740016705')


class OpusTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='opus'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        # Temporary solution for lack of TLSv1.3 support in Apple Python
        # The following URL cannot be retrieved using Python 3.9.6 from Xcode 15.x
        # https://downloads.xiph.org/releases/opus/opus-1.5.1.tar.gz
        # ssl.SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1129)
        # >>> import ssl; print(ssl.OPENSSL_VERSION, ssl.HAS_TLSv1_3)
        # LibreSSL 2.8.3 False
        # TODO: remove this workaround when TLSv1.3 will be available in Python shipped with Xcode
        state.download_source(
            'https://ftp.osuosl.org/pub/xiph/releases/opus/opus-1.5.2.tar.gz',
            '65c1d2f78b9f2fb20082c38cbe47c951ad5839345876e46941612ee87f9a7ce1')

    def configure(self, state: BuildState):
        state.options['PC_BUILD'] = 'floating-point'
        super().configure(state)

    @staticmethod
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        cflags = 'Cflags:'
        libs = 'Libs:'

        if line.startswith(cflags):
            return cflags + ' -I${includedir}/opus\n'
        elif line.startswith(libs):
            return libs + ' -L${libdir} -lopus\n'

        return line


class OpusFileTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='opusfile'):
        super().__init__(name)

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
    def __init__(self, name='pcre'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.pcre.org/pub/pcre/pcre-8.45.tar.bz2',
            '4dae6fdcd2bb0bb6c37b5f97c33c2be954da743985369cddac3546e3218bffb8')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('pcre.h.in')

    def configure(self, state: BuildState):
        opts = state.options
        opts['--enable-unicode-properties'] = 'yes'
        opts['--enable-cpp'] = 'no'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        self.update_config_script(state.install_path / 'bin/pcre-config')


class PngTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='png'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://downloads.sourceforge.net/project/libpng/libpng16/1.6.48/libpng-1.6.48.tar.xz',
            '46fd06ff37db1db64c0dc288d78a3f5efd23ad9ac41561193f983e20937ece03')

    def configure(self, state: BuildState):
        opts = state.options
        opts['PNG_FRAMEWORK'] = 'NO'
        opts['PNG_SHARED'] = 'NO'

        super().configure(state)

    def post_build(self, state: BuildState):
        super().post_build(state)
        self.update_config_script(state.install_path / 'bin/libpng16-config')


class PortMidiTarget(base.CMakeTarget):
    def __init__(self, name='portmidi'):
        super().__init__(name)

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
    def __init__(self, name='samplerate'):
        super().__init__(name)

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
    def __init__(self, name='sdl2'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL/releases/download/release-2.32.6/SDL2-2.32.6.tar.gz',
            '6a7a40d6c2e00016791815e1a9f4042809210bdf10cc78d2c75b45c4f52f93ad')

    def configure(self, state: BuildState):
        opts = state.options
        opts['SDL_STATIC_PIC'] = 'YES'
        opts['SDL_TEST'] = 'NO'

        super().configure(state)


class Sdl2ImageTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='sdl2_image'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL_image/releases/download/release-2.8.8/SDL2_image-2.8.8.tar.gz',
            '2213b56fdaff2220d0e38c8e420cbe1a83c87374190cba8c70af2156097ce30a')

    def configure(self, state: BuildState):
        opts = state.options
        opts['SDL2IMAGE_WEBP'] = 'YES'
        opts['SDL2IMAGE_WEBP_SHARED'] = 'NO'

        super().configure(state)


class Sdl2MixerTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='sdl2_mixer'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.8.1/SDL2_mixer-2.8.1.tar.gz',
            'cb760211b056bfe44f4a1e180cc7cb201137e4d1572f2002cc1be728efd22660')

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
    def __init__(self, name='sdl2_net'):
        super().__init__(name)
        self.version = '2.2.0'

    def prepare_source(self, state: BuildState):
        base_url = 'https://github.com/libsdl-org/SDL_net/releases/download'
        state.download_source(
            f'{base_url}/release-{self.version}/SDL2_net-{self.version}.tar.gz',
            '4e4a891988316271974ff4e9585ed1ef729a123d22c08bd473129179dc857feb')

    def post_build(self, state: BuildState):
        super().post_build(state)

        self.write_pc_file(state, filename='SDL2_net.pc', name='SDL2_net',
                           description='net library for Simple DirectMedia Layer',
                           version=self.version, requires='sdl2 >= 2.0.4',
                           libs='-lSDL2_net', cflags='-I${includedir}/SDL2')


class Sdl2TtfTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='sdl2_ttf'):
        super().__init__(name)

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
    def _process_pkg_config(pcfile: Path, line: str) -> str:
        return line + 'Requires.private: freetype2\n' if line.startswith('Requires:') else line


class SfmlTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='sfml'):
        super().__init__(name)

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
    def __init__(self, name='sndfile'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libsndfile/libsndfile/releases/download/1.2.2/libsndfile-1.2.2.tar.xz',
            '3799ca9924d3125038880367bf1468e53a1b7e3686a934f098b7e1d286cdb80e')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_EXAMPLES'] = 'NO'
        opts['BUILD_PROGRAMS'] = 'NO'
        opts['BUILD_TESTING'] = 'NO'
        opts['ENABLE_CPACK'] = 'NO'

        super().configure(state)


class SodiumTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='sodium'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/jedisct1/libsodium/releases/download/1.0.20-RELEASE/libsodium-1.0.20.tar.gz',
            'ebb65ef6ca439333c2bb41a0c1990587288da07f6c7fd07cb3a18cc18d30ce19')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libsodium.pc.in')


class VorbisTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='vorbis'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://ftp.osuosl.org/pub/xiph/releases/vorbis/libvorbis-1.3.7.tar.xz',
            'b33cc4934322bcbf6efcbacf49e3ca01aadbea4114ec9589d1b1e9d20f72954b')


class VulkanHeadersTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='vulkan-headers'):
        super().__init__(name)
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            # Version should match with the current MoltenVK release
            'https://github.com/KhronosGroup/Vulkan-Headers/archive/refs/tags/v1.4.313.tar.gz',
            'f3298b8dc620530493296759858a69b622f98ececa0e8c75488ad2000778148f')


class VulkanLoaderTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='vulkan-loader'):
        super().__init__(name)
        self.version = '1.4.313'

    def prepare_source(self, state: BuildState):
        state.download_source(
            # Version should match with the current MoltenVK release
            f'https://github.com/KhronosGroup/Vulkan-Loader/archive/refs/tags/v{self.version}.tar.gz',
            '0c2436993597f5bd0ee420b6b27632758ed3ab439043d251795fd13d4e70a2f3')

    def configure(self, state: BuildState):
        opts = state.options
        opts['APPLE_STATIC_LOADER'] = 'YES'
        opts['CMAKE_INSTALL_SYSCONFDIR'] = '/usr/local/etc'

        super().configure(state)

    def post_build(self, state: BuildState):
        lib_path = state.install_path / 'lib'
        os.makedirs(lib_path, exist_ok=True)
        shutil.copy(state.build_path / 'loader/libvulkan.a', lib_path)

        self.write_pc_file(state, filename='vulkan.pc',
                           name='Vulkan-Loader', description='Vulkan Loader', version=self.version,
                           libs='-lvulkan', libs_private='-lc++ -framework CoreFoundation')


class WavPackTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='wavpack'):
        super().__init__(name)

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
    def __init__(self, name='webp'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.5.0.tar.gz',
            '7d6fab70cf844bf6769077bd5d7a74893f8ffd4dfb42861745750c63c2a5c92c')

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
    def __init__(self, name='xmp'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libxmp/libxmp/releases/download/libxmp-4.6.3/libxmp-4.6.3.tar.gz',
            'b189a2ff3f3eef0008512e0fb27c2cdc27480bc1066b82590a84d02548fab96d')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_SHARED'] = 'NO'
        opts['LIBXMP_PIC'] = 'YES'

        super().configure(state)


class ZlibNgTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='zlib-ng'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.2.4.tar.gz',
            'a73343c3093e5cdc50d9377997c3815b878fd110bf6511c2c7759f2afb90f5a3')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('zlib-ng.h')

    def configure(self, state: BuildState):
        opts = state.options
        opts['WITH_GTEST'] = 'NO'
        opts['WITH_SANITIZER'] = 'NO'
        opts['ZLIB_COMPAT'] = 'YES'
        opts['ZLIB_ENABLE_TESTS'] = 'NO'
        opts['ZLIBNG_ENABLE_TESTS'] = 'NO'

        super().configure(state)
