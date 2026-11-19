/* q2_frag.c - internal fragmentation for 100 processes of random size
 * under page sizes of 1 KB, 4 KB and 2 MB.
 *
 * Every process is rounded up to a whole number of pages; the waste is the
 * sum of the unused bytes in the last page of each process.
 */
#include <stdio.h>
#include <stdlib.h>

#define PROCESSES 100

static unsigned long sizes[PROCESSES];

static unsigned long round_up(unsigned long bytes, unsigned long page)
{
    return ((bytes + page - 1) / page) * page;
}

static void report(unsigned long page, const char *name)
{
    unsigned long used = 0, allocated = 0, max_waste = 0, worst = 0;

    for (int i = 0; i < PROCESSES; i++) {
        unsigned long r = round_up(sizes[i], page);
        unsigned long waste = r - sizes[i];
        used += sizes[i];
        allocated += r;
        if (waste > max_waste) { max_waste = waste; worst = (unsigned long)i; }
    }

    printf("%-6s page: requested %9lu B  allocated %9lu B  "
           "waste %8lu B (%5.2f%%)  worst %lu B (process %lu)\n",
           name, used, allocated, allocated - used,
           100.0 * (double)(allocated - used) / (double)allocated,
           max_waste, worst);
}

int main(void)
{
    unsigned long total = 0;
    srand(20261119);                     /* fixed seed: reproducible run */

    /* Realistic student programs: 4 KB .. 20 MB, skewed towards small. */
    for (int i = 0; i < PROCESSES; i++) {
        unsigned long r = (unsigned long)rand();
        sizes[i] = 4096UL + (r % 4096UL) * (r % 5120UL);
        if (sizes[i] > 20UL * 1024 * 1024)
            sizes[i] = 20UL * 1024 * 1024;
        total += sizes[i];
    }

    printf("100 processes, total requested memory %lu B (%.1f MB)\n\n",
           total, total / 1048576.0);

    report(1024UL,        "1 KB");
    report(4096UL,        "4 KB");
    report(2UL * 1024 * 1024, "2 MB");

    printf("\nper-process view (first 10):\n");
    printf("%8s %10s %10s %10s\n", "process", "bytes", "4KB alloc", "waste");
    for (int i = 0; i < 10; i++)
        printf("%8d %10lu %10lu %10lu\n", i, sizes[i],
               round_up(sizes[i], 4096UL), round_up(sizes[i], 4096UL) - sizes[i]);
    return 0;
}
