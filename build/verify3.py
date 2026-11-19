"""Verify that every headline number quoted in the report appears in a log.

Run before building the document:  python build/verify3.py
Exit status 0 means the report's claims are backed by real program output.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
LOGS = os.path.join(WORK, "logs")

# (log file, text that must appear, description)
CLAIMS = [
    ("q1_sizes_and_ldd.log", "8419909 bin/q1_app_static.exe", "static executable size"),
    ("q1_sizes_and_ldd.log", "30529 bin/q1_app_shared.exe", "shared executable size"),
    ("q1_sizes_and_ldd.log", "8406082 bin/libcrypto.dll", "shared library size"),
    ("q1_startup.log", "q1_app_static: 434998 us", "static start-up mean"),
    ("q1_startup.log", "q1_app_shared: 203723 us", "shared start-up mean"),
    ("q1_library_swap.log", "library version : 2.0", "library swapped to 2.0"),
    ("q1_dlopen_missing.log", "exit=2", "missing library exit code"),
    ("q2_todo_1024.log", "2049 -> page 2 offset 1 : page fault", "TODO expected output"),
    ("q2_todo_2048.log", "9000 -> page 4 offset 808 : physical 808", "2048-byte page recompute"),
    ("q2_fragmentation.log", "14.97%", "2 MB internal fragmentation"),
    ("q2_boundary.log", "SIGSEGV", "read past the mapping faults"),
    ("q3_segment.log", "SEGMENTATION FAULT (offset 65536 >= limit 65536)", "limit check"),
    ("q3_fragmentation.log", "84.35%", "external fragmentation"),
    ("q3_fragmentation.log", "allocating 6 MB after the removals: FAILED", "6 MB cannot fit"),
    ("q3_tables.log", "4194304", "flat page table size"),
    ("q4_locality.log", "sequential faults", "locality run"),
    ("q4_memlimit.log", "1024 MB", "working set growth"),
    ("q5_todo.log", "3 frames: FIFO 15, LRU 12, Optimal 9", "TODO expected output"),
    ("q5_replace.log", "FIFO 3 frames 9, 4 frames 10 faults", "Belady with FIFO"),
    ("q5_replace.log", "LRU  3 frames 10, 4 frames 8 faults", "no Belady with LRU"),
    ("q6_raid.log", "RAID 5       20.0 TB", "RAID 5 capacity"),
    ("q6_raid.log", "0.054783%", "RAID 5 loss risk in 24 h"),
    ("q6_readspeed.log", "1358.3 MB/s", "SSD read throughput"),
    ("q7_mlock_off.log", "worst case      :     2941.9 us", "unlocked worst case"),
    ("q7_mlock_on.log", "worst case      :     1793.9 us", "locked worst case"),
    ("q7_sim.log", "faults    2846", "ML faults with the fourth task"),
]


def main() -> int:
    failures = []
    for name, needle, description in CLAIMS:
        path = os.path.join(LOGS, name)
        if not os.path.exists(path):
            failures.append(f"{description}: log {name} is missing")
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if needle not in text:
            failures.append(f"{description}: '{needle}' not found in {name}")

    for f in failures:
        print("FAIL:", f)
    print(f"{len(CLAIMS) - len(failures)}/{len(CLAIMS)} claims verified against the logs")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
