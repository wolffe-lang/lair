import importlib.machinery
import importlib.util
from pathlib import Path
import time
root=Path(__file__).resolve().parents[2]
loader=importlib.machinery.SourceFileLoader('repro_pty',str(root/'tools/pty'))
p=importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name,loader));loader.exec_module(p)
assert p.mac_memory_ok()
for delay in (0,.180):
    s=p.Session([str(root/'target/native/lair'),'--input-loop','ctrl-c'],24,80,p.env_for(),settle=.01)
    start=time.monotonic()
    stamps=[]
    try:
        while b'\x1b[?u' not in s.out and time.monotonic()-start<2:s.pump(.005)
        assert b'\x1b[?u' in s.out
        query=time.monotonic()
        for part in (b'x\x1b[',b'?0',b'uy'):
            if part==b'uy' and delay:s.pump(delay)
            stamps.append((part,round((time.monotonic()-query)*1000,3)))
            s.type(part,settle=.005)
        s.pump(.04)
        s.type(b'\x03')
        s.finish(timeout=5)
        print('controlled-parent-delay-ms',delay*1000,'write-ms-after-query-observed',stamps,flush=True)
        print('stderr',repr(s.err),'exit',s.status,flush=True)
        want=b'exact=false startup=5' if delay else b'exact=true startup=2'
        assert want in s.err
        assert b'event key=1121' in s.err
    finally:
        if not hasattr(s,'status'):s.type(b'q');s.finish(timeout=5)
