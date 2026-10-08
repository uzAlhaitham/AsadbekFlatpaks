# uzAlhaitham's Wallpaper Selector

> Browse and set wallpapers from [Wallhaven.cc](https://wallhaven.cc)

A PyQt5 desktop application for browsing and setting wallpapers from
Wallhaven.cc, available on **Linux (Flatpak)** and **Windows (EXE)**.

---

## Features

- Search wallpapers on Wallhaven.cc
- Filter by category: **General / Anime / People**
- SFW / NSFW filter (requires Wallhaven API key)
- Download manager with **pause / resume**
- **Set wallpaper** on KDE Plasma, GNOME, XFCE, Sway
- Multi-language UI (Uzbek, Russian, English, and more)
- Built-in **image viewer** with:
  - Mouse wheel **zoom**
  - Left-click **pan**
  - **Fit** and **100%** buttons
  - Horizontal + vertical scrollbars
- Smooth animations throughout the UI

---

## Installation

### Linux (Flatpak)

Add the repository:

    flatpak remote-add --if-not-exists asadbekflatpaks https://uzAlhaitham.github.io/AsadbekFlatpaks/asadbekflatpaks.flatpakrepo

Install:

    flatpak install asadbekflatpaks io.github.uzAlhaitham.WallpaperSelector

Update:

    flatpak update io.github.uzAlhaitham.WallpaperSelector

### Windows (EXE)

Download the latest `.exe` from the
[Releases page](https://github.com/uzAlhaitham/AsadbekFlatpaks/releases).
No installation required - just double-click.

> On first launch, Windows Defender may warn you
> (the EXE is unsigned). Click **More info -> Run anyway**.

---

## Changelog

### v1.2.3 - 2025-10-08

**UI polish:**

- Transparent scrollbars in image viewer (no more solid black bars)
- Smooth scrollbar handles with hover and pressed states
- Image viewer opens at 90% of main window
- Native OS titlebar for reliable resize (fixed Wayland/GNOME glitch)
- Cleaner image viewer layout

### v1.2.2 - 2025-10-08

- Easier window drag (middle mouse, Alt, Ctrl)
- Image viewer size = 90% of main window

### v1.2.1 - 2025-10-08

- Fixed window stays at user-chosen size when switching images
- Window can now be resized smaller (MIN_W 300 -> 250)
- Ctrl + left-click to drag window

### v1.1.0 - 2025-10-08

**New features:**

- Smooth animations across the whole UI
  - Card hover zoom
  - Card fade-in (staggered)
  - Click ripple effect
  - Loading spinner
  - Pagination button press animation
  - Smooth scroll-to-top on refresh
- **Image viewer overhaul**:
  - Mouse wheel **zoom** (5% - 800%)
  - Left-click **pan** (drag image)
  - **Fit** button (fill screen, no black bars)
  - **100%** button (original pixel size)
  - Horizontal + vertical **scrollbars**
- New keyboard shortcuts in image viewer:
  - `F` - Fit to screen
  - `1` - 100% original size
  - `Left` / `Right` - previous / next image
  - `F11` - fullscreen toggle
  - `Esc` - exit fullscreen / close

**Bug fixes:**

- **Config not saving on fresh install** - API key, folder, and
  language were lost after restart on both Windows and Linux
- **Windows config path** - now saves to
  `%LOCALAPPDATA%\uzAlhaithamWallpaper\config.json` instead of
  the Linux-style `~/.uzalhaitham_wallpaper.json`
- **Fullscreen mode** no longer breaks when switching images
- **Keyboard arrows** in image viewer work reliably
- Removed **6-column grid** option (caused UI glitches)

### v1.0.0 - 2025-10-07

- First public release
- Wallhaven.cc search + download manager
- Set wallpaper on KDE / GNOME / XFCE / Sway
- Multi-language UI

---

## Requirements

- **Linux:** Flatpak with `org.kde.Platform//5.15-24.08` and
  `com.riverbankcomputing.PyQt.BaseApp//5.15-24.08`
- **Windows:** Windows 10 or 11 (64-bit), no dependencies
- **Internet:** Required for Wallhaven.cc API

---

## License

MIT - see [LICENSE](../../LICENSE).

---

## O'zbekcha

# uzAlhaitham'ning Fon rasmi Tanlagichi

> [Wallhaven.cc](https://wallhaven.cc) saytidan fon rasmlarini
> ko'rish va o'rnatish

**Linux (Flatpak)** va **Windows (EXE)** uchun PyQt5 dasturi.

### Xususiyatlar

- Wallhaven.cc saytidan fon rasmlarini qidirish
- Kategoriya bo'yicha filtrlash: **Umumiy / Anime / Odamlar**
- SFW / NSFW filtri (API kalit bilan)
- Yuklab olish menejeri (pauza / davom ettirish)
- **Fon rasmini o'rnatish**: KDE Plasma, GNOME, XFCE, Sway
- Ko'p tilli interfeys (o'zbek, rus, ingliz va boshqalar)
- Ichki **rasm ko'ruvchi**:
  - Sichqoncha g'ildiragi bilan **zoom**
  - Chap tugma bilan **surish**
  - **Fit** va **100%** tugmalari
  - Gorizontal va vertikal scrollbarlar
- Butun interfeys bo'ylab silliq animatsiyalar

### O'rnatish

**Linux (Flatpak):**

    flatpak remote-add --if-not-exists asadbekflatpaks https://uzAlhaitham.github.io/AsadbekFlatpaks/asadbekflatpaks.flatpakrepo

    flatpak install asadbekflatpaks io.github.uzAlhaitham.WallpaperSelector

**Windows (EXE):**

[Releases sahifasidan](https://github.com/uzAlhaitham/AsadbekFlatpaks/releases)
oxirgi `.exe` faylni yuklab oling va ikki marta bosing.

> Birinchi marta Windows Defender ogohlantirishi mumkin
> (fayl imzosiz). **More info -> Run anyway** tugmasini bosing.

### v1.1.0 - Yangilanishlar

**Yangi xususiyatlar:**

- Interfeys bo'ylab silliq animatsiyalar
  - Kartalar ustida hover zoom
  - Kartalar ketma-ket paydo bo'lishi
  - Bosganda to'lqin effekti
  - Yuklanish spinner'i
  - Pagination tugmalari bosilish animatsiyasi
  - Sahifa yangilanganda silliq tepaga o'tish
- **Rasm ko'ruvchi yangilandi**:
  - Sichqoncha g'ildiragi bilan **zoom** (5% - 800%)
  - Chap tugma bilan **surish**
  - **Fit** tugmasi (ekranni to'ldirish)
  - **100%** tugmasi (original hajm)
  - Gorizontal va vertikal scrollbarlar
- Yangi klaviatura tugmalari:
  - `F` - Fit
  - `1` - 100%
  - `Left` / `Right` - oldingi / keyingi rasm
  - `F11` - to'liq ekran
  - `Esc` - to'liq ekrandan chiqish

**Tuzatilgan xatolar:**

- **Config saqlanmasligi** - API kalit, papka va til qayta
  ishga tushirilgandan keyin yo'qolib qolardi
- **Windows'dagi config yo'li** - endi to'g'ri joyga saqlanadi
  (`%LOCALAPPDATA%\uzAlhaithamWallpaper\config.json`)
- **To'liq ekran rejimi** rasm almashtirilganda buzilmaydi
- **Klaviatura strelkalari** ishonchli ishlaydi
- **6 talik grid** olib tashlandi (UI muammosi sabab edi)

---

**Muallif:** uzAlhaitham
**Litsenziya:** MIT
