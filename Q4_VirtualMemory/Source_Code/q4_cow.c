/* q4_cow.c - show that fork() copies page tables, not pages: the child
 * shares every page until it writes, and only the written pages are copied.
 *
 * Counters come from GetProcessMemoryInfo(), because the MSYS2 runtime's
 * getrusage() reports no fault counts.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <windows.h>
#include <psapi.h>

#define MB 128

static void counters(const char *who)
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof pmc))
        printf("%-34s working set %8lu KB   faults %8lu\n", who,
               (unsigned long)(pmc.WorkingSetSize / 1024),
               (unsigned long)pmc.PageFaultCount);
    fflush(stdout);
}

int main(void)
{
    size_t bytes = (size_t)MB * 1024 * 1024;
    char *buf = malloc(bytes);
    if (!buf) { perror("malloc"); return 1; }
    memset(buf, 0x5A, bytes);              /* every page is private */

    counters("parent before fork");

    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 1; }

    if (pid == 0) {
        /* child 1: read every page, no writes -> pages stay shared */
        unsigned long long sum = 0;
        for (size_t i = 0; i < bytes; i += 4096) sum += (unsigned char)buf[i];
        counters("child: read all pages");
        printf("   (checksum %llu)\n", sum);
        fflush(stdout);
        exit(0);                            /* exit(), not _exit(): flush */
    }
    int st;
    waitpid(pid, &st, 0);
    counters("parent after child 1");

    pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {
        /* child 2: write one byte per page -> every page is copied */
        for (size_t i = 0; i < bytes; i += 4096) buf[i] = 0x11;
        counters("child: wrote every page");
        fflush(stdout);
        exit(0);
    }
    waitpid(pid, &st, 0);
    counters("parent after child 2");

    pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {
        /* child 3: write 1 MB of the 128 MB -> only 256 pages copied */
        for (size_t i = 0; i < 1024 * 1024; i += 4096) buf[i] = 0x22;
        counters("child: wrote only 1 MB");
        fflush(stdout);
        exit(0);
    }
    waitpid(pid, &st, 0);
    counters("parent after child 3");

    free(buf);
    return 0;
}
