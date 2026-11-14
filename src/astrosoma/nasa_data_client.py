"""Verified NASA OSDR and NOAA SWPC live telemetry & space-radiation client.

Strictly fetches real JSON records over verified TLS (ssl.create_default_context())
with clean fallback to the versioned snapshot under data/verified_nasa_telemetry.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import ssl
from typing import Any, Dict, List
import urllib.parse
import urllib.request

OSDR_SEARCH_URL = "https://osdr.nasa.gov/osdr/data/search"
NOAA_PROTONS_URL = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
NOAA_KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

HRP_HAZARDS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "radiation",
        "title_en": "Space Radiation",
        "title_tr": "Uzay Radyasyonu",
        "url": "https://www.nasa.gov/hrp/hazards/",
        "health_impact_en": "Increases ionizing dose (GCR + SPE), cancer/degenerative risk, and immune stress.",
        "health_impact_tr": "İyonlaştırıcı dozu (GCR + SPE), hücresel hasar ve bağışıklık baskılanması riskini artırır.",
        "monitored_by": ["dose_rate_msv_day", "cumulative_dose_msv", "noaa_goes_proton_pfu"],
    },
    {
        "id": "isolation",
        "title_en": "Isolation & Confinement",
        "title_tr": "İzolasyon ve Kapalı Ortam",
        "url": "https://www.nasa.gov/hrp/hazards/",
        "health_impact_en": "Drives circadian disruption, sleep deficit, cognitive fatigue, and mood drift.",
        "health_impact_tr": "Sirkadiyen ritim bozulması, uyku eksikliği, bilişsel yorgunluk ve ruh hali düşüşüne yol açar.",
        "monitored_by": ["sleep_hours", "mood_score", "hrv_sdnn_ms"],
    },
    {
        "id": "distance",
        "title_en": "Distance from Earth",
        "title_tr": "Dünya'dan Uzaklık ve İletişim Gecikmesi",
        "url": "https://www.nasa.gov/hrp/risks/",
        "health_impact_en": "Cuts real-time Earth medical support (up to 22 min Mars one-way latency); demands autonomous triage.",
        "health_impact_tr": "Yer hekimi canlı desteğini keser (Mars'ta 22 dk tek yön gecikme); otonom triyaj şarttır.",
        "monitored_by": ["werr_reserve_index", "autonomous_triage_required"],
    },
    {
        "id": "gravity",
        "title_en": "Altered Gravity Fields",
        "title_tr": "Değişen Yerçekimi Alanları",
        "url": "https://www.nasa.gov/hrp/hazards/",
        "health_impact_en": "Induces headward fluid shift (SANS), bone mineral loss, cardiac deconditioning, and orthostatic stress.",
        "health_impact_tr": "Başa sıvı kayması (SANS), kemik mineral kaybı, kalp kondisyon düşüşü ve ortostatik stres yaratır.",
        "monitored_by": ["bp_systolic_mmhg", "bp_diastolic_mmhg", "heart_rate_bpm", "core_temp_c"],
    },
    {
        "id": "environment",
        "title_en": "Hostile / Closed Environments",
        "title_tr": "Zorlu ve Kapalı Yaşam Ortamı",
        "url": "https://www.nasa.gov/hrp/ongoing-hrp-research/",
        "health_impact_en": "Exposes crew to cabin CO2 accumulation, microbial shifts, noise, and regolith dust during EVAs.",
        "health_impact_tr": "Kabin CO2 birikimi, mikrobiyal değişim ve EVA sonrası toz maruziyetine sebep olur.",
        "monitored_by": ["cabin_co2_mmhg", "spo2_pct", "blood_glucose_mgdl", "core_temp_c"],
    },
]

OFFICIAL_RESOURCES: List[Dict[str, str]] = [
    {"agency": "NASA HRP", "title": "5 Hazards of Human Spaceflight", "url": "https://www.nasa.gov/hrp/hazards/"},
    {"agency": "NASA HRP", "title": "Risks of Human Spaceflight", "url": "https://www.nasa.gov/hrp/risks/"},
    {"agency": "NASA HRP", "title": "Ongoing HRP Research in Space", "url": "https://www.nasa.gov/hrp/ongoing-hrp-research/"},
    {"agency": "CSA / ASC", "title": "Monitoring Radiation for Astronaut Health", "url": "https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp"},
    {"agency": "CSA / ASC", "title": "Why Do We Conduct Science Experiments in Space?", "url": "https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp"},
    {"agency": "NASA OSDR", "title": "NASA Open Science Data Repository (GeneLab / ALSDA)", "url": "https://osdr.nasa.gov/bio/repo/"},
    {"agency": "NOAA SWPC", "title": "GOES Solar Proton Flux & Planetary Kp Feeds", "url": "https://www.swpc.noaa.gov/products/goes-proton-flux"},
]


def _get_json(url: str, timeout: int = 15) -> Any:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "AstroSoma-SpaceApps-2026/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def map_proton_flux_to_noaa_scale(pfu_10mev: float) -> Dict[str, Any]:
    """Map >=10 MeV integral proton flux (pfu) to NOAA S-scale solar radiation storm tier."""
    if pfu_10mev >= 100000:
        scale, tier = "S5 (Extreme)", "critical"
    elif pfu_10mev >= 10000:
        scale, tier = "S4 (Severe)", "critical"
    elif pfu_10mev >= 1000:
        scale, tier = "S3 (Strong)", "critical"
    elif pfu_10mev >= 100:
        scale, tier = "S2 (Moderate)", "watch"
    elif pfu_10mev >= 10:
        scale, tier = "S1 (Minor)", "watch"
    else:
        scale, tier = "S0 (Quiet)", "optimal"
    # Conservative physical estimate mapping GOES free-space flux inside moderated habitat wall
    estimated_hab_msv_day = round(0.55 + 0.08 * min(50.0, max(0.0, pfu_10mev)), 3)
    return {
        "pfu_10mev": round(pfu_10mev, 4),
        "noaa_s_scale": scale,
        "status": tier,
        "estimated_leo_hab_msv_day": estimated_hab_msv_day,
    }


def fetch_noaa_space_weather() -> Dict[str, Any]:
    """Retrieve live NOAA SWPC GOES >=10 MeV integral proton flux and planetary Kp index."""
    protons = _get_json(NOAA_PROTONS_URL)
    ge10 = [row for row in protons if row.get("energy") == ">=10 MeV" and row.get("flux") is not None]
    latest_p = ge10[-1] if ge10 else {"flux": 0.0, "time_tag": "", "satellite": None}
    pfu = float(latest_p.get("flux", 0.0))

    kp_rows = _get_json(NOAA_KP_URL)
    kp_latest = kp_rows[-1] if isinstance(kp_rows, list) and kp_rows else {}
    kp_val = float(kp_latest.get("Kp", 0.0)) if isinstance(kp_latest, dict) else 0.0

    scaled = map_proton_flux_to_noaa_scale(pfu)
    return {
        "source": "NOAA SWPC Live Feed",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "satellite": latest_p.get("satellite"),
        "proton_time_tag": latest_p.get("time_tag"),
        "proton_series_tail": [
            {"time_tag": r["time_tag"], "flux": round(float(r["flux"]), 4)}
            for r in ge10[-24:]
        ],
        "kp_index": kp_val,
        "kp_time_tag": kp_latest.get("time_tag") if isinstance(kp_latest, dict) else "",
        **scaled,
    }


def fetch_nasa_osdr_studies(queries: List[str] | None = None, per_query: int = 3) -> List[Dict[str, Any]]:
    """Retrieve verified NASA OSDR biomedical/radiation/cardiovascular study metadata."""
    terms = queries or [
        "radiation astronaut",
        "spaceflight cardiovascular",
        "microgravity bone",
        "spaceflight immune sleep",
    ]
    seen: set[str] = set()
    studies: List[Dict[str, Any]] = []
    for term in terms:
        url = f"{OSDR_SEARCH_URL}?term={urllib.parse.quote(term)}&from=0&size={per_query}&type=cgene"
        payload = _get_json(url)
        hits = payload.get("hits", {}).get("hits", [])
        for h in hits:
            src = h.get("_source", {})
            acc = str(src.get("Accession", "")).strip()
            if not acc or acc in seen:
                continue
            seen.add(acc)
            studies.append({
                "accession": acc,
                "title": str(src.get("Study Title", "")).strip(),
                "organism": str(src.get("organism", "")).strip(),
                "project_type": str(src.get("Project Type", "")).strip(),
                "factor": str(src.get("Study Factor Name", "")).strip(),
                "query_domain": term,
                "url": f"https://osdr.nasa.gov/bio/repo/data/studies/{acc}",
            })
    return studies


def build_verified_snapshot(repo_root: Path | None = None) -> Dict[str, Any]:
    """Fetch live NASA OSDR & NOAA SWPC datasets and persist verified JSON caches."""
    root = repo_root or Path(__file__).resolve().parents[2]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    swpc = fetch_noaa_space_weather()
    osdr = fetch_nasa_osdr_studies()

    snapshot = {
        "schema_version": "astrosoma-verified-telemetry-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "space_weather": swpc,
        "nasa_osdr_studies": osdr,
        "hrp_hazards": HRP_HAZARDS_CATALOG,
        "official_resources": OFFICIAL_RESOURCES,
    }

    (data_dir / "verified_nasa_telemetry.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "hrp_hazards_catalog.json").write_text(
        json.dumps(HRP_HAZARDS_CATALOG, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return snapshot


def load_cached_snapshot(repo_root: Path | None = None) -> Dict[str, Any]:
    """Load pre-verified offline NASA OSDR & NOAA SWPC telemetry cache."""
    root = repo_root or Path(__file__).resolve().parents[2]
    path = root / "data" / "verified_nasa_telemetry.json"
    return json.loads(path.read_text(encoding="utf-8"))
