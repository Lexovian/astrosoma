"""Command-line interface for AstroSoma telemetry evaluation, SEI testing & NASA sync."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .clinical_triage import evaluate_astronaut_state
from .codec_werr24 import VitalsFrame, pack_werr24, simulate_seu_bitflip
from .nasa_data_client import build_verified_snapshot
from .pedagogy_engine import compute_gamification_state, evaluate_learning_gate


SCENARIOS = {
    "nominal": VitalsFrame(environment="station"),
    "solar_storm": VitalsFrame(
        environment="lunar_base",
        heart_rate_bpm=98.0,
        bp_systolic_mmhg=134.0,
        bp_diastolic_mmhg=86.0,
        spo2_pct=97.0,
        core_temp_c=37.2,
        blood_glucose_mgdl=104.0,
        dose_rate_msv_day=6.4,
        sleep_hours=6.0,
        mood_score=6.0,
        hrv_sdnn_ms=34.0,
        cabin_co2_mmhg=2.4,
        cumulative_dose_msv=215.0,
    ),
    "rover_hypoxia_co2": VitalsFrame(
        environment="rover",
        heart_rate_bpm=122.0,
        bp_systolic_mmhg=148.0,
        bp_diastolic_mmhg=95.0,
        spo2_pct=90.2,
        core_temp_c=38.3,
        blood_glucose_mgdl=61.0,
        dose_rate_msv_day=1.1,
        sleep_hours=5.0,
        mood_score=4.2,
        hrv_sdnn_ms=20.0,
        cabin_co2_mmhg=4.8,
        cumulative_dose_msv=148.0,
    ),
    "mars_blackout": VitalsFrame(
        environment="mars_transit",
        heart_rate_bpm=88.0,
        bp_systolic_mmhg=131.0,
        bp_diastolic_mmhg=84.0,
        spo2_pct=96.5,
        core_temp_c=37.1,
        blood_glucose_mgdl=88.0,
        dose_rate_msv_day=2.1,
        sleep_hours=5.4,
        mood_score=5.5,
        hrv_sdnn_ms=31.0,
        cabin_co2_mmhg=3.1,
        cumulative_dose_msv=392.0,
    ),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AstroSoma 0-SRAM Astronaut Health CLI")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS.keys()), default="nominal")
    parser.add_argument("--environment", default=None, help="Override environment id")
    parser.add_argument("--simulate-seu", action="store_true", help="Run cosmic-ray bit-flip test")
    parser.add_argument("--sync-nasa", action="store_true", help="Fetch & save verified NASA OSDR + NOAA data")
    args = parser.parse_args(argv)

    if args.sync_nasa:
        snap = build_verified_snapshot(Path(__file__).resolve().parents[2])
        print(json.dumps({
            "synced_utc": snap["generated_utc"],
            "osdr_count": len(snap["nasa_osdr_studies"]),
            "noaa_s_scale": snap["space_weather"]["noaa_s_scale"],
            "kp_index": snap["space_weather"]["kp_index"],
        }, indent=2))
        return 0

    vitals = SCENARIOS[args.scenario]
    if args.environment:
        vitals = VitalsFrame(**{**vitals.to_dict(), "environment": args.environment})

    evaluation = evaluate_astronaut_state(vitals)
    gate = evaluate_learning_gate(sleep_hours=vitals.sleep_hours, mood_score=vitals.mood_score)
    gamify = compute_gamification_state(["morning_vitals", "ared_bone"], quiz_correct_count=2, streak_days=5)

    out = {
        "evaluation": evaluation,
        "learning_gate": gate,
        "gamification": gamify,
    }
    if args.simulate_seu:
        out["seu_resilience"] = simulate_seu_bitflip(pack_werr24(vitals), bit_index=47)

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
