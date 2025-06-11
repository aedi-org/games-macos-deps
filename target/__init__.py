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

from .library import *
from .main import *
from .tool import *


def targets():
    return (
        PrBoomPlusTarget(),
        DsdaDoom(),
        ChocolateDoomTarget(),
        CrispyDoomTarget(),
        RudeTarget(),
        WoofTarget(),
        DoomRetroTarget(),
        Doom64EXTarget(),
        DevilutionXTarget(),
        EDuke32Target(),
        NBloodTarget(),
        QuakespasmTarget(),
        QuakespasmExpTarget(),
        Q2ProTarget(),

        # Libraries
        Bzip2Target(),
        DumbTarget(),
        FlacTarget(),
        FluidSynthTarget(),
        FmtTarget(),
        FreeTypeTarget(),
        FtglTarget(),
        GlewTarget(),
        GlibTarget(),
        GmeTarget(),
        HarfBuzzTarget(),
        InstPatchTarget(),
        LameTarget(),
        MadTarget(),
        MikmodTarget(),
        ModPlugTarget(),
        MoltenVKTarget(),
        Mpg123Target(),
        OggTarget(),
        OpusFileTarget(),
        OpusTarget(),
        PcreTarget(),
        PngTarget(),
        PortMidiTarget(),
        SamplerateTarget(),
        Sdl2ImageTarget(),
        Sdl2MixerTarget(),
        Sdl2NetTarget(),
        Sdl2Target(),
        Sdl2TtfTarget(),
        SfmlTarget(),
        SndFileTarget(),
        SodiumTarget(),
        VorbisTarget(),
        VulkanHeadersTarget(),
        VulkanLoaderTarget(),
        WavPackTarget(),
        WebpTarget(),
        XmpTarget(),
        ZlibNgTarget(),

        # Tools
        DosBoxXTarget(),
        DzipTarget(),
        EricWToolsTarget(),
        GlslangTarget(),
        QPakManTarget(),
    )
