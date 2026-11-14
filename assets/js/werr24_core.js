/**
 * AstroSoma Core Engine — Browser & Node.js Cross-Runtime Parity Twin
 * Implements bit-exact WERR-24 packet framing, CRC-16/CCITT-FALSE, 0-SRAM
 * homeostatic reserve (z -> z^2 + c), NASA-STD-3001 clinical guardrails,
 * and CEIT LearningGate ZPD guidance (anchored to Lexovian/WerrSoma & jesmaat/WerreduR).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AstroSomaCore = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const MAGIC_BYTE = 0xA5;
  const PROTOCOL_VERSION = 0x01;
  const FRAME_SIZE_BYTES = 24;
  const MAX_ESCAPE_ITER = 32;
  const ESCAPE_RADIUS_SQ = 4.0;

  const ENV_NAME_TO_ID = {
    spacecraft: 0,
    station: 1,
    rover: 2,
    lunar_base: 3,
    mars_transit: 4,
  };
  const ENV_ID_TO_NAME = ['spacecraft', 'station', 'rover', 'lunar_base', 'mars_transit'];

  const ENVIRONMENTS = {
    spacecraft: {
      id: 'spacecraft',
      name_en: 'Crew Spacecraft (Orion)',
      name_tr: 'Mürettebat Uzay Aracı (Orion)',
      gravity_g: 0.0,
      one_way_delay_sec: [0.01, 1.3],
      comms_mode_en: 'Near-real-time / Lunar Transit Relay',
      comms_mode_tr: 'Yakın Gerçek Zamanlı / Ay Transit Rölesi',
      baseline_rad_msv_day: 1.2,
      shielding_note_en: 'Use aft water-wall storm shelter if SPE >= 10 MeV alert triggers.',
      shielding_note_tr: 'SPE >= 10 MeV uyarısında arka su-duvarı radyasyon sığınağına geçin.',
    },
    station: {
      id: 'station',
      name_en: 'Orbital Space Station (ISS)',
      name_tr: 'Yörünge Uzay İstasyonu (ISS)',
      gravity_g: 0.0,
      one_way_delay_sec: [0.004, 0.25],
      comms_mode_en: 'Live Earth Flight Surgeon Link',
      comms_mode_tr: 'Canlı Yer Uçuş Hekimi Bağlantısı',
      baseline_rad_msv_day: 0.55,
      shielding_note_en: 'Magnetosphere attenuates GCR; maintain US Lab / Zvezda sleep shielding.',
      shielding_note_tr: "Manyetosfer GCR'yi azaltır; uyku kompartmanı kalkanlamasını koruyun.",
    },
    rover: {
      id: 'rover',
      name_en: 'Pressurized Surface Rover',
      name_tr: 'Basınçlı Yüzey Keşif Aracı',
      gravity_g: 0.165,
      one_way_delay_sec: [1.28, 2.5],
      comms_mode_en: 'Surface Relay + Autonomous EVA Loop',
      comms_mode_tr: 'Yüzey Rölesi + Otonom EVA Döngüsü',
      baseline_rad_msv_day: 0.95,
      shielding_note_en: 'Monitor cabin CO2 scrubbers and EVA suit cooling loop closely.',
      shielding_note_tr: 'Kabin CO2 tutucularını ve EVA elbise soğutma devresini yakından izleyin.',
    },
    lunar_base: {
      id: 'lunar_base',
      name_en: 'Artemis Lunar Habitat Base',
      name_tr: 'Artemis Ay Yaşam Üssü',
      gravity_g: 0.165,
      one_way_delay_sec: [1.28, 1.4],
      comms_mode_en: '2.6 s Round-Trip — Assisted Crew Autonomy',
      comms_mode_tr: '2.6 sn Gidiş-Dönüş — Destekli Mürettebat Otonomisi',
      baseline_rad_msv_day: 1.1,
      shielding_note_en: 'Regolith overburden cuts SPE dose; log post-EVA regolith dust exposure.',
      shielding_note_tr: 'Regolit örtü SPE dozunu düşürür; EVA sonrası toz maruziyetini kaydedin.',
    },
    mars_transit: {
      id: 'mars_transit',
      name_en: 'Mars Transit & Surface Habitat',
      name_tr: 'Mars Transit ve Yüzey Yaşam Üssü',
      gravity_g: 0.38,
      one_way_delay_sec: [180.0, 1320.0],
      comms_mode_en: 'Autonomous On-Board Triage (Up to 22-min Signal Delay)',
      comms_mode_tr: 'Otonom Araç İçi Triyaj (22 Dakikaya Varan Sinyal Gecikmesi)',
      baseline_rad_msv_day: 1.8,
      shielding_note_en: 'Earth surgeons cannot intervene live; execute 0-SRAM self-care protocols immediately.',
      shielding_note_tr: 'Yer hekimleri canlı müdahale edemez; 0-SRAM öz-bakım protokolünü anında uygulayın.',
    },
  };

  const INDICATOR_SPECS = [
    ['heart_rate_bpm', 'Heart Rate', 'Kalp Atış Hızı', 'BPM', 'cardio', 50.0, 95.0, 42.0, 118.0],
    ['bp_systolic_mmhg', 'Systolic BP', 'Sistolik Tansiyon', 'mmHg', 'cardio', 95.0, 128.0, 86.0, 145.0],
    ['bp_diastolic_mmhg', 'Diastolic BP', 'Diyastolik Tansiyon', 'mmHg', 'cardio', 60.0, 84.0, 50.0, 94.0],
    ['hrv_sdnn_ms', 'ECG HRV (SDNN)', 'EKG Kalp Hızı Değişkenliği', 'ms', 'cardio', 35.0, 160.0, 22.0, 220.0],
    ['spo2_pct', 'Blood Oxygen (SpO2)', 'Kan Oksijeni (SpO2)', '%', 'resp', 95.0, 100.0, 91.5, 100.0],
    ['cabin_co2_mmhg', 'Cabin pCO2', 'Kabin Kısmi CO2', 'mmHg', 'resp', 0.0, 2.5, 0.0, 4.2],
    ['core_temp_c', 'Core Body Temp', 'Vücut Çekirdek Sıcaklığı', '°C', 'musculo', 36.2, 37.5, 35.4, 38.2],
    ['blood_glucose_mgdl', 'Blood Glucose', 'Kan Şekeri', 'mg/dL', 'metab', 75.0, 130.0, 65.0, 175.0],
    ['sleep_hours', 'Sleep Duration (24h)', 'Uyku Süresi (24 sa)', 'h', 'neuro', 6.5, 9.5, 5.2, 11.0],
    ['mood_score', 'Behavioral / Mood Index', 'Ruh Hali ve Bilişsel Denge', '/10', 'neuro', 6.5, 10.0, 4.5, 10.0],
    ['dose_rate_msv_day', 'Radiation Dose Rate', 'Radyasyon Doz Hızı', 'mSv/day', 'immune_rad', 0.0, 1.5, 0.0, 4.5],
    ['cumulative_dose_msv', 'Cumulative Mission Dose', 'Kümülatif Görev Dozu', 'mSv', 'immune_rad', 0.0, 350.0, 0.0, 550.0],
  ];

  const ANATOMY_REGIONS = {
    neuro: {
      id: 'neuro',
      title_en: 'Neuro-Vestibular & Circadian Core',
      title_tr: 'Nöro-Vestibüler ve Sirkadiyen Sistem',
      hrp_hazards: ['Isolation & Confinement', 'Distance from Earth', 'Gravity Fields'],
      indicators: ['sleep_hours', 'mood_score'],
    },
    ocular: {
      id: 'ocular',
      title_en: 'Ocular & Cephalad Fluid (SANS)',
      title_tr: 'Göz ve Kafa İçi Sıvı Basıncı (SANS)',
      hrp_hazards: ['Gravity Fields', 'Hostile/Closed Environments'],
      indicators: ['bp_systolic_mmhg', 'cabin_co2_mmhg'],
    },
    cardio: {
      id: 'cardio',
      title_en: 'Cardiovascular & Lead-II ECG',
      title_tr: 'Kardiyovasküler Sistem ve EKG',
      hrp_hazards: ['Gravity Fields', 'Space Radiation', 'Isolation & Confinement'],
      indicators: ['heart_rate_bpm', 'bp_systolic_mmhg', 'bp_diastolic_mmhg', 'hrv_sdnn_ms'],
    },
    resp: {
      id: 'resp',
      title_en: 'Respiratory & Habitat Atmosphere',
      title_tr: 'Solunum ve Kabin Atmosferi',
      hrp_hazards: ['Hostile/Closed Environments'],
      indicators: ['spo2_pct', 'cabin_co2_mmhg'],
    },
    metab: {
      id: 'metab',
      title_en: 'Metabolic & Glycemic Balance',
      title_tr: 'Metabolik ve Glisemik Denge',
      hrp_hazards: ['Isolation & Confinement', 'Distance from Earth'],
      indicators: ['blood_glucose_mgdl', 'sleep_hours'],
    },
    musculo: {
      id: 'musculo',
      title_en: 'Musculoskeletal & Thermoregulation',
      title_tr: 'Kas-İskelet ve Isı Düzenleme',
      hrp_hazards: ['Gravity Fields', 'Hostile/Closed Environments'],
      indicators: ['core_temp_c', 'sleep_hours'],
    },
    immune_rad: {
      id: 'immune_rad',
      title_en: 'Immune Defense & Radiation Shielding',
      title_tr: 'Bağışıklık ve Radyasyon Kalkanlama',
      hrp_hazards: ['Space Radiation', 'Hostile/Closed Environments', 'Distance from Earth'],
      indicators: ['dose_rate_msv_day', 'cumulative_dose_msv', 'mood_score'],
    },
  };

  const STATUS_RANK = { optimal: 0, watch: 1, critical: 2 };

  function clampInt(val, lo, hi) {
    const rounded = Math.floor(val + 0.5);
    return Math.max(lo, Math.min(hi, rounded));
  }

  function roundTo(val, digits) {
    const factor = Math.pow(10, digits);
    return Math.round((val + Number.EPSILON) * factor) / factor;
  }

  function crc16Ccitt(bytes) {
    let crc = 0xFFFF;
    for (let i = 0; i < bytes.length; i++) {
      crc ^= (bytes[i] << 8) & 0xFFFF;
      for (let b = 0; b < 8; b++) {
        if (crc & 0x8000) {
          crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
        } else {
          crc = (crc << 1) & 0xFFFF;
        }
      }
    }
    return crc;
  }

  function normalizeVitals(v) {
    return Object.assign({
      environment: 'station',
      heart_rate_bpm: 72.0,
      bp_systolic_mmhg: 118.0,
      bp_diastolic_mmhg: 76.0,
      spo2_pct: 98.2,
      core_temp_c: 36.9,
      blood_glucose_mgdl: 95.0,
      dose_rate_msv_day: 0.55,
      sleep_hours: 7.2,
      mood_score: 8.0,
      hrv_sdnn_ms: 52.0,
      cabin_co2_mmhg: 2.1,
      cumulative_dose_msv: 124.0,
    }, v || {});
  }

  function packWerr24(input) {
    const v = normalizeVitals(input);
    const buf = new ArrayBuffer(FRAME_SIZE_BYTES);
    const view = new DataView(buf);
    const bytes = new Uint8Array(buf);
    const envId = Object.prototype.hasOwnProperty.call(ENV_NAME_TO_ID, v.environment) ? ENV_NAME_TO_ID[v.environment] : 1;

    view.setUint8(0, MAGIC_BYTE);
    view.setUint8(1, ((envId & 0x0F) << 4) | (PROTOCOL_VERSION & 0x0F));
    view.setUint16(2, clampInt(v.heart_rate_bpm * 10.0, 0, 65535), false);
    view.setUint8(4, clampInt(v.bp_systolic_mmhg, 0, 255));
    view.setUint8(5, clampInt(v.bp_diastolic_mmhg, 0, 255));
    view.setUint16(6, clampInt(v.spo2_pct * 100.0, 0, 10000), false);
    view.setUint16(8, clampInt((v.core_temp_c - 30.0) * 100.0, 0, 65535), false);
    view.setUint16(10, clampInt(v.blood_glucose_mgdl * 10.0, 0, 65535), false);
    view.setUint16(12, clampInt(v.dose_rate_msv_day * 1000.0, 0, 65535), false);
    view.setUint16(14, clampInt(v.sleep_hours * 60.0, 0, 1440), false);
    view.setUint8(16, clampInt(v.mood_score * 10.0, 10, 100));
    view.setUint8(17, clampInt(v.hrv_sdnn_ms, 0, 255));
    view.setUint16(18, clampInt(v.cabin_co2_mmhg * 10.0, 0, 65535), false);
    view.setUint16(20, clampInt(v.cumulative_dose_msv * 10.0, 0, 65535), false);

    const crc = crc16Ccitt(bytes.subarray(0, 22));
    view.setUint16(22, crc, false);
    return bytes;
  }

  function bytesToHex(bytes) {
    let hex = '';
    for (let i = 0; i < bytes.length; i++) {
      hex += bytes[i].toString(16).padStart(2, '0');
    }
    return hex;
  }

  function unpackWerr24(bytes) {
    if (!bytes || bytes.length !== FRAME_SIZE_BYTES) {
      throw new Error('Expected 24 bytes');
    }
    const u8 = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    const view = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
    const magic = view.getUint8(0);
    const meta = view.getUint8(1);
    const crcRx = view.getUint16(22, false);
    const crcCalc = crc16Ccitt(u8.subarray(0, 22));
    const envName = ENV_ID_TO_NAME[(meta >> 4) & 0x0F] || 'station';

    return {
      magic_valid: magic === MAGIC_BYTE,
      version: meta & 0x0F,
      crc_valid: crcRx === crcCalc && magic === MAGIC_BYTE,
      crc_received: crcRx,
      crc_computed: crcCalc,
      environment: envName,
      vitals: {
        environment: envName,
        heart_rate_bpm: roundTo(view.getUint16(2, false) / 10.0, 1),
        bp_systolic_mmhg: view.getUint8(4),
        bp_diastolic_mmhg: view.getUint8(5),
        spo2_pct: roundTo(view.getUint16(6, false) / 100.0, 2),
        core_temp_c: roundTo(30.0 + view.getUint16(8, false) / 100.0, 2),
        blood_glucose_mgdl: roundTo(view.getUint16(10, false) / 10.0, 1),
        dose_rate_msv_day: roundTo(view.getUint16(12, false) / 1000.0, 3),
        sleep_hours: roundTo(view.getUint16(14, false) / 60.0, 2),
        mood_score: roundTo(view.getUint8(16) / 10.0, 1),
        hrv_sdnn_ms: view.getUint8(17),
        cabin_co2_mmhg: roundTo(view.getUint16(18, false) / 10.0, 1),
        cumulative_dose_msv: roundTo(view.getUint16(20, false) / 10.0, 1),
      },
    };
  }

  function dev(val, target, scale) {
    return Math.min(2.5, Math.abs(val - target) / scale);
  }

  function werrHomeostaticIndex(input) {
    const v = normalizeVitals(input);
    const sCardio = 0.45 * dev(v.heart_rate_bpm, 70.0, 25.0) + 0.35 * dev(v.bp_systolic_mmhg, 118.0, 28.0) + 0.20 * Math.max(0.0, (42.0 - v.hrv_sdnn_ms) / 28.0);
    const sMetab = 0.55 * dev(v.blood_glucose_mgdl, 96.0, 32.0) + 0.45 * dev(v.core_temp_c, 36.9, 1.1);
    const sNeuro = 0.40 * Math.max(0.0, (7.0 - v.sleep_hours) / 3.5) + 0.35 * Math.max(0.0, (7.5 - v.mood_score) / 4.5) + 0.25 * Math.max(0.0, (v.cabin_co2_mmhg - 2.0) / 3.0);
    const sRadResp = 0.55 * Math.max(0.0, (98.0 - v.spo2_pct) / 5.0) + 0.45 * Math.max(0.0, (v.dose_rate_msv_day - 0.8) / 3.2);

    const cx = -0.68 + 0.48 * Math.min(2.0, 0.5 * (sCardio + sMetab));
    const cy = 0.14 + 0.46 * Math.min(2.0, 0.5 * (sNeuro + sRadResp));

    let zr = 0.0;
    let zi = 0.0;
    let escapeIter = MAX_ESCAPE_ITER;
    for (let step = 0; step < MAX_ESCAPE_ITER; step++) {
      const zr2 = zr * zr - zi * zi + cx;
      const zi2 = 2.0 * zr * zi + cy;
      zr = zr2;
      zi = zi2;
      if (zr * zr + zi * zi > ESCAPE_RADIUS_SQ) {
        escapeIter = step + 1;
        break;
      }
    }

    const strainMean = 0.25 * (sCardio + sMetab + sNeuro + sRadResp);
    const boundaryRatio = escapeIter / MAX_ESCAPE_ITER;
    const reserveIndex = Math.max(0.0, Math.min(1.0, boundaryRatio * Math.exp(-0.38 * strainMean)));

    return {
      c_real: roundTo(cx, 6),
      c_imag: roundTo(cy, 6),
      escape_iter: escapeIter,
      max_iter: MAX_ESCAPE_ITER,
      bounded_attractor: escapeIter === MAX_ESCAPE_ITER,
      reserve_index: roundTo(reserveIndex, 4),
      strain_vector: {
        cardio: roundTo(sCardio, 4),
        metabolic: roundTo(sMetab, 4),
        neuro_behavioral: roundTo(sNeuro, 4),
        radiation_resp: roundTo(sRadResp, 4),
      },
      weight_ram_bytes: 0,
      packet_bytes: FRAME_SIZE_BYTES,
    };
  }

  function classifyIndicator(val, optLo, optHi, warnLo, warnHi) {
    if (val >= optLo && val <= optHi) return 'optimal';
    if (val >= warnLo && val <= warnHi) return 'watch';
    return 'critical';
  }

  function evaluateAstronautState(input) {
    const v = normalizeVitals(input);
    const env = ENVIRONMENTS[v.environment] || ENVIRONMENTS.station;
    const frame = packWerr24(v);
    const werr = werrHomeostaticIndex(v);

    const indicators = {};
    let maxStatus = 'optimal';
    for (let i = 0; i < INDICATOR_SPECS.length; i++) {
      const [key, label_en, label_tr, unit, region, optLo, optHi, warnLo, warnHi] = INDICATOR_SPECS[i];
      const rawVal = Number(v[key]);
      const st = classifyIndicator(rawVal, optLo, optHi, warnLo, warnHi);
      if (STATUS_RANK[st] > STATUS_RANK[maxStatus]) maxStatus = st;
      indicators[key] = {
        key, label_en, label_tr, unit, region, status: st,
        value: roundTo(rawVal, 3),
        optimal_range: [optLo, optHi],
        watch_range: [warnLo, warnHi],
      };
    }

    let overallStatus = maxStatus;
    if (overallStatus === 'optimal' && werr.reserve_index < 0.58) {
      overallStatus = 'watch';
    }

    const anatomyRegions = {};
    const regionKeys = Object.keys(ANATOMY_REGIONS);
    for (let r = 0; r < regionKeys.length; r++) {
      const regId = regionKeys[r];
      const meta = ANATOMY_REGIONS[regId];
      let regStatus = 'optimal';
      if (regId === 'ocular' && (v.bp_systolic_mmhg > 135 || v.cabin_co2_mmhg > 3.0)) {
        regStatus = 'watch';
      }
      for (let j = 0; j < meta.indicators.length; j++) {
        const indSt = indicators[meta.indicators[j]].status;
        if (STATUS_RANK[indSt] > STATUS_RANK[regStatus]) regStatus = indSt;
      }
      anatomyRegions[regId] = {
        id: regId,
        title_en: meta.title_en,
        title_tr: meta.title_tr,
        status: regStatus,
        hrp_hazards: meta.hrp_hazards.slice(),
        indicators: meta.indicators.map((k) => indicators[k]),
      };
    }

    return {
      overall_status: overallStatus,
      autonomous_triage_required: env.one_way_delay_sec[1] >= 10.0,
      environment: env,
      packet_hex: bytesToHex(frame),
      packet_bytes: frame.length,
      werr_homeostatic: werr,
      indicators,
      anatomy_regions: anatomyRegions,
    };
  }

  function simulateSeuBitflip(bytes, bitIndex) {
    const idx = (bitIndex || 19) % (FRAME_SIZE_BYTES * 8);
    const byteI = Math.floor(idx / 8);
    const bitI = idx % 8;
    const corrupted = new Uint8Array(bytes);
    corrupted[byteI] ^= (1 << bitI);
    const decoded = unpackWerr24(corrupted);
    return {
      flipped_bit: idx,
      flipped_byte: byteI,
      corrupted_hex: bytesToHex(corrupted),
      seu_detected_by_crc: !decoded.crc_valid,
      corrupted_neural_weights_bytes: 0,
    };
  }

  function evaluateLearningGate(opts) {
    const o = Object.assign({
      quiz_streak: 0,
      routine_adherence_pct: 80,
      sleep_hours: 7.2,
      mood_score: 8.0,
      crew_role: 'non_medical_pilot',
    }, opts || {});
    const cognitiveReserve = Math.min(1.0, Math.max(0.0, 0.55 * (o.sleep_hours / 8.0) + 0.45 * (o.mood_score / 10.0)));
    const masteryIndex = Math.min(1.0, Math.max(0.0, 0.45 * Math.min(1.0, o.quiz_streak / 3.0) + 0.55 * (o.routine_adherence_pct / 100.0)));
    let tier = 2;
    let label_en = 'Tier 2 — Applied Space Physiology Coach';
    let label_tr = 'Düzey 2 — Uygulamalı Uzay Fizyolojisi Koçu';
    if (cognitiveReserve < 0.62 || masteryIndex < 0.40) {
      tier = 1;
      label_en = 'Tier 1 — High-Clarity Immediate Action Guide';
      label_tr = 'Düzey 1 — Sade ve Hızlı Müdahale Rehberi';
    } else if (masteryIndex >= 0.78 && o.crew_role === 'flight_surgeon_liaison') {
      tier = 3;
      label_en = 'Tier 3 — Aerospace Clinical & HRP Research Brief';
      label_tr = 'Düzey 3 — Havacılık Tıbbı ve HRP Araştırma Özeti';
    }
    return {
      zpd_tier: tier,
      label_en,
      label_tr,
      cognitive_reserve: roundTo(cognitiveReserve, 3),
      mastery_index: roundTo(masteryIndex, 3),
    };
  }

  return {
    MAGIC_BYTE,
    PROTOCOL_VERSION,
    FRAME_SIZE_BYTES,
    ENVIRONMENTS,
    INDICATOR_SPECS,
    ANATOMY_REGIONS,
    crc16Ccitt,
    packWerr24,
    unpackWerr24,
    bytesToHex,
    werrHomeostaticIndex,
    evaluateAstronautState,
    simulateSeuBitflip,
    evaluateLearningGate,
  };
}));
