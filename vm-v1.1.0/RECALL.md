# [Recall vm-v1.1.0]

## Authority

Repository: `taylorfrey529-ai/reaper-is-free`  
Candidate branch: `candidate/vm-v1.1.0-certified-hardening`  
Historical certified source branch: `vm-v1.1.0-permanence`  
Base continuity: `linux-ububtu-vm-workspace`  
REAPER: 7.79 Linux x86_64  
Canonical display: `:88` at 2560x1440x24  
Audio boundary: ALSA / `apollo_spdif_capture` + `apollo_spdif_playback` / 48 kHz

## Restore order

1. Restore the existing VM/workspace from admitted backups. Do not recreate instrument libraries from guesses.
2. Stage the complete durable Drive custody set locally and run the offline verifier.
3. If pinned runtime assets are missing or changed, stop REAPER and run `rehydrate-offline-v1.1.0.py --apply`; never auto-heal on ordinary startup.
4. Check out the admitted source revision and run `bash vm-v1.1.0/bin/install-v1.1.0.sh`.
5. Enter only through the v1.1.0 fail-closed launcher.
6. After the retained Ultra Realism project opens, run `Sunwell_VM_v1_1_0_Regression.lua`.
7. Run `verify-live-certification-v1.1.0.py` against the fresh 78/0 REAPER report, genuine 2560x1440 screenshot/recording, and the exact eight non-silent 48 kHz Virtual Apollo audition windows: drums, bass DI, L/R rhythm Neural, lead Neural, Strings High, Strings Low, Horns.
8. Keep Golden Master/release promotion owner-gated.

## Non-regression rules

- No automatic download, clone, package install, reinstallation, repair, or model substitution is allowed in the gate.
- Offline rehydration is a separate explicit owner-invoked cold operation. It must verify the entire durable set first, construct a complete replacement payload before promotion, preserve displaced runtime bytes under `recovery-backups/vm-v1.1.0/`, and roll back on failed post-install verification.
- Black & Blue, Metal GTX, AVLDrums, sforzando, VSCO 2 CE, NAM, the Obsidian guitar model, and the 23-track color/routing contract must verify before promotion.
- A missing or changed asset causes FAIL, not self-healing.
- The three Metal GTX clean-DI sampler instances remain independent.
- Metal GTX Clean DI recovery is deterministic and hash-pinned: stock XTracking -> exactly one `set_cc48=64` to `set_cc48=0` replacement -> approved Clean-DI SHA-256. A present mismatched derivative fails closed.
- The three guitar Neural tracks use the verified Obsidian NAM state; Bass Neural remains owner-select until a separately verified bass model is approved.
- Preserve the original Ultra Realism project/hash as authority; revisions are branches, not silent overwrites.
- Never infer a PASS from serialized plugin state alone. Live REAPER instantiation plus Virtual Apollo audio is the final runtime gate.
- The live certification verifier rejects evidence older than the current certification session, requires the full 78/0 in-REAPER report, all eight approved audition windows, rhythm L/R dominance, a real 2560x1440 screenshot, and a finalized 2560x1440 recording. Bass Neural is not an audition window until the owner approves a bass NAM model.
- Every audition WAV must be created by the verifier's `capture` command directly from `apollo_spdif_capture` at S32_LE / 48 kHz / stereo and retain a matching SHA-256 provenance sidecar; arbitrary external WAVs are not final-certification evidence.

## Current branch status

Source hardening is implemented. A fresh live `:88` re-application/cold-cycle remains the runtime certification gate.
Candidate `vm-v1.1.0/**` changes must produce raw-head push evidence for both the permanence contract and Runtime Restore Bridge. Pull-request merge-ref runs are separate merge-compatibility evidence and must not be mislabeled as exact-head certification.

## Durable recovery authority

- Custody manifest: `vm-v1.1.0/config/durable-recovery-v1.1.0.json`
- Offline verifier: `vm-v1.1.0/bin/verify-durable-recovery-v1.1.0.py`
- Explicit offline rehydrator: `vm-v1.1.0/bin/rehydrate-offline-v1.1.0.py`
- Fail-closed live certification verifier: `vm-v1.1.0/bin/verify-live-certification-v1.1.0.py`
- Durable Drive folder: `VM v1.1.0 Durable Recovery - 2026-09-23`
- The verifier must PASS after staging Drive bytes before a cold runtime restore is admitted.
- GitHub Actions artifacts are staging evidence only and are never the permanence authority.
