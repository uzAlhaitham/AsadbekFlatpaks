# AsadbekFlatpaks

A personal Flatpak repository — my curated collection of hand-packaged, GPG-signed applications, all served from a single unified remote for effortless installation and updates.

## Available Applications

| App | Package | Version | Description |
|-----|---------|---------|-------------|
| **Namida** | `com.msob7y.namida` | 7.1.2 | Beautiful music & video player with YouTube support |

## Installation

Add the repository once:

    flatpak remote-add --if-not-exists asadbekflatpaks https://uzAlhaitham.github.io/AsadbekFlatpaks/asadbekflatpaks.flatpakrepo

Then install any app:

    flatpak install asadbekflatpaks com.msob7y.namida

## Updating

    flatpak update

## Manual Installation

Download `.flatpak` bundles from the [Releases](https://github.com/uzAlhaitham/AsadbekFlatpaks/releases) page.

## Adding a New App

1. Create a folder: `apps/<app-name>/`
2. Add the manifest: `apps/<app-name>/<app-id>.yml`
3. Add the bundle: `apps/<app-name>/bundle/<App>-x86_64.flatpak`
4. Add metadata: `apps/<app-name>/app-info.yml`
5. Push — everything else is automated via GitHub Actions

## Structure

    apps/
    └── namida/
        ├── com.msob7y.namida.yml    # Flatpak manifest
        ├── app-info.yml              # App metadata
        ├── icons/                    # App icons
        └── bundle/
            └── Namida-x86_64.flatpak # Prebuilt bundle

## License

The configuration, scripts, and metadata in **this repository** are licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

The applications themselves are licensed under their own respective licenses:
- **Namida** — EULA (see [upstream](https://github.com/namidaco/namida))

This repository is **not affiliated** with the original app developers.
