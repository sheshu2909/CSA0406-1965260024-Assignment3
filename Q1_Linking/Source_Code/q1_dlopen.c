/* q1_dlopen.c - load the encryption library only when the branch really needs
 * to encrypt something (Alternative Concept: run-time loading).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>

typedef const char *(*version_fn)(void);
typedef void (*encrypt_fn)(unsigned char *, size_t);
typedef unsigned long (*checksum_fn)(const unsigned char *, size_t);

int main(int argc, char **argv)
{
    const char *path = (argc > 1) ? argv[1] : "./libcrypto.so";
    printf("opening %s lazily (RTLD_LAZY)\n", path);

    void *h = dlopen(path, RTLD_LAZY);
    if (!h) {
        fprintf(stderr, "dlopen failed: %s\n", dlerror());
        return 2;                      /* library missing: caller decides */
    }

    version_fn  ver  = (version_fn)  dlsym(h, "crypto_version");
    encrypt_fn  enc  = (encrypt_fn)  dlsym(h, "crypto_encrypt");
    checksum_fn sum  = (checksum_fn) dlsym(h, "crypto_checksum");
    const char *err  = dlerror();
    if (err || !ver || !enc || !sum) {
        fprintf(stderr, "dlsym failed: %s\n", err ? err : "missing symbol");
        dlclose(h);
        return 3;
    }

    unsigned char buf[64];
    for (size_t i = 0; i < sizeof buf; i++)
        buf[i] = (unsigned char)i;

    printf("library version : %s\n", ver());
    printf("checksum before : %lu\n", sum(buf, sizeof buf));
    enc(buf, sizeof buf);
    printf("checksum after  : %lu\n", sum(buf, sizeof buf));

    dlclose(h);
    printf("library unloaded\n");
    return 0;
}
