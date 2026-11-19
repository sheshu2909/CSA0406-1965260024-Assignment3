/* q5_replace.c - FIFO, LRU, Optimal and Clock (second chance) over the same
 * reference strings, 3 to 10 frames, with timing for 100,000 references.
 *
 * Two workloads:
 *   locality - a small hot set with occasional excursions (a web server)
 *   random   - uniformly random pages (no locality at all)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define REFS 100000      /* timing run */
#define TBL_REFS 10000   /* fault table: Optimal is O(n^2), so it needs a shorter string */
#define OPT_REFS 2000    /* Optimal timing */
#define MAXF 10

static int find(const int *f, int n, int page)
{
    for (int i = 0; i < n; i++)
        if (f[i] == page) return i;
    return -1;
}

static long fifo(const int *ref, int len, int frames)
{
    int f[MAXF]; int used = 0, next = 0; long faults = 0;
    for (int i = 0; i < len; i++) {
        if (find(f, used, ref[i]) >= 0) continue;
        faults++;
        if (used < frames) f[used++] = ref[i];
        else { f[next] = ref[i]; next = (next + 1) % frames; }
    }
    return faults;
}

static long lru(const int *ref, int len, int frames)
{
    int f[MAXF], last[MAXF]; int used = 0; long faults = 0;
    for (int i = 0; i < len; i++) {
        int k = find(f, used, ref[i]);
        if (k >= 0) { last[k] = i; continue; }
        faults++;
        if (used < frames) { f[used] = ref[i]; last[used] = i; used++; }
        else {
            int v = 0;
            for (int j = 1; j < frames; j++) if (last[j] < last[v]) v = j;
            f[v] = ref[i]; last[v] = i;
        }
    }
    return faults;
}

static long optimal(const int *ref, int len, int frames)
{
    int f[MAXF]; int used = 0; long faults = 0;
    for (int i = 0; i < len; i++) {
        if (find(f, used, ref[i]) >= 0) continue;
        faults++;
        if (used < frames) { f[used++] = ref[i]; continue; }
        int victim = 0, farthest = -1;
        for (int j = 0; j < frames; j++) {
            int next = len;
            for (int t = i + 1; t < len; t++)
                if (ref[t] == f[j]) { next = t; break; }
            if (next > farthest) { farthest = next; victim = j; }
        }
        f[victim] = ref[i];
    }
    return faults;
}

/* Clock / second chance: one reference bit per frame, hand sweeps round. */
static long clock_algo(const int *ref, int len, int frames)
{
    int f[MAXF], bit[MAXF]; int used = 0, hand = 0; long faults = 0;
    memset(bit, 0, sizeof bit);
    for (int i = 0; i < len; i++) {
        int k = find(f, used, ref[i]);
        if (k >= 0) { bit[k] = 1; continue; }
        faults++;
        if (used < frames) { f[used] = ref[i]; bit[used] = 1; used++; continue; }
        while (bit[hand]) { bit[hand] = 0; hand = (hand + 1) % frames; }
        f[hand] = ref[i]; bit[hand] = 1; hand = (hand + 1) % frames;
    }
    return faults;
}

static double now_ms(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

static void fill_locality(int *ref, int len, int pages)
{
    srand(1965260024);
    int hot = pages / 10;                 /* 10% hot set */
    for (int i = 0; i < len; i++) {
        if (rand() % 100 < 90) ref[i] = rand() % hot;              /* hot */
        else if (rand() % 100 < 70) ref[i] = hot + rand() % (pages - hot);
        else ref[i] = rand() % pages;                              /* random */
    }
}

static void fill_random(int *ref, int len, int pages)
{
    srand(1965260025);
    for (int i = 0; i < len; i++) ref[i] = rand() % pages;
}

int main(void)
{
    int *loc = malloc(sizeof(int) * TBL_REFS);
    int *rnd = malloc(sizeof(int) * TBL_REFS);
    int *loc_big = malloc(sizeof(int) * REFS);
    int *loc_opt = malloc(sizeof(int) * OPT_REFS);
    if (!loc || !rnd || !loc_big || !loc_opt) { perror("malloc"); return 1; }

    fill_locality(loc, TBL_REFS, 64);
    fill_random(rnd, TBL_REFS, 64);
    fill_locality(loc_big, REFS, 64);
    fill_locality(loc_opt, OPT_REFS, 64);

    printf("fault table: %d references, 64 pages, locality 90%% hot set\n\n", TBL_REFS);

    printf("%-8s %6s %8s %8s %8s %8s\n", "workload", "frames", "FIFO", "LRU", "Optimal", "Clock");
    for (int frames = 3; frames <= MAXF; frames++) {
        printf("%-8s %6d %8ld %8ld %8ld %8ld\n", "locality", frames,
               fifo(loc, TBL_REFS, frames), lru(loc, TBL_REFS, frames),
               optimal(loc, TBL_REFS, frames), clock_algo(loc, TBL_REFS, frames));
    }
    printf("\n");
    for (int frames = 3; frames <= MAXF; frames++) {
        printf("%-8s %6d %8ld %8ld %8ld %8ld\n", "random", frames,
               fifo(rnd, TBL_REFS, frames), lru(rnd, TBL_REFS, frames),
               optimal(rnd, TBL_REFS, frames), clock_algo(rnd, TBL_REFS, frames));
    }

    /* Belady's anomaly on the classic string */
    int b[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    printf("\nBelady string: FIFO 3 frames %ld, 4 frames %ld faults\n",
           fifo(b, 12, 3), fifo(b, 12, 4));
    printf("               LRU  3 frames %ld, 4 frames %ld faults\n",
           lru(b, 12, 3), lru(b, 12, 4));

    /* timing: 100,000 references for the on-line algorithms, 2,000 for the
     * off-line Optimal algorithm, which scans the future on every fault. */
    printf("\nrun time on the 90%%-locality string, 4 frames\n");
    struct { const char *name; long (*fn)(const int *, int, int); int n; int len; } algos[] = {
        {"FIFO",    fifo,      REFS,     0},
        {"LRU",     lru,       REFS,     0},
        {"Clock",   clock_algo, REFS,    0},
        {"Optimal", optimal,   OPT_REFS, 0}
    };
    for (int a = 0; a < 4; a++) {
        const int *ref = (algos[a].fn == optimal) ? loc_opt : loc_big;
        double t0 = now_ms();
        long f = algos[a].fn(ref, algos[a].n, 4);
        double t1 = now_ms();
        printf("  %-8s %9.3f ms  over %6d refs  (%ld faults, %6.3f us/ref)\n",
               algos[a].name, t1 - t0, algos[a].n, f, (t1 - t0) * 1000.0 / algos[a].n);
    }

    free(loc); free(rnd); free(loc_big); free(loc_opt);
    return 0;
}
