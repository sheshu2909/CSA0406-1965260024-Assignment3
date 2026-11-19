/* q2_todo.c - Q2 "Complete the Code".
 * The given program, with TODO 1 filled in. PAGE_SIZE can be overridden at
 * compile time with -DPAGE_SIZE=2048 for the second half of the exercise.
 */
#include <stdio.h>

#ifndef PAGE_SIZE
#define PAGE_SIZE 1024
#endif
#define PAGES 8

/* Page table of a process: frame number, or -1 if the page is not in memory. */
int page_table[PAGES] = {5, 2, -1, 7, 0, -1, 3, -1};

int main(void)
{
    unsigned logical[] = {0, 1500, 3100, 6200, 9000, 2049};
    printf("PAGE_SIZE = %d\n", PAGE_SIZE);

    for (int i = 0; i < 6; i++) {
        unsigned a = logical[i];
        /* TODO 1 (completed): split the address into page number and offset,
         * then translate through the page table. */
        unsigned p = a / PAGE_SIZE;
        unsigned d = a % PAGE_SIZE;

        printf("%u -> page %u offset %u : ", a, p, d);

        if (p >= PAGES) {
            printf("invalid address\n");
            continue;
        }
        int frame = page_table[p];
        if (frame == -1) {
            printf("page fault\n");
            continue;
        }
        printf("physical %u\n", (unsigned)(frame * PAGE_SIZE) + d);
    }
    return 0;
}
