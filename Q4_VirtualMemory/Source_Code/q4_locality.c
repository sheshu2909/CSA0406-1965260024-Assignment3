/* q4_locality.c - count page faults for the same amount of work done with
 * good locality (sequential) and poor locality (random order).
 *
 * The program runs on the MSYS2 runtime, whose getrusage() does not report
 * page faults, so the counters come from the Windows process API:
 *   PageFaultCount  - hard and soft faults taken by the process
 *   WorkingSetSize  - physical pages currently mapped in
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

static unsigned long working_set_kb(void)
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof pmc))
        return (unsigned long)(pmc.WorkingSetSize / 1024);
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
    size_t mb    = (argc > 1) ? (size_t)atoi(argv[1]) : 64;
    size_t bytes = mb * 1024 * 1024;
    long sys_page = sysconf(_SC_PAGESIZE);

    printf("buffer %zu MB, MSYS2 page size %ld B, Windows page 4096 B\n",
           mb, sys_page);
    printf("pages touched: %zu (one byte per 4 KB)\n\n", bytes / 4096);

    char *buf = malloc(bytes);
    if (!buf) { perror("malloc"); return 1; }
    memset(buf, 1, bytes);                 /* leave no page untouched */

    /* Trim the working set before each pass, so both passes start with the
     * buffer paged out and the fault counts show locality, not luck. */
    EmptyWorkingSet(GetCurrentProcess());
    printf("baseline   faults %8lu  working set %7lu KB (after trim)\n",
           page_faults(), working_set_kb());

    /* 1. sequential: one byte per 4 KB page, in address order */
    unsigned long f0 = page_faults();
    double t0 = now_ms();
    for (size_t off = 0; off < bytes; off += 4096)
        buf[off]++;
    double t1 = now_ms();
    unsigned long f1 = page_faults();
    printf("sequential faults %8lu  (%+ld)  time %8.3f ms\n",
           f1, (long)(f1 - f0), t1 - t0);

    /* 2. random: identical work, random page order (poor locality) */
    size_t pages = bytes / 4096;
    size_t *order = malloc(pages * sizeof *order);
    if (!order) { perror("malloc order"); return 1; }
    for (size_t i = 0; i < pages; i++) order[i] = i;
    srand(1965260024);
    for (size_t i = pages; i > 1; i--) {          /* Fisher-Yates shuffle */
        size_t j = (size_t)rand() % i;
        size_t t = order[i - 1]; order[i - 1] = order[j]; order[j] = t;
    }

    EmptyWorkingSet(GetCurrentProcess());
    printf("trimmed before the random pass, working set %lu KB\n", working_set_kb());
    unsigned long f2 = page_faults();
    t0 = now_ms();
    for (size_t i = 0; i < pages; i++)
        buf[order[i] * 4096]++;
    t1 = now_ms();
    unsigned long f3 = page_faults();
    printf("random     faults %8lu  (%+ld)  time %8.3f ms\n",
           f3, (long)(f3 - f2), t1 - t0);

    printf("\nsummary: %zu pages touched, %ld fault(s) sequential, %ld random\n",
           pages, (long)(f1 - f0), (long)(f3 - f2));
    printf("working set after the run: %lu KB\n", working_set_kb());

    free(order);
    free(buf);
    return 0;
}
