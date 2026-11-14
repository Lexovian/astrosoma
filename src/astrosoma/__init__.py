"""AstroSoma — Autonomous Bioneural & Homeostatic Astronaut Health Monitoring."""

from .codec_werr24 import (
    FRAME_SIZE_BYTES,
    MAGIC_BYTE,
    PROTOCOL_VERSION,
    VitalsFrame,
    crc16_ccitt,
    pack_werr24,
    simulate_seu_bitflip,
    unpack_werr24,
    werr_homeostatic_index,
)
from .clinical_triage import (
    ANATOMY_REGIONS,
    ENVIRONMENTS,
    INDICATOR_SPECS,
    evaluate_astronaut_state,
)
from .pedagogy_engine import (
    ROUTINE_QUESTS,
    CREW_QUIZZES,
    compute_gamification_state,
    evaluate_learning_gate,
    get_non_medical_brief,
)

__version__ = "1.0.0"

__all__ = [
    "ANATOMY_REGIONS",
    "CREW_QUIZZES",
    "ENVIRONMENTS",
    "FRAME_SIZE_BYTES",
    "INDICATOR_SPECS",
    "MAGIC_BYTE",
    "PROTOCOL_VERSION",
    "ROUTINE_QUESTS",
    "VitalsFrame",
    "__version__",
    "compute_gamification_state",
    "crc16_ccitt",
    "evaluate_astronaut_state",
    "evaluate_learning_gate",
    "get_non_medical_brief",
    "pack_werr24",
    "simulate_seu_bitflip",
    "unpack_werr24",
    "werr_homeostatic_index",
]
