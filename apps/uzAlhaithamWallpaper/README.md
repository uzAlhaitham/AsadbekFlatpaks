# uzAlhaitham's Wallpaper Selector

Wallhaven.cc'dan fon rasmlarini ko'rish va o'rnatish uchun PyQt5 ilova.

## Xususiyatlar

- Wallhaven API orqali rasm qidirish
- General / Anime / People toifalari
- SFW / NSFW filtri (API kalit bilan)
- Rasm yuklab olish, pauza, davom ettirish
- Fon rasmini o'rnatish (KDE Plasma / GNOME / XFCE / Sway)
- Ko'p tilli interfeys (o'zbek, rus, ingliz, turk, nemis, fransuz, va boshqalar)
- To'liq ekran ko'rish, grid o'lchamini sozlash
- Sozlamalar dialogi

## O'rnatish

### 1. Kerakli runtime'larni o'rnatish

flatpak install -y flathub org.kde.Platform//5.15-24.08 com.riverbankcomputing.PyQt.BaseApp//5.15-24.08

### 2. Ilovani o'rnatish

flatpak install --user bundle/WallpaperSelector-x86_64.flatpak

### 3. Ishga tushirish

flatpak run io.github.uzAlhaitham.WallpaperSelector

Yoki Desktop menyusidan **"uzAlhaitham's Wallpaper Selector"** ni toping.

## Ruxsatlar

- `--filesystem=home` — fon rasmlarini saqlash uchun
- `--share=network` — Wallhaven API uchun
- `--talk-name=org.freedesktop.Flatpak` — fon rasmini host'da o'rnatish uchun
- `--talk-name=org.kde.plasmashell` — KDE Plasma integratsiyasi
- `--socket=session-bus` — tizim D-Bus interfeyslari uchun

## Litsenziya

MIT
