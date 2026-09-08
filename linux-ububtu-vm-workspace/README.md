# linux-ububtu-vm-workspace

GitHub backup and recovery authority for the ChatGPT Linux/Ubuntu-style REAPER 7.79 workspace.

## Start here

- [`RECALL.md`](RECALL.md) — short fresh-session recovery card and one-command boot path.
- [`BOOT-HANDOFF.md`](BOOT-HANDOFF.md) — full recover -> restore -> desktop -> Virtual Apollo -> REAPER -> playback -> agent-ear -> screenshot acceptance procedure. For snapshot transport/hash discrepancies, `SNAPSHOT-INTEGRITY.md` has precedence.
- [`RUNTIME-BUNDLES.md`](RUNTIME-BUNDLES.md) — exact identities of external runtime payloads.
- [`BINARY-MANIFEST.md`](BINARY-MANIFEST.md) — known binary/audio/evidence identities.
- [`SNAPSHOT-INTEGRITY.md`](SNAPSHOT-INTEGRITY.md) — provenance and the admitted historical/repository snapshot byte identities.

Canonical backup commit retained by the handoff:

`350f07895fbca399dfe0c50ca1e4c5723e9a9a58`

## Regression-safe source restore

Run:

```bash
bash scripts/verify-regression.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
```

`restore.sh` detects the payload format by bytes, admits only hashes recorded in `SHA256SUMS`, validates the gzip/tar stream, and only then extracts. See `SNAPSHOT-INTEGRITY.md`: the handoff-recorded source archive hash and the raw-gzip bytes actually stored by GitHub are distinct identities and are deliberately preserved rather than silently conflated.

Historical handoff source-archive SHA-256:

`92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84`

Current committed raw-gzip repository transport SHA-256:

`8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28`

Full local compressed snapshot SHA-256:

`c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`

## Runtime bundles

Before using local runtime archives, run:

```bash
bash verify-runtime-bundles.sh /mnt/data
```

Filename alone is not authority; hashes must match `RUNTIME-BUNDLES.md`.

Large third-party/runtime binaries remain external to normal Git storage. The committed source/config snapshot contains the reproducible desktop, project/configuration, graphics source, and Virtual Apollo implementation required to reconstruct the live workspace.

## Live boot

Once the source/config roots and exact runtime dependencies are present:

```bash
python3 scripts/start-live-session.py
```

The launcher starts/reuses X11/Openbox on `:88`, starts Virtual Apollo, enforces the canonical REAPER ALSA/S/PDIF settings, opens the existing `ASIO-Routing-Project`, and reports the real REAPER license/evaluation UI state without bypassing it.

## Canonical audio state

```text
REAPER backend: ALSA (linux_audio_mode=1)
Interface: apollo_spdif
Stereo S/PDIF: 2 input / 2 output
Sample rate: 48 kHz
Buffer: 256 samples x 3
Project tempo: 120 BPM
Generated drum arrangement: 8 bars / 16 seconds
```

## Regression-prevention rule

Do not replace established backup state from assumptions. Preserve approved continuity, verify hashes before promotion, and run `scripts/verify-regression.sh` before publishing changes to this workspace.
