# reaper-is-free — recall card

Use this as the repository-level entrypoint for recovering the REAPER 7.79 workspace without rebuilding from assumptions.

## Repository identity

```text
Repository: taylorfrey529-ai/reaper-is-free
Primary branch: main
Continuity branch: linux-ububtu-vm-workspace
Historical backup commit: 350f07895fbca399dfe0c50ca1e4c5723e9a9a58
Full local backup SHA-256: c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a
Current reconstructed GitHub source/config snapshot SHA-256: be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac
Golden Master: GM-2026-09-08
Golden Master ID: 74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f
Golden Master payload bytes: 888467386
```

## Fresh-start path

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
bash linux-ububtu-vm-workspace/scripts/verify-regression.sh
```

Retrieve the private Golden Master snapshot described by `GOLDEN-MASTER.md` / `golden-master/MANIFEST.json`, then verify it before using any payload:

```bash
bash golden-master/verify-golden-master.sh /path/to/GM-2026-09-08
bash linux-ububtu-vm-workspace/restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
bash linux-ububtu-vm-workspace/verify-runtime-bundles.sh /path/to/GM-2026-09-08
```

Then reconcile the admitted restored source/config into the canonical live roots and boot with:

```bash
python3 linux-ububtu-vm-workspace/scripts/start-live-session.py
```

Read these before changing recovery state:

- `GOLDEN-MASTER.md`
- `golden-master/MANIFEST.json`
- `linux-ububtu-vm-workspace/RECALL.md`
- `linux-ububtu-vm-workspace/BOOT-HANDOFF-CURRENT.md`
- `linux-ububtu-vm-workspace/SNAPSHOT-INTEGRITY.md`
- `linux-ububtu-vm-workspace/RUNTIME-BUNDLES.md`

## Canonical continuity locks

```text
REAPER 7.79 Linux x86_64
X11 / Openbox on :88
1440x900 where supported
ASIO-Routing-Project
ALSA: linux_audio_mode=1
apollo_spdif
2-in / 2-out stereo S/PDIF
48000 Hz
256 samples x 3
120 BPM / 4/4
```

Never regress `linux_audio_mode` to `0` (JACK). Preserve REAPER's legitimate license/evaluation UI and report it without bypassing it.

## State vocabulary

- **Restored** — checksum-admitted backup/snapshot state recovered.
- **Reconstructed** — recreated from an admitted authority.
- **Verified live** — actually executed and observed in the current runtime.
- **Golden Master admitted** — every required payload byte identity matches `golden-master/SHA256SUMS`; split transports also pass their per-part hashes and final reassembled hashes.

Do not describe reconstructed data as byte-identical historical restoration without matching checksum evidence.

## Audio continuity

The repository also retains the overhead-anchored drum alignment workflow. Stereo overheads remain fixed; close drum shells are aligned non-destructively to their corresponding overhead arrivals. Tom 1 is self-anchored to Tom 1 transients in the stereo overheads.
