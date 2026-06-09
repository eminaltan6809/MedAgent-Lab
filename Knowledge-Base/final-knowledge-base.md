# Med-AgentLab Final Knowledge Base

Bu dosya, Med-AgentLab projesinin mevcut ve GitHub'a aktarılmış final uygulama halini anlatan ana bilgi kaynağıdır. İleride bu projeyle çalışan LLM'ler, eski fikir dosyaları yerine öncelikle bu dosyayı baz almalıdır.

Son güncelleme: 2026-06-09  
Aktif uygulama girişi: `app.py`  
Aktif arayüz: `frontend/index.html`

## 1. Projenin Kısa Tanımı

Med-AgentLab, klinik görüşme metinleri üzerinde nitel analiz yapmayı hedefleyen bir bitirme projesi prototipidir. Sistem; kullanıcıdan dosya alır, metinleri işler, kişisel veri örüntülerini azaltmaya çalışır, temalar çıkarır, PubMed destekli doğrulama yapar ve analiz sonucunu Excel, Markdown ve Word dosyası olarak sunar.

Proje klinik karar destek sistemi değildir. Üretilen sonuçlar akademik/prototip amaçlıdır ve gerçek akademik ya da klinik kullanım öncesinde alan uzmanı tarafından kontrol edilmelidir.

## 2. Mevcut Final Mimari

Final uygulama iki ana parçadan oluşur:

- `app.py`: FastAPI backend, analiz pipeline'ı, ajan sınıfları, model router, dosya işleme ve indirme uç noktaları.
- `frontend/index.html`: Tek sayfalık web arayüzü, dosya yükleme, iş takibi, sonuç gösterimi, model router/gizlilik paneli ve indirme butonları.

Runtime sırasında oluşan dosyalar Git'e dahil edilmez:

- `.env`
- `uploads/`
- `outputs/`
- `*.db`
- `*.log`
- `__pycache__/`
- demo veya hasta-veri benzeri Excel dosyaları

## 3. Backend Özeti

Backend FastAPI ile yazılmıştır ve aktif dosya `app.py` dosyasıdır. Uygulama başlangıcında `.env` dosyası `python-dotenv` ile yüklenir. CORS tüm origin'lere açıktır, çünkü proje yerel geliştirme ve prototip kullanımına göre tasarlanmıştır.

Backend'in temel sorumlulukları:

- Dosya yükleme almak.
- Analiz işini background task olarak başlatmak.
- İş durumunu bellekte ve SQLite veritabanında takip etmek.
- Excel, TXT ve PDF içeriklerini metne dönüştürmek.
- Ajan tabanlı analiz pipeline'ını çalıştırmak.
- Sonuçları Excel, Markdown ve DOCX formatında üretmek.
- Frontend'i `/` endpoint'i üzerinden servis etmek.

SQLite veritabanı dosyası `med_agentlab.db` olarak oluşturulur. Bu dosya runtime çıktısıdır ve Git'e eklenmemelidir.

## 4. API Uç Noktaları

`app.py` içinde mevcut olan endpoint'ler:

| Endpoint | Metot | Amaç |
| --- | --- | --- |
| `/upload` | POST | Dosya yükler ve analiz işini başlatır. |
| `/jobs` | GET | Geçmiş işleri listeler. |
| `/status/{job_id}` | GET | Analiz durumunu, ilerlemeyi, logları ve router bilgilerini döndürür. |
| `/results/{job_id}` | GET | Tamamlanan işin analiz sonuçlarını döndürür. |
| `/download/{job_id}` | GET | Excel çıktısını indirir. |
| `/download/report/{job_id}` | GET | Markdown rapor çıktısını indirir. |
| `/download/report/docx/{job_id}` | GET | Word rapor çıktısını indirir. |
| `/cancel/{job_id}` | POST | Devam eden işi iptal eder. |
| `/health` | GET | Basit sağlık kontrolü döndürür. |
| `/` | GET | Frontend HTML dosyasını servis eder. |

## 5. Analiz Pipeline'ı

Pipeline sınıfı `QualitativeAnalysisPipeline` olarak tanımlıdır. Tekil metin işleme akışı `process_single_text` metodunda gerçekleşir.

Temel akış:

1. Girdi metni alınır.
2. Agent A ile gizlilik/ön işleme yapılır.
3. Agent B ile tema çıkarımı yapılır.
4. Agent C ile PubMed destekli doğrulama yapılır.
5. Agent D ile tüm sonuçlardan akademik rapor sentezi yapılır.
6. Çıktılar Excel, Markdown ve gerektiğinde DOCX olarak sunulur.

Uzun TXT/PDF içeriklerinde metin `chunk_text_sliding_window` fonksiyonu ile parçalanır. Varsayılan parça boyutu 2250 kelime, örtüşme 340 kelimedir.

Excel yüklemede backend dosyayı pandas ile okur. Kodda öncelikli metin kolonu `text_data` olarak beklenir.

## 6. Ajanlar

### Agent A - Privacy Scrubber

Kod sınıfı: `AgentA_PrivacyScrubber`

Görevi:

- Metni analizden önce gizlilik açısından hafifletmek.
- Ollama üzerinde tanımlı yerel modelle kişisel veri temizliği denemek.
- Ollama çağrısı başarısız olursa `PatternGuard` fallback mekanizmasını kullanmak.

Varsayılan model:

- `OLLAMA_MODEL`, yoksa `ollama/qwen3:4b`

Önemli sınırlama:

- Regex tabanlı fallback yalnızca belirli örüntülere odaklanır: TC kimlik numarası, telefon ve e-posta. Bu, tam kapsamlı anonimleştirme garantisi değildir.

### Agent B - Thematic Mapper

Kod sınıfı: `AgentB_ThematicMapper`

Görevi:

- Gizlilikten geçirilmiş metinden ana tema ve alt temalar çıkarmak.
- Model router havuzundan uygun modeli sırayla denemek.
- Model çağrıları başarısız olursa yerel anahtar kelime tabanlı fallback tema çıkarımı yapmak.

Kullandığı router görevi:

- `theme`

### Agent C - PubMed Validator

Kod sınıfı: `AgentC_PubMedValidator`

Görevi:

- Çıkarılan temaları PubMed üzerinden bulunan literatür başlıklarıyla karşılaştırmak.
- PubMed ESearch/ESummary çağrıları ile başlık listesi üretmek.
- Model router üzerinden doğrulama açıklaması oluşturmak.
- Ağ, kota veya model hatalarında heuristic fallback kullanmak.

Kullandığı router görevi:

- `validation`

Önemli sınırlama:

- PubMed entegrasyonu literatür bağlamı sağlar; klinik doğruluk garantisi vermez.

### Agent D - Academic Reducer

Kod sınıfı: `AgentD_AcademicReducer`

Görevi:

- Tekil analiz sonuçlarını birleştirerek Markdown formatında akademik rapor üretmek.
- Model router üzerinden rapor sentezi yapmak.
- Model çağrısı başarısız olursa deterministik fallback rapor üretmek.

Kullandığı router görevi:

- `reduction`

## 7. Model Router ve Fallback Mantığı

Model router `get_model_pool` ve `call_model_pool` fonksiyonlarıyla uygulanır. Amaç, tek bir dış modele bağımlı kalmadan görev bazlı model havuzu kullanmaktır.

Desteklenen görev havuzları:

- `THEME_MODEL_POOL`
- `VALIDATION_MODEL_POOL`
- `REDUCTION_MODEL_POOL`

Bu değişkenler `.env` içinde virgülle ayrılmış model listesi olarak verilebilir. Boş bırakılırsa kod varsayılan model sırasını kullanır.

Varsayılan model değişkenleri:

- `GROQ_MODEL`
- `GEMINI_FAST_MODEL`
- `GEMINI_LITE_MODEL`
- `AGENT_C_MODEL`
- `AGENT_D_MODEL`

Router olayları `record_router_event` ile job içine eklenir. Frontend'deki "Router & Gizlilik" paneli bu olayları gösterir.

Önemli mevcut durum:

- Router olayları job runtime verisine eklenir.
- SQLite şemasında router olayları için ayrı kalıcı kolon yoktur. Bu yüzden geçmiş işlerde router olaylarının kalıcılığı sınırlıdır.

## 8. Ollama Kullanımı

Ollama, projede hafif ve yerel gizlilik/ön işleme ajanı olarak kullanılır.

İlgili fonksiyonlar:

- `get_ollama_base_url`
- `get_ollama_model_name`
- `is_ollama_api_ready`
- `list_ollama_models`
- `ensure_ollama_service_sync`
- `ensure_ollama_service`

Analiz işi başlarken `run_pipeline_job` içinde `ensure_ollama_service(job_id)` çağrılır. Bu, analiz başlamadan önce Ollama servisinin hazır olup olmadığını kontrol eder ve uygun ortamda başlatmayı dener.

Varsayılan ayarlar:

- `OLLAMA_API_BASE=http://127.0.0.1:11434`
- `OLLAMA_MODEL=ollama/qwen3:4b`

Ollama'nın görevi ağır muhakeme değildir. Ağır tema çıkarımı, literatür doğrulama ve rapor sentezi model router havuzundaki dış modellerle yapılır.

## 9. Dosya Girdileri ve Çıktıları

Backend tarafında desteklenen girdi tipleri:

- Excel: `.xlsx`, `.xls`
- TXT
- PDF

Frontend arayüzünde yükleme metni Excel dosyalarına odaklanır. Kodun backend tarafı TXT/PDF işleyebilir, fakat mevcut kullanıcı deneyimi Excel ağırlıklı tasarlanmıştır.

Üretilen çıktılar:

- Excel analiz sonucu
- Markdown rapor
- DOCX rapor

Runtime çıktı klasörü:

- `outputs/`

Yüklenen dosyalar:

- `uploads/`

Bu klasörler GitHub'a gönderilmez.

## 10. Frontend Özeti

Frontend tek dosyadır:

- `frontend/index.html`

API adresi sabit olarak şu şekilde tanımlıdır:

- `const API = 'http://localhost:8000';`

Frontend özellikleri:

- Excel dosyası seçme ve analiz başlatma.
- İş geçmişi görüntüleme.
- Analiz durumunu polling ile takip etme.
- Devam eden işi iptal etme.
- Sonuçları tablo/rapor/grafik sekmelerinde gösterme.
- Chart.js ile tema grafiği üretme.
- Router & Gizlilik panelinde model denemelerini, fallback durumlarını ve PII redaction sayısını gösterme.
- Excel, Markdown ve Word çıktısı indirme.

Not:

- Arayüzde görünen ana yükleme akışı Excel odaklıdır.

## 11. Ortam Değişkenleri

Güvenli örnek dosya:

- `.env.example`

Gerçek anahtarlar `.env` içinde tutulmalıdır ve Git'e eklenmemelidir.

Beklenen/opsiyonel değişkenler:

| Değişken | Amaç |
| --- | --- |
| `GROQ_API_KEY` | Groq model çağrıları için API anahtarı. |
| `GEMINI_API_KEY` | Gemini model çağrıları için API anahtarı. |
| `OLLAMA_API_BASE` | Yerel Ollama API adresi. |
| `OLLAMA_MODEL` | Agent A için kullanılacak Ollama modeli. |
| `GROQ_MODEL` | Varsayılan Groq modeli. |
| `GEMINI_FAST_MODEL` | Varsayılan hızlı Gemini modeli. |
| `GEMINI_LITE_MODEL` | Varsayılan hafif Gemini modeli. |
| `THEME_MODEL_POOL` | Tema çıkarımı için opsiyonel model havuzu. |
| `VALIDATION_MODEL_POOL` | Doğrulama için opsiyonel model havuzu. |
| `REDUCTION_MODEL_POOL` | Rapor sentezi için opsiyonel model havuzu. |
| `AGENT_C_MODEL` | Agent C için opsiyonel model override. |
| `AGENT_D_MODEL` | Agent D için opsiyonel model override. |

## 12. Kurulum ve Çalıştırma

Bağımlılık kurulumu:

```bash
pip install -r requirements.txt
```

`.env` oluşturma:

```bash
cp .env.example .env
```

Ollama modelini hazırlama:

```bash
ollama pull qwen3:4b
```

Backend'i çalıştırma:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Arayüz:

```text
http://127.0.0.1:8000
```

Sağlık kontrolü:

```text
http://127.0.0.1:8000/health
```

## 13. GitHub'a Dahil Edilen Ana Dosyalar

Final repo için anlamlı kaynak dosyalar:

- `app.py`
- `frontend/index.html`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md`
- `create_demo_data.py`
- `main.py`
- `Knowledge-Base/`
- `tools/build_final_report.py`

`main.py`, eski pipeline yaklaşımını içeren referans dosyasıdır. Aktif servis hedefi `app.py` olmalıdır.

## 14. Bilinen Sınırlamalar

Bu sınırlamalar kodun mevcut halinden çıkarılmıştır:

- Sistem klinik karar destek sistemi değildir.
- Regex fallback tam anonimleştirme sağlamaz; yalnızca belirli PII örüntülerini yakalar.
- Frontend yükleme deneyimi Excel odaklıdır.
- Backend TXT/PDF desteklese de arayüz mesajları Excel kullanımını merkeze alır.
- PubMed erişimi ağ, SSL, API yanıtı veya kota durumlarından etkilenebilir.
- Ücretsiz API modellerinde kota dolması mümkündür; router havuzu bu riski azaltır ama tamamen ortadan kaldırmaz.
- Router olayları runtime job verisinde tutulur; SQLite tarafında özel kalıcı router event şeması yoktur.
- Model çıktıları deterministik değildir ve akademik raporlar insan kontrolü gerektirir.
- Demo veri üretim script'i vardır, fakat gerçek hasta verisi repo'ya dahil edilmemelidir.

## 15. İleride LLM'ler İçin Çalışma Kuralları

Bu projeyle çalışan bir LLM aşağıdaki kurallara uymalıdır:

1. Aktif backend olarak `app.py` dosyasını baz al.
2. Aktif frontend olarak `frontend/index.html` dosyasını baz al.
3. Eski `Knowledge-Base` dosyalarındaki iddiaları final gerçeklik sayma; önce bu dosyayı ve kodu kontrol et.
4. Hasta verisi, upload çıktısı, analiz çıktısı, `.env`, DB ve log dosyalarını rapora veya commit'e dahil etme.
5. Özellik anlatırken kodda karşılığı olmayan fonksiyon veya davranış uydurma.
6. Ollama'yı yerel ve hafif gizlilik/ön işleme ajanı olarak konumlandır.
7. Ağır görevleri model router havuzundaki dış modellerin yürüttüğünü belirt.
8. Fallback mekanizmalarını "garanti" gibi anlatma; bunlar hata/kota durumunda çalışmayı sürdüren destek mekanizmalarıdır.
9. PubMed destekli doğrulamayı klinik doğrulama olarak değil, literatür bağlamı olarak tanımla.
10. Yeni özellik eklenirse bu dosyayı aynı commit içinde güncelle.

## 16. Kısa Final Tanım

Med-AgentLab'ın final hali; FastAPI backend, tek sayfa frontend, Ollama destekli yerel gizlilik ajanı, dış model havuzlu tema/doğrulama/rapor ajanları, PubMed literatür bağlamı, background job takibi ve çok formatlı çıktı üretimi bulunan bir nitel analiz prototipidir.
