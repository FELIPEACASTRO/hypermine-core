/**
 * SHA-256 — Implementação Genérica (C++ puro)
 * 
 * Esta é a implementação de referência do SHA-256, sem otimizações
 * específicas de hardware. Serve como baseline para comparação
 * e como fallback quando nenhuma extensão SIMD está disponível.
 * 
 * Performance esperada: ~50 MH/s por core (baseline)
 * 
 * Referência: FIPS 180-4 (Secure Hash Standard)
 * https://csrc.nist.gov/publications/detail/fips/180/4/final
 */

#include <cstdint>
#include <cstring>
#include <array>

namespace hypermine {
namespace sha256 {

// ============================================================================
// Constantes SHA-256 (primeiros 32 bits das partes fracionárias
// das raízes cúbicas dos primeiros 64 primos)
// ============================================================================

static constexpr std::array<uint32_t, 64> K = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

// ============================================================================
// Operações Fundamentais
// ============================================================================

/// Rotação à direita de 32 bits
static inline constexpr uint32_t rotr(uint32_t x, int n) {
    return (x >> n) | (x << (32 - n));
}

/// Função de escolha: se x então y, senão z
static inline constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (~x & z);
}

/// Função de maioria: maioria de bits em x, y, z
static inline constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}

/// Sigma0 (para message schedule)
static inline constexpr uint32_t sigma0(uint32_t x) {
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
}

/// Sigma1 (para message schedule)
static inline constexpr uint32_t sigma1(uint32_t x) {
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
}

/// Sigma0 maiúsculo (para compressão)
static inline constexpr uint32_t Sigma0(uint32_t x) {
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
}

/// Sigma1 maiúsculo (para compressão)
static inline constexpr uint32_t Sigma1(uint32_t x) {
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
}

// ============================================================================
// Estado SHA-256
// ============================================================================

struct Sha256State {
    uint32_t h[8];  // Estado hash (256 bits)
    uint64_t total;  // Total de bytes processados
    uint8_t buffer[64]; // Buffer para bloco parcial
    uint32_t buflen;    // Bytes no buffer
};

/// Inicializa o estado SHA-256 com os valores iniciais (H0)
void sha256_init(Sha256State& state) {
    state.h[0] = 0x6a09e667;
    state.h[1] = 0xbb67ae85;
    state.h[2] = 0x3c6ef372;
    state.h[3] = 0xa54ff53a;
    state.h[4] = 0x510e527f;
    state.h[5] = 0x9b05688c;
    state.h[6] = 0x1f83d9ab;
    state.h[7] = 0x5be0cd19;
    state.total = 0;
    state.buflen = 0;
}

// ============================================================================
// Função de Compressão (64 rodadas)
// ============================================================================

/// Processa um bloco de 512 bits (64 bytes)
void sha256_transform(Sha256State& state, const uint8_t block[64]) {
    uint32_t W[64];
    uint32_t a, b, c, d, e, f, g, h;
    
    // Preparar message schedule (W)
    // Primeiros 16 words: converter big-endian para host
    for (int i = 0; i < 16; ++i) {
        W[i] = (static_cast<uint32_t>(block[i * 4]) << 24)
             | (static_cast<uint32_t>(block[i * 4 + 1]) << 16)
             | (static_cast<uint32_t>(block[i * 4 + 2]) << 8)
             | (static_cast<uint32_t>(block[i * 4 + 3]));
    }
    
    // Words 16-63: extensão via sigma functions
    for (int i = 16; i < 64; ++i) {
        W[i] = sigma1(W[i - 2]) + W[i - 7] + sigma0(W[i - 15]) + W[i - 16];
    }
    
    // Inicializar variáveis de trabalho
    a = state.h[0]; b = state.h[1]; c = state.h[2]; d = state.h[3];
    e = state.h[4]; f = state.h[5]; g = state.h[6]; h = state.h[7];
    
    // 64 rodadas de compressão
    for (int i = 0; i < 64; ++i) {
        uint32_t T1 = h + Sigma1(e) + ch(e, f, g) + K[i] + W[i];
        uint32_t T2 = Sigma0(a) + maj(a, b, c);
        
        h = g;
        g = f;
        f = e;
        e = d + T1;
        d = c;
        c = b;
        b = a;
        a = T1 + T2;
    }
    
    // Adicionar ao estado
    state.h[0] += a; state.h[1] += b; state.h[2] += c; state.h[3] += d;
    state.h[4] += e; state.h[5] += f; state.h[6] += g; state.h[7] += h;
}

// ============================================================================
// Interface Pública
// ============================================================================

/// Atualiza o hash com dados adicionais
void sha256_update(Sha256State& state, const uint8_t* data, size_t len) {
    state.total += len;
    
    // Se temos dados no buffer, completar o bloco
    if (state.buflen > 0) {
        uint32_t need = 64 - state.buflen;
        if (len < need) {
            memcpy(state.buffer + state.buflen, data, len);
            state.buflen += len;
            return;
        }
        memcpy(state.buffer + state.buflen, data, need);
        sha256_transform(state, state.buffer);
        data += need;
        len -= need;
        state.buflen = 0;
    }
    
    // Processar blocos completos
    while (len >= 64) {
        sha256_transform(state, data);
        data += 64;
        len -= 64;
    }
    
    // Guardar dados restantes no buffer
    if (len > 0) {
        memcpy(state.buffer, data, len);
        state.buflen = len;
    }
}

/// Finaliza o hash e produz o digest de 256 bits
void sha256_final(Sha256State& state, uint8_t digest[32]) {
    // Padding: 1 bit + zeros + comprimento em 64 bits big-endian
    uint64_t total_bits = state.total * 8;
    
    uint8_t pad = 0x80;
    sha256_update(state, &pad, 1);
    
    // Pad com zeros até 56 bytes (mod 64)
    uint8_t zero = 0;
    while (state.buflen != 56) {
        sha256_update(state, &zero, 1);
    }
    
    // Comprimento em big-endian (8 bytes)
    uint8_t len_bytes[8];
    for (int i = 7; i >= 0; --i) {
        len_bytes[i] = total_bits & 0xff;
        total_bits >>= 8;
    }
    sha256_update(state, len_bytes, 8);
    
    // Converter estado para big-endian
    for (int i = 0; i < 8; ++i) {
        digest[i * 4]     = (state.h[i] >> 24) & 0xff;
        digest[i * 4 + 1] = (state.h[i] >> 16) & 0xff;
        digest[i * 4 + 2] = (state.h[i] >> 8) & 0xff;
        digest[i * 4 + 3] = state.h[i] & 0xff;
    }
}

// ============================================================================
// Função de Conveniência: SHA-256 de um bloco
// ============================================================================

/// Calcula SHA-256 de um bloco de dados
void sha256(const uint8_t* data, size_t len, uint8_t digest[32]) {
    Sha256State state;
    sha256_init(state);
    sha256_update(state, data, len);
    sha256_final(state, digest);
}

/// Double SHA-256 (usado no Bitcoin)
/// hash = SHA-256(SHA-256(data))
void double_sha256(const uint8_t* data, size_t len, uint8_t digest[32]) {
    uint8_t first_hash[32];
    sha256(data, len, first_hash);
    sha256(first_hash, 32, digest);
}

/// Verifica se um hash satisfaz o target de dificuldade
/// Retorna true se hash < target (little-endian comparison)
bool check_difficulty(const uint8_t hash[32], const uint8_t target[32]) {
    for (int i = 31; i >= 0; --i) {
        if (hash[i] < target[i]) return true;
        if (hash[i] > target[i]) return false;
    }
    return false; // hash == target
}

// ============================================================================
// Loop de Mineração (Single-threaded, referência)
// ============================================================================

/// Minera um bloco tentando nonces sequenciais
/// Retorna o nonce encontrado ou 0 se nenhum foi encontrado
uint64_t mine_block_generic(
    const uint8_t* block_header,  // 76 bytes (sem nonce)
    size_t header_len,
    const uint8_t target[32],
    uint64_t nonce_start,
    uint64_t nonce_end
) {
    uint8_t header[80]; // 76 bytes header + 4 bytes nonce
    memcpy(header, block_header, header_len);
    
    uint8_t hash[32];
    
    for (uint64_t nonce = nonce_start; nonce < nonce_end; ++nonce) {
        // Inserir nonce no header (little-endian, offset 76)
        header[76] = nonce & 0xff;
        header[77] = (nonce >> 8) & 0xff;
        header[78] = (nonce >> 16) & 0xff;
        header[79] = (nonce >> 24) & 0xff;
        
        // Double SHA-256
        double_sha256(header, 80, hash);
        
        // Verificar dificuldade
        if (check_difficulty(hash, target)) {
            return nonce;
        }
    }
    
    return 0; // Nenhum nonce encontrado
}

} // namespace sha256
} // namespace hypermine
