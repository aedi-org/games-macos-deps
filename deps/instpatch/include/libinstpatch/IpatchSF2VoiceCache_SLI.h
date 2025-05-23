/*
 * libInstPatch
 * Copyright (C) 1999-2014 Element Green <element@elementsofsound.org>
 *
 * Author of this file: (C) 2012 BALATON Zoltan <balaton@eik.bme.hu>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; version 2.1
 * of the License only.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, see <https://www.gnu.org/licenses/>.
 */
#ifndef __IPATCH_SF2_VOICE_CACHE_SLI_H__
#define __IPATCH_SF2_VOICE_CACHE_SLI_H__

#include <glib.h>
#include <glib-object.h>
#include <libinstpatch/IpatchConverter.h>
#include <libinstpatch/IpatchConverterSF2VoiceCache.h>

typedef IpatchConverterSF2VoiceCache IpatchConverterSLIInstToSF2VoiceCache;
typedef IpatchConverterSF2VoiceCacheClass IpatchConverterSLIInstToSF2VoiceCacheClass;
typedef IpatchConverterSF2VoiceCache IpatchConverterSLIZoneToSF2VoiceCache;
typedef IpatchConverterSF2VoiceCacheClass IpatchConverterSLIZoneToSF2VoiceCacheClass;
typedef IpatchConverterSF2VoiceCache IpatchConverterSLISampleToSF2VoiceCache;
typedef IpatchConverterSF2VoiceCacheClass IpatchConverterSLISampleToSF2VoiceCacheClass;

#define IPATCH_TYPE_CONVERTER_SLI_INST_TO_SF2_VOICE_CACHE \
  (ipatch_converter_sli_inst_to_sf2_voice_cache_get_type ())
#define IPATCH_TYPE_CONVERTER_SLI_ZONE_TO_SF2_VOICE_CACHE \
  (ipatch_converter_sli_zone_to_sf2_voice_cache_get_type ())
#define IPATCH_TYPE_CONVERTER_SLI_SAMPLE_TO_SF2_VOICE_CACHE \
  (ipatch_converter_sli_sample_to_sf2_voice_cache_get_type ())

GType ipatch_converter_sli_inst_to_sf2_voice_cache_get_type(void);
GType ipatch_converter_sli_zone_to_sf2_voice_cache_get_type(void);
GType ipatch_converter_sli_sample_to_sf2_voice_cache_get_type(void);

#endif
