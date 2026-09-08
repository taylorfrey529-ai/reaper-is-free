# REAPER 7.79 Golden Master

Golden Master: `GM-2026-09-08`

Golden Master ID:

```text
sha256:74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f
```

The ID is the SHA-256 of `golden-master/SHA256SUMS`. That file records the final byte identity of every required payload. Total admitted payload size is **888,467,386 bytes**.

## Two-tier authority

1. **GitHub / `reaper-is-free`** stores source/config state, project state, manifests, hashes, boot/recovery logic, regression checks, and the complete Golden Master transport map.
2. **Private Google Drive binary tier** stores the exact runtime payload bytes. The snapshot folder is `REAPER 7.79 Golden Master/GM-2026-09-08`, Drive folder ID `1XkDhdvB218Z5ttGNU3CZsL89RmmXU6Ij`.

The Drive folder was private/not-shared when admitted. Treat it as immutable. A file is never admitted by name or Drive ID alone; SHA-256 verification is mandatory.

## Payloads

| Payload | Bytes | SHA-256 | Storage transport |
|---|---:|---|---|
| `linux-ububtu-vm-workspace-backup.tar.gz` | 6,456,501 | `c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a` | direct Drive file |
| `operating-system.zip` | 96,356,195 | `060c674c9855aee0cb1c14a0e895c8cecfe2fb001a8fee12904956c5951fbb30` | direct Drive file |
| `toolchains.zip` | 326,141,054 | `568650bc01243a4eee7abaa6512ef4ae58e34e1a11c0178b7f76acbe57fec711` | five ordered 64 MiB parts |
| `packages.zip` | 83,156,062 | `3a70c1dbdccdf68b766df2c68bcd82e597de7ffafdb8fd2d7f0ec86ffdcad1a2` | direct Drive file |
| `audio.zip` | 53,274,996 | `093f590ba02b0284dc676d7f8ae499ead6fd93316524f7872cfa3c6fda0660bd` | direct Drive file |
| `graphics.zip` | 323,082,578 | `746fba7dbf8ef9a72c2596c51f57c81b5112f5537a6001989e2abcf9b907a72d` | five ordered 64 MiB parts |

The large `toolchains.zip` and `graphics.zip` archives are split only for transport. Concatenating their ordered parts recreates the original archive bytes, and the final archive SHA-256 remains authoritative. Exact Drive file IDs and per-part hashes are recorded in `golden-master/MANIFEST.json`.

## Recovery gate

After downloading the Golden Master folder to one local directory, with the two part directories preserved, run:

```bash
bash golden-master/verify-golden-master.sh /path/to/GM-2026-09-08
```

The verifier checks every split part before assembly, reconstructs the two large archives when necessary, verifies all six final SHA-256 identities, and validates the tar/ZIP containers.

Then recover the repository-backed state and boot:

```bash
bash linux-ububtu-vm-workspace/restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
bash linux-ububtu-vm-workspace/verify-runtime-bundles.sh /path/to/GM-2026-09-08
python3 linux-ububtu-vm-workspace/scripts/start-live-session.py
```

## Admission rule

A future replacement is a new Golden Master, not a mutation of `GM-2026-09-08`. Create a new dated snapshot, compute new hashes, run regression/live verification, then explicitly promote it.
