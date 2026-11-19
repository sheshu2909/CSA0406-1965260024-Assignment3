#!/usr/bin/env bash
# run_all.sh - execute every Assignment 3 program and keep the output as
# evidence. Run from work3/ with the MSYS2 toolchain on PATH.
set -u
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"

cd "$(dirname "$0")"
mkdir -p logs bin

say() { echo "== $* =="; }

# ---------- Q1 ----------
say "Q1 static vs shared"
{
  echo "# Q1 sizes"
  stat -c '%s %n' bin/q1_app_static.exe bin/q1_app_shared.exe bin/libcrypto.dll
  echo
  echo "# ldd q1_app_shared.exe"
  ldd bin/q1_app_shared.exe
  echo
  echo "# ldd q1_app_static.exe"
  ldd bin/q1_app_static.exe
  echo
  echo "# run static"
  ./bin/q1_app_static.exe
  echo
  echo "# run shared"
  ./bin/q1_app_shared.exe
} > logs/q1_sizes_and_ldd.log 2>&1

say "Q1 dlopen"
{ ./bin/q1_dlopen.exe ./bin/libcrypto.dll; echo "exit=$?"; } > logs/q1_dlopen.log 2>&1
{ ./bin/q1_dlopen.exe ./bin/does_not_exist.dll; echo "exit=$?"; } > logs/q1_dlopen_missing.log 2>&1

say "Q1 replace the library without recompiling"
{
  echo "# before the swap"
  ./bin/q1_app_shared.exe | head -1
  cp bin/libcrypto.dll /tmp/libcrypto_v1_backup.dll
  cp bin/libcrypto_v2.dll bin/libcrypto.dll
  echo "# after replacing libcrypto.dll with version 2 (program untouched)"
  ./bin/q1_app_shared.exe | head -1
  cp /tmp/libcrypto_v1_backup.dll bin/libcrypto.dll
  echo "# after restoring version 1"
  ./bin/q1_app_shared.exe | head -1
} > logs/q1_library_swap.log 2>&1

say "Q1 /proc/self/maps"
{ ./bin/q1_maps.exe; } > logs/q1_maps.log 2>&1

say "Q1 start-up time (20 runs each)"
{
  for exe in q1_app_static q1_app_shared; do
    total=0
    for i in $(seq 20); do
      t0=$(date +%s%N); ./bin/$exe.exe >/dev/null; t1=$(date +%s%N)
      total=$((total + (t1 - t0)))
    done
    echo "$exe: $((total / 20 / 1000)) us mean over 20 runs"
  done
} > logs/q1_startup.log 2>&1

say "Q1 two copies share the library"
{
  ./bin/q1_app_shared.exe >/dev/null &
  p1=$!
  ./bin/q1_app_shared.exe >/dev/null &
  p2=$!
  sleep 0.3
  echo "two processes: $p1 $p2"
  grep -i libcrypto /proc/$p1/maps | head -3
  echo "---"
  grep -i libcrypto /proc/$p2/maps | head -3
  wait
} > logs/q1_shared_pages.log 2>&1

# ---------- Q2 ----------
say "Q2"
{ ./bin/q2_todo.exe; }            > logs/q2_todo_1024.log 2>&1
{ ./bin/q2_todo_2048.exe; }       > logs/q2_todo_2048.log 2>&1
{ ./bin/q2_frag.exe; }            > logs/q2_fragmentation.log 2>&1
{ ./bin/q2_eat.exe; }             > logs/q2_eat.log 2>&1
{ ./bin/q2_boundary.exe; }        > logs/q2_boundary.log 2>&1
{ getconf PAGESIZE; ./bin/q2_boundary.exe | head -1; } > logs/q2_pagesize.log 2>&1

# ---------- Q3 ----------
say "Q3"
{ ./bin/q3_segment.exe; }         > logs/q3_segment.log 2>&1
{ ./bin/q3_frag.exe; }            > logs/q3_fragmentation.log 2>&1
{ ./bin/q3_tables.exe; }          > logs/q3_tables.log 2>&1
{ ./bin/q3_segv.exe; echo "exit=$?"; } > logs/q3_segv.log 2>&1
{ sleep 0.2 & pid=$!; grep -E 'rwxp|r--p' /proc/$pid/maps | head -12; wait; } > logs/q3_maps.log 2>&1

# ---------- Q4 ----------
say "Q4"
{ ./bin/q4_locality.exe 64; }     > logs/q4_locality.log 2>&1
{ ./bin/q4_cow.exe; }             > logs/q4_cow.log 2>&1
{
  for m in 64 128 256 512 1024 1536; do ./bin/q4_memlimit.exe $m 3; done
} > logs/q4_memlimit.log 2>&1

# ---------- Q5 ----------
say "Q5"
{ ./bin/q5_todo.exe; }            > logs/q5_todo.log 2>&1
{ ./bin/q5_replace.exe; }         > logs/q5_replace.log 2>&1

# ---------- Q6 ----------
say "Q6"
{ ./bin/q6_raid.exe; }            > logs/q6_raid.log 2>&1
{ ./bin/q6_readspeed.exe ./logs/readtest.bin 3; } > logs/q6_readspeed.log 2>&1

# ---------- Q7 ----------
say "Q7"
{ ./bin/q7_sim.exe; }             > logs/q7_sim.log 2>&1
{ ./bin/q7_mlock.exe 2000 32; }   > logs/q7_mlock_off.log 2>&1
{ ./bin/q7_mlock.exe -l 2000 32; } > logs/q7_mlock_on.log 2>&1

say "done"
ls -1 logs | wc -l
