#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, re, zipfile
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
def chunked(root,a,key,source=None):
    mp=staged(root,a['manifest'])
    with zipfile.ZipFile(mp) as z: m=json.loads(z.read(member(z,'manifest.json')))
    if source and m.get('source_commit')!=source: fail('source commit')
    if len(a['drive_objects'])!=len(m['parts']): fail('part count')
    logical=hashlib.sha256(); total=0
    for obj,part in zip(a['drive_objects'],m['parts']):
        p=staged(root,obj)
        with zipfile.ZipFile(p) as z:
            q=member(z); ph=hashlib.sha256(); n=0
            with z.open(q) as f:
                while True:
                    b=f.read(CHUNK)
                    if not b: break
                    ph.update(b); logical.update(b); n+=len(b); total+=len(b)
        if pathlib.PurePosixPath(q).name!=part['name'] or n!=part['size'] or ph.hexdigest()!=part['sha256']: fail('inner part '+part['name'])
    got=logical.hexdigest()
    if got!=m['logical_sha256'] or got!=a[key] or total!=m['logical_size']: fail('logical reconstruction')
    ok(m['logical_name']+' '+got)
def single_inner(root,a,suffix,key):
    p=staged(root,a['drive_objects'][0])
    with zipfile.ZipFile(p) as z:
        q=member(z,suffix)
        with z.open(q) as f: got=digest_stream(f)[1]
    if got!=a[key]: fail(suffix+' inner hash')
    ok(suffix+' '+got)
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
    single_inner(root,a['sforzando'],'LINUX_plogue-sforzando_1.982_x86_64.zip','source_archive_sha256')
    single_inner(root,a['avldrums'],'avldrums-exact.tar.gz','recovery_tar_sha256')
    chunked(root,a['black_and_blue'],'logical_tar_sha256',a['black_and_blue']['source_commit'])
    metal(root,a['metal_gtx'])
    chunked(root,a['vsco_2_ce'],'archive_sha256')
    single_inner(root,a['nam'],'astra-nam-gm2-linux.tar.gz','inner_tar_sha256')
    direct(root,a['obsidian'],'model_sha256')
    print('VM v1.1.0 durable recovery: PASS')
if __name__=='__main__': main()
