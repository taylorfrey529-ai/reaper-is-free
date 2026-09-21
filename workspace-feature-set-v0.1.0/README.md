# workspace-feature-set-v0.1.0 — Frozen Source

Frozen from the verified Sunwell Gateway workspace on 2026-09-21.

- Base branch: `linux-ububtu-vm-workspace`
- Base commit: `a195c0b2fe522844a2450b0d4c456c6181dbd19e`
- Version: `0.1.0`
- Verification before publication: `37/37` checks passed
- Source archive SHA-256: `80008e442e913939d7b58464bd29397bef95b7eb0c0e6a18c7b7f034e7976666`

The complete source archive is stored as six binary chunks:
`source-freeze.tar.xz.part.000` through `source-freeze.tar.xz.part.005`.

Reconstruct it with:

```bash
cat source-freeze.tar.xz.part.* > workspace-feature-set-v0.1.0-source-freeze.tar.xz
sha256sum workspace-feature-set-v0.1.0-source-freeze.tar.xz
tar -xJf workspace-feature-set-v0.1.0-source-freeze.tar.xz
```

The archive contains the feature-set source, ReaScripts, JSFX, tests, manifests, documentation, and install/verification tooling. Large sample libraries are intentionally excluded; the feature set references the persistent VM libraries instead of duplicating them.

The live modified REAPER song was not saved or overwritten while freezing and publishing this checkpoint.
