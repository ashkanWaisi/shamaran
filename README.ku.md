<div dir="rtl">

<p align="center">
  <img src="docs/assets/shamaran-lockup.png" alt="نیشانی فەرمی شاماران" width="500">
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.fa.md">فارسی</a> · <a href="README.ku.md">کوردی (سۆرانی)</a>
</p>

<p align="center">
  <a href="https://github.com/ashkanWaisi/shamaran/actions/workflows/tests.yml"><img alt="تاقیکردنەوەکان" src="https://github.com/ashkanWaisi/shamaran/actions/workflows/tests.yml/badge.svg"></a>
  <a href="https://github.com/ashkanWaisi/shamaran/releases"><img alt="وەشان" src="https://img.shields.io/github/v/release/ashkanWaisi/shamaran?display_name=tag&sort=semver"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB">
  <img alt="Local first" src="https://img.shields.io/badge/local--first-yes-169B62">
  <img alt="Ollama" src="https://img.shields.io/badge/provider-Ollama-111111">
  <a href="LICENSE"><img alt="مۆڵەتی MIT" src="https://img.shields.io/badge/license-MIT-4C72B0"></a>
</p>

<h3 align="center">ئەجێنتێکی زیرەکی دەستکردی پارێزراو و ناوخۆیی بۆ کاری ڕاستەقینە لەسەر کۆمپیوتەر</h3>

<p align="center">بیر بکەرەوە · دروست بکە · لەبیرت بێت · کردار بکە</p>

---

## ناساندن

شاماران ئەجێنتێکی زیرەکی دەستکردی ناوخۆییە کە بۆ کارکردن لەگەڵ پڕۆژەکانی
بەرنامەسازی، فایل، تێرمیناڵ، کۆگاکانی Git و بیرگەی بەردەوامی پڕۆژە دروست کراوە.
داواکاری بە زمانی ئاسایی دەگۆڕێت بۆ پلانێکی کورت و کردارگەلێکی کۆنترۆڵکراو.
هەر ئامرازێک پێش جێبەجێکردن پشتڕاست دەکرێتەوە و ئەنجامی ڕاستەقینەی بۆ هەنگاوی
دواتر دەگەڕێتەوە.

وەشانی ئێستا [Ollama](https://ollama.com/) وەک دابینکەری مۆدێلی ناوخۆیی بەکار
دەهێنێت. ناوەڕۆکی شاماران سادە، تاقیکراوە و لە چوارچێوە گەورەکانی orchestration
سەربەخۆیە.

> **گرنگ:** شاماران پرۆسەیەکی بێ‌چاودێری نییە. گۆڕینی فایل، جێبەجێکردنی فەرمان
> و کرداری Git بە سیاسەتی دیاریکراو و پشتڕاستکردنەوەی بەکارهێنەر سنووردار کراون.

## ناوی شاماران

ناوی **شاماران** لە **شاهماران (Şahmaran)** وەرگیراوە؛ کەسایەتییەکی ئەفسانەیی
نیوەمرۆڤ و نیوەمار لە ئەفسانەناسی، ڕۆحانیەت، چیرۆکی زارەکی، هونەر و یادەوەریی
کەلتووریی کورددا. چیرۆکەکانی هێمای زانیاری، چارەسەری، پاراستن، سروشت، بەرگری و
ئەنجامی ناپاکی هەڵدەگرن. توێژینەوە کوردییەکان ئەوی وەک دایکی زەوی کوردستان و
بەشێک لە ڕۆحانیەتی کۆنی کوردی ناساندووە.

ناو و ناسنامەی پیکسڵی فەرمیی پڕۆژەکە ڕێز لە میراتی کوردی، خەڵکی کوردستان و ئەو
بنەماڵە کوردزمانانە دەگرێت کە وێنە و چیرۆکی شامارانیان پاراستووە. بۆ سەرچاوەکان
[تێبینیی بنەچەی کەلتووری](docs/cultural-origin.md) بخوێنەرەوە.

## بۆچی شاماران؟

| بنەما | جێبەجێکردن |
| --- | --- |
| **ناوخۆیی** | مۆدێلی Ollama، بیرگەی SQLite، تۆمار و workspace دەتوانن لەسەر کۆمپیوتەرەکەت بمێننەوە. |
| **بەڵگەمحەور** | شاماران تەنها کاتێک سەرکەوتن ڕادەگەیەنێت کە ئامرازەکە ئەنجامی سەرکەوتوو بگەڕێنێتەوە. |
| **پارێزراو بە بنەڕەت** | پشکنینی ڕێڕەو، جێبەجێکردن بە `shell=False`، کاتی سنووردار و پشتڕاستکردنەوەی گۆڕانکاری. |
| **هەنگاوی سنووردار** | هەر داواکارییەک ژمارەیەکی دیاریکراوی هەنگاوی هەیە؛ بنەڕەت هەشت هەنگاوە. |
| **پێکهاتەیی** | دابینکەر، ئامراز، بیرگە، ناوەڕۆکی ئەجێنت و UI لە یەکتر جیاکراونەتەوە. |
| **ڕوون** | Pythonی تایپ‌کراو و وابەستەیی کەم، پشکنین و گەشەپێدان ئاسان دەکەن. |

## تواناکانی وەشانی 0.1.0

| بەش | توانای ئێستا |
| --- | --- |
| ئەجێنت | پلانی کورت، کرداری JSONی پشتڕاستکراو، لووپی چاودێری و سنووری هەنگاو |
| مۆدێل | پەیوەندی بە Ollama، لیستی مۆدێل، پشکنینی تەندروستی و هەڵەی خوێندراو |
| فایل | لیست، خوێندنەوە، نووسین، گۆڕینی وردی دەق و دروستکردنی بوخچە |
| تێرمیناڵ | فەرمانی ڕێگەپێدراو، timeout، تۆمارکردنی دەرئەنجام و سیاسەتی پاراستن |
| Git | status، diff، log، branch، add و commitی ناوخۆیی |
| بیرگە | تۆمار، گەڕان، لیستی نوێ، لەبیرکردن و پاککردنەوە بە SQLite |
| ڕووکار | ڕووکاری Rich، ڕێنمایی یەکەم جار، Doctor و فەرمانە ناوخۆییەکان |
| کوالێتی | تاقیکردنەوە لە Python 3.11–3.13 و Windows، macOS و Linux |

## دەستپێکردنی خێرا

### پێویستییەکان

- Python 3.11 یان نوێتر
- Git
- Ollamaی دامەزراو و کارا
- مۆدێلێکی دامەزراو لە Ollama

### دامەزراندنی کورت بە uv

```powershell
uv tool install "git+https://github.com/ashkanWaisi/shamaran.git"
shamaran setup --model qwen3.5:9b
shamaran web
```

فەرمانی یەکەم شاماران ڕاستەوخۆ لە GitHub و لە ژینگەیەکی جیاواز دادەمەزرێنێت.
فەرمانی `setup` ڕێکخستنەکە لە `~/.shamaran/.env` دروست دەکات تا `shamaran` لە
هەر بوخچەیەکەوە کار بکات. بۆ نوێکردنەوە:

```powershell
uv tool upgrade shamaran
```

### ڕووکاری گرافیکی Web

```powershell
shamaran web
```

ڕووکاری سووک و پیکسڵی Copper Archive لە `http://127.0.0.1:8000` دەکرێتەوە.
دۆخی Ollama، هەڵبژاردنی مۆدێل، سنووری هەنگاو، گەڕان لە بیرگە، چالاکیی ئامراز،
ڕێگەدان بە گۆڕانکاری بۆ هەر نامەیەک و زمانەکانی ئینگلیزی، فارسی و کوردیی سۆرانی
لەخۆدەگرێت.

### وەرگرتنی سورس بۆ گەشەپێدان

```powershell
git clone https://github.com/ashkanWaisi/shamaran.git
cd shamaran
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

لە macOS و Linux:

```bash
git clone https://github.com/ashkanWaisi/shamaran.git
cd shamaran
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

### ڕێکخستنی Ollama

```env
SHAMARAN_PROVIDER=ollama
SHAMARAN_WORKSPACE=./workspace
SHAMARAN_MAX_STEPS=8
SHAMARAN_CONFIRM_MUTATIONS=true

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b
OLLAMA_TIMEOUT=120
```

پشکنینی دامەزراندن:

```powershell
shamaran doctor
```

جێبەجێکردن:

```powershell
shamaran
```

## فەرمانە ناوخۆییەکان

| فەرمان | مەبەست |
| --- | --- |
| `/help` | پیشاندانی یارمەتی |
| `/status` | دۆخی جێبەجێکردن و دابینکەر |
| `/tools` | لیستی ئامرازەکان |
| `/config` | ڕێکخستنی بێ‌نهێنی |
| `/memory` | بیرگەی نوێی ناوخۆیی |
| `/memory clear` | پاککردنەوەی بیرگە دوای پشتڕاستکردنەوە |
| `/clear` | پاککردنەوەی تێرمیناڵ |
| `/version` | پیشاندانی وەشان |
| `/doctor` | پشکنینی دامەزراندن |
| `/exit` | کۆتایی سێشن |

## چۆنیەتی کارکردن

1. بەکارهێنەر ئامانجەکە دەڵێت.
2. مۆدێل پلانێکی کورت یان کردارێکی ڕێکخراو دەگەڕێنێتەوە.
3. Pydantic ناوی ئامراز و argumentەکان پشتڕاست دەکاتەوە.
4. ئامراز سیاسەتی فایل، تێرمیناڵ یان Git جێبەجێ دەکات.
5. کرداری هەستیار بۆ ڕەزامەندی پیشان دەدرێت.
6. ئەنجامی ڕێکخراو بۆ هەنگاوی دواتر دەگەڕێتەوە.
7. لووپەکە بە وەڵامی کۆتایی یان سنووری هەنگاو کۆتایی دێت.

## پاراستن

- ڕێڕەوی نووسین ناتوانێت بە `..`، ڕێڕەوی ڕەها یان symlink لە workspace بچێتە دەرەوە.
- فەرمانەکان بە لیستی argument و `shell=False` جێبەجێ دەکرێن.
- pipe، redirection، command substitution و فەرمانی وێرانکەر قەدەغە کراون.
- گۆڕینی فایل و کرداری Git پشتڕاستکردنەوەی بەکارهێنەر پێویستە.
- Git push، force-push، reset-hard، clean و سڕینەوە وەک ئامرازی ئەجێنت بەردەست نین.
- بیرگەی SQLite هەوڵ دەدات زانیاریی نهێنی تۆمار نەکات.

ئەم پاراستنانە مەترسی کەم دەکەنەوە، بەڵام کۆدی نەناسراو بە تەواوی بێ‌مەترسی
ناکەن. پێش جێبەجێکردنی کۆدی کەسانی تر، سەرچاوە و داواکاریی ڕەزامەندی بخوێنەرەوە.
وردەکاری لە [سیاسەتی پاراستن](SECURITY.md)دایە.

## دۆخی پڕۆژە

شاماران `0.1.0` وەشانێکی سەرەتاییە. ڕووکاری تێرمیناڵ و Web UI کاردەکەن و تاقیکراونەتەوە.
ئەم توانایانە هێشتا لە وەشانی ئێستادا نین:

- کاری خۆکار و بێ‌چاودێری لە background
- دەستگەیشتنی بێ‌سنوور بە Shell
- Git pushی خۆکار
- کۆنترۆڵی وێبگەڕ یان desktop
- بیرگەی semantic بە embedding
- دەنگ
- plugin یان MCP runtime

بابەتەکانی roadmap بەڵێنی داهاتوون، نە توانای ئێستا.

## بەڵگەنامەکان

- [پێکهاتە](docs/architecture.md)
- [ڕێنمایی پاراستن](docs/security.md)
- [ڕێنمایی دابینکەر](docs/providers.md)
- [ڕێنمایی ئامراز](docs/tools.md)
- [ناو و بنەچەی کەلتووری](docs/cultural-origin.md)
- [یارمەتی](SUPPORT.md)
- [بەشداری](CONTRIBUTING.md)
- [گۆڕانکارییەکان](CHANGELOG.md)

## دروستکەر

**شاماران لەلایەن Ashkan Allahveisi دروست، دیزاین و بەرنامەسازی کراوە.**

- GitHub: [@ashkanWaisi](https://github.com/ashkanWaisi)
- ڕاپۆرتی کێشە: [github.com/ashkanWaisi/shamaran/issues](https://github.com/ashkanWaisi/shamaran/issues)

## مۆڵەت

Copyright © 2026 Ashkan Allahveisi

کۆدی سەرچاوە بە [مۆڵەتی MIT](LICENSE) بڵاو کراوەتەوە.

</div>
