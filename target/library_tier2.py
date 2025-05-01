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


class FluidSynthTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='fluidsynth'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/FluidSynth/fluidsynth/archive/refs/tags/v2.4.5.tar.gz',
            '2d2a5ca35bbb3f3fd241ef388a0cb3ae5755ebbb78121c7869f02b021d694810',
            patches='fluidsynth-sf3-support')

    def configure(self, state: BuildState):
        opts = state.options
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
            'https://github.com/fmtlib/fmt/archive/refs/tags/8.1.1.tar.gz',
            '3d794d3cf67633b34b2771eb9f073bde87e846e0d395d254df7b211ef1ec7346')

    def configure(self, state: BuildState):
        opts = state.options
        opts['FMT_DOC'] = 'NO'
        opts['FMT_TEST'] = 'NO'

        super().configure(state)


class GmeTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='gme'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://github.com/libgme/game-music-emu/archive/refs/tags/0.6.3.tar.gz',
            '4c5a7614acaea44e5cb1423817d2889deb82674ddbc4e3e1291614304b86fca0',
            patches='gme-no-ubsan')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('gme.txt')


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
            'https://downloads.sourceforge.net/project/mikmod/libmikmod/3.3.12/libmikmod-3.3.12.tar.gz',
            'adef6214863516a4a5b44ebf2c71ef84ecdfeb3444973dacbac70911c9bc67e9')

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


class PngTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='png'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://sourceforge.net/projects/libpng/files/libpng16/1.6.45/libpng-1.6.45.tar.xz',
            '926485350139ffb51ef69760db35f78846c805fef3d59bfdcb2fba704663f370')

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
            'https://github.com/libsdl-org/SDL/releases/download/release-2.32.4/SDL2-2.32.4.tar.gz',
            'f15b478253e1ff6dac62257ded225ff4e7d0c5230204ac3450f1144ee806f934')

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


class SodiumTarget(base.ConfigureMakeStaticDependencyTarget):
    def __init__(self, name='sodium'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.download_source(
            'https://download.libsodium.org/libsodium/releases/libsodium-1.0.18.tar.gz',
            '6f504490b342a4f8a4c4a02fc9b866cbef8622d5df4e5452b46be121e46636c1')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('libsodium.pc.in')


class VulkanHeadersTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='vulkan-headers'):
        super().__init__(name)
        self.multi_platform = False

    def prepare_source(self, state: BuildState):
        state.download_source(
            # Version should match with the current MoltenVK release
            'https://github.com/KhronosGroup/Vulkan-Headers/archive/refs/tags/v1.3.296.tar.gz',
            'e204e0b3c19f622d197df945737f5db913d6621830999b8578d34e80a7c90585')


class VulkanLoaderTarget(base.CMakeStaticDependencyTarget):
    def __init__(self, name='vulkan-loader'):
        super().__init__(name)
        self.version = '1.3.296'

    def prepare_source(self, state: BuildState):
        state.download_source(
            # Version should match with the current MoltenVK release
            f'https://github.com/KhronosGroup/Vulkan-Loader/archive/refs/tags/v{self.version}.tar.gz',
            '682d5323cf31308402c888599b375ebf15810f95d6d1a08ad2f525766becf99b')

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
            'https://github.com/dbry/WavPack/releases/download/5.6.0/wavpack-5.6.0.tar.xz',
            'af8035f457509c3d338b895875228a9b81de276c88c79bb2d3e31d9b605da9a9')

    def configure(self, state: BuildState):
        opts = state.options
        opts['BUILD_TESTING'] = 'NO'
        opts['WAVPACK_BUILD_DOCS'] = 'NO'
        opts['WAVPACK_BUILD_PROGRAMS'] = 'NO'
        opts['WAVPACK_ENABLE_LIBCRYPTO'] = 'NO'
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
            'https://github.com/libxmp/libxmp/releases/download/libxmp-4.6.2/libxmp-4.6.2.tar.gz',
            'acac1705be2c4fb4d2d70dc05759853ba6aab747a83de576b082784d46f5a4b9')

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
