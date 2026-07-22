<div align="center">
<img src="static/img/logo-square.png" width="110" alt="StanNG logo">
<h1>⚡ StanNG</h1>
<p>
  <strong>یک پنل تک‌سرویسهٔ VLESS-over-WebSocket با تم جادوگری</strong><br>
  <strong>A single‑service VLESS‑over‑WebSocket panel with a wizarding theme</strong>
</p>
<p>
  <a href="https://railway.app/new/template"><img src="https://railway.app/button.svg" alt="Deploy on Railway"></a>
  <a href="https://render.com/deploy"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render"></a>
</p>
<img src="docs/screenshots/login.jpg" width="720" alt="StanNG login screen">
</div>

---

## ✨ ویژگی‌ها (Features)

- **بدون دیتابیس خارجی** – همه چیز در یک فایل JSON محلی (`data/db.json`) ذخیره می‌شود.
- **راه‌اندازی یک‌باره** – اولین بازدیدکننده، ادمین را می‌سازد. رمز پیش‌فرض وجود ندارد.
- **مدیریت کاربران پیشرفته** – حجم (GB)، اعتبار (روز)، سقف درخواست، محدودیت اتصال همزمان و قفل IP.
- **تنظیمات پیشرفته کانفیگ** – Fingerprint، ALPN، SNI اختصاصی (Domain Fronting) و پارامترهای Fragment به‌صورت سراسری.
- **لینک اشتراک سازگار با v2rayNG** – خروجی `/sub/{uid}` فقط یک کانفیگ TLS معتبر است.
- **صفحه وضعیت عمومی** – هر کاربر می‌تواند مصرف و وضعیت خود را بدون ورود ببیند.
- **ضد فروش** – با یک کلیک UUID کاربر را عوض کنید تا لینک‌های قبلی باطل شوند.
- **آپدیت خودکار درون‌پنلی** – از داشبورد، بدون از دست دادن کاربران و تنظیمات به‌روزرسانی کنید.
- **دو زبانه (فارسی/انگلیسی) و تم تاریک/روشن** – کاملاً واکنش‌گرا برای موبایل.
- **جلوه‌های صوتی، انیمیشن، دکمه پشتیبانی تلگرام و بیدارباش خودکار** – همه چیز بدون وابستگی خارجی.

---

## 🚀 نصب سریع (Quick Deploy)

### Railway (پیشنهادی)

1. ریپازیتوری را Fork کنید یا به گیت‌هاب خودتان Push کنید.
2. در [Railway](https://railway.app) → **New Project → Deploy from GitHub repo**.
3. بعد از دیپلوی، به `<your-domain>/setup` بروید و نام‌کاربری/رمز عبور بسازید.

> 💡 Railway از IP اختصاصی خودش استفاده می‌کند. در صورت فیلترشدن، حالت Fragment را از پنل (تنظیمات → تنظیمات پیشرفته) و در کلاینت فعال کنید.

### Render

1. Fork / Push به گیت‌هاب.
2. در [Render](https://render.com) → **New → Web Service** و ریپازیتوری را متصل کنید.
3. بعد از دیپلوی به `/setup` بروید.

> 💡 روی Render پشت شبکهٔ Cloudflare هستید، بنابراین کانفیگ‌ها از IPهای تمیز کلودفلر عبور می‌کنند.

### اجرای محلی

```bash
git clone https://github.com/<your-username>/StanNG.git
cd StanNG
pip install -r requirements.txt
python main.py
# → http://localhost:8000/setup
```

---

## 🔑 راه‌اندازی اولیه

- اولین بازدیدکننده به `/setup` هدایت می‌شود و یک نام‌کاربری (۳–۳۲ کاراکتر، حروف/عدد/زیرخط) و رمز عبور (حداقل ۶ کاراکتر) می‌سازد.
- رمز با PBKDF2‑SHA256 (۲۶۰k تکرار) هش می‌شود و در `data/db.json` ذخیره می‌شود.
- پس از آن، فقط با همان اطلاعات وارد پنل می‌شوید.

---

## ⚙️ متغیرهای محیطی (اختیاری)

| متغیر | توضیح | پیش‌فرض |
|---|---|---|
| `PORT` | پورت اجرای سرویس | `8000` |
| `STANNG_DATA_DIR` | مسیر ذخیره‌سازی دیتابیس JSON | `./data` |

---

## 📁 ساختار پروژه (Project Structure)

```
StanNG/
├── main.py                  # FastAPI app (routes, auth, WS, OTA)
├── vless_engine.py          # VLESS parser + relay engine
├── storage.py               # Atomic JSON persistence
├── colo_map.py              # Cloudflare colo → location lookup
├── requirements.txt
├── Procfile / railway.json / render.yaml
├── templates/               # HTML templates (setup, login, dashboard, status, icons)
├── static/                  # CSS, JS, fonts, images, sound effects
└── data/                    # db.json (git‑ignored)
```

---

## 📡 مستندات API (خلاصه)

| دسته | مسیرها |
|---|---|
| **احراز هویت** | `POST /api/login`, `POST /api/logout`, `POST /api/change-password` |
| **کاربران** | `GET/POST /api/inbounds`, `PATCH/DELETE /api/inbounds/{uid}`, `POST /api/inbounds/{uid}/reset-usage`, `POST /api/inbounds/{uid}/regenerate` |
| **لینک‌ها** | `GET /api/inbounds/{uid}/links`, `GET /api/inbounds/{uid}/qr` |
| **اشتراک** | `GET /sub/{uid}` (Base64), `GET /sub/{uid}/json`, `GET /status/{uid}` (صفحه عمومی), `GET /api/status/{uid}` (JSON) |
| **تنظیمات** | `POST /api/settings` |
| **سیستم** | `GET /health`, `GET /stats`, `GET /api/ota/check`, `POST /api/ota/update` |
| **WebSocket** | `WS /ws/{uid}` (نقطه اتصال VLESS) |

---

## 🔒 نکات امنیتی

- رمزها با **PBKDF2‑HMAC‑SHA256** (۲۶۰k تکرار) هش می‌شوند.
- نشست‌ها با کوکی امضاشده (`itsdangerous`) و انقضای ۷ روزه.
- محدودیت تلاش ورود (۶ بار ناموفق = قفل ۵ دقیقه‌ای IP).
- `data/db.json` حاوی اطلاعات حساس است و هرگز نباید commit شود (در `.gitignore` قرار دارد).

---

## 📜 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است. منابع شخص‌ثالث بسته‌بندی‌شده در ریپازیتوری شامل فونت Vazirmatn، Cinzel و MedievalSharp (SIL OFL 1.1)، افکت‌های صوتی از Kenney.nl (CC0) و تصاویر تولیدشده اختصاصی با هوش مصنوعی می‌باشند.

---

<div align="center">
<sub>StanNG یک پروژهٔ مستقل و غیررسمی است و هیچ ارتباطی با هیچ برند یا اثر تجاری‌ای ندارد. تم جادوگری صرفاً الهام‌گرفته از سبک آکادمی تاریک است.</sub>
</div>