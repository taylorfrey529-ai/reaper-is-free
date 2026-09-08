# Runtime bundle authority

Snapshot date: 2026-09-08

These are the exact runtime archives supplied alongside the current `linux-ububtu-vm-workspace` backup. They are external runtime payloads for reconstructing the workspace; the GitHub source/config backup remains the continuity authority for configuration and project state.

| Local archive | Bytes | Uncompressed bytes | Entries | SHA-256 | Identified role |
|---|---:|---:|---:|---|---|
| `toolchains.zip` | 326,141,054 | 711,138,556 | 10,578 | `568650bc01243a4eee7abaa6512ef4ae58e34e1a11c0178b7f76acbe57fec711` | Toolchain payload; inventory includes .NET SDK 10.0.302 Linux x64. |
| `audio(2).zip` | 53,274,996 | 281,693,197 | 10,703 | `093f590ba02b0284dc676d7f8ae499ead6fd93316524f7872cfa3c6fda0660bd` | Audio payload; inventory includes REAPER 7.79 Linux x86_64. |
| `operating-system.zip` | 96,356,195 | 96,330,906 | 6 | `060c674c9855aee0cb1c14a0e895c8cecfe2fb001a8fee12904956c5951fbb30` | Ubuntu 24.04.4 amd64 netboot operating-system payload. |
| `packages(2).zip` | 83,156,062 | 83,718,295 | 26 | `3a70c1dbdccdf68b766df2c68bcd82e597de7ffafdb8fd2d7f0ec86ffdcad1a2` | Ubuntu 24.04 amd64 package payload. |
| `graphics.zip` | 323,082,578 | 323,018,945 | 11 | `746fba7dbf8ef9a72c2596c51f57c81b5112f5537a6001989e2abcf9b907a72d` | Graphics payload; inventory includes Vulkan SDK 1.4.321.1 Linux x86_64. |

Total supplied archive bytes: **882,010,885**.

## GitHub storage boundary

The runtime archives themselves are not committed as ordinary Git blobs in this backup. `toolchains.zip` and `graphics.zip` exceed GitHub's normal 100 MB single-file limit, and the active GitHub connector does not expose Git LFS or release-asset upload. The remaining archives are also large binary payloads and are intentionally kept external rather than pretending a partial connector upload is a complete backup.

This document therefore binds the exact byte identities of the supplied runtime payloads. A future boot must validate the local archives against these hashes before treating them as the authoritative runtime inputs.

## Expected local locations

Preferred current-session locations:

```text
/mnt/data/toolchains.zip
/mnt/data/audio(2).zip
/mnt/data/operating-system.zip
/mnt/data/packages(2).zip
/mnt/data/graphics.zip
```

For continuity with earlier sessions, `audio.zip` may be accepted in place of `audio(2).zip`, and `packages.zip` in place of `packages(2).zip`, **only if the candidate file matches the SHA-256 recorded above**.

Run:

```bash
bash verify-runtime-bundles.sh /mnt/data
```

Do not infer equivalence from filename alone.
