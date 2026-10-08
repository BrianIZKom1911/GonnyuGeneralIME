cmake_minimum_required(VERSION 3.22)
project(gannyu_rime_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_path(RIME_INCLUDE_DIR rime_api.h REQUIRED)
find_library(RIME_LIBRARY NAMES rime REQUIRED)
set(RIME_DEPENDENCY_LIBRARIES "" CACHE STRING "Static libraries required by librime")

add_library(gannyu_rime_engine STATIC gannyu_rime_engine.cpp)
target_include_directories(gannyu_rime_engine PUBLIC
  "${CMAKE_CURRENT_LIST_DIR}/../../crates/ffi/include"
  "${RIME_INCLUDE_DIR}")
target_link_libraries(gannyu_rime_engine PUBLIC
  "${RIME_LIBRARY}"
  ${RIME_DEPENDENCY_LIBRARIES})
if(MSVC)
  target_compile_options(gannyu_rime_engine PRIVATE /W4)
else()
  target_compile_options(gannyu_rime_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()

option(GANNYU_RIME_BUILD_PROBES "Build host-only Rime adapter probes" ON)

if(GANNYU_RIME_BUILD_PROBES)
  find_package(Threads REQUIRED)
  enable_testing()
  add_executable(gannyu_rime_snapshot_probe rime_snapshot_probe.cpp)
  target_include_directories(gannyu_rime_snapshot_probe PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../../crates/ffi/include"
    "${RIME_INCLUDE_DIR}")
  target_link_libraries(gannyu_rime_snapshot_probe PRIVATE Threads::Threads)
  add_test(NAME rime_snapshot_equivalence COMMAND gannyu_rime_snapshot_probe)

  add_executable(gannyu_rime_resource_cleanup_probe rime_resource_cleanup_probe.cpp)
  target_include_directories(gannyu_rime_resource_cleanup_probe PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../../crates/ffi/include"
    "${RIME_INCLUDE_DIR}")
  add_test(NAME rime_resource_cleanup COMMAND gannyu_rime_resource_cleanup_probe)

  add_executable(gannyu_rime_engine_probe rime_engine_probe.cpp)
  target_link_libraries(gannyu_rime_engine_probe PRIVATE gannyu_rime_engine)

  add_executable(gannyu_rime_engine_concurrency_probe rime_engine_concurrency_probe.cpp)
  target_link_libraries(gannyu_rime_engine_concurrency_probe PRIVATE gannyu_rime_engine)

  if(APPLE)
    add_executable(gannyu_rime_engine_memory_probe rime_engine_memory_probe.cpp)
    target_link_libraries(gannyu_rime_engine_memory_probe PRIVATE gannyu_rime_engine)
    if(RIME_LIBRARY MATCHES "\\.a$")
      foreach(probe IN ITEMS gannyu_rime_engine_probe gannyu_rime_engine_concurrency_probe gannyu_rime_engine_memory_probe)
        target_link_options(${probe} PRIVATE "LINKER:-force_load,${RIME_LIBRARY}")
      endforeach()
    endif()
  endif()
endif()
