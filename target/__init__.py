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

from .library_tier1 import *
from .library_tier2 import *
from .library_tier3 import *
from .main import *
from .tool import *


def targets():
    return (
        GZDoomTarget(),
        QZDoomTarget(),
        VkDoomTarget(),
        LZDoomTarget(),
        RazeTarget(),
        HandsOfNecromancyTarget(),
        RedemptionTarget(),
        DisdainTarget(),
        AccTarget(),
        WadExtTarget(),
        ZdbspTarget(),
        ZDRayTarget(),
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

        # Libraries needed for GZDoom and Raze
        Bzip2Target(),
        FfiTarget(),
        FlacTarget(),
        GlibTarget(),
        IconvTarget(),
        IntlTarget(),
        LameTarget(),
        MoltenVKTarget(),
        Mpg123Target(),
        OggTarget(),
        OpenALTarget(),
        OpusTarget(),
        PcreTarget(),
        QuasiGlibTarget(),
        SndFileTarget(),
        VorbisTarget(),
        VpxTarget(),
        ZMusicTarget(),

        # Libraries needed for other targets
        DumbTarget(),
        FluidSynthTarget(),
        FmtTarget(),
        GmeTarget(),
        InstPatchTarget(),
        MadTarget(),
        MikmodTarget(),
        ModPlugTarget(),
        OpusFileTarget(),
        PngTarget(),
        PortMidiTarget(),
        SamplerateTarget(),
        Sdl2Target(),
        Sdl2ImageTarget(),
        Sdl2MixerTarget(),
        Sdl2NetTarget(),
        SodiumTarget(),
        VulkanHeadersTarget(),
        VulkanLoaderTarget(),
        WavPackTarget(),
        WebpTarget(),
        XmpTarget(),
        ZlibNgTarget(),

        # Obsolete libraries without binaries
        BrotliTarget(),
        ExpatTarget(),
        FftwTarget(),
        FobosTarget(),
        FreeImageTarget(),
        FreeTypeTarget(),
        FtglTarget(),
        GlewTarget(),
        GlfwTarget(),
        HarfBuzzTarget(),
        HighwayTarget(),
        JpegTurboTarget(),
        LuaTarget(),
        Sdl2TtfTarget(),
        SfmlTarget(),
        TiffTarget(),
        UsbTarget(),
        WxWidgetsTarget(),
        ZstdTarget(),

        # Tools without binaries stored in the repo, can be outdated
        AutoconfTarget(),
        AutomakeTarget(),
        Bzip3Target(),
        DfuUtilTarget(),
        DosBoxXTarget(),
        DzipTarget(),
        EricWToolsTarget(),
        FFmpegTarget(),
        GlslangTarget(),
        HackRFTarget(),
        M4Target(),
        P7ZipTarget(),
        PbzxTarget(),
        QPakManTarget(),
        Radare2Target(),
        RizinTarget(),
        SeverZipTarget(),
        UnrarTarget(),
        XdeltaTarget(),
        XzTarget(),
        ZipTarget(),
    )
