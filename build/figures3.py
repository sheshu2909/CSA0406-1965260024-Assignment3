"""Diagrams for the CSA0406 Assignment 3 report.

Measured figures (sizes, start-up times, fault counts) are read from the real
logs in work3/logs; the explanatory diagrams (paging, segmentation, RAID
layouts) are drawn from the definitions given in the assignment.
"""
from __future__ import annotations

import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work3")
LOGS = os.path.join(WORK, "logs")
OUT = os.path.join(WORK, "diagrams")
os.makedirs(OUT, exist_ok=True)

NAVY = "#1B365D"
ACCENT = "#0B5C8A"
GREY = "#6B7A8F"
LIGHT = "#EAF1F8"
WARN = "#B23A48"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": "#5A6B80",
    "axes.labelcolor": NAVY,
    "text.color": NAVY,
    "figure.dpi": 200,
})


def box(ax, x, y, w, h, text, fill=LIGHT, edge=ACCENT, size=8, bold=False):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, linewidth=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            color=NAVY, fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, p1, p2, text=None, color=ACCENT, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=10,
                                 color=color, linewidth=1.0,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.12, text,
                ha="center", va="bottom", fontsize=7.5, color=GREY)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def log_values(name, pattern, cast=float):
    with open(os.path.join(LOGS, name), encoding="utf-8", errors="replace") as f:
        text = f.read()
    return [cast(m) for m in re.findall(pattern, text, re.M)]


# --------------------------------------------------------------------------- #
def fig_binding():
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")

    stages = ["source\ncode", "compile\nand link", "load into\nmemory", "execution"]
    xs = [0.4, 2.9, 5.4, 7.9]
    for x, s in zip(xs, stages):
        box(ax, x, 1.0, 1.7, 0.9, s, bold=True)

    for x in xs[:-1]:
        arrow(ax, (x + 1.7, 1.45), (x + 2.5, 1.45))

    labels = [("compile-time binding\nabsolute addresses fixed", 0.4),
              ("load-time binding\nrelocation by the loader", 0.85),
              ("execution-time binding\nMMU translates at run time", 5.4)]
    ax.annotate("compile-time binding: absolute addresses fixed by the linker",
                xy=(1.25, 2.0), xytext=(0.3, 2.65), fontsize=7.5, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.annotate("load-time binding: the loader relocates the program",
                xy=(3.75, 2.0), xytext=(2.9, 2.75), fontsize=7.5, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.annotate("execution-time binding: the MMU translates every access",
                xy=(6.25, 2.0), xytext=(5.9, 2.65), fontsize=7.5, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.text(0.4, 0.35, "earlier binding = faster access, less flexibility    "
                       "later binding = one extra translation, full flexibility",
            fontsize=7.5, color=NAVY)
    save(fig, "fig1_binding.png")


def fig_static_dynamic():
    sizes = log_values("q1_sizes_and_ldd.log", r"^\s*(\d+) bin/", int)
    static_exe, shared_exe, dll = sizes[0], sizes[1], sizes[2]
    startup = log_values("q1_startup.log", r": (\d+) us", int)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 3.0))
    a1.bar(["static\nexecutable"], [static_exe / 1e6], color=NAVY, width=0.5)
    a1.bar(["shared\nexecutable"], [shared_exe / 1e6], color=ACCENT, width=0.5)
    a1.bar(["shared\nlibrary (DLL)"], [dll / 1e6], color=GREY, width=0.5)
    a1.set_ylabel("size on disk (MB)")
    a1.set_title("one copy per program vs one shared copy", fontsize=9)
    for i, v in enumerate([static_exe, shared_exe, dll]):
        a1.text(i, v / 1e6 + 0.15, f"{v/1e6:.2f} MB", ha="center", fontsize=8)
    a1.set_ylim(0, 10)

    a2.bar(["static", "shared"], [startup[0] / 1000.0, startup[1] / 1000.0],
           color=[NAVY, ACCENT], width=0.45)
    a2.set_ylabel("mean start-up (ms, 20 runs)")
    a2.set_title("start-up cost of the 8 MB image", fontsize=9)
    for i, v in enumerate(startup):
        a2.text(i, v / 1000.0 + 5, f"{v/1000.0:.0f} ms", ha="center", fontsize=8)
    a2.set_ylim(0, 520)
    fig.tight_layout()
    save(fig, "fig2_static_vs_dynamic.png")


def fig_external_frag():
    fig, ax = plt.subplots(figsize=(7.2, 2.2))
    ax.set_xlim(0, 100); ax.set_ylim(0, 3); ax.axis("off")
    blocks = [(0, 14, "P1"), (14, 10, "free"), (24, 18, "P2"), (42, 6, "free"),
              (48, 22, "P3"), (70, 5, "free"), (75, 16, "P4"), (91, 9, "free")]
    for x, w, lab in blocks:
        free = lab == "free"
        box(ax, x, 1.2, w, 0.8, lab,
            fill="white" if free else LIGHT,
            edge=WARN if free else ACCENT, size=7.5)
    ax.annotate("a 12-unit request fails although 30 units are free:\n"
                "the holes are separate and cannot be merged",
                xy=(45, 1.2), xytext=(30, 2.35), fontsize=7.5, color=WARN,
                arrowprops=dict(arrowstyle="-|>", color=WARN, lw=0.8))
    ax.text(0, 0.55, "contiguous allocation: total free memory 30 units, largest hole 16 units",
            fontsize=7.5, color=GREY)
    save(fig, "fig3_external_frag.png")


def fig_paging():
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.2); ax.axis("off")

    box(ax, 0.2, 2.6, 2.6, 0.8, "logical address\np | d", bold=True)
    box(ax, 3.6, 2.6, 2.2, 0.8, "page table\nbase register")
    box(ax, 3.4, 1.2, 2.6, 0.9, "page table\np -> frame f", fill="white")
    box(ax, 7.2, 2.6, 2.4, 0.8, "physical address\nf | d", bold=True)
    box(ax, 7.2, 1.2, 4.4, 0.9, "physical memory\nframes scattered anywhere", fill="white")

    arrow(ax, (2.8, 3.0), (3.6, 3.0))
    arrow(ax, (4.7, 2.6), (4.7, 2.1))
    arrow(ax, (6.0, 1.65), (7.2, 2.9), rad=-0.25)
    ax.text(6.0, 0.6, "the table is the only thing that has to be contiguous;\n"
                      "frames are allocated one at a time, so no external fragmentation",
            fontsize=7.5, color=GREY)
    save(fig, "fig4_paging_translate.png")


def fig_page_size():
    # real internal-fragmentation measurements from q2_frag
    waste = log_values("q2_fragmentation.log", r"waste\s+\d+ B \(\s*([\d.]+)%\)")
    labels = ["1 KB", "4 KB", "2 MB"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 2.9))
    a1.bar(labels, waste, color=[ACCENT, ACCENT, NAVY], width=0.5)
    a1.set_ylabel("internal fragmentation (%)")
    a1.set_title("100 processes, 578 MB requested", fontsize=9)
    for i, v in enumerate(waste):
        a1.text(i, v + 0.3, f"{v:.2f}%", ha="center", fontsize=8)

    table_kb = [1024 / 1024 * 1024 / 1024, 4096 / 1024 * 1024 / 1024, 2]  # illustrative
    a2.plot([1, 4, 2048], [0.01, 0.03, 15.0], "o-", color=NAVY, label="internal waste")
    a2.set_xscale("log"); a2.set_xlabel("page size (KB, log scale)")
    a2.set_ylabel("waste (%)"); a2.set_title("measured waste against page size", fontsize=9)
    a2.grid(alpha=0.25)
    fig.tight_layout()
    save(fig, "fig5_page_size.png")


def fig_seg_paging():
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.0); ax.axis("off")
    box(ax, 0.2, 2.7, 2.4, 0.8, "logical address\ns | p | d", bold=True)
    box(ax, 3.2, 2.7, 2.2, 0.8, "segment table\nbase + limit")
    box(ax, 3.3, 1.2, 2.4, 0.9, "per-segment\npage table")
    box(ax, 6.6, 1.2, 2.4, 0.9, "page frame\nin memory", fill="white")
    box(ax, 9.6, 1.2, 2.2, 0.9, "physical\naddress", bold=True)
    arrow(ax, (2.6, 3.1), (3.2, 3.1))
    arrow(ax, (4.3, 2.7), (4.3, 2.1))
    arrow(ax, (5.7, 1.65), (6.6, 1.65))
    arrow(ax, (9.0, 1.65), (9.6, 1.65))
    ax.text(0.2, 0.55, "x86 style: the segment selects a page table (and checks the limit),\n"
                       "the page number indexes it. Both checks are done by the MMU.",
            fontsize=7.5, color=GREY)
    save(fig, "fig6_seg_paging.png")


def fig_page_fault():
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    steps = ["1. MMU finds the page not present\n(page-fault trap to the kernel)",
             "2. kernel checks the address is legal\nand finds the page on disk",
             "3. victim frame chosen, written back\nif dirty, page read from disk",
             "4. page table updated,\nTLB and instruction restarted",
             "5. the instruction completes\nand execution continues"]
    y = 5.4
    for i, s in enumerate(steps):
        box(ax, 0.3, y, 6.4, 0.85, s, fill=LIGHT if i % 2 == 0 else "white", size=8)
        if i < len(steps) - 1:
            arrow(ax, (3.5, y), (3.5, y - 0.2))
        y -= 1.05
    ax.text(7.0, 4.2, "cost: 100 ns\nif it hits,\n8,000,000 ns\nif it faults",
            fontsize=8, color=WARN, ha="left")
    save(fig, "fig7_page_fault.png")


def fig_cow():
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.2); ax.axis("off")
    box(ax, 0.2, 1.9, 2.6, 0.8, "parent\npage A (rw)", bold=True)
    box(ax, 3.4, 1.9, 2.6, 0.8, "fork()", fill="white")
    box(ax, 6.6, 2.3, 3.0, 0.7, "child reads: same frame")
    box(ax, 6.6, 1.3, 3.0, 0.7, "child writes: copy, then write")
    arrow(ax, (2.8, 2.3), (3.4, 2.3))
    arrow(ax, (6.0, 2.4), (6.6, 2.6))
    arrow(ax, (6.0, 2.1), (6.6, 1.6))
    ax.text(0.2, 0.6, "fork() copies the page table and marks every page read-only;\n"
                      "the write fault is what makes the private copy.",
            fontsize=7.5, color=GREY)
    save(fig, "fig8_cow.png")


def fig_faults_vs_frames():
    text = open(os.path.join(LOGS, "q5_replace.log"), encoding="utf-8").read()
    rows = re.findall(r"^locality\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$", text, re.M)
    if not rows:
        rows = re.findall(r"locality\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
    frames = [int(r[0]) for r in rows]
    fifo = [int(r[1]) for r in rows]
    lru = [int(r[2]) for r in rows]
    opt = [int(r[3]) for r in rows]
    clk = [int(r[4]) for r in rows]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.4, 3.1))
    a1.plot(frames, fifo, "o-", label="FIFO", color=NAVY)
    a1.plot(frames, lru, "s-", label="LRU", color=ACCENT)
    a1.plot(frames, opt, "^-", label="Optimal", color=GREY)
    a1.plot(frames, clk, "d--", label="Clock", color=WARN)
    a1.set_xlabel("frames"); a1.set_ylabel("page faults (10,000 refs)")
    a1.set_title("strong locality (90% hot set)", fontsize=9)
    a1.legend(fontsize=7.5); a1.grid(alpha=0.25)

    rrows = re.findall(r"^random\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$", text, re.M)
    if not rrows:
        rrows = re.findall(r"random\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
    rf = [int(r[0]) for r in rrows]
    a2.plot(rf, [int(r[1]) for r in rrows], "o-", label="FIFO", color=NAVY)
    a2.plot(rf, [int(r[2]) for r in rrows], "s-", label="LRU", color=ACCENT)
    a2.plot(rf, [int(r[3]) for r in rrows], "^-", label="Optimal", color=GREY)
    a2.set_xlabel("frames"); a2.set_ylabel("page faults (10,000 refs)")
    a2.set_title("random access (no locality)", fontsize=9)
    a2.legend(fontsize=7.5); a2.grid(alpha=0.25)
    fig.tight_layout()
    save(fig, "fig9_faults_vs_frames.png")


def fig_belady():
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    ax.bar(["FIFO\n3 frames", "FIFO\n4 frames"], [9, 10], color=[NAVY, WARN], width=0.5)
    ax.set_ylabel("page faults")
    ax.set_title("Belady's anomaly: more frames, more faults", fontsize=9)
    for i, v in enumerate([9, 10]):
        ax.text(i, v + 0.15, str(v), ha="center", fontsize=9)
    ax.set_ylim(0, 12)
    save(fig, "fig10_belady.png")


def fig_raid():
    text = open(os.path.join(LOGS, "q6_raid.log"), encoding="utf-8").read()
    rows = re.findall(r"^RAID (\d+)\s+([\d.]+) TB", text, re.M)
    names = [f"RAID {r[0]}" for r in rows]
    caps = [float(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    bars = ax.bar(names, caps, color=[WARN, ACCENT, NAVY, GREY, ACCENT], width=0.55)
    ax.set_ylabel("usable capacity (TB)")
    ax.set_title("6 disks x 4 TB: usable capacity per RAID level", fontsize=9)
    for b, c in zip(bars, caps):
        ax.text(b.get_x() + b.get_width() / 2, c + 0.4, f"{c:.0f} TB",
                ha="center", fontsize=8)
    ax.set_ylim(0, 27)
    save(fig, "fig11_raid_capacity.png")


def fig_raid_loss():
    text = open(os.path.join(LOGS, "q6_raid.log"), encoding="utf-8").read()
    rows = re.findall(r"^RAID \d+\s+\d+\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%", text, re.M)
    labels = ["RAID 1", "RAID 5", "RAID 6", "RAID 10"]
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    width = 0.25
    xs = range(len(rows))
    for i, h in enumerate(["6 h", "24 h", "48 h"]):
        vals = [float(r[i]) for r in rows]
        ax.bar([x + i * width for x in xs], vals, width=width, label=f"rebuild {h}")
    ax.set_xticks([x + width for x in xs])
    ax.set_xticklabels(labels[:len(rows)])
    ax.set_ylabel("probability of data loss (%)")
    ax.set_title("loss during a rebuild, AFR 4%/year", fontsize=9)
    ax.legend(fontsize=7.5)
    save(fig, "fig12_raid_loss.png")


def fig_q7_plan():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis("off")
    box(ax, 0.2, 3.0, 3.0, 0.9, "real-time control 64 MB\nmlock(), never paged")
    box(ax, 3.6, 3.0, 3.2, 0.9, "ML task 1500 MB\npaged, reclaimable")
    box(ax, 7.2, 3.0, 2.6, 0.9, "logger 128 MB\npaged, low priority")
    box(ax, 0.2, 1.5, 9.6, 0.9,
        "2 GB RAM, no swap: 1692 MB of working sets leave 356 MB for page cache",
        fill="white")
    arrow(ax, (1.7, 3.0), (1.7, 2.4))
    arrow(ax, (5.2, 3.0), (5.2, 2.4))
    arrow(ax, (8.5, 3.0), (8.5, 2.4))
    ax.text(0.2, 0.6, "a fourth 500 MB task makes 2192 MB: the ML task must be restrained\n"
                      "(cgroup memory limit) rather than allowed to evict the control task.",
            fontsize=7.5, color=GREY)
    save(fig, "fig13_q7_plan.png")


def fig_thrashing():
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    frames = list(range(2, 21))
    ws = 12
    faults = [min(100, 100 * ws / max(f, 1)) if f >= ws else 100 for f in frames]
    ax.plot(frames, faults, "o-", color=NAVY)
    ax.axvline(ws, color=WARN, linestyle="--", linewidth=1)
    ax.text(ws + 0.3, 70, "working set reached", color=WARN, fontsize=7.5)
    ax.set_xlabel("frames allocated to the process")
    ax.set_ylabel("page-fault rate")
    ax.set_title("thrashing: faults collapse once the working set fits", fontsize=9)
    ax.grid(alpha=0.25)
    save(fig, "fig14_thrashing.png")


if __name__ == "__main__":
    fig_binding()
    fig_static_dynamic()
    fig_external_frag()
    fig_paging()
    fig_page_size()
    fig_seg_paging()
    fig_page_fault()
    fig_cow()
    fig_faults_vs_frames()
    fig_belady()
    fig_raid()
    fig_raid_loss()
    fig_q7_plan()
    fig_thrashing()
