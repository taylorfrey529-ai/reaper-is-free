# Runtime bundle authority

Snapshot date: 2026-09-08
Golden Master: `GM-2026-09-08`
Golden Master ID: `sha256:74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f`

These are the exact runtime archives admitted for reconstructing the REAPER 7.79 Linux workspace. GitHub remains the source/config and recovery authority; exact binary payload bytes are preserved in the private Golden Master storage tier described by [`../GOLDEN-MASTER.md`](../GOLDEN-MASTER.md).

| Archive | Bytes | Uncompressed bytes | Entries | SHA-256 | Role |
|---|---:|---:|---:|---|---|
| `toolchains.zip` | 326,141,054 | 711,138,556 | 10,578 | `568650bc01243a4eee7abaa6512ef4ae58e34e1a11c0178b7f76acbe57fec711` | Toolchain payload; includes .NET SDK 10.0.302 Linux x64. |
| `audio.zip` | 53,274,996 | 281,693,197 | 10,703 | `093f590ba02b0284dc676d7f8ae499ead6fd93316524f7872cfa3c6fda0660bd` | Audio payload; includes REAPER 7.79 Linux x86_64. |
| `operating-system.zip` | 96,356,195 | 96,330,906 | 6 | `060c674c9855aee0cb1c14a0e895c8cecfe2fb001a8fee12904956c5951fbb30` | Ubuntu 24.04.4 amd64 netboot operating-system payload. |
| `packages.zip` | 83,156,062 | 83,718,295 | 26 | `3a70c1dbdccdf68b766df2c68bcd82e597de7ffafdb8fd2d7f0ec86ffdcad1a2` | Ubuntu 24.04 amd64 package payload. |
| `graphics.zip` | 323,082,578 | 323,018,945 | 11 | `746fba7dbf8ef9a72c2596c51f57c81b5112f5537a6001989e2abcf9b907a72d` | Graphics payload; includes Vulkan SDK 1.4.321.1 Linux x86_64. |

Runtime archive bytes total: **882,010,885**. Including the exact 6,456,501-byte full workspace backup, the Golden Master payload set totals **888,467,386 bytes**.

## Binary storage

The binary payloads are not ordinary Git blobs. They are preserved in the private Google Drive snapshot `REAPER 7.79 Golden Master/GM-2026-09-08` (folder ID `1XkDhdvB218Z5ttGNU3CZsL89RmmXU6Ij`).

`toolchains.zip` and `graphics.zip` are stored there as ordered 64 MiB parts because the direct large-file upload path rejected the complete archives. Per-part hashes and Drive IDs are in `../golden-master/MANIFEST.json`; concatenation must reproduce the final archive hash above before the payload is admitted.

## Local recovery

Canonical local names are the names in the table above. Earlier aliases `audio(2).zip` and `packages(2).zip` remain accepted only if their content hashes match.

Run either:

```bash
bash golden-master/verify-golden-master.sh /path/to/GM-2026-09-08
```

for the complete Golden Master gate, or:

```bash
bash linux-ububtu-vm-workspace/verify-runtime-bundles.sh /path/to/GM-2026-09-08
```

when the five runtime archives are already assembled.

Never infer equivalence from filenames, storage IDs, or timestamps alone.
