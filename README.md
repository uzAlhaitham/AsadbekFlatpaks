# AsadbekFlatpaks

A personal Flatpak repository — my curated collection of hand-packaged, GPG-signed applications, all served from a single unified remote.

## Available Applications

| App | Package | Platform | Description |
|-----|---------|----------|-------------|
| **Namida** | `com.msob7y.namida` | Linux | Beautiful music & video player with YouTube support |
| **WSelector** | `io.github.Cookiiieee.WSelector` | Linux | Wallpaper Selector Manager |
| **Ranking System** | `io.github.uzalhaitham.RankingSystem` | Linux | Genshin Impact profile viewer with Akasha.cv ranking |
| **Wallpaper Selector** | `io.github.uzAlhaitham.WallpaperSelector` | Linux + Windows | Browse and set wallpapers from Wallhaven.cc |

## Linux — Adding the Repository

    flatpak remote-add --if-not-exists asadbekflatpaks https://uzAlhaitham.github.io/AsadbekFlatpaks/asadbekflatpaks.flatpakrepo

Then install any app:

    flatpak install asadbekflatpaks io.github.uzAlhaitham.WallpaperSelector

## Windows — Direct Download

Download the latest `.exe` from the [Releases](https://github.com/uzAlhaitham/AsadbekFlatpaks/releases) page. No installation required — just run it.

## Credits

All applications are the work of their respective authors. This repository only repackages them for personal use.

- [Namida](https://github.com/namidaco/namida) — developed by namidaco
- [WSelector](https://github.com/Cookiiieee/WSelector) — developed by Phillip Cook
- [Wallpaper Selector](apps/uzAlhaithamWallpaper/) — developed by uzAlhaitham

## License

The configuration, scripts, and metadata in **this repository** are licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

The applications themselves are licensed under their own respective licenses.

This repository is **not affiliated** with the original app developers.
