/* q2_eat.c - effective memory-access time with and without a TLB.
 *
 * EAT = h * (t_tlb + t_mem) + (1 - h) * (t_tlb + 2 * t_mem)
 * With a 4 KB page a 32-bit address needs one page-table level, a 48-bit
 * address needs four, so each extra level costs one more memory access.
 */
#include <stdio.h>

static double eat(double hit, int tlb_ns, int mem_ns, int levels)
{
    double miss_cost = tlb_ns + (levels + 1) * mem_ns;
    double hit_cost  = tlb_ns + mem_ns;
    return hit * hit_cost + (1.0 - hit) * miss_cost;
}

int main(void)
{
    const int mem_ns = 100;
    const int tlb_ns = 10;
    const double hits[] = {0.80, 0.95, 0.99};

    printf("TLB access %d ns, memory access %d ns\n\n", tlb_ns, mem_ns);

    printf("%-22s %10s %10s %10s\n", "scheme", "80% hit", "95% hit", "99% hit");
    printf("%-22s %10.2f %10.2f %10.2f\n", "no TLB (1-level walk)",
           (double)(2 * mem_ns), (double)(2 * mem_ns), (double)(2 * mem_ns));
    printf("%-22s %10.2f %10.2f %10.2f\n", "TLB, 32-bit (1 level)",
           eat(hits[0], tlb_ns, mem_ns, 1), eat(hits[1], tlb_ns, mem_ns, 1),
           eat(hits[2], tlb_ns, mem_ns, 1));
    printf("%-22s %10.2f %10.2f %10.2f\n", "TLB, 48-bit (4 levels)",
           eat(hits[0], tlb_ns, mem_ns, 4), eat(hits[1], tlb_ns, mem_ns, 4),
           eat(hits[2], tlb_ns, mem_ns, 4));

    printf("\ntranslation-only view: one 2 MB page covers 512 x 4 KB pages,\n"
           "so a 2 MB page needs no lower level for the same address range.\n");

    printf("\n%-10s %12s %12s %12s\n", "hit rate", "4 KB (ns)", "2 MB (ns)", "saving");
    for (int i = 0; i < 3; i++) {
        double small = eat(hits[i], tlb_ns, mem_ns, 2);   /* two levels */
        double large = eat(hits[i], tlb_ns, mem_ns, 1);   /* one level  */
        printf("%-10.0f %12.2f %12.2f %11.2f%%\n", hits[i] * 100, small, large,
               100.0 * (small - large) / small);
    }
    return 0;
}
