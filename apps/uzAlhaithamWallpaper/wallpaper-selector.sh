#!/bin/sh
# In Flatpak, $HOME = ~/.var/app/<app-id>.
# Fon rasmini o'rnatish uchun real $HOME kerak (host'dan ko'rinadi).
case "$HOME" in
    */.var/app/*)
        export HOME="${HOME%/.var/app/*}"
        ;;
esac
exec python3 /app/share/wallpaper-selector/main.py "$@"
