/* q3_tables.c - size of the translation tables for the same program under
 * pure paging, pure segmentation and segmented paging (Intel x86 style).
 */
#include <stdio.h>

int main(void)
{
    const double page_size   = 4096.0;
    const double pte_bytes   = 4.0;        /* a 32-bit page-table entry */
    const double ste_bytes   = 8.0;        /* base + limit + protection */
    const double addr_32     = 4294967296.0;   /* 4 GiB */

    const double pages_32    = addr_32 / page_size;
    const double paging_1lv  = pages_32 * pte_bytes;

    /* two-level: 1024 entries per table, 1024 tables, only the used ones */
    const double used_pages  = 300000.0;                  /* ~1.2 GB program */
    const double tables_used = (used_pages / 1024.0 < 1024.0)
                               ? (used_pages / 1024.0) : 1024.0;
    const double paging_2lv  = 1024.0 * pte_bytes          /* directory */
                             + tables_used * 1024.0 * pte_bytes;

    const double segments    = 4.0;
    const double seg_table   = segments * ste_bytes;

    /* segmented paging: each segment has its own page table */
    const double seg_paging  = seg_table + segments * 1024.0 * pte_bytes;

    printf("%-34s %14s\n", "scheme", "table bytes");
    printf("%-34s %14.0f\n", "paging, one level, whole 4 GiB", paging_1lv);
    printf("%-34s %14.0f\n", "paging, two level, 1.2 GB program", paging_2lv);
    printf("%-34s %14.0f\n", "pure segmentation, 4 segments", seg_table);
    printf("%-34s %14.0f\n", "segmented paging, 4 segments", seg_paging);

    printf("\n%-34s %14.0f\n", "paging 1-level in KB", paging_1lv / 1024);
    printf("%-34s %14.0f\n", "paging 2-level in KB", paging_2lv / 1024);
    printf("%-34s %14.0f\n", "segmentation in bytes", seg_table);
    printf("%-34s %14.0f\n", "segmented paging in KB", seg_paging / 1024);

    printf("\naddress bits:\n");
    printf("  32-bit address, 4 KB pages -> %10.0f pages, %2.0f bits of page number, "
           "%2.0f bits of offset\n", pages_32, 20.0, 12.0);
    printf("  48-bit address, 4 KB pages -> %10.0f pages, %2.0f bits of page number, "
           "%2.0f bits of offset\n", (281474976710656.0 / page_size), 36.0, 12.0);
    printf("  4-level x86-64 walk: 9 + 9 + 9 + 9 + 12 = 48 bits\n");
    return 0;
}
