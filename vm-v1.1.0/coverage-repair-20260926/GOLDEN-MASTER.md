# VM v1.1.0 Golden Master Promotion

Promotion date: 2026-09-26

## Authority

Owner authorization was given by the explicit continuation command after the owner-gated coverage-repair certification.

## Canonical promotion

- Repository: `taylorfrey529-ai/reaper-is-free`
- Canonical branch: `linux-ububtu-vm-workspace`
- Promotion PR: #8 — `vm-v1.1.0: promote coverage repair certification`
- Merged repair commit: `ae94d736e48992788997b576871173e21aa1c200`
- Golden Master anchor branch: `golden-master/vm-v1.1.0-20260926`

The candidate recovery manifest is retained unchanged as pre-promotion evidence; its `golden_master_promoted: false` field records the gate state before this promotion.

## Fresh promotion gates

- Cold candidate verifier: 18 PASS / 0 FAIL
- Embedded workspace feature verifier: 37 PASS / 0 FAIL
- Main-instance Sunwell regression from certification turn: 25 PASS / 0 FAIL
- GitHub vm-v1.1.0 permanence contract: PASS
- GitHub Runtime Restore Bridge attempt 2: PASS
  - sforzando: PASS
  - AVLDrums: PASS
  - Black & Blue: PASS
  - VSCO 2 CE: PASS
- Virtual Apollo proof: 48 kHz / stereo / S32_LE, non-silent

## Continuity hashes

- Canonical project SHA-256:
  `2ea85263d6dc125bf7739264956a1ee1a8074c2b42f69b606b5e9d8b7e9771f1`
- REAPER configuration baseline SHA-256:
  `063451212000b02adebe69fbae97b7def547e8a90b53683c46ea946f6358e45c`

## Known retained boundary

In this reconstructed runtime, CLI `reaper -nonewinst <script.lua>` may start a secondary REAPER process rather than attaching to the canonical instance. The accepted live regression was therefore run from REAPER's Actions window inside the canonical process.

This file records the completed Golden Master promotion. It does not change audio assets, instrument libraries, the canonical RPP, or the durable Drive custody layout.
