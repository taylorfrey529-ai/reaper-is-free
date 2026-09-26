# VM v1.1.0 Coverage Repair Candidate — 2026-09-26

Owner-gated continuation package for the REAPER 7.79 workspace. It does not merge, promote, or overwrite the Golden Master.

## Certified repaired surface

The original ten reconstruction-coverage failures are now real runtime assets/state, not synthetic sentinels:

- Metal GTX sentinel + 2,739-audio floor
- Black & Blue Dark Black + Baby Blue + 2,208-audio floor
- ARIA Free Sounds Vol.1 / Garritan Jazz Piano Lite portable entry point
- AVLDrums LV2
- Neural Amp Modeler LV2 + Obsidian model
- sforzando 1.982 REAPER cache identity
- 38 unique Sunwell action registrations

`verify-current.sh` is read-only and fail-closed. It checks the ten requested items, pinned binary/SFZ/model hashes, and then runs the workspace feature verifier when available.

## Live evidence this continuation

Cold filesystem verification: 37 PASS / 0 FAIL.

Main-instance REAPER regression: 25 PASS / 0 FAIL, launched manually from REAPER's Actions window so it runs inside the canonical project instance.

Virtual Apollo proof: 48 kHz, 32-bit PCM, stereo, 30 s; peak approximately -2.00 / -2.06 dBFS; RMS approximately -24.93 / -25.35 dBFS.

Canonical project SHA-256 remains `2ea85263d6dc125bf7739264956a1ee1a8074c2b42f69b606b5e9d8b7e9771f1`.

## Important launcher boundary

In this container, `reaper -nonewinst <script.lua>` does **not** attach to the already-running canonical REAPER instance. It starts a second process; when that second process also opens the production audio configuration it can contend for the Apollo device. Therefore:

- do not use the CLI `workspace-feature-set regression` entry point while canonical REAPER is running;
- run `Sunwell_Regression_Check.lua` from **Actions > Show action list...** inside the existing REAPER window;
- or use `verify-current.sh` / `verify-feature-set.sh` for non-GUI regression;
- treat any future CLI-to-running-instance bridge as unverified until it proves single-process behavior.

This is a launcher/IPC limitation of the current reconstructed environment, not a REAPER-core audio failure.

## Durable recovery coordinates

See `recovery-manifest.json`. Heavy libraries remain outside Git history. Google Drive is the durable byte store; this source package records folder/file identities and logical archive SHA-256 values.
