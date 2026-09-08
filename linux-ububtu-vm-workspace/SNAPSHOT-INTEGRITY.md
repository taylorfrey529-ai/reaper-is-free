# Snapshot integrity and transport identities

This file exists to prevent a discovered restore regression from being forgotten.

## Verified facts

The handoff and canonical backup commit `350f07895fbca399dfe0c50ca1e4c5723e9a9a58` record the historical source/config archive SHA-256 as:

`92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84`

The exact full local backup independently verified at 6,456,501 bytes is:

`c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`

During a clean GitHub Actions checkout on 2026-09-08, the actual bytes committed at `linux-ububtu-vm-workspace/source-snapshot.tar.gz.b64` were detected as **raw gzip**, not textual base64, and hashed to:

`8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28`

That committed repository transport hash is now explicitly recorded in `SHA256SUMS` instead of being silently conflated with the historical source-archive hash.

## Precedence

1. When available, the full local backup with SHA-256 `c67b69…bb31` is the strongest byte-level recovery authority.
2. The GitHub source/config payload may be used only when its decoded/raw archive bytes match either the historical source-archive identity or the explicitly recorded committed repository-transport identity.
3. After hash admission, the tar must validate and the regression gate must confirm the canonical ALSA / `apollo_spdif` continuity locks before the snapshot is treated as recoverable.
4. Runtime archives remain separate and must match `RUNTIME-BUNDLES.md`.

## Why two source hashes are retained

They describe two observed byte identities, not two silently interchangeable backups. The historical handoff hash is preserved for provenance. The repository transport hash describes what GitHub actually stores at the historical `.b64` path. Deleting either value would erase evidence of the mismatch and make the restore failure likely to recur.

`restore.sh` therefore detects gzip vs base64 by bytes, verifies against the admitted identities, validates the tar stream, and only then extracts it.
