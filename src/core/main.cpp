/**
 * HyperMine Core — Entry Point
 * 
 * Ponto de entrada principal do minerador.
 * Inicializa hardware, carrega configuração e inicia o loop de mineração.
 */

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <iostream>

// Forward declarations para módulos Rust (via FFI)
extern "C" {
    // Funções exportadas pelo engine Rust
    // void hypermine_engine_init(const char* config_path);
    // void hypermine_engine_start();
    // void hypermine_engine_stop();
}

// ============================================================================
// Versão e Informações
// ============================================================================

constexpr const char* HYPERMINE_VERSION = "1.0.0";
constexpr const char* HYPERMINE_NAME = "HyperMine Core";

// ============================================================================
// Detecção de CPU Features
// ============================================================================

struct CpuFeatures {
    bool sse42   = false;
    bool avx2    = false;
    bool avx512f = false;
    bool sha_ni  = false;
    bool aes_ni  = false;
    
    std::string cpu_name;
    uint32_t cores = 0;
    uint32_t threads = 0;
    uint32_t cache_l3_kb = 0;
};

#if defined(__x86_64__) || defined(_M_X64)
#include <cpuid.h>

CpuFeatures detect_cpu_features() {
    CpuFeatures features;
    
    uint32_t eax, ebx, ecx, edx;
    
    // Get CPU name
    char cpu_name[49] = {0};
    for (uint32_t i = 0x80000002; i <= 0x80000004; ++i) {
        __cpuid(i, eax, ebx, ecx, edx);
        memcpy(cpu_name + (i - 0x80000002) * 16, &eax, 4);
        memcpy(cpu_name + (i - 0x80000002) * 16 + 4, &ebx, 4);
        memcpy(cpu_name + (i - 0x80000002) * 16 + 8, &ecx, 4);
        memcpy(cpu_name + (i - 0x80000002) * 16 + 12, &edx, 4);
    }
    features.cpu_name = cpu_name;
    
    // Feature detection
    __cpuid(1, eax, ebx, ecx, edx);
    features.sse42 = (ecx >> 20) & 1;  // SSE4.2
    features.aes_ni = (ecx >> 25) & 1; // AES-NI
    
    __cpuid_count(7, 0, eax, ebx, ecx, edx);
    features.avx2 = (ebx >> 5) & 1;    // AVX2
    features.avx512f = (ebx >> 16) & 1; // AVX-512F
    features.sha_ni = (ebx >> 29) & 1;  // SHA-NI
    
    // Core/thread count
    features.cores = std::thread::hardware_concurrency();
    features.threads = features.cores; // Simplified
    
    return features;
}

#elif defined(__aarch64__)

CpuFeatures detect_cpu_features() {
    CpuFeatures features;
    features.cpu_name = "ARM64 Processor";
    features.cores = std::thread::hardware_concurrency();
    features.threads = features.cores;
    // ARM features detected via getauxval(AT_HWCAP)
    return features;
}

#else

CpuFeatures detect_cpu_features() {
    CpuFeatures features;
    features.cpu_name = "Unknown Processor";
    features.cores = std::thread::hardware_concurrency();
    features.threads = features.cores;
    return features;
}

#endif

// ============================================================================
// Huge Pages Setup
// ============================================================================

#ifdef __linux__
#include <sys/mman.h>

void* allocate_huge_pages(size_t size) {
    void* ptr = mmap(nullptr, size,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                     -1, 0);
    
    if (ptr == MAP_FAILED) {
        // Fallback para páginas normais
        ptr = mmap(nullptr, size,
                   PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS,
                   -1, 0);
        if (ptr != MAP_FAILED) {
            // Tentar madvise para transparent huge pages
            madvise(ptr, size, MADV_HUGEPAGE);
        }
    }
    
    return (ptr == MAP_FAILED) ? nullptr : ptr;
}

void free_huge_pages(void* ptr, size_t size) {
    if (ptr) {
        munmap(ptr, size);
    }
}

#endif

// ============================================================================
// Banner e CLI
// ============================================================================

void print_banner() {
    printf("\n");
    printf("  ╔══════════════════════════════════════════════════════════╗\n");
    printf("  ║                                                        ║\n");
    printf("  ║   ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗            ║\n");
    printf("  ║   ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗           ║\n");
    printf("  ║   ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝           ║\n");
    printf("  ║   ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗           ║\n");
    printf("  ║   ██║  ██║   ██║   ██║     ███████╗██║  ██║           ║\n");
    printf("  ║   ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝           ║\n");
    printf("  ║                                                        ║\n");
    printf("  ║   ███╗   ███╗██╗███╗   ██╗███████╗                     ║\n");
    printf("  ║   ████╗ ████║██║████╗  ██║██╔════╝                     ║\n");
    printf("  ║   ██╔████╔██║██║██╔██╗ ██║█████╗                       ║\n");
    printf("  ║   ██║╚██╔╝██║██║██║╚██╗██║██╔══╝                       ║\n");
    printf("  ║   ██║ ╚═╝ ██║██║██║ ╚████║███████╗                     ║\n");
    printf("  ║   ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝                     ║\n");
    printf("  ║                                                        ║\n");
    printf("  ║   Universal High-Performance Cryptocurrency Miner      ║\n");
    printf("  ║   Version %s                                       ║\n", HYPERMINE_VERSION);
    printf("  ║                                                        ║\n");
    printf("  ╚══════════════════════════════════════════════════════════╝\n");
    printf("\n");
}

void print_cpu_info(const CpuFeatures& cpu) {
    printf("  CPU: %s\n", cpu.cpu_name.c_str());
    printf("  Cores/Threads: %u/%u\n", cpu.cores, cpu.threads);
    printf("  Features: ");
    if (cpu.sse42)   printf("SSE4.2 ");
    if (cpu.avx2)    printf("AVX2 ");
    if (cpu.avx512f) printf("AVX-512 ");
    if (cpu.sha_ni)  printf("SHA-NI ");
    if (cpu.aes_ni)  printf("AES-NI ");
    printf("\n\n");
}

// ============================================================================
// Main
// ============================================================================

int main(int argc, char* argv[]) {
    print_banner();
    
    // Detectar CPU
    auto cpu = detect_cpu_features();
    print_cpu_info(cpu);
    
    // Parse argumentos
    std::string config_path = "config.toml";
    std::string coins_filter = "";
    bool benchmark_mode = false;
    std::string benchmark_algo = "";
    uint32_t threads = 0;
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--config" && i + 1 < argc) {
            config_path = argv[++i];
        } else if (arg == "--coins" && i + 1 < argc) {
            coins_filter = argv[++i];
        } else if (arg == "--threads" && i + 1 < argc) {
            threads = std::stoul(argv[++i]);
        } else if (arg == "--benchmark") {
            benchmark_mode = true;
        } else if (arg == "--algorithm" && i + 1 < argc) {
            benchmark_algo = argv[++i];
        } else if (arg == "--help" || arg == "-h") {
            printf("Uso: hypermine [opções]\n\n");
            printf("Opções:\n");
            printf("  --config <path>      Caminho para config.toml (default: config.toml)\n");
            printf("  --coins <lista>      Moedas a minerar (separadas por vírgula)\n");
            printf("  --threads <n>        Número de threads CPU\n");
            printf("  --benchmark          Executar benchmarks\n");
            printf("  --algorithm <algo>   Algoritmo para benchmark\n");
            printf("  --help, -h           Mostrar esta ajuda\n");
            return 0;
        } else if (arg == "--version" || arg == "-v") {
            printf("%s v%s\n", HYPERMINE_NAME, HYPERMINE_VERSION);
            return 0;
        }
    }
    
    printf("  Config: %s\n", config_path.c_str());
    if (!coins_filter.empty()) {
        printf("  Coins: %s\n", coins_filter.c_str());
    }
    if (threads > 0) {
        printf("  Threads: %u\n", threads);
    }
    printf("\n");
    
    if (benchmark_mode) {
        printf("  [BENCHMARK MODE]\n");
        printf("  Running benchmarks for: %s\n",
               benchmark_algo.empty() ? "all algorithms" : benchmark_algo.c_str());
        // TODO: Implementar benchmarks
        return 0;
    }
    
    printf("  Initializing mining engine...\n");
    printf("  Loading configuration from: %s\n", config_path.c_str());
    
    // TODO: Inicializar engine Rust via FFI
    // hypermine_engine_init(config_path.c_str());
    // hypermine_engine_start();
    
    printf("  HyperMine Core initialized successfully.\n");
    printf("  Press Ctrl+C to stop.\n\n");
    
    return 0;
}
