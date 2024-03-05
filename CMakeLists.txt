cmake_minimum_required(VERSION 3.27)
project(runtime)

set(CMAKE_CXX_STANDARD 17)

set(CUSTOM_LIBRARY_DIR "D:/library/install")

list(APPEND CMAKE_PREFIX_PATH ${CUSTOM_LIBRARY_DIR}/fmt)
list(APPEND CMAKE_PREFIX_PATH ${CUSTOM_LIBRARY_DIR}/spdlog)

find_package(spdlog CONFIG REQUIRED)

file(GLOB_RECURSE RUNTIME_SRC "src/runtime/*.h" "src/runtime/*.hpp" "src/runtime/*.cpp")
file(GLOB_RECURSE TEST_SRC "src/test/*.h" "src/test/*.hpp" "src/test/*.cpp")

include_directories(generated)

file(GLOB_RECURSE GENERATED_SRC "generated/*.h" "generated/*.cpp")

add_executable(${PROJECT_NAME} main.cpp ${RUNTIME_SRC} ${TEST_SRC} ${GENERATED_SRC})
target_link_libraries(${PROJECT_NAME} PRIVATE spdlog::spdlog)
