#pragma once

#include <cstddef>
#include <cstdint>

/**
 * 64-byte Zero-Bridge Atomic Memory State Vector shared across all language modules.
 * Must be exactly 64 bytes and aligned to 64-byte boundaries to satisfy the
 * Zero-Bridge Synchronous Memory Rule (shared physical memory between C++ and
 * embedded Python AI runtime).
 */
struct alignas(64) AtomicStateVector {
    // Example fields – total size must be 64 bytes.
    uint64_t timestamp;          // 8 bytes
    double   price;              // 8 bytes
    double   volatility;         // 8 bytes
    double   greeks[5];          // 5 * 8 = 40 bytes
    // Padding to reach 64 bytes if needed (already 64).
};

static_assert(sizeof(AtomicStateVector) == 64, "AtomicStateVector must be exactly 64 bytes");
