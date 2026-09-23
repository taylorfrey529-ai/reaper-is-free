# vm-v1.1.0 — REAPER 7.79 permanence layer

This branch hardens the Ultra Realism instrument/NAM runtime without silently reinstalling or substituting anything.

## Contract

The v1.1.0 gate is **verify-only and fail-closed**. It pins the known-good identities for:

- AVLDrums + Black Pearl kit
- Black & Blue Basses + Dark Black program
- Metal GTX library + stock XTracking + Clean DI XTracking
- sforzando runtime
- VSCO 2 CE 1.1.0 + local recovery archive
- Neural Amp Modeler LV2 + Obsidian model
- the exact 23-track Ultra Realism name/color contract
- DI-to-Neural routing roles and rhythm-Neural panning through a REAPER-side regression action

The Bass Neural model remains deliberately unassigned until the owner selects a separately verified bass-suitable NAM model. Obsidian is pinned only to the three guitar Neural tracks.

## Install into the restored VM

From a checkout of this branch:

```bash
git checkout vm-v1.1.0-permanence
bash vm-v1.1.0/bin/install-v1.1.0.sh
```

The installer copies only gate/config/script files. It does **not** install or modify instrument libraries, NAM models, REAPER projects, or plugins.

If every pinned asset is already present and correct, enter through:

```bash
/mnt/data/ubuntu-desktop-workspace/bin/enter-vm-v1.1.0.sh start
```

That entry runs the existing Sunwell asset gate first, then the v1.1.0 full permanence gate, and only then invokes the existing Sunwell gateway.

## Full vs fast verification

Full verification is the default and includes the 2.30 GB VSCO recovery-archive SHA-256.

For a diagnostic pass only:

```bash
VM_V110_FAST=1 bash /mnt/data/ubuntu-desktop-workspace/vm-v1.1.0/bin/verify-permanence-v1.1.0.sh
```

Fast mode never changes assets; it only skips the expensive VSCO archive digest while still requiring the archive to exist.

## REAPER live gate

After REAPER opens the retained Ultra Realism project, run:

```text
Scripts/Sunwell/Sunwell_VM_v1_1_0_Regression.lua
```

It verifies the exact 23-track order/colors, expected FX roles, DI-to-Neural receive topology, centered/muted-main-send clean guitar DIs, hard-panned L/R rhythm Neural tracks, and VM-local runtime sentinels. Its report is written to:

```text
/mnt/data/ubuntu-desktop-workspace/logs/vm-v1.1.0-reaper-regression.txt
```

No PASS from this source branch is a substitute for a fresh live REAPER + Virtual Apollo proof. Owner Golden Master/release promotion remains manual.

## Durable recovery custody

The external instrument/NAM recovery layer is pinned in `config/durable-recovery-v1.1.0.json`. Google Drive is durable custody; GitHub Actions artifacts are staging only.

After the Drive files named by that manifest have been staged into one local directory, verify them offline with:

```bash
python3 vm-v1.1.0/bin/verify-durable-recovery-v1.1.0.py --staging /path/to/staged-drive-files
```

The verifier performs no downloads, installs, repairs, or substitutions. It validates sforzando, AVL/Black Pearl, Black & Blue, Metal GTX, VSCO 2 CE, NAM, and Obsidian and reconstructs the chunked library digests fail-closed.
