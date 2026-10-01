"""Wait for the D1 mini (CH340) to appear, then erase + flash + verify a CC2530 page by page, with retries and
reconnects. Usage: auto_flash.py file.hex"""
import sys, time
import serial.tools.list_ports
from cclib import CCHEXFile, openCCDebugger
path = sys.argv[1]
hexf = CCHEXFile(path); hexf.load()
PAGE = 0x800
pages = {}
for mb in hexf.memBlocks:
    for i, b in enumerate(mb.bytes):
        a = mb.addr + i; p = a - a % PAGE
        pages.setdefault(p, bytearray(b"\xff" * PAGE))[a - p] = b
todo = sorted(pages)

def port():
    for p in serial.tools.list_ports.comports():
        if "1A86:7523" in (p.hwid or "").upper(): return p.device
print("waiting for D1 mini (CH340)...", flush=True)
while not port(): time.sleep(2)
dev = port(); time.sleep(2); print("found", dev, flush=True)

def connect():
    for i in range(5):
        try: return openCCDebugger(dev, enterDebug=True)
        except Exception as e: print("connect failed:", e, flush=True); time.sleep(3)
    sys.exit("ERROR: cannot reach the chip - check J1 wiring and board power")
d = connect()
print(f"chip 0x{d.chipID:04x}, IEEE {d.getSerial() if hasattr(d, 'getSerial') else '?'}, flash {d.flashSize // 1024} KB", flush=True)
print("chip erase...", flush=True); d.chipErase(); d.ser.close(); time.sleep(1)
d = connect(); print(f"after erase: flash {d.flashSize // 1024} KB", flush=True)
if d.flashSize < 256 * 1024: sys.exit("ERROR: flash still reports < 256 KB after erase")
d.pauseDMA(False); t0 = time.time(); n = 0
while n < len(todo):
    p = todo[n]
    for attempt in range(1, 4):
        try:
            d.writeCODE(p, pages[p], erase=True, verify=True); break
        except Exception as e:
            print(f"page 0x{p:05x} attempt {attempt}: {e}", flush=True)
            try: d.ser.close()
            except Exception: pass
            time.sleep(2); d = connect(); d.pauseDMA(False)
    else:
        sys.exit(f"ERROR: page 0x{p:05x} failed 3 times; resume with resume_e18.py {dev} <hex> 0x{p:05x}")
    n += 1
    if n % 10 == 0 or n == len(todo):
        print(f"page {n}/{len(todo)}  {(time.time() - t0) / 60:.1f} min", flush=True)
print(f"DONE: {len(todo)} pages written + verified in {(time.time() - t0) / 60:.1f} min", flush=True)
