# Asadbek Flatpaks

Shaxsiy Flatpak repozitoriyasi.

## Ilovalar

| App | Package | Platform | Description |
|-----|---------|----------|-------------|
| **Akasha System** | `asadbek.akasha.cv` | Linux + Windows | Akasha.cv desktop client (Genshin Impact leaderboard viewer) |
| **DesignCraft** | `ai.storyteller.designcraft` | Linux | Graphic design tool |
| **EffectCraft** | `ai.storyteller.effectcraft` | Linux | Visual effects tool |
| **FilmCraft** | `ai.storyteller.filmcraft` | Linux | Video editing tool |
| **LightCraft** | `ai.storyteller.lightcraft` | Linux | Lighting design tool |
| **Namida** | `com.msob7y.namida` | Linux | Beautiful music & video player with YouTube support |
| **PdfCraft** | `ai.storyteller.pdfcraft` | Linux | PDF editing tool |
| **PhotoCraft** | `ai.storyteller.photocraft` | Linux | Photo editor |
| **Ranking System** | `io.github.uzalhaitham.RankingSystem` | Linux | Genshin Impact profile viewer with Akasha.cv ranking |
| **VectorCraft** | `ai.storyteller.vectorcraft` | Linux | Vector graphics tool |
| **Wallpaper Selector** | `io.github.uzAlhaitham.WallpaperSelector` | Linux + Windows | Browse and set wallpapers from Wallhaven.cc |
| **WSelector** | `io.github.Cookiiieee.WSelector` | Linux | Wallpaper Selector Manager |

## Linux — Repozitoriyani qo'shish

    flatpak remote-add --if-not-exists asadbekflatpaks https://uzAlhaitham.github.io/AsadbekFlatpaks/asadbekflatpaks.flatpakrepo

Keyin istalgan ilovani o'rnating:

    flatpak install asadbekflatpaks ai.storyteller.designcraft

## Windows — To'g'ridan-to'g'ri yuklab olish

Eng so'nggi `.exe` faylini [Releases](https://github.com/uzAlhaitham/AsadbekFlatpaks/releases) sahifasidan yuklab oling. O'rnatish shart emas — shunchaki ishga tushiring.

## Eslatma

**PhotoCraft** Wayland'da fayl tortib tashlashni (drag-and-drop) qo'llab-quvvatlamaydi. X11 rejimida ishga tushiring:

    flatpak override --user --socket=x11 --nosocket=wayland --env=GDK_BACKEND=x11 --env=WAYLAND_DISPLAY= ai.storyteller.photocraft

Yoki dastur ichidagi **File > Open** menyusidan foydalaning.

## Credits

All applications are the work of their respective authors. This repository only repackages them for personal use.

- [Namida](https://github.com/namidaco/namida) — developed by namidaco
- [WSelector](https://github.com/Cookiiieee/WSelector) — developed by Phillip Cook
- [Wallpaper Selector](apps/uzAlhaithamWallpaper/) — developed by uzAlhaitham
- Craft ilovalari — developed by Storyteller

## License

The configuration, scripts, and metadata in **this repository** are licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

The applications themselves are licensed under their own respective licenses.

This repository is **not affiliated** with the original app developers.
