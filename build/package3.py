"""Assemble the Assignment 3 submission folder and ZIP.

Layout mirrors Assignment 2: one folder per task with its source, its output
logs and its screenshots, plus the report, the diagrams and a README.
"""
from __future__ import annotations

import os
import shutil
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work3")
PKG = os.path.join(WORK, "pkg", "CSA0406_Assignment3_Submission")
ZIP = os.path.join(ROOT, "CSA0406_Assignment3_Complete_Submission.zip")

TASKS = {
    "Q1_Linking": {
        "src": ["q1_app.c", "q1_crypto.c", "q1_crypto.h", "q1_tables.c", "q1_dlopen.c", "q1_maps.c"],
        "logs": ["q1_sizes_and_ldd.log", "q1_dlopen.log", "q1_dlopen_missing.log",
                 "q1_library_swap.log", "q1_maps.log", "q1_startup.log",
                 "q1_shared_pages.log"],
        "shots": ["q1_static_shared.png", "q1_dlopen.png", "q1_library_swap.png", "q1_maps.png"],
    },
    "Q2_Paging": {
        "src": ["q2_todo.c", "q2_frag.c", "q2_eat.c", "q2_boundary.c"],
        "logs": ["q2_todo_1024.log", "q2_todo_2048.log", "q2_fragmentation.log",
                 "q2_eat.log", "q2_boundary.log", "q2_pagesize.log"],
        "shots": ["q2_todo.png", "q2_frag.png"],
    },
    "Q3_Segmentation": {
        "src": ["q3_segment.c", "q3_segv.c", "q3_frag.c", "q3_tables.c"],
        "logs": ["q3_segment.log", "q3_segv.log", "q3_fragmentation.log",
                 "q3_tables.log", "q3_maps.log"],
        "shots": ["q3_segment.png", "q3_segv.png"],
    },
    "Q4_VirtualMemory": {
        "src": ["q4_locality.c", "q4_cow.c", "q4_memlimit.c"],
        "logs": ["q4_locality.log", "q4_cow.log", "q4_memlimit.log"],
        "shots": ["q4_memlimit.png"],
    },
    "Q5_Replacement": {
        "src": ["q5_todo.c", "q5_replace.c"],
        "logs": ["q5_todo.log", "q5_replace.log"],
        "shots": ["q5_replace.png"],
    },
    "Q6_Disk": {
        "src": ["q6_raid.c", "q6_readspeed.c"],
        "logs": ["q6_raid.log", "q6_readspeed.log"],
        "shots": ["q6_raid.png"],
    },
    "Q7_Plan": {
        "src": ["q7_mlock.c", "q7_sim.c"],
        "logs": ["q7_mlock_off.log", "q7_mlock_on.log", "q7_sim.log"],
        "shots": ["q7_mlock.png"],
    },
}

README = """# CSA0406 - Operating Systems - Assignment 3 (CO3)

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
gcc -std=c11 -O2 -fPIC -shared q1_crypto.c q1_tables.c -o libcrypto.dll \\
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
"""

CHECKLIST = """CSA0406 Assignment 3 - Submission Checklist

[X] Every task executed and its output captured in Output/
[X] Every task has the C source in Source_Code/
[X] Screenshots of the real runs in Screenshots/
[X] Complete-the-Code programs (Q2 TODO 1, Q5 TODO 1) finished and run
[X] Outputs compared with the expected outputs in the question paper
[X] Diagrams for paging, segmentation, page faults, RAID and the Q7 plan
[X] Measurements quoted from logs, not estimated
[X] Platform limitations stated (MSYS2 page size, fault counters, fork)
[X] README with name, register number, compiler, OS, build commands
[X] Report with theory, code, output, evaluation, complexity and conclusion
"""


def copy(src_dir, dst_dir, names):
    os.makedirs(dst_dir, exist_ok=True)
    for n in names:
        s = os.path.join(src_dir, n)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst_dir, n))
        else:
            print("  missing:", s)


def main():
    if os.path.isdir(os.path.join(WORK, "pkg")):
        shutil.rmtree(os.path.join(WORK, "pkg"))
    os.makedirs(PKG, exist_ok=True)

    copy(os.path.join(WORK, "diagrams"), os.path.join(PKG, "Diagrams"),
         sorted(os.listdir(os.path.join(WORK, "diagrams"))))
    copy(os.path.join(WORK, "logs"), os.path.join(PKG, "All_Logs"),
         [n for n in sorted(os.listdir(os.path.join(WORK, "logs"))) if n.endswith(".log")])

    for task, spec in TASKS.items():
        base = os.path.join(PKG, task)
        copy(os.path.join(WORK, "src"), os.path.join(base, "Source_Code"), spec["src"])
        copy(os.path.join(WORK, "logs"), os.path.join(base, "Output"), spec["logs"])
        copy(os.path.join(WORK, "shots"), os.path.join(base, "Screenshots"), spec["shots"])

    rep = os.path.join(PKG, "01_Final_Report")
    os.makedirs(rep, exist_ok=True)
    for name in ("Assignment_3_Final_Report.docx", "Assignment_3_Final_Report.pdf"):
        s = os.path.join(ROOT, name)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(rep, name))

    with open(os.path.join(PKG, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)
    with open(os.path.join(PKG, "Submission_Checklist.txt"), "w", encoding="utf-8") as f:
        f.write(CHECKLIST)

    count = 0
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dirpath, _, files in os.walk(PKG):
            for name in files:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, os.path.dirname(PKG))
                z.write(full, rel.replace("\\", "/"))
                count += 1
    size = os.path.getsize(ZIP)
    print(f"packaged {count} files, {size/1e6:.2f} MB -> {ZIP}")

    # integrity check
    with zipfile.ZipFile(ZIP) as z:
        bad = z.testzip()
        print("zip entries:", len(z.namelist()), "corrupt:", bad)


if __name__ == "__main__":
    main()
