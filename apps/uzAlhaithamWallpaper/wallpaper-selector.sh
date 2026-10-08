#!/bin/sh
# X11 ni majburiy qilish (Wayland glitch'lari uchun)
export QT_QPA_PLATFORM=xcb
export QT_AUTO_SCREEN_SCALE_FACTOR=0

# Flatpak ichida $HOME = ~/.var/app/<app-id>
# Fon rasmini o'rnatish uchun real $HOME kerak
case "$HOME" in
    */.var/app/*)
        export HOME="${HOME%/.var/app/*}"
        ;;
esac

exec python3 /app/share/wallpaper-selector/main.py "$@"
