cmake_minimum_required(VERSION 3.15)

project(OptionAlphaCPP LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SRC_FILES
    src/behavioral_psychology_engine.cpp
    src/cashflow_capital_ecosystem_engine.cpp
    src/tactical_swing_trading_engine.cpp
    src/tactical_options_discipline_engine.cpp
)

add_library(optionalpha_cpp STATIC ${SRC_FILES})

# Ensure 64-byte alignment for AtomicStateVector on all targets
if (MSVC)
    target_compile_options(optionalpha_cpp PRIVATE /arch:AVX)
else()
    target_compile_options(optionalpha_cpp PRIVATE -march=native)
endif()
