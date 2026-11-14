"""Automated test & cross-runtime parity suite for AstroSoma."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from astrosoma.clinical_triage import (  # noqa: E402
    ANATOMY_REGIONS,
    ENVIRONMENTS,
    evaluate_astronaut_state,
)
from astrosoma.codec_werr24 import (  # noqa: E402
    FRAME_SIZE_BYTES,
    VitalsFrame,
    crc16_ccitt,
    pack_werr24,
    simulate_seu_bitflip,
    unpack_werr24,
    werr_homeostatic_index,
)
from astrosoma.cli import SCENARIOS  # noqa: E402
from astrosoma.nasa_data_client import (  # noqa: E402
    load_cached_snapshot,
    map_proton_flux_to_noaa_scale,
)
from astrosoma.pedagogy_engine import (  # noqa: E402
    compute_gamification_state,
    evaluate_learning_gate,
    get_non_medical_brief,
)


def test_werr24_roundtrip_and_zero_sram_guarantee():
    vitals = VitalsFrame(
        environment="mars_transit",
        heart_rate_bpm=78.4,
        bp_systolic_mmhg=124.0,
        bp_diastolic_mmhg=79.0,
        spo2_pct=97.65,
        core_temp_c=37.05,
        blood_glucose_mgdl=101.2,
        dose_rate_msv_day=1.842,
        sleep_hours=6.75,
        mood_score=7.5,
        hrv_sdnn_ms=48.0,
        cabin_co2_mmhg=2.3,
        cumulative_dose_msv=312.4,
    )
    frame = pack_werr24(vitals)
    assert len(frame) == FRAME_SIZE_BYTES == 24

    decoded = unpack_werr24(frame)
    assert decoded["magic_valid"] is True
    assert decoded["crc_valid"] is True
    assert decoded["environment"] == "mars_transit"
    rv = decoded["vitals"]
    assert rv.heart_rate_bpm == pytest.approx(78.4, abs=0.1)
    assert rv.bp_systolic_mmhg == 124.0
    assert rv.spo2_pct == pytest.approx(97.65, abs=0.01)
    assert rv.core_temp_c == pytest.approx(37.05, abs=0.01)
    assert rv.dose_rate_msv_day == pytest.approx(1.842, abs=0.001)

    werr = werr_homeostatic_index(vitals)
    assert werr["weight_ram_bytes"] == 0
    assert werr["packet_bytes"] == 24
    assert 0.0 <= werr["reserve_index"] <= 1.0


def test_seu_single_bit_flip_detected_across_every_bit():
    frame = pack_werr24(SCENARIOS["nominal"])
    for bit_idx in range(FRAME_SIZE_BYTES * 8):
        res = simulate_seu_bitflip(frame, bit_index=bit_idx)
        assert res["seu_detected_by_crc"] is True
        assert res["corrupted_neural_weights_bytes"] == 0


def test_clinical_triage_environments_and_anatomy_regions():
    assert set(ENVIRONMENTS.keys()) == {"spacecraft", "station", "rover", "lunar_base", "mars_transit"}
    assert len(ANATOMY_REGIONS) == 7

    nominal = evaluate_astronaut_state(SCENARIOS["nominal"])
    assert nominal["overall_status"] == "optimal"
    assert nominal["autonomous_triage_required"] is False

    mars = evaluate_astronaut_state(SCENARIOS["mars_blackout"])
    assert mars["autonomous_triage_required"] is True
    assert mars["overall_status"] in {"watch", "critical"}

    rover_crit = evaluate_astronaut_state(SCENARIOS["rover_hypoxia_co2"])
    assert rover_crit["overall_status"] == "critical"
    assert rover_crit["anatomy_regions"]["resp"]["status"] == "critical"
    assert rover_crit["anatomy_regions"]["metab"]["status"] == "critical"

    storm = evaluate_astronaut_state(SCENARIOS["solar_storm"])
    assert storm["anatomy_regions"]["immune_rad"]["status"] == "critical"


def test_learning_gate_and_gamification_ceit_behavior():
    fatigued = evaluate_learning_gate(quiz_streak=3, routine_adherence_pct=95.0, sleep_hours=4.5, mood_score=4.5)
    assert fatigued["zpd_tier"] == 1
    assert fatigued["adapted_for_non_medical_crew"] is True

    expert = evaluate_learning_gate(
        quiz_streak=3,
        routine_adherence_pct=90.0,
        sleep_hours=8.0,
        mood_score=9.0,
        crew_role="flight_surgeon_liaison",
    )
    assert expert["zpd_tier"] == 3

    for lang in ("en", "tr"):
        brief = get_non_medical_brief("cardio", lang=lang, tier=fatigued["zpd_tier"])
        assert brief["meaning"] and brief["measure"] and brief["action_tip"]

    gam = compute_gamification_state(["morning_vitals", "ared_bone", "radiation_sync"], quiz_correct_count=2, streak_days=4)
    assert gam["xp"] == (50 + 80 + 60) + (2 * 40) + (3 * 20)
    assert "ARED Iron Spine" in gam["badges"]
    assert "ALARA Shield Steward" in gam["badges"]


def test_verified_nasa_snapshot_and_noaa_scale():
    assert map_proton_flux_to_noaa_scale(0.2)["status"] == "optimal"
    assert map_proton_flux_to_noaa_scale(120.0)["status"] == "watch"
    assert map_proton_flux_to_noaa_scale(1500.0)["status"] == "critical"

    snap = load_cached_snapshot(ROOT)
    assert snap["schema_version"] == "astrosoma-verified-telemetry-v1"
    assert len(snap["nasa_osdr_studies"]) >= 5
    assert len(snap["hrp_hazards"]) == 5
    assert "noaa_s_scale" in snap["space_weather"]


def test_python_to_javascript_werr24_bit_exact_parity():
    node = shutil.which("node")
    assert node is not None, "Node.js is required for cross-runtime parity check"

    js_path = (ROOT / "assets" / "js" / "werr24_core.js").as_posix()
    payload = [v.to_dict() for v in SCENARIOS.values()]
    node_script = (
        f"const core = require('{js_path}');\n"
        "const fs = require('fs');\n"
        "const cases = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const out = cases.map((v) => {\n"
        "  const ev = core.evaluateAstronautState(v);\n"
        "  const seu = core.simulateSeuBitflip(core.packWerr24(v), 47);\n"
        "  return { hex: ev.packet_hex, reserve: ev.werr_homeostatic.reserve_index, status: ev.overall_status, seu_ok: seu.seu_detected_by_crc };\n"
        "});\n"
        "console.log(JSON.stringify(out));\n"
    )
    proc = subprocess.run(
        [node, "-e", node_script],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    js_results = json.loads(proc.stdout)

    for py_vitals, js_res in zip(SCENARIOS.values(), js_results):
        py_eval = evaluate_astronaut_state(py_vitals)
        assert js_res["hex"] == py_eval["packet_hex"]
        assert js_res["reserve"] == pytest.approx(py_eval["werr_homeostatic"]["reserve_index"], abs=1e-4)
        assert js_res["status"] == py_eval["overall_status"]
        assert js_res["seu_ok"] is True
        assert crc16_ccitt(pack_werr24(py_vitals)[:22]) == unpack_werr24(pack_werr24(py_vitals))["crc_received"]
