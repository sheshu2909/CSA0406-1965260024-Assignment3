/* q3_frag.c - external fragmentation from segmentation.
 * 20 segments of random size are placed in a 64 MB region with first fit,
 * half of them are released, and the resulting holes are measured.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REGION   (64u * 1024u * 1024u)
#define SEGS     20

struct hole { unsigned start, len; };

static struct hole free_list[SEGS + 1];
static int free_count;

static int seg_start[SEGS], seg_len[SEGS];
static int alive[SEGS];

static void insert_free(unsigned start, unsigned len)
{
    int i = free_count++;
    while (i > 0 && free_list[i - 1].start > start) {
        free_list[i] = free_list[i - 1];
        i--;
    }
    free_list[i].start = start;
    free_list[i].len = len;

    /* coalesce with the neighbour on the right, then on the left */
    if (i + 1 < free_count &&
        free_list[i].start + free_list[i].len == free_list[i + 1].start) {
        free_list[i].len += free_list[i + 1].len;
        for (int j = i + 1; j + 1 < free_count; j++) free_list[j] = free_list[j + 1];
        free_count--;
    }
    if (i > 0 && free_list[i - 1].start + free_list[i - 1].len == free_list[i].start) {
        free_list[i - 1].len += free_list[i].len;
        for (int j = i; j + 1 < free_count; j++) free_list[j] = free_list[j + 1];
        free_count--;
    }
}

static int allocate(unsigned len)
{
    for (int i = 0; i < free_count; i++) {
        if (free_list[i].len < len) continue;
        unsigned start = free_list[i].start;
        free_list[i].start += len;
        free_list[i].len -= len;
        if (free_list[i].len == 0) {
            for (int j = i; j + 1 < free_count; j++) free_list[j] = free_list[j + 1];
            free_count--;
        }
        return (int)start;
    }
    return -1;
}

static void release(int seg)
{
    insert_free((unsigned)seg_start[seg], (unsigned)seg_len[seg]);
    alive[seg] = 0;
}

static void report(const char *when)
{
    unsigned free_bytes = 0, largest = 0;
    for (int i = 0; i < free_count; i++) {
        free_bytes += free_list[i].len;
        if (free_list[i].len > largest) largest = free_list[i].len;
    }
    unsigned used = 0;
    for (int i = 0; i < SEGS; i++) if (alive[i]) used += (unsigned)seg_len[i];

    printf("%-28s holes %2d  free %8.2f MB  largest %8.2f MB  used %8.2f MB\n",
           when, free_count, free_bytes / 1048576.0, largest / 1048576.0,
           used / 1048576.0);
}

int main(void)
{
    srand(1965260024);
    free_count = 0;
    insert_free(0, REGION);

    printf("region %.0f MB, 20 segments of random size (0.1 .. 6 MB)\n\n",
           REGION / 1048576.0);

    for (int i = 0; i < SEGS; i++) {
        seg_len[i] = (int)((rand() % 59 + 1) * 102400);   /* 0.1 .. 6 MB */
        alive[i] = 1;
    }

    int failed = 0;
    for (int i = 0; i < SEGS; i++) {
        int s = allocate((unsigned)seg_len[i]);
        if (s < 0) { failed++; alive[i] = 0; continue; }
        seg_start[i] = s;
    }
    printf("loaded %d of %d segments after first fit\n", SEGS - failed, SEGS);
    report("after loading");

    /* remove every segment with an odd index (a program exiting) */
    for (int i = 1; i < SEGS; i += 2)
        if (alive[i]) release(i);
    report("after removing 10 segments");

    printf("\nfree list\n");
    printf("%10s %10s\n", "start", "size");
    for (int i = 0; i < free_count; i++)
        printf("%10u %10u\n", free_list[i].start, free_list[i].len);

    unsigned free_bytes = 0;
    for (int i = 0; i < free_count; i++) free_bytes += free_list[i].len;
    printf("\nexternal fragmentation = 1 - largest_hole / total_free = ");
    unsigned largest = 0;
    for (int i = 0; i < free_count; i++)
        if (free_list[i].len > largest) largest = free_list[i].len;
    printf("%.2f%%\n", free_bytes ? 100.0 * (1.0 - (double)largest / free_bytes) : 0.0);

    /* 34 MB is free, but no single hole is big enough for a 6 MB segment */
    int probe = allocate(6u * 1024u * 1024u);
    printf("allocating 6 MB after the removals: %s\n",
           probe >= 0 ? "succeeded" : "FAILED - 34 MB is free but in pieces");
    probe = allocate(5u * 1024u * 1024u);
    printf("allocating 5 MB after the removals: %s\n",
           probe >= 0 ? "succeeded" : "FAILED - the free memory is in pieces");
    return 0;
}
