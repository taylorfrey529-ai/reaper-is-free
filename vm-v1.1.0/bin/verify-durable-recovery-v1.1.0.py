#!/usr/bin/env python3
import argparse, hashlib, io, json, pathlib, re, shutil, subprocess, tarfile, tempfile, zipfile
CHUNK=8*1024*1024

def fail(m): raise SystemExit('FAIL: '+m)
def ok(m): print('PASS: '+m)
def digest_stream(f,h=None):
    h=h or hashlib.sha256(); n=0
    while True:
        b=f.read(CHUNK)
        if not b: break
        h.update(b); n+=len(b)
    return n,h.hexdigest()
def sha(path):
    with open(path,'rb') as f: return digest_stream(f)[1]
def staged(root,obj):
    p=root/obj['name']
    if not p.is_file(): fail('missing '+obj['name'])
    if obj.get('bytes') is not None and p.stat().st_size!=obj['bytes']: fail('size '+obj['name'])
    if obj.get('wrapper_sha256') and sha(p)!=obj['wrapper_sha256']: fail('wrapper hash '+obj['name'])
    return p
def member(z,suffix=None):
    ns=[n for n in z.namelist() if not n.endswith('/') and (suffix is None or n.endswith(suffix))]
    if len(ns)!=1: fail('ZIP member selection '+str(ns))
    return ns[0]
def chunked(root,a,key,source=None,materialize=False):
    mp=staged(root,a['manifest'])
    with zipfile.ZipFile(mp) as z: m=json.loads(z.read(member(z,'manifest.json')))
    if source and m.get('source_commit')!=source: fail('source commit')
    if len(a['drive_objects'])!=len(m['parts']): fail('part count')
    logical=hashlib.sha256(); total=0
    tmp=None; sink=None
    if materialize:
        h=tempfile.NamedTemporaryFile(prefix='vm-v110-',delete=False)
        tmp=pathlib.Path(h.name); sink=h
    try:
        for obj,part in zip(a['drive_objects'],m['parts']):
            p=staged(root,obj)
            with zipfile.ZipFile(p) as z:
                q=member(z); ph=hashlib.sha256(); n=0
                with z.open(q) as f:
                    while True:
                        b=f.read(CHUNK)
                        if not b: break
                        ph.update(b); logical.update(b); n+=len(b); total+=len(b)
                        if sink: sink.write(b)
            if pathlib.PurePosixPath(q).name!=part['name'] or n!=part['size'] or ph.hexdigest()!=part['sha256']: fail('inner part '+part['name'])
        if sink: sink.close(); sink=None
        got=logical.hexdigest()
        if got!=m['logical_sha256'] or got!=a[key] or total!=m['logical_size']: fail('logical reconstruction')
        ok(m['logical_name']+' '+got)
        return tmp
    finally:
        if sink: sink.close()
def single_inner(root,a,suffix,key):
    p=staged(root,a['drive_objects'][0])
    with zipfile.ZipFile(p) as z:
        q=member(z,suffix)
        with z.open(q) as f: got=digest_stream(f)[1]
    if got!=a[key]: fail(suffix+' inner hash')
    ok(suffix+' '+got)

def sforzando(root,a):
    p=staged(root,a['drive_objects'][0])
    with zipfile.ZipFile(p) as outer:
        q=member(outer,'LINUX_plogue-sforzando_1.982_x86_64.zip')
        source=outer.read(q)
    if hashlib.sha256(source).hexdigest()!=a['source_archive_sha256']: fail('sforzando source ZIP')
    with tempfile.TemporaryDirectory(prefix='vm-v110-sfz-') as td:
        td=pathlib.Path(td)
        with zipfile.ZipFile(io.BytesIO(source)) as z:
            debs=[n for n in z.namelist() if n.endswith('plogue-sforzando_1.982_amd64.deb')]
            if len(debs)!=1: fail('sforzando DEB selection')
            deb=td/'sforzando.deb'; deb.write_bytes(z.read(debs[0]))
        out=td/'debroot'
        try:
            subprocess.run(['dpkg-deb','-x',str(deb),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except (FileNotFoundError,subprocess.CalledProcessError):
            fail('sforzando dpkg-deb extraction')
        bins=list(out.rglob('sforzando.so'))
        bins=[x for x in bins if 'sforzando.vst3' in str(x)]
        if len(bins)!=1 or sha(bins[0])!=a['binary_sha256']: fail('sforzando installed binary')
    ok('sforzando source ZIP + installed VST3 binary')

def avldrums(root,a):
    p=staged(root,a['drive_objects'][0])
    with zipfile.ZipFile(p) as z:
        q=member(z,'avldrums-exact.tar.gz'); blob=z.read(q)
    if hashlib.sha256(blob).hexdigest()!=a['recovery_tar_sha256']: fail('AVL recovery tar')
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as t:
        files={pathlib.PurePosixPath(m.name).name:m for m in t.getmembers() if m.isfile()}
        for name,key in [('avldrums.so','binary_sha256'),('Black_Pearl_4_LV2.sf2','black_pearl_sha256')]:
            m=files.get(name)
            if not m: fail('AVL missing '+name)
            f=t.extractfile(m)
            if f is None or digest_stream(f)[1]!=a[key]: fail('AVL hash '+name)
    ok('AVL recovery tar + plugin + Black Pearl')

def nam(root,a):
    p=staged(root,a['drive_objects'][0])
    with zipfile.ZipFile(p) as z:
        q=member(z,'astra-nam-gm2-linux.tar.gz'); blob=z.read(q)
    if hashlib.sha256(blob).hexdigest()!=a['inner_tar_sha256']: fail('NAM inner tar')
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as t:
        ms=[m for m in t.getmembers() if m.isfile() and m.name.endswith('/neural_amp_modeler.so')]
        if len(ms)!=1: fail('NAM plugin selection')
        f=t.extractfile(ms[0])
        if f is None or digest_stream(f)[1]!=a['plugin_sha256']: fail('NAM plugin hash')
    ok('NAM recovery tar + LV2 binary')

def inspect_blackblue(path,a):
    audio=sfz=sample_bytes=0; dark=None
    with tarfile.open(path,'r:') as t:
        for m in t:
            if not m.isfile(): continue
            low=m.name.lower()
            if low.endswith(('.wav','.flac','.aif','.aiff')):
                audio+=1; sample_bytes+=m.size
            if low.endswith('.sfz'): sfz+=1
            if m.name.endswith('/Programs/01-darkblack_keysw.sfz'):
                f=t.extractfile(m)
                if f is not None: dark=digest_stream(f)[1]
    if audio!=a['sample_files'] or sample_bytes!=a['sample_bytes'] or sfz!=a['sfz_files']: fail('BlackBlue inventory')
    if dark!=a['dark_black_sha256']: fail('Dark Black hash')
    ok('BlackBlue inventory + Dark Black')

def inspect_vsco(path,a):
    sfz=wav=0
    with tarfile.open(path,'r:gz') as t:
        for m in t:
            if not m.isfile(): continue
            low=m.name.lower()
            if low.endswith('.sfz'): sfz+=1
            if low.endswith('.wav'): wav+=1
    if sfz!=a['sfz_files'] or wav!=a['wav_files']: fail('VSCO inventory')
    ok('VSCO inventory')
def metal(root,a):
    mp=staged(root,a['drive_manifest'])
    with zipfile.ZipFile(mp) as z:
        sums=z.read('SHA256SUMS').decode(); recovery=z.read('RECOVERY.txt').decode()
    exp={pathlib.PurePosixPath(m.group(2)).name:m.group(1) for line in sums.splitlines() if (m:=re.match(r'^([0-9a-f]{64})\s+(.+)$',line.strip()))}
    logical=hashlib.sha256()
    for obj in a['drive_objects']:
        p=staged(root,obj)
        with zipfile.ZipFile(p) as z:
            q=member(z); name=pathlib.PurePosixPath(q).name; ph=hashlib.sha256()
            with z.open(q) as f:
                while True:
                    b=f.read(CHUNK)
                    if not b: break
                    ph.update(b); logical.update(b)
        if exp.get(name)!=ph.hexdigest(): fail('Metal GTX part '+name)
    got=logical.hexdigest()
    if got!=a['logical_archive_sha256'] or got not in recovery: fail('Metal GTX reconstruction')
    ok('Metal GTX '+got)
def direct(root,a,key):
    obj=a['drive_objects'][0]; p=root/obj['name']
    if not p.is_file() or p.stat().st_size!=obj['bytes'] or sha(p)!=a[key]: fail(obj['name'])
    ok(obj['name'])
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--staging',required=True,type=pathlib.Path); ap.add_argument('--config',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]/'config'/'durable-recovery-v1.1.0.json'); x=ap.parse_args()
    c=json.loads(x.config.read_text()); a=c['assets']; root=x.staging
    if c.get('version')!='vm-v1.1.0' or not root.is_dir(): fail('configuration/staging')
    sforzando(root,a['sforzando'])
    avldrums(root,a['avldrums'])
    bb=chunked(root,a['black_and_blue'],'logical_tar_sha256',a['black_and_blue']['source_commit'],materialize=True)
    try: inspect_blackblue(bb,a['black_and_blue'])
    finally:
        if bb: bb.unlink(missing_ok=True)
    metal(root,a['metal_gtx'])
    vs=chunked(root,a['vsco_2_ce'],'archive_sha256',materialize=True)
    try: inspect_vsco(vs,a['vsco_2_ce'])
    finally:
        if vs: vs.unlink(missing_ok=True)
    nam(root,a['nam'])
    direct(root,a['obsidian'],'model_sha256')
    print('VM v1.1.0 durable recovery: PASS')
if __name__=='__main__': main()
