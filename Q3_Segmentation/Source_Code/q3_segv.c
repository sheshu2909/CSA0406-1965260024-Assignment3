/* q3_segv.c - trigger a real segmentation fault and print what happened
 * before it, so the shell can report the signal and the core-dump state.
 */
#define _GNU_SOURCE   /* sigaction(), SA_SIGINFO, siginfo_t */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

static void handler(int sig, siginfo_t *info, void *ctx)
{
    (void)ctx;
    printf("\ncaught signal %d (%s)\n", sig,
           sig == SIGSEGV ? "SIGSEGV" : "other");
    printf("faulting address : %p\n", info->si_addr);
    printf("reason           : %s\n",
           info->si_code == SEGV_MAPERR ? "SEGV_MAPERR (no mapping)" :
           info->si_code == SEGV_ACCERR ? "SEGV_ACCERR (wrong permissions)" :
                                          "other code");
    printf("the kernel delivered SIGSEGV, the handler will now re-raise it\n");
    signal(SIGSEGV, SIG_DFL);
    raise(SIGSEGV);
}

int main(void)
{
    printf("pid %d, about to write through a NULL pointer\n", (int)getpid());

    struct sigaction sa;
    sa.sa_sigaction = handler;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);

    int *p = NULL;
    *p = 42;                 /* the fault happens here */
    printf("never reached: %d\n", *p);
    return 0;
}
