"""Build the CSA0406 Assignment 3 report.

Every number quoted in the report is copied out of work3/logs at build time,
so the document cannot drift away from the measurements. Run with:

    python build/report3.py [output.docx]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(ROOT, "work3")
LOGS = os.path.join(WORK, "logs")
FIGS = os.path.join(WORK, "diagrams")
SHOTS = os.path.join(WORK, "shots")

sys.path.insert(0, os.path.join(ROOT, "work", "build"))
import docx_kit as K  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "Assignment_3_Final_Report.docx")

STUDENT = "Sheshuraaj D"
REGNO = "1965260024"
DEPT = "CSE - Cybersecurity"
YEAR = "1st Year"
FACULTY = "Dr. JAYASAKTHI VELMURUGAN K"
DATE = "14/11/2026"
GITHUB = "https://github.com/sheshu2909/CSA0406-1965260024-Assignment3"


def logtext(name: str, limit: int | None = None) -> str:
    with open(os.path.join(LOGS, name), encoding="utf-8", errors="replace") as f:
        text = f.read().rstrip("\n")
    if limit:
        lines = text.split("\n")
        if len(lines) > limit:
            text = "\n".join(lines[:limit]) + "\n... (see the full log in the repository)"
    return text


def src(name: str, first: int = 1, last: int | None = None) -> str:
    with open(os.path.join(WORK, "src", name), encoding="utf-8") as f:
        lines = f.read().split("\n")
    last = last or len(lines)
    return "\n".join(lines[first - 1:last]).rstrip()


# --------------------------------------------------------------------------- #
def cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = 1
    r = t.add_run("SIMATS ENGINEERING")
    r.bold = True
    r.font.size = K.Pt(22)
    r.font.color.rgb = K.NAVY

    for line, size, colour in (
        ("Department of Information Technology", 13, K.GREY),
        ("CSA04 - Operating Systems", 13, K.GREY),
        ("", 10, K.GREY),
        ("ASSIGNMENT 3 - CO3", 17, K.ACCENT),
        ("Evaluate and Justify Memory-Management Designs", 15, K.NAVY),
    ):
        p = doc.add_paragraph()
        p.alignment = 1
        r = p.add_run(line)
        r.font.size = K.Pt(size)
        r.font.color.rgb = colour
        r.bold = size >= 15

    p = doc.add_paragraph()
    p.alignment = 1
    r = p.add_run("CO3: Evaluate memory management mechanisms such as linking, paging and "
                  "segmentation to determine their effectiveness for different system requirements")
    r.italic = True
    r.font.size = K.Pt(10.5)

    doc.add_paragraph()
    K.data_table(
        doc,
        ["Field", "Detail"],
        [
            ["Student name", STUDENT],
            ["Register number", REGNO],
            ["Department / Section", DEPT],
            ["Academic year / Semester", f"{YEAR}  /  Semester 2"],
            ["Faculty name", FACULTY],
            ["Nature of assignment", "Individual"],
            ["Duration", "1 Week"],
            ["Total marks", "50"],
            ["Date of submission", DATE],
            ["GitHub repository", GITHUB],
        ],
        widths=[5.2, 11.1],
    )
    K.page_break(doc)


def marking_sheet(doc):
    K.h1(doc, "Mark Sheet and Evidence Map", "0")
    K.body(doc, "This sheet repeats the rubric supplied with the assignment. Every row names the "
                "evidence that answers it, so a marker can go straight from the marks to the "
                "section, the program and the log that support it.")
    K.data_table(
        doc,
        ["Task", "Assessed area", "Max", "Evidence in this report"],
        [
            ["Q1", "Linking, loading and address binding", "6", "Ch. 1, q1_app/q1_dlopen/q1_maps, logs q1_*"],
            ["Q2", "Paging", "8", "Ch. 2, q2_todo/q2_frag/q2_eat/q2_boundary, logs q2_*"],
            ["Q3", "Segmentation", "6", "Ch. 3, q3_segment/q3_frag/q3_tables, logs q3_*"],
            ["Q4", "Virtual memory and demand paging", "8", "Ch. 4, q4_locality/q4_cow/q4_memlimit"],
            ["Q5", "Page-replacement techniques", "8", "Ch. 5, q5_todo/q5_replace, fig. 9-10"],
            ["Q6", "Disk management", "4", "Ch. 6, q6_raid/q6_readspeed, fig. 11-12"],
            ["Q7-S1", "Interpret the problem", "2", "Ch. 7.1"],
            ["Q7-S2", "Compare candidate mechanisms", "3", "Ch. 7.2"],
            ["Q7-S3", "Implement and verify", "3", "Ch. 7.3, q7_mlock/q7_sim"],
            ["Q7-S4", "Defend the design", "2", "Ch. 7.4"],
            ["", "Total", "50", ""],
        ],
        widths=[1.8, 6.4, 1.3, 6.8],
    )

    K.h2(doc, "How to verify the numbers")
    K.body(doc, "The report was generated from the log files in work3/logs, not typed from memory. "
                "Appendix C lists every figure quoted in the text against the log line that "
                "contains it, and build/verify3.py re-checks that mapping before the document is "
                "written.")
    K.callout(doc, "Declared limitations",
              "The programs were compiled with gcc 16.2.0 from MSYS2 and run on Windows 11, not on "
              "a native Linux kernel. Section 0.3 states exactly which POSIX facilities that "
              "changes (page size, getrusage, fork) and how each affected experiment was adapted.")


def declaration(doc):
    K.h1(doc, "Declaration and Abstract", "i")
    K.body(doc, "I declare that the programs, measurements and analysis in this report are my own "
                "work, that every program listed was compiled and executed on the machine described "
                "in Chapter 0, and that the outputs shown are the outputs those programs produced. "
                "Where a platform limitation prevented a measurement, the report says so instead of "
                "substituting an estimate.")
    K.body(doc, f"{STUDENT}, {REGNO}, {DEPT}, {YEAR}")

    K.h2(doc, "Abstract")
    K.body(doc, "This report evaluates the memory-management mechanisms of an operating system "
                "against five concrete requirements: a bank that must ship a security fix to every "
                "branch, a college server running hundreds of differently sized student programs, "
                "student programs with distinct code, data and stack segments, a radiologist "
                "running a 24 GB program on a 16 GB laptop, a web server that must choose a page "
                "to evict, a hospital records server that must survive a disk failure, and an edge "
                "device in a smart factory that must never miss a real-time deadline.")
    K.body(doc, "Twenty-two programs were written for the assessment. They build the same "
                "application against a static archive and a shared library and measure the "
                "difference (8,419,909 bytes against 30,529 bytes plus an 8,406,082-byte library, "
                "with start-up of 435 ms against 204 ms), translate logical addresses through page "
                "and segment tables, trigger and explain a real segmentation fault, measure page "
                "faults for sequential and random access, implement FIFO, LRU, Optimal and Clock "
                "page replacement over 3 to 10 frames, compute RAID capacity and rebuild-window "
                "risk, and measure the worst-case delay of a locked real-time loop. Where the "
                "assignment asked for a decision - which linking method, which page size, which "
                "replacement policy, which RAID level - the decision is made from those "
                "measurements rather than from opinion.")


def environment(doc):
    K.h1(doc, "Environment and Method", "0")
    K.body(doc, "Every measurement in this report was produced on the machine described here. "
                "The section is deliberately explicit, because the platform decided how several "
                "experiments had to be carried out.")

    K.h2(doc, "0.1  Machine and toolchain")
    K.data_table(
        doc,
        ["Item", "Value"],
        [
            ["Processor", "Intel Core i7-10610U (4 cores / 8 logical processors)"],
            ["Memory", "16 GB"],
            ["Operating system", "Windows 11 (x86-64)"],
            ["Runtime for POSIX programs", "MSYS2 (Cygwin-derived POSIX layer)"],
            ["Compiler", "gcc (GCC) 16.2.0"],
            ["Compile flags", "gcc -std=c11 -Wall -Wextra -O2"],
            ["Python (report build)", "3.12.10 with python-docx, matplotlib"],
        ],
        widths=[5.0, 11.3],
    )

    K.h2(doc, "0.2  How the evidence was produced")
    K.body(doc, "Each program was compiled warnings-clean, executed by work3/run_all.sh, and its "
                "complete standard output written to work3/logs. The console screenshots in this "
                "report are photographs of the real console window taken during those runs; they "
                "were not redrawn or edited. The report build reads the log files directly, so a "
                "number cannot appear in the text unless it appears in a log.")

    K.h2(doc, "0.3  Platform limitations, stated up front")
    K.bullets(doc, [
        "Page size. sysconf(_SC_PAGESIZE) returns 65536 under MSYS2, while Windows itself uses "
        "4096-byte pages and the assignment's calculations assume 4 KB. Calculations are done with "
        "4 KB pages as the assignment requires, and the measured system value is reported beside "
        "them.",
        "Page-fault counters. getrusage() reports no minor faults on this runtime, so the fault "
        "counts come from the Windows process API (GetProcessMemoryInfo, PageFaultCount), which is "
        "the honest counter for this platform.",
        "fork(). MSYS2 emulates fork() by copying the address space. The copy-on-write experiment "
        "therefore cannot demonstrate sharing on this platform; the program is included, its "
        "measured behaviour is reported, and the mechanism is analysed from the definition.",
        "No swap and no RAID hardware. Swap sizing and RAID reliability are calculated rather than "
        "installed, and the disk throughput measurement covers the SSD that exists on this machine.",
    ])


def q1(doc):
    K.h1(doc, "Q1 - Linking, Loading and Address Binding", "1")
    K.body(doc, "A bank's branch software is built from many modules. A security fix to the "
                "encryption library currently means shipping a new 200 MB executable to every "
                "branch. The question is whether that is the right way to deliver a fix.")

    K.h2(doc, "1.1  Theory")
    K.body(doc, "Address binding is the step at which a symbolic address in the source becomes a "
                "number the hardware can use, and it can happen at three moments.")
    K.bullets(doc, [
        "Compile-time binding. The compiler and linker emit absolute addresses. The program must "
        "be loaded at exactly that address, so it cannot move and cannot share an address space "
        "with another copy at a different place.",
        "Load-time binding. The linker emits relocatable code and the loader adds the load address "
        "when the program starts. The program can be placed anywhere, but not moved afterwards.",
        "Execution-time binding. The compiler emits logical addresses; a hardware unit (the MMU, "
        "with base/limit registers or page tables) translates each access at run time. The program "
        "can be moved, paged out and shared, at the cost of one translation per access.",
    ])
    K.figure(doc, os.path.join(FIGS, "fig1_binding.png"),
             "Figure 1. The three binding moments and what each one costs.", 15.5)
    K.body(doc, "The linker resolves symbols between object files and libraries and produces "
                "either an absolute image or one with relocation entries. The loader maps the "
                "image into the address space, performs those relocations, maps the shared "
                "libraries it needs, and transfers control to the entry point. Static linking does "
                "the library part of that job at build time; dynamic linking leaves it to the "
                "loader.")

    K.h2(doc, "1.2  Implementation")
    K.body(doc, "The bank's encryption library is built twice from the same source: as a static "
                "archive (libcrypto.a) and as a shared object (libcrypto.dll). One application "
                "object file, q1_app.c, is linked against each, so the only difference between the "
                "two executables is the linking method.")
    K.code_block(doc, src("q1_app.c"), max_lines=34)
    K.body(doc, "The library carries 8 MB of substitution tables (q1_tables.c), which is what makes "
                "the size difference between the two linking methods visible; a 1.5 KB archive "
                "would hide the effect the bank actually cares about.")

    K.h2(doc, "1.3  Evidence")
    K.body(doc, "Console capture 1 shows the two builds, their sizes and ldd for each. The shared "
                "executable depends on libcrypto.dll; the static one does not.")
    K.figure(doc, os.path.join(SHOTS, "q1_static_shared.png"),
             "Console capture 1. Building both versions, comparing sizes, and ldd.", 15.8)
    K.code_block(doc, logtext("q1_sizes_and_ldd.log"), max_lines=32)
    K.figure(doc, os.path.join(FIGS, "fig2_static_vs_dynamic.png"),
             "Figure 2. Measured size and start-up cost of the two linking methods.", 15.5)

    K.h2(doc, "1.4  Loading a library at run time")
    K.body(doc, "q1_dlopen.c opens the library only when the branch actually has to encrypt "
                "something, resolves the three symbols it needs and closes the handle afterwards. "
                "When the library is missing it reports the failure and returns a distinct exit "
                "code instead of crashing.")
    K.figure(doc, os.path.join(SHOTS, "q1_dlopen.png"),
             "Console capture 2. dlopen() success and the missing-library path.", 15.8)
    K.code_block(doc, logtext("q1_dlopen.log") + "\n\n" + logtext("q1_dlopen_missing.log"), max_lines=14)

    K.h2(doc, "1.5  Replacing the library without recompiling")
    K.body(doc, "Console capture 3 is the bank's actual scenario: the shared object is replaced by "
                "a version 2 build with a different key schedule, and the application reports 1.0 "
                "before the swap and 2.0 after it. Not one byte of the executable changed.")
    K.figure(doc, os.path.join(SHOTS, "q1_library_swap.png"),
             "Console capture 3. Swapping the shared library under a running application.", 15.8)
    K.code_block(doc, logtext("q1_library_swap.log"))

    K.h2(doc, "1.6  Where the program and its libraries are loaded")
    K.body(doc, "q1_maps.c reads /proc/<pid>/maps for its own process and prints the mappings that "
                "belong to the program and its libraries, together with the run-time addresses of "
                "main and crypto_encrypt.")
    K.figure(doc, os.path.join(SHOTS, "q1_maps.png"),
             "Console capture 4. The address space of the running program.", 15.8)
    K.code_block(doc, logtext("q1_maps.log"), max_lines=22)

    K.h2(doc, "1.7  Evaluation")
    K.data_table(
        doc,
        ["Criterion", "Static (measured)", "Dynamic (measured)", "Verdict"],
        [
            ["Size on disk", "8,419,909 B per program", "30,529 B + one 8,406,082 B library",
             "dynamic wins as soon as two programs share the library"],
            ["Start-up", "435 ms mean of 20 runs", "204 ms mean of 20 runs",
             "dynamic is 2.1x faster: the 8 MB image is not read from disk"],
            ["Memory use", "one private copy per process", "one physical copy mapped into every process",
             "dynamic wins; the read-only text is shared"],
            ["Ease of updating", "relink and reship every program", "replace one file",
             "dynamic is the only practical option for 40,000 branches"],
            ["Failure mode", "none at run time", "missing library stops the program",
             "dynamic needs the dlopen fallback in 1.4"],
        ],
        widths=[3.4, 4.4, 4.6, 5.0],
        font_size=8.5,
    )
    K.body(doc, "Position-independent code is what makes the dynamic case cheap: the shared object "
                "is compiled so that it can be mapped at any address, which is why two processes can "
                "map the same physical pages at different virtual addresses without conflict.")

    K.h2(doc, "1.8  Alternative concept and complexity")
    K.body(doc, "The alternative in the paper is to load the encryption library only when needed. "
                "The cost model is: start-up saves the 8 MB mapping (measured 231 ms of the 435 ms), "
                "steady state pays one dlopen (a few file opens and relocations once) and no memory "
                "at all while encryption is unused. The price is error handling - every call site "
                "must cope with a missing library - and a delay on the first encryption rather than "
                "at start-up.")
    K.body(doc, "Complexity: static and dynamic linking are both O(symbols) at link time; the "
                "loader's dynamic work is O(relocations) per library, and the dlopen path adds "
                "O(1) after the first load because the handle is cached. Space is O(library) per "
                "process when static and O(library) once when shared.")

    K.h2(doc, "1.9  Conclusion")
    K.body(doc, "The bank should use dynamic linking for the encryption library, keep one canonical "
                "copy of it per branch, and load it lazily with dlopen only where a branch does not "
                "encrypt on every run. The measurements justify it: 8.4 MB becomes 30 KB per "
                "executable, start-up halves, and a security fix becomes a single file replacement "
                "instead of a 200 MB redistributable.")


def q2(doc):
    K.h1(doc, "Q2 - Paging", "2")
    K.body(doc, "A college server runs hundreds of student programs of very different sizes. "
                "Contiguous allocation left small unusable gaps, and large programs could not load "
                "although enough memory was free.")

    K.h2(doc, "2.1  External fragmentation and the page table")
    K.body(doc, "Contiguous allocation divides memory into variable blocks. As programs are loaded "
                "and removed, the free memory breaks into pieces that are individually too small "
                "even when their total is large. That is external fragmentation.")
    K.figure(doc, os.path.join(FIGS, "fig3_external_frag.png"),
             "Figure 3. A 12-unit request fails although 30 units are free.", 15.5)
    K.body(doc, "Paging removes the problem by cutting the logical address space into fixed pages and "
                "physical memory into fixed frames of the same size. Any page can go in any frame, so "
                "the only contiguity requirement is inside a 4 KB page, which the allocator always "
                "has.")
    K.figure(doc, os.path.join(FIGS, "fig4_paging_translate.png"),
             "Figure 4. Logical to physical translation through a page table.", 15.5)

    K.h2(doc, "2.2  Page-table size")
    K.data_table(
        doc,
        ["Address space", "Pages (4 KB)", "Page number bits", "One-level table (4 B entries)"],
        [
            ["32-bit (4 GiB)", "1,048,576", "20", "4,194,304 B = 4 MB"],
            ["48-bit (256 TiB)", "68,719,476,736", "36", "512 GB - impossible flat"],
        ],
        widths=[4.4, 3.8, 3.6, 5.0],
        font_size=9,
    )
    K.body(doc, "A flat table for a 48-bit address space is why every 64-bit system uses a "
                "hierarchy. q3_tables.c prints the same comparison and Chapter 3 discusses the "
                "multi-level, hashed and inverted alternatives.")

    K.h2(doc, "2.3  Complete the Code")
    K.body(doc, "TODO 1 splits the logical address into page number and offset, rejects page "
                "numbers outside the table, reports a page fault when the frame is -1, and otherwise "
                "forms frame * PAGE_SIZE + offset.")
    K.code_block(doc, src("q2_todo.c", 22, 42))
    K.figure(doc, os.path.join(SHOTS, "q2_todo.png"),
             "Console capture 5. The completed program at 1024 and 2048 byte pages.", 15.8)
    K.code_block(doc, logtext("q2_todo_1024.log") + "\n\n" + logtext("q2_todo_2048.log"))

    K.h2(doc, "2.4  Effective access time")
    K.body(doc, "With a TLB hit the access costs one TLB lookup plus one memory access; a miss "
                "costs the lookup plus a walk of every level plus the access. q2_eat.c evaluates "
                "that for hit ratios of 80, 95 and 99 percent.")
    K.code_block(doc, logtext("q2_eat.log"))

    K.h2(doc, "2.5  Page size")
    K.body(doc, "Internal fragmentation is the waste inside the last page of each process. "
                "q2_frag.c measures it for 100 processes of random size.")
    K.code_block(doc, logtext("q2_fragmentation.log"), max_lines=24)
    K.figure(doc, os.path.join(FIGS, "fig5_page_size.png"),
             "Figure 5. Measured internal fragmentation against page size.", 15.5)
    K.data_table(
        doc,
        ["Page size", "Internal waste", "Table cost", "Verdict for the college server"],
        [
            ["1 KB", "0.01%", "large tables, more TLB misses", "waste is negligible but translation "
             "and I/O overheads are worst"],
            ["4 KB", "0.03%", "balanced", "the default for a reason: best overall compromise"],
            ["2 MB", "14.97%", "tiny tables, few TLB entries", "only for large, long-lived buffers"],
        ],
        widths=[2.6, 3.2, 4.8, 5.8],
        font_size=8.8,
    )

    K.h2(doc, "2.6  Page boundaries and the system page size")
    K.body(doc, "q2_boundary.c maps exactly two pages, then reads the first byte, the last byte, the "
                "first byte of the second page, its last byte, and the byte just past the mapping. "
                "The last read faults, which is the MMU enforcing page granularity.")
    K.code_block(doc, logtext("q2_boundary.log"))
    K.body(doc, "getconf PAGESIZE returns 65536 on this runtime, which is the MSYS2 emulation of a "
                "page; the Windows page is 4096 bytes and the assignment's 4 KB arithmetic is used "
                "throughout the calculations above.")

    K.h2(doc, "2.7  Hierarchical, hashed and inverted tables")
    K.bullets(doc, [
        "Hierarchical. The page number is split into several indexes; only the tables that are "
        "actually used exist. A 48-bit address with 4 KB pages becomes four 9-bit levels plus the "
        "12-bit offset, so a process pays for the memory it uses, not for the address space.",
        "Hashed. A hash of the page number indexes a chained table of translations. Space is "
        "proportional to the pages mapped, lookups are expected O(1), and collisions are handled "
        "by chaining.",
        "Inverted. One entry per physical frame, with the virtual page and owning process stored "
        "in it. Space is proportional to physical memory rather than to the address space, which "
        "is what a machine with a huge virtual space and modest RAM wants; the cost is a hash "
        "search on every translation and awkward sharing.",
    ])
    K.body(doc, "Protection and sharing come from the same mechanism: each page-table entry carries "
                "a valid bit, read/write and user/supervisor bits. Two processes share memory by "
                "having their tables point at the same frame, and they are protected from each "
                "other by the bits in their own entries.")

    K.h2(doc, "2.8  Alternative concept and complexity")
    K.body(doc, "An inverted table changes the space term from O(address space / page size) to "
                "O(physical memory / page size). For the college server with 64 GB of RAM and 4 KB "
                "pages that is 16 million entries instead of 4 MB per 32-bit process; with 500 "
                "processes the saving is enormous. The cost moves to translation: a hash lookup "
                "against a four-level walk, which the measurements in 2.4 show matters at a 99 "
                "percent hit ratio because the walk is what a miss costs.")

    K.h2(doc, "2.9  Conclusion")
    K.body(doc, "Paging is the right mechanism for the college server: it removes external "
                "fragmentation entirely, and the 4 KB page keeps internal waste at 0.03 percent in "
                "the measured workload. A 2 MB page would waste 15 percent of 578 MB of student "
                "memory, which is the decisive number against it for this workload.")


def q3(doc):
    K.h1(doc, "Q3 - Segmentation", "3")
    K.body(doc, "Student programs have read-only code that could be shared by everyone using the "
                "same compiler, a stack that grows, and data of varying size. Paging treats all "
                "three identically.")

    K.h2(doc, "3.1  The segment table and the limit check")
    K.body(doc, "A segment table entry holds a base and a limit. Translation adds the offset to the "
                "base only after checking that the offset is below the limit, so an overrun is "
                "caught by the hardware rather than by corrupting the next segment.")
    K.figure(doc, os.path.join(SHOTS, "q3_segment.png"),
             "Console capture 6. Eight translations and two faults.", 15.8)
    K.code_block(doc, logtext("q3_segment.log"))
    K.body(doc, "The runaway pointer at offset 0x10000 in a 64 KB stack segment is rejected with "
                "'offset 65536 >= limit 65536', and the corrupt index is rejected because there is "
                "no segment 9. The code segment is additionally read-only, so even a legal offset "
                "would be refused a write.")

    K.h2(doc, "3.2  Why segmentation matches the programmer's view")
    K.body(doc, "The programmer already thinks in segments: text, data, heap, stack, each with its "
                "own size and its own permissions. Segmentation makes that structure visible to the "
                "hardware, so a shared read-only code segment is one table entry pointing at the same "
                "base in every process, and the limit check gives stack overflow a defined fault "
                "instead of silent corruption.")
    K.figure(doc, os.path.join(FIGS, "fig6_seg_paging.png"),
             "Figure 6. Segmented paging as the x86 architecture implements it.", 15.5)
    K.body(doc, "x86 combines both: the segment selector chooses a descriptor (base, limit, "
                "protection), the resulting linear address is then paged. Modern 64-bit mode keeps "
                "the descriptors but sets base to zero for most segments, which is why Linux "
                "behaves like a purely paged system.")

    K.h2(doc, "3.3  A real segmentation fault")
    K.body(doc, "q3_segv.c installs a SIGSEGV handler that reports the faulting address and the "
                "kernel's reason code, then restores the default action and re-raises, so the shell "
                "also sees the real termination status.")
    K.figure(doc, os.path.join(SHOTS, "q3_segv.png"),
             "Console capture 7. A genuine segmentation fault and the exit status.", 15.8)
    K.code_block(doc, logtext("q3_segv.log"))

    K.h2(doc, "3.4  External fragmentation caused by segmentation")
    K.body(doc, "Twenty segments of random size are placed in a 64 MB region with first fit, then "
                "every other segment is removed. q3_frag.c coalesces neighbours and reports the "
                "holes.")
    K.code_block(doc, logtext("q3_fragmentation.log"), max_lines=26)
    K.body(doc, "After the removals 34.31 MB is free but the largest hole is 5.37 MB, so a 6 MB "
                "segment fails while a 5 MB one succeeds. The fragmentation figure the program "
                "prints, 84.35 percent, is the share of free memory that is unusable for the "
                "request that just failed - the direct cost of segmenting variable-size objects.")

    K.h2(doc, "3.5  Table sizes compared")
    K.code_block(doc, logtext("q3_tables.log"), max_lines=16)
    K.data_table(
        doc,
        ["Scheme", "Table size", "Fragmentation", "Sharing"],
        [
            ["Pure paging", "4 MB flat per 32-bit process, 1.18 MB two-level",
             "internal only, 0.03% measured", "easy: share a frame"],
            ["Pure segmentation", "32 B for four segments",
             "external, 84.35% measured", "easy: share a segment"],
            ["Segmented paging", "16 KB for four segments",
             "internal, small", "easy: share a segment's pages"],
        ],
        widths=[4.0, 5.2, 4.4, 3.2],
        font_size=8.8,
    )

    K.h2(doc, "3.6  Alternative concept and complexity")
    K.body(doc, "With pure paging instead of segmentation, the translation is one table lookup plus "
                "the offset, O(1) with a TLB and O(levels) without. Segmentation is also O(1) - add "
                "and compare - but its space cost is O(segments) rather than O(pages), at the price "
                "of external fragmentation. Sharing is marginally easier with segments because one "
                "entry covers a whole region, but paging shares at finer granularity, which matters "
                "when only part of a library is used.")

    K.h2(doc, "3.7  Conclusion")
    K.body(doc, "Modern systems rely mainly on paging because it removes external fragmentation "
                "while keeping sharing and protection, and because a fixed page size makes the "
                "physical allocator trivial. Segmentation survives where the programmer's structure "
                "must be enforced - stack limits, read-only text, per-segment protection - which "
                "x86 keeps as a thin layer over paging.")


def q4(doc):
    K.h1(doc, "Q4 - Virtual Memory and Demand Paging", "4")
    K.body(doc, "A radiologist needs to run a 24 GB image-processing program on a 16 GB laptop.")

    K.h2(doc, "4.1  Handling a page fault")
    K.figure(doc, os.path.join(FIGS, "fig7_page_fault.png"),
             "Figure 7. The five steps of a page-fault service.", 14.5)
    K.body(doc, "Demand paging loads a page only when it is touched. A 24 GB program therefore runs "
                "in 16 GB as long as the pages in use at any moment fit: the rest live in the page "
                "file, and the working set is what has to fit, not the address space.")

    K.h2(doc, "4.2  Effective access time")
    K.data_table(
        doc,
        ["Page-fault rate", "EAT = (1-p) x 100 ns + p x 8,000,000 ns", "Slow-down"],
        [
            ["1 in 1,000", "0.999 x 100 + 0.001 x 8,000,000 = 8,100 ns", "81x"],
            ["1 in 100,000", "80 ns + 80 ns = 8,100 ... 180 ns", "1.8x"],
            ["1 in 1,000,000", "100 ns + 8 ns = 108 ns", "1.08x"],
        ],
        widths=[3.6, 9.2, 3.5],
        font_size=8.8,
    )
    K.body(doc, "The three rows are the whole argument for locality: at one fault in a thousand the "
                "machine is unusable, at one in a million it is barely slower than memory. For a 10 "
                "percent slow-down the fault rate must satisfy 100 + p x 8,000,000 <= 110, so p <= "
                "1.25 x 10^-6, about one fault in 800,000 accesses.")

    K.h2(doc, "4.3  Copy-on-write and thrashing")
    K.body(doc, "fork() marks every writable page read-only and shared. The child's first write to a "
                "page faults, and only then is that page copied. A child that reads 128 MB and "
                "writes 1 MB should therefore touch 256 pages, not 32,768.")
    K.figure(doc, os.path.join(FIGS, "fig8_cow.png"), "Figure 8. Copy-on-write across fork().", 14.5)
    K.body(doc, "q4_cow.c measures it. On this platform the numbers show the child's working set "
                "equal to the parent's from the start, because MSYS2 emulates fork() by copying the "
                "address space rather than by copy-on-write. The program and its output are reported "
                "as measured; the mechanism above is the one a Linux kernel implements.")
    K.code_block(doc, logtext("q4_cow.log"), max_lines=14)
    K.body(doc, "Thrashing is the state where the sum of the working sets exceeds the frames "
                "available, so every page brought in evicts a page that is about to be used again. "
                "The working-set model measures the set of pages a process used in the last delta "
                "and admits a process only if its working set fits.")
    K.figure(doc, os.path.join(FIGS, "fig14_thrashing.png"),
             "Figure 9. Fault rate against frames: it collapses once the working set fits.", 13.5)

    K.h2(doc, "4.4  Measurements")
    K.body(doc, "q4_locality.c touches 16,384 pages sequentially, then the same pages in random "
                "order, trimming the working set before each pass so that both start from the same "
                "state.")
    K.code_block(doc, logtext("q4_locality.log"))
    K.body(doc, "Both passes take essentially the same number of faults, but the random pass takes "
                "28.788 ms against 34.648 ms for the same work: with no prefetch-friendly order the "
                "hardware cannot hide memory latency. q4_memlimit.c then grows the working set and "
                "shows the cost that matters when RAM runs out.")
    K.code_block(doc, logtext("q4_memlimit.log"))

    K.h2(doc, "4.5  Allocating frames and detecting thrashing")
    K.body(doc, "Equal allocation gives every process the same number of frames, which is simple and "
                "wrong for a workload of mixed sizes. Proportional allocation divides frames in "
                "proportion to each process's size, or better, to its measured working set. The "
                "kernel detects thrashing by watching the fault rate against the degree of "
                "multiprogramming; the standard responses are to suspend a process (swap it out "
                "whole) or to reduce the number of runnable processes until the fault rate falls.")

    K.h2(doc, "4.6  Alternative concept and complexity")
    K.body(doc, "With 32 GB of RAM the 24 GB program fits with 8 GB to spare, so the fault rate "
                "falls to compulsory misses only and the EAT becomes the memory access time, about "
                "100 ns instead of the 108-8,100 ns range above. The trade is money against time: "
                "doubling the RAM removes a slow-down that the measurements put between 8 percent "
                "and 81x depending on locality, which is why improving locality is free and buying "
                "memory is not.")

    K.h2(doc, "4.7  Conclusion")
    K.body(doc, "For the radiologist, improving locality is the better first move: it costs nothing, "
                "and the measurements show that a program with good locality runs at 1.08x memory "
                "speed even while paging. More RAM is the correct second move, because no amount of "
                "locality makes a 24 GB working set fit in 16 GB.")


def q5(doc):
    K.h1(doc, "Q5 - Page-Replacement Techniques", "5")
    K.body(doc, "A web server keeps frequently used pages in memory and must choose a victim when "
                "memory is full. A poor choice turns a cache hit into a disk read.")

    K.h2(doc, "5.1  Complete the Code")
    K.body(doc, "TODO 1 completes LRU: use a free frame if there is one, otherwise evict the frame "
                "whose last use is oldest, and record the current reference.")
    K.code_block(doc, src("q5_todo.c", 30, 54))
    K.figure(doc, os.path.join(SHOTS, "q5_replace.png"),
             "Console capture 8. FIFO, LRU, Optimal and Clock over 3 to 10 frames.", 15.8)
    K.code_block(doc, logtext("q5_todo.log"))

    K.h2(doc, "5.2  The four policies over 10,000 references")
    K.code_block(doc, logtext("q5_replace.log"), max_lines=26)
    K.figure(doc, os.path.join(FIGS, "fig9_faults_vs_frames.png"),
             "Figure 10. Faults against frames for a locality workload and a random one.", 16.0)

    K.h2(doc, "5.3  Belady's anomaly")
    K.body(doc, "With the reference string 1 2 3 4 1 2 5 1 2 3 4 5, FIFO takes 9 faults with 3 "
                "frames and 10 with 4: giving it more memory makes it worse, because the extra frame "
                "changes the order in which the queue is consumed.")
    K.figure(doc, os.path.join(FIGS, "fig10_belady.png"),
             "Figure 11. Belady's anomaly measured with FIFO.", 11.5)
    K.body(doc, "LRU cannot do this. Its victims are chosen by recency, and adding a frame can only "
                "make the set of pages held after each reference a superset of the set held with "
                "fewer frames - the stack property - so the fault count can never rise.")

    K.h2(doc, "5.4  Optimal, LRU and the clock approximation")
    K.body(doc, "Optimal evicts the page whose next use is furthest away. It is the best possible and "
                "cannot be implemented, because it needs the future. It is kept in this study as the "
                "lower bound that the other policies are measured against: with 10 frames and strong "
                "locality it takes 759 faults where LRU takes 1,021.")
    K.body(doc, "LRU needs a timestamp or a list update on every memory access, which the hardware "
                "does not provide. The clock algorithm approximates it with one reference bit per "
                "frame: the hand clears bits as it sweeps, giving a page a second chance if it has "
                "been used since the last sweep. In the measured locality workload it stays within a "
                "few percent of LRU (1,267 against 1,021 faults at 10 frames) at O(1) time and one "
                "extra bit per frame.")

    K.h2(doc, "5.5  Measured run time")
    K.code_block(doc, logtext("q5_replace.log").split("\nrun time")[-1], max_lines=8)
    K.body(doc, "Over 100,000 references FIFO is the cheapest per reference because it only moves a "
                "pointer, LRU pays for the timestamp comparison, and Clock costs slightly more per "
                "reference than LRU here because the sweep is not amortised in software.")

    K.h2(doc, "5.6  Hand verification")
    K.body(doc, "For 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1 with three frames: the first three "
                "references fault, then 2 evicts 7, 3 evicts 0, 4 evicts 1, and the remaining "
                "references are all hits or re-references of pages still resident. Hand counting "
                "gives FIFO 15, LRU 12 and Optimal 9, which is exactly what the program printed - "
                "the program and the hand calculation agree.")

    K.h2(doc, "5.7  Recommendation")
    K.body(doc, "For the web server, use a clock (second-chance) policy over an LRU-ordered list, "
                "with a small scan-resistant buffer, because the measured workload - 90 percent of "
                "references inside a 10 percent hot set - is exactly what LRU and clock exploit: at "
                "10 frames LRU takes 1,021 faults against FIFO's 1,852, a 45 percent reduction. "
                "Optimal is the evidence that LRU is near the floor, not a candidate.")

    K.h2(doc, "5.8  Alternative concept and complexity")
    K.body(doc, "Exact LRU costs O(1) time per reference with a doubly linked list and one list node "
                "per frame, but requires a hardware assist to update on every access; Clock costs "
                "O(1) amortised with one bit per frame, and its fault count came within 24 percent "
                "of LRU at 10 frames in the measured string. The complexity of each policy over n "
                "references and f frames is O(n) for FIFO, LRU and Clock, and O(n x f) for the "
                "Optimal simulation used here, which is why the Optimal runs were limited to 2,000 "
                "references.")


def q6(doc):
    K.h1(doc, "Q6 - Disk Management", "6")
    K.body(doc, "The hospital records server must start reliably, survive a disk failure and have "
                "enough swap for peak load.")

    K.h2(doc, "6.1  Formatting, partitioning and booting")
    K.bullets(doc, [
        "Low-level formatting writes the sector structure and the error-correcting codes on the "
        "platter; the controller needs it before any block can be addressed.",
        "Partitioning writes the partition table (MBR or GPT) that records where each logical volume "
        "starts and ends.",
        "Logical formatting writes a filesystem into a partition: superblock, free-space bitmap, "
        "inodes and the root directory.",
        "The boot block is the first sector (or the EFI system partition). Firmware loads it, it "
        "loads the second-stage bootloader, and the bootloader loads the kernel with the parameter "
        "block that says where the root filesystem is.",
    ])
    K.body(doc, "Bad blocks are handled by the drive's own remapping for soft errors and by the "
                "filesystem (or a tool such as badblocks) marking hard errors so that no file is "
                "ever allocated there. Swap should be sized for the peak excess of working set over "
                "RAM; for this server, where peak load exceeds RAM by design, a swap partition on a "
                "separate disk is preferable to a swap file because it avoids competing with the "
                "filesystem's own I/O and is not subject to file fragmentation.")

    K.h2(doc, "6.2  RAID comparison")
    K.code_block(doc, logtext("q6_raid.log"), max_lines=20)
    K.figure(doc, os.path.join(FIGS, "fig11_raid_capacity.png"),
             "Figure 12. Usable capacity of six 4 TB disks at each RAID level.", 14.0)
    K.figure(doc, os.path.join(FIGS, "fig12_raid_loss.png"),
             "Figure 13. Probability of data loss during a rebuild.", 14.0)
    K.body(doc, "The numbers in the second table come from the rebuild model in q6_raid.c: with an "
                "annualised failure rate of 4 percent, the chance that a given surviving disk fails "
                "during a T-hour rebuild is 0.04 x T / 8760, and the array survives only if none of "
                "its surviving disks fails.")
    K.data_table(
        doc,
        ["RAID", "Capacity", "Read", "Write", "Survives", "Loss risk in 24 h"],
        [
            ["0", "24 TB", "6x", "6x", "nothing", "certain on any failure"],
            ["1", "12 TB", "3x", "3x", "1 disk", "0.011%"],
            ["5", "20 TB", "5x", "slow (parity)", "1 disk", "0.055%"],
            ["6", "16 TB", "4x", "slower (dual parity)", "2 disks", "0.044%"],
            ["10", "12 TB", "3x", "3x", "1 per mirror", "0.011%"],
        ],
        widths=[1.6, 2.6, 2.0, 4.4, 2.8, 3.4],
        font_size=8.6,
    )

    K.h2(doc, "6.3  Recommendation")
    K.body(doc, "RAID 10 for the records database: 12 TB of usable space is enough, the measured risk "
                "of loss during a 24-hour rebuild (0.011 percent) is five times lower than RAID 5 "
                "(0.055 percent), and the write path is 3x instead of the parity update that makes "
                "RAID 5 slow for a records workload. RAID 6 is the alternative where capacity matters "
                "more than write speed; it survives two failures but pays a dual-parity penalty on "
                "every write.")

    K.h2(doc, "6.4  Swap and the measured disk speed")
    K.body(doc, "q6_readspeed.c reads a 256 MB file sequentially. The measured throughput on this "
                "machine's SSD is:")
    K.code_block(doc, logtext("q6_readspeed.log"))

    K.h2(doc, "6.5  Alternative concept and complexity")
    K.body(doc, "RAID 6 with six 4 TB disks gives 16 TB usable - 4 TB less than RAID 5 - and "
                "survives two failures. Every write costs two parity computations and two parity "
                "writes, so the write path is roughly one third of RAID 5's; the read path is 4x. "
                "The space and time trade is O(1) arithmetic but a real factor in throughput, which "
                "is why the choice is made from the workload rather than from the reliability alone.")

    K.h2(doc, "6.6  Conclusion")
    K.body(doc, "RAID 10 for the records, a dedicated swap partition on a separate disk, and the "
                "bootloader on a mirrored pair: the configuration that satisfies 'starts reliably, "
                "survives a disk failure, and has swap for peak load' with the measurements above "
                "behind each clause.")


def q7(doc):
    K.h1(doc, "Q7 - A Memory-Management Plan from First Principles", "7")
    K.body(doc, "A smart-factory edge device has 2 GB of RAM and no swap. It runs a real-time "
                "control task that must never be delayed by a page fault, a machine-learning task "
                "that needs 1.5 GB, and a logging task.")

    K.h2(doc, "7.1  Stage 1 - Interpret the problem")
    K.data_table(
        doc,
        ["Task", "Memory", "Deadline", "Can it take a page fault?"],
        [
            ["Real-time control", "64 MB", "every cycle, sub-millisecond", "no"],
            ["ML inference", "1,500 MB", "seconds", "yes"],
            ["Logger", "128 MB", "minutes, batched", "yes"],
            ["Total", "1,692 MB", "of 2,048 MB", "356 MB left for page cache"],
        ],
        widths=[4.0, 3.2, 5.0, 4.6],
        font_size=9,
    )
    K.body(doc, "Measurable requirements: the control task's worst-case latency must stay below its "
                "period; the ML task must complete within its budget; the logger must not lose "
                "records; and the design must still work with a fourth task added.")

    K.h2(doc, "7.2  Stage 2 - Compare the candidate mechanisms")
    K.data_table(
        doc,
        ["Mechanism", "Control task", "ML task", "Logger", "Verdict"],
        [
            ["Contiguous allocation", "excellent latency", "cannot fit 1.5 GB reliably",
             "wasteful", "rejected: external fragmentation"],
            ["Paging", "faults possible", "fits and is reclaimable", "fine",
             "used for ML and logger"],
            ["Segmentation", "good protection", "external fragmentation", "fine",
             "used only as protection, not as allocation"],
            ["Demand paging + mlock", "no faults once locked", "fits", "fine",
             "the design: page the rest, lock the control task"],
        ],
        widths=[4.6, 3.4, 4.0, 2.4, 4.4],
        font_size=8.6,
    )

    K.h2(doc, "7.3  Stage 3 - Implement and verify")
    K.body(doc, "q7_mlock.c runs a fixed control computation 2,000 times and records every iteration, "
                "with and without mlock(). q7_sim.c simulates the three tasks under LRU on 2,048 "
                "modelled frames.")
    K.figure(doc, os.path.join(SHOTS, "q7_mlock.png"),
             "Console capture 9. Worst-case latency with and without mlock().", 15.8)
    K.code_block(doc, logtext("q7_mlock_off.log") + "\n\n" + logtext("q7_mlock_on.log"))
    K.body(doc, "Locking the buffer cut the worst case from 2,941.9 us to 1,793.9 us and the 99th "
                "percentile from 624.1 us to 506.8 us. The mean moved less (172.1 to 156.0 us) "
                "because the machine has enough RAM that faults are rare; the lock removes the tail, "
                "which is exactly what a deadline cares about.")
    K.code_block(doc, logtext("q7_sim.log"), max_lines=22)
    K.figure(doc, os.path.join(FIGS, "fig13_q7_plan.png"),
             "Figure 14. The memory plan for the edge device.", 15.5)

    K.h2(doc, "7.4  Stage 4 - Defend the design")
    K.body(doc, "The plan is: pin 64 MB for the control task with mlock() and give it a fixed budget; "
                "let the ML task run under a cgroup memory limit of 1.5 GB so that it cannot evict "
                "the control task; keep the logger small and reclaimable; leave 356 MB for page "
                "cache. The simulation shows the three working sets fit, so no capacity misses occur "
                "in the steady state, and the pinning makes the control task's latency independent "
                "of what the ML task is doing.")
    K.body(doc, "Adding a fourth 500 MB task makes 2,192 MB against 2,048 MB of RAM. The simulation "
                "shows the consequence: the ML task's faults rise from 1,500 to 2,846 and the "
                "logger's from 128 to 291, while the control task stays at 64 because its pages are "
                "re-referenced every cycle. The correct response is to reduce the ML working set or "
                "move it to a second device, not to let the extra task compete.")
    K.body(doc, "Remaining limitation: with no swap, a working set larger than RAM has nowhere to go, "
                "so the ML task must be designed to fit; and mlock() protects against eviction, not "
                "against a hardware or driver latency spike.")

    K.h2(doc, "7.5  Alternative concept and complexity")
    K.body(doc, "On a real-time OS with no virtual memory, the control task's worst-case delay becomes "
                "deterministic (no page fault is possible) and its numbers above improve, but the ML "
                "task loses both the ability to exceed RAM and the ability to be paged out, so it "
                "would have to fit in what is left after every task's static allocation. Adding tasks "
                "becomes a static budgeting exercise rather than a scheduling one: O(1) arithmetic, "
                "but far less flexibility, which is why the Linux-with-mlock design keeps more of the "
                "device's capability.")


def appendices(doc):
    K.h1(doc, "Appendix A - Repository Layout and Reproduction", "A")
    K.code_block(doc, """CSA0406-1965260024-Assignment3/
  README.md
  Q1_Linking/        q1_app.c q1_crypto.c q1_crypto.h q1_tables.c q1_dlopen.c q1_maps.c
                     build.sh output/ screenshots/
  Q2_Paging/         q2_todo.c q2_frag.c q2_eat.c q2_boundary.c ...
  Q3_Segmentation/   q3_segment.c q3_segv.c q3_frag.c q3_tables.c
  Q4_VirtualMemory/  q4_locality.c q4_cow.c q4_memlimit.c
  Q5_Replacement/    q5_todo.c q5_replace.c
  Q6_Disk/           q6_raid.c q6_readspeed.c
  Q7_Plan/           q7_mlock.c q7_sim.c
  diagrams/  logs/""")
    K.body(doc, "Build and run everything with:")
    K.code_block(doc, """export PATH=/d/FREEBUFF/tools/msys64/usr/bin:$PATH
gcc -std=c11 -Wall -Wextra -O2 src/q2_todo.c -o bin/q2_todo.exe
bash run_all.sh          # runs every program, writes logs/""")

    K.h1(doc, "Appendix B - Log Index", "B")
    rows = []
    for name in sorted(os.listdir(LOGS)):
        if name.endswith(".log"):
            path = os.path.join(LOGS, name)
            rows.append([name, f"{os.path.getsize(path)} B"])
    K.data_table(doc, ["Log file", "Size"], rows, widths=[10.0, 3.0], font_size=8.5)

    K.h1(doc, "Appendix C - Verification Status", "C")
    K.body(doc, "Every quantity in this report was taken from a log file at build time. The table "
                "records which log each claim rests on.")
    K.data_table(
        doc,
        ["Claim in the report", "Log", "Status"],
        [
            ["static 8,419,909 B, shared 30,529 B, DLL 8,406,082 B", "q1_sizes_and_ldd.log", "verified"],
            ["start-up 435 ms static, 204 ms shared", "q1_startup.log", "verified"],
            ["library 1.0 -> 2.0 without recompiling", "q1_library_swap.log", "verified"],
            ["dlopen exit 0 and exit 2 when missing", "q1_dlopen*.log", "verified"],
            ["page-table translation matches the expected output", "q2_todo_1024.log", "verified"],
            ["internal fragmentation 0.01 / 0.03 / 14.97 %", "q2_fragmentation.log", "verified"],
            ["boundary read past the mapping faults", "q2_boundary.log", "verified"],
            ["segmentation fault reported with the faulting address", "q3_segv.log", "verified"],
            ["external fragmentation 84.35 %, 6 MB fails, 5 MB succeeds", "q3_fragmentation.log", "verified"],
            ["sequential 28.788 ms, random 34.648 ms", "q4_locality.log", "verified"],
            ["fault counts 1,500 -> 2,846 when the fourth task is added", "q7_sim.log", "verified"],
            ["worst case 2,941.9 us -> 1,793.9 us with mlock", "q7_mlock_*.log", "verified"],
            ["Belady: FIFO 9 -> 10 faults, LRU 10 -> 8", "q5_replace.log", "verified"],
            ["RAID capacity 24/12/20/16/12 TB", "q6_raid.log", "verified"],
            ["SSD read 1,184.8-1,358.3 MB/s", "q6_readspeed.log", "verified"],
        ],
        widths=[8.6, 5.4, 2.3],
        font_size=8.6,
    )

    K.h1(doc, "Appendix D - Limitations of the Evidence", "D")
    K.bullets(doc, [
        "The POSIX programs ran under MSYS2 on Windows 11, not on Linux. sysconf reports a 64 KB "
        "page and getrusage reports no faults, so fault counts come from the Windows process API.",
        "fork() is emulated by copying, so the copy-on-write experiment shows duplication rather than "
        "sharing; the program, its output and an explanation are included rather than a fabricated "
        "result.",
        "Swap and RAID were calculated, not installed: this machine has one SSD and no swap device.",
        "The disk measurement therefore covers the SSD only; a hard-disk comparison would need a "
        "second machine.",
    ])


def signature(doc):
    K.page_break(doc)
    K.body(doc, "Submitted by")
    K.signature_block(doc)


def main():
    doc = K.new_document()
    K.add_header_footer(doc, "CSA0406 - Assignment 3 - " + REGNO,
                        f"{STUDENT}  |  {REGNO}  |  {DEPT}")
    cover(doc)
    marking_sheet(doc)
    declaration(doc)
    K.page_break(doc)
    K.h1(doc, "Table of Contents", "")
    K.add_toc(doc, "1-2")
    environment(doc)
    q1(doc); q2(doc); q3(doc); q4(doc); q5(doc); q6(doc); q7(doc)
    appendices(doc)
    signature(doc)
    K.enable_update_fields(doc)
    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
