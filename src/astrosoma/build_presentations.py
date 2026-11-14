"""Build widescreen 7-slide EN & TR HTML/PDF presentations using Playwright Chromium."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]


def _slide_css() -> str:
    return """
    @page { size: 13.333in 7.5in; margin: 0; }
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0;
      background: #060b16; color: #edf4ff;
      font-family: 'Segoe UI', Inter, Arial, sans-serif;
    }
    .slide {
      width: 13.333in; height: 7.5in;
      padding: 0.48in 0.62in;
      position: relative;
      overflow: hidden;
      page-break-after: always;
      background: radial-gradient(circle at 88% 12%, #13294b 0%, #070d1b 60%);
      display: flex; flex-direction: column; justify-content: space-between;
    }
    .slide:last-child { page-break-after: auto; }
    .hdr {
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid rgba(56, 189, 248, 0.28);
      padding-bottom: 10px; margin-bottom: 14px;
    }
    .eyebrow {
      font-size: 13px; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #38bdf8;
    }
    .pg { font-size: 13px; color: #93a7c7; font-weight: 600; }
    h1 { font-size: 42px; line-height: 1.12; margin: 8px 0 14px; color: #ffffff; }
    h2 { font-size: 30px; line-height: 1.18; margin: 0 0 14px; color: #f8fafc; }
    h3 { font-size: 17px; margin: 0 0 8px; color: #7dd3fc; }
    p, li { font-size: 15.5px; line-height: 1.48; color: #dbeafe; margin: 0 0 8px; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: stretch; flex: 1; }
    .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; align-items: stretch; flex: 1; }
    .hero-grid { display: grid; grid-template-columns: 1.45fr 0.9fr; gap: 30px; align-items: center; flex: 1; }
    .card {
      background: rgba(15, 29, 54, 0.88);
      border: 1px solid rgba(56, 189, 248, 0.28);
      border-radius: 14px; padding: 18px 20px;
      display: flex; flex-direction: column; justify-content: flex-start;
    }
    .kpi { font-size: 28px; font-weight: 800; color: #10b981; font-family: Consolas, monospace; margin-bottom: 4px; }
    .kpi.warn { color: #f59e0b; }
    .kpi.cyan { color: #38bdf8; }
    .patch-wrap {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: rgba(12, 23, 44, 0.82); border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 18px; padding: 20px;
    }
    .patch-wrap img { width: 310px; height: 310px; border-radius: 16px; object-fit: cover; }
    .pill {
      display: inline-block; padding: 4px 11px; border-radius: 999px;
      font-size: 12.5px; font-weight: 700; margin-right: 6px; margin-bottom: 6px;
      background: rgba(56, 189, 248, 0.16); color: #bae6fd; border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .pill.green { background: rgba(16, 185, 129, 0.16); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.45); }
    table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 6px; }
    th, td { border: 1px solid rgba(56, 189, 248, 0.24); padding: 7px 10px; text-align: left; }
    th { background: rgba(56, 189, 248, 0.14); color: #7dd3fc; font-weight: 700; }
    code { font-family: Consolas, monospace; background: rgba(2, 6, 23, 0.75); padding: 2px 6px; border-radius: 5px; color: #7dd3fc; font-size: 13.5px; }
    .ftr {
      border-top: 1px solid rgba(56, 189, 248, 0.2);
      padding-top: 8px; margin-top: 12px;
      display: flex; justify-content: space-between; font-size: 12.5px; color: #93a7c7;
    }
    """


def _build_slides_html(lang: str, snap: Dict[str, Any]) -> str:
    is_tr = lang == "tr"
    sw = snap.get("space_weather", {})
    studies = snap.get("nasa_osdr_studies", [])[:4]
    study_rows = "".join(
        f"<tr><td><code>{escape(s['accession'])}</code></td><td>{escape(s['organism'])}</td><td>{escape(s['title'][:78])}...</td></tr>"
        for s in studies
    )
    patch_uri = (ROOT / "assets" / "astrosoma_mission_patch.jpg").as_uri()

    if is_tr:
        s1 = f"""
        <section class="slide">
          <div class="hdr"><span class="eyebrow">NASA Space Apps Challenge 2026 · Universal Event</span><span class="pg">1 / 7</span></div>
          <div class="hero-grid">
            <div>
              <span class="pill green">CANLI: https://astrosoma.space/</span>
              <span class="pill">0-SRAM Otonom Triyaj</span>
              <span class="pill">CEIT Uyarlanır Mürettebat UX</span>
              <h1>AstroSoma</h1>
              <p style="font-size:20px;color:#7dd3fc;font-weight:600;margin-bottom:18px;">
                Uzay Görevlerinde Astronotlar İçin Sıfır-SRAM Bioneural ve Otonom Sağlık İzleme Yazılımı
              </p>
              <div class="card">
                <p><b>Takım Lideri:</b> Dağhan Dağlı (<code>@Lexovian</code>) — Yapay Zeka ve Sistem Mimarisi (<i>Lexovian/WerrSoma</i>)</p>
                <p><b>Eş-Araştırmacı:</b> Dr. Zerrin Dağlı (<code>@jesmaat</code>) — Bilgisayar ve Öğretim Teknolojileri Eğitimi (CEIT) Doktora, Mersin Üniv. (<i>jesmaat/WerreduR</i>)</p>
                <p style="margin-bottom:0;"><b>Açık Kaynak &amp; İletişim:</b> <code>github.com/Lexovian/astrosoma</code> (Apache-2.0) · <code>info@astrosoma.space</code></p>
              </div>
            </div>
            <div class="patch-wrap">
              <img src="{patch_uri}" alt="AstroSoma Mission Patch">
              <div style="margin-top:10px;font-size:13px;color:#93a7c7;">Mission Patch (SI-GENERATED) · WERR-24 &amp; CEIT</div>
            </div>
          </div>
          <div class="ftr"><span>Create Health Monitoring Software for Astronauts on Space Missions</span><span>astrosoma.space</span></div>
        </section>"""

        s2 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Görev Problemi ve NASA HRP 5 Tehlikesi</span><span class="pg">2 / 7</span></div>
          <h2>Dünya'dan Uzakta Mürettebat Sağlığı Neden Otonom Olmalı?</h2>
          <div class="grid2">
            <div class="card">
              <h3>NASA HRP 5 Uzay Uçuşu Tehlikesi</h3>
              <ul>
                <li><b>Uzay Radyasyonu:</b> GCR ve Güneş Proton Olayları (SPE) hücresel doz yükü ve bellek bit-kaymaları (SEU) üretir.</li>
                <li><b>Dünya'dan Uzaklık:</b> Mars görevlerinde tek yön sinyal gecikmesi <b>22 dakikaya</b> ulaşır — Yer uçuş hekimi canlı müdahale edemez.</li>
                <li><b>Değişen Yerçekimi:</b> Başa sıvı kayması (<b>SANS</b>), aylık %1–1.5 kemik kaybı ve ortostatik intolerans gelişir.</li>
                <li><b>İzolasyon ve Kapalı Ortam:</b> Günde 16 yörünge gün doğumu uykuyu bozar; kabin <b>CO2</b> yükselmesi SpO2 düşmeden bilişi etkiler.</li>
              </ul>
            </div>
            <div class="card">
              <h3>Klasik Yapay Zeka Modelleri Neden Yetersiz?</h3>
              <div class="kpi warn">SRAM Bit-Kayması (SEU) Riski</div>
              <p>Derin öğrenme modelleri megabaytlarca/gigabaytlarca öğrenilmiş ağırlığı değişebilir SRAM bellekte saklar. Kozmik ışın kaynaklı tek bir bit-kayması (Single-Event Upset), yer bağlantısı yokken klinik triyaj ağırlıklarını sessizce bozabilir.</p>
              <div style="margin-top:12px;" class="kpi">AstroSoma Çözümü: 0-Bayt Ağırlık RAM</div>
              <p>Ağırlıksız prosedürel sınır matematiği (<code>WERR-24</code>) + deterministik <code>NASA-STD-3001</code> klinik koruma eşikleri + <code>CRC-16</code> paket doğrulaması.</p>
            </div>
          </div>
          <div class="ftr"><span>NASA HRP 5 Hazards &amp; CSA Radiation Research</span><span>astrosoma.space · 2 / 7</span></div>
        </section>"""

        s3 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Çekirdek Mimari · Lexovian/WerrSoma Tabanlı</span><span class="pg">3 / 7</span></div>
          <h2>İki Katmanlı Güvenli Triyaj: NASA Eşikleri + 24 Bayt 0-SRAM WERR-24</h2>
          <div class="grid2">
            <div class="card">
              <h3>192-Bit (24 Bayt) Değişmez Telemetri Çerçevesi</h3>
              <table>
                <tr><th>Bayt</th><th>Alan</th><th>Çözünürlük</th></tr>
                <tr><td><code>0..1</code></td><td>Sihirli Başlık + Ortam</td><td><code>0xA5</code> + 5 Görev Ortamı</td></tr>
                <tr><td><code>2..9</code></td><td>HR, Tansiyon (SBP/DBP), SpO2, Isı</td><td>0.1 BPM, 1 mmHg, 0.01%, 0.01°C</td></tr>
                <tr><td><code>10..17</code></td><td>Glikoz, Doz Hızı, Uyku, Ruh, HRV</td><td>0.1 mg/dL, 1 µSv/g, 1 dk, SDNN</td></tr>
                <tr><td><code>18..23</code></td><td>Kabin pCO2, Küm. Doz, CRC-16</td><td><code>CRC-16/CCITT-FALSE</code></td></tr>
              </table>
            </div>
            <div class="card">
              <h3>Sıfır-SRAM Homeostaz Rezervi (<code>z → z² + c</code>)</h3>
              <p>12 fizyolojik/radyasyon göstergesi, 4 boyutlu yük vektörüne normalize edilip Mandelbrot ana kardiyoid kararlılık sınırına (32 adım) haritalanır:</p>
              <ul>
                <li><b>Değişebilir Ağırlık RAM'i:</b> <code>0 Bayt</code> (öğrenilmiş matris yoktur).</li>
                <li><b>Tam Doğrulama:</b> Python ve JavaScript arasında bit-düzeyinde özdeş 24-bayt çıktı ve <code>192/192</code> tek-bit SEU hata tespiti.</li>
                <li><b>İki Katmanlı Güvenlik:</b> Kesin NASA-STD-3001 / ALARA sınırları asla kara kutu tarafından ezilmez.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Zenodo DOI: 10.5281/zenodo.22996625 (WerrSoma)</span><span>astrosoma.space · 3 / 7</span></div>
        </section>"""

        s4 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Etkileşimli Kullanıcı Deneyimi</span><span class="pg">4 / 7</span></div>
          <h2>Tıklanabilir İnsan Anatomisi, Çoklu Girdi ve 5 Uzay Ortamı</h2>
          <div class="grid3">
            <div class="card">
              <h3>7 Tıklanabilir Vücut Bölgesi</h3>
              <ul>
                <li><b>Nöro / Uyku:</b> Sirkadiyen &amp; Ruh Hali</li>
                <li><b>Oküler (SANS):</b> Kafa içi sıvı basıncı</li>
                <li><b>Kardiyovasküler:</b> Canlı Lead-II EKG &amp; BP</li>
                <li><b>Solunum:</b> SpO2 + Kabin pCO2 eşleşmesi</li>
                <li><b>Metabolik:</b> Kan şekeri &amp; hidrasyon</li>
                <li><b>Kas-İskelet:</b> Vücut ısısı + ARED kemik yükü</li>
                <li><b>Bağışıklık &amp; Radyasyon:</b> ALARA + GOES</li>
              </ul>
            </div>
            <div class="card">
              <h3>Çoklu Veri Girdi Kanalları</h3>
              <ul>
                <li><b>Klavye &amp; Kaydırıcı:</b> 12 göstergede anlık simülasyon.</li>
                <li><b>Kamera Optik rPPG:</b> Tarayıcı <code>getUserMedia</code> yeşil-kanal nabız çıkarımı (+ donanımsız sentetik yedek).</li>
                <li><b>JSON/CSV Yükleme:</b> Taşınabilir ultrason &amp; giyilebilir sensör kayıtlarını içeri aktarma.</li>
                <li><b>Canlı EKG + 14 Sol Trend:</b> Renk kodlu (Yeşil/Kehribar/Kırmızı) dinamik grafikler.</li>
              </ul>
            </div>
            <div class="card">
              <h3>5 Uzay Görev Ortamı</h3>
              <ul>
                <li><b>ISS İstasyonu:</b> 0 g, canlı hekim bağlantısı</li>
                <li><b>Orion Aracı:</b> Ay geçiş rölesi + su-duvarı sığınak</li>
                <li><b>Yüzey Aracı (Rover):</b> EVA CO2 &amp; soğutma izlemi</li>
                <li><b>Artemis Ay Üssü:</b> 0.165 g + regolit kalkan</li>
                <li><b>Mars Transit / Üs:</b> 22 dk gecikme — Tam Otonom Mod</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Canlı Uygulama: https://astrosoma.space/</span><span>astrosoma.space · 4 / 7</span></div>
        </section>"""

        s5 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">CEIT Pedagojik Yaklaşım · jesmaat/WerreduR Tabanlı</span><span class="pg">5 / 7</span></div>
          <h2>Tıp Dışı Astronotlar İçin Sade Dil ve Oyunlaştırılmış Sağlık Rutini</h2>
          <div class="grid2">
            <div class="card">
              <h3>Uyarlanır <code>LearningGate</code> (CEIT — Mersin Üniv.)</h3>
              <p>Dr. Zerrin Dağlı'nın <i>Procedural Fractal Pedagogy</i> (SSRN <code>7641538</code>) modeliyle uyku, ruh hali ve bilgi durumuna göre ZPD anlatım düzeyi otomatik seçilir:</p>
              <ul>
                <li><b>Düzey 1 (Yüksek Yorgunlukta):</b> Tek cümle sade anlam + güvenli ölçüm adımı + <i>"Şu An Ne Yapmalısın?"</i> kartı.</li>
                <li><b>Düzey 2 (Mürettebat Koçu):</b> Mikro yerçekimi fizyolojisi (neden kabin CO2'si SpO2'den önce uyarır?).</li>
                <li><b>Düzey 3 (Uçuş Hekimi Özeti):</b> Klinik aralıklar ve NASA HRP risk bağlantıları.</li>
              </ul>
            </div>
            <div class="card">
              <h3>Görev Rutini İstemleri ve Oyunlaştırma</h3>
              <div class="kpi cyan">+290 XP Günlük Görev Döngüsü</div>
              <ul>
                <li><b>Zamanlı Hatırlatıcılar:</b> Sabah Tansiyon/SpO2, 11:00 ARED Kemik Direnci (45 dk), Hidrasyon, Dozimetre, Akşam Işık Azaltma.</li>
                <li><b>Rozet &amp; Rütbe Sistemi:</b> <i>ARED Iron Spine</i>, <i>ALARA Shield Steward</i>, <i>Circadian Guardian</i>.</li>
                <li><b>3 Soruluk Mürettebat Testi:</b> SANS, CO2 vs SpO2 ve SPE sığınak kararlarını pekiştirir.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Department of Computer Education &amp; Instructional Technology (CEIT)</span><span>astrosoma.space · 5 / 7</span></div>
        </section>"""

        s6 = f"""
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Gerçek NASA Verileri ve Otomatik Doğrulama</span><span class="pg">6 / 7</span></div>
          <h2>Canlı NASA OSDR + NOAA SWPC Entegrasyonu ve Test Kanıtları</h2>
          <div class="grid2">
            <div class="card">
              <h3>Doğrulanmış Gerçek Veri Kaynakları</h3>
              <p><b>NOAA SWPC GOES Canlı Akışı:</b> ≥10 MeV proton = <code>{escape(str(sw.get('pfu_10mev', '--')))} pfu</code> ({escape(str(sw.get('noaa_s_scale', 'S0')))}), <b>Kp = {escape(str(sw.get('kp_index', '--')))}</b>.</p>
              <table>
                <tr><th>OSDR ID</th><th>Organizma</th><th>Doğrulanmış Çalışma</th></tr>
                {study_rows}
              </table>
            </div>
            <div class="card">
              <h3>Ölçülmüş Mühendislik Doğrulaması</h3>
              <div class="kpi">6 / 6 Pytest Suite BAŞARILI</div>
              <ul>
                <li><b>Bit-Düzeyinde Parite:</b> Python (<code>codec_werr24.py</code>) ve JavaScript (<code>werr24_core.js</code>) Node.js çapraz testinde özdeş paket hex ve rezerv skoru verdi.</li>
                <li><b>192 / 192 SEU Testi:</b> 24 baytlık çerçevedeki tüm 192 bit tek tek ters çevrilerek CRC-16'nın %100 hata yakaladığı ve model ağırlık belleğinin <code>0 Bayt</code> kaldığı doğrulandı.</li>
                <li><b>Cloudflare Edge CORS Vekili:</b> <code>/api/nasa-osdr</code> + çevrimdışı JSON önbellek.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>osdr.nasa.gov · services.swpc.noaa.gov</span><span>astrosoma.space · 6 / 7</span></div>
        </section>"""

        s7 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Açık Kaynak Yayın ve Yol Haritası</span><span class="pg">7 / 7</span></div>
          <h2>Uzaya Hazır Mimari · Hemen Deneyin</h2>
          <div class="grid2">
            <div class="card">
              <h3>Canlı Ekosistem Bağlantıları</h3>
              <ul>
                <li><b>Canlı Web Uygulaması:</b> <code>https://astrosoma.space/</code> (Cloudflare Pages, Full Strict SSL, Edge OSDR Proxy)</li>
                <li><b>Kaynak Kodu (Apache-2.0):</b> <code>https://github.com/Lexovian/astrosoma</code></li>
                <li><b>Takım Sayfası:</b> <code>spaceappschallenge.org/2026/find-a-team/astrosoma1/</code></li>
                <li><b>İletişim:</b> <code>info@astrosoma.space</code></li>
              </ul>
            </div>
            <div class="card">
              <h3>Sonraki Görev Aşamaları</h3>
              <ul>
                <li><b>Donanım Köprüsü:</b> Arduino / WERRobotics giyilebilir nabız oksimetresi ve I2C dozimetrelerden doğrudan seri WERR-24 paketi akışı.</li>
                <li><b>Klinik Kalibrasyon:</b> Daha fazla NASA ALSDA / OSDR insan uçuşu fenotip serisinin eklenmesi.</li>
                <li><b>Mürettebat Hazırlığı:</b> Dünya çapındaki analog habitat ekiplerinin (MDRS, HI-SEAS) CEIT rehber modüllerini test etmesi.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Team AstroSoma · Dağhan Dağlı &amp; Dr. Zerrin Dağlı</span><span>NASA Space Apps Challenge 2026</span></div>
        </section>"""
        title = "AstroSoma — NASA Space Apps 2026 Sunumu (TR)"
    else:
        s1 = f"""
        <section class="slide">
          <div class="hdr"><span class="eyebrow">NASA Space Apps Challenge 2026 · Universal Event</span><span class="pg">1 / 7</span></div>
          <div class="hero-grid">
            <div>
              <span class="pill green">LIVE: https://astrosoma.space/</span>
              <span class="pill">0-SRAM Autonomous Triage</span>
              <span class="pill">CEIT Adaptive Crew UX</span>
              <h1>AstroSoma</h1>
              <p style="font-size:20px;color:#7dd3fc;font-weight:600;margin-bottom:18px;">
                Zero-SRAM Bioneural &amp; Homeostatic Health Monitoring Software for Astronauts on Space Missions
              </p>
              <div class="card">
                <p><b>Team Owner:</b> Dağhan Dağlı (<code>@Lexovian</code>) — AI &amp; Systems Architecture (<i>Lexovian/WerrSoma</i>)</p>
                <p><b>Co-Investigator:</b> Dr. Zerrin Dağlı (<code>@jesmaat</code>) — Ph.D., Department of Computer Education &amp; Instructional Technology (CEIT), Mersin Univ. (<i>jesmaat/WerreduR</i>)</p>
                <p style="margin-bottom:0;"><b>Open Source &amp; Contact:</b> <code>github.com/Lexovian/astrosoma</code> (Apache-2.0) · <code>info@astrosoma.space</code></p>
              </div>
            </div>
            <div class="patch-wrap">
              <img src="{patch_uri}" alt="AstroSoma Mission Patch">
              <div style="margin-top:10px;font-size:13px;color:#93a7c7;">Mission Patch (SI-GENERATED) · WERR-24 &amp; CEIT</div>
            </div>
          </div>
          <div class="ftr"><span>Challenge: Create Health Monitoring Software for Astronauts on Space Missions</span><span>astrosoma.space</span></div>
        </section>"""

        s2 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Deep-Space Problem &amp; NASA HRP 5 Hazards</span><span class="pg">2 / 7</span></div>
          <h2>Why Astronaut Health Monitoring Must Be Radiation-Resilient &amp; Autonomous</h2>
          <div class="grid2">
            <div class="card">
              <h3>NASA HRP 5 Hazards of Human Spaceflight</h3>
              <ul>
                <li><b>Space Radiation:</b> Galactic Cosmic Rays (GCR) &amp; Solar Proton Events (SPE) increase biological dose AND trigger Single-Event Upsets (SEUs) in avionics SRAM.</li>
                <li><b>Distance from Earth:</b> Mars transit reaches <b>22-minute one-way latency</b> — flight surgeons cannot intervene live.</li>
                <li><b>Altered Gravity Fields:</b> Causes cephalad fluid shift (<b>SANS</b>), ~1–1.5%/mo bone mineral loss, and orthostatic intolerance.</li>
                <li><b>Isolation &amp; Closed Cabin:</b> 16 orbital sunrises/day impair sleep; rising <b>CO2</b> causes headache before SpO2 drops.</li>
              </ul>
            </div>
            <div class="card">
              <h3>Why Heavy Learned Weights Fail Deep Space</h3>
              <div class="kpi warn">SRAM Bit-Flip Vulnerability</div>
              <p>Conventional neural networks store megabytes to gigabytes of learned parameters in mutable SRAM. A single unmitigated cosmic-ray bit-flip can silently distort triage thresholds when Earth links are unavailable.</p>
              <div style="margin-top:12px;" class="kpi">AstroSoma Defense: 0 Bytes Weight RAM</div>
              <p>Deterministic <code>WERR-24</code> procedural escape boundary + transparent <code>NASA-STD-3001</code> guardrails + <code>CRC-16/CCITT-FALSE</code> packet authentication.</p>
            </div>
          </div>
          <div class="ftr"><span>NASA HRP 5 Hazards &amp; CSA Radiation Research</span><span>astrosoma.space · 2 / 7</span></div>
        </section>"""

        s3 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Core Architecture · Anchored to Lexovian/WerrSoma</span><span class="pg">3 / 7</span></div>
          <h2>Dual-Layer Triage: Clinical Guardrails + 24-Byte 0-SRAM WERR-24 Protocol</h2>
          <div class="grid2">
            <div class="card">
              <h3>Immutable 192-Bit (24-Byte) Telemetry Frame</h3>
              <table>
                <tr><th>Bytes</th><th>Fields</th><th>Quantization Resolution</th></tr>
                <tr><td><code>0..1</code></td><td>Magic + Environment ID</td><td><code>0xA5</code> + 5 Space Environments</td></tr>
                <tr><td><code>2..9</code></td><td>HR, BP (SBP/DBP), SpO2, Core Temp</td><td>0.1 BPM, 1 mmHg, 0.01%, 0.01°C</td></tr>
                <tr><td><code>10..17</code></td><td>Glucose, Dose Rate, Sleep, Mood, HRV</td><td>0.1 mg/dL, 1 µSv/d, 1 min, SDNN</td></tr>
                <tr><td><code>18..23</code></td><td>Cabin pCO2, Cum. Dose, CRC-16</td><td><code>CRC-16/CCITT-FALSE</code> over 0..22</td></tr>
              </table>
            </div>
            <div class="card">
              <h3>Zero-SRAM Procedural Homeostatic Index (<code>z → z² + c</code>)</h3>
              <p>12 physiological &amp; habitat variables normalize into a 4D strain vector mapped onto the quadratic stability boundary (32 iterations):</p>
              <ul>
                <li><b>Mutable Neural Weight RAM:</b> <code>0 Bytes</code> — zero weight corruption vector.</li>
                <li><b>Cross-Runtime Parity:</b> Bit-identical 24-byte frames &amp; reserve scores verified across Python &amp; browser JS.</li>
                <li><b>Clinical Safety First:</b> Explicit NASA-STD-3001 / ALARA limits always govern alerts transparently.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>WerrSoma Reference DOI: 10.5281/zenodo.22996625</span><span>astrosoma.space · 3 / 7</span></div>
        </section>"""

        s4 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Challenge UX Fulfillment</span><span class="pg">4 / 7</span></div>
          <h2>Interactive Human Anatomy, Multi-Modal Inputs &amp; 5 Space Environments</h2>
          <div class="grid3">
            <div class="card">
              <h3>7 Clickable Body Systems</h3>
              <ul>
                <li><b>Neuro / Brain:</b> Sleep &amp; Mood readiness</li>
                <li><b>Ocular (SANS):</b> Cephalad fluid &amp; pCO2 watch</li>
                <li><b>Cardiovascular:</b> Lead-II ECG, HR, BP &amp; HRV</li>
                <li><b>Respiratory:</b> SpO2 + Cabin pCO2 co-alerts</li>
                <li><b>Metabolic:</b> Capillary glucose &amp; hydration</li>
                <li><b>Musculoskeletal:</b> Core temp &amp; ARED bone loading</li>
                <li><b>Immune &amp; Radiation:</b> ALARA + GOES flux</li>
              </ul>
            </div>
            <div class="card">
              <h3>Multi-Modal Data Capture</h3>
              <ul>
                <li><b>Keyboard / Sliders:</b> Instant sensitivity exploration across all 12 metrics.</li>
                <li><b>Webcam Optical rPPG:</b> Browser <code>getUserMedia</code> green-channel pulse estimation (+ deterministic optical waveform fallback).</li>
                <li><b>JSON / CSV Import:</b> Replays wearable &amp; portable ultrasound telemetry logs.</li>
                <li><b>Dynamic Charts:</b> Real-time Canvas P-QRS-T ECG &amp; 14-Sol nominal band trends.</li>
              </ul>
            </div>
            <div class="card">
              <h3>5 Mission Environments</h3>
              <ul>
                <li><b>ISS Station:</b> 0 g, live flight surgeon link</li>
                <li><b>Orion Spacecraft:</b> Transit relay &amp; water-wall storm shelter</li>
                <li><b>Surface Rover:</b> EVA CO2 scrubber &amp; thermal watch</li>
                <li><b>Artemis Lunar Base:</b> 0.165 g + regolith overburden</li>
                <li><b>Mars Transit / Hab:</b> Up to 22-min delay — Autonomous Mode</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Live Web Console: https://astrosoma.space/</span><span>astrosoma.space · 4 / 7</span></div>
        </section>"""

        s5 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">CEIT Adaptive Pedagogy · Anchored to jesmaat/WerreduR</span><span class="pg">5 / 7</span></div>
          <h2>Plain-Language Crew Explanations &amp; Gamified Health Routines</h2>
          <div class="grid2">
            <div class="card">
              <h3>Adaptive <code>LearningGate</code> (Dept. of CEIT, Mersin Univ.)</h3>
              <p>Built on Dr. Zerrin Dağlı's <i>Procedural Fractal Pedagogy</i> (SSRN <code>7641538</code>), cognitive reserve (sleep + mood) and mastery dynamically select the ZPD tier:</p>
              <ul>
                <li><b>Tier 1 (High Fatigue / Stress):</b> Ultra-clear analogy, step-by-step measurement tip, and one immediate action.</li>
                <li><b>Tier 2 (Crew Coach):</b> Spaceflight rationale (why rising CO2 impairs judgment before SpO2 drops).</li>
                <li><b>Tier 3 (Medical Liaison):</b> Full NASA HRP hazard cross-references and clinical operational bands.</li>
              </ul>
            </div>
            <div class="card">
              <h3>Scheduled Routine Prompts &amp; Gamification</h3>
              <div class="kpi cyan">+290 XP Daily Mission Adherence Loop</div>
              <ul>
                <li><b>Routine Check-ins:</b> Morning Rest BP/SpO2, 11:00 ARED Bone Loading (45 min), Hydration/Glucose Sync, Dosimeter Sync, Evening Circadian Dimming.</li>
                <li><b>Milestones &amp; Badges:</b> <i>ARED Iron Spine</i>, <i>ALARA Shield Steward</i>, <i>Circadian Guardian</i>.</li>
                <li><b>Interactive Micro-Quiz:</b> Builds non-medical crew autonomy across orbital and surface emergencies.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>WerreduR Zenodo Archive DOI: 10.5281/zenodo.23128224</span><span>astrosoma.space · 5 / 7</span></div>
        </section>"""

        s6 = f"""
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Verified Real NASA Telemetry &amp; Automated Testing</span><span class="pg">6 / 7</span></div>
          <h2>Live NASA OSDR + NOAA SWPC Feeds &amp; Reproducible Verification</h2>
          <div class="grid2">
            <div class="card">
              <h3>Real Flight &amp; Space Weather Endpoints</h3>
              <p><b>NOAA SWPC GOES Live:</b> &ge;10 MeV Proton Flux = <code>{escape(str(sw.get('pfu_10mev', '--')))} pfu</code> ({escape(str(sw.get('noaa_s_scale', 'S0')))}), <b>Kp = {escape(str(sw.get('kp_index', '--')))}</b>.</p>
              <table>
                <tr><th>OSDR ID</th><th>Organism</th><th>Verified NASA OSDR Study</th></tr>
                {study_rows}
              </table>
            </div>
            <div class="card">
              <h3>Empirical Engineering Checks</h3>
              <div class="kpi">6 / 6 Automated Tests Passing</div>
              <ul>
                <li><b>Cross-Runtime Bit-Exact Parity:</b> Python (<code>codec_werr24.py</code>) and JS (<code>werr24_core.js</code>) match byte-for-byte via Node.js CI verification.</li>
                <li><b>Exhaustive 192-Bit SEU Fault Sweep:</b> Every single bit-flip across the 24-byte frame is flagged by <code>CRC-16</code> while neural weight RAM stays at <code>0 Bytes</code>.</li>
                <li><b>Cloudflare Pages Edge Proxy:</b> <code>/api/nasa-osdr</code> resolves browser CORS cleanly with versioned JSON fallback.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>osdr.nasa.gov · services.swpc.noaa.gov</span><span>astrosoma.space · 6 / 7</span></div>
        </section>"""

        s7 = """
        <section class="slide">
          <div class="hdr"><span class="eyebrow">Open-Source Deployment &amp; Next Horizons</span><span class="pg">7 / 7</span></div>
          <h2>Ready for Analog Crews &amp; Deep-Space Validation</h2>
          <div class="grid2">
            <div class="card">
              <h3>Verified Project Links</h3>
              <ul>
                <li><b>Live Console:</b> <code>https://astrosoma.space/</code> (Cloudflare Pages, Full Strict SSL)</li>
                <li><b>GitHub Repository:</b> <code>https://github.com/Lexovian/astrosoma</code> (Apache-2.0)</li>
                <li><b>NASA Space Apps Team:</b> <code>spaceappschallenge.org/2026/find-a-team/astrosoma1/</code></li>
                <li><b>Team Email:</b> <code>info@astrosoma.space</code></li>
              </ul>
            </div>
            <div class="card">
              <h3>Post-Hackathon Roadmap</h3>
              <ul>
                <li><b>Sensor Bridge:</b> Direct WebSerial / microcontroller WERR-24 framing from Arduino &amp; wearable PPG/dosimeter hardware.</li>
                <li><b>OSDR/ALSDA Replay:</b> Streaming historical spaceflight physiology cohorts directly through the clinical guardrail evaluator.</li>
                <li><b>Analog Habitat Trials:</b> Bilingual EN/TR CEIT usability evaluation with non-medical analog crew volunteers.</li>
              </ul>
            </div>
          </div>
          <div class="ftr"><span>Team AstroSoma · Dağhan Dağlı &amp; Dr. Zerrin Dağlı</span><span>NASA Space Apps Challenge 2026</span></div>
        </section>"""
        title = "AstroSoma — NASA Space Apps 2026 Presentation (EN)"

    return f"<!DOCTYPE html><html lang='{lang}'><head><meta charset='utf-8'><title>{title}</title><style>{_slide_css()}</style></head><body>{s1}{s2}{s3}{s4}{s5}{s6}{s7}</body></html>"


def build_all() -> None:
    snap_path = ROOT / "data" / "verified_nasa_telemetry.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))

    demo_dir = ROOT / "demo"
    docs_dir = ROOT / "docs"
    demo_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    en_html = demo_dir / "slides_en.html"
    tr_html = demo_dir / "slides_tr.html"
    en_html.write_text(_build_slides_html("en", snap), encoding="utf-8")
    tr_html.write_text(_build_slides_html("tr", snap), encoding="utf-8")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for html_file, pdf_name in [
            (en_html, "AstroSoma_Presentation_EN.pdf"),
            (tr_html, "AstroSoma_Presentation_TR.pdf"),
        ]:
            page.goto(html_file.as_uri(), wait_until="load")
            page.pdf(
                path=str(docs_dir / pdf_name),
                width="13.333in",
                height="7.5in",
                print_background=True,
                margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"},
            )
            print("Built PDF:", docs_dir / pdf_name)
        browser.close()


if __name__ == "__main__":
    build_all()
