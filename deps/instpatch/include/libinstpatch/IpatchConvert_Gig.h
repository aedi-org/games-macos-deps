/*
 * libInstPatch
 * Copyright (C) 1999-2014 Element Green <element@elementsofsound.org>
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
#ifndef __IPATCH_CONVERT_GIG_H__
#define __IPATCH_CONVERT_GIG_H__

#include <glib.h>
#include <glib-object.h>
#include <libinstpatch/IpatchConverter.h>

typedef IpatchConverter IpatchConverterGigToFile;
typedef IpatchConverterClass IpatchConverterGigToFileClass;

typedef IpatchConverter IpatchConverterFileToGig;
typedef IpatchConverterClass IpatchConverterFileToGigClass;

typedef IpatchConverter IpatchConverterFileToGigSample;
typedef IpatchConverterClass IpatchConverterFileToGigSampleClass;

#define IPATCH_TYPE_CONVERTER_GIG_TO_FILE \
  (ipatch_converter_gig_to_file_get_type ())

#define IPATCH_TYPE_CONVERTER_FILE_TO_GIG \
  (ipatch_converter_file_to_gig_get_type ())

#define IPATCH_TYPE_CONVERTER_FILE_TO_GIG_SAMPLE \
  (ipatch_converter_file_to_gig_sample_get_type ())

GType ipatch_converter_gig_to_file_get_type(void);
GType ipatch_converter_file_to_gig_get_type(void);
GType ipatch_converter_file_to_gig_sample_get_type(void);

#endif
