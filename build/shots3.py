"""Capture genuine console screenshots for Assignment 3.

Each shot is a real bash session: the script is written to disk, run inside a
real console window, and the window is photographed with PrintWindow().
Nothing in the images is drawn or edited afterwards.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work3")
SHOTS = os.path.join(WORK, "shots")
SCRIPTS = os.path.join(SHOTS, "scripts")
CAPTURE = os.path.join(ROOT, "work", "build", "capture_terminal.ps1")
MSYS = "/d/FREEBUFF/tools/msys64/usr/bin"

HEAD = f"""
export PATH="{MSYS}:$PATH"
cd "{WORK}"
PS4='\\n$ '
"""

SHOTS_DEF = {
    "q1_static_shared": ("""
set -x
gcc -std=c11 -Wall -Wextra -O2 src/q1_app.c src/libcrypto.a -o bin/q1_app_static.exe
gcc -std=c11 -Wall -Wextra -O2 src/q1_app.c -Lsrc -lcrypto -o bin/q1_app_shared.exe
stat -c '%10s bytes  %n' bin/q1_app_static.exe bin/q1_app_shared.exe bin/libcrypto.dll
echo '--- ldd shared ---'
ldd bin/q1_app_shared.exe | grep -v -E 'ntdll|KERNEL'
echo '--- ldd static ---'
ldd bin/q1_app_static.exe | grep -v -E 'ntdll|KERNEL'
set +x
""", 12, 30),

    "q1_dlopen": ("""
set -x
./bin/q1_dlopen.exe ./bin/libcrypto.dll
echo "exit=$?"
./bin/q1_dlopen.exe ./bin/not_there.dll
echo "exit=$?"
set +x
""", 6, 20),

    "q1_library_swap": ("""
set -x
cp bin/libcrypto.dll /tmp/keep_v1.dll
echo 'before: ' $(./bin/q1_app_shared.exe | head -1)
cp bin/libcrypto_v2.dll bin/libcrypto.dll
echo 'after : ' $(./bin/q1_app_shared.exe | head -1)
cp /tmp/keep_v1.dll bin/libcrypto.dll
echo 'back  : ' $(./bin/q1_app_shared.exe | head -1)
set +x
""", 8, 18),

    "q1_maps": ("""
set -x
./bin/q1_maps.exe
set +x
""", 6, 30),

    "q2_todo": ("""
set -x
./bin/q2_todo.exe
echo
./bin/q2_todo_2048.exe
set +x
""", 6, 26),

    "q2_frag": ("""
set -x
./bin/q2_frag.exe
set +x
""", 6, 30),

    "q3_segment": ("""
set -x
./bin/q3_segment.exe
set +x
""", 6, 30),

    "q3_segv": ("""
set -x
./bin/q3_segv.exe
echo "exit status $?"
set +x
""", 6, 20),

    "q4_memlimit": ("""
set -x
for m in 64 128 256 512 1024; do ./bin/q4_memlimit.exe $m 3; done
set +x
""", 8, 18),

    "q5_replace": ("""
set -x
./bin/q5_replace.exe
set +x
""", 10, 40),

    "q6_raid": ("""
set -x
./bin/q6_raid.exe
set +x
""", 6, 30),

    "q7_mlock": ("""
set -x
./bin/q7_mlock.exe 2000 32
echo
./bin/q7_mlock.exe -l 2000 32
set +x
""", 10, 30),
}


def posix(path: str) -> str:
    """C:\\a\\b -> /c/a/b, the form bash -l can open."""
    p = os.path.abspath(path).replace("\\", "/")
    if len(p) > 1 and p[1] == ":":
        p = "/" + p[0].lower() + p[2:]
    return p


def main(only=None):
    os.makedirs(SCRIPTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    names = [only] if only else list(SHOTS_DEF)
    for name in names:
        body, wait, lines = SHOTS_DEF[name]
        script = os.path.join(SCRIPTS, f"{name}.sh")
        with open(script, "w", newline="\n") as f:
            f.write(HEAD + body)
        out = os.path.join(SHOTS, f"{name}.png")
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", CAPTURE,
            "-Title", f"SHOT-{name}",
            "-Script", posix(script),
            "-OutPath", out,
            "-WaitSeconds", str(wait),
            "-Cols", "124",
            "-Lines", str(lines),
        ]
        print(f"capturing {name} ...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip()[:300])
        if not os.path.exists(out):
            print(f"  WARNING: {name} produced no image")
    print("done")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
