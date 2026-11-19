/* q1_app.c - the branch application. It is compiled twice, once against the
 * static archive and once against the shared object, without changing a line.
 */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "q1_crypto.h"

#define RECORD_LEN 2000000UL   /* 2 MB of "customer records" */

static unsigned char records[RECORD_LEN];

int main(void)
{
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (size_t i = 0; i < RECORD_LEN; i++)
        records[i] = (unsigned char)(i * 31u + 7u);

    unsigned long before = crypto_checksum(records, RECORD_LEN);
    crypto_encrypt(records, RECORD_LEN);
    unsigned long after = crypto_checksum(records, RECORD_LEN);

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double work_ms = (t1.tv_sec - t0.tv_sec) * 1e3 +
                     (t1.tv_nsec - t0.tv_nsec) / 1e6;

    printf("library version : %s\n", crypto_version());
    printf("records         : %lu bytes\n", RECORD_LEN);
    printf("checksum before : %lu\n", before);
    printf("checksum after  : %lu\n", after);
    printf("encrypt time    : %.3f ms\n", work_ms);
    return 0;
}
