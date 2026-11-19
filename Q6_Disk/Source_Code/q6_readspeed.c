/* q6_readspeed.c - measure sequential read throughput of the filesystem that
 * holds the file passed on the command line. The same program measures the
 * SSD here and would measure a hard disk on a machine that has one.
 *
 * Usage: q6_readspeed <file> [passes]
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CHUNK (1024 * 1024)

static double now_ms(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <file> [passes]\n", argv[0]);
        return 1;
    }
    int passes = (argc > 2) ? atoi(argv[2]) : 3;

    /* create a 256 MB file of pseudo-random data if it is not there yet */
    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        f = fopen(argv[1], "wb");
        if (!f) { perror("create"); return 1; }
        char *blk = malloc(CHUNK);
        if (!blk) { perror("malloc"); return 1; }
        srand(1965260024);
        for (int i = 0; i < 256; i++) {
            for (int j = 0; j < CHUNK; j += 4)
                *(unsigned int *)(blk + j) = (unsigned int)rand();
            fwrite(blk, 1, CHUNK, f);
        }
        fclose(f);
        free(blk);
        printf("created %s (256 MB)\n", argv[1]);
        f = fopen(argv[1], "rb");
        if (!f) { perror("reopen"); return 1; }
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *buf = malloc(CHUNK);
    if (!buf) { perror("malloc"); return 1; }

    for (int p = 0; p < passes; p++) {
        fseek(f, 0, SEEK_SET);
        double t0 = now_ms();
        size_t total = 0;
        size_t n;
        while ((n = fread(buf, 1, CHUNK, f)) > 0) total += n;
        double t1 = now_ms();
        double secs = (t1 - t0) / 1000.0;
        printf("pass %d: %zu bytes in %8.2f ms  ->  %7.1f MB/s\n",
               p + 1, total, t1 - t0, (double)total / 1048576.0 / secs);
    }

    printf("\nfile size %.1f MB\n", size / 1048576.0);
    fclose(f);
    free(buf);
    return 0;
}
