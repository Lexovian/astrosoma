# Contributing to AstroSoma

Thank you for contributing to **AstroSoma** (`Lexovian/astrosoma`), an open-source Apache-2.0 astronaut health monitoring platform built for the **NASA Space Apps Challenge 2026**.

## Development Prerequisites

- **Python** `3.10+` (`pytest` for tests; `playwright` with Chromium only needed when regenerating slide PDFs)
- **Node.js** `18+` (required by the cross-runtime Python ↔ JavaScript parity test suite)

## Local Setup & Verification

```bash
git clone https://github.com/Lexovian/astrosoma.git
cd astrosoma

# Run full unit & Python<->JS bit-exact parity tests
python -m pytest -v tests/test_astrosoma_core.py

# Evaluate mission scenarios & inject a cosmic-ray Single-Event Upset test
PYTHONPATH=src python -m astrosoma.cli --scenario solar_storm --simulate-seu

# Refresh live NASA OSDR & NOAA SWPC verified snapshot (requires internet)
PYTHONPATH=src python -m astrosoma.cli --sync-nasa
```

## Regenerating Bilingual Presentation Decks

Slide decks under `demo/` and `docs/` are generated deterministically from verified telemetry snapshots:

```bash
PYTHONPATH=src python -m astrosoma.build_presentations
```

This updates:
- `demo/slides_en.html` and `demo/slides_tr.html`
- `docs/AstroSoma_Presentation_EN.pdf` and `docs/AstroSoma_Presentation_TR.pdf`

## Pull Request & Code Quality Standards

1. **Maintain bit-exact parity:** Any encoding or `werrHomeostaticIndex` math updates in `src/astrosoma/codec_werr24.py` or `clinical_triage.py` must be mirrored identically in `assets/js/werr24_core.js` so `test_python_to_javascript_werr24_bit_exact_parity` stays green.
2. **Never store neural weight matrices in mutable RAM:** Keep `weight_ram_bytes == 0` in the `WERR-24` core.
3. **Preserve non-diagnostic educational disclaimers & plain-language clarity:** AstroSoma assists non-medical crew members with structured triage and educational coaching; avoid clinical jargon in Tier 1 explanations and maintain bilingual EN/TR symmetry.
4. **Never commit secrets:** Keep API keys, tokens, and environment files outside the repository.
5. Verify tests pass locally (`python -m pytest -v`) before opening a Pull Request.

## License

Contributions are licensed under the **Apache License 2.0** (`LICENSE`).
