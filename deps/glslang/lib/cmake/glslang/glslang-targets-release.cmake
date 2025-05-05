#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "glslang::SPVRemapper" for configuration "Release"
set_property(TARGET glslang::SPVRemapper APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::SPVRemapper PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libSPVRemapper.15.3.0.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libSPVRemapper.15.dylib"
  )

list(APPEND _cmake_import_check_targets glslang::SPVRemapper )
list(APPEND _cmake_import_check_files_for_glslang::SPVRemapper "${_IMPORT_PREFIX}/lib/libSPVRemapper.15.3.0.dylib" )

# Import target "glslang::SPIRV" for configuration "Release"
set_property(TARGET glslang::SPIRV APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::SPIRV PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libSPIRV.15.3.0.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libSPIRV.15.dylib"
  )

list(APPEND _cmake_import_check_targets glslang::SPIRV )
list(APPEND _cmake_import_check_files_for_glslang::SPIRV "${_IMPORT_PREFIX}/lib/libSPIRV.15.3.0.dylib" )

# Import target "glslang::glslang" for configuration "Release"
set_property(TARGET glslang::glslang APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::glslang PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libglslang.15.3.0.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libglslang.15.dylib"
  )

list(APPEND _cmake_import_check_targets glslang::glslang )
list(APPEND _cmake_import_check_files_for_glslang::glslang "${_IMPORT_PREFIX}/lib/libglslang.15.3.0.dylib" )

# Import target "glslang::glslang-default-resource-limits" for configuration "Release"
set_property(TARGET glslang::glslang-default-resource-limits APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::glslang-default-resource-limits PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libglslang-default-resource-limits.15.3.0.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libglslang-default-resource-limits.15.dylib"
  )

list(APPEND _cmake_import_check_targets glslang::glslang-default-resource-limits )
list(APPEND _cmake_import_check_files_for_glslang::glslang-default-resource-limits "${_IMPORT_PREFIX}/lib/libglslang-default-resource-limits.15.3.0.dylib" )

# Import target "glslang::glslang-standalone" for configuration "Release"
set_property(TARGET glslang::glslang-standalone APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::glslang-standalone PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/glslang"
  )

list(APPEND _cmake_import_check_targets glslang::glslang-standalone )
list(APPEND _cmake_import_check_files_for_glslang::glslang-standalone "${_IMPORT_PREFIX}/bin/glslang" )

# Import target "glslang::spirv-remap" for configuration "Release"
set_property(TARGET glslang::spirv-remap APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(glslang::spirv-remap PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/spirv-remap"
  )

list(APPEND _cmake_import_check_targets glslang::spirv-remap )
list(APPEND _cmake_import_check_files_for_glslang::spirv-remap "${_IMPORT_PREFIX}/bin/spirv-remap" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
