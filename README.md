# CSA0406 - Operating Systems - Assignment 3 (CO3)

**Student:** Sheshuraaj D
**Register number:** 1965260024
**Department:** CSE - Cybersecurity, 1st Year
**Faculty:** Dr. JAYASAKTHI VELMURUGAN K
**Submitted:** 14/11/2026

Evaluate and justify memory-management designs: linking and loading, paging,
segmentation, virtual memory, page replacement, disk management, and a
memory-management plan for an edge device.

## Compiler and platform

| Item | Value |
|---|---|
| Compiler | gcc (GCC) 16.2.0 from MSYS2 |
| Command | `gcc -std=c11 -Wall -Wextra -O2` (plus `-lpsapi -lm` where used) |
| Operating system | Windows 11 (x86-64), POSIX programs run on the MSYS2 runtime |
| Python for the report | 3.12.10 + python-docx + matplotlib |

All programs compile warnings-clean with `-Wall -Wextra`.

## How to build and run

```bash
export PATH=/d/FREEBUFF/tools/msys64/usr/bin:$PATH
cd work3
bash run_all.sh          # compiles nothing, runs everything, writes logs/
```

To rebuild the Q1 library variants:

```bash
cd src
gcc -std=c11 -O2 -c q1_crypto.c -o q1_crypto.o
gcc -std=c11 -O2 -c q1_tables.c -o q1_tables.o
ar rcs libcrypto.a q1_crypto.o q1_tables.o
gcc -std=c11 -O2 -fPIC -shared q1_crypto.c q1_tables.c -o libcrypto.dll \
    -Wl,--out-implib=libcrypto.dll.a
gcc -std=c11 -Wall -Wextra -O2 q1_app.c libcrypto.a        -o ../bin/q1_app_static.exe
gcc -std=c11 -Wall -Wextra -O2 q1_app.c -L. -lcrypto       -o ../bin/q1_app_shared.exe
```

## Task folders

| Folder | Contents | Result |
|---|---|---|
| `Q1_Linking` | static vs shared build, dlopen, /proc/self/maps | 8,419,909 B static vs 30,529 B + 8,406,082 B shared; start-up 435 ms vs 204 ms; library swapped 1.0 -> 2.0 without recompiling |
| `Q2_Paging` | completed TODO 1, fragmentation, EAT, page boundaries | output matches the expected output exactly; internal waste 0.01 / 0.03 / 14.97 % for 1 KB / 4 KB / 2 MB pages |
| `Q3_Segmentation` | segment table, real SIGSEGV, fragmentation, table sizes | limit violation caught at offset == limit; external fragmentation 84.35 %; 6 MB request fails while 5 MB succeeds |
| `Q4_VirtualMemory` | locality, copy-on-write, growing working set | 16,438 faults sequential vs 16,432 random; random pass 20 % slower for identical work |
| `Q5_Replacement` | completed TODO 1, FIFO/LRU/Optimal/Clock, 3-10 frames | matches the expected output; Belady reproduced with FIFO (9 -> 10 faults) and absent for LRU (10 -> 8) |
| `Q6_Disk` | RAID capacity and loss model, read throughput | 24/12/20/16/12 TB for RAID 0/1/5/6/10; loss risk in 24 h 0.011 % RAID 10 vs 0.055 % RAID 5; SSD read 1,184-1,358 MB/s |
| `Q7_Plan` | mlock latency, three-task simulator | worst case 2,941.9 us -> 1,793.9 us with mlock; adding a 500 MB task raises ML faults 1,500 -> 2,846 |

## Honest platform notes

* `sysconf(_SC_PAGESIZE)` returns 65536 under MSYS2; Windows pages are 4 KB and
  all assignment arithmetic uses 4 KB.
* `getrusage()` reports no page faults on this runtime, so fault counts come
  from `GetProcessMemoryInfo` (`PageFaultCount`).
* MSYS2 emulates `fork()` by copying, so the copy-on-write experiment shows
  duplication rather than sharing; the output is reported as measured.

## Report

`01_Final_Report/Assignment_3_Final_Report.docx` and `.pdf`.
