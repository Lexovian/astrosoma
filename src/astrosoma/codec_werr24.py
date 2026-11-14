"""24-byte WERR-24 telemetry codec and zero-SRAM procedural boundary evaluator.

Adapts the zero-storage procedural boundary core from Lexovian/WerrSoma
(Zenodo DOI: 10.5281/zenodo.22996625) for cosmic-radiation-resilient astronaut
health telemetry. No learned neural weights reside in mutable SRAM; packets carry
192-bit (24-byte) physiological state protected by CRC-16/CCITT-FALSE.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import struct
from typing import Any, Dict

MAGIC_BYTE = 0xA5
PROTOCOL_VERSION = 0x01
FRAME_SIZE_BYTES = 24
MAX_ESCAPE_ITER = 32
ESCAPE_RADIUS_SQ = 4.0

# >BBHBBHHHHHBBHHH -> 1+1 + 2+1+1 + 2+2+2+2+2 + 1+1 + 2+2+2 = 24 bytes
FRAME_STRUCT = struct.Struct(">BBHBBHHHHHBBHHH")

ENV_NAME_TO_ID = {
    "spacecraft": 0,
    "station": 1,
    "rover": 2,
    "lunar_base": 3,
    "mars_transit": 4,
}
ENV_ID_TO_NAME = {v: k for k, v in ENV_NAME_TO_ID.items()}


@dataclass(frozen=True)
class VitalsFrame:
    """Quantizable physiological + cabin environment telemetry snapshot."""

    environment: str = "station"
    heart_rate_bpm: float = 72.0
    bp_systolic_mmhg: float = 118.0
    bp_diastolic_mmhg: float = 76.0
    spo2_pct: float = 98.2
    core_temp_c: float = 36.9
    blood_glucose_mgdl: float = 95.0
    dose_rate_msv_day: float = 0.55
    sleep_hours: float = 7.2
    mood_score: float = 8.0
    hrv_sdnn_ms: float = 52.0
    cabin_co2_mmhg: float = 2.1
    cumulative_dose_msv: float = 124.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _clamp_int(val: float, lo: int, hi: int) -> int:
    rounded = int(math.floor(val + 0.5))
    return max(lo, min(hi, rounded))


def crc16_ccitt(data: bytes) -> int:
    """Compute CRC-16/CCITT-FALSE checksum over arbitrary bytes."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def pack_werr24(vitals: VitalsFrame | Dict[str, Any]) -> bytes:
    """Encode astronaut vitals and environment into an immutable 24-byte frame."""
    v = vitals if isinstance(vitals, VitalsFrame) else VitalsFrame(**vitals)
    env_id = ENV_NAME_TO_ID.get(v.environment, 1)
    meta = ((env_id & 0x0F) << 4) | (PROTOCOL_VERSION & 0x0F)

    hr_x10 = _clamp_int(v.heart_rate_bpm * 10.0, 0, 65535)
    sbp = _clamp_int(v.bp_systolic_mmhg, 0, 255)
    dbp = _clamp_int(v.bp_diastolic_mmhg, 0, 255)
    spo2_x100 = _clamp_int(v.spo2_pct * 100.0, 0, 10000)
    temp_off = _clamp_int((v.core_temp_c - 30.0) * 100.0, 0, 65535)
    glu_x10 = _clamp_int(v.blood_glucose_mgdl * 10.0, 0, 65535)
    dose_usv = _clamp_int(v.dose_rate_msv_day * 1000.0, 0, 65535)
    sleep_min = _clamp_int(v.sleep_hours * 60.0, 0, 1440)
    mood_x10 = _clamp_int(v.mood_score * 10.0, 10, 100)
    hrv = _clamp_int(v.hrv_sdnn_ms, 0, 255)
    co2_x10 = _clamp_int(v.cabin_co2_mmhg * 10.0, 0, 65535)
    cum_msv_x10 = _clamp_int(v.cumulative_dose_msv * 10.0, 0, 65535)

    body = FRAME_STRUCT.pack(
        MAGIC_BYTE,
        meta,
        hr_x10,
        sbp,
        dbp,
        spo2_x100,
        temp_off,
        glu_x10,
        dose_usv,
        sleep_min,
        mood_x10,
        hrv,
        co2_x10,
        cum_msv_x10,
        0,
    )[:22]
    checksum = crc16_ccitt(body)
    return body + struct.pack(">H", checksum)


def unpack_werr24(frame: bytes) -> Dict[str, Any]:
    """Decode a 24-byte WERR-24 packet and verify magic header + CRC-16 integrity."""
    if len(frame) != FRAME_SIZE_BYTES:
        raise ValueError(f"Expected {FRAME_SIZE_BYTES} bytes, got {len(frame)}")

    fields = FRAME_STRUCT.unpack(frame)
    (
        magic,
        meta,
        hr_x10,
        sbp,
        dbp,
        spo2_x100,
        temp_off,
        glu_x10,
        dose_usv,
        sleep_min,
        mood_x10,
        hrv,
        co2_x10,
        cum_msv_x10,
        crc_rx,
    ) = fields

    crc_calc = crc16_ccitt(frame[:22])
    env_id = (meta >> 4) & 0x0F
    version = meta & 0x0F

    return {
        "magic_valid": magic == MAGIC_BYTE,
        "version": version,
        "crc_valid": crc_rx == crc_calc and magic == MAGIC_BYTE,
        "crc_received": crc_rx,
        "crc_computed": crc_calc,
        "environment": ENV_ID_TO_NAME.get(env_id, "station"),
        "vitals": VitalsFrame(
            environment=ENV_ID_TO_NAME.get(env_id, "station"),
            heart_rate_bpm=round(hr_x10 / 10.0, 1),
            bp_systolic_mmhg=float(sbp),
            bp_diastolic_mmhg=float(dbp),
            spo2_pct=round(spo2_x100 / 100.0, 2),
            core_temp_c=round(30.0 + temp_off / 100.0, 2),
            blood_glucose_mgdl=round(glu_x10 / 10.0, 1),
            dose_rate_msv_day=round(dose_usv / 1000.0, 3),
            sleep_hours=round(sleep_min / 60.0, 2),
            mood_score=round(mood_x10 / 10.0, 1),
            hrv_sdnn_ms=float(hrv),
            cabin_co2_mmhg=round(co2_x10 / 10.0, 1),
            cumulative_dose_msv=round(cum_msv_x10 / 10.0, 1),
        ),
    }


def _dev(val: float, target: float, scale: float) -> float:
    return min(2.5, abs(val - target) / scale)


def werr_homeostatic_index(vitals: VitalsFrame | Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate zero-SRAM procedural boundary reserve (z -> z^2 + c) over quantized state.

    Zero neural weights are stored in SRAM; physiological homeostasis is mapped
    across the main Mandelbrot cardioid–period-2 stability locus so nominal states
    stay bounded while multi-modal overload smoothly escapes the boundary.
    """
    v = vitals if isinstance(vitals, VitalsFrame) else VitalsFrame(**vitals)

    # Four normalized physiological strain coordinates around mission baselines
    s_cardio = 0.45 * _dev(v.heart_rate_bpm, 70.0, 25.0) + 0.35 * _dev(v.bp_systolic_mmhg, 118.0, 28.0) + 0.20 * max(0.0, (42.0 - v.hrv_sdnn_ms) / 28.0)
    s_metab = 0.55 * _dev(v.blood_glucose_mgdl, 96.0, 32.0) + 0.45 * _dev(v.core_temp_c, 36.9, 1.1)
    s_neuro = 0.40 * max(0.0, (7.0 - v.sleep_hours) / 3.5) + 0.35 * max(0.0, (7.5 - v.mood_score) / 4.5) + 0.25 * max(0.0, (v.cabin_co2_mmhg - 2.0) / 3.0)
    s_rad_resp = 0.55 * max(0.0, (98.0 - v.spo2_pct) / 5.0) + 0.45 * max(0.0, (v.dose_rate_msv_day - 0.8) / 3.2)

    cx = -0.68 + 0.48 * min(2.0, 0.5 * (s_cardio + s_metab))
    cy = 0.14 + 0.46 * min(2.0, 0.5 * (s_neuro + s_rad_resp))

    zr, zi = 0.0, 0.0
    escape_iter = MAX_ESCAPE_ITER
    mag_sq = 0.0
    for step in range(MAX_ESCAPE_ITER):
        zr2 = zr * zr - zi * zi + cx
        zi2 = 2.0 * zr * zi + cy
        zr, zi = zr2, zi2
        mag_sq = zr * zr + zi * zi
        if mag_sq > ESCAPE_RADIUS_SQ:
            escape_iter = step + 1
            break

    strain_mean = 0.25 * (s_cardio + s_metab + s_neuro + s_rad_resp)
    # Bounded orbit reserve modulated by continuous strain magnitude
    boundary_ratio = escape_iter / float(MAX_ESCAPE_ITER)
    reserve_index = max(0.0, min(1.0, boundary_ratio * math.exp(-0.38 * strain_mean)))

    return {
        "c_real": round(cx, 6),
        "c_imag": round(cy, 6),
        "escape_iter": escape_iter,
        "max_iter": MAX_ESCAPE_ITER,
        "bounded_attractor": escape_iter == MAX_ESCAPE_ITER,
        "reserve_index": round(reserve_index, 4),
        "strain_vector": {
            "cardio": round(s_cardio, 4),
            "metabolic": round(s_metab, 4),
            "neuro_behavioral": round(s_neuro, 4),
            "radiation_resp": round(s_rad_resp, 4),
        },
        "weight_ram_bytes": 0,
        "packet_bytes": FRAME_SIZE_BYTES,
    }


def simulate_seu_bitflip(frame: bytes, bit_index: int = 19) -> Dict[str, Any]:
    """Inject a synthetic Single-Event Upset bit-flip to demonstrate CRC + 0-SRAM safety."""
    if len(frame) != FRAME_SIZE_BYTES:
        raise ValueError(f"Expected {FRAME_SIZE_BYTES} bytes, got {len(frame)}")
    total_bits = FRAME_SIZE_BYTES * 8
    idx = bit_index % total_bits
    byte_i, bit_i = divmod(idx, 8)
    corrupted = bytearray(frame)
    corrupted[byte_i] ^= 1 << bit_i
    decoded = unpack_werr24(bytes(corrupted))
    return {
        "flipped_bit": idx,
        "flipped_byte": byte_i,
        "corrupted_hex": bytes(corrupted).hex(),
        "seu_detected_by_crc": not decoded["crc_valid"],
        "corrupted_neural_weights_bytes": 0,
        "recovery_mode": "Reject corrupted telemetry packet; retain stateless arithmetic triage engine intact.",
    }
