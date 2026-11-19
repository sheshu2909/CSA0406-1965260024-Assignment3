/* q3_segment.c - translate (segment, offset) pairs through a segment table
 * and show what happens when the offset exceeds the segment limit.
 */
#include <stdio.h>

#define SEGMENTS 4

struct segment {
    const char *name;
    unsigned base;
    unsigned limit;      /* size in bytes */
    int      prot;       /* 0 = read-only, 1 = read/write */
};

static struct segment table[SEGMENTS] = {
    /*  name      base    limit   prot */
    { "code",    0x00400000, 0x00080000, 0 },   /* 512 KB, read-only */
    { "data",    0x00800000, 0x00040000, 1 },   /* 256 KB, read/write */
    { "heap",    0x00C00000, 0x00200000, 1 },   /*   2 MB, read/write */
    { "stack",   0x7FF00000, 0x00010000, 1 },   /*  64 KB, read/write */
};

static void translate(const char *what, int seg, unsigned offset)
{
    if (seg < 0 || seg >= SEGMENTS) {
        printf("%-22s seg %d off 0x%06X  -> invalid segment\n", what, seg, offset);
        return;
    }
    const struct segment *s = &table[seg];
    printf("%-22s seg %d off 0x%06X  -> ", what, seg, offset);
    if (offset >= s->limit) {
        printf("SEGMENTATION FAULT (offset %u >= limit %u)\n", offset, s->limit);
        return;
    }
    printf("physical 0x%08X  [%s, %s]\n", s->base + offset, s->name,
           s->prot ? "read/write" : "read-only");
}

int main(void)
{
    printf("segment table\n");
    printf("%-8s %10s %10s  %s\n", "segment", "base", "limit", "protection");
    for (int i = 0; i < SEGMENTS; i++)
        printf("%-8s 0x%08X %10u  %s\n", table[i].name, table[i].base,
               table[i].limit, table[i].prot ? "read/write" : "read-only");

    printf("\ntranslations\n");
    translate("main()",              0, 0x00000100);
    translate("printf()",            0, 0x0007FFF0);
    translate("customer_record[0]",  1, 0x00000000);
    translate("customer_record[9]",  1, 0x00000240);
    translate("malloc() result",     2, 0x00100000);
    translate("recursion frame",     3, 0x0000FFF0);
    translate("runaway pointer",     3, 0x00010000);   /* one past the end */
    translate("corrupt index",      9, 0x00000010);   /* no such segment */

    printf("\nnote: the code segment is read-only, so a write to 0x%08X\n"
           "      would be stopped by the MMU even though it is inside the limit.\n",
           table[0].base + 0x100);
    return 0;
}
