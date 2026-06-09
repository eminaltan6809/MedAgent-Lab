#!/usr/bin/env python3
"""
Med-AgentLab Demo Veri Oluşturucu
Projenin 5 aşamalı pipeline'ını test etmek için gerçekçi Türkçe klinik görüşme verileri üretir.
Üretilen Excel dosyası, uygulamaya yüklenip analiz edilebilir.
"""

import pandas as pd

# Gerçekçi Türkçe klinik görüşme verileri
# Her biri farklı hasta senaryolarını temsil eder
sample_interviews = [
    # Hasta 1 - Kronik ağrı ve depresyon
    (
        "Görüşme yapılan hasta Ahmet Yılmaz, 45 yaşında erkek, TC Kimlik No: 12345678901. "
        "Hasta son 6 aydır kronik bel ağrısından şikayetçi. Ağrı özellikle sabah saatlerinde artıyor "
        "ve günlük aktivitelerini ciddi şekilde kısıtlıyor. Hasta ifadesine göre: 'Sabahları yataktan "
        "kalkmak bile çok zor, ağrı dayanılmaz hale geliyor. İş yerimde performansım düştü, patronum "
        "sürekli uyarıyor.' Hasta ayrıca uyku bozukluğu ve iştahsızlık bildiriyor. Son 3 aydır "
        "antidepresan kullanmaya başlamış (Sertralin 50mg/gün). Hastanın e-posta adresi "
        "ahmet.yilmaz@email.com olup kendisine ulaşılabilir. Telefon: 05321234567. "
        "Muayenede lomber bölgede hassasiyet saptandı. Beck Depresyon Ölçeği skoru 24 (orta düzey depresyon). "
        "Hasta daha önce fizik tedavi almış ancak yeterli fayda görmediğini belirtiyor."
    ),

    # Hasta 2 - Anksiyete ve panik atak
    (
        "Hasta Fatma Demir, 32 yaş, kadın. İletişim: fatma.demir@gmail.com, Tel: 05559876543. "
        "Son 1 yıldır tekrarlayan panik atak atakları yaşıyor. Ataklar genellikle kalabalık ortamlarda "
        "tetikleniyor. Hasta şöyle anlatıyor: 'Kalbim çok hızlı çarpıyor, nefes alamıyorum, ölecekmiş "
        "gibi hissediyorum. AVM'ye gidemez oldum, toplu taşıma kullanamıyorum.' Agorafobi belirtileri "
        "mevcut. Hamilton Anksiyete Ölçeği skoru 28 (şiddetli anksiyete). Hasta bilişsel davranışçı "
        "terapi almaya başlamış, 4. seansta. Alprazolam 0.5mg kullanıyor gerektiğinde. "
        "Hastanın annesi de anksiyete bozukluğu tanısı almış, genetik yatkınlık düşünülüyor. "
        "Uyku kalitesi düşük, sık kabus görme şikayeti var. Sosyal izolasyon belirgin."
    ),

    # Hasta 3 - Onkoloji hastası - Psikolojik etkileri
    (
        "Hasta Mehmet Kaya, 58 yaş, erkek, TC: 98765432109. Akciğer kanseri tanısı almış, "
        "Evre IIIB. 3 kür kemoterapi tamamlanmış. Hasta bulantı, yorgunluk ve ağız yaralarından "
        "şikayetçi. Psikolojik değerlendirmede: 'Artık yaşamak istemiyorum bazen, ailem için "
        "dayanıyorum. Çocuklarım küçük, onları büyütemeyeceğim diye çok korkuyorum.' "
        "Uyku bozukluğu, konsantrasyon güçlüğü, ağlama nöbetleri mevcut. Eşi ile ilişkisinde "
        "gerginlik artmış. Hasta onkoloji psikoloğuna yönlendirildi. İntihar düşüncesi sorgulandı, "
        "aktif plan yok ancak pasif ölüm düşünceleri mevcut. HADS-D skoru: 15 (klinik depresyon). "
        "Kemoterapinin yan etkileri (nöropati, iştahsızlık, kilo kaybı) hastanın yaşam kalitesini "
        "ciddi şekilde düşürmekte. Palyatif bakım ekibi ile konsültasyon planlandı."
    ),

    # Hasta 4 - Çocuk/Ergen DEHB
    (
        "Hasta Ece Şahin, 11 yaş, kız. Annesi Ayşe Şahin (Tel: 05441112233) tarafından getirildi. "
        "Okul başarısında belirgin düşüş, öğretmen geri bildirimi: 'Derste sürekli dalgın, "
        "yerinde duramıyor, arkadaşlarıyla kavga ediyor.' Conners Ebeveyn Değerlendirme Ölçeği "
        "dikkat eksikliği alt ölçeği T skoru: 72 (klinik düzey). Hiperaktivite-impulsivite T skoru: 68. "
        "Hasta ile görüşmede: 'Ders çok sıkıcı, arkadaşlarım beni sevmiyor, hep benim suçum gibi "
        "davranıyorlar.' Özgüven düşüklüğü, sosyal ilişkilerde zorluk belirgin. "
        "Ailede DEHB öyküsü mevcut (baba tanılı). Uyku düzeni bozuk, gece geç saatlere kadar "
        "tablet kullanıyor. Beslenme düzensiz, kahvaltı yapmıyor. Davranışçı müdahale ve "
        "psikoeğitim programı planlandı. Metilfenidat başlanması değerlendiriliyor."
    ),

    # Hasta 5 - Travma Sonrası Stres Bozukluğu (TSSB)
    (
        "Hasta Ali Özkan, 29 yaş, erkek. Adres: Kadıköy, İstanbul. 6 ay önce ciddi bir trafik "
        "kazası geçirmiş. O zamandan beri flashback'ler, kabuslar ve aşırı irkilme tepkisi var. "
        "Hasta anlatıyor: 'Araç kornası duyunca donakalıyorum, kaza anı gözümün önüne geliyor. "
        "Gece ter içinde uyanıyorum. Araba kullanamıyorum, işe bile gidemez oldum.' "
        "PCL-5 toplam skoru: 52 (TSSB tanı eşiği üzerinde). Kaçınma davranışları belirgin: "
        "araç kullanmıyor, otoyoldan geçen yollarda yürümüyor. Duygusal küntleşme mevcut. "
        "Alkol tüketimi artmış (günde 3-4 bira). İş kaybı nedeniyle maddi sıkıntı yaşıyor. "
        "EMDR terapisi planlandı. Prazosin 1mg gece başlandı kabus tedavisi için. "
        "Komorbid alkol kötüye kullanımı açısından takip önerildi."
    ),

    # Hasta 6 - Geriatrik hasta - Demans ve bakıcı tükenmişliği
    (
        "Hasta Hatice Arslan, 78 yaş, kadın. Kızı Zeynep Arslan (zeynep.arslan@hotmail.com) "
        "tarafından getirildi. Son 2 yıldır ilerleyici unutkanlık, zaman ve yer dezoryantasyonu. "
        "Mini Mental Durum Değerlendirmesi (MMSE) skoru: 18/30. Alzheimer tipi demans düşünülüyor. "
        "Kızı ifade ediyor: 'Annem ocağı açık bırakıyor, evden çıkıp kayboldu bir kez. "
        "Beni tanımadığı anlar oluyor, çok zor. Ben de tükenmişlik hissediyorum, uyuyamıyorum.' "
        "Bakıcı tükenmişlik ölçeği: yüksek düzey. Hasta agresif davranışlar sergileyebiliyor, "
        "özellikle banyo yaptırma sırasında. Donepezil 10mg kullanıyor. "
        "Gündüz bakım merkezi ve bakıcı destek grubu önerildi. "
        "Hastanın vasküler risk faktörleri: hipertansiyon, diyabet tip 2, hiperlipidemi."
    ),

    # Hasta 7 - Yeme bozukluğu
    (
        "Hasta Selin Aydın, 19 yaş, üniversite öğrencisi, kadın. Anoreksiya nervoza tanısı ile "
        "takipte. Son 4 ayda 8 kg kaybetmiş, şu anki BMI: 16.2 (düşük ağırlıklı). "
        "Hasta: 'Yemek yediğimde kendimi çok suçlu hissediyorum, aynada hala şişman görüyorum. "
        "Spor yapmadan duramıyorum, günde 3 saat koşuyorum.' Amenore 3 aydır mevcut. "
        "Laboratuvar bulguları: düşük potasyum (3.1 mEq/L), düşük albumin, düşük demir. "
        "EAT-26 skoru: 38 (yüksek risk). Aile ilişkileri gergin, anne aşırı kontrollü. "
        "Kusma davranışı sorgulandı, hasta reddediyor ancak diş erozyonu ve parotis şişliği "
        "mevcut. Yatarak tedavi endikasyonu değerlendiriliyor. Beslenme uzmanı ve psikiyatri "
        "işbirliği ile takip planlandı. Fluoksetin 20mg başlanması düşünülüyor."
    ),

    # Hasta 8 - Madde bağımlılığı
    (
        "Hasta Burak Çetin, 34 yaş, erkek. Alkol ve benzodiazepin bağımlılığı. Son 5 yıldır "
        "düzenli alkol kullanımı, günde yaklaşık 1 litre rakı. 2 kez detoks programına alınmış "
        "ancak nüks etmiş. Hasta: 'İçmeden uyuyamıyorum, ellerim titriyor, terliyorum. "
        "Eşim beni terk etti, çocuğumu göremiyorum. Her şeyi kaybettim ama bırakamıyorum.' "
        "AUDIT skoru: 32 (ağır alkol kullanım bozukluğu). Karaciğer fonksiyon testleri yüksek "
        "(AST: 89, ALT: 102, GGT: 245). Hepatomegali saptandı. Yoksunluk belirtileri mevcut: "
        "tremor, terleme, anksiyete, insomnia. Delirium tremens riski değerlendirildi. "
        "Yatarak detoksifikasyon programına alındı. Diazepam azaltma protokolü başlandı. "
        "AA toplantılarına katılım ve bireysel psikoterapi planlandı."
    ),

    # Hasta 9 - Bipolar bozukluk
    (
        "Hasta Deniz Koç, 27 yaş, erkek. Bipolar Bozukluk Tip I tanısı, 3. manik epizod. "
        "Ailesi tarafından acile getirilmiş. Son 1 haftadır uyumamış, aşırı enerjik, "
        "grandiöz düşünceler mevcut. Hasta: 'Ben özel biriyim, büyük bir proje üzerinde "
        "çalışıyorum, uyumaya vaktim yok. Milyonlarca dolar kazanacağım.' "
        "Konuşma hızı artmış, düşünce uçuşması var. Kredi kartından 50.000 TL harcama yapmış. "
        "İş yerinde uygunsuz davranışlar nedeniyle işten çıkarılma riski. "
        "Young Mani Değerlendirme Ölçeği skoru: 38. Lityum kan düzeyi: 0.3 mEq/L (subterapötik, "
        "ilaç uyumsuzluğu). Lityum dozu artırıldı, Olanzapin 10mg eklendi. "
        "Yatış önerildi ancak hasta reddediyor. Aile psikoeğitimi ve yakın takip planlandı."
    ),

    # Hasta 10 - Kronik yorgunluk ve fibromiyalji
    (
        "Hasta Elif Güneş, 41 yaş, kadın. Fibromiyalji ve kronik yorgunluk sendromu tanıları. "
        "Son 3 yıldır yaygın vücut ağrısı, kronik yorgunluk ve bilişsel bulanıklık şikayetleri. "
        "Hasta: 'Her yerim ağrıyor, sabah kalktığımda bile yorgunum. İsimleri unutuyorum, "
        "işe konsantre olamıyorum. Doktorlar bir şey bulamıyor, kafamda mı diyorlar?' "
        "Fibromiyalji Etki Anketi skoru: 72 (ağır etkilenme). Tender point muayenesi: 14/18. "
        "Uyku çalışması: alfa-delta uyku paterni saptanmış. Komorbid irritabl bağırsak sendromu "
        "ve temporomandibuler eklem disfonksiyonu mevcut. Duloksetin 60mg, Pregabalin 150mg "
        "kullanıyor. Egzersiz programı önerildi ancak ağrı nedeniyle uyum düşük. "
        "Multidisipliner ağrı yönetimi programına yönlendirildi. Mindfulness temelli stres "
        "azaltma programı başlatıldı."
    ),
]

# DataFrame oluştur - app.py'deki pipeline 'text_data' sütununu bekliyor
df = pd.DataFrame({
    "text_data": sample_interviews
})

# Excel dosyasını kaydet
output_path = "demo_klinik_gorusmeler.xlsx"
df.to_excel(output_path, index=False, engine="openpyxl")
print(f"[OK] Demo Excel dosyasi olusturuldu: {output_path}")
print(f"   -> {len(sample_interviews)} klinik gorusme kaydi")
print(f"   -> Sutun: 'text_data' (pipeline'in bekledigi format)")
print(f"   -> Icerik: PII bilgileri (isim, TC, tel, e-posta), klinik bulgular, olcek sonuclari")
print(f"\nHasta senaryolari:")
senaryolar = [
    "Kronik ağrı + Depresyon",
    "Panik atak + Agorafobi",
    "Onkoloji + Psikolojik etki",
    "Çocuk DEHB",
    "Travma Sonrası Stres (TSSB)",
    "Geriatrik Demans + Bakıcı tükenmişliği",
    "Anoreksiya Nervoza",
    "Alkol/Madde bağımlılığı",
    "Bipolar Bozukluk (Manik epizod)",
    "Fibromiyalji + Kronik yorgunluk"
]
for i, s in enumerate(senaryolar, 1):
    print(f"   {i}. {s}")
