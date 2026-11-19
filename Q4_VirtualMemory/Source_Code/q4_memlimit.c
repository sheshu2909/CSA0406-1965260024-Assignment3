/* q4_memlimit.c - touch a growing working set and report the time and the
 * page faults, so the effect of running out of RAM can be measured by
 * starting the program under a memory limit.
 *
 * Usage: q4_memlimit <megabytes> [passes]
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <windows.h>
#include <psapi.h>

static unsigned long page_faults(void)
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof pmc))
        return (unsigned long)pmc.PageFaultCount;
    return 0;
}

static unsigned long peak_working_set_kb(void)
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof pmc))
        return (unsigned long)(pmc.PeakWorkingSetSize / 1024);
    return 0;
}

static double now_ms(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

int main(int argc, char **argv)
{
    size_t mb    = (argc > 1) ? (size_t)atoi(argv[1]) : 128;
    int    passes = (argc > 2) ? atoi(argv[2]) : 3;
    size_t bytes = mb * 1024 * 1024;
    size_t pages = bytes / 4096;

    char *buf = malloc(bytes);
    if (!buf) {
        fprintf(stderr, "malloc(%zu MB) failed\n", mb);
        return 1;
    }

    unsigned long f0 = page_faults();
    double t0 = now_ms();

    for (int r = 0; r < passes; r++)
        for (size_t p = 0; p < pages; p++)
            buf[p * 4096] = (char)(p + r);

    double t1 = now_ms();
    unsigned long f1 = page_faults();

    unsigned long long checksum = 0;
    for (size_t p = 0; p < pages; p++) checksum += (unsigned char)buf[p * 4096];

    printf("%5zu MB  %d pass(es)  %9.2f ms  faults %9lu  peak working set %8lu KB  "
           "checksum %llu\n",
           mb, passes, t1 - t0, f1 - f0, peak_working_set_kb(), checksum);

    free(buf);
    return 0;
}
