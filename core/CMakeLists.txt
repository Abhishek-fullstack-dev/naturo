cmake_minimum_required(VERSION 3.16)
project(naturo_core VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Shared library
add_library(naturo_core SHARED
    src/version.cpp
)

target_include_directories(naturo_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_definitions(naturo_core PRIVATE NATURO_BUILDING)

# On Windows, put DLL in bin/
set_target_properties(naturo_core PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

# Tests
option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    enable_testing()
    add_executable(test_naturo_core tests/test_version.cpp)
    target_link_libraries(test_naturo_core PRIVATE naturo_core)
    add_test(NAME test_version COMMAND test_naturo_core)
endif()
