/* q1_tables.c - the encryption library's substitution tables.
 *
 * A real cipher ships hundreds of kilobytes of constant tables; this file
 * carries 8 MB so that the difference between copying the library into every
 * executable and sharing one copy in memory can actually be measured.
 */
#include <stddef.h>

#define SBOX_BYTES (8u * 1024u * 1024u)

const unsigned char crypto_sbox[SBOX_BYTES] = { 1 };

const size_t crypto_sbox_len = SBOX_BYTES;
