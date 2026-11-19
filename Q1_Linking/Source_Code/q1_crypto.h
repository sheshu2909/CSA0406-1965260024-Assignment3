/* q1_crypto.h - the bank's "encryption library" used for the linking study. */
#ifndef Q1_CRYPTO_H
#define Q1_CRYPTO_H

#include <stddef.h>

/* Version string so two library builds can be told apart at run time. */
const char *crypto_version(void);

/* Encrypt n bytes in place with a rotating-XOR cipher (stands in for AES). */
void crypto_encrypt(unsigned char *buf, size_t n);

/* Checksum used to show that the plaintext round-trips. */
unsigned long crypto_checksum(const unsigned char *buf, size_t n);

#endif /* Q1_CRYPTO_H */
