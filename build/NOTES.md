# Build and verification scripts

These are the exact scripts used to produce the evidence and the report.

| Script | Purpose |
|---|---|
| `verify3.py` | re-checks 26 headline numbers in the report against `logs/` |
| `report3.py` | builds the Word report (needs python-docx and matplotlib) |
| `figures3.py` | draws the diagrams, reading measured values from the logs |
| `shots3.py` | captures the console screenshots (`capture_terminal.ps1`) |
| `package3.py` | assembles the submission folder and ZIP |
| `docx_kit.py` | shared python-docx styling helpers |

`run_all.sh` (repository root) executes every program and writes its output to
`logs/`. It expects gcc on `PATH`; the author used gcc 16.2.0 from MSYS2 with

```bash
export PATH=/d/FREEBUFF/tools/msys64/usr/bin:$PATH
```

Paths inside `report3.py`, `shots3.py` and `package3.py` are relative to the
author's working tree (`../work3`, `../work/build`); adjust those few constants
if the tree is laid out differently.
