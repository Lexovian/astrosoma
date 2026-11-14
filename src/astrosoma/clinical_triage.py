"""Clinical guardrail evaluator, 7-region human anatomy mapping, and mission profiles.

Threshold guardrails are anchored to NASA-STD-3001 Vol. 2 environmental/medical
operational bands, AHA resting blood pressure/HR criteria, and ALARA ionizing
radiation limits, blended cleanly with AstroSoma's 0-SRAM homeostatic index.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .codec_werr24 import VitalsFrame, pack_werr24, werr_homeostatic_index

STATUS_RANK = {"optimal": 0, "watch": 1, "critical": 2}


@dataclass(frozen=True)
class EnvironmentProfile:
    id: str
    name_en: str
    name_tr: str
    gravity_g: float
    one_way_delay_sec: Tuple[float, float]
    comms_mode_en: str
    comms_mode_tr: str
    baseline_rad_msv_day: float
    shielding_note_en: str
    shielding_note_tr: str


ENVIRONMENTS: Dict[str, EnvironmentProfile] = {
    "spacecraft": EnvironmentProfile(
        id="spacecraft",
        name_en="Crew Spacecraft (Orion)",
        name_tr="Mürettebat Uzay Aracı (Orion)",
        gravity_g=0.0,
        one_way_delay_sec=(0.01, 1.3),
        comms_mode_en="Near-real-time / Lunar Transit Relay",
        comms_mode_tr="Yakın Gerçek Zamanlı / Ay Transit Rölesi",
        baseline_rad_msv_day=1.20,
        shielding_note_en="Use aft water-wall storm shelter if SPE >= 10 MeV alert triggers.",
        shielding_note_tr="SPE >= 10 MeV uyarısında arka su-duvarı radyasyon sığınağına geçin.",
    ),
    "station": EnvironmentProfile(
        id="station",
        name_en="Orbital Space Station (ISS)",
        name_tr="Yörünge Uzay İstasyonu (ISS)",
        gravity_g=0.0,
        one_way_delay_sec=(0.004, 0.25),
        comms_mode_en="Live Earth Flight Surgeon Link",
        comms_mode_tr="Canlı Yer Uçuş Hekimi Bağlantısı",
        baseline_rad_msv_day=0.55,
        shielding_note_en="Magnetosphere attenuates GCR; maintain US Lab / Zvezda sleep shielding.",
        shielding_note_tr="Manyetosfer GCR'yi azaltır; uyku kompartmanı kalkanlamasını koruyun.",
    ),
    "rover": EnvironmentProfile(
        id="rover",
        name_en="Pressurized Surface Rover",
        name_tr="Basınçlı Yüzey Keşif Aracı",
        gravity_g=0.165,
        one_way_delay_sec=(1.28, 2.5),
        comms_mode_en="Surface Relay + Autonomous EVA Loop",
        comms_mode_tr="Yüzey Rölesi + Otonom EVA Döngüsü",
        baseline_rad_msv_day=0.95,
        shielding_note_en="Monitor cabin CO2 scrubbers and EVA suit cooling loop closely.",
        shielding_note_tr="Kabin CO2 tutucularını ve EVA elbise soğutma devresini yakından izleyin.",
    ),
    "lunar_base": EnvironmentProfile(
        id="lunar_base",
        name_en="Artemis Lunar Habitat Base",
        name_tr="Artemis Ay Yaşam Üssü",
        gravity_g=0.165,
        one_way_delay_sec=(1.28, 1.4),
        comms_mode_en="2.6 s Round-Trip — Assisted Crew Autonomy",
        comms_mode_tr="2.6 sn Gidiş-Dönüş — Destekli Mürettebat Otonomisi",
        baseline_rad_msv_day=1.10,
        shielding_note_en="Regolith overburden cuts SPE dose; log post-EVA regolith dust exposure.",
        shielding_note_tr="Regolit örtü SPE dozunu düşürür; EVA sonrası toz maruziyetini kaydedin.",
    ),
    "mars_transit": EnvironmentProfile(
        id="mars_transit",
        name_en="Mars Transit & Surface Habitat",
        name_tr="Mars Transit ve Yüzey Yaşam Üssü",
        gravity_g=0.38,
        one_way_delay_sec=(180.0, 1320.0),
        comms_mode_en="Autonomous On-Board Triage (Up to 22-min Signal Delay)",
        comms_mode_tr="Otonom Araç İçi Triyaj (22 Dakikaya Varan Sinyal Gecikmesi)",
        baseline_rad_msv_day=1.80,
        shielding_note_en="Earth surgeons cannot intervene live; execute 0-SRAM self-care protocols immediately.",
        shielding_note_tr="Yer hekimleri canlı müdahale edemez; 0-SRAM öz-bakım protokolünü anında uygulayın.",
    ),
}


# (key, label_en, label_tr, unit, region_id, opt_low, opt_high, warn_low, warn_high)
INDICATOR_SPECS: Tuple[Tuple[str, str, str, str, str, float, float, float, float], ...] = (
    ("heart_rate_bpm", "Heart Rate", "Kalp Atış Hızı", "BPM", "cardio", 50.0, 95.0, 42.0, 118.0),
    ("bp_systolic_mmhg", "Systolic BP", "Sistolik Tansiyon", "mmHg", "cardio", 95.0, 128.0, 86.0, 145.0),
    ("bp_diastolic_mmhg", "Diastolic BP", "Diyastolik Tansiyon", "mmHg", "cardio", 60.0, 84.0, 50.0, 94.0),
    ("hrv_sdnn_ms", "ECG HRV (SDNN)", "EKG Kalp Hızı Değişkenliği", "ms", "cardio", 35.0, 160.0, 22.0, 220.0),
    ("spo2_pct", "Blood Oxygen (SpO2)", "Kan Oksijeni (SpO2)", "%", "resp", 95.0, 100.0, 91.5, 100.0),
    ("cabin_co2_mmhg", "Cabin pCO2", "Kabin Kısmi CO2", "mmHg", "resp", 0.0, 2.5, 0.0, 4.2),
    ("core_temp_c", "Core Body Temp", "Vücut Çekirdek Sıcaklığı", "°C", "musculo", 36.2, 37.5, 35.4, 38.2),
    ("blood_glucose_mgdl", "Blood Glucose", "Kan Şekeri", "mg/dL", "metab", 75.0, 130.0, 65.0, 175.0),
    ("sleep_hours", "Sleep Duration (24h)", "Uyku Süresi (24 sa)", "h", "neuro", 6.5, 9.5, 5.2, 11.0),
    ("mood_score", "Behavioral / Mood Index", "Ruh Hali ve Bilişsel Denge", "/10", "neuro", 6.5, 10.0, 4.5, 10.0),
    ("dose_rate_msv_day", "Radiation Dose Rate", "Radyasyon Doz Hızı", "mSv/day", "immune_rad", 0.0, 1.5, 0.0, 4.5),
    ("cumulative_dose_msv", "Cumulative Mission Dose", "Kümülatif Görev Dozu", "mSv", "immune_rad", 0.0, 350.0, 0.0, 550.0),
)


ANATOMY_REGIONS: Dict[str, Dict[str, Any]] = {
    "neuro": {
        "id": "neuro",
        "title_en": "Neuro-Vestibular & Circadian Core",
        "title_tr": "Nöro-Vestibüler ve Sirkadiyen Sistem",
        "hrp_hazards": ["Isolation & Confinement", "Distance from Earth", "Gravity Fields"],
        "indicators": ["sleep_hours", "mood_score"],
    },
    "ocular": {
        "id": "ocular",
        "title_en": "Ocular & Cephalad Fluid (SANS)",
        "title_tr": "Göz ve Kafa İçi Sıvı Basıncı (SANS)",
        "hrp_hazards": ["Gravity Fields", "Hostile/Closed Environments"],
        "indicators": ["bp_systolic_mmhg", "cabin_co2_mmhg"],
    },
    "cardio": {
        "id": "cardio",
        "title_en": "Cardiovascular & Lead-II ECG",
        "title_tr": "Kardiyovasküler Sistem ve EKG",
        "hrp_hazards": ["Gravity Fields", "Space Radiation", "Isolation & Confinement"],
        "indicators": ["heart_rate_bpm", "bp_systolic_mmhg", "bp_diastolic_mmhg", "hrv_sdnn_ms"],
    },
    "resp": {
        "id": "resp",
        "title_en": "Respiratory & Habitat Atmosphere",
        "title_tr": "Solunum ve Kabin Atmosferi",
        "hrp_hazards": ["Hostile/Closed Environments"],
        "indicators": ["spo2_pct", "cabin_co2_mmhg"],
    },
    "metab": {
        "id": "metab",
        "title_en": "Metabolic & Glycemic Balance",
        "title_tr": "Metabolik ve Glisemik Denge",
        "hrp_hazards": ["Isolation & Confinement", "Distance from Earth"],
        "indicators": ["blood_glucose_mgdl", "sleep_hours"],
    },
    "musculo": {
        "id": "musculo",
        "title_en": "Musculoskeletal & Thermoregulation",
        "title_tr": "Kas-İskelet ve Isı Düzenleme",
        "hrp_hazards": ["Gravity Fields", "Hostile/Closed Environments"],
        "indicators": ["core_temp_c", "sleep_hours"],
    },
    "immune_rad": {
        "id": "immune_rad",
        "title_en": "Immune Defense & Radiation Shielding",
        "title_tr": "Bağışıklık ve Radyasyon Kalkanlama",
        "hrp_hazards": ["Space Radiation", "Hostile/Closed Environments", "Distance from Earth"],
        "indicators": ["dose_rate_msv_day", "cumulative_dose_msv", "mood_score"],
    },
}


def _classify_indicator(value: float, opt_lo: float, opt_hi: float, warn_lo: float, warn_hi: float) -> str:
    if opt_lo <= value <= opt_hi:
        return "optimal"
    if warn_lo <= value <= warn_hi:
        return "watch"
    return "critical"


def _recommended_actions(indicators: Dict[str, Dict[str, Any]], env: EnvironmentProfile) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []

    if indicators["dose_rate_msv_day"]["status"] != "optimal":
        actions.append({
            "priority": indicators["dose_rate_msv_day"]["status"],
            "title_en": "Activate ALARA Radiation Shielding Protocol",
            "title_tr": "ALARA Radyasyon Kalkanlama Protokolünü Başlat",
            "detail_en": env.shielding_note_en,
            "detail_tr": env.shielding_note_tr,
        })
    if indicators["spo2_pct"]["status"] != "optimal" or indicators["cabin_co2_mmhg"]["status"] != "optimal":
        actions.append({
            "priority": "critical" if (indicators["spo2_pct"]["status"] == "critical" or indicators["cabin_co2_mmhg"]["status"] == "critical") else "watch",
            "title_en": "Verify O2 Partial Pressure & CDRA CO2 Scrubber",
            "title_tr": "O2 Kısmi Basıncını ve CO2 Tutucu Devreyi Kontrol Et",
            "detail_en": "Rest upright, verify pulse oximeter finger perfusion warm-up, and inspect cabin airflow fans.",
            "detail_tr": "Dik oturun, parmak ucu sıcaklığını kontrol edip nabız oksimetreyi yenileyin ve kabin havalandırma fanlarını doğrulayın.",
        })
    if indicators["blood_glucose_mgdl"]["status"] != "optimal":
        val = indicators["blood_glucose_mgdl"]["value"]
        low = val < 75.0
        actions.append({
            "priority": indicators["blood_glucose_mgdl"]["status"],
            "title_en": "Correct Hypoglycemia Risk Immediately" if low else "Monitor Post-Meal Glycemic Elevation",
            "title_tr": "Düşük Kan Şekeri Riskini Hemen Dengele" if low else "Yüksek Glikoz Eğilimini İzle",
            "detail_en": "Consume 15 g fast oral carbohydrate gel & recheck in 15 min." if low else "Log hydration + light orbital cycling and repeat glucose check in 60 min.",
            "detail_tr": "15 g hızlı karbonhidrat jeli tüketin ve 15 dk sonra tekrar ölçün." if low else "Su tüketimini artırın, hafif egzersiz ekleyin ve 60 dk sonra ölçümü tekrarlayın.",
        })
    if indicators["heart_rate_bpm"]["status"] != "optimal" or indicators["bp_systolic_mmhg"]["status"] != "optimal":
        actions.append({
            "priority": "critical" if ("critical" in (indicators["heart_rate_bpm"]["status"], indicators["bp_systolic_mmhg"]["status"])) else "watch",
            "title_en": "Run 60-Second Seated ECG & Orthostatic Hydration Check",
            "title_tr": "60 Saniyelik Oturur EKG ve Sıvı Denge Kontrolü Yap",
            "detail_en": "Record 1-lead ECG strip, drink 250 mL electrolyte solution, and avoid sudden vertical posture shifts." if env.gravity_g > 0 else "Capture resting ECG strip, hydrate 250 mL, and repeat seated BP cuff reading after 5 min.",
            "detail_tr": "Tek kanallı EKG kaydı alın, 250 mL elektrolitli sıvı tüketin ve 5 dk dinlenip tansiyonu tekrarlayın.",
        })
    if indicators["sleep_hours"]["status"] != "optimal" or indicators["mood_score"]["status"] != "optimal":
        actions.append({
            "priority": "watch",
            "title_en": "Initiate Circadian Recovery & Behavioral Decompression",
            "title_tr": "Sirkadiyen Dinlenme ve Bilişsel Rahatlama Rutini Başlat",
            "detail_en": "Dim blue cabin LEDs 90 min pre-sleep and schedule crew private family uplink / mindfulness audio.",
            "detail_tr": "Uyku öncesi 90 dk mavi ışığı azaltın; kişisel sesli dinlenme / yer mesajı bloğu planlayın.",
        })

    if not actions:
        actions.append({
            "priority": "optimal",
            "title_en": "All Physiological Systems Nominal — Maintain Mission Routine",
            "title_tr": "Tüm Fizyolojik Sistemler Normal — Görev Rutinini Sürdür",
            "detail_en": "Continue scheduled ARED resistance training, hydration tracking, and evening log.",
            "detail_tr": "Planlı ARED direnç egzersizi, sıvı takibi ve akşam uyku kaydına devam edin.",
        })
    return actions


def evaluate_astronaut_state(vitals: VitalsFrame | Dict[str, Any]) -> Dict[str, Any]:
    """Run full clinical + 0-SRAM WERR-24 evaluation across all indicators and regions."""
    v = vitals if isinstance(vitals, VitalsFrame) else VitalsFrame(**vitals)
    env = ENVIRONMENTS.get(v.environment, ENVIRONMENTS["station"])
    frame = pack_werr24(v)
    werr = werr_homeostatic_index(v)

    indicators: Dict[str, Dict[str, Any]] = {}
    max_status = "optimal"
    for key, label_en, label_tr, unit, region, opt_lo, opt_hi, warn_lo, warn_hi in INDICATOR_SPECS:
        raw_val = float(getattr(v, key))
        st = _classify_indicator(raw_val, opt_lo, opt_hi, warn_lo, warn_hi)
        if STATUS_RANK[st] > STATUS_RANK[max_status]:
            max_status = st
        indicators[key] = {
            "key": key,
            "label_en": label_en,
            "label_tr": label_tr,
            "value": round(raw_val, 3),
            "unit": unit,
            "region": region,
            "status": st,
            "optimal_range": [opt_lo, opt_hi],
            "watch_range": [warn_lo, warn_hi],
        }

    # Combine explicit clinical status with WERR reserve check (high multi-modal load -> at least watch)
    overall_status = max_status
    if overall_status == "optimal" and werr["reserve_index"] < 0.58:
        overall_status = "watch"

    regions_out: Dict[str, Dict[str, Any]] = {}
    for reg_id, meta in ANATOMY_REGIONS.items():
        reg_status = "optimal"
        if reg_id == "ocular" and (v.bp_systolic_mmhg > 135 or v.cabin_co2_mmhg > 3.0):
            reg_status = "watch"
        for ind_key in meta["indicators"]:
            ind_st = indicators[ind_key]["status"]
            if STATUS_RANK[ind_st] > STATUS_RANK[reg_status]:
                reg_status = ind_st
        regions_out[reg_id] = {
            "id": reg_id,
            "title_en": meta["title_en"],
            "title_tr": meta["title_tr"],
            "status": reg_status,
            "hrp_hazards": meta["hrp_hazards"],
            "indicators": [indicators[k] for k in meta["indicators"]],
        }

    autonomous_required = env.one_way_delay_sec[1] >= 10.0

    return {
        "overall_status": overall_status,
        "autonomous_triage_required": autonomous_required,
        "environment": {
            "id": env.id,
            "name_en": env.name_en,
            "name_tr": env.name_tr,
            "gravity_g": env.gravity_g,
            "one_way_delay_sec": list(env.one_way_delay_sec),
            "comms_mode_en": env.comms_mode_en,
            "comms_mode_tr": env.comms_mode_tr,
        },
        "packet_hex": frame.hex(),
        "packet_bytes": len(frame),
        "werr_homeostatic": werr,
        "indicators": indicators,
        "anatomy_regions": regions_out,
        "actions": _recommended_actions(indicators, env),
    }
