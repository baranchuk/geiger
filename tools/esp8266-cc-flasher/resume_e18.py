"""Resume CC2530 flashing from a page-aligned address: per 2 KB page erase + write + verify, retry on error.
Usage: resume_e18.py COM3 file.hex 0x22000"""
import sys, time
from cclib import CCHEXFile, openCCDebugger
port, path, start = sys.argv[1], sys.argv[2], int(sys.argv[3], 0)
hexf = CCHEXFile(path); hexf.load()
dbg = openCCDebugger(port, enterDebug=True)
print(f"chip 0x{dbg.chipID:04x}, flash {dbg.flashSize // 1024} KB", flush=True)
dbg.pauseDMA(False)
PAGE = dbg.flashPageSize
pages = {}                                   # page addr -> bytearray(PAGE) filled with 0xFF
for mb in hexf.memBlocks:
    for i, b in enumerate(mb.bytes):
        a = mb.addr + i
        if a < start: continue
        p = a - a % PAGE
        pages.setdefault(p, bytearray(b"\xff" * PAGE))[a - p] = b
todo = sorted(pages); t0 = time.time()
print(f"{len(todo)} pages from 0x{todo[0]:05x} to 0x{todo[-1] + PAGE - 1:05x}", flush=True)
for n, p in enumerate(todo, 1):
    for attempt in range(1, 4):
        try:
            dbg.writeCODE(p, pages[p], erase=True, verify=True); break
        except IOError as e:
            print(f"page 0x{p:05x} attempt {attempt}: {e}", flush=True); time.sleep(0.5)
    else:
        sys.exit(f"ERROR: page 0x{p:05x} failed 3 times")
    if n % 4 == 0 or n == len(todo):
        print(f"page {n}/{len(todo)} @0x{p:05x}  {(time.time() - t0) / 60:.1f} min", flush=True)
print("DONE: all remaining pages written + verified", flush=True)
