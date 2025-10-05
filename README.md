# BUDUN Sigorta Web Sitesi

Modern, responsive ve mobil uyumlu sigorta poliçe takip web uygulaması.

## 🚀 Özellikler

- **Modern UI/UX**: Bootstrap 5 ile şık ve kullanıcı dostu arayüz
- **Mobil Uyumlu**: Tüm cihazlarda mükemmel görünüm
- **Responsive Design**: Tablet ve telefon optimizasyonu
- **Multi-tenant**: Şirket bazlı veri izolasyonu
- **Gerçek Zamanlı**: Supabase ile canlı veri
- **Güvenli**: HTTPS ve session tabanlı kimlik doğrulama

## 🛠️ Teknoloji Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: Supabase (PostgreSQL)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Deployment**: Vercel

## 📁 Proje Yapısı

```
BUDUNWEBSITE/
├── app.py                 # Flask ana uygulama
├── requirements.txt       # Python bağımlılıkları
├── vercel.json           # Vercel konfigürasyonu
├── templates/            # HTML şablonları
│   ├── base.html        # Ana şablon
│   ├── login.html       # Giriş sayfası
│   ├── dashboard.html   # Ana panel
│   └── policies.html    # Poliçe yönetimi
├── static/              # Statik dosyalar
│   ├── css/
│   │   └── style.css   # Custom CSS
│   └── js/
│       └── app.js      # JavaScript fonksiyonları
└── README.md           # Bu dosya
```

## 🔧 Kurulum

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
export SECRET_KEY="your-secret-key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-key"
```

### 3. Çalıştır
```bash
python app.py
```

## 🌐 Vercel Deployment

### 1. GitHub'a Push
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Vercel'e Bağla
1. [Vercel](https://vercel.com) hesabına giriş yap
2. "Import Project" butonuna tıkla
3. GitHub repository'ni seç
4. Environment variables'ları ekle:
   - `SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### 3. Deploy
Vercel otomatik olarak deploy edecek!

## 📱 Sayfalar

### 🏠 Ana Sayfa (/)
- Giriş yapmış kullanıcıları dashboard'a yönlendirir
- Giriş yapmamış kullanıcıları login sayfasına yönlendirir

### 🔐 Giriş (/login)
- Kullanıcı kimlik doğrulama
- Session yönetimi
- Hata mesajları

### 📊 Dashboard (/dashboard)
- İstatistik kartları (toplam poliçe, aktif, süresi dolacak)
- Hızlı işlemler
- Son poliçeler tablosu
- Şirket bazlı veri filtreleme

### 📋 Poliçeler (/policies)
- Poliçe listesi (tablo görünümü)
- Arama ve filtreleme
- Yeni poliçe ekleme (modal)
- Poliçe görüntüleme/düzenleme

## 🔌 API Endpoints

### GET /api/policies
Poliçeleri getir (şirket bazlı filtreleme)

### POST /api/policies
Yeni poliçe ekle

### GET /api/companies
Şirketler listesi

### GET /api/salespeople
Satışçılar listesi (şirket bazlı filtreleme)

## 🎨 Tasarım Özellikleri

### Responsive Design
- **Desktop**: Tam özellikli arayüz
- **Tablet**: Optimize edilmiş layout
- **Mobile**: Touch-friendly arayüz

### Modern UI Elements
- Gradient kartlar
- Hover efektleri
- Smooth animasyonlar
- Shadow efektleri
- Rounded corners

### Color Scheme
- **Primary**: Bootstrap Blue (#0d6efd)
- **Success**: Green (#198754)
- **Warning**: Yellow (#ffc107)
- **Info**: Light Blue (#0dcaf0)

## 🔒 Güvenlik

- Session tabanlı kimlik doğrulama
- CSRF koruması
- XSS koruması
- HTTPS zorunlu (production)
- Şirket bazlı veri izolasyonu

## 📊 Veritabanı

### Supabase Tables
- `users`: Kullanıcılar
- `companies`: Şirketler
- `policies`: Poliçeler
- `salespeople`: Satışçılar
- `user_permissions`: Kullanıcı yetkileri

### Row Level Security (RLS)
- Kullanıcılar sadece kendi şirketlerinin verilerini görebilir
- Admin kullanıcıları tüm verileri görebilir

## 🚀 Gelecek Özellikler

- [ ] Poliçe düzenleme
- [ ] Poliçe silme
- [ ] Excel export
- [ ] PDF raporlar
- [ ] Email bildirimleri
- [ ] Gelişmiş filtreleme
- [ ] Bulk operations

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. GitHub Issues kullanın
2. Email: support@budun.com
3. Dokümantasyonu kontrol edin

## 📄 Lisans

Bu proje özel lisans altındadır. Tüm hakları saklıdır.

---

**BUDUN Sigorta** - Modern Sigorta Yönetim Sistemi 🛡️
