# Golden Master post-upload read-back verification

Golden Master: `GM-2026-09-08`

Golden Master ID:

```text
sha256:74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f
```

Verification date: 2026-09-08
Storage snapshot folder ID: `1XkDhdvB218Z5ttGNU3CZsL89RmmXU6Ij`
Golden Master admission commit: `6cd104cbf70237be473b7eda5dca058dcd182069`

## Method

The payloads were uploaded to the private Google Drive Golden Master snapshot and then downloaded back through the authenticated Drive connector. SHA-256 was recomputed over the downloaded bytes. For split transports, every downloaded part was verified individually and the ordered downloaded parts were concatenated as a byte stream; the aggregate stream was then checked against the original final archive SHA-256.

This is a post-upload proof. It does not infer integrity from file names, Drive IDs, sizes, timestamps, or upload success alone.

## Direct payload read-back

| Payload | Bytes | Read-back SHA-256 | Result |
|---|---:|---|---|
| `linux-ububtu-vm-workspace-backup.tar.gz` | 6,456,501 | `c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a` | PASS |
| `operating-system.zip` | 96,356,195 | `060c674c9855aee0cb1c14a0e895c8cecfe2fb001a8fee12904956c5951fbb30` | PASS |
| `packages.zip` | 83,156,062 | `3a70c1dbdccdf68b766df2c68bcd82e597de7ffafdb8fd2d7f0ec86ffdcad1a2` | PASS |
| `audio.zip` | 53,274,996 | `093f590ba02b0284dc676d7f8ae499ead6fd93316524f7872cfa3c6fda0660bd` | PASS |

## `toolchains.zip` split read-back

| Part | Bytes | Read-back SHA-256 | Result |
|---|---:|---|---|
| `part-00` | 67,108,864 | `f0b31daa590afed0f95dee3af1187ba285f7b7f9310aa342986fadb53461f864` | PASS |
| `part-01` | 67,108,864 | `92a5629a258764f65993a1b125beed4026a72dfe372bc4a170ca304157b1bc09` | PASS |
| `part-02` | 67,108,864 | `17f95eda91c0bb60d5a054ec7763f28ffe348a01a37a543cac18d6dad343e7a9` | PASS |
| `part-03` | 67,108,864 | `43a621acc3708d1fb3e939a5a7378dae31a769c8da73a6dcd5d8199233368150` | PASS |
| `part-04` | 57,705,598 | `388f86155848e8f5de27c442bf2181ecd160606f4b2a04f00d453c8e22254f43` | PASS |

Downloaded part bytes total: **326,141,054**.

Ordered downloaded-part stream SHA-256:

```text
568650bc01243a4eee7abaa6512ef4ae58e34e1a11c0178b7f76acbe57fec711
```

Result: **PASS** — byte-identical to the admitted `toolchains.zip`.

## `graphics.zip` split read-back

| Part | Bytes | Read-back SHA-256 | Result |
|---|---:|---|---|
| `part-00` | 67,108,864 | `31c6dbf2114b33948d4a6a1b0fa42b431ae5f40a16ac5e2280221a0524a22a8b` | PASS |
| `part-01` | 67,108,864 | `937cea7d1a43fb2c212be22c97fc18c7a7931fe238e2ac8f772a8f0be790f46a` | PASS |
| `part-02` | 67,108,864 | `c0d903af0d84f0ccb57e6507db4148e3a57cbbd9796960733706fe265a7e5661` | PASS |
| `part-03` | 67,108,864 | `85c02d49b97c121565a76b129c49eb7b141a913066a4382d827eca9cc6f7db51` | PASS |
| `part-04` | 54,647,122 | `0b5be2d3565811b6c014974e45268cbf5e389173fa83c50cbb806a21e9b28428` | PASS |

Downloaded part bytes total: **323,082,578**.

Ordered downloaded-part stream SHA-256:

```text
746fba7dbf8ef9a72c2596c51f57c81b5112f5537a6001989e2abcf9b907a72d
```

Result: **PASS** — byte-identical to the admitted `graphics.zip`.

## Complete payload result

All six required final payload identities were proven from stored/read-back bytes. The complete Golden Master payload set remains **888,467,386 bytes** and matches `golden-master/SHA256SUMS`.

Repository regression also passed on the Golden Master admission commit on both branches:

- `main`: workflow run `34267422001` — success.
- `linux-ububtu-vm-workspace`: workflow run `34267429320` — success.

The Golden Master is therefore **byte-preserved, read-back verified, and repository-admitted**.
