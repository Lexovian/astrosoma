"""Adaptive CEIT / LearningGate crew pedagogy & gamification module.

Adapts Dr. Zerrin Dagli's LearningGate ZPD controller from jesmaat/WerreduR
(SSRN: 7641538, Zenodo DOI: 10.5281/zenodo.23128224) so non-medical astronauts
receive plain-language explanations, measurement coaching, and gamified
mission health adherence without clinical jargon overload.
"""

from __future__ import annotations

from typing import Any, Dict, List

ROUTINE_QUESTS: List[Dict[str, Any]] = [
    {
        "id": "morning_vitals",
        "xp": 50,
        "window_en": "07:30 Mission Time",
        "window_tr": "07:30 Görev Saati",
        "title_en": "Morning Rest BP, HR & SpO2 Check",
        "title_tr": "Sabah Dinlenik Tansiyon, Nabız ve SpO2 Ölçümü",
        "instruction_en": "Measure seated before caffeine: keep cuff at heart level and warm cold fingertips first.",
        "instruction_tr": "Kafein öncesi oturur pozisyonda ölçün: manşonu kalp hizasında tutun, soğuk parmakları ısıtın.",
    },
    {
        "id": "ared_bone",
        "xp": 80,
        "window_en": "11:00 Countermeasure Block",
        "window_tr": "11:00 Koruyucu Egzersiz Bloğu",
        "title_en": "ARED Resistive Bone & Spine Loading (45 min)",
        "title_tr": "ARED Dirençli Kemik ve Omurga Yüklemesi (45 dk)",
        "instruction_en": "Protects hip & lumbar bone mineral density (~1–1.5%/mo loss risk in microgravity) and vascular tone.",
        "instruction_tr": "Mikro yerçekiminde kalça ve bel kemik kaybını önler; damar tonusunu korur.",
    },
    {
        "id": "hydration_glucose",
        "xp": 45,
        "window_en": "15:00 Mid-Shift Hydration",
        "window_tr": "15:00 Vardiya Ortası Hidrasyon",
        "title_en": "Hydration & Capillary Glucose Sync",
        "title_tr": "Sıvı Tüketimi ve Kan Şekeri Kaydı",
        "instruction_en": "Spaceflight lowers plasma volume by ~10–15%. Drink 300 mL water/electrolytes and log glucose.",
        "instruction_tr": "Uzay uçuşunda plazma hacmi %10–15 azalır. 300 mL sıvı alın ve glikoz değerini kaydedin.",
    },
    {
        "id": "radiation_sync",
        "xp": 60,
        "window_en": "18:00 Dosimeter & NOAA Sync",
        "window_tr": "18:00 Dozimetre ve Uzay Havası Eşitleme",
        "title_en": "Verify Personal Dosimeter & Solar Proton Feed",
        "title_tr": "Kişisel Dozimetre ve Güneş Proton Akışı Kontrolü",
        "instruction_en": "Confirm cumulative dose stays well inside ALARA mission budget; review GOES >=10 MeV flux.",
        "instruction_tr": "Kümülatif dozun ALARA görev bütçesi içinde olduğunu ve GOES >=10 MeV proton akışını doğrulayın.",
    },
    {
        "id": "evening_winddown",
        "xp": 55,
        "window_en": "21:30 Sleep & Mood Check-In",
        "window_tr": "21:30 Uyku ve Ruh Hali Günlüğü",
        "title_en": "Circadian Dimming & Behavioral Readiness Log",
        "title_tr": "Sirkadiyen Işık Azaltma ve Ruh Hali Kaydı",
        "instruction_en": "Log 1–10 mood cleanly; orbital sunrises every 90 min disturb melatonin unless cabin LEDs dim.",
        "instruction_tr": "1–10 ruh halini girin; 90 dakikada bir gün doğumu nedeniyle kabin ışığını uyku moduna alın.",
    },
]

CREW_QUIZZES: List[Dict[str, Any]] = [
    {
        "id": "quiz_spo2_co2",
        "region": "resp",
        "question_en": "In a closed rover cabin, a crewmate reports a dull headache and cabin pCO2 climbs to 4.1 mmHg while SpO2 reads 96%. What is the safest first step?",
        "question_tr": "Basınçlı keşif aracında kabin pCO2 değeri 4.1 mmHg'ya çıkıp mürettebatta hafif baş ağrısı başlarken SpO2 %96 görünüyorsa ilk doğru adım nedir?",
        "options_en": [
            "Ignore it because SpO2 is above 95%.",
            "Inspect cabin air circulation & CO2 scrubber loop immediately and re-measure.",
            "Start heavy anaerobic exercise to raise heart rate.",
        ],
        "options_tr": [
            "SpO2 %95'in üzerinde olduğu için önemseme.",
            "Kabin hava sirkülasyonunu ve CO2 tutucuyu hemen kontrol et ve ölçümü tekrarla.",
            "Nabzı yükseltmek için ağır anaerobik egzersiz yap.",
        ],
        "correct_index": 1,
        "explain_en": "High cabin CO2 causes headaches and cognitive fog BEFORE blood SpO2 drops steeply. Always check airflow & CO2 scrubbers when pCO2 rises.",
        "explain_tr": "Yüksek kabin CO2 seviyesi, kandaki SpO2 ciddi düşmeden ÖNCE baş ağrısı ve odak kaybı yapar. Hava akışı ve tutucuları hemen doğrulamak gerekir.",
    },
    {
        "id": "quiz_sans_fluid",
        "region": "ocular",
        "question_en": "Why do astronauts often notice mild facial puffiness and near-vision focus shifts after entering microgravity?",
        "question_tr": "Astronotlarda mikro yerçekimine girdikten sonra neden yüz şişkinliği ve yakın görme odak değişimi görülebilir?",
        "options_en": [
            "Body fluids shift headward without Earth's gravity pulling them down (SANS).",
            "Red blood cells double inside orbital stations.",
            "Body temperature permanently increases to 40°C.",
        ],
        "options_tr": [
            "Yerçekimi olmadığında vücut sıvıları baş bölgesine doğru yer değiştirir (SANS).",
            "İstasyonda alyuvar sayısı iki katına çıkar.",
            "Vücut sıcaklığı kalıcı olarak 40°C'ye yükselir.",
        ],
        "correct_index": 0,
        "explain_en": "Headward fluid shift raises intracranial and ocular pressure (Spaceflight Associated Neuro-ocular Syndrome, SANS), monitored via eye/BP checks.",
        "explain_tr": "Baş bölgesine sıvı kayması göz içi ve kafa içi basıncı etkileyebilir (SANS); bu yüzden görme ve tansiyon takibi kritiktir.",
    },
    {
        "id": "quiz_spe_radiation",
        "region": "immune_rad",
        "question_en": "GOES satellites detect a strong Solar Proton Event (>=10 MeV storm) during a Lunar Base mission. What does ALARA recommend?",
        "question_tr": "Ay Üssü görevinde GOES uyduları güçlü bir Güneş Proton Olayı (>=10 MeV fırtınası) bildirirse ALARA ilkesi ne önerir?",
        "options_en": [
            "Proceed immediately with an unshielded surface EVA.",
            "Postpone outdoor EVA and shelter inside high-hydrogen / regolith-shielded modules.",
            "Turn off personal dosimeters to conserve battery.",
        ],
        "options_tr": [
            "Korunmasız yüzey yürüyüşüne (EVA) hemen çık.",
            "Dış EVA görevini ertele ve su/hidrojen veya regolit kalkanlı iç modüle çekil.",
            "Pil tasarrufu için kişisel dozimetreleri kapat.",
        ],
        "correct_index": 1,
        "explain_en": "ALARA ('As Low As Reasonably Achievable') prevents acute solar storm exposure by moving behind hydrogen-rich water walls or regolith shielding.",
        "explain_tr": "ALARA ('Mümkün Olan En Düşük Doz') ilkesine göre dış görev ertelenir ve su/polietilen/regolit kalkanlı sığınağa geçilir.",
    },
]

_NON_MEDICAL_GUIDES: Dict[str, Dict[str, Dict[str, str]]] = {
    "neuro": {
        "en": {
            "meaning": "Tracks sleep debt and mental readiness. Six 90-minute orbital sunrises/day confuse your internal clock.",
            "measure": "Log actual uninterrupted sleep hours and honest 1–10 focus/mood score before planning high-risk EVA work.",
            "action_tip": "Sleep < 6 h raises human error risk sharply; dim cabin lighting to warm amber 90 min before rest.",
        },
        "tr": {
            "meaning": "Uyku borcunu ve zihinsel hazırlığı izler. Günde 16 kez gün doğumu görmek iç saati bozabilir.",
            "measure": "Riskli görev öncesi kesintisiz uyku sürenizi ve 1–10 odak/ruh hali puanınızı girin.",
            "action_tip": "6 saatin altı uyku hata riskini artırır; uyku öncesi 90 dakika kabin ışığını sıcak tona düşürün.",
        },
    },
    "ocular": {
        "en": {
            "meaning": "Watches headward fluid shift signs affecting optic nerves and reading sharpness (SANS).",
            "measure": "Check visual Amsler grid crispness plus seated systolic BP & cabin CO2 together.",
            "action_tip": "High CO2 worsens cranial blood flow; keep cabin pCO2 < 2.5 mmHg and report new blurriness.",
        },
        "tr": {
            "meaning": "Mikro yerçekiminde sıvının başa kayması sonucu oluşan görme/optik sinir basıncını (SANS) izler.",
            "measure": "Yakın okuma keskinliğini, oturur tansiyonu ve kabin CO2 düzeyini birlikte değerlendirin.",
            "action_tip": "Yüksek CO2 kafa içi basıncı artırır; pCO2 < 2.5 mmHg hedefleyin ve bulanıklığı kaydedin.",
        },
    },
    "cardio": {
        "en": {
            "meaning": "Measures how smoothly your heart pumps blood without gravity's usual leg pull.",
            "measure": "Sit quietly 3 minutes, align cuff at heart level, and place dry finger softly on ECG/rPPG sensor.",
            "action_tip": "Before landing or Moon/Mars gravity return, prioritize hydration + lower-body resistance.",
        },
        "tr": {
            "meaning": "Kalbin yerçekimi olmadan veya düşük yerçekiminde kanı ne kadar verimli pompaladığını gösterir.",
            "measure": "3 dk dinlendikten sonra manşonu kalp hizasında takın ve EKG/rPPG sensörüne sabit temas sağlayın.",
            "action_tip": "Ay/Mars inişi öncesi ortostatik bayılmayı önlemek için sıvı + direnç antrenmanına öncelik verin.",
        },
    },
    "resp": {
        "en": {
            "meaning": "Checks whether your red blood cells carry ample oxygen (SpO2 >= 95%) in fresh scrubbed cabin air.",
            "measure": "Clip pulse oximeter onto a warm finger away from bright cockpit spotlights.",
            "action_tip": "Remember: high cabin CO2 can cause drowsiness even while SpO2 stays normal — watch BOTH gauges.",
        },
        "tr": {
            "meaning": "Kandaki oksijen doygunluğunu (SpO2 >= %95) ve kabin havasındaki CO2 birikimini birlikte izler.",
            "measure": "Oksimetreyi sıcak bir parmağa takın; parlak kokpit ışığının doğrudan sensöre vurmasını önleyin.",
            "action_tip": "SpO2 normalken bile yüksek kabin CO2 uyuşukluk yapar; iki göstergeyi birlikte takip edin.",
        },
    },
    "metab": {
        "en": {
            "meaning": "Blood sugar (glucose) fuels your brain during long shifts; extreme dips or spikes impair EVA judgment.",
            "measure": "Scan noninvasive sensor or finger-stick drop before meals or 2 h post-meal.",
            "action_tip": "Under 70 mg/dL requires fast carbohydrates within minutes; verify sensor calibration if unexpected.",
        },
        "tr": {
            "meaning": "Kan şekeri beynin ana yakıtıdır; aşırı düşüş veya çıkış uzay yürüyüşünde karar kalitesini bozar.",
            "measure": "Öğün öncesi veya öğünden 2 saat sonra sensör taraması yapın.",
            "action_tip": "70 mg/dL altı hızlı müdahale gerektirir; beklenmedik değerde sensörü yeniden doğrulayın.",
        },
    },
    "musculo": {
        "en": {
            "meaning": "Tracks core body thermal stability during spacewalks and supports bone/muscle protection routines.",
            "measure": "Check ear/oral probe or ingestible core capsule away from cold/hot drinks by 15 min.",
            "action_tip": "Microgravity weakens weight-bearing bones fast — never skip scheduled ARED/treadmill loading.",
        },
        "tr": {
            "meaning": "EVA sırasındaki vücut ısısını ve mikro yerçekiminde kemik/kas koruma disiplinini izler.",
            "measure": "Sıcak/soğuk içeceklerden en az 15 dk sonra çekirdek/kulak ölçümü yapın.",
            "action_tip": "Yerçekimsiz ortamda kemik kaybı hızlıdır; ARED ve direnç egzersizlerini aksatmayın.",
        },
    },
    "immune_rad": {
        "en": {
            "meaning": "Monitors daily space radiation (mSv/day) and immune-stress load outside Earth's protective magnetic shield.",
            "measure": "Sync waist dosimeter daily and cross-check live NOAA GOES solar proton flux.",
            "action_tip": "During Solar Proton Events, relocate sleeping bags inside water-walled storm shelters (ALARA).",
        },
        "tr": {
            "meaning": "Dünya manyetik kalkanı dışındaki radyasyon doz hızını (mSv/gün) ve bağışıklık yükünü izler.",
            "measure": "Günlük kişisel dozimetreyi eşitleyin ve canlı NOAA GOES güneş proton akışıyla karşılaştırın.",
            "action_tip": "Güneş fırtınasında ALARA gereği su-duvarlı iç sığınak bölmelerine geçin.",
        },
    },
}


def evaluate_learning_gate(
    quiz_streak: int = 0,
    routine_adherence_pct: float = 80.0,
    sleep_hours: float = 7.2,
    mood_score: float = 8.0,
    crew_role: str = "non_medical_pilot",
) -> Dict[str, Any]:
    """Select adaptive ZPD explanation tier without requiring ML weights in RAM.

    Low sleep / mood lowers cognitive load budget so UI surfaces concise
    step-by-step action cards (Tier 1) instead of dense clinical telemetry.
    """
    cognitive_reserve = min(1.0, max(0.0, 0.55 * (sleep_hours / 8.0) + 0.45 * (mood_score / 10.0)))
    mastery_index = min(1.0, max(0.0, 0.45 * min(1.0, quiz_streak / 3.0) + 0.55 * (routine_adherence_pct / 100.0)))

    if cognitive_reserve < 0.62 or mastery_index < 0.40:
        tier = 1
        label_en = "Tier 1 — High-Clarity Immediate Action Guide"
        label_tr = "Düzey 1 — Sade ve Hızlı Müdahale Rehberi"
    elif mastery_index < 0.78 or crew_role != "flight_surgeon_liaison":
        tier = 2
        label_en = "Tier 2 — Applied Space Physiology Coach"
        label_tr = "Düzey 2 — Uygulamalı Uzay Fizyolojisi Koçu"
    else:
        tier = 3
        label_en = "Tier 3 — Aerospace Clinical & HRP Research Brief"
        label_tr = "Düzey 3 — Havacılık Tıbbı ve HRP Araştırma Özeti"

    return {
        "zpd_tier": tier,
        "label_en": label_en,
        "label_tr": label_tr,
        "cognitive_reserve": round(cognitive_reserve, 3),
        "mastery_index": round(mastery_index, 3),
        "adapted_for_non_medical_crew": True,
    }


def get_non_medical_brief(region_id: str, lang: str = "en", tier: int = 1) -> Dict[str, str]:
    """Return plain-language non-medical guidance tailored to organ system & tier."""
    loc = "tr" if lang == "tr" else "en"
    guide = _NON_MEDICAL_GUIDES.get(region_id, _NON_MEDICAL_GUIDES["cardio"])[loc]
    return {
        "region_id": region_id,
        "tier": str(tier),
        "meaning": guide["meaning"],
        "measure": guide["measure"],
        "action_tip": guide["action_tip"],
    }


def compute_gamification_state(
    completed_quest_ids: List[str],
    quiz_correct_count: int = 0,
    streak_days: int = 1,
) -> Dict[str, Any]:
    """Compute mission wellness XP, adherence percentage, rank, and unlocked badges."""
    valid_ids = {q["id"]: q["xp"] for q in ROUTINE_QUESTS}
    unique_done = {qid for qid in completed_quest_ids if qid in valid_ids}
    xp = sum(valid_ids[qid] for qid in unique_done) + max(0, quiz_correct_count) * 40 + max(0, streak_days - 1) * 20
    adherence = round((len(unique_done) / float(len(ROUTINE_QUESTS))) * 100.0, 1)

    if xp >= 320:
        rank_en, rank_tr = "Deep-Space Homeostasis Commander", "Derin Uzay Homeostaz Komutanı"
    elif xp >= 200:
        rank_en, rank_tr = "Mission Flight Medic Steward", "Görev Sağlık Sorumlusu"
    elif xp >= 100:
        rank_en, rank_tr = "Orbital Wellness Specialist", "Yörünge Sağlık Uzmanı"
    else:
        rank_en, rank_tr = "Crew Readiness Cadet", "Mürettebat Hazırlık Adayı"

    badges = []
    if "ared_bone" in unique_done:
        badges.append("ARED Iron Spine")
    if "radiation_sync" in unique_done:
        badges.append("ALARA Shield Steward")
    if "evening_winddown" in unique_done:
        badges.append("Circadian Guardian")
    if quiz_correct_count >= 2:
        badges.append("Crew Bio-Literacy Star")

    return {
        "xp": xp,
        "adherence_pct": adherence,
        "completed_count": len(unique_done),
        "total_quests": len(ROUTINE_QUESTS),
        "streak_days": max(1, streak_days),
        "rank_en": rank_en,
        "rank_tr": rank_tr,
        "badges": badges,
    }
