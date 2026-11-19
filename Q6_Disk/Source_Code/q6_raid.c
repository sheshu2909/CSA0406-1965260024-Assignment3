/* q6_raid.c - usable capacity of 6 disks of 4 TB at each RAID level, and
 * the probability that a second disk fails during the rebuild window.
 *
 * Rebuild model: after one disk fails the array is exposed until the spare is
 * rebuilt. With an annualised failure rate AFR per disk, the chance a given
 * disk fails during T hours is p = AFR * T / 8760. For n surviving disks the
 * chance that none fails is (1-p)^n, so p(data loss) = 1 - (1-p)^n.
 */
#include <stdio.h>
#include <math.h>

#define DISKS   6
#define DISK_TB 4.0

static void row(const char *name, double usable_tb, double overhead,
                const char *faults, const char *rd, const char *wr)
{
    printf("%-8s %8.1f TB %8.1f%%  %-26s %-18s %s\n",
           name, usable_tb, overhead * 100.0, faults, rd, wr);
}

int main(void)
{
    double total = DISKS * DISK_TB;

    printf("%d disks of %.0f TB = %.0f TB raw\n\n", DISKS, DISK_TB, total);
    printf("%-8s %11s %9s  %-26s %-18s %s\n",
           "RAID", "usable", "overhead", "survives", "read", "write");
    row("RAID 0",  total,                0.0,
        "no disk failure", "6x striped", "6x striped");
    row("RAID 1",  total / 2.0,          0.5,
        "1 disk (mirror pair)", "3x", "3x");
    row("RAID 5",  total - DISK_TB,      1.0 / DISKS,
        "1 disk (single parity)", "5x", "1x + parity update");
    row("RAID 6",  total - 2 * DISK_TB,  2.0 / DISKS,
        "2 disks (dual parity)", "4x", "2x + dual parity");
    row("RAID 10", total / 2.0,          0.5,
        "1 per mirror pair", "3x", "3x");

    const double afr = 0.04;                 /* 4 % per disk per year */
    const double hours[] = {6.0, 24.0, 48.0};
    const char *names[] = {"RAID 1", "RAID 5", "RAID 6", "RAID 10"};
    /* surviving disks that must all stay alive for the array to survive */
    int ns[] = {1, DISKS - 1, DISKS - 2, 1};

    printf("\nprobability of losing data during a rebuild, AFR %.0f%%/year\n",
           afr * 100.0);
    printf("%-8s %9s %13s %13s %13s\n",
           "RAID", "disks n", "6 h", "24 h", "48 h");
    for (int a = 0; a < 4; a++) {
        printf("%-8s %9d", names[a], ns[a]);
        for (int h = 0; h < 3; h++) {
            double p = afr * hours[h] / 8760.0;
            printf(" %12.6f%%", 100.0 * (1.0 - pow(1.0 - p, ns[a])));
        }
        printf("\n");
    }

    printf("\nwith 6 disks the array sees roughly 6x the failure rate of one\n"
           "disk, and the rebuild window is when the second failure hurts.\n");
    return 0;
}
