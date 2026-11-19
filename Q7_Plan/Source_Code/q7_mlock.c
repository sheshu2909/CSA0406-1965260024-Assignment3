/* q7_mlock.c - worst-case delay of a time-critical control loop, measured
 * with the control buffer paged normally and with it locked in memory.
 *
 * Usage: q7_mlock [-l] [iterations] [buffer_mb]
 *   -l            lock the buffer with mlock() before the loop
 *
 * Each iteration does the same amount of work on a large buffer, so a page
 * fault inside an iteration shows up as one unusually slow iteration.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <unistd.h>
#include <sys/mman.h>
#include <windows.h>
#include <psapi.h>

static double now_us(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e6 + t.tv_nsec / 1e3;
}

static unsigned long faults(void)
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof pmc))
        return (unsigned long)pmc.PageFaultCount;
    return 0;
}

int main(int argc, char **argv)
{
    int lock = 0, iters = 2000;
    size_t mb = 32;
    int positional = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-l") == 0) lock = 1;
        else if (positional == 0) { iters = atoi(argv[i]); positional++; }
        else mb = (size_t)atoi(argv[i]);
    }

    size_t bytes = mb * 1024 * 1024;
    unsigned char *buf = malloc(bytes);
    if (!buf) { perror("malloc"); return 1; }
    memset(buf, 1, bytes);

    int locked = 0;
    if (lock) {
        if (mlock(buf, bytes) == 0) locked = 1;
        else printf("mlock failed: %s (errno %d)\n", strerror(errno), errno);
    }

    unsigned long f0 = faults();
    double *sample = malloc(sizeof(double) * (size_t)iters);
    if (!sample) { perror("malloc"); return 1; }

    unsigned char acc = 0;
    for (int i = 0; i < iters; i++) {
        double t0 = now_us();
        /* the control computation: read and write one byte per 4 KB page */
        for (size_t off = 0; off < bytes; off += 4096) {
            buf[off] = (unsigned char)(buf[off] + 1);
            acc ^= buf[off];
        }
        double t1 = now_us();
        sample[i] = t1 - t0;
    }
    unsigned long f1 = faults();

    /* min, mean, 99th percentile and worst case */
    double sum = 0.0, worst = sample[0], best = sample[0];
    int over_1000 = 0;
    for (int i = 0; i < iters; i++) {
        sum += sample[i];
        if (sample[i] > worst) worst = sample[i];
        if (sample[i] < best)  best  = sample[i];
        if (sample[i] > 1000.0) over_1000++;
    }
    for (int i = 1; i < iters; i++) {          /* insertion sort for p99 */
        double v = sample[i];
        int j = i - 1;
        while (j >= 0 && sample[j] > v) { sample[j + 1] = sample[j]; j--; }
        sample[j + 1] = v;
    }

    printf("mode            : %s\n", lock ? (locked ? "mlock (locked)" : "mlock requested, NOT locked")
                                           : "normal paging");
    printf("buffer          : %zu MB, iterations %d\n", mb, iters);
    printf("mean            : %10.1f us\n", sum / iters);
    printf("minimum         : %10.1f us\n", best);
    printf("99th percentile : %10.1f us\n", sample[(int)(iters * 0.99)]);
    printf("worst case      : %10.1f us\n", worst);
    printf("iterations > 1 ms: %d\n", over_1000);
    printf("page faults     : %lu\n", f1 - f0);
    printf("(checksum %u)\n", acc);

    if (locked) munlock(buf, bytes);
    free(sample);
    free(buf);
    return 0;
}
