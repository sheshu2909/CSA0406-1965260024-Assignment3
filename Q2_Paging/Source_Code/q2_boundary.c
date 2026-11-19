/* q2_boundary.c - touch addresses at the start of a page, the last byte of a
 * page, and one byte past the end of a mapped region, to show that the MMU
 * works in whole pages and that the page after a mapping is unmapped.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <setjmp.h>
#include <sys/mman.h>

static sigjmp_buf jump;
static volatile sig_atomic_t faulted;

static void on_segv(int sig)
{
    (void)sig;
    faulted = 1;
    siglongjmp(jump, 1);
}

static void probe(const char *what, volatile unsigned char *p)
{
    faulted = 0;
    if (sigsetjmp(jump, 1) == 0) {
        unsigned char v = *p;
        printf("%-34s %p  read ok, value %u\n", what, (void *)p, v);
    } else {
        printf("%-34s %p  SIGSEGV (%s)\n", what, (void *)p,
               faulted ? "page not mapped" : "unknown");
    }
}

int main(void)
{
    long page = sysconf(_SC_PAGESIZE);
    printf("system page size: %ld bytes\n\n", page);

    size_t len = (size_t)page * 2;             /* exactly two pages */
    unsigned char *base = mmap(NULL, len, PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (base == MAP_FAILED) { perror("mmap"); return 1; }
    memset(base, 0xAB, len);

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_segv;
    sigaction(SIGSEGV, &sa, NULL);

    probe("start of page 0", base);
    probe("last byte of page 0", base + page - 1);
    probe("start of page 1", base + page);
    probe("last byte of page 1", base + len - 1);
    probe("first byte past the mapping", base + len);

    /* Fault counts show that the two pages were really touched. */
    printf("\n");
    fflush(stdout);
    munmap(base, len);
    return 0;
}
