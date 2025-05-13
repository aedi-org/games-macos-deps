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

import shutil
from platform import machine

from aedi.state import BuildState
from aedi.target.base import CMakeMainTarget, MakeMainTarget


class PrBoomPlusTarget(CMakeMainTarget):
    def __init__(self, name='prboom-plus'):
        super().__init__(name)
        self.src_root = 'prboom2'
        self.outputs = ('Launcher.app',)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/coelckers/prboom-plus.git')

    def configure(self, state: BuildState):
        opts = state.options
        opts['CMAKE_C_FLAGS'] = '-D_FILE_OFFSET_BITS=64'
        opts['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'SDL2_mixer', 'SDL2_image')
        opts['CMAKE_POLICY_DEFAULT_CMP0056'] = 'NEW'

        if state.architecture() != machine():
            opts['FORCE_CROSSCOMPILE'] = 'YES'
            opts['IMPORT_EXECUTABLES'] = state.native_build_path / 'ImportExecutables.cmake'

        super().configure(state)


class DsdaDoom(PrBoomPlusTarget):
    def __init__(self, name='dsda-doom'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/kraflab/dsda-doom.git')


class ChocolateDoomBaseTarget(CMakeMainTarget):
    def __init__(self, name=None):
        super().__init__(name)

    def configure(self, state: BuildState):
        state.options['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'SDL2_mixer')
        super().configure(state)

    def _fill_outputs(self, exe_prefix: str):
        self.outputs = (
            f'src/{exe_prefix}-doom',
            f'src/{exe_prefix}-heretic',
            f'src/{exe_prefix}-hexen',
            f'src/{exe_prefix}-server',
            f'src/{exe_prefix}-setup',
            f'src/{exe_prefix}-strife',
            'src/midiread',
            'src/mus2mid',
        )


class ChocolateDoomTarget(ChocolateDoomBaseTarget):
    def __init__(self, name='chocolate-doom'):
        super().__init__(name)
        self._fill_outputs('chocolate')

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/chocolate-doom/chocolate-doom.git')


class CrispyDoomTarget(ChocolateDoomBaseTarget):
    def __init__(self, name='crispy-doom'):
        super().__init__(name)
        self._fill_outputs('crispy')

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/fabiangreffrath/crispy-doom.git')


class RudeTarget(ChocolateDoomBaseTarget):
    def __init__(self, name='rude'):
        super().__init__(name)
        self._fill_outputs('rude')

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/drfrag666/RUDE.git')

    def post_build(self, state: BuildState):
        super().post_build(state)
        shutil.copy(state.source + '/data/rude.wad', state.install_path)


class WoofTarget(ChocolateDoomBaseTarget):
    def __init__(self, name='woof'):
        super().__init__(name)
        self.outputs = ('Source/woof',)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/fabiangreffrath/woof.git')


class DoomRetroTarget(CMakeMainTarget):
    def __init__(self, name='doomretro'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/bradharding/doomretro.git')


class Doom64EXTarget(CMakeMainTarget):
    def __init__(self, name='doom64ex'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/svkaiser/Doom64EX.git')

    def configure(self, state: BuildState):
        opts = state.options
        opts['ENABLE_SYSTEM_FLUIDSYNTH'] = 'YES'
        opts['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'SDL2', 'fluidsynth')

        super().configure(state)


class DevilutionXTarget(CMakeMainTarget):
    def __init__(self, name='devilutionx'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/diasurgical/devilutionX.git')

    def configure(self, state: BuildState):
        state.options['BUILD_TESTING'] = 'NO'
        super().configure(state)


class EDuke32Target(MakeMainTarget):
    def __init__(self, name='eduke32'):
        super().__init__(name)

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://voidpoint.io/terminx/eduke32.git')

    def detect(self, state: BuildState) -> bool:
        def has_bundle(name: str) -> bool:
            probe_path = state.source / f'platform/Apple/bundles/{name}.app'
            return probe_path.exists()

        return has_bundle('EDuke32') and not has_bundle('NBlood')


class NBloodTarget(EDuke32Target):
    def __init__(self, name='nblood'):
        super().__init__(name)
        self.tool = 'gmake'

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/nukeykt/NBlood.git')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('nblood.pk3')

    def configure(self, state: BuildState):
        super().configure(state)

        for target in ('duke3d', 'sw', 'blood', 'rr', 'exhumed', 'tools'):
            state.options[target] = None


class QuakespasmTarget(MakeMainTarget):
    def __init__(self, name='quakespasm'):
        super().__init__(name)
        self.src_root = 'Quake'

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://git.code.sf.net/p/quakespasm/quakespasm')

    def detect(self, state: BuildState) -> bool:
        return state.has_source_file('Quakespasm.txt') and not QuakespasmExpTarget().detect(state)

    def configure(self, state: BuildState):
        super().configure(state)

        # TODO: Use macOS specific Makefile which requires manual application bundle creation
        opts = state.options
        opts['USE_SDL2'] = '1'
        opts['USE_CODEC_FLAC'] = '1'
        opts['USE_CODEC_OPUS'] = '1'
        opts['USE_CODEC_MIKMOD'] = '1'
        opts['USE_CODEC_UMX'] = '1'
        # Add main() alias to workaround executable linking without macOS launcher
        opts['COMMON_LIBS'] = '-framework OpenGL -Wl,-alias -Wl,_SDL_main -Wl,_main'


class QuakespasmExpTarget(CMakeMainTarget):
    def __init__(self, name='quakespasm-exp'):
        super().__init__(name)
        self.outputs = (self.name, 'quakespasm-exp.pak')

    def prepare_source(self, state: BuildState):
        state.checkout_git('https://github.com/alexey-lysiuk/quakespasm-exp.git')

    def configure(self, state: BuildState):
        opts = state.options
        opts['CMAKE_EXE_LINKER_FLAGS'] += state.run_pkg_config('--libs', 'ogg', 'SDL2')
        opts['QUAKE_GENERATE_VERSION_HEADER'] = 'ON'
        opts['QUAKE_MACOS_BUNDLE'] = 'OFF'
        opts['QUAKE_MACOS_MOUSE_ACCELERATION'] = 'ON'

        if state.xcode:
            opts['QUAKE_BUILD_ENGINE_PAK'] = 'OFF'
        else:
            opts['QUAKE_LTO'] = 'ON'

            if state.architecture() != machine():
                opts['MakeQuakePak_DIR'] = state.native_build_path
                opts['EntFixesGenerator_DIR'] = state.native_build_path

        super().configure(state)
