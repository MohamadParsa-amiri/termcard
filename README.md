# termcard

> Spaced-repetition flashcards in your terminal — zero dependencies, first-class RTL support.

[![PyPI](https://img.shields.io/pypi/v/termcard)](https://pypi.org/project/termcard/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/termcard/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![tests](https://github.com/MohamadParsa-amiri/termcard/actions/workflows/tests.yml/badge.svg)](https://github.com/MohamadParsa-amiri/termcard/actions/workflows/tests.yml)

**termcard** is a small command-line flashcard app built around the classic **SM-2 spaced-repetition algorithm** (the algorithm Anki's scheduler is based on). It keeps everything in a single JSON file, ships with **zero third-party dependencies**, and — unusually for a terminal app — renders **right-to-left scripts like Persian and Arabic correctly**.

```text
  +==========================================================+
  |                        TERMCARD                          |
  +==========================================================+

  Decks: 1   Cards: 8   Due: 8   New: 8

  [D] Decks
  [R] Review all due cards
  [S] Statistics
  [Q] Quit
```

## Features

- **SM-2 spaced repetition** — cards you find easy come back later; cards you struggle with come back sooner (`Again / Hard / Good / Easy`).
- **Typed-answer mode** — try to recall and type the answer before revealing it. Answers are graded as *correct / close / wrong* using fuzzy matching.
- **Persian & Arabic friendly** — typed answers are normalized before grading: Arabic yeh/kaf map to Persian ones (`ي→ی`, `ك→ک`), Arabic-Indic digits to ASCII (`۱۲۳→123`), accents are ignored (`adios` = `Adiós`), and punctuation/case don't matter.
- **RTL rendering** — Persian/Arabic card text is aligned and wrapped properly in the terminal using Unicode bidi controls and display-width awareness.
- **Decks & statistics** — organize cards into decks, track review counts and average ease factor.
- **Safe storage** — one JSON file, written atomically (temp file + rename), so a crash mid-save can't corrupt your data.
- **Zero dependencies** — pure Python standard library. Install it and you're done.

## Install

```bash
python -m pip install termcard
```

Requires Python 3.10+. No other dependencies.

Or run from source:

```bash
git clone https://github.com/MohamadParsa-amiri/termcard.git
cd termcard
python -m termcard
```

## Quick start

```bash
termcard --demo        # first run: seed a small Spanish demo deck, then start
termcard               # normal run (data lives in ~/.termcard/decks.json)
termcard --data X.json # use a custom data file
termcard --version
```

In the app: press `D` to create a deck, `A` inside a deck to add cards, and `R` to start a review session.

### Review flow

1. The **front** of a card is shown.
2. Type your answer (or just press Enter to reveal it directly).
3. If you typed something, you get instant feedback: `Correct!` / `So close! (87% match)` / `Wrong answer`.
4. The **back** is revealed, then you rate your recall: `1 Again · 2 Hard · 3 Good · 4 Easy` — that rating drives the SM-2 scheduler.

<!-- TODO: after first release, record a short GIF (e.g. with https://github.com/charmbracelet/vhs or asciinema) and embed it here. -->

## How scheduling works

termcard uses the SM-2 algorithm with four recall ratings:

| Rating | Effect |
|--------|--------|
| Again  | Reset the streak; card returns tomorrow (and again this session) |
| Hard   | Streak is kept, but the ease factor drops so future intervals grow more slowly |
| Good   | Interval grows (1 → 6 → ×ease-factor days) |
| Easy   | Interval grows faster; ease factor rises |

The interval between reviews multiplies each time you rate `Good` or `Easy`, so well-known cards can go weeks or months between reviews, while weak cards stay in rotation.

## Data & privacy

All data lives in a single JSON file:

- Default: `~/.termcard/decks.json`
- Override: `--data PATH` flag or `TERMCARD_DATA` environment variable

No accounts, no network calls, no telemetry. Your cards are yours.

## Development

```bash
git clone https://github.com/MohamadParsa-amiri/termcard.git
cd termcard
python -m unittest discover -s tests -v
```

The test suite covers models, the SM-2 scheduler, atomic storage, and Persian answer normalization/matching.

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

# termcard (نسخه‌ی فارسی)

<div dir="rtl">

**ترم‌کارت** یک اپلیکیشن فلش‌کارت خط فرمانی است که بر پایه‌ی الگوریتم تکرار فاصله‌دار **SM-2** (الگوریتمی که زمان‌بندی Anki بر پایه‌ی آن است) ساخته شده است. تمام داده‌ها در یک فایل JSON ذخیره می‌شود، هیچ وابستگی جانبی ندارد، و — برخلاف بیشتر ابزارهای ترمینالی — متن فارسی و عربی را **درست** نمایش می‌دهد.

## امکانات

- **تکرار فاصله‌دار SM-2** — کارت‌های سخت زودتر و کارت‌های آسان دیرتر برمی‌گردند (`Again / Hard / Good / Easy`).
- **حالت جواب تایپی** — قبل از دیدن پاسخ، جواب را تایپ کنید؛ برنامه با تطبیق فازی نتیجه را اعلام می‌کند: درست / نزدیک بود / غلط.
- **نرمال‌سازی فارسی** — «ي» و «ك» عربی با «ی» و «ک» فارسی، ارقام عربی با انگلیسی، اعراب و علائم نقطه‌گذاری در مقایسه‌ی جواب نادیده گرفته می‌شوند.
- **رندر راست‌به‌چپ** — متن فارسی در ترمینال با کنترل‌کننده‌های bidi یونیکد و محاسبه‌ی عرض واقعی نویسه‌ها، تراز و درست نمایش داده می‌شود.
- **دسته‌ها و آمار** — کارت‌ها را در دسته‌های جدا نگه دارید و آمار مرورها را ببینید.
- **ذخیره‌سازی امن** — یک فایل JSON که به‌صورت اتمیک (فایل موقت + rename) نوشته می‌شود؛ قطع‌شدن ناگهانی برنامه داده‌ها را خراب نمی‌کند.
- **بدون وابستگی** — فقط کتابخانه‌ی استاندارد پایتون.

## نصب

```bash
pip install termcard
```

پایتون ۳.۱۰ به بالا. هیچ پیش‌نیاز دیگری لازم نیست.

## شروع سریع

```bash
termcard --demo   # بار اول: یک دسته‌ی نمونه‌ی اسپانیایی ساخته می‌شود
termcard          # اجرای عادی (داده‌ها در ~/.termcard/decks.json)
```

داخل برنامه: با `D` دسته بسازید، داخل دسته با `A` کارت اضافه کنید و با `R` مرور را شروع کنید.

در جلسه‌ی مرور، جلوی هر کارت می‌توانید جواب را تایپ کنید (یا فقط Enter بزنید تا پاسخ نمایش داده شود)، سپس کیفیت یادآوری‌تان را از ۱ تا ۴ مشخص می‌کنید و الگوریتم زمان مرور بعدی را تعیین می‌کند.

## داده‌ها و حریم خصوصی

- محل پیش‌فرض داده‌ها: `~/.termcard/decks.json`
- تغییر محل: فلگ `--data` یا متغیر محیطی `TERMCARD_DATA`
- بدون ثبت‌نام، بدون اتصال به شبکه، بدون تلمتری.

## توسعه

```bash
python -m unittest discover -s tests -v
```

مجموعه‌ی تست‌ها مدل‌ها، الگوریتم SM-2، ذخیره‌سازی اتمیک و نرمال‌سازی جواب فارسی را پوشش می‌دهد.

## لایسنس

[MIT](LICENSE) — آزاد برای استفاده، تغییر و انتشار.

</div>
