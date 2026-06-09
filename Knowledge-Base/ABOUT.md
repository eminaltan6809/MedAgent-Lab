\# Dağıtık Yapay Zeka Ajanları İçin Maliyet-Etkin MapReduce Orkestrasyon Altyapısı; Med-AgentLab (Tıp Dikeyinde Otonom Nitel Veri Analizi)



\# 1. Vizyon ve Proje Özeti

İsmim Emin ALTAN, 4.sınıf yazılım mühendisliği öğrencisiyim. Bitirme projesi kapsamında yapmayı hedeflediğim projenin temeli, vizyon ve misyonu bu dosyada belirtilmiştir.

Tıbbi araştırmalarda nitel veri analizi (hasta mülakatları, açık uçlu anketler, doktor notları), günümüzde MAXQDA gibi lisans ücretleri on binlerce lirayı bulan, geleneksel ve manuel yazılımlarla yapılmaktadır. Bir tıp akademisyeninin yüzlerce sayfalık mülakatı okuyup "kodlaması" (tematik analiz) aylar sürmektedir. 



Med-AgentLab, bu hantal ve pahalı süreci otonom bir "Yapay Zeka Laboratuvarı"na dönüştüren açık kaynaklı bir framework'tür. Büyük Dil Modellerini (LLM) tek bir sohbet botu olarak kullanmak yerine; MapReduce (Parçala ve Birleştir) mimarisiyle veriyi küçük parçalara böler ve her biri farklı zeka seviyesine/göreve sahip ajanlardan oluşan bir filoya asenkron olarak dağıtır.



\# 2. Çözülen Temel Problemler

1\. Zaman ve Maliyet Darboğazı: Aylar süren nitel kodlama sürecini (coding) dakikalara indirir.

2\. Context Window (Bağlam Penceresi) Sınırı: Devasa veriler tek bir LLM'e verildiğinde halüsinasyon başlar ve sistem çöker. MapReduce mimarisi veriyi (chunks) mantıksal parçalara bölerek LLM'lerin sadece odaklanması gereken alana bakmasını sağlar.

3\. Veri Gizliliği (KVKK/HIPAA): Tıbbi verilerin buluta gönderilmeden önce yerel (local) modellerle anonimleştirilmesini sağlayarak %100 gizlilik uyumluluğu sunar.



\# 3. Heterojen "Multi-Agent" Mimarisi

Proje, tek bir modele (örn. sadece Groq) bağımlı değildir. `LiteLLM` kullanılarak farklı görevler, o görevde en iyi/en ucuz olan modellere yönlendirilir:

\*  Gizlilik Bekçisi Ajanı (Ollama - Yerel): İnternete çıkmadan hasta PII (Kişisel Tanımlanabilir Bilgi) verilerini sansürler.

\*  Mapper Ajanlar (Groq - Llama-3): Devasa donanım gücüyle (LPU) bulutta saniyeler içinde binlerce kelimeyi okuyup ham temaları çıkarır.

\*  Medikal Teyit Ajanı (Gemini 1.5 Flash): Çıkarılan ham temaları tıp literatürüyle karşılaştırır, AI halüsinasyonlarını engeller.

\*  Master Reducer (OpenAI GPT-4o-mini / DeepSeek): Doğrulanmış verileri alıp, tek sayfalık, akademik formatta nihai araştırma özetini yazar.



\# 4. Kullanılan Teknolojiler ve Altyapı

\- Orkestrasyon \& Asenkronite: Python `asyncio` (Eşzamanlı 20+ ajan yönetimi)

\- Model Yönlendirme (Routing): `LiteLLM` (Standartlaştırılmış API çağrıları)

\- Hata Toleransı (Resilience): `Tenacity` kütüphanesi ile "Exponential Backoff". API Rate Limit (Hız Sınırı) aşımlarında sistemin çökmesini engeller.

\- Observability (İzlenebilirlik): `Streamlit`. Kullanıcı, ajanların arka plandaki çalışmalarını siyah bir terminalde değil, modern bir UI/UX arayüzünde canlı ilerleme çubuklarıyla (progress bar) izler.



\# 5. Neden Ben? (Kurucu Notu)  

Sınırlı donanım kaynaklarına (4GB VRAM) sahip bir mühendislik öğrencisi olarak, büyük AI modellerini tek bir makinede çalıştırmanın imkansızlığını fark ettim. Bu "kısıt", beni sistemi asenkron olarak buluta dağıtmaya, maliyet optimizasyonuna ve API darboğazlarını çözmeye itti. Bu proje, "Zeka pahalı donanımlarda değil, akıllı mimarilerdedir" felsefesinin (DeepSeek Moment) bir kanıtıdır.



\# 6. SDLC Fazı ve Mevcut Durum

Proje şu anda Planlama, Empati ve Dizayn aşamasındadır. "Önce insan-bilgisayar etkileşimi" prensibi gereği, hedef kitlemiz olan tıp akademisyenlerinin deneyimi tasarlanmaktadır. Prototip (Wireframe) onayı alınmadan kodlamaya (Implementation) geçilmeyecektir.



