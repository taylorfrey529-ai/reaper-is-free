# Snapshot integrity and recovery provenance

This file records the 2026-09-08 GitHub restore regression and the repair that prevents it from recurring.

## Byte authorities

- Full local backup — **verified original authority**, 6,456,501 bytes:
  `c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`
- Historical source/config hash recorded by commit `350f07895fbca399dfe0c50ca1e4c5723e9a9a58`:
  `92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84`
- Corrupt GitHub blob that previously occupied `source-snapshot.tar.gz.b64` — **rejected, never restore from it**:
  `8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28`
- Current reconstructed source/config archive — deterministically rebuilt from the checksum-verified full local backup:
  `be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac`

## What happened

The historical `.b64` GitHub path actually contained raw gzip bytes. A fresh GitHub Actions checkout proved that blob did not match the handoff-recorded source hash. After temporarily recording its observed hash, the next regression run proved the gzip stream itself was truncated (`Unexpected EOF`). It is therefore retained only as a rejected historical identity in `SHA256SUMS`; it is not an admitted recovery source.

## Current repository snapshot

The valid current source/config snapshot was rebuilt from the independently verified full backup `c67b69…bb31`. Large generated WAVs, screenshots, wallpaper imagery, and third-party runtime binaries were excluded; source, configuration, project files, Openbox/X11 launchers, graphics scripts, and Virtual Apollo implementation/state were retained.

The archive is deterministic (`tar --sort=name`, fixed mtime/ownership, `gzip -n`) and stored as small UTF-8 base64 chunks under:

`source-snapshot.parts/part-*.b64`

Each part has its own SHA-256 in `source-snapshot.parts/SHA256SUMS`. `restore.sh` verifies every part, assembles/decodes the archive, verifies `be32a0…beac`, validates the tar stream, and only then extracts it.

## Precedence

1. Prefer the exact full local backup `c67b69…bb31` when available.
2. For GitHub-only recovery, use the current split source/config snapshot verified as `be32a0…beac`.
3. A separately recovered historical source archive may be accepted only if it exactly matches `92327d…ba84`.
4. Never accept `8276f6…1f28`; that identity is explicitly rejected as corrupt.
5. Runtime archives are independent and must pass `verify-runtime-bundles.sh`.

## State vocabulary

- **Restored** — recovered from a checksum-admitted backup/snapshot.
- **Reconstructed** — recreated from an admitted authority because an excluded or corrupt transport was unavailable.
- **Verified live** — actually executed and observed in the current runtime.
