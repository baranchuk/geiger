"""Erase + flash a locked CC2530 (E18 module) via CCLib proxy, non-interactive. Usage: flash_e18.py COM3 file.hex"""
import sys, time
from cclib import CCHEXFile, openCCDebugger
port, path = sys.argv[1], sys.argv[2]
hexf = CCHEXFile(path); hexf.load()
top = max(mb.addr + mb.size for mb in hexf.memBlocks)
print(f"hex: {len(hexf.memBlocks)} blocks, top 0x{top:05x} ({top // 1024} KB)", flush=True)
dbg = openCCDebugger(port, enterDebug=True)
print(f"before erase: flash {dbg.flashSize // 1024} KB", flush=True)
print("chip erase...", flush=True); dbg.chipErase(); dbg.ser.close(); time.sleep(1)
dbg = openCCDebugger(port, enterDebug=True)
print(f"after erase: chip 0x{dbg.chipID:04x}, flash {dbg.flashSize // 1024} KB", flush=True)
if top > dbg.flashSize: sys.exit("ERROR: image larger than flash")
dbg.pauseDMA(False)
t0 = time.time()
for mb in hexf.memBlocks:
    print(f"-> 0x{mb.addr:05x}: {mb.size} B", flush=True)
    dbg.writeCODE(mb.addr, mb.bytes, verify=True, showProgress=True)
print(f"\nDONE in {(time.time() - t0) / 60:.1f} min (written + verified)", flush=True)
