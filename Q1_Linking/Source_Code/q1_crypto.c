/* q1_crypto.c - implementation of the bank's encryption library.
 * Built twice: once into libcrypto.so.1 (version "1.0") and once into
 * libcrypto.so.2 (version "2.0", different key) so the loader can be shown
 * picking up a replacement library without recompiling the program.
 */
#include "q1_crypto.h"

/* substitution tables defined in q1_tables.c (8 MB) */
extern const unsigned char crypto_sbox[];
extern const size_t crypto_sbox_len;

#ifdef LIB_VERSION_2
#define CRYPTO_KEY 0xA7u
#define CRYPTO_VERSION "2.0"
#else
#define CRYPTO_KEY 0x5Au
#define CRYPTO_VERSION "1.0"
#endif

const char *crypto_version(void)
{
    return CRYPTO_VERSION;
}

void crypto_encrypt(unsigned char *buf, size_t n)
{
    unsigned char key = CRYPTO_KEY;
    for (size_t i = 0; i < n; i++) {
        unsigned char v = buf[i];
        v ^= crypto_sbox[(i * 4099u) % crypto_sbox_len] ^ key;
        v = (unsigned char)((v << 3) | (v >> 5));   /* rotate left by 3 */
        buf[i] = v;
        key = (unsigned char)(key + 7u);            /* key schedule */
    }
}

unsigned long crypto_checksum(const unsigned char *buf, size_t n)
{
    unsigned long sum = 5381UL;
    for (size_t i = 0; i < n; i++)
        sum = ((sum << 5) + sum) ^ buf[i];          /* djb2-style */
    return sum;
}
