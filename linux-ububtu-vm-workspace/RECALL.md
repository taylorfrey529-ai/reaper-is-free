# linux-ububtu-vm-workspace — recall card

Use this file when a fresh ChatGPT workspace needs to recover the REAPER 7.79 Linux production environment without reconstructing it from assumptions.

## Identity

- Repository: `taylorfrey529-ai/reaper-is-free`
- Branch: `linux-ububtu-vm-workspace`
- Backup root: `linux-ububtu-vm-workspace/`
- Canonical backup commit retained by the handoff: `350f07895fbca399dfe0c50ca1e4c5723e9a9a58`
- Full local backup SHA-256: `c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`
- Historical handoff source-archive SHA-256: `92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84`
- Current committed raw-gzip repository transport SHA-256: `8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28`
- Integrity precedence and mismatch record: `SNAPSHOT-INTEGRITY.md`

`BOOT-HANDOFF.md` remains the detailed operational handoff, but `SNAPSHOT-INTEGRITY.md` supersedes its historical snapshot-transport wording where the two conflict. This file is the short operational index.

## Fresh-start sequence

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
git checkout linux-ububtu-vm-workspace
cd linux-ububtu-vm-workspace
bash scripts/verify-regression.sh
bash verify-runtime-bundles.sh /mnt/data
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
```

Reconstitute the restored snapshot into its canonical live roots if they are not already present:

```text
/mnt/data/ubuntu-desktop-workspace
/mnt/data/graphics-workspace
/mnt/data/virtual-apollo
```

Recover excluded third-party binaries only from runtime archives that match `RUNTIME-BUNDLES.md` hashes. REAPER must remain version **7.79 Linux x86_64**.

Then boot with:

```bash
python3 scripts/start-live-session.py
```

The launcher is path-independent inside the checkout. It starts/reuses X11/Openbox on `:88`, starts Virtual Apollo, verifies the REAPER audio continuity locks, opens the canonical `ASIO-Routing-Project.RPP`, and waits long enough to observe the real REAPER license/evaluation UI instead of racing it.

## Continuity locks

```text
Desktop: X11 / Openbox
Display: :88
Geometry: 1440x900 where supported
REAPER: 7.79 Linux x86_64
Project: ASIO-Routing-Project
Backend: ALSA
linux_audio_mode: 1
Interface: apollo_spdif
S/PDIF: stereo 2-in / 2-out
Sample rate: 48000 Hz
Buffer: 256 samples x 3
Tempo: 120 BPM
Meter: 4/4
```

Never change `linux_audio_mode=1` to `0`; `0` previously selected JACK and caused the audio-hardware/JACK-server regression.

## License/evaluation behavior

The backup preserves REAPER's legitimate license/evaluation state. The launcher must **not** click, hide, suppress, patch, or bypass a REAPER activation/evaluation prompt. A verified 2026-09-08 boot displayed a main title containing `REAPER v7.79 - EVALUATION LICENSE` and the normal evaluation dialog. On a licensed future installation, `activation_window_detected=false` is not itself a failure.

## Restore transport compatibility

Do not manually run `base64 -d source-snapshot.tar.gz.b64` as a recovery shortcut. GitHub currently stores raw gzip bytes at that historical `.b64` path. `restore.sh` detects gzip vs base64, verifies the result against the admitted identities in `SHA256SUMS`, validates the tar stream, and only then extracts it. `SNAPSHOT-INTEGRITY.md` explains why the historical handoff hash and the committed repository transport hash are both retained.

## State vocabulary

- **Restored** — byte/config state recovered from the backup and checksum-validated.
- **Reconstructed** — an excluded runtime component recreated or rehydrated from an authoritative runtime bundle.
- **Verified live** — actually executed and observed in the current workspace.

Do not describe reconstructed runtime state as byte-identical restoration without checksum evidence.

## Regression gate

Before publishing further backup changes, run:

```bash
bash scripts/verify-regression.sh
```

The repository CI workflow runs the same source/config regression gate on changes to this workspace. It verifies both snapshot transport forms, checksum identity, Python launcher syntax, and the canonical ALSA/Virtual-Apollo continuity tokens.
