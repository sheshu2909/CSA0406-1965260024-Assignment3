/* q1_maps.c - show where the program and its libraries are mapped.
 * Reads /proc/<pid>/maps of THIS process (not of the shell command).
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "q1_crypto.h"

int main(void)
{
    unsigned char buf[32];
    for (size_t i = 0; i < sizeof buf; i++)
        buf[i] = (unsigned char)i;
    crypto_encrypt(buf, sizeof buf);   /* force the library to be used */

    pid_t pid = getpid();
    char path[64];
    snprintf(path, sizeof path, "/proc/%d/maps", (int)pid);

    FILE *f = fopen(path, "r");
    if (!f) { perror("fopen maps"); return 1; }

    printf("pid %d, address space (text, data and shared objects only)\n", (int)pid);
    printf("%-34s %-6s %-9s %s\n", "address range", "perms", "offset", "object");

    char line[512];
    int shown = 0;
    while (fgets(line, sizeof line, f)) {
        /* keep the program image, the stack and any shared library */
        if (!strstr(line, "q1_") && !strstr(line, ".so") && !strstr(line, "[stack]"))
            continue;
        char range[64], perms[8], offset[16], dev[16], obj[256];
        obj[0] = '\0';
        if (sscanf(line, "%63s %7s %15s %15s %*s %255[^\n]", range, perms, offset, dev, obj) >= 4)
            printf("%-34s %-6s %-9s %s\n", range, perms, offset, obj);
        if (++shown > 40) break;
    }
    fclose(f);
    printf("main is at %p, crypto_encrypt at %p\n", (void *)main, (void *)crypto_encrypt);
    return 0;
}
