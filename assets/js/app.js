(function () {
  'use strict';

  const C = window.AstroSomaCore;

  const SCENARIO_PRESETS = {
    nominal: {
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
    },
    solar_storm: {
      environment: 'lunar_base',
      heart_rate_bpm: 98.0,
      bp_systolic_mmhg: 134.0,
      bp_diastolic_mmhg: 86.0,
      spo2_pct: 97.0,
      core_temp_c: 37.2,
      blood_glucose_mgdl: 104.0,
      dose_rate_msv_day: 6.4,
      sleep_hours: 6.0,
      mood_score: 6.0,
      hrv_sdnn_ms: 34.0,
      cabin_co2_mmhg: 2.4,
      cumulative_dose_msv: 215.0,
    },
    rover_hypoxia_co2: {
      environment: 'rover',
      heart_rate_bpm: 122.0,
      bp_systolic_mmhg: 148.0,
      bp_diastolic_mmhg: 95.0,
      spo2_pct: 90.2,
      core_temp_c: 38.3,
      blood_glucose_mgdl: 61.0,
      dose_rate_msv_day: 1.1,
      sleep_hours: 5.0,
      mood_score: 4.2,
      hrv_sdnn_ms: 20.0,
      cabin_co2_mmhg: 4.8,
      cumulative_dose_msv: 148.0,
    },
    mars_blackout: {
      environment: 'mars_transit',
      heart_rate_bpm: 88.0,
      bp_systolic_mmhg: 131.0,
      bp_diastolic_mmhg: 84.0,
      spo2_pct: 96.5,
      core_temp_c: 37.1,
      blood_glucose_mgdl: 88.0,
      dose_rate_msv_day: 2.1,
      sleep_hours: 5.4,
      mood_score: 5.5,
      hrv_sdnn_ms: 31.0,
      cabin_co2_mmhg: 3.1,
      cumulative_dose_msv: 392.0,
    },
  };

  const SLIDER_BOUNDS = {
    heart_rate_bpm: [35, 160, 0.5],
    bp_systolic_mmhg: [70, 190, 1],
    bp_diastolic_mmhg: [40, 120, 1],
    hrv_sdnn_ms: [10, 180, 1],
    spo2_pct: [82, 100, 0.1],
    cabin_co2_mmhg: [0.3, 7.0, 0.1],
    core_temp_c: [34.0, 40.0, 0.1],
    blood_glucose_mgdl: [45, 240, 1],
    sleep_hours: [2.0, 12.0, 0.1],
    mood_score: [1.0, 10.0, 0.5],
    dose_rate_msv_day: [0.1, 15.0, 0.05],
    cumulative_dose_msv: [0, 650, 1],
  };

  const NON_MED_GUIDES = {
    neuro: {
      en: ['Tracks sleep debt & mental sharpness; 16 orbital sunrises/day confuse melatonin.', 'Log actual uninterrupted rest + honest 1–10 mood before EVAs.', 'Dim blue cabin lights 90 min pre-sleep if rest < 6.5 h.'],
      tr: ['Uyku borcunu ve zihinsel odaklanmayı izler; 90 dakikada bir gün doğumu iç saati bozar.', 'EVA öncesi gerçek uyku süresini ve 1–10 ruh halini kaydedin.', 'Uyku < 6.5 saat ise yatmadan 90 dk önce kabin mavi ışığını kısın.'],
    },
    ocular: {
      en: ['Monitors cephalad fluid shift (SANS) risking near-vision & optic nerve pressure.', 'Check Amsler grid reading sharpness along with BP & cabin CO2.', 'Keep cabin pCO2 < 2.5 mmHg and report visual floaters promptly.'],
      tr: ['Başa sıvı kaymasını (SANS) ve göz içi basınç riskini izler.', 'Yakın görme keskinliğini tansiyon ve kabin CO2 ile birlikte kontrol edin.', 'Kabin pCO2 < 2.5 mmHg tutun ve bulanıklık hissini hemen bildirin.'],
    },
    cardio: {
      en: ['Measures heart strain and blood vessel tone in altered gravity.', 'Sit quietly 3 min, cuff at heart level, keep finger still on ECG/rPPG sensor.', 'Before gravity transition or landing, hydrate 250 mL electrolytes + leg exercises.'],
      tr: ['Değişen yerçekiminde kalp yükünü ve damar tonusunu ölçer.', '3 dk dinlenip manşonu kalp hizasında takın ve EKG/rPPG sensörünü sabit tutun.', 'Yüksek yerçekimi dönüşü öncesi 250 mL elektrolitli sıvı + bacak direnç hareketi yapın.'],
    },
    resp: {
      en: ['Tracks blood oxygen (SpO2) alongside cabin carbon dioxide (pCO2).', 'Warm fingertip before clipping oximeter; avoid bright overhead lamp glare.', 'High CO2 causes headaches BEFORE SpO2 falls — inspect scrubber airflow immediately.'],
      tr: ['Kan oksijenini (SpO2) ve kabin karbondioksitini (pCO2) birlikte takip eder.', 'Oksimetre öncesi parmağı ısıtın ve parlak kokpit ışığından koruyun.', 'Yüksek CO2, SpO2 düşmeden baş ağrısı yapar — hemen hava tutucuları doğrulayın.'],
    },
    metab: {
      en: ['Blood glucose fuels focus and manual dexterity during spaceflight.', 'Log fasting morning glucose or 2h post-meal sensor check.', 'Below 70 mg/dL requires 15 g quick carb gel + repeat check in 15 min.'],
      tr: ['Kan şekeri uzayda dikkat ve el becerisi için beynin ana yakıtıdır.', 'Sabah açlık veya yemekten 2 saat sonra sensör ölçümü kaydedin.', '70 mg/dL altında 15 g hızlı karbonhidrat jeli alıp 15 dk sonra tekrar ölçün.'],
    },
    musculo: {
      en: ['Monitors thermal load in EVA suits plus weight-bearing bone preservation.', 'Wait 15 min after hot/cold drinks before logging core temperature.', 'Complete ARED resistive exercise daily to curb microgravity bone mineral loss.'],
      tr: ['EVA giysisi ısı yükünü ve mikro yerçekiminde kemik korumasını takip eder.', 'Sıcak/soğuk içeceklerden 15 dk sonra çekirdek sıcaklığı ölçün.', 'Kemik kaybını sınırlamak için günlük ARED direnç yüklemesini aksatmayın.'],
    },
    immune_rad: {
      en: ['Monitors acute Solar Particle Event dose rate (mSv/day) and ALARA mission total.', 'Cross-check personal waist dosimeter against live NOAA GOES proton stream.', 'Move sleep bunks behind water/polyethylene or regolith shielding during storms.'],
      tr: ['Anlık güneş fırtınası doz hızını (mSv/gün) ve ALARA görev toplamını izler.', 'Kişisel dozimetreyi canlı NOAA GOES proton akışıyla eşleştirin.', 'Fırtınada uyku bölmesini su/polietilen veya regolit kalkanlı sığınağa taşıyın.'],
    },
  };

  const QUESTS = [
    { id: 'morning_vitals', xp: 50, winEn: '07:30 Mission', winTr: '07:30 Görev', tEn: 'Morning Rest BP, HR & SpO2 Check', tTr: 'Sabah Dinlenik Tansiyon, Nabız & SpO2', dEn: 'Measure seated at heart level before caffeine.', dTr: 'Kafein öncesi kalp hizasında oturur ölçüm.' },
    { id: 'ared_bone', xp: 80, winEn: '11:00 Countermeasure', winTr: '11:00 Egzersiz', tEn: 'ARED Bone & Spine Resistance (45 min)', tTr: 'ARED Kemik ve Omurga Direnci (45 dk)', dEn: 'Protects femur/lumbar BMD in microgravity.', dTr: 'Mikro yerçekiminde kemik yoğunluğunu korur.' },
    { id: 'hydration_glucose', xp: 45, winEn: '15:00 Hydration', winTr: '15:00 Sıvı', tEn: 'Electrolyte Hydration & Glucose Sync', tTr: 'Elektrolit ve Kan Şekeri Kaydı', dEn: 'Drink 300 mL & log capillary glucose.', dTr: '300 mL sıvı tüketin ve glikoz kaydedin.' },
    { id: 'radiation_sync', xp: 60, winEn: '18:00 Shielding', winTr: '18:00 Radyasyon', tEn: 'Dosimeter & NOAA GOES Storm Check', tTr: 'Dozimetre ve NOAA GOES Kontrolü', dEn: 'Confirm dose rate fits ALARA budget.', dTr: 'Doz hızının ALARA içinde olduğunu doğrulayın.' },
    { id: 'evening_winddown', xp: 55, winEn: '21:30 Sleep', winTr: '21:30 Uyku', tEn: 'Circadian LED Dim & Mood Check-In', tTr: 'Sirkadiyen Işık Kısma & Ruh Hali', dEn: 'Dim blue light 90 min before bunk rest.', dTr: 'Uyku öncesi 90 dk mavi ışığı azaltın.' },
  ];

  const QUIZZES = [
    {
      qEn: 'In a rover cabin, pCO2 rises to 4.2 mmHg with headache while SpO2 is 96%. First safest step?',
      qTr: 'Keşif aracında pCO2 4.2 mmHg\'ya çıkıp baş ağrısı başlarken SpO2 %96 ise ilk güvenli adım nedir?',
      optsEn: ['Ignore it since SpO2 > 95%', 'Check CO2 scrubber & cabin airflow fans immediately', 'Start intense sprinting'],
      optsTr: ['SpO2 > %95 olduğu için önemseme', 'CO2 tutucu ve kabin hava fanlarını hemen kontrol et', 'Yoğun koşu başlat'],
      correct: 1,
      expEn: 'CO2 buildup causes headache and brain fog BEFORE blood SpO2 drops.',
      expTr: 'Kabin CO2 birikimi, SpO2 düşmeden ÖNCE baş ağrısı ve odak kaybı yapar.',
    },
    {
      qEn: 'Why do astronauts develop facial puffiness & reading blur (SANS) in microgravity?',
      qTr: 'Mikro yerçekiminde neden yüz şişkinliği ve yakın görme bulanıklığı (SANS) oluşabilir?',
      optsEn: ['Headward fluid shift raises cranial/ocular pressure', 'Body temp rises permanently to 40°C', 'Blood cells double in orbit'],
      optsTr: ['Sıvının baş bölgesine kayması kafa/göz içi basıncı artırır', 'Vücut sıcaklığı kalıcı 40°C olur', 'Yörüngede alyuvar sayısı iki katına çıkar'],
      correct: 0,
      expEn: 'Without Earth gravity pulling fluids down, headward shift affects optic nerves (SANS).',
      expTr: 'Yerçekimi olmayınca başa doğru kayan sıvı optik sinir basıncını etkiler (SANS).',
    },
    {
      qEn: 'GOES >=10 MeV proton storm triggers on Lunar Base. What does ALARA prescribe?',
      qTr: 'Ay Üssünde GOES >=10 MeV güneş proton fırtınası başlarsa ALARA ne gerektirir?',
      optsEn: ['Begin unshielded outdoor EVA', 'Defer EVA and shelter inside water/regolith-shielded core', 'Disable personal dosimeters'],
      optsTr: ['Korunmasız dış EVA yürüyüşüne çık', 'EVA\'yı ertele ve su/regolit kalkanlı iç sığınağa geç', 'Kişisel dozimetreleri kapat'],
      correct: 1,
      expEn: 'ALARA protects crew via hydrogen-rich water walls or lunar regolith overburden.',
      expTr: 'ALARA gereği su duvarlı veya regolit kalkanlı iç bölmeye geçilir.',
    },
  ];

  const UI_I18N = {
    en: {
      pageTitle: 'AstroSoma — Autonomous Astronaut Health Monitoring Console',
      brandSub: '0-SRAM Autonomous Astronaut Health & Homeostasis Console',
      lblEnv: 'Mission Environment',
      lblRole: 'Crew Role (CEIT Adaptive UX)',
      lblScenarios: 'Scenarios:',
      scNominal: 'Nominal Orbit',
      scStorm: 'Solar Proton Storm (SPE)',
      scRover: 'Rover CO2 & Hypoglycemia',
      scMars: 'Mars 22-min Blackout',
      anatomyHeading: 'Interactive Human Anatomy',
      clickHintPill: 'Click body region',
      telemetryHeading: 'Physiological Indicators & 0-SRAM Triage',
      lblWerrReserve: '0-SRAM Homeostatic Reserve',
      lblWeightRam: 'Mutable Neural Weight RAM',
      valWeightRam: '0 Bytes (SEU-Free)',
      lblPacketSize: 'Telemetry Packet Frame',
      valPacketSize: '24 Bytes + CRC-16',
      lblZpdTier: 'CEIT Explanation Mode',
      btnTabCharts: 'ECG & Dynamic Trends',
      btnTabGuide: 'Non-Medical Crew Guide (CEIT)',
      btnTabQuests: 'Routines, Gamification & Quiz',
      btnTabNasaData: 'NASA OSDR, NOAA & WERR-24 Hex',
      btnCameraRppg: 'Optical rPPG Camera Scan',
      lblUploadLog: 'Upload JSON/CSV',
      btnSeuTest: 'Simulate Cosmic-Ray SEU Bit-Flip',
      btnExportJson: 'Export WERR-24',
      lblEcgTitle: 'Live Lead-II ECG Synthesis',
      ecgFootHint: 'Deterministic P-QRS-T envelope driven live by current HR and SDNN heart rate variability.',
      lblTrendTitle: '14-Sol Multi-Vital Drift Chart',
      trendFootHint: 'Shaded emerald band marks NASA operational nominal range for selected indicator.',
      lblQuestHeader: 'Mission Routine Prompts & XP',
      lblWerrHexTitle: 'WERR-24 24-Byte Telemetry Packet & SEU Fault Log',
      lblOsdrTitle: 'Verified NASA OSDR Studies & NOAA GOES Proton Feed',
      btnRefreshLive: 'Sync Live Feeds',
      crcStatusPill: 'CRC-16 VALID',
      rppgModalTitle: 'Optical rPPG Vital Scanner',
      rppgExplain: 'Uses browser camera frames (green-channel PPG brightness delta) to estimate pulse rate safely in-browser, with deterministic optical waveform fallback if no camera is attached.',
      btnCloseRppg: 'Close',
      btnRunRppg: 'Start 4s Scan',
      btnApplyRppg: 'Apply Estimate to Vitals',
      rppgReadySub: 'Click Start Scan to sample 4 seconds of optical pulse trace.',
      footerSlidesLink: '7-Slide HTML Deck (EN)',
      footerArchLink: 'Apache-2.0 Open Source',
      footerRefsLbl: 'Core References',
      footerContactLbl: 'Contact',
      svgLblImmune: 'IMMUNE & RADIATION SHIELD',
      svgLblNeuro: 'NEURO',
      svgLblResp: 'RESP',
      svgLblCardio: 'CARDIO',
      svgLblMetab: 'METAB',
      svgLblMusculo: 'BONE / °C',
      meaningLbl: 'What It Means (Plain Language)',
      measureLbl: 'How to Measure Safely',
      actionLbl: 'Immediate Crew Action',
      seuDefault: 'Click "Simulate Cosmic-Ray SEU Bit-Flip" above to flip a random bit inside the 24-byte buffer and test CRC-16 fault detection.',
    },
    tr: {
      pageTitle: 'AstroSoma — Otonom Astronot Sağlık İzleme Konsolu',
      brandSub: '0-SRAM Otonom Astronot Sağlık ve Homeostaz Konsolu',
      lblEnv: 'Görev Ortamı',
      lblRole: 'Mürettebat Rolü (CEIT Uyarlanır Arayüz)',
      lblScenarios: 'Senaryolar:',
      scNominal: 'Normal Yörünge',
      scStorm: 'Güneş Proton Fırtınası (SPE)',
      scRover: 'Araç CO2 ve Hipoglisemi',
      scMars: 'Mars 22-dk İletişim Gecikmesi',
      anatomyHeading: 'Etkileşimli İnsan Anatomisi',
      clickHintPill: 'Vücut bölgesine tıkla',
      telemetryHeading: 'Fizyolojik Göstergeler ve 0-SRAM Triyajı',
      lblWerrReserve: '0-SRAM Homeostaz Rezervi',
      lblWeightRam: 'Değişebilir Ağ Ağırlık RAM\'i',
      valWeightRam: '0 Bayt (SEU Bağışık)',
      lblPacketSize: 'Telemetri Paket Çerçevesi',
      valPacketSize: '24 Bayt + CRC-16',
      lblZpdTier: 'CEIT Anlatım Düzeyi',
      btnTabCharts: 'EKG ve Dinamik Trendler',
      btnTabGuide: 'Tıp Dışı Mürettebat Rehberi (CEIT)',
      btnTabQuests: 'Rutinler, Oyunlaştırma ve Test',
      btnTabNasaData: 'NASA OSDR, NOAA ve WERR-24 Hex',
      btnCameraRppg: 'Kamera Optik rPPG Nabız Tarama',
      lblUploadLog: 'JSON/CSV Yükle',
      btnSeuTest: 'Kozmik Işın SEU Bit-Kayması Testi',
      btnExportJson: 'WERR-24 Dışa Aktar',
      lblEcgTitle: 'Canlı Lead-II EKG Sentezi',
      ecgFootHint: 'Güncel kalp hızı (BPM) ve SDNN değişkenliği ile anlık çizilen deterministik P-QRS-T dalgası.',
      lblTrendTitle: '14 Sol Çoklu Gösterge Trend Grafiği',
      trendFootHint: 'Yeşil gölgeli bant, seçili gösterge için NASA operasyonel normal aralığını gösterir.',
      lblQuestHeader: 'Görev Sağlığı Rutinleri & XP',
      lblWerrHexTitle: 'WERR-24 24-Bayt Paket ve SEU Hata Günlüğü',
      lblOsdrTitle: 'Doğrulanmış NASA OSDR Çalışmaları ve NOAA GOES Akışı',
      btnRefreshLive: 'Canlı Akışları Eşitle',
      crcStatusPill: 'CRC-16 GEÇERLİ',
      rppgModalTitle: 'Optik rPPG Kamera Nabız Tarayıcı',
      rppgExplain: 'Tarayıcı kamerası karelerinden (yeşil-kanal PPG parlaklık farkı) güvenli şekilde nabız tahmini yapar; kamera yoksa deterministik optik dalga yedeği kullanır.',
      btnCloseRppg: 'Kapat',
      btnRunRppg: '4 sn Taramayı Başlat',
      btnApplyRppg: 'Tahmini Göstergelere Uygula',
      rppgReadySub: '4 saniyelik optik nabız örneklemesi için Taramayı Başlat düğmesine tıklayın.',
      footerSlidesLink: '7 Slaytlık HTML Sunumu (TR)',
      footerArchLink: 'Apache-2.0 Açık Kaynak',
      footerRefsLbl: 'Temel Referanslar',
      footerContactLbl: 'İletişim',
      svgLblImmune: 'BAĞIŞIKLIK VE RADYASYON KALKANI',
      svgLblNeuro: 'NÖRO',
      svgLblResp: 'SOLUNUM',
      svgLblCardio: 'KARDİYO',
      svgLblMetab: 'METAB',
      svgLblMusculo: 'KEMİK / °C',
      meaningLbl: 'Basit Anlamı',
      measureLbl: 'Doğru Ölçüm Adımı',
      actionLbl: 'Şu An Ne Yapmalısın?',
      seuDefault: '24 baytlık pakette rastgele bir kozmik ışın bit-hatası simüle etmek ve CRC-16 algılamasını doğrulamak için yukarıdaki SEU düğmesine tıklayın.',
    },
  };

  const SELECT_OPTION_I18N = {
    envSelect: {
      en: {
        station: 'ISS Space Station (0 g)',
        spacecraft: 'Orion Spacecraft (Transit)',
        rover: 'Pressurized Surface Rover',
        lunar_base: 'Artemis Lunar Base (0.165 g)',
        mars_transit: 'Mars Transit & Habitat (22m delay)',
      },
      tr: {
        station: 'ISS Uzay İstasyonu (0 g)',
        spacecraft: 'Orion Uzay Aracı (Transit)',
        rover: 'Basınçlı Yüzey Keşif Aracı',
        lunar_base: 'Artemis Ay Üssü (0.165 g)',
        mars_transit: 'Mars Transit ve Üs (22 dk gecikme)',
      },
    },
    roleSelect: {
      en: {
        non_medical_pilot: 'Non-Medical Pilot / Specialist',
        flight_engineer: 'EVA / Flight Engineer',
        flight_surgeon_liaison: 'Crew Medical Officer / Liaison',
      },
      tr: {
        non_medical_pilot: 'Tıp Dışı Pilot / Görev Uzmanı',
        flight_engineer: 'EVA / Uçuş Mühendisi',
        flight_surgeon_liaison: 'Mürettebat Sağlık Sorumlusu',
      },
    },
    trendMetricSelect: {
      en: {
        heart_rate_bpm: 'Heart Rate (BPM)',
        spo2_pct: 'SpO2 (%)',
        blood_glucose_mgdl: 'Blood Glucose (mg/dL)',
        sleep_hours: 'Sleep Duration (h)',
        dose_rate_msv_day: 'Radiation Dose (mSv/day)',
      },
      tr: {
        heart_rate_bpm: 'Kalp Atış Hızı (BPM)',
        spo2_pct: 'Kan Oksijeni SpO2 (%)',
        blood_glucose_mgdl: 'Kan Şekeri (mg/dL)',
        sleep_hours: 'Uyku Süresi (sa)',
        dose_rate_msv_day: 'Radyasyon Dozu (mSv/gün)',
      },
    },
  };

  const HAZARD_TR = {
    'Space Radiation': 'Uzay Radyasyonu',
    'Isolation & Confinement': 'İzolasyon ve Kapalı Ortam',
    'Distance from Earth': "Dünya'dan Uzaklık",
    'Gravity Fields': 'Değişen Yerçekimi',
    'Hostile/Closed Environments': 'Zorlu / Kapalı Ortam',
  };

  function getInitialLang() {
    try {
      const qs = new URLSearchParams(window.location.search).get('lang');
      if (qs === 'tr' || qs === 'en') return qs;
      const saved = window.localStorage.getItem('astrosoma_lang');
      if (saved === 'tr' || saved === 'en') return saved;
    } catch (_) {}
    return 'en';
  }

  let state = {
    lang: getInitialLang(),
    scenario: 'nominal',
    selectedRegion: 'cardio',
    vitals: Object.assign({}, SCENARIO_PRESETS.nominal),
    crewRole: 'non_medical_pilot',
    completedQuests: new Set(['morning_vitals']),
    quizIndex: 0,
    quizCorrect: 0,
    quizStreak: 1,
    quizFeedback: '',
    streakDays: 3,
    lastSeuResult: null,
    nasaSnapshot: null,
    rppgEstimate: null,
    rppgStream: null,
    ecgPhase: 0,
  };

  const els = {
    envSelect: document.getElementById('envSelect'),
    roleSelect: document.getElementById('roleSelect'),
    langToggle: document.getElementById('langToggle'),
    missionBadge: document.getElementById('missionBadge'),
    deckLink: document.getElementById('deckLink'),
    regionChips: document.getElementById('regionChips'),
    regionDetailBox: document.getElementById('regionDetailBox'),
    vitalsGrid: document.getElementById('vitalsGrid'),
    actionsBox: document.getElementById('actionsBox'),
    commsDelayPill: document.getElementById('commsDelayPill'),
    valWerrReserve: document.getElementById('valWerrReserve'),
    valZpdTier: document.getElementById('valZpdTier'),
    ecgReadoutPill: document.getElementById('ecgReadoutPill'),
    trendMetricSelect: document.getElementById('trendMetricSelect'),
    trendSvg: document.getElementById('trendSvg'),
    ceitGuideContainer: document.getElementById('ceitGuideContainer'),
    questList: document.getElementById('questList'),
    xpBarFill: document.getElementById('xpBarFill'),
    gamifyXpSummary: document.getElementById('gamifyXpSummary'),
    gamifyRankPill: document.getElementById('gamifyRankPill'),
    badgeList: document.getElementById('badgeList'),
    quizContainer: document.getElementById('quizContainer'),
    packetHexBox: document.getElementById('packetHexBox'),
    packetBreakdown: document.getElementById('packetBreakdown'),
    seuLogBox: document.getElementById('seuLogBox'),
    noaaHeaderChip: document.getElementById('noaaHeaderChip'),
    noaaDetailCard: document.getElementById('noaaDetailCard'),
    osdrList: document.getElementById('osdrList'),
    rppgModal: document.getElementById('rppgModal'),
    rppgVideo: document.getElementById('rppgVideo'),
    rppgReadout: document.getElementById('rppgReadout'),
    rppgSub: document.getElementById('rppgSub'),
    btnApplyRppg: document.getElementById('btnApplyRppg'),
  };

  function statusColor(status) {
    if (status === 'critical') return '#ef4444';
    if (status === 'watch') return '#f59e0b';
    return '#10b981';
  }

  function statusLabel(status) {
    if (state.lang === 'tr') {
      return status === 'critical' ? 'KRİTİK' : status === 'watch' ? 'İZLEME' : 'NORMAL';
    }
    return status.toUpperCase();
  }

  function applyI18nStatic() {
    const t = UI_I18N[state.lang];
    document.documentElement.lang = state.lang;
    document.title = t.pageTitle;
    Object.keys(t).forEach((id) => {
      const node = document.getElementById(id);
      if (node && id !== 'seuDefault' && id !== 'pageTitle' && !id.endsWith('Lbl')) {
        node.textContent = t[id];
      }
    });
    const footerRefs = document.getElementById('footerRefsLbl');
    if (footerRefs) footerRefs.textContent = t.footerRefsLbl;
    const footerContact = document.getElementById('footerContactLbl');
    if (footerContact) footerContact.textContent = t.footerContactLbl;

    Object.keys(SELECT_OPTION_I18N).forEach((selectId) => {
      const sel = document.getElementById(selectId);
      const map = SELECT_OPTION_I18N[selectId][state.lang];
      if (!sel || !map) return;
      Array.from(sel.options).forEach((opt) => {
        if (map[opt.value]) opt.textContent = map[opt.value];
      });
    });

    els.deckLink.href = state.lang === 'tr' ? '/docs/AstroSoma_Presentation_TR.pdf' : '/docs/AstroSoma_Presentation_EN.pdf';
    els.deckLink.textContent = state.lang === 'tr' ? 'Sunum PDF (TR)' : 'Pitch PDF (EN)';
    const footerSlides = document.getElementById('footerSlidesLink');
    if (footerSlides) {
      footerSlides.href = state.lang === 'tr' ? '/demo/slides_tr.html' : '/demo/slides_en.html';
    }
    renderNasaFeeds();
  }

  function renderAll() {
    applyI18nStatic();
    const evalRes = C.evaluateAstronautState(state.vitals);
    const gam = computeGamify();
    const gate = C.evaluateLearningGate({
      quiz_streak: state.quizStreak,
      routine_adherence_pct: gam.adherence,
      sleep_hours: state.vitals.sleep_hours,
      mood_score: state.vitals.mood_score,
      crew_role: state.crewRole,
    });

    // Header badges
    els.missionBadge.className = 'pill status-' + evalRes.overall_status;
    els.missionBadge.textContent = statusLabel(evalRes.overall_status);
    els.valWerrReserve.textContent = Math.round(evalRes.werr_homeostatic.reserve_index * 1000) / 10 + '%';
    els.valWerrReserve.style.color = statusColor(evalRes.overall_status);
    els.valZpdTier.textContent = state.lang === 'tr' ? gate.label_tr : gate.label_en;

    const dMin = evalRes.environment.one_way_delay_sec[0];
    const dMax = evalRes.environment.one_way_delay_sec[1];
    const delayStr = dMax >= 60
      ? Math.round(dMin / 60) + '–' + Math.round(dMax / 60) + (state.lang === 'tr' ? ' dk' : ' min')
      : dMin + '–' + dMax + (state.lang === 'tr' ? ' sn' : ' s');
    els.commsDelayPill.textContent = (state.lang === 'tr' ? 'Sinyal Gecikmesi: ' : 'Delay: ') + delayStr + ' · ' + (state.lang === 'tr' ? evalRes.environment.comms_mode_tr : evalRes.environment.comms_mode_en);
    els.commsDelayPill.className = 'pill ' + (evalRes.autonomous_triage_required ? 'status-watch' : 'status-optimal');

    els.ecgReadoutPill.textContent = `${state.vitals.heart_rate_bpm} BPM · HRV ${state.vitals.hrv_sdnn_ms} ms`;

    renderAnatomy(evalRes, gate);
    renderVitalsGrid(evalRes);
    renderActions(evalRes);
    renderTrendSvg(evalRes);
    renderCeitGuide(evalRes, gate);
    renderQuestsAndQuiz(gam);
    renderPacketInspector(evalRes);
  }

  function renderAnatomy(evalRes, gate) {
    const hotspots = document.querySelectorAll('#anatomySvg .body-hotspot');
    hotspots.forEach((g) => {
      const regId = g.getAttribute('data-region');
      const reg = evalRes.anatomy_regions[regId];
      const col = statusColor(reg ? reg.status : 'optimal');
      g.classList.toggle('selected', regId === state.selectedRegion);
      g.querySelectorAll('.hotspot-core, .hotspot-ring').forEach((shape) => {
        shape.setAttribute('stroke', col);
        if (shape.classList.contains('hotspot-core')) {
          shape.setAttribute('fill', col);
        }
      });
    });

    const chipHtml = Object.keys(C.ANATOMY_REGIONS).map((regId) => {
      const r = evalRes.anatomy_regions[regId];
      const shortName = state.lang === 'tr' ? r.title_tr.split(' ')[0] : r.title_en.split(' ')[0];
      const selCls = regId === state.selectedRegion ? ' selected' : '';
      return `<button type="button" class="region-chip status-${r.status}${selCls}" data-chip="${regId}">${shortName}</button>`;
    }).join('');
    els.regionChips.innerHTML = chipHtml;
    els.regionChips.querySelectorAll('button').forEach((b) => {
      b.addEventListener('click', () => {
        state.selectedRegion = b.getAttribute('data-chip');
        renderAll();
      });
    });

    const sel = evalRes.anatomy_regions[state.selectedRegion];
    const t = UI_I18N[state.lang];
    const guide = (NON_MED_GUIDES[state.selectedRegion] || NON_MED_GUIDES.cardio)[state.lang];
    const title = state.lang === 'tr' ? sel.title_tr : sel.title_en;
    const indsHtml = sel.indicators.map((ind) => {
      const name = state.lang === 'tr' ? ind.label_tr : ind.label_en;
      return `<span class="pill status-${ind.status}">${name}: <b>${ind.value} ${ind.unit}</b></span>`;
    }).join(' ');
    const hazHtml = sel.hrp_hazards.map((h) => `<span class="hazard-tag">NASA HRP: ${state.lang === 'tr' ? (HAZARD_TR[h] || h) : h}</span>`).join('');

    els.regionDetailBox.innerHTML = `
      <h3><span>${title}</span><span class="pill status-${sel.status}">${statusLabel(sel.status)}</span></h3>
      <div class="hazard-tags">${hazHtml}</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">${indsHtml}</div>
      <div><b>${t.meaningLbl}:</b> ${guide[0]}</div>
      <div style="margin-top:4px;"><b>${t.measureLbl}:</b> ${guide[1]}</div>
      <div style="margin-top:4px;color:#7dd3fc;"><b>${t.actionLbl}:</b> ${guide[2]}</div>
      <div class="vital-range-hint" style="margin-top:5px;">${state.lang === 'tr' ? 'CEIT Modu' : 'CEIT Mode'}: ${state.lang === 'tr' ? gate.label_tr : gate.label_en}</div>
    `;
  }

  function renderVitalsGrid(evalRes) {
    const keys = Object.keys(evalRes.indicators);
    els.vitalsGrid.innerHTML = keys.map((key) => {
      const ind = evalRes.indicators[key];
      const [min, max, step] = SLIDER_BOUNDS[key];
      const name = state.lang === 'tr' ? ind.label_tr : ind.label_en;
      const optStr = `${ind.optimal_range[0]}–${ind.optimal_range[1]} ${ind.unit}`;
      return `
        <div class="vital-card st-${ind.status}">
          <div class="vital-top">
            <span class="vital-name">${name}</span>
            <span class="vital-readout">${ind.value} <small>${ind.unit}</small></span>
          </div>
          <div class="vital-slider-row">
            <input type="range" min="${min}" max="${max}" step="${step}" value="${state.vitals[key]}" data-vital-range="${key}" aria-label="${name} slider">
            <input type="number" min="${min}" max="${max}" step="${step}" value="${state.vitals[key]}" data-vital-num="${key}" aria-label="${name} value">
          </div>
          <div class="vital-range-hint">${state.lang === 'tr' ? 'NASA Normal' : 'NASA Nominal'}: ${optStr}</div>
        </div>
      `;
    }).join('');

    els.vitalsGrid.querySelectorAll('[data-vital-range]').forEach((el) => {
      el.addEventListener('input', (e) => {
        const k = e.target.getAttribute('data-vital-range');
        state.vitals[k] = parseFloat(e.target.value);
        renderAll();
      });
    });
    els.vitalsGrid.querySelectorAll('[data-vital-num]').forEach((el) => {
      el.addEventListener('change', (e) => {
        const k = e.target.getAttribute('data-vital-num');
        const val = parseFloat(e.target.value);
        if (!Number.isNaN(val)) {
          state.vitals[k] = val;
          renderAll();
        }
      });
    });
  }

  function renderActions(evalRes) {
    const inds = evalRes.indicators;
    const env = evalRes.environment;
    const cards = [];
    if (inds.dose_rate_msv_day.status !== 'optimal') {
      cards.push({
        st: inds.dose_rate_msv_day.status,
        title: state.lang === 'tr' ? 'ALARA Radyasyon Kalkanlama Uyarısı' : 'Activate ALARA Radiation Shielding',
        body: state.lang === 'tr' ? env.shielding_note_tr : env.shielding_note_en,
      });
    }
    if (inds.spo2_pct.status !== 'optimal' || inds.cabin_co2_mmhg.status !== 'optimal') {
      cards.push({
        st: (inds.spo2_pct.status === 'critical' || inds.cabin_co2_mmhg.status === 'critical') ? 'critical' : 'watch',
        title: state.lang === 'tr' ? 'Kabin CO2 Tutucu ve Oksijen Kontrolü' : 'Verify Cabin O2 & CO2 Scrubber Airflow',
        body: state.lang === 'tr' ? 'Dik oturun, oksimetre temasını doğrulayın ve kabin fanlarını inceleyin.' : 'Rest upright, warm fingertip oximeter contact, and verify CO2 scrubber airflow.',
      });
    }
    if (inds.blood_glucose_mgdl.status !== 'optimal') {
      const low = state.vitals.blood_glucose_mgdl < 75;
      cards.push({
        st: inds.blood_glucose_mgdl.status,
        title: low ? (state.lang === 'tr' ? 'Hızlı Hipoglisemi Önlemi' : 'Immediate Low Glucose Protocol') : (state.lang === 'tr' ? 'Yüksek Glikoz Takibi' : 'Glycemic Elevation Watch'),
        body: low ? (state.lang === 'tr' ? '15 g hızlı karbonhidrat jeli alıp 15 dk sonra tekrar ölçün.' : 'Take 15 g oral carbohydrate gel and recheck glucose in 15 min.') : (state.lang === 'tr' ? 'Su tüketip 60 dk sonra tekrar ölçün.' : 'Hydrate and recheck in 60 min.'),
      });
    }
    if (!cards.length) {
      cards.push({
        st: 'optimal',
        title: state.lang === 'tr' ? 'Tüm Sistemler Normal — Görev Rutinine Devam' : 'All Physiological Indicators Nominal',
        body: (state.lang === 'tr' ? env.shielding_note_tr : env.shielding_note_en),
      });
    }
    els.actionsBox.innerHTML = cards.map((c) => `
      <div class="action-item status-${c.st}">
        <strong>${c.title}</strong>
        <span>${c.body}</span>
      </div>
    `).join('');
  }

  function renderTrendSvg(evalRes) {
    const key = els.trendMetricSelect.value;
    const ind = evalRes.indicators[key];
    const current = state.vitals[key];
    const [optLo, optHi] = ind.optimal_range;
    const baseline = 0.5 * (optLo + optHi);
    const pts = [];
    for (let sol = 1; sol <= 14; sol++) {
      const w = Math.sin(sol * 0.72) * (optHi - optLo) * 0.14;
      const frac = sol / 14;
      const yVal = baseline * (1 - frac) + current * frac + w * (1 - frac * 0.7);
      pts.push({ sol, yVal });
    }
    pts[13].yVal = current;

    const allVals = pts.map((p) => p.yVal).concat([optLo, optHi]);
    const vMin = Math.min.apply(null, allVals) * 0.94;
    const vMax = Math.max.apply(null, allVals) * 1.06 || 1;
    const padX = 40;
    const W = 520;
    const H = 148;
    const toX = (sol) => padX + ((sol - 1) / 13) * (W - padX - 15);
    const toY = (val) => 16 + (1 - (val - vMin) / (vMax - vMin || 1)) * (H - 34);

    const bandTop = toY(optHi);
    const bandBot = toY(optLo);
    const pathD = pts.map((p, idx) => `${idx === 0 ? 'M' : 'L'}${toX(p.sol).toFixed(1)},${toY(p.yVal).toFixed(1)}`).join(' ');
    const dots = pts.map((p) => `<circle cx="${toX(p.sol).toFixed(1)}" cy="${toY(p.yVal).toFixed(1)}" r="3.4" fill="#38bdf8"/>`).join('');

    els.trendSvg.innerHTML = `
      <rect x="${padX}" y="${Math.min(bandTop, bandBot)}" width="${W - padX - 15}" height="${Math.max(4, Math.abs(bandBot - bandTop))}" fill="#10b981" fill-opacity="0.14"/>
      <text x="6" y="${toY(optHi).toFixed(1)}" fill="#93a7c7" font-size="10">${optHi}</text>
      <text x="6" y="${toY(optLo).toFixed(1)}" fill="#93a7c7" font-size="10">${optLo}</text>
      <path d="${pathD}" fill="none" stroke="#38bdf8" stroke-width="2.4"/>
      ${dots}
      <text x="${padX}" y="162" fill="#93a7c7" font-size="10">Sol 1</text>
      <text x="270" y="162" fill="#93a7c7" font-size="10">Sol 7</text>
      <text x="${W - 42}" y="162" fill="#38bdf8" font-size="10">${state.lang === 'tr' ? 'Şimdi' : 'Now'} (${current})</text>
    `;
  }

  function renderCeitGuide(evalRes, gate) {
    const cards = Object.keys(C.ANATOMY_REGIONS).map((regId) => {
      const reg = evalRes.anatomy_regions[regId];
      const g = NON_MED_GUIDES[regId][state.lang];
      const title = state.lang === 'tr' ? reg.title_tr : reg.title_en;
      return `
        <div class="vital-card st-${reg.status}">
          <div class="vital-top">
            <strong class="vital-name">${title}</strong>
            <span class="pill status-${reg.status}">${statusLabel(reg.status)}</span>
          </div>
          <div style="font-size:0.81rem;"><b>${UI_I18N[state.lang].meaningLbl}:</b> ${g[0]}</div>
          <div style="font-size:0.81rem;"><b>${UI_I18N[state.lang].measureLbl}:</b> ${g[1]}</div>
          <div style="font-size:0.81rem;color:#7dd3fc;"><b>${UI_I18N[state.lang].actionLbl}:</b> ${g[2]}</div>
        </div>
      `;
    }).join('');
    els.ceitGuideContainer.innerHTML = `
      <p class="vital-range-hint" style="margin-top:0;">
        ${state.lang === 'tr'
          ? `<b>WerreduR LearningGate</b> Altyapısı (Dr. Zerrin Dağlı, CEIT Böl. — Mersin Üniv.): aktif düzey = <b>${gate.label_tr}</b> (Bilişsel Rezerv %${Math.round(gate.cognitive_reserve * 100)} · Hakimiyet %${Math.round(gate.mastery_index * 100)}).`
          : `Powered by <b>WerreduR LearningGate</b> (Dr. Zerrin Dagli, Dept. of CEIT — Mersin Univ.): active tier = <b>${gate.label_en}</b> (Cognitive Reserve ${Math.round(gate.cognitive_reserve * 100)}% · Mastery ${Math.round(gate.mastery_index * 100)}%).`}
      </p>
      <div class="vitals-grid">${cards}</div>
    `;
  }

  function computeGamify() {
    let xp = state.quizCorrect * 40 + (state.streakDays - 1) * 20;
    QUESTS.forEach((q) => { if (state.completedQuests.has(q.id)) xp += q.xp; });
    const adherence = Math.round((state.completedQuests.size / QUESTS.length) * 100);
    const isTr = state.lang === 'tr';
    const rank = xp >= 320
      ? (isTr ? 'Derin Uzay Homeostaz Komutanı' : 'Deep-Space Homeostasis Commander')
      : xp >= 200
        ? (isTr ? 'Görev Sağlık Sorumlusu' : 'Mission Flight Medic Steward')
        : xp >= 100
          ? (isTr ? 'Yörünge Sağlık Uzmanı' : 'Orbital Wellness Specialist')
          : (isTr ? 'Mürettebat Hazırlık Adayı' : 'Crew Readiness Cadet');
    const badges = [];
    if (state.completedQuests.has('ared_bone')) badges.push(isTr ? 'ARED Demir Omurga' : 'ARED Iron Spine');
    if (state.completedQuests.has('radiation_sync')) badges.push(isTr ? 'ALARA Kalkan Sorumlusu' : 'ALARA Shield Steward');
    if (state.completedQuests.has('evening_winddown')) badges.push(isTr ? 'Sirkadiyen Koruyucu' : 'Circadian Guardian');
    if (state.quizCorrect >= 2) badges.push(isTr ? 'Mürettebat Biyo-Okuryazarlık Yıldızı' : 'Crew Bio-Literacy Star');
    return { xp, adherence, rank, badges };
  }

  function renderQuestsAndQuiz(gam) {
    els.gamifyRankPill.textContent = gam.rank;
    els.gamifyXpSummary.textContent = state.lang === 'tr'
      ? `${gam.xp} XP · ${state.completedQuests.size}/${QUESTS.length} (%${gam.adherence}) · Seri ${state.streakDays} gün`
      : `${gam.xp} XP · ${state.completedQuests.size}/${QUESTS.length} (${gam.adherence}%) · Streak ${state.streakDays}d`;
    els.xpBarFill.style.width = Math.min(100, Math.round((gam.xp / 360) * 100)) + '%';
    els.badgeList.innerHTML = gam.badges.map((b) => `<span class="hazard-tag">${b}</span>`).join('');

    els.questList.innerHTML = QUESTS.map((q) => {
      const chk = state.completedQuests.has(q.id) ? 'checked' : '';
      const title = state.lang === 'tr' ? q.tTr : q.tEn;
      const win = state.lang === 'tr' ? q.winTr : q.winEn;
      const desc = state.lang === 'tr' ? q.dTr : q.dEn;
      return `
        <label class="quest-card">
          <input type="checkbox" data-quest="${q.id}" ${chk}>
          <div>
            <strong>${title} <span class="hazard-tag">+${q.xp} XP · ${win}</span></strong>
            <div class="vital-range-hint">${desc}</div>
          </div>
        </label>
      `;
    }).join('');
    els.questList.querySelectorAll('[data-quest]').forEach((cb) => {
      cb.addEventListener('change', (e) => {
        const qid = e.target.getAttribute('data-quest');
        if (e.target.checked) state.completedQuests.add(qid);
        else state.completedQuests.delete(qid);
        renderAll();
      });
    });

    const q = QUIZZES[state.quizIndex % QUIZZES.length];
    const qText = state.lang === 'tr' ? q.qTr : q.qEn;
    const opts = state.lang === 'tr' ? q.optsTr : q.optsEn;
    els.quizContainer.innerHTML = `
      <div class="panel-header" style="margin-bottom:6px;">
        <strong>${state.lang === 'tr' ? 'Mürettebat Hazırlık Mini-Testi' : 'Crew Readiness Micro-Quiz'} (${(state.quizIndex % QUIZZES.length) + 1}/${QUIZZES.length})</strong>
        <button type="button" id="btnNextQuiz">${state.lang === 'tr' ? 'Sonraki Soru' : 'Next'}</button>
      </div>
      <div style="font-size:0.88rem;font-weight:600;">${qText}</div>
      ${opts.map((opt, idx) => `<button type="button" class="quiz-option" data-quiz-opt="${idx}">${opt}</button>`).join('')}
      <div class="vital-range-hint" style="margin-top:8px;color:#bae6fd;">${state.quizFeedback}</div>
    `;
    document.getElementById('btnNextQuiz').addEventListener('click', () => {
      state.quizIndex = (state.quizIndex + 1) % QUIZZES.length;
      state.quizFeedback = '';
      renderAll();
    });
    els.quizContainer.querySelectorAll('[data-quiz-opt]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const chosen = parseInt(e.target.getAttribute('data-quiz-opt'), 10);
        if (chosen === q.correct) {
          state.quizCorrect += 1;
          state.quizStreak += 1;
          state.quizFeedback = '✔ +40 XP — ' + (state.lang === 'tr' ? q.expTr : q.expEn);
        } else {
          state.quizStreak = 0;
          state.quizFeedback = '✖ ' + (state.lang === 'tr' ? q.expTr : q.expEn);
        }
        renderAll();
      });
    });
  }

  function renderPacketInspector(evalRes) {
    els.packetHexBox.textContent = evalRes.packet_hex.match(/.{1,2}/g).join(' ');
    els.packetBreakdown.textContent = state.lang === 'tr'
      ? `Bayt [0]=0xA5 Sihirli Başlık · [1]=Ortam(${evalRes.environment.id}) · [2..21]=12 Sayısallaştırılmış Gösterge · [22..23]=CRC-16/CCITT-FALSE · ` +
        `WERR c=(${evalRes.werr_homeostatic.c_real}, ${evalRes.werr_homeostatic.c_imag}i), Kaçış=${evalRes.werr_homeostatic.escape_iter}/32, AğırlıkRAM=0 B`
      : `Bytes [0]=0xA5 Magic · [1]=Env(${evalRes.environment.id}) · [2..21]=12 Quantized Vitals · [22..23]=CRC-16/CCITT-FALSE · ` +
        `WERR c=(${evalRes.werr_homeostatic.c_real}, ${evalRes.werr_homeostatic.c_imag}i), Escape=${evalRes.werr_homeostatic.escape_iter}/32, WeightRAM=0 B`;
    if (state.lastSeuResult) {
      els.seuLogBox.innerHTML = state.lang === 'tr'
        ? `<strong>SEU Bit-Kayması Enjeksiyon Sonucu</strong><br>` +
          `Ters Çevrilen Bit #${state.lastSeuResult.flipped_bit} (Bayt ${state.lastSeuResult.flipped_byte}) → Bozulan Hex: <code>${state.lastSeuResult.corrupted_hex}</code><br>` +
          `<span style="color:#10b981;font-weight:700;">CRC-16 Bütünlük Kontrolü Bozuk Paketi Reddetti: ${state.lastSeuResult.seu_detected_by_crc} · Ağ Ağırlık RAM'i Hasarı: 0 Bayt</span>`
        : `<strong>Cosmic-Ray SEU Bit-Flip Simulation Result</strong><br>` +
          `Flipped Bit #${state.lastSeuResult.flipped_bit} (Byte ${state.lastSeuResult.flipped_byte}) → Corrupted Hex: <code>${state.lastSeuResult.corrupted_hex}</code><br>` +
          `<span style="color:#10b981;font-weight:700;">CRC-16 Integrity Check Rejected Corrupt Packet: ${state.lastSeuResult.seu_detected_by_crc} · Neural Weight RAM Corrupted: 0 Bytes</span>`;
    } else {
      els.seuLogBox.textContent = UI_I18N[state.lang].seuDefault;
    }
  }

  function renderNasaFeeds() {
    if (!state.nasaSnapshot) return;
    const sw = state.nasaSnapshot.space_weather || {};
    const scale = sw.noaa_s_scale || 'S0 (Quiet)';
    const st = sw.status || 'optimal';
    els.noaaHeaderChip.className = 'pill status-' + st;
    els.noaaHeaderChip.textContent = `${state.lang === 'tr' ? 'GOES Proton' : 'GOES Proton'}: ${sw.pfu_10mev ?? '--'} pfu · ${scale} · Kp ${sw.kp_index ?? '--'}`;

    els.noaaDetailCard.innerHTML = state.lang === 'tr'
      ? `<strong>${sw.source || 'NOAA SWPC'}</strong> · GOES-${sw.satellite || 18} (${sw.proton_time_tag || ''})<br>` +
        `&ge;10 MeV Proton Akışı: <b>${sw.pfu_10mev} pfu</b> (${scale}) · Gezegensel Kp: <b>${sw.kp_index}</b> · Tahmini LEO Modül Dozu: <b>${sw.estimated_leo_hab_msv_day} mSv/gün</b>`
      : `<strong>${sw.source || 'NOAA SWPC'}</strong> · GOES-${sw.satellite || 18} (${sw.proton_time_tag || ''})<br>` +
        `&ge;10 MeV Proton Flux: <b>${sw.pfu_10mev} pfu</b> (${scale}) · Planetary Kp: <b>${sw.kp_index}</b> · Estimated LEO Habitat Baseline: <b>${sw.estimated_leo_hab_msv_day} mSv/day</b>`;

    const studies = state.nasaSnapshot.nasa_osdr_studies || [];
    els.osdrList.innerHTML = studies.map((s) => `
      <div class="osdr-card">
        <a href="${s.url}" target="_blank" rel="noopener"><b>${s.accession}</b></a> — ${s.organism || 'Spaceflight'} (${s.project_type || 'OSDR'})
        <div class="vital-range-hint" style="color:#dbeafe;margin-top:2px;">${s.title}</div>
      </div>
    `).join('');
  }

  async function syncNasaAndNoaa() {
    try {
      const localResp = await fetch('/data/verified_nasa_telemetry.json');
      if (localResp.ok) {
        state.nasaSnapshot = await localResp.json();
        renderNasaFeeds();
      }
    } catch (_) {}

    // Upgrade NOAA SWPC live in browser (Access-Control-Allow-Origin: *)
    try {
      const [pResp, kpResp] = await Promise.all([
        fetch('https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json'),
        fetch('https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'),
      ]);
      if (pResp.ok && kpResp.ok) {
        const protons = await pResp.json();
        const kpRows = await kpResp.json();
        const ge10 = protons.filter((r) => r.energy === '>=10 MeV' && r.flux != null);
        const latestP = ge10[ge10.length - 1];
        const latestKp = kpRows[kpRows.length - 1];
        if (latestP && state.nasaSnapshot) {
          const pfu = Number(latestP.flux);
          let sScale = 'S0 (Quiet)', sStatus = 'optimal';
          if (pfu >= 1000) { sScale = 'S3+ (Strong)'; sStatus = 'critical'; }
          else if (pfu >= 10) { sScale = 'S1–S2 (Active)'; sStatus = 'watch'; }
          state.nasaSnapshot.space_weather = Object.assign({}, state.nasaSnapshot.space_weather, {
            source: 'NOAA SWPC Live Browser Feed',
            satellite: latestP.satellite,
            proton_time_tag: latestP.time_tag,
            pfu_10mev: Math.round(pfu * 1000) / 1000,
            noaa_s_scale: sScale,
            status: sStatus,
            kp_index: latestKp ? Number(latestKp.Kp) : state.nasaSnapshot.space_weather.kp_index,
          });
          renderNasaFeeds();
        }
      }
    } catch (_) {}

    // Optionally refresh OSDR via AstroSoma Cloudflare Pages Function when deployed
    try {
      const edgeResp = await fetch('/api/nasa-osdr?term=radiation+astronaut&size=4');
      if (edgeResp.ok) {
        const edgeJson = await edgeResp.json();
        if (edgeJson.ok && Array.isArray(edgeJson.studies) && edgeJson.studies.length && state.nasaSnapshot) {
          const existing = new Set(edgeJson.studies.map((x) => x.accession));
          const merged = edgeJson.studies.concat((state.nasaSnapshot.nasa_osdr_studies || []).filter((x) => !existing.has(x.accession)));
          state.nasaSnapshot.nasa_osdr_studies = merged;
          renderNasaFeeds();
        }
      }
    } catch (_) {}
  }

  // Real-time P-QRS-T ECG animation loop
  function startEcgLoop() {
    const canvas = document.getElementById('ecgCanvas');
    const ctx = canvas.getContext('2d');
    const hist = new Array(240).fill(0);

    function ecgSample(phase01) {
      // Normalized cardiac cycle [0, 1) -> P wave, QRS complex, T wave
      const g = (mu, sigma, amp) => amp * Math.exp(-Math.pow((phase01 - mu) / sigma, 2));
      return g(0.18, 0.032, 0.14) - g(0.37, 0.012, 0.16) + g(0.41, 0.013, 1.0) - g(0.45, 0.015, 0.28) + g(0.68, 0.055, 0.28);
    }

    let lastTs = performance.now();
    function tick(ts) {
      const dt = Math.min(0.05, (ts - lastTs) / 1000);
      lastTs = ts;
      const beatsPerSec = Math.max(0.5, state.vitals.heart_rate_bpm / 60.0);
      const jitter = Math.sin(ts * 0.002) * Math.min(0.08, (state.vitals.hrv_sdnn_ms || 40) / 1200);
      state.ecgPhase = (state.ecgPhase + dt * (beatsPerSec + jitter)) % 1.0;

      hist.shift();
      hist.push(ecgSample(state.ecgPhase));

      const W = canvas.width;
      const H = canvas.height;
      ctx.fillStyle = '#060e1a';
      ctx.fillRect(0, 0, W, H);

      ctx.strokeStyle = 'rgba(16, 185, 129, 0.12)';
      ctx.lineWidth = 1;
      for (let x = 0; x < W; x += 25) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
      for (let y = 0; y < H; y += 25) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

      ctx.strokeStyle = state.vitals.heart_rate_bpm > 118 || state.vitals.heart_rate_bpm < 42 ? '#ef4444' : '#10b981';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      const baseY = H * 0.62;
      for (let i = 0; i < hist.length; i++) {
        const px = (i / (hist.length - 1)) * W;
        const py = baseY - hist[i] * (H * 0.50);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // Camera Optical rPPG modal handlers
  async function openRppgModal() {
    const tr = state.lang === 'tr';
    els.rppgModal.classList.add('open');
    els.rppgReadout.textContent = tr ? 'Hazır' : 'Ready';
    els.rppgSub.textContent = UI_I18N[state.lang].rppgReadySub;
    els.btnApplyRppg.disabled = true;
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        state.rppgStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 320, height: 240 } });
        els.rppgVideo.srcObject = state.rppgStream;
      }
    } catch (_) {
      els.rppgSub.textContent = tr
        ? 'Fiziksel kamera izni yok; sentetik optik PPG dalga modu etkin.'
        : 'No physical camera granted; synthetic optical PPG trace mode active.';
    }
  }

  function closeRppgModal() {
    els.rppgModal.classList.remove('open');
    if (state.rppgStream) {
      state.rppgStream.getTracks().forEach((t) => t.stop());
      state.rppgStream = null;
      els.rppgVideo.srcObject = null;
    }
  }

  async function runRppgScan() {
    const tr = state.lang === 'tr';
    els.rppgReadout.textContent = tr ? 'Optik yeşil kanal örnekleniyor...' : 'Sampling optical green channel...';
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 48;
    const cctx = canvas.getContext('2d');
    const samples = [];
    const start = performance.now();
    while (performance.now() - start < 2400) {
      if (state.rppgStream && els.rppgVideo.readyState >= 2) {
        cctx.drawImage(els.rppgVideo, 0, 0, 64, 48);
        const img = cctx.getImageData(16, 12, 32, 24).data;
        let gSum = 0;
        for (let i = 1; i < img.length; i += 4) gSum += img[i];
        samples.push(gSum / (32 * 24));
      } else {
        samples.push(128 + 3.2 * Math.sin((performance.now() - start) * 0.0078));
      }
      await new Promise((r) => setTimeout(r, 40));
    }
    // Zero-crossing / mean-crossing peak counter -> BPM estimate
    const mean = samples.reduce((a, b) => a + b, 0) / samples.length;
    let crossings = 0;
    for (let i = 1; i < samples.length; i++) {
      if (samples[i - 1] < mean && samples[i] >= mean) crossings++;
    }
    const elapsedMin = 2.4 / 60.0;
    const estHr = Math.max(54, Math.min(128, Math.round(crossings / elapsedMin)));
    state.rppgEstimate = { hr: state.rppgStream ? estHr : 74.0 };
    els.rppgReadout.textContent = tr
      ? `Tahmini Nabız: ${state.rppgEstimate.hr} BPM (${samples.length} optik kare)`
      : `Estimated Pulse: ${state.rppgEstimate.hr} BPM (${samples.length} optical frames)`;
    els.btnApplyRppg.disabled = false;
  }

  function wireEvents() {
    els.envSelect.addEventListener('change', (e) => {
      state.vitals.environment = e.target.value;
      renderAll();
    });
    els.roleSelect.addEventListener('change', (e) => {
      state.crewRole = e.target.value;
      renderAll();
    });
    els.langToggle.addEventListener('click', () => {
      state.lang = state.lang === 'en' ? 'tr' : 'en';
      try {
        window.localStorage.setItem('astrosoma_lang', state.lang);
        const url = new URL(window.location.href);
        url.searchParams.set('lang', state.lang);
        window.history.replaceState({}, '', url.toString());
      } catch (_) {}
      renderAll();
    });

    document.querySelectorAll('.scenario-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.scenario-btn').forEach((x) => x.classList.remove('active'));
        btn.classList.add('active');
        const id = btn.getAttribute('data-scenario');
        state.scenario = id;
        state.vitals = Object.assign({}, SCENARIO_PRESETS[id]);
        els.envSelect.value = state.vitals.environment;
        renderAll();
      });
    });

    document.querySelectorAll('#anatomySvg .body-hotspot').forEach((g) => {
      const select = () => {
        state.selectedRegion = g.getAttribute('data-region');
        renderAll();
      };
      g.addEventListener('click', select);
      g.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(); } });
    });

    document.querySelectorAll('.tab-btn').forEach((b) => {
      b.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach((x) => x.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach((x) => x.classList.remove('active'));
        b.classList.add('active');
        document.getElementById(b.getAttribute('data-tab')).classList.add('active');
      });
    });

    els.trendMetricSelect.addEventListener('change', () => renderAll());
    document.getElementById('btnRefreshLive').addEventListener('click', syncNasaAndNoaa);

    document.getElementById('btnSeuTest').addEventListener('click', () => {
      const frame = C.packWerr24(state.vitals);
      state.lastSeuResult = C.simulateSeuBitflip(frame, Math.floor(Math.random() * 192));
      document.querySelector('[data-tab="tabNasaData"]').click();
      renderAll();
    });

    document.getElementById('btnExportJson').addEventListener('click', () => {
      const payload = JSON.stringify(C.evaluateAstronautState(state.vitals), null, 2);
      const blob = new Blob([payload], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `astrosoma_werr24_${state.vitals.environment}.json`;
      a.click();
    });

    document.getElementById('telemetryUpload').addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const text = String(reader.result);
          if (file.name.endsWith('.json')) {
            const parsed = JSON.parse(text);
            Object.keys(SLIDER_BOUNDS).forEach((k) => {
              if (typeof parsed[k] === 'number') state.vitals[k] = parsed[k];
            });
          } else {
            const lines = text.trim().split(/\r?\n/);
            if (lines.length >= 2) {
              const hdr = lines[0].split(',').map((h) => h.trim());
              const row = lines[1].split(',').map((v) => v.trim());
              hdr.forEach((k, i) => {
                if (Object.prototype.hasOwnProperty.call(SLIDER_BOUNDS, k) && !Number.isNaN(Number(row[i]))) {
                  state.vitals[k] = Number(row[i]);
                }
              });
            }
          }
          renderAll();
        } catch (err) {
          alert((state.lang === 'tr' ? 'Telemetri dosyası okunamadı: ' : 'Could not parse telemetry file: ') + err.message);
        }
      };
      reader.readAsText(file);
    });

    document.getElementById('btnCameraRppg').addEventListener('click', openRppgModal);
    document.getElementById('btnCloseRppg').addEventListener('click', closeRppgModal);
    document.getElementById('btnRunRppg').addEventListener('click', runRppgScan);
    els.btnApplyRppg.addEventListener('click', () => {
      if (state.rppgEstimate) {
        state.vitals.heart_rate_bpm = state.rppgEstimate.hr;
        renderAll();
      }
      closeRppgModal();
    });
  }

  wireEvents();
  renderAll();
  startEcgLoop();
  syncNasaAndNoaa();
})();
