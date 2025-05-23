#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SPIRV-Tools" for configuration "Release"
set_property(TARGET SPIRV-Tools APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SPIRV-Tools PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libSPIRV-Tools.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libSPIRV-Tools.dylib"
  )

list(APPEND _cmake_import_check_targets SPIRV-Tools )
list(APPEND _cmake_import_check_files_for_SPIRV-Tools "${_IMPORT_PREFIX}/lib/libSPIRV-Tools.dylib" )

# Import target "SPIRV-Tools-shared" for configuration "Release"
set_property(TARGET SPIRV-Tools-shared APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SPIRV-Tools-shared PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libSPIRV-Tools-shared.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libSPIRV-Tools-shared.dylib"
  )

list(APPEND _cmake_import_check_targets SPIRV-Tools-shared )
list(APPEND _cmake_import_check_files_for_SPIRV-Tools-shared "${_IMPORT_PREFIX}/lib/libSPIRV-Tools-shared.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
