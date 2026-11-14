# AstroSoma System Architecture

**AstroSoma** is a dual-layer, radiation-resilient health monitoring platform designed for **NASA Space Apps Challenge 2026** (*Create Health Monitoring Software for Astronauts on Space Missions*). It combines deterministic clinical safety guardrails with a zero-SRAM procedural homeostatic engine (`WERR-24`) and an adaptive Zone of Proximal Development (ZPD) UX (`LearningGate`) built for non-medical crew members.

---

## 1. Design Principles & Hazard Alignment

AstroSoma monitors all **5 NASA Human Research Program (HRP) Hazards of Human Spaceflight**:

1. **Space Radiation** — Daily dose rate (`mSv/day`), cumulative mission exposure (`mSv`), ALARA shelter triggers, and live NOAA SWPC GOES $\ge 10\text{ MeV}$ proton flux (`S0–S5`).
2. **Isolation & Confinement** — Sleep debt (`hours/24h`), behavioral mood score (`/10`), heart-rate variability (`SDNN ms`), circadian dimming prompts, and gamified daily adherence.
3. **Distance from Earth** — Autonomous onboard triage whenever one-way communication latency is $\ge 10\text{ s}$ (such as Mars transit up to `1320 s` / `22 min` one-way).
4. **Altered Gravity Fields** — Headward fluid shifts (SANS risk in `ocular` + `bp_systolic_mmhg` + `cabin_co2_mmhg`), cardiovascular deconditioning, and ARED bone/spine loading routines.
5. **Hostile / Closed Environments** — Cabin `pCO2` partial pressure (`mmHg`), blood `SpO2` (`%`), blood glucose (`mg/dL`), and core body temperature (`°C`).

---

## 2. Layer 1 & Layer 2: Dual-Layer Safety + 0-SRAM WERR-24 Core

AstroSoma never allows an opaque black-box model to override physiological safety:

- **Layer 1 — Explicit Clinical Guardrails (`src/astrosoma/clinical_triage.py`, `assets/js/werr24_core.js`):**
  Twelve physiological and habitat telemetry signals classify into `optimal`, `watch`, or `critical` across **7 interactive human anatomy regions** (`neuro`, `ocular`, `cardio`, `resp`, `metab`, `musculo`, `immune_rad`) using NASA-STD-3001 Vol. 2 / AHA / ALARA operational bounds. Explicit clinical alerts directly trigger concrete action cards.
- **Layer 2 — Zero-SRAM Procedural Homeostatic Index (`src/astrosoma/codec_werr24.py`):**
  Adapted from `Lexovian/WerrSoma` (Zenodo DOI: `10.5281/zenodo.22996625`). Four normalized physiological strain coordinates (`cardio`, `metabolic`, `neuro_behavioral`, `radiation_resp`) map onto the quadratic boundary iterator $z \to z^2 + c$ (`MAX_ESCAPE_ITER = 32`, `ESCAPE_RADIUS_SQ = 4.0`).
  - **Mutable neural weight RAM:** `0 bytes` (`weight_ram_bytes == 0`). There are no learned weight matrices in SRAM that a heavy-ion Single-Event Upset (SEU) can silently corrupt.
  - If an overall state passes single-variable bounds but shows compound multi-system strain (`reserve_index < 0.58`), AstroSoma conservatively promotes `overall_status` from `optimal` to `watch`.

---

## 3. Immutable 24-Byte `WERR-24` Frame Specification

Every vitals + environment snapshot packs deterministically into `24 bytes` (`192 bits`, big-endian struct `>BBHBBHHHHHBBHHH`) protected by `CRC-16/CCITT-FALSE` (polynomial `0x1021`, init `0xFFFF`):

| Byte Offset | Field | Format / Scaling |
| --- | --- | --- |
| `0` | Magic Header | `0xA5` (`uint8`) |
| `1` | Environment & Protocol Version | High nibble `env_id (0..4)`, Low nibble `0x1` (`uint8`) |
| `2..3` | Heart Rate | `round(HR_bpm * 10)` (`uint16`) |
| `4` | Systolic Blood Pressure | `SBP_mmHg` (`uint8`) |
| `5` | Diastolic Blood Pressure | `DBP_mmHg` (`uint8`) |
| `6..7` | Blood Oxygen (`SpO2`) | `round(SpO2_% * 100)` (`uint16`) |
| `8..9` | Core Body Temperature | `round((Temp_C - 30.0) * 100)` (`uint16`) |
| `10..11` | Blood Glucose | `round(Glucose_mgdL * 10)` (`uint16`) |
| `12..13` | Radiation Dose Rate | `round(Dose_mSv_day * 1000)` ($\mu\text{Sv/day}$, `uint16`) |
| `14..15` | Sleep Duration (24h) | `round(Sleep_h * 60)` (`minutes`, `uint16`) |
| `16` | Behavioral / Mood Index | `round(Mood * 10)` (`10..100`, `uint8`) |
| `17` | ECG HRV (SDNN) | `HRV_ms` (`uint8`) |
| `18..19` | Cabin `pCO2` | `round(pCO2_mmHg * 10)` (`uint16`) |
| `20..21` | Cumulative Mission Dose | `round(CumDose_mSv * 10)` (`uint16`) |
| `22..23` | Integrity Checksum | `CRC-16/CCITT-FALSE` over bytes `0..21` (`uint16`) |

Because Python (`codec_werr24.py`) and browser JavaScript (`assets/js/werr24_core.js`) implement identical rounding, scaling, bit packing, and IEEE-754 iteration math, `tests/test_astrosoma_core.py` enforces **bit-exact parity** on every CI push, alongside exhaustive 192-bit SEU bit-flip verification (`192/192` single-bit flips detected by CRC).

---

## 4. Five Supported Spaceflight Environments

| Profile ID | Mission Environment | Gravity (`g`) | One-Way Latency (`s`) | Autonomous Triage Required |
| --- | --- | --- | --- | --- |
| `spacecraft` | Crew Spacecraft (Orion) | `0.00` | `0.01 – 1.3` | `False` |
| `station` | Orbital Space Station (ISS) | `0.00` | `0.004 – 0.25` | `False` |
| `rover` | Pressurized Surface Rover | `0.165` | `1.28 – 2.5` | `False` |
| `lunar_base` | Artemis Lunar Habitat Base | `0.165` | `1.28 – 1.4` | `False` |
| `mars_transit` | Mars Transit & Surface Habitat | `0.38` | `180 – 1320` | `True` ($\ge 10\text{ s}$) |

---

## 5. Adaptive Non-Medical Crew UX (`LearningGate` / CEIT)

Adapted from Dr. Zerrin Dağlı's *Procedural Fractal Pedagogy* (`jesmaat/WerreduR`, SSRN `7641538`, Zenodo DOI `10.5281/zenodo.23128224`; Department of Computer Education and Instructional Technology (CEIT), Mersin University):

- **ZPD Cognitive-Load Controller (`evaluate_learning_gate`):** Computes `cognitive_reserve` from sleep and mood plus `mastery_index` from quiz streak and daily adherence:
  - **Tier 1:** Triggered automatically under fatigue or low reserve (`cognitive_reserve < 0.62` or `mastery_index < 0.40`). Surfaces plain-language analogies, measurement technique tips, and immediate corrective steps.
  - **Tier 2:** Applied space physiology coaching for active non-medical crew members.
  - **Tier 3:** Aerospace clinical and HRP research summaries when mastery and readiness are high.
- **Gamified Adherence Loop (`compute_gamification_state`):** Five daily mission check-ins (`290 XP` total routine base: Morning Vitals, 11:00 ARED Bone Loading, Hydration & Glucose Sync, Radiation & NOAA Sync, Evening Circadian Wind-Down) plus interactive situational quizzes (`+40 XP` per correct answer), streak bonuses, ranks, and achievement badges (`ARED Iron Spine`, `ALARA Shield Steward`, `Circadian Guardian`, `Crew Bio-Literacy Star`).

---

## 6. Edge Telemetry & Offline-First Data Pipeline

- **Live Space Weather:** Browser fetches NOAA SWPC GOES primary integral protons (`>=10 MeV`) and planetary `Kp` feeds directly (`Access-Control-Allow-Origin: *`).
- **Live NASA OSDR Proxy:** Because `osdr.nasa.gov/osdr/data/search` restricts cross-origin browser requests (`Access-Control-Allow-Origin: osdr.nasa.gov`), [functions/api/nasa-osdr.js](../functions/api/nasa-osdr.js) runs as a Cloudflare Pages Function at `/api/nasa-osdr` with 30-minute edge caching (`cacheTtl: 1800`).
- **Offline Snapshot:** `python -m astrosoma.cli --sync-nasa` refreshes verified JSON caches under `data/verified_nasa_telemetry.json` and `data/hrp_hazards_catalog.json` over TLS so spacecraft or air-gapped browsers always retain full mission reference datasets.
