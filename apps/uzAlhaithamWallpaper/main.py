import os
import sys
import json
import shutil
import subprocess
import threading
from pathlib import Path
from locale import getdefaultlocale
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QTimer, QEvent, QUrl,
                          QPoint)
from PyQt5.QtGui import (QPixmap, QImage, QPainter, QBrush,
                         QKeySequence, QDesktopServices, QFontMetrics,
                         QCursor, QColor)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QScrollArea, QGridLayout,
    QComboBox,
    QFrame, QMessageBox, QStatusBar, QToolButton, QMenu, QInputDialog,
    QAction, QShortcut, QProgressBar, QDialog, QSizePolicy
)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "uzAlhaithamWallpaper/1.0"})

# ==================== Flatpak support ====================
IN_FLATPAK = Path("/.flatpak-info").exists()

def run_cmd(cmd, **kwargs):
    """Flatpak ichida bo'lsak, buyruqni host'da ishga tushiramiz."""
    if IN_FLATPAK:
        cmd = ["flatpak-spawn", "--host"] + list(cmd)
    return subprocess.run(cmd, **kwargs)


# ==================== Translation Strings ====================
# Faqat tarjima qilinishi kerak bo'lgan matnlar
TR = {
    "en": {
        # Tooltips (description) — tarjima qilinadi
        "tip_general": "General Wallpapers",
        "tip_anime": "Anime/Manga style",
        "tip_people": "Wallpapers featuring people",
        "tip_sfw": "Safe For Work",
        "tip_nsfw": "Mature Content (Not Safe For Work)",
        "tip_save_as": "Save to a custom folder",
        "tip_remove": "Remove this image from disk",
        "tip_fullscreen": "Fullscreen",
        # Section labels
        "lbl_category": "CATEGORY",
        "lbl_safety": "SAFETY",
        "lbl_sort_by": "Sort by:",
        "lbl_grid": "Grid:",
        # Sort options
        "sort_latest": "Latest",
        "sort_popular": "Popular",
        "sort_random": "Random",
        # Search
        "search_ph": "Search wallpapers...",
        # Settings dialog
        "settings_title": "Settings",
        "settings_lang": "LANGUAGE",
        "settings_lang_label": "Display language:",
        "settings_api": "WALLHAVEN API KEY",
        "settings_folder": "DOWNLOAD FOLDER",
        "settings_data": "DATA",
        "settings_clear_cache": "Clear cache",
        "settings_clear_all": "Clear ALL data",
        "settings_close": "Close",
        "settings_save_api": "Save API key",
        "settings_del_api": "Delete API key",
        "settings_get_api": "Get API",
        "settings_change_folder": "Change folder",
        "settings_api_ph": "Paste API key...",
        "settings_lang_saved": "Language saved. Restart to apply.",
        # Pagination
        "goto_ph": "Enter page number to jump to...",
        # Toggle buttons (endi tarjima qilinadi)
        "btn_general": "General",
        "btn_anime": "Anime",
        "btn_people": "People",
        "btn_sfw": "SFW",
        "btn_nsfw": "NSFW",
        # Action buttons
        "set_bg": "Set Wallpaper",
        "btn_download": "⬇ Download",
        "btn_save_as": "Save as …",
        "loading": "Loading...",
        "status_cancelled": "Cancelled",
"status_error": "Error",
"msg_download_error": "Download error",
"msg_failed": "Failed",
        "btn_set_bg": "Set Wallpaper",
        "btn_downloaded": "📂 Downloaded",
        "btn_online": "🌐 Online",
        # Settings labels
        "lbl_language": "LANGUAGE",
        "lbl_display_lang": "Display language:",
        "lbl_api_key": "WALLHAVEN API KEY",
        "lbl_download_folder": "DOWNLOAD FOLDER",
        "lbl_data": "DATA",
        "btn_clear_cache": "Clear cache",
        "btn_clear_all": "Clear ALL data",
        "btn_close": "Close",
        "btn_save_api": "Save API key",
        "btn_del_api": "Delete API key",
        "btn_get_api": "Get API",
        "btn_change_folder": "Change folder",
        "api_ph": "Paste API key...",
        "lang_saved_msg": "Language saved. Restart to apply.",
        "lang_title": "Language",
        "lang_changed": "Language changed. Restart the application to apply fully?",
        "btn_ok": "OK",
        "btn_later": "Later",
        "btn_restart": "Restart",
        "btn_yes": "Yes",
        "btn_no": "No",
        "msg_cache_cleared": "Cache cleared. (current wallpaper saved)",
        "msg_all_cleared": "All data cleared. Restart the application.",
        "msg_api_saved": "API key saved.",
        "tip_folder": "Wallpapers will be downloaded to this folder",
        "tip_home": "Go to home (first page, clear search)",
        "tip_refresh": "Refresh current page",
        "tip_settings": "Open settings",
        "btn_show": "Show",
        "btn_hide": "Hide",
        "badge_set": "INSTALLED",
        "msg_api_deleted": "API key deleted.",
        "msg_lang_saved": "Language saved. Restart the application.",
                "nsfw_countdown": "⚠  Enabling NSFW in {}...",
        "msg_ok_title": "OK",
        "error_title": "Error",
        "msg_all_cleared_title": "Clear ALL data",
        "clear_cache_title": "Clear cache",
        "clear_cache_body": "Clear cache? (thumbnails and temporary data)",
        "clear_all_title": "Clear ALL data",
        "clear_all_body": "ALL data will be deleted. Continue?",
        "del_api_title": "Delete API key",
        "del_api_body": "Delete the API key?",
        "cancel": "Cancel",
        "confirm_delete_title": "Delete wallpaper",
        "confirm_delete_body": 'Delete "{}" from disk?',
    },
}
LANG = "en"

# ==================== Translation ====================
_TRANS_CACHE = {}
# ==================== Manual translations ====================
# Google Translate noto'g'ri tarjima qiladigan so'zlar
MANUAL_TRANS = {
    "uz": {
        "Downloaded": "Yuklab Olingan",
        "Online": "Onlayn",
        "Download": "Yuklash",
        "Save as …": "Boshqa joyga saqlash",
        "Set Wallpaper": "Fon rasmini o'rnatish",
        "General": "Umumiy",
        "Anime": "Anime",
        "People": "Odamlar",
        "SFW": "SFW",
        "NSFW": "NSFW",
        "Latest": "Yangi",
        "Popular": "Mashhur",
        "Random": "Tasodifiy",
        "Close": "Yopish",
        "Cancel": "Bekor qilish",
        "Yes": "Ha",
        "No": "Yo'q",
        "Later": "Keyinroq",
        "Restart": "Qayta ishga tushirish",
        "Show": "Ko'rsatish",
        "Hide": "Yashirish",
        "Settings": "Sozlamalar",
        "Search wallpapers...": "Fon rasmlarini qidirish...",
        "column": "ustun",
        "columns": "ustun",
        "Grid": "Ustunlar",
        "Grid:": "Ustunlar:",
        "Sort by:": "Saralash:",
        "Grid:": "Ustunlar:",
        "Fullscreen": "To'liq ekran",
        "CATEGORY": "KATEGORIYA",
        "SAFETY": "XAVFSIZLIK",
        "LANGUAGE": "TIL",
        "Display language:": "Ko'rsatish tili:",
        "WALLHAVEN API KEY": "WALLHAVEN API KALITI",
        "DOWNLOAD FOLDER": "YUKLASH PAPKASI",
        "DATA": "MA'LUMOTLAR",
        "Clear cache": "Keshni tozalash",
        "Clear ALL data": "Barcha ma'lumotlarni o'chirish",
        "Save API key": "API kalitni saqlash",
        "Delete API key": "API kalitni o'chirish",
        "Get API": "API olish",
        "Change folder": "Papkani o'zgartirish",
        "Open settings": "Sozlamalarni ochish",
        "Wallpapers will be downloaded to this folder": "Fon rasmlari shu papkaga yuklanadi",
        "Go to home (first page, clear search)": "Boshiga qaytish (birinchi sahifa, qidiruvni tozalash)",
        "Refresh current page": "Joriy sahifani yangilash",
        "Wallpaper set: {}": "Fon rasmi o'rnatildi: {}",
        "API key saved.": "API kalit saqlandi.",
        "API key deleted.": "API kalit o'chirildi.",
        "API key is empty!": "API kalit bo'sh!",
        "Cache cleared.": "Kesh tozalandi.",
        "All data cleared.": "Barcha ma'lumotlar o'chirildi.",
        "All data cleared. Continue?": "Barcha ma'lumotlar o'chiriladi. Davom etilsinmi?",
        "Clear cache? (thumbnails and temporary data)": "Keshni tozalash? (rasmlar va vaqtinchalik ma'lumotlar)",
        "Delete the API key?": "API kalitni o'chirish?",
        "Restart the application to apply?": "Qo'llash uchun dasturni qayta ishga tushirish?",
        "Language saved. Restart the application.": "Til saqlandi. Dasturni qayta ishga tushiring.",
        "Remove this image from disk": "Rasmni diskdan o'chirish",
        "Save to a custom folder": "Boshqa papkaga saqlash",
        "General Wallpapers": "Umumiy fon rasmlari",
        "Anime/Manga style": "Anime/Manga uslubi",
        "Wallpapers featuring people": "Odamlar tasvirlangan fon rasmlari",
        "Safe For Work": "Hamma uchun xavfsiz",
        "Mature Content (Not Safe For Work)": "Kattalar uchun kontent",
        "Enter page number to jump to...": "O'tish uchun sahifa raqamini kiriting...",
    },
    "ru": {
        "Downloaded": "Скачано",
        "Online": "Онлайн",
        "Download": "Скачать",
        "Save as …": "Сохранить как …",
        "Set Wallpaper": "Установить обои",
        "Close": "Закрыть",
        "Cancel": "Отмена",
        "Yes": "Да",
        "No": "Нет",
        "Later": "Позже",
        "Restart": "Перезапустить",
        "Show": "Показать",
        "Hide": "Скрыть",
        "Settings": "Настройки",
        "Search wallpapers...": "Поиск обоев...",
        "column": "столбец",
        "columns": "столбцов",
        "Grid": "Сетка",
        "Grid:": "Сетка:",
        "Sort by:": "Сортировать по:",
        "Grid:": "Сетка:",
        "Fullscreen": "Полный экран",
        "CATEGORY": "КАТЕГОРИЯ",
        "SAFETY": "БЕЗОПАСНОСТЬ",
        "LANGUAGE": "ЯЗЫК",
        "Display language:": "Язык интерфейса:",
        "WALLHAVEN API KEY": "КЛЮЧ API WALLHAVEN",
        "DOWNLOAD FOLDER": "ПАПКА ЗАГРУЗКИ",
        "DATA": "ДАННЫЕ",
        "Clear cache": "Очистить кеш",
        "Clear ALL data": "Очистить ВСЕ данные",
        "Save API key": "Сохранить ключ API",
        "Delete API key": "Удалить ключ API",
        "Get API": "Получить API",
        "Change folder": "Изменить папку",
        "Open settings": "Открыть настройки",
        "Wallpapers will be downloaded to this folder": "Обои будут загружены в эту папку",
        "Go to home (first page, clear search)": "На главную (первая страница, очистить поиск)",
        "Refresh current page": "Обновить текущую страницу",
        "Wallpaper set: {}": "Обои установлены: {}",
        "API key saved.": "Ключ API сохранён.",
        "API key deleted.": "Ключ API удалён.",
        "API key is empty!": "Ключ API пуст!",
        "Cache cleared.": "Кеш очищен.",
        "All data cleared.": "Все данные удалены.",
        "All data cleared. Continue?": "Все данные будут удалены. Продолжить?",
        "Clear cache? (thumbnails and temporary data)": "Очистить кеш? (миниатюры и временные данные)",
        "Delete the API key?": "Удалить ключ API?",
        "Restart the application to apply?": "Перезапустить приложение?",
        "Language saved. Restart the application.": "Язык сохранён. Перезапустите приложение.",
        "Remove this image from disk": "Удалить это изображение с диска",
        "Save to a custom folder": "Сохранить в другую папку",
        "General Wallpapers": "Общие обои",
        "Anime/Manga style": "Стиль аниме/манга",
        "Wallpapers featuring people": "Обои с людьми",
        "Safe For Work": "Безопасно для всех",
        "Mature Content (Not Safe For Work)": "Контент для взрослых",
        "Enter page number to jump to...": "Введите номер страницы...",
    },
}


def manual_translate(text, lang):
    """Qo'lda kiritilgan tarjimalar."""
    if lang in MANUAL_TRANS:
        return MANUAL_TRANS[lang].get(text, None)
    return None




def get_installed_badge_text():
    """INSTALLED badge uchun matn (har til uchun)."""
    lang = T.get_language() if hasattr(T, "get_language") else "en"
    texts = {
        "en": "INSTALLED",
        "uz": "O'rnatilgan",
        "ru": "Установлено",
        "tr": "YÜKLENDİ",
        "de": "INSTALLIERT",
        "fr": "INSTALLÉ",
        "es": "INSTALADO",
        "it": "INSTALLATO",
        "pt": "INSTALADO",
        "ja": "インストール済み",
        "ko": "설치됨",
        "zh-CN": "已安装",
        "ar": "مثبت",
        "hi": "स्थापित",
    }
    return texts.get(lang, "INSTALLED")


def translate_text(text, target_lang):
    """Google Translate bepul endpoint orqali tarjima (kesh bilan)."""
    if not text or target_lang == "en":
        return text
    # Avval qo'lda kiritilgan tarjimani tekshiramiz
    mt = manual_translate(text, target_lang)
    if mt is not None:
        return mt
    ck = f"{target_lang}::{text}"
    if ck in _TRANS_CACHE:
        return _TRANS_CACHE[ck]
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
        r = SESSION.get(url, params=params, timeout=5)
        if r.status_code != 200:
            _TRANS_CACHE[ck] = text
            return text
        data = r.json()
        if not data or not data[0]:
            _TRANS_CACHE[ck] = text
            return text
        parts = []
        for part in data[0]:
            if part and part[0]:
                parts.append(part[0])
        result = "".join(parts)
        if result:
            _TRANS_CACHE[ck] = result
            return result
    except Exception:
        pass
    _TRANS_CACHE[ck] = text
    return text



def detect_system_lang():
    try:
        from locale import getdefaultlocale
        loc = getdefaultlocale()[0] or "en"
        c = loc.split("_")[0].lower()
        return c if c else "en"
    except Exception:
        return "en"

class TransDict:
    """Dinamik tarjima qiluvchi dict."""

    def __init__(self, base):
        self._base = base
        self._cache = {}
        self._lang = "en"

    def set_language(self, lang):
        if lang == "auto":
            lang = detect_system_lang()
        # Agar til o'zgarmagan bo'lsa — hech narsa qilmaymiz
        if lang == self._lang and self._cache:
            return
        self._lang = lang
        self._cache.clear()
        # MUHIM: global keshni ham tozalaymiz
        _TRANS_CACHE.clear()

    def get_language(self):
        return self._lang

    def __getitem__(self, key):
        return self._get(key)

    def get(self, key, default=None):
        if key in self._base:
            return self._get(key)
        return default if default is not None else key

    def _get(self, key):
        text = self._base.get(key, key)
        if self._lang == "en":
            return text
        ck = f"{self._lang}:{key}"
        if ck in self._cache:
            return self._cache[ck]
        tr = translate_text(text, self._lang)
        self._cache[ck] = tr
        return tr



T = TransDict(TR["en"])


# ==================== Platform-specific paths ====================
if sys.platform == "win32":
    # Windows: %LOCALAPPDATA%\uzAlhaithamWallpaper
    _APP_DATA = Path(os.environ.get("LOCALAPPDATA",
                                    Path.home() / "AppData" / "Local"))
    _CONFIG_DIR = _APP_DATA / "uzAlhaithamWallpaper"
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE = _CONFIG_DIR / "config.json"
    CURRENT_WALLPAPER_DIR = _CONFIG_DIR / "cache"
    DEFAULT_DL_FOLDER = Path.home() / "Pictures" / "Wallpapers"
elif sys.platform == "darwin":
    # macOS: ~/Library/Application Support
    _CONFIG_DIR = Path.home() / "Library" / "Application Support" / "uzAlhaithamWallpaper"
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE = _CONFIG_DIR / "config.json"
    CURRENT_WALLPAPER_DIR = _CONFIG_DIR / "cache"
    DEFAULT_DL_FOLDER = Path.home() / "Pictures" / "Wallpapers"
else:
    # Linux (host yoki Flatpak)
    CONFIG_FILE = Path.home() / ".uzalhaitham_wallpaper.json"
    CURRENT_WALLPAPER_DIR = Path.home() / ".cache" / "uzAlhaithamWallpaper"
    DEFAULT_DL_FOLDER = Path.home() / "Wallpapers"

CURRENT_WALLPAPER_FILE = CURRENT_WALLPAPER_DIR / "current_wallpaper"
CURRENT_WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
# Windows fon rasmi webp'ni qo'llamaydi
if sys.platform == "win32":
    SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
else:
    SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search"
THUMB_PX = 320
THUMB_WORKERS = 8

_API_KEY = ""

def get_api_key():
    return _API_KEY

def set_api_key(k):
    global _API_KEY
    _API_KEY = (k or "").strip()

def set_wallpaper(image_path):
    image_path = str(Path(image_path).resolve())
    if not os.path.isfile(image_path):
        return False
    if sys.platform == "win32":
        return _win(image_path)
    return _linux(image_path)

def _win(image_path):
    import ctypes
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
    except Exception:
        pass
    return bool(ctypes.windll.user32.SystemParametersInfoW(
        20, 0, image_path, 0x01 | 0x02))

def _linux(image_path):
    """KDE/GNOME/XFCE/Sway — wallpaper o'rnatish."""
    # KDE Plasma 6 — eng ishonchli usul
    for tool in ("plasma-apply-wallpaperimage",
                 "/usr/lib/plasma-apply-wallpaperimage",
                 "/usr/lib64/plasma-apply-wallpaperimage"):
        if shutil.which(tool) or Path(tool).exists():
            try:
                r = run_cmd([tool, image_path],
                                   capture_output=True, text=True, timeout=15)
                print(f"[wallpaper] {tool}: rc={r.returncode}")
                if r.returncode == 0:
                    print(f"[wallpaper] set via {tool}")
                    return True
                print(f"[wallpaper] stderr: {r.stderr}")
            except Exception as e:
                print(f"[wallpaper] {tool}: {e}")

    # KDE Plasma 5 — qdbus
    for dbus in ("qdbus6", "qdbus"):
        if shutil.which(dbus):
            # Plasma 5 uchun
            script = (
                'var ds = desktops();'
                'for (var i=0; i<ds.length; i++) {'
                '  ds[i].wallpaperPlugin = "org.kde.image";'
                '  ds[i].currentConfigGroup = '
                '    Array("Wallpaper","org.kde.image","General");'
                f'  ds[i].writeConfig("Image","file://{image_path}");'
                '}'
            )
            try:
                r = run_cmd(
                    [dbus, "org.kde.plasmashell", "/PlasmaShell",
                     "org.kde.PlasmaShell.evaluateScript", script],
                    capture_output=True, text=True, timeout=10)
                if r.returncode == 0 and "Error" not in r.stdout:
                    print(f"[wallpaper] set via {dbus}")
                    return True
            except Exception:
                pass

    # GNOME
    if shutil.which("gsettings"):
        try:
            run_cmd(["gsettings", "set",
                            "org.gnome.desktop.background",
                            "picture-uri", f"file://{image_path}"], check=True)
            run_cmd(["gsettings", "set",
                            "org.gnome.desktop.background",
                            "picture-uri-dark",
                            f"file://{image_path}"], check=True)
            print("[wallpaper] set via gsettings")
            return True
        except Exception as e:
            print(f"[wallpaper] gsettings: {e}")

    # XFCE
    if shutil.which("xfconf-query"):
        try:
            run_cmd(["xfconf-query", "-c", "xfce4-desktop",
                            "-p",
                            "/backdrop/screen0/monitor0/workspace0/last-image",
                            "-s", image_path], check=True)
            print("[wallpaper] set via xfconf-query")
            return True
        except Exception as e:
            print(f"[wallpaper] xfconf: {e}")

    # Sway
    if shutil.which("swaymsg"):
        try:
            run_cmd(["swaymsg", "output", "*", "bg",
                            image_path, "fill"], check=True)
            return True
        except Exception:
            pass

    print("[wallpaper] no supported backend")
    return False



class WallhavenWorker(QThread):
    finished = pyqtSignal(list, int)
    error = pyqtSignal(str)

    def __init__(self, query, categories, purity, sorting, page=1,
                 api_key=""):
        super().__init__()
        self.query = query
        self.categories = categories
        self.purity = purity
        self.sorting = sorting
        self.page = page
        self.api_key = api_key

    def run(self):
        try:
            params = {"q": self.query, "categories": self.categories,
                      "purity": self.purity, "sorting": self.sorting,
                      "page": self.page}
            if self.api_key:
                params["apikey"] = self.api_key
            r = SESSION.get(WALLHAVEN_API, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = [{"id": w.get("id"), "url": w.get("path"),
                      "thumb": (w.get("thumbs", {}).get("small")
                                or w.get("thumbs", {}).get("original")),
                      "resolution": w.get("resolution")}
                     for w in data.get("data", [])]
            meta = data.get("meta", {})
            last_page = int(meta.get("last_page", self.page))
            self.finished.emit(items, last_page)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QThread):
    progress = pyqtSignal(str, int, int)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str, str)
    state = pyqtSignal(str, str)

    def __init__(self, wid, url, folder, filename):
        super().__init__()
        self.wid = wid
        self.url = url
        self.folder = Path(folder)
        self.filename = filename
        self._pause = threading.Event()
        self._pause.set()
        self._cancel = False
        self._last_pct = 0

    def pause(self):
        self._pause.clear()
        self.state.emit(self.wid, "paused")

    def resume(self):
        self._pause.set()
        self.state.emit(self.wid, "downloading")

    def cancel(self):
        self._cancel = True
        self._pause.set()

    def run(self):
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            out = self.folder / self.filename
            if out.exists():
                out.unlink()
            r = SESSION.get(self.url, stream=True, timeout=60)
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            got = 0
            self.state.emit(self.wid, "downloading")
            with open(out, "wb") as f:
                for chunk in r.iter_content(262144):
                    if self._cancel:
                        r.close()
                        try:
                            out.unlink()
                        except Exception:
                            pass
                        self.state.emit(self.wid, "cancelled")
                        return
                    self._pause.wait()
                    if self._cancel:
                        r.close()
                        try:
                            out.unlink()
                        except Exception:
                            pass
                        self.state.emit(self.wid, "cancelled")
                        return
                    f.write(chunk)
                    got += len(chunk)
                    self.progress.emit(self.wid, got, total)
            self.finished.emit(self.wid, str(out))
            self.state.emit(self.wid, "done")
        except Exception as e:
            self.state.emit(self.wid, "error")
            self.error.emit(self.wid, str(e))

class ThumbLoaderPool(QThread):
    loaded = pyqtSignal(str, QImage)

    def __init__(self, items, size=THUMB_PX, workers=THUMB_WORKERS):
        super().__init__()
        self.items = items
        self.size = size
        self.workers = workers
        self._stop = False

    def stop(self):
        self._stop = True

    def _fetch(self, wid, url):
        if self._stop:
            return wid, None
        try:
            if url.startswith("http"):
                r = SESSION.get(url, timeout=10)
                if r.status_code != 200:
                    return wid, None
                img = QImage()
                img.loadFromData(r.content)
            else:
                img = QImage(url)
            if self._stop or img.isNull():
                return wid, None
            img = img.scaled(self.size, self.size,
                             Qt.KeepAspectRatioByExpanding,
                             Qt.SmoothTransformation)
            return wid, img
        except Exception:
            return wid, None

    def run(self):
        try:
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futures = [ex.submit(self._fetch, wid, url)
                           for wid, url in self.items]
                for fut in as_completed(futures):
                    if self._stop:
                        break
                    try:
                        wid, img = fut.result()
                        if img is not None:
                            self.loaded.emit(wid, img)
                    except Exception:
                        pass
        except Exception:
            pass

class FullImageWorker(QThread):
    loaded = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, item, cache=None):
        super().__init__()
        self.item = item
        self.cache = cache
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        if self._stop:
            return
        try:
            wid = self.item["id"]
            if self.cache is not None and wid in self.cache:
                img = self.cache[wid]
                if not self._stop:
                    self.loaded.emit(img)
                return
            if self.item.get("_local"):
                img = QImage(self.item["_path"])
            else:
                r = SESSION.get(self.item["url"], timeout=20)
                img = QImage()
                img.loadFromData(r.content)
            if self._stop:
                return
            if not img.isNull():
                self.loaded.emit(img)
            else:
                self.error.emit("Yuklab bo'lmadi")
        except Exception as e:
            if not self._stop:
                self.error.emit(str(e))

class WallpaperCard(QFrame):
    clicked = pyqtSignal(str)
    download_clicked = pyqtSignal(str, bool)
    set_bg_clicked = pyqtSignal(str)
    remove_clicked = pyqtSignal(str)

    HOVER_BAR_H = 48
    ZOOM = 1.04

    def __init__(self, item, is_downloaded=False, is_current=False,
                 card_size=(320, 180), initial_pixmap=None):
        super().__init__()
        self.item = item
        self.wid = item["id"]
        self.is_downloaded = is_downloaded
        self.is_current = is_current
        self._pixmap = None
        self._cache_key = None
        self._cached = None
        self._zoom = 1.0
        self._dl_state = "idle"
        self._dl_pct = 0

        self.setFixedSize(*card_size)
        self.setStyleSheet(
            "WallpaperCard { background:#2b2b2b; border-radius:10px; }")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        # Rasm
        self.img_label = QLabel(self)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet(
            "background:#1e1e1e; border-radius:10px; color:#666;")
        self.img_label.setText("\u23f3")
        self.img_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Hover bar (pastda)
        self.hover_bar = QWidget(self)
        self.hover_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(20,20,20,0.05),
                stop:0.5 rgba(15,15,15,0.35),
                stop:1 rgba(10,10,10,0.78));
            border-bottom-left-radius:10px;
            border-bottom-right-radius:10px;
        """)
        hb = QHBoxLayout(self.hover_bar)
        hb.setContentsMargins(8, 4, 8, 6)
        hb.setSpacing(8)
        hb.addStretch()

        # Markaziy tugma / badge
        self.btn_action = None
        self.installed_badge = None
        if is_current:
            # INSTALLED badge (yashil/sariq)
            self.installed_badge = QLabel(
                get_installed_badge_text())
            self.installed_badge.setAlignment(Qt.AlignCenter)
            self.installed_badge.setFixedHeight(30)
            self.installed_badge.setStyleSheet("""
                QLabel {
                    background: rgba(255,180,40,0.95);
                    color: #000;
                    border: 1px solid #ffffff;
                    border-radius: 11px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0 16px;
                    letter-spacing: 1px;
                }
            """)
            hb.addWidget(self.installed_badge)
        elif is_downloaded:
            self.btn_action = QPushButton(T["set_bg"])
            self.btn_action.clicked.connect(
                lambda: self.set_bg_clicked.emit(self.wid))
            self._style_green(self.btn_action)
            hb.addWidget(self.btn_action)
        else:
            self.btn_action = QPushButton(T["btn_download"])
            self.btn_action.clicked.connect(
                lambda: self.download_clicked.emit(self.wid, False))
            self._style_primary(self.btn_action)
            hb.addWidget(self.btn_action)



        hb.addStretch()
        self.hover_bar.hide()

        # Status badge (yuqori chapda) — yuklab olish jarayoni
        self.status_badge = QLabel("", self)
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(22)
        self.status_badge.setMinimumWidth(22)
        self.status_badge.setStyleSheet(
            "background: rgba(0,0,0,0.7); color:#fff;"
            "border-radius:11px; font-weight:bold; font-size:11px;"
            "padding:0 8px;")
        self.status_badge.hide()
        self._update_badge()

        # X (o'chirish) tugmasi — faqat yuklangan
        self.remove_btn = QPushButton("\u2715", self)
        self.remove_btn.setFixedSize(24, 24)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setToolTip(
            T.get("tip_remove", "Remove this image from disk"))
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background: rgba(220,60,60,0.85);
                color: #fff;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover { background: rgba(240,70,70,1.0); }
        """)
        self.remove_btn.clicked.connect(
            lambda: self.remove_clicked.emit(self.wid))
        if is_downloaded:
            self.remove_btn.show()
            self.remove_btn.raise_()
        else:
            self.remove_btn.hide()

        if initial_pixmap is not None and not initial_pixmap.isNull():
            self.set_pixmap(initial_pixmap)
        self._reposition_badges()

    def showEvent(self, e):
        super().showEvent(e)
        self._reposition_badges()

    def contextMenuEvent(self, e):
        """O'ng tugma bosilganda menyu."""
        menu = QMenu(self)
        # Save as
        act_save = QAction(
            T.get("btn_save_as", "Save as …"), self)
        act_save.triggered.connect(self._ctx_save_as)
        menu.addAction(act_save)
        # Set as wallpaper (agar yuklangan bo'lsa)
        if self.is_downloaded:
            act_set = QAction(T["set_bg"], self)
            act_set.triggered.connect(
                lambda: self.set_bg_clicked.emit(self.wid))
            menu.addAction(act_set)
        # Download (agar yuklanmagan bo'lsa)
        else:
            act_dl = QAction(T["btn_download"], self)
            act_dl.triggered.connect(
                lambda: self.download_clicked.emit(self.wid, False))
            menu.addAction(act_dl)
        # Remove (agar yuklangan bo'lsa)
        if self.is_downloaded:
            menu.addSeparator()
            act_rm = QAction(
                "🗑 " + T.get("tip_remove", "Remove"), self)
            act_rm.triggered.connect(
                lambda: self.remove_clicked.emit(self.wid))
            menu.addAction(act_rm)
        # Ko'rsatish
        menu.exec_(e.globalPos())

    def _ctx_save_as(self):
        self.download_clicked.emit(self.wid, True)

    def _style_primary(self, b):
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(30)
        b.setMinimumWidth(100)
        b.setStyleSheet("""
            QPushButton { background: rgba(90,159,212,0.95); color:#fff;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 0 18px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background: rgba(107,175,228,1.0); }
        """)

    def _style_secondary(self, b):
        b.setCursor(Qt.PointingHandCursor)
        b.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.15); color:#fff;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 0 12px; font-size: 12px; }
            QPushButton:hover { background: rgba(255,255,255,0.28); }
        """)

    def _style_green(self, b):
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(30)
        b.setMinimumWidth(150)
        b.setStyleSheet("""
            QPushButton { background: rgba(80,200,120,0.9); color:#fff;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 0 16px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background: rgba(90,220,140,1.0); }
        """)

    def set_current(self, is_current):
        """INSTALLED badge ga o'tish yoki orqaga qaytarish."""
        if self.is_current == is_current:
            return
        self.is_current = is_current
        try:
            hb = self.hover_bar.layout()
            # Eski widgetning o'rnini eslab qolamiz
            old_idx = -1
            if self.btn_action is not None:
                old_idx = hb.indexOf(self.btn_action)
                self.btn_action.setParent(None)
                self.btn_action.deleteLater()
                self.btn_action = None
            if self.installed_badge is not None:
                old_idx = hb.indexOf(self.installed_badge)
                self.installed_badge.setParent(None)
                self.installed_badge.deleteLater()
                self.installed_badge = None

            if old_idx < 0:
                # Fallback: o'rtaga qo'yamiz (stretch lardan keyin)
                old_idx = 1

            # Yangi widgetni qo'shamiz
            if is_current:
                self.installed_badge = QLabel(
                    get_installed_badge_text())
                self.installed_badge.setAlignment(Qt.AlignCenter)
                self.installed_badge.setMinimumHeight(30)
                self.installed_badge.setSizePolicy(
                    QSizePolicy.Preferred, QSizePolicy.Fixed)
                self.installed_badge.setStyleSheet("""
                    QLabel {
                        background: rgba(255,180,40,0.95);
                        color: #000;
                        border: 1px solid #ffffff;
                        border-radius: 11px;
                        font-weight: bold;
                        font-size: 12px;
                        padding: 6px 20px;
                    }
                """)
                hb.insertWidget(old_idx, self.installed_badge)
            else:
                if self.is_downloaded:
                    self.btn_action = QPushButton(T["set_bg"])
                    self.btn_action.clicked.connect(
                        lambda: self.set_bg_clicked.emit(self.wid))
                    self._style_green(self.btn_action)
                else:
                    self.btn_action = QPushButton(T["btn_download"])
                    self.btn_action.clicked.connect(
                        lambda: self.download_clicked.emit(self.wid, False))
                    self._style_primary(self.btn_action)
                hb.insertWidget(old_idx, self.btn_action)
        except Exception as e:
            print("set_current:", e)


    def _reposition_badges(self):
        w = self.width()
        if self.remove_btn.isVisible():
            self.remove_btn.move(w - 24 - 6, 6)

    def set_pixmap(self, img: QImage):
        if img is None or img.isNull():
            return
        self._pixmap = QPixmap.fromImage(img)
        self._cache_key = None
        self._render()

    def _render(self):
        if self._pixmap is None:
            return
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
        key = (w, h, self._zoom)
        if self._cache_key == key and self._cached is not None:
            self.img_label.setPixmap(self._cached)
            return
        self._cache_key = key
        z = self._zoom
        sw, sh = int(w * z), int(h * z)
        scaled = self._pixmap.scaled(sw, sh, Qt.KeepAspectRatioByExpanding,
                                     Qt.SmoothTransformation)
        x = (scaled.width() - w) // 2
        y = (scaled.height() - h) // 2
        cropped = scaled.copy(x, y, w, h)
        rounded = QPixmap(w, h)
        rounded.fill(Qt.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(cropped))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, 10, 10)
        p.end()
        self._cached = rounded
        self.img_label.setPixmap(rounded)
        self.img_label.setText("")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = self.width(), self.height()
        self.img_label.setGeometry(0, 0, w, h)
        self.hover_bar.setGeometry(0, h - self.HOVER_BAR_H, w, self.HOVER_BAR_H)
        self.status_badge.move(6, 6)
        self._reposition_badges()
        self._cache_key = None
        self._render()

    def enterEvent(self, e):
        self._zoom = self.ZOOM
        self._cache_key = None
        self._render()
        self.hover_bar.show()
        self.hover_bar.raise_()
        if self.remove_btn.isVisible():
            self.remove_btn.raise_()

    def leaveEvent(self, e):
        self._zoom = 1.0
        self._cache_key = None
        self._render()
        self.hover_bar.hide()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            pos = e.pos()
            if self.hover_bar.geometry().contains(pos):
                return
            if self.remove_btn.isVisible() and \
                    self.remove_btn.geometry().contains(pos):
                return
            self.clicked.emit(self.wid)

    def set_download_state(self, state, pct=0):
        self._dl_state = state
        self._dl_pct = pct
        self._update_badge()

    def _update_badge(self):
        s = self._dl_state
        if s == "downloading":
            self.status_badge.setText(f"\u2b07 {self._dl_pct}%")
            self.status_badge.setStyleSheet(
                "background: rgba(90,159,212,0.95); color:#fff;"
                "border-radius:11px; font-weight:bold; font-size:11px;"
                "padding:0 8px;")
            self.status_badge.show()
            self.status_badge.adjustSize()
            self.status_badge.setFixedHeight(22)
        elif s == "paused":
            self.status_badge.setText(f"\u23f8 {self._dl_pct}%")
            self.status_badge.setStyleSheet(
                "background: rgba(230,150,40,0.95); color:#fff;"
                "border-radius:11px; font-weight:bold; font-size:11px;"
                "padding:0 8px;")
            self.status_badge.show()
            self.status_badge.adjustSize()
            self.status_badge.setFixedHeight(22)
        elif s == "done":
            self.status_badge.setText("\u2713")
            self.status_badge.setStyleSheet(
                "background: rgba(80,200,120,0.95); color:#fff;"
                "border-radius:11px; font-weight:bold; font-size:12px;"
                "padding:0 6px;")
            self.status_badge.show()
            self.status_badge.setFixedSize(22, 22)
        elif s == "error":
            self.status_badge.setText("!")
            self.status_badge.setStyleSheet(
                "background: rgba(220,80,80,0.95); color:#fff;"
                "border-radius:11px; font-weight:bold; font-size:12px;"
                "padding:0 6px;")
            self.status_badge.show()
            self.status_badge.setFixedSize(22, 22)
        else:
            self.status_badge.hide()



class NsfwConfirmBar(QWidget):
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "background: rgba(200,80,80,0.15); border-radius: 6px;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 3, 10, 3)
        lay.setSpacing(10)

        self.lbl = QLabel(T.get("nsfw_countdown", "⚠  Enabling NSFW in {}...").format(3))
        self.lbl.setStyleSheet(
            "color: #ff9090; font-weight: bold; font-size: 11px;")
        lay.addWidget(self.lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 30)
        self.bar.setValue(30)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)
        self.bar.setStyleSheet("""
            QProgressBar { background: #3a3a3a; border-radius: 2px; }
            QProgressBar::chunk { background: #e05050; border-radius: 2px; }
        """)
        lay.addWidget(self.bar, stretch=1)

        self.btn_cancel = QPushButton(T["cancel"])
        self.btn_cancel.setFixedHeight(24)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton { background: #3a3a3a; color: #ddd;
                border: 1px solid #ffffff; border-radius: 6px;
                padding: 4px 14px; font-size: 11px; }
            QPushButton:hover { background: #4a4a4a;
                border: 1px solid #5a9fd4; }
        """)
        self.btn_cancel.clicked.connect(self._on_cancel)
        lay.addWidget(self.btn_cancel)

        self._t = 30
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def _on_cancel(self):
        self.timer.stop()
        self.hide()
        self.cancelled.emit()

    def start(self):
        self._t = 30
        self.bar.setValue(30)
        self.lbl.setText(T.get("nsfw_countdown", "⚠  Enabling NSFW in {}...").format(3))
        self.timer.start(100)
        self.show()

    def _tick(self):
        self._t -= 1
        self.bar.setValue(self._t)
        secs = max(1, (self._t + 9) // 10)
        self.lbl.setText(T.get("nsfw_countdown", "⚠  Enabling NSFW in {}...").format(secs))
        if self._t <= 0:
            self.timer.stop()
            self.hide()
            self.confirmed.emit()

    def stop(self):
        self.timer.stop()
        self.hide()


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None, current=""):
        super().__init__(parent)
        self.setWindowTitle("Wallhaven API Key")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet("""
            QDialog { background:#1e1e1e; color:#e0e0e0; }
            QLabel { color:#e0e0e0; }
            QLineEdit { background:#252525; color:#e0e0e0;
                border:1px solid #3d3d3d; border-radius: 11px;
                padding:8px 12px; }
            QLineEdit:focus { border:1px solid #5a9fd4; }
            QPushButton { background:#2b2b2b; color:#e0e0e0;
                border:1px solid #3d3d3d; border-radius: 11px;
                padding:7px 14px; }
            QPushButton:hover { background:#3a3a3a;
                border:1px solid #5a9fd4; }
            QPushButton#primary { background:#5a9fd4; color:#fff;
                border:none; font-weight:bold; }
            QPushButton#primary:hover { background:#6bafe4; }
        """)
        self.api_key = ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)
        info = QLabel("NSFW requires a Wallhaven API key.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#bbb;")
        lay.addWidget(info)
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("API Key:"))
        self.input = QLineEdit()
        self.input.setPlaceholderText("Paste API key...")
        self.input.setText(current or "")
        self.input.setMinimumHeight(36)
        row.addWidget(self.input, stretch=1)
        btn_get = QPushButton(T["btn_get_api"])
        btn_get.setCursor(Qt.PointingHandCursor)
        btn_get.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://wallhaven.cc/settings/account")))
        row.addWidget(btn_get)
        lay.addLayout(row)
        btns = QHBoxLayout()
        btns.addStretch()
        bc = QPushButton(T["cancel"])
        bc.clicked.connect(self.reject)
        btns.addWidget(bc)
        bo = QPushButton(T["btn_ok"])
        bo.setObjectName("primary")
        bo.setCursor(Qt.PointingHandCursor)
        bo.clicked.connect(self._ok)
        btns.addWidget(bo)
        lay.addLayout(btns)

    def _ok(self):
        k = self.input.text().strip()
        if not k:
            QMessageBox.warning(self, T.get("error_title", "Error"), "API key is required")
            return
        self.api_key = k
        self.accept()

class ImageViewer(QDialog):
    def __init__(self, items, index, parent, is_downloaded_func,
                 do_download_func, set_bg_func, thumb_cache=None):
        super().__init__(None)
        self._main_window = parent  # MainWindow reference
        self.items = items
        self.index = index
        self.is_downloaded_func = is_downloaded_func
        self.do_download_func = do_download_func
        self.set_bg_func = set_bg_func
        self.thumb_cache = thumb_cache or {}
        self._pix = None
        self._worker = None
        self._drag_pos = None
        self._fullscreen = False
        self._aspect = None
        self._resizing = False
        self._resize_edge = None
        self._resize_start = None
        self._RESIZE_MARGIN = 8

        self.setWindowTitle("uzAlhaitham's wallpaper Selector")
        # Frameless
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # 90% ekran
        screen = QApplication.primaryScreen().availableGeometry()
        w = int(screen.width() * 0.9)
        h = int(screen.height() * 0.9)
        self.resize(w, h)
        self.move(screen.x() + (screen.width() - w) // 2,
                  screen.y() + (screen.height() - h) // 2)

        self.setStyleSheet("background:#0d0d0d;")

        # Rasm
        self.img_label = QLabel(self)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background:#0d0d0d; color:#888; "
                                     "font-size: 14px;")
        self.img_label.setText(T.get("loading", "Loading..."))
        self.img_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Top-right overlay (fullscreen + close)
        self.top_bar = QWidget(self)
        self.top_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        self.top_bar.setAttribute(Qt.WA_NoSystemBackground, True)
        self.top_bar.setStyleSheet("background: transparent; border: none;")
        tb_lay = QHBoxLayout(self.top_bar)
        tb_lay.setContentsMargins(0, 0, 0, 0)
        tb_lay.setSpacing(6)

        self.btn_fs = self._mk_top_btn("⛶")
        self.btn_fs.setToolTip("Fullscreen (F11)")
        self.btn_fs.clicked.connect(self._toggle_fs)
        tb_lay.addWidget(self.btn_fs)

        self.btn_close = self._mk_top_btn("✕", danger=True)
        self.btn_close.setToolTip("Close (Esc)")
        self.btn_close.clicked.connect(self.close)
        tb_lay.addWidget(self.btn_close)

        self.top_bar.adjustSize()

        # Bottom bar (prev/action/next + close)
        self.bar = QWidget(self)
        self.bar.setAttribute(Qt.WA_TranslucentBackground, True)
        self.bar.setAttribute(Qt.WA_NoSystemBackground, True)
        self.bar.setStyleSheet("background: transparent; border: none;")
        bar_lay = QVBoxLayout(self.bar)
        bar_lay.setContentsMargins(0, 0, 0, 0)
        bar_lay.setSpacing(6)

        row1 = QHBoxLayout()
        row1.addStretch()
        self.btn_prev = self._mk_btn("◀")
        self.btn_prev.clicked.connect(self.prev)
        row1.addWidget(self.btn_prev)
        self.btn_action = self._mk_btn("⬇ Download", primary=True)
        self.btn_action.clicked.connect(self.action)
        row1.addWidget(self.btn_action)
        self.btn_next = self._mk_btn("▶")
        self.btn_next.clicked.connect(self.next)
        row1.addWidget(self.btn_next)
        row1.addStretch()
        bar_lay.addLayout(row1)

        self.bar.adjustSize()

        # Shortcuts
        QShortcut(QKeySequence(Qt.Key_Left), self, self.prev)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.next)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fs)

        # Hover detection
        self.setMouseTracking(True)
        self.img_label.setMouseTracking(True)
        self.top_bar.setMouseTracking(True)
        self.bar.setMouseTracking(True)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._maybe_hide_ui)
        self.installEventFilter(self)
        self.img_label.installEventFilter(self)
        self.top_bar.installEventFilter(self)
        self.bar.installEventFilter(self)

        self._load()

    def _mk_top_btn(self, text, danger=False):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedSize(34, 34)
        if danger:
            b.setStyleSheet("""
                QPushButton { background: rgba(200,60,60,0.85);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; font-size: 15px;
                    font-weight: bold; padding: 0; }
                QPushButton:hover { background: rgba(230,70,70,1.0); }
            """)
        else:
            b.setStyleSheet("""
                QPushButton { background: rgba(35,35,35,0.85);
                    color:#e8e8e8; border:1px solid #ffffff;
                    border-radius: 11px; font-size: 15px; padding: 0; }
                QPushButton:hover { background: rgba(55,55,55,1.0); }
            """)
        return b

    def _mk_btn(self, text, primary=False, danger=False):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(34)
        b.setMinimumWidth(44)
        if primary:
            b.setStyleSheet("""
                QPushButton { background: rgba(90,159,212,0.95);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 20px;
                    font-weight: bold; font-size: 13px; }
                QPushButton:hover { background: rgba(107,175,228,1.0); }
            """)
        elif danger:
            b.setStyleSheet("""
                QPushButton { background: rgba(200,60,60,0.85);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 20px;
                    font-weight: bold; font-size: 13px; }
                QPushButton:hover { background: rgba(230,70,70,1.0); }
            """)
        else:
            b.setStyleSheet("""
                QPushButton { background: rgba(35,35,35,0.9);
                    color:#e8e8e8; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 16px;
                    font-size: 14px; }
                QPushButton:hover { background: rgba(55,55,55,1.0); }
            """)
        return b

    def _stop_worker(self):
        if self._worker is not None:
            try:
                self._worker.loaded.disconnect()
                self._worker.error.disconnect()
            except Exception:
                pass
            self._worker.stop()
            self._worker = None

    def _load(self):
        item = self.items[self.index]
        self.img_label.setPixmap(QPixmap())
        self.img_label.setText(T.get("loading", "Loading..."))
        self._update_button()

        self._stop_worker()
        self._worker = FullImageWorker(item, cache=None)
        self._worker.loaded.connect(self._on_full_loaded)
        self._worker.error.connect(self._on_full_error)
        self._worker.start()

    def _on_full_loaded(self, img: QImage):
        if img is None or img.isNull():
            return
        self._pix = img
        # Aspect ratio ni o'rnatamiz va oynani moslashtiramiz
        if img.height() > 0:
            self._aspect = img.width() / img.height()
        self._apply_aspect_once()
        self._update()

    def _apply_aspect_once(self):
        """Oynani rasm proporsiyasiga moslashtiradi (bir marta)."""
        if not hasattr(self, "_aspect") or self._aspect is None:
            return
        screen = QApplication.primaryScreen().availableGeometry()
        max_w = int(screen.width() * 0.9)
        max_h = int(screen.height() * 0.9)
        # Ekran o'lchamiga sig'adigan maksimal aspect
        w = max_w
        h = int(w / self._aspect)
        if h > max_h:
            h = max_h
            w = int(h * self._aspect)
        if w < 300:
            w = 300
            h = int(w / self._aspect)
        self._resizing = True
        self.resize(w, h)
        self.move(screen.x() + (screen.width() - w) // 2,
                  screen.y() + (screen.height() - h) // 2)
        self._resizing = False

    def _on_full_error(self, msg):
        self.img_label.setText(f"⚠ {msg}")

    def _update_button(self):
        wid = self.items[self.index]["id"]
        path = self.is_downloaded_func(wid)

        # Current wallpaper tekshiruvi (MainWindow orqali)
        is_current = False
        try:
            pw = self._main_window
            if pw is not None:
                cur = getattr(pw, "current_wallpaper_id", None)
                if cur:
                    norm_wid = wid.replace("wallhaven-", "")
                    norm_cur = cur.replace("wallhaven-", "")
                    is_current = (norm_wid == norm_cur)
        except Exception as e:
            print(f"[iv check] {e}")

        print(f"[iv update] wid={wid} path={bool(path)} "
              f"is_current={is_current}")

        try:
            self.btn_action.clicked.disconnect()
        except TypeError:
            pass

        if is_current:
            self.btn_action.setText(
                chr(0x2713) + " " + get_installed_badge_text())
            self.btn_action.setStyleSheet("""
                QPushButton { background: rgba(255,180,40,0.95);
                    color:#000; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 24px;
                    font-weight: bold; font-size: 12px;
                    letter-spacing: 0.5px; }
                QPushButton:hover { background: rgba(255,200,80,1.0); }
            """)
            self.btn_action.clicked.connect(self.set_bg)
        elif path:
            self.btn_action.setText(T["set_bg"])
            self.btn_action.setStyleSheet("""
                QPushButton { background: rgba(80,200,120,0.95);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 24px;
                    font-weight: bold; font-size: 12px;
                    }
                QPushButton:hover { background: rgba(90,220,140,1.0); }
            """)
            self.btn_action.clicked.connect(self.set_bg)
        else:
            self.btn_action.setText(T["btn_download"])
            self.btn_action.setStyleSheet("""
                QPushButton { background: rgba(90,159,212,0.95);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; padding: 0 24px;
                    font-weight: bold; font-size: 13px;
                    }
                QPushButton:hover { background: rgba(107,175,228,1.0); }
            """)
            self.btn_action.clicked.connect(self.action)
        self.bar.adjustSize()
        self._position_bars()


    def _update(self):
        if self._pix is None:
            return
        w, h = self.img_label.width(), self.img_label.height()
        if w < 10 or h < 10:
            return
        # To'liq qoplash (crop) — qora joy yo'q
        scaled = self._pix.scaled(w, h, Qt.KeepAspectRatioByExpanding,
                                  Qt.SmoothTransformation)
        # Markazdan crop
        x = (scaled.width() - w) // 2
        y = (scaled.height() - h) // 2
        cropped = scaled.copy(x, y, w, h)
        self.img_label.setPixmap(QPixmap.fromImage(cropped))

    def _position_bars(self):
        # Top bar — yuqori o'ng burchak
        self.top_bar.adjustSize()
        tbw = self.top_bar.width()
        self.top_bar.move(self.width() - tbw - 12, 12)

        # Bottom bar — pastda, markazda
        self.bar.adjustSize()
        bw = self.bar.width()
        bh = self.bar.height()
        x = (self.width() - bw) // 2
        y = self.height() - bh - 20
        self.bar.move(max(0, x), max(0, y))

        self.top_bar.raise_()
        self.bar.raise_()

    def _toggle_fs(self):
        if self.isFullScreen():
            self.showNormal()
            self._fullscreen = False
        else:
            self.showFullScreen()
            self._fullscreen = True

    def _show_ui(self):
        if self.top_bar.isHidden():
            self.top_bar.show()
        if self.bar.isHidden():
            self.bar.show()
        self.top_bar.raise_()
        self.bar.raise_()

    def _maybe_hide_ui(self):
        pos = QCursor.pos()
        # Top bar ustida?
        for w in (self.top_bar, self.bar):
            try:
                local = w.mapFromGlobal(pos)
                if w.rect().contains(local):
                    return
            except Exception:
                pass
        self.top_bar.hide()
        self.bar.hide()

    def _edge_at(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = self._RESIZE_MARGIN
        on_l = x < m
        on_r = x > w - m
        on_t = y < m
        on_b = y > h - m
        if on_t and on_l: return "tl"
        if on_t and on_r: return "tr"
        if on_b and on_l: return "bl"
        if on_b and on_r: return "br"
        if on_l: return "l"
        if on_r: return "r"
        if on_t: return "t"
        if on_b: return "b"
        return None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            edge = self._edge_at(e.pos())
            if edge:
                self._resize_edge = edge
                self._resize_start = (e.globalPos(),
                                       self.geometry())
                e.accept()
                return
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        self._show_ui()
        self._hide_timer.start(1500)

        # Resize holati
        if self._resize_edge and e.buttons() & Qt.LeftButton:
            self._perform_resize(e.globalPos())
            e.accept()
            return

        # Cursor yangilash
        if not (e.buttons() & Qt.LeftButton):
            edge = self._edge_at(e.pos())
            cursors = {
                "l": Qt.SizeHorCursor, "r": Qt.SizeHorCursor,
                "t": Qt.SizeVerCursor, "b": Qt.SizeVerCursor,
                "tl": Qt.SizeFDiagCursor, "br": Qt.SizeFDiagCursor,
                "tr": Qt.SizeBDiagCursor, "bl": Qt.SizeBDiagCursor,
            }
            if edge:
                self.setCursor(cursors[edge])
            else:
                self.unsetCursor()

        # Drag (move)
        if self._drag_pos is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)
            e.accept()

    def _perform_resize(self, global_pos):
        if not self._resize_start:
            return
        start_pos, start_geo = self._resize_start
        dx = global_pos.x() - start_pos.x()
        dy = global_pos.y() - start_pos.y()

        x0, y0 = start_geo.x(), start_geo.y()
        w0, h0 = start_geo.width(), start_geo.height()
        aspect = getattr(self, "_aspect", None)
        if aspect is None or aspect <= 0:
            aspect = w0 / max(h0, 1)

        MIN_W = 300
        edge = self._resize_edge

        # Anchor nuqtasi: qaysi burchak qimirlamaydi
        # l/t bo'lsa — pastki-o'ng anchor; r/b bo'lsa — yuqori-chap anchor
        anchor_right = "l" in edge
        anchor_bottom = "t" in edge

        # Yangi o'lchamni hisoblash
        if "l" in edge or "r" in edge:
            # Gorizontal tortish — asosiy
            new_w = w0 + dx if "r" in edge else w0 - dx
            new_w = max(MIN_W, new_w)
            new_h = int(new_w / aspect)
        elif "t" in edge or "b" in edge:
            # Vertikal tortish — asosiy
            new_h = h0 + dy if "b" in edge else h0 - dy
            new_h = max(int(MIN_W / aspect), new_h)
            new_w = int(new_h * aspect)
        else:
            # Burchak — dominant o'q
            if abs(dx) > abs(dy):
                new_w = w0 + dx if "r" in edge else w0 - dx
                new_w = max(MIN_W, new_w)
                new_h = int(new_w / aspect)
            else:
                new_h = h0 + dy if "b" in edge else h0 - dy
                new_h = max(int(MIN_W / aspect), new_h)
                new_w = int(new_h * aspect)

        # Anchor asosida x, y ni hisoblash
        if anchor_right:
            x = x0 + w0 - new_w
        else:
            x = x0
        if anchor_bottom:
            y = y0 + h0 - new_h
        else:
            y = y0

        self.setGeometry(int(x), int(y), int(new_w), int(new_h))

    def mouseReleaseEvent(self, e):
        self._drag_pos = None
        self._resize_edge = None
        self._resize_start = None
        self.unsetCursor()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            # Faqat tepa qismida (birinchi 60px) ishlasin
            if e.pos().y() <= 60:
                self._toggle_fs()
                e.accept()
                return
        super().mouseDoubleClickEvent(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.img_label.setGeometry(0, 0, self.width(), self.height())
        self._update()
        self._position_bars()

    def prev(self):
        if self.index > 0:
            self.index -= 1
            self._load()

    def next(self):
        if self.index < len(self.items) - 1:
            self.index += 1
            self._load()

    def save_as(self):
        item = self.items[self.index]
        self.do_download_func(item["id"], True)
        QTimer.singleShot(1500, self._update_button)

    def action(self):
        self.do_download_func(self.items[self.index]["id"])
        QTimer.singleShot(1500, self._update_button)

    def set_bg(self):
        wid = self.items[self.index]["id"]
        print(f"[iv set_bg] wid={wid}")
        # 1. Set qilish
        self.set_bg_func(wid)
        # 2. Parent ning current ni belgilash
        try:
            pw = self._main_window
            if pw is not None and hasattr(pw, "_mark_as_current"):
                pw._mark_as_current(wid)
        except Exception as e:
            print(f"[iv set_bg] mark err: {e}")
        # 3. Tugmani DARHOL INSTALLED ga
        check = chr(0x2713)
        self.btn_action.setText(
            check + " " + get_installed_badge_text())
        self.btn_action.setStyleSheet("""
            QPushButton { background: rgba(255,180,40,0.95);
                color:#000; border:1px solid #ffffff;
                border-radius: 11px; padding: 0 24px;
                font-weight: bold; font-size: 12px;
                letter-spacing: 0.5px; }
            QPushButton:hover { background: rgba(255,200,80,1.0); }
        """)
        try:
            self.btn_action.clicked.disconnect()
        except TypeError:
            pass
        self.btn_action.clicked.connect(self.set_bg)
        self.bar.adjustSize()
        self._position_bars()


    def closeEvent(self, e):
        self._stop_worker()
        super().closeEvent(e)

class ToggleButton(QPushButton):
    def __init__(self, text, tooltip=""):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
            self.setToolTipDuration(8000)
        self.setStyleSheet("""
            QPushButton {
                background: #252525; color: #aaa;
                border: 1px solid #ffffff;
                border-radius: 11px;
                padding: 5px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #2f2f2f; color: #ddd; }
            QPushButton:checked {
                background: #5a9fd4; color: #fff;
                border: 1px solid #ffffff;
                font-weight: bold;
            }
            QPushButton:checked:hover { background: #6bafe4; }
        """)

class DownloadsIndicator(QFrame):
    """Progress bar = butun background."""
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self._pct = 0
        self._total = 0
        self._completed = 0

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(10)

        self.icon = QLabel("📥")
        self.icon.setStyleSheet(
            "background: transparent; font-size: 14px;")
        lay.addWidget(self.icon)

        self.count = QLabel("0/0")
        self.count.setStyleSheet(
            "background: transparent; color: #e8e8e8; "
            "font-size: 12px; font-weight: bold;")
        lay.addWidget(self.count)

        lay.addStretch()

        # Doim ko'rinadi (bo'sh holatda ham joy egallaydi)
        self.setStyleSheet(self.styleSheet())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def set_card_width(self, w):
        self.setFixedWidth(int(w))

    def update_overall(self, total, completed):
        self._total = total
        self._completed = completed
        if total == 0:
            self._pct = 0
            self.count.setText("")
            self.update()
            return
        self._pct = int(completed * 100 / total) if total else 0
        self.count.setText(f"{completed}/{total}")
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        if w < 4 or h < 4:
            p.end()
            return

        from PyQt5.QtCore import QRectF
        rect = QRectF(0.5, 0.5, w - 1, h - 1)

        # 1. Asosiy fon (qora 90%)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(25, 25, 30, 230))
        p.drawRoundedRect(rect, 11, 11)

        # 2. Progress to'ldirish (yashil)
        if self._pct > 0:
            from PyQt5.QtGui import QPainterPath
            fill_w = (w - 1) * self._pct / 100.0
            if fill_w > 1:
                fill_rect = QRectF(0.5, 0.5, fill_w, h - 1)
                path = QPainterPath()
                path.addRoundedRect(rect, 11, 11)
                p.setClipPath(path)
                p.fillRect(fill_rect, QColor(76, 175, 80, 220))
                p.setClipping(False)

        # 3. Hover holati
        if self.underMouse():
            p.setBrush(QColor(255, 255, 255, 20))
            p.drawRoundedRect(rect, 11, 11)

        # 4. Border
        p.setPen(QColor(255, 255, 255, 200))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(rect, 11, 11)
        p.end()

class DownloadItemWidget(QFrame):
    pause_clicked = pyqtSignal(str)
    resume_clicked = pyqtSignal(str)
    remove_clicked = pyqtSignal(str)

    def __init__(self, wid, name, thumb_img=None):
        super().__init__()
        self.wid = wid
        self.state = "downloading"
        self._full_name = name
        self._pct = 0
        self._state_color = QColor(76, 175, 80, 220)  # yashil

        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(8)

        # Thumbnail
        self.thumb_lbl = QLabel()
        self.thumb_lbl.setFixedSize(46, 28)
        self.thumb_lbl.setStyleSheet(
            "background: rgba(0,0,0,0.5); border-radius: 4px; "
            "color: #666; font-size: 9px;")
        self.thumb_lbl.setAlignment(Qt.AlignCenter)
        self.thumb_lbl.setText("...")
        if thumb_img is not None:
            self._set_thumb(thumb_img)
        lay.addWidget(self.thumb_lbl)

        # Nom
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet(
            "color: #fff; font-size: 12px; background: transparent; "
            "font-weight: bold;")
        self.lbl_name.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Preferred)
        self.lbl_name.setToolTip(name)
        lay.addWidget(self.lbl_name, stretch=1)

        # Foiz
        self.lbl_pct = QLabel("0%")
        self.lbl_pct.setFixedWidth(44)
        self.lbl_pct.setStyleSheet(
            "color: #fff; font-size: 11px; background: transparent; "
            "font-weight: bold;")
        self.lbl_pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(self.lbl_pct)

        # Pause
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(24, 24)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet("""
            QPushButton { background: rgba(0,0,0,0.4); color:#fff;
                border: 1px solid #ffffff; border-radius: 11px;
                font-size: 11px; padding: 0; }
            QPushButton:hover { background: rgba(0,0,0,0.7); }
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)
        lay.addWidget(self.btn_pause)

        # X
        self.btn_x = QPushButton("✕")
        self.btn_x.setFixedSize(24, 24)
        self.btn_x.setCursor(Qt.PointingHandCursor)
        self.btn_x.setStyleSheet("""
            QPushButton { background: rgba(0,0,0,0.4); color:#fff;
                border: 1px solid #ffffff; border-radius: 11px;
                font-size: 11px; padding: 0; }
            QPushButton:hover { background: rgba(180,40,40,0.9); }
        """)
        self.btn_x.clicked.connect(
            lambda: self.remove_clicked.emit(self.wid))
        lay.addWidget(self.btn_x)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        if w < 4 or h < 4:
            p.end()
            return

        from PyQt5.QtCore import QRectF
        rect = QRectF(0.5, 0.5, w - 1, h - 1)

        # 1. Qora fon (background)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(25, 25, 30, 230))
        p.drawRoundedRect(rect, 11, 11)

        # 2. Progress to'ldirish (state rangida)
        if self._pct > 0:
            from PyQt5.QtGui import QPainterPath
            fill_w = (w - 1) * self._pct / 100.0
            if fill_w > 1:
                fill_rect = QRectF(0.5, 0.5, fill_w, h - 1)
                path = QPainterPath()
                path.addRoundedRect(rect, 11, 11)
                p.setClipPath(path)
                p.fillRect(fill_rect, self._state_color)
                p.setClipping(False)

        # 3. Border
        p.setPen(QColor(255, 255, 255, 200))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(rect, 11, 11)
        p.end()

    def _set_thumb(self, img: QImage):
        pix = QPixmap.fromImage(img)
        if pix.isNull():
            return
        w, h = self.thumb_lbl.width(), self.thumb_lbl.height()
        scaled = pix.scaled(w, h, Qt.KeepAspectRatioByExpanding,
                            Qt.SmoothTransformation)
        x = (scaled.width() - w) // 2
        y = (scaled.height() - h) // 2
        cropped = scaled.copy(x, y, w, h)
        rounded = QPixmap(w, h)
        rounded.fill(Qt.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(cropped))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, 4, 4)
        p.end()
        self.thumb_lbl.setPixmap(rounded)
        self.thumb_lbl.setText("")

    def set_thumb(self, img: QImage):
        self._set_thumb(img)

    def _toggle_pause(self):
        if self.state == "paused":
            self.resume_clicked.emit(self.wid)
        else:
            self.pause_clicked.emit(self.wid)

    def set_progress(self, got, total):
        if total > 0:
            self._pct = int(got * 100 / total)
            self.lbl_pct.setText(f"{self._pct}%")
            self.update()

    def set_state(self, state):
        self.state = state
        if state == "paused":
            self.btn_pause.setText("▶")
            self._state_color = QColor(230, 150, 40, 220)  # sariq
            self.update()
        elif state == "downloading":
            self.btn_pause.setText("⏸")
            self._state_color = QColor(76, 175, 80, 220)  # yashil
            self.update()
        elif state == "done":
            self.btn_pause.setEnabled(False)
            self.btn_pause.setText("\u2713")
            self.btn_pause.setStyleSheet("""
                QPushButton { background: rgba(76,175,80,0.9);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; }
            """)
            self._pct = 100
            self.lbl_pct.setText("100%")
            self._state_color = QColor(76, 175, 80, 220)
            self.update()
        elif state == "cancelled":
            self.btn_pause.setEnabled(False)
            self.lbl_pct.setText(T.get("status_cancelled", "Cancelled"))
            self._state_color = QColor(80, 80, 80, 220)
            self.update()
        elif state == "error":
            self.btn_pause.setEnabled(False)
            self.btn_pause.setText("!")
            self.btn_pause.setStyleSheet("""
                QPushButton { background: rgba(220,80,80,0.9);
                    color:#fff; border:1px solid #ffffff;
                    border-radius: 11px; }
            """)
            self.lbl_pct.setText(T.get("status_error", "Error"))
            self._state_color = QColor(200, 60, 60, 220)
            self.update()

class DownloadsList(QFrame):
    pause_clicked = pyqtSignal(str)
    resume_clicked = pyqtSignal(str)
    cancel_clicked = pyqtSignal(str)
    count_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DownloadsList")
        self.setStyleSheet("""
            QFrame#DownloadsList {
                background: rgba(20,20,25,0.92);
                border: 1px solid #ffffff;
                border-radius: 11px;
            }
        """)
        self.items_widgets = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)
        self._lay = lay
        # Scroll uchun
        self.setMaximumHeight(400)
        self.hide()

    def add_download(self, wid, name, thumb_img=None):
        if wid in self.items_widgets:
            return
        w = DownloadItemWidget(wid, name, thumb_img)
        w.pause_clicked.connect(self.pause_clicked.emit)
        w.resume_clicked.connect(self.resume_clicked.emit)
        w.remove_clicked.connect(self.remove_item)
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        w.setMinimumWidth(300)
        self.items_widgets[wid] = w
        # Stretch dan oldin qo'shamiz (pastga yopishmasin)
        self._lay.insertWidget(self._lay.count() - 1, w)
        self.count_changed.emit()

    def set_thumb(self, wid, img):
        w = self.items_widgets.get(wid)
        if w:
            w.set_thumb(img)

    def update_progress(self, wid, got, total):
        w = self.items_widgets.get(wid)
        if w:
            w.set_progress(got, total)

    def set_state(self, wid, state):
        w = self.items_widgets.get(wid)
        if w:
            w.set_state(state)

    def remove_item(self, wid):
        w = self.items_widgets.get(wid)
        if not w:
            return
        if w.state in ("downloading", "paused"):
            self.cancel_clicked.emit(wid)
            return
        self._lay.removeWidget(w)
        w.setParent(None)
        w.deleteLater()
        del self.items_widgets[wid]
        if not self.items_widgets:
            self.hide()
        self.count_changed.emit()

    def clear(self):
        for wid, w in list(self.items_widgets.items()):
            self._lay.removeWidget(w)
            w.setParent(None)
            w.deleteLater()
        self.items_widgets.clear()
        self.count_changed.emit()

    def active_count(self):
        return sum(1 for w in self.items_widgets.values()
                   if w.state in ("downloading", "paused"))

    def total_count(self):
        return len(self.items_widgets)







class MessageDialog(QDialog):
    """Faqat OK tugmasi bilan xabar dialogi."""

    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QPushButton {
                background: #5a9fd4; color: #fff;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 8px 24px; font-weight: bold;
            }
            QPushButton:hover { background: #6bafe4; }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        msg = QLabel(message)
        msg.setWordWrap(True)
        lay.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        self.btn_ok.setAutoDefault(True)
        btn_row.addWidget(self.btn_ok)
        lay.addLayout(btn_row)

        self.btn_ok.setFocus()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
            self.accept()
            return
        super().keyPressEvent(e)


class ConfirmDialog(QDialog):
    """Yes/No tasdiq dialog."""

    YES = 1
    NO = 2

    def __init__(self, parent, title, message,
                 yes_text=None, no_text=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QPushButton {
                background: #2b2b2b; color: #e0e0e0;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 8px 22px; }
            QPushButton:hover {
                background: #3a3a3a;
                border: 1px solid #5a9fd4;
            }
            QPushButton#primary {
                background: #5a9fd4; color: #fff;
                border: 1px solid #ffffff;
                font-weight: bold;
            }
            QPushButton#primary:hover {
                background: #6bafe4;
            }
            QPushButton#danger {
                background: rgba(200,60,60,0.9);
                color: #fff;
                border: 1px solid #ffffff;
                font-weight: bold;
            }
            QPushButton#danger:hover {
                background: rgba(230,70,70,1.0);
            }
        """)
        self.result_choice = self.NO

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        msg = QLabel(message)
        msg.setWordWrap(True)
        lay.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_no = QPushButton(no_text or T["btn_no"])
        self.btn_no.clicked.connect(self._on_no)
        btn_row.addWidget(self.btn_no)

        self.btn_yes = QPushButton(yes_text or T["btn_yes"])
        self.btn_yes.setObjectName("danger")
        self.btn_yes.clicked.connect(self._on_yes)
        self.btn_yes.setDefault(True)
        self.btn_yes.setAutoDefault(True)
        btn_row.addWidget(self.btn_yes)

        lay.addLayout(btn_row)
        self.btn_yes.setFocus()

    def _on_yes(self):
        self.result_choice = self.YES
        self.accept()

    def _on_no(self):
        self.result_choice = self.NO
        self.accept()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_yes()
            return
        if e.key() == Qt.Key_Escape:
            self._on_no()
            return
        super().keyPressEvent(e)


class LanguageConfirmDialog(QDialog):
    """OK / Later dialog."""

    RESTART = 1
    LATER = 2

    def __init__(self, parent=None, title=None, message=None):
        super().__init__(parent)
        if title is None:
            title = T.get("lang_title", "Language")
        if message is None:
            message = T.get("lang_changed",
                            "Restart the application to apply?")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QPushButton {
                background: #2b2b2b; color: #e0e0e0;
                border: 1px solid #ffffff; border-radius: 11px;
                padding: 8px 20px; }
            QPushButton:hover {
                background: #3a3a3a;
                border: 1px solid #5a9fd4;
            }
            QPushButton#primary {
                background: #5a9fd4; color: #fff;
                border: 1px solid #ffffff;
                font-weight: bold;
            }
            QPushButton#primary:hover {
                background: #6bafe4;
            }
        """)
        self.result_choice = self.LATER

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        msg = QLabel(message)
        msg.setWordWrap(True)
        lay.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_later = QPushButton(T.get("btn_later", "Later"))
        self.btn_later.clicked.connect(self._on_later)
        btn_row.addWidget(self.btn_later)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setObjectName("primary")
        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_ok.setDefault(True)
        self.btn_ok.setAutoDefault(True)
        btn_row.addWidget(self.btn_ok)

        lay.addLayout(btn_row)
        self.btn_ok.setFocus()

    def _on_ok(self):
        self.result_choice = self.RESTART
        self.accept()

    def _on_later(self):
        self.result_choice = self.LATER
        self.accept()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_ok()
            return
        if e.key() == Qt.Key_Escape:
            self._on_later()
            return
        super().keyPressEvent(e)


class SettingsDialog(QDialog):
    """Sozlamalar dialogi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T["settings_title"])
        self.setModal(True)
        self.setMinimumSize(560, 340)
        self.setStyleSheet("""
            QDialog { background:#1a1a1a; color:#e0e0e0; }
            QLabel { color:#e0e0e0; }
            QLabel#section { color:#5a9fd4; font-size:13px;
                font-weight:bold; padding-top:10px; }
            QLineEdit { background:#252525; color:#e0e0e0;
                border:1px solid #ffffff; border-radius:11px;
                padding:8px 12px; }
            QLineEdit:focus { border:1px solid #5a9fd4; }
            QPushButton { background:#2b2b2b; color:#e0e0e0;
                border:1px solid #ffffff; border-radius:11px;
                padding:8px 16px; }
            QPushButton:hover { background:#3a3a3a;
                border:1px solid #5a9fd4; }
            QPushButton#primary { background:#5a9fd4; color:#fff;
                border:1px solid #ffffff; font-weight:bold; }
            QPushButton#primary:hover { background:#6bafe4; }
            QPushButton#danger { background:rgba(200,60,60,0.85);
                color:#fff; border:1px solid #ffffff; }
            QPushButton#danger:hover { background:rgba(230,70,70,1.0); }
        """)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        # ============ API Key ============
        lbl2 = QLabel(T["lbl_api_key"])
        lbl2.setObjectName("section")
        root.addWidget(lbl2)

        api_row = QHBoxLayout()
        self.input_api = QLineEdit()
        self.input_api.setPlaceholderText(T["api_ph"])
        self.input_api.setText(get_api_key() or "")
        self.input_api.setEchoMode(QLineEdit.Password)
        self.input_api.setMinimumWidth(150)
        api_row.addWidget(self.input_api, stretch=1)

        self.btn_show_key = QPushButton(T.get("btn_show", "Show"))
        self.btn_show_key.setMinimumWidth(100)
        self.btn_show_key.setMaximumWidth(140)
        self.btn_show_key.setFixedHeight(34)
        self.btn_show_key.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_show_key.setCheckable(True)
        self.btn_show_key.setCursor(Qt.PointingHandCursor)
        self.btn_show_key.setToolTip(T.get("tip_show_key", "Show API key"))
        self.btn_show_key.setStyleSheet("""
            QPushButton {
                background: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #ffffff;
                border-radius: 11px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 14px;
            }
            QPushButton:hover {
                background: #3a3a3a;
                border: 1px solid #5a9fd4;
            }
            QPushButton:checked {
                background: #5a9fd4;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
        """)
        def _toggle_echo(checked):
            if checked:
                self.input_api.setEchoMode(QLineEdit.Normal)
                self.btn_show_key.setText(T.get("btn_hide", "Hide"))
                self.btn_show_key.setToolTip(
                    T.get("tip_hide_key", "Hide API key"))
            else:
                self.input_api.setEchoMode(QLineEdit.Password)
                self.btn_show_key.setText(T.get("btn_show", "Show"))
                self.btn_show_key.setToolTip(
                    T.get("tip_show_key", "Show API key"))
        self.btn_show_key.toggled.connect(_toggle_echo)
        api_row.addWidget(self.btn_show_key)

        btn_get = QPushButton(T["btn_get_api"])
        btn_get.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://wallhaven.cc/settings/account")))
        api_row.addWidget(btn_get)
        root.addLayout(api_row)

        api_btn_row = QHBoxLayout()
        api_btn_row.addStretch()
        btn_save_api = QPushButton(T["btn_save_api"])
        btn_save_api.setObjectName("primary")
        btn_save_api.clicked.connect(self._save_api)
        api_btn_row.addWidget(btn_save_api)
        btn_del_api = QPushButton(T["btn_del_api"])
        btn_del_api.setObjectName("danger")
        btn_del_api.clicked.connect(self._delete_api)
        api_btn_row.addWidget(btn_del_api)
        root.addLayout(api_btn_row)

        # ============ Language ============
        lbl_lang = QLabel(T["lbl_language"])
        lbl_lang.setObjectName("section")
        root.addWidget(lbl_lang)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(T["lbl_display_lang"]))
        self.combo_lang = QComboBox()
        self.combo_lang.setMinimumWidth(220)
        self.combo_lang.addItem("Auto (System)", "auto")
        self.combo_lang.addItem("English", "en")
        self.combo_lang.addItem("O'zbekcha", "uz")
        self.combo_lang.addItem("Русский", "ru")
        self.combo_lang.addItem("Türkçe", "tr")
        self.combo_lang.addItem("Deutsch", "de")
        self.combo_lang.addItem("Français", "fr")
        self.combo_lang.addItem("Español", "es")
        self.combo_lang.addItem("Italiano", "it")
        self.combo_lang.addItem("Português", "pt")
        self.combo_lang.addItem("日本語", "ja")
        self.combo_lang.addItem("한국어", "ko")
        self.combo_lang.addItem("中文", "zh-CN")
        self.combo_lang.addItem("العربية", "ar")
        self.combo_lang.addItem("हिन्दी", "hi")
        # Joriy tilni tanlash — config dagi (hozirgi faol emas!)
        current_lang = self._get_lang()
        idx = self.combo_lang.findData(current_lang)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        # Bloklash — ochilganda signal chiqmasin
        self.combo_lang.blockSignals(True)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.blockSignals(False)
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.combo_lang, stretch=1)
        root.addLayout(lang_row)

        # ============ Download Folder ============
        lbl3 = QLabel(T["lbl_download_folder"])
        lbl3.setObjectName("section")
        root.addWidget(lbl3)

        folder_row = QHBoxLayout()
        self.lbl_folder = QLabel(str(self._get_dl_folder()))
        self.lbl_folder.setStyleSheet("color:#aaa; font-size:11px;")
        self.lbl_folder.setWordWrap(True)
        folder_row.addWidget(self.lbl_folder, stretch=1)
        btn_folder = QPushButton(T["btn_change_folder"])
        btn_folder.clicked.connect(self._change_folder)
        folder_row.addWidget(btn_folder)
        root.addLayout(folder_row)

        # ============ Data ============
        lbl4 = QLabel(T["lbl_data"])
        lbl4.setObjectName("section")
        root.addWidget(lbl4)

        data_row = QHBoxLayout()
        data_row.addStretch()
        btn_cache = QPushButton(T["btn_clear_cache"])
        btn_cache.clicked.connect(self._clear_cache)
        data_row.addWidget(btn_cache)
        btn_all = QPushButton(T["btn_clear_all"])
        btn_all.setObjectName("danger")
        btn_all.clicked.connect(self._clear_all)
        data_row.addWidget(btn_all)
        root.addLayout(data_row)

        # Close + Restart
        close_row = QHBoxLayout()
        close_row.addStretch()
        btn_close = QPushButton(T["btn_close"])
        btn_close.clicked.connect(self.accept)
        close_row.addWidget(btn_close)

        self.btn_restart = QPushButton(T["btn_restart"])
        self.btn_restart.setObjectName("primary")
        self.btn_restart.clicked.connect(self._restart_app)
        self.btn_restart.hide()  # boshlang'ichda yashirin
        close_row.addWidget(self.btn_restart)
        root.addLayout(close_row)

    def _parent_window(self):
        return self.parent()

    def _get_lang(self):
        pw = self._parent_window()
        if pw is not None and hasattr(pw, "_cfg_lang"):
            return pw._cfg_lang
        return "auto"

    def _on_lang_changed(self):
        lang = self.combo_lang.currentData()
        pw = self._parent_window()
        if pw is None:
            return
        # Faqat config'ga yozamiz — T.set_language chaqirmaymiz!
        # Shunda hozirgi til o'zgarmaydi
        pw._cfg_lang = lang
        if hasattr(pw, "_save_cfg"):
            pw._save_cfg()

        # OK / Later dialog
        dlg = LanguageConfirmDialog(self)
        dlg.exec_()
        if dlg.result_choice == LanguageConfirmDialog.RESTART:
            self._restart_app()
        else:
            # "Restart" tugmasini ko'rsatamiz
            if hasattr(self, "btn_restart"):
                self.btn_restart.show()


    def _restart_app(self):
        import sys as _sys
        import os as _os
        pw = self._parent_window()
        try:
            if pw is not None and hasattr(pw, "_save_cfg"):
                pw._save_cfg()
        except Exception:
            pass
        try:
            QApplication.quit()
            _os.execv(_sys.executable,
                      [_sys.executable] + _sys.argv)
        except Exception as e:
            print("restart:", e)


    def _get_dl_folder(self):
        pw = self._parent_window()
        if pw is not None and hasattr(pw, "download_folder"):
            return pw.download_folder or DEFAULT_DL_FOLDER
        return DEFAULT_DL_FOLDER

    def _save_api(self):
        k = self.input_api.text().strip()
        if not k:
            MessageDialog(self, T.get("error_title", "Error"), T.get("msg_api_empty", "API key is empty!")).exec_()
            return
        set_api_key(k)
        pw = self._parent_window()
        if pw and hasattr(pw, "_save_cfg"):
            pw._save_cfg()
        MessageDialog(self, "OK", T.get("msg_api_saved", "API key saved.")).exec_()

    def _delete_api(self):
        dlg = ConfirmDialog(
            self,
            T.get("del_api_title", "Delete API key"),
            T.get("del_api_body", "Delete the API key?"),
            yes_text=T["btn_yes"], no_text=T["btn_no"])
        dlg.exec_()
        if dlg.result_choice != ConfirmDialog.YES:
            return
        set_api_key("")
        self.input_api.clear()
        pw = self._parent_window()
        if pw and hasattr(pw, "_save_cfg"):
            pw._save_cfg()
        MessageDialog(self, "OK", T.get("msg_api_deleted", "API key deleted.")).exec_()


    def _change_folder(self):
        start = str(self._get_dl_folder())
        f = QFileDialog.getExistingDirectory(
            self, "Yuklash papkasini tanlang", start)
        if not f:
            return
        pw = self._parent_window()
        if pw and hasattr(pw, "download_folder"):
            pw.download_folder = Path(f)
            pw.download_folder.mkdir(parents=True, exist_ok=True)
            if hasattr(pw, "_save_cfg"):
                pw._save_cfg()
            if getattr(pw, "mode", None) == "local":
                pw.load_local()
        self.lbl_folder.setText(f)

    def _clear_cache(self):
        dlg = ConfirmDialog(
            self,
            T.get("clear_cache_title", "Clear cache"),
            T.get("clear_cache_body",
                  "Clear cache? (thumbnails and temporary data)"),
            yes_text=T["btn_yes"], no_text=T["btn_no"])
        dlg.exec_()
        if dlg.result_choice != ConfirmDialog.YES:
            return
        try:
            import shutil as _sh
            cache_dir = Path.home() / ".cache" / "uzAlhaithamWallpaper"
            if cache_dir.exists():
                # Joriy wallpaper faylini SAQLAB QOLAMIZ
                current_files = []
                for f in cache_dir.glob("current_wallpaper*"):
                    current_files.append((f, f.read_bytes()))
                # Keshni o'chiramiz (lekin current_wallpaper ni saqlaymiz)
                for item in cache_dir.iterdir():
                    if item.name.startswith("current_wallpaper"):
                        continue
                    try:
                        if item.is_dir():
                            _sh.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink()
                    except Exception:
                        pass
            # __pycache__
            for pp in Path(__file__).parent.rglob("__pycache__"):
                _sh.rmtree(pp, ignore_errors=True)
            # Parent windowning thumb keshini ham tozalaymiz
            pw = self._parent_window()
            if pw is not None and hasattr(pw, "thumbs"):
                try:
                    pw.thumbs.clear()
                except Exception:
                    pass
            QMessageBox.information(
                self, "OK",
                T.get("msg_cache_cleared",
                      "Cache cleared. (current wallpaper saved)"))
        except Exception as e:
            QMessageBox.critical(self, T.get("error_title", "Error"), str(e))


    def _clear_all(self):
        dlg = ConfirmDialog(
            self,
            T.get("clear_all_title", "Clear ALL data"),
            T.get("clear_all_body",
                  "ALL data will be deleted. Continue?"),
            yes_text=T["btn_yes"], no_text=T["btn_no"])
        dlg.exec_()
        if dlg.result_choice != ConfirmDialog.YES:
            return
        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            set_api_key("")
            self.input_api.clear()
            # OK / Later dialog
            dlg2 = LanguageConfirmDialog(
                self,
                title=T.get("msg_all_cleared_title", "Clear ALL data"),
                message=T.get("msg_all_cleared",
                              "All data cleared. Restart the application."))
            dlg2.exec_()
            if dlg2.result_choice == LanguageConfirmDialog.RESTART:
                self._restart_app()
            else:
                if hasattr(self, "btn_restart"):
                    self.btn_restart.show()
        except Exception as e:
            QMessageBox.critical(self, T.get("error_title", "Error"), str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("uzAlhaitham's wallpaper Selector")
        self.resize(1300, 850)
        self.setMinimumSize(900, 600)

        self.download_folder = None
        self.items = []
        self.cards = {}
        self.thumbs = {}
        self.wh_worker = None
        self.downloads = {}
        self.thumb_loader = None
        self.nsfw_pending = False
        self.grid_cols = 4
        self.fullscreen_grid = False
        self.sort_mode = "latest"
        self.mode = "online"
        self.current_page = 1
        self.total_pages = 1
        self.current_wallpaper_id = None
        self._dl_expanded = False

        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._relayout)

        self._pending_thumbs = {}
        self._thumb_flush = QTimer(self)
        self._thumb_flush.setInterval(80)
        self._thumb_flush.setSingleShot(True)
        self._thumb_flush.timeout.connect(self._flush_thumbs)

        # Tilni oldindan o'rnatish (UI yaratilishidan oldin)
        self._preload_language()
        self._theme()
        self._ui()
        self._shortcuts()
        self._load_cfg()
        # Global event filter
        QApplication.instance().installEventFilter(self)
        QTimer.singleShot(150, self.refresh)

    def _theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#1a1a1a; color:#e0e0e0;
                font-family:'Segoe UI','Noto Sans',sans-serif; font-size:12px; }
            QPushButton { background:#2b2b2b; border:1px solid #ffffff;
                border-radius: 11px; padding:5px 10px; color:#e0e0e0;
                font-size:12px; }
            QPushButton:hover { background:#3a3a3a; border:1px solid #5a9fd4; }
            QPushButton#primary { background:#5a9fd4; color:#fff;
                font-weight:bold; border:none; }
            QPushButton#primary:hover { background:#6bafe4; }
            QPushButton#iconbtn { padding: 0; font-size: 13px; }
            QLineEdit { background:#252525; border:1px solid #ffffff;
                border-radius: 11px; padding:5px 10px; color:#e0e0e0; }
            QLineEdit:focus { border:1px solid #5a9fd4; }
            QToolButton { background:#2b2b2b; border:1px solid #ffffff;
                border-radius: 11px; padding:5px 10px; color:#e0e0e0;
                font-size:12px; }
            QToolButton:hover { background:#3a3a3a; border:1px solid #5a9fd4; }
            QToolButton::menu-indicator { image: none; }
            QMenu { background:#252525; border:1px solid #3d3d3d;
                border-radius: 11px; padding:6px; color:#e0e0e0; }
            QMenu::item { padding:6px 24px 6px 16px; border-radius: 11px;
                font-size:12px; }
            QMenu::item:selected { background:#3a3a3a; color:#5a9fd4; }
            QScrollArea { border:none; background:transparent; }
            QScrollBar:vertical { background:transparent; width:10px; }
            QScrollBar::handle:vertical { background:#3d3d3d;
                border-radius: 11px; min-height:30px; }
            QScrollBar::handle:vertical:hover { background:#5a9fd4; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical
                { height:0; background:transparent; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
                { background: transparent; }
            QStatusBar { background:#151515; color:#888;
                border-top:1px solid #2d2d2d; font-size:11px; }
            QLabel#section { color:#888; font-size:10px; font-weight:bold;
                letter-spacing:1px; }
            QToolTip {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #ffffff;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)

    def _icon_btn(self, char, tooltip=""):
        b = QPushButton(char)
        b.setObjectName("iconbtn")
        b.setFixedSize(36, 34)
        b.setStyleSheet(
            "QPushButton { background:#2b2b2b; color:#e0e0e0; "
            "border:1px solid #ffffff; border-radius:11px; "
            "padding: 0px 0px 3px 0px; font-size: 14px; } "
            "QPushButton:hover { background:#3a3a3a; "
            "border:1px solid #5a9fd4; }")
        if tooltip:
            b.setToolTip(tooltip)
        b.setCursor(Qt.PointingHandCursor)
        return b

    def _ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        root = QVBoxLayout(c)
        root.setContentsMargins(10, 8, 10, 4)
        root.setSpacing(6)

        # ROW 1
        r1 = QHBoxLayout()
        r1.setSpacing(8)
        self.btn_folder = QPushButton("📁")
        self.btn_folder.setFixedSize(36, 34)
        self.btn_folder.setStyleSheet(
            "QPushButton { background:#2b2b2b; color:#e0e0e0; "
            "border:1px solid #ffffff; border-radius:11px; "
            "padding: 0px 0px 3px 0px; font-size: 14px; } "
            "QPushButton:hover { background:#3a3a3a; "
            "border:1px solid #5a9fd4; }")
        self.btn_folder.setToolTip(T.get("tip_folder", "Wallpapers folder"))
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self.choose_folder)
        r1.addWidget(self.btn_folder)

        btn_ref = self._icon_btn("⟳", T.get("tip_refresh", "Refresh"))
        btn_ref.clicked.connect(self.refresh)
        r1.addWidget(btn_ref)

        self.btn_home = self._icon_btn("⌂", T.get("tip_home", "Home"))
        self.btn_home.clicked.connect(self.go_home)
        r1.addWidget(self.btn_home)

        self.search = QLineEdit()
        self.search.setPlaceholderText(T["search_ph"])
        self.search.returnPressed.connect(self.search_now)
        self.search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search.setFixedHeight(34)
        self.search.setMinimumWidth(100)
        r1.addWidget(self.search, stretch=1)

        btn_search = self._icon_btn("🔍")
        btn_search.clicked.connect(self.search_now)
        r1.addWidget(btn_search)

        self.btn_mode = QPushButton(T["btn_downloaded"])
        self.btn_mode.setObjectName("primary")
        self.btn_mode.setFixedHeight(34)
        self.btn_mode.setMinimumWidth(130)
        self.btn_mode.setMaximumWidth(150)
        self.btn_mode.setCursor(Qt.PointingHandCursor)
        self.btn_mode.clicked.connect(self.toggle_mode)
        r1.addWidget(self.btn_mode)

        self.btn_grid = QToolButton()
        self.btn_grid.setText(f"▦ {self.grid_cols}")
        self.btn_grid.setToolTip(T["lbl_grid"])
        self.btn_grid.setPopupMode(QToolButton.InstantPopup)
        self.btn_grid.setFixedSize(60, 34)
        gm = QMenu(self)
        for c_ in (2, 3, 4, 6):
            a = QAction(f"{c_} " + (T.get("col_single", "column") if c_ == 1 else T.get("col_plural", "columns")), self)
            a.triggered.connect(lambda _, x=c_: self.set_grid(x))
            gm.addAction(a)
        self.btn_grid.setMenu(gm)
        r1.addWidget(self.btn_grid)

        self.btn_fs = self._icon_btn("⛶", T["tip_fullscreen"])
        self.btn_fs.setCheckable(True)
        self.btn_fs.clicked.connect(self.toggle_fs)
        r1.addWidget(self.btn_fs)

        lbl_sort = QLabel(T["lbl_sort_by"])
        lbl_sort.setStyleSheet("color:#888; font-size:11px;")
        r1.addWidget(lbl_sort)

        self.btn_sort = QToolButton()
        self.btn_sort.setText(T["sort_latest"] + "  ▾")
        self.btn_sort.setPopupMode(QToolButton.InstantPopup)
        self.btn_sort.setFixedSize(110, 34)
        m = QMenu(self)
        for key in ("latest", "popular", "random"):
            a = QAction(T[key].capitalize(), self)
            a.triggered.connect(lambda _, k=key: self.set_sort(k))
            m.addAction(a)
        self.btn_sort.setMenu(m)
        r1.addWidget(self.btn_sort)
        root.addLayout(r1)

        # ROW 2
        r2 = QHBoxLayout()
        r2.setSpacing(6)
        lbl = QLabel(T["lbl_category"])
        lbl.setObjectName("section")
        lbl.setFixedWidth(72)
        r2.addWidget(lbl)
        self.tb_general = ToggleButton(T["btn_general"], T["tip_general"])
        self.tb_general.setChecked(True)
        self.tb_general.clicked.connect(self._on_cat_click)
        r2.addWidget(self.tb_general)
        self.tb_anime = ToggleButton(T["btn_anime"], T["tip_anime"])
        self.tb_anime.clicked.connect(self._on_cat_click)
        r2.addWidget(self.tb_anime)
        self.tb_people = ToggleButton(T["btn_people"], T["tip_people"])
        self.tb_people.clicked.connect(self._on_cat_click)
        r2.addWidget(self.tb_people)
        r2.addSpacing(14)
        lbl2 = QLabel(T["lbl_safety"])
        lbl2.setObjectName("section")
        lbl2.setFixedWidth(60)
        r2.addWidget(lbl2)
        self.tb_sfw = ToggleButton(T["btn_sfw"], T["tip_sfw"])
        self.tb_sfw.setChecked(True)
        self.tb_sfw.clicked.connect(self._on_sfw_click)
        r2.addWidget(self.tb_sfw)
        self.tb_nsfw = ToggleButton(T["btn_nsfw"], T["tip_nsfw"])
        self.tb_nsfw.clicked.connect(self._on_nsfw_click)
        r2.addWidget(self.tb_nsfw)
        r2.addStretch()

        # Settings tugmasi — o'ng chekkada
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(34, 30)
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setToolTip(T.get("tip_settings", "Settings"))
        self.btn_settings.setStyleSheet(
            "QPushButton { background:#2b2b2b; color:#e0e0e0; "
            "border:1px solid #ffffff; border-radius:11px; "
            "font-size: 16px; padding: 0; } "
            "QPushButton:hover { background:#3a3a3a; "
            "border:1px solid #5a9fd4; }")
        self.btn_settings.clicked.connect(self._open_settings)
        r2.addWidget(self.btn_settings)

        root.addLayout(r2)

        self.nsfw_bar = NsfwConfirmBar()
        self.nsfw_bar.confirmed.connect(self._nsfw_ok)
        self.nsfw_bar.cancelled.connect(self._nsfw_no)
        self.nsfw_bar.hide()
        root.addWidget(self.nsfw_bar)

        # Scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")
        self.gc = QWidget()
        self.gc.setStyleSheet("background: transparent;")
        self.gc_layout = QVBoxLayout(self.gc)
        self.gc_layout.setContentsMargins(0, 6, 0, 12)
        self.gc_layout.setSpacing(12)

        # grid holder (grid uchun alohida)
        self.grid_holder = QWidget()
        self.grid_holder.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_holder)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.gc_layout.addWidget(self.grid_holder)

        self.scroll.setWidget(self.gc)
        self.scroll.viewport().installEventFilter(self)
        # Scroll bo'lganda popup yopilsin
        self.scroll.verticalScrollBar().valueChanged.connect(
            self._on_scroll_hide_popup)
        root.addWidget(self.scroll, stretch=1)

        # Status bar (yashirin — kerak emas)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.hide()
        self.page_lbl = QLabel("")

        # ============ Pagination — floating overlay ============
        self.pagination_widget = QWidget()
        self.pagination_widget.setStyleSheet("background: transparent; border: none;")
        self.pagination_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pagination_widget.setFixedHeight(40)
        self.pagination_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.pagination_widget.setStyleSheet("background: transparent;")
        pv = QVBoxLayout(self.pagination_widget)
        pv.setContentsMargins(0, 0, 0, 0)
        pv.setSpacing(0)

        # Row 1 — page buttons
        self.pagination_row = QWidget()
        self.pagination_row.setStyleSheet("background: transparent; border: none;")
        self.pagination_row.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pagination_layout = QHBoxLayout(self.pagination_row)
        self.pagination_layout.setContentsMargins(6, 2, 6, 2)
        self.pagination_layout.setSpacing(3)
        pv.addWidget(self.pagination_row, alignment=Qt.AlignCenter)

        # Pagination ni gc_layout ga qo'shamiz (scroll ichida, grid ostida)
        # Pastdagi qator: chapda 🔍 + pagination, o'ngda downloads
        self.bottom_row = QHBoxLayout()
        self.bottom_row.setContentsMargins(0, 0, 0, 0)
        self.bottom_row.setSpacing(6)
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(38, 28)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setStyleSheet("""
            QPushButton { background: rgba(20,20,25,0.92);
                color: #e8e8e8; border: 1px solid #ffffff;
                border-radius: 11px; font-size: 14px; padding: 0; }
            QPushButton:hover { background: rgba(40,40,50,1.0);
                border: 1px solid #5a9fd4; }
        """)
        self.search_btn.clicked.connect(self._open_goto_dialog)
        self.bottom_row.addWidget(self.search_btn, alignment=Qt.AlignLeft)
        # Chap bo'shliq
        self.bottom_row.addStretch(1)
        # Pagination — markazda
        self.bottom_row.addWidget(self.pagination_widget)
        # O'ng bo'shliq
        self.bottom_row.addStretch(1)
        # Downloads indicator — o'ngda
        self.dl_indicator = DownloadsIndicator()
        self.dl_indicator.clicked.connect(self._toggle_dl_list)
        self.bottom_row.addWidget(self.dl_indicator, alignment=Qt.AlignRight)
        # O'ngdan bo'shliq (chaproqqa surish)
        self.bottom_row.addSpacing(30)

        self.gc_layout.addLayout(self.bottom_row)
        self.pagination_widget.hide()

        # Downloads list — popup
        self.dl_list = DownloadsList()
        self.dl_list.setParent(self)
        self.dl_list.setAttribute(Qt.WA_TranslucentBackground, True)
        self.dl_list.setAttribute(Qt.WA_NoSystemBackground, True)
        self.dl_list.pause_clicked.connect(self._dl_pause)
        self.dl_list.resume_clicked.connect(self._dl_resume)
        self.dl_list.cancel_clicked.connect(self._dl_cancel)
        self.dl_list.count_changed.connect(self._refresh_dl_bar)
        self.dl_list.hide()

    def _position_overlays(self):
        pass

    def _toggle_dl_list(self):
        if self.dl_list.isVisible():
            self.dl_list.hide()
        else:
            self._position_dl_list()
            self.dl_list.show()
            self.dl_list.raise_()

    def _on_scroll_hide_popup(self, value=None):
        if hasattr(self, "dl_list") and self.dl_list.isVisible():
            self.dl_list.hide()

    def _position_dl_list(self):
        if not hasattr(self, "dl_indicator") or not hasattr(self, "dl_list"):
            return
        try:
            # Indicator ning MainWindow dagi joylashuvi
            ind_global = self.dl_indicator.mapToGlobal(QPoint(0, 0))
            ind_pos = self.mapFromGlobal(ind_global)
            ind_right = ind_pos.x() + self.dl_indicator.width()
            ind_top = ind_pos.y()

            # Popup kengligi = indicator kengligi
            list_w = max(self.dl_indicator.width(), 280)
            items_count = self.dl_list.total_count()
            list_h = max(60, min(400, 20 + items_count * 54))

            # O'ng chekkasi indicator bilan BIR XIL
            x = ind_right - list_w
            if x < 0:
                x = 0
            # Pastdan indicator ustida
            y = ind_top - list_h - 8
            if y < 0:
                y = 0

            self.dl_list.setGeometry(int(x), int(y),
                                     int(list_w), int(list_h))
            inner_w = int(list_w) - 20
            for item in self.dl_list.items_widgets.values():
                item.setMinimumWidth(inner_w)
                item.setMaximumWidth(inner_w)
            self.dl_list.raise_()
        except Exception as e:
            print("position_dl_list:", e)

    def _refresh_dl_bar(self):
        total = self.dl_list.total_count()
        completed = total - self.dl_list.active_count()
        if hasattr(self, "dl_indicator"):
            self.dl_indicator.update_overall(total, completed)
        if total == 0:
            self.dl_list.hide()
            return
        if self.dl_list.isVisible():
            QTimer.singleShot(0, self._position_dl_list)

    def eventFilter(self, obj, event):
        # Asosiy window da sichqoncha bosilsa — dl_list yopilsin
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, "dl_list") and self.dl_list.isVisible():
                # QScrollArea yoki boshqa widget ichida bosilsa — yopish
                try:
                    if obj is self.scroll.viewport() or obj is self.scroll:
                        self.dl_list.hide()
                except Exception:
                    pass
        return super().eventFilter(obj, event)

    def eventFilter(self, obj, event):
        if obj is self.scroll.viewport() and event.type() == QEvent.Resize:
            self._resize_timer.start(150)
        # Scroll paytida popup yopilsin
        if event.type() == QEvent.Wheel:
            if hasattr(self, "dl_list") and self.dl_list.isVisible():
                self.dl_list.hide()
        return super().eventFilter(obj, event)

    def wheelEvent(self, e):
        # Scroll da popup yopilsin
        if hasattr(self, "dl_list") and self.dl_list.isVisible():
            self.dl_list.hide()
        super().wheelEvent(e)

    def _preload_translations(self):
        """Barcha tarjimalarni sekin, FONDA yuklaymiz (UI bloklanmasin)."""
        try:
            keys = list(TR["en"].keys())
            def _worker():
                import time
                for k in keys:
                    try:
                        _ = T[k]
                        time.sleep(0.05)
                    except Exception:
                        pass
            import threading as _th
            t = _th.Thread(target=_worker, daemon=True)
            t.start()
        except Exception:
            pass


    def _preload_language(self):
        """Config'dan tilni oldindan o'qib, UI yaratilishidan oldin o'rnatamiz."""
        try:
            if CONFIG_FILE.exists():
                d = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                lang = d.get("language", "auto")
                self._cfg_lang = lang
                # Keshni tozalab, tilni o'rnatamiz
                _TRANS_CACHE.clear()
                T.set_language(lang)
        except Exception as e:
            print("preload_language:", e)
        QTimer.singleShot(100, self._preload_translations)


    def _refresh_ui_texts(self):
        """UI dagi matnlarni qayta o'rnatadi (til o'zgarganda)."""
        try:
            self.tb_general.setText(T["btn_general"])
            self.tb_anime.setText(T["btn_anime"])
            self.tb_people.setText(T["btn_people"])
            self.tb_sfw.setText(T["btn_sfw"])
            self.tb_nsfw.setText(T["btn_nsfw"])
            self.tb_general.setToolTip(T["tip_general"])
            self.tb_anime.setToolTip(T["tip_anime"])
            self.tb_people.setToolTip(T["tip_people"])
            self.tb_sfw.setToolTip(T["tip_sfw"])
            self.tb_nsfw.setToolTip(T["tip_nsfw"])
            if hasattr(self, "btn_folder"):
                self.btn_folder.setToolTip(
                    T.get("tip_folder", "Wallpapers folder"))
            if hasattr(self, "btn_home"):
                self.btn_home.setToolTip(T.get("tip_home", "Home"))
            if hasattr(self, "btn_settings"):
                self.btn_settings.setToolTip(
                    T.get("tip_settings", "Settings"))
            if self.mode == "online":
                self.btn_mode.setText(T["btn_downloaded"])
            else:
                self.btn_mode.setText(T["btn_online"])
            self.search.setPlaceholderText(T["search_ph"])
            self.btn_sort.setText(
                T["sort_" + self.sort_mode].capitalize() + "  \u25be")
        except Exception as e:
            print("refresh_ui_texts:", e)



    def _set_language(self, lang):
        # Faqat config'ga yozamiz — T.set_language chaqirmaymiz
        self._cfg_lang = lang
        self._save_cfg()


    def _shortcuts(self):
        QShortcut(QKeySequence("Ctrl+H"), self, self._quick_disable_nsfw)
        QShortcut(QKeySequence("Escape"), self, self._close_fs)

    def _load_cfg(self):
        if CONFIG_FILE.exists():
            try:
                d = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                f = d.get("download_folder", "")
                if f:
                    self.download_folder = Path(f)
                self.sort_mode = d.get("sort_mode", "latest")
                self.grid_cols = int(d.get("grid_cols", 4))
                self.btn_grid.setText(f"\u25a6 {self.grid_cols}")
                self.btn_sort.setText(T[self.sort_mode].capitalize() + "  \u25be")
                if d.get("api_key"):
                    set_api_key(d["api_key"])
                cw = d.get("current_wallpaper_id", "")
                if cw:
                    self.current_wallpaper_id = cw
                # Language
                lang = d.get("language", "auto")
                self._cfg_lang = lang
                T.set_language(lang)
                # Category ni tiklash (SFW/NSFW saqlanmaydi)
                g = d.get("cat_general", True)
                a = d.get("cat_anime", False)
                pe = d.get("cat_people", False)
                # Kamida bittasi yoqilgan bo'lishi kerak
                if not (g or a or pe):
                    g = True
                self.tb_general.blockSignals(True)
                self.tb_anime.blockSignals(True)
                self.tb_people.blockSignals(True)
                self.tb_general.setChecked(g)
                self.tb_anime.setChecked(a)
                self.tb_people.setChecked(pe)
                self.tb_general.blockSignals(False)
                self.tb_anime.blockSignals(False)
                self.tb_people.blockSignals(False)
            except Exception:
                pass
        if not self.download_folder:
            self.download_folder = DEFAULT_DL_FOLDER
            self.download_folder.mkdir(parents=True, exist_ok=True)

    def _save_cfg(self):
        try:
            CONFIG_FILE.write_text(json.dumps({
                "download_folder": str(self.download_folder or ""),
                "sort_mode": self.sort_mode,
                "grid_cols": self.grid_cols,
                "api_key": get_api_key(),
                "current_wallpaper_id": self.current_wallpaper_id or "",
                "cat_general": self.tb_general.isChecked(),
                "cat_anime": self.tb_anime.isChecked(),
                "cat_people": self.tb_people.isChecked(),
                "language": self._cfg_lang,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _on_cat_click(self):
        checked = [b for b in (self.tb_general, self.tb_anime,
                                self.tb_people) if b.isChecked()]
        if not checked:
            sender = self.sender()
            if sender is not None:
                sender.setChecked(True)
            return
        self._save_cfg()
        self.current_page = 1
        self.refresh()

    def _on_sfw_click(self):
        if not self.tb_sfw.isChecked() and not self.tb_nsfw.isChecked():
            sender = self.sender()
            if sender is not None:
                sender.setChecked(True)
            return
        self.current_page = 1
        self.refresh()

    def _on_nsfw_click(self):
        if self.tb_nsfw.isChecked():
            if not get_api_key():
                dlg = ApiKeyDialog(self)
                if dlg.exec_() == QDialog.Accepted:
                    set_api_key(dlg.api_key)
                    self._save_cfg()
                else:
                    self.tb_nsfw.setChecked(False)
                    return
            self.nsfw_pending = True
            self.tb_nsfw.setChecked(False)
            self.nsfw_bar.start()
        else:
            if not self.tb_sfw.isChecked():
                self.tb_nsfw.setChecked(True)
                return
            if not self.nsfw_pending:
                self.current_page = 1
                self.refresh()

    def _nsfw_ok(self):
        self.nsfw_pending = False
        self.tb_nsfw.setChecked(True)
        self.current_page = 1
        self.refresh()

    def _nsfw_no(self):
        self.nsfw_pending = False

    def _quick_disable_nsfw(self):
        self.nsfw_bar.stop()
        self.nsfw_pending = False
        if self.tb_nsfw.isChecked():
            self.tb_nsfw.setChecked(False)
        self.tb_sfw.setChecked(True)
        self.current_page = 1
        self.refresh()

    def _cats_bits(self):
        return (("1" if self.tb_general.isChecked() else "0") +
                ("1" if self.tb_anime.isChecked() else "0") +
                ("1" if self.tb_people.isChecked() else "0"))

    def _purity_bits(self):
        return "101" if self.tb_nsfw.isChecked() else "100"

    def _sort_param(self):
        return {"latest": "date_added", "popular": "toplist",
                "random": "random"}.get(self.sort_mode, "date_added")

    def set_sort(self, key):
        self.sort_mode = key
        self.btn_sort.setText(T[key].capitalize() + "  \u25be")
        self._save_cfg()
        self.current_page = 1
        self.refresh()

    def set_grid(self, cols):
        self.grid_cols = cols
        self.btn_grid.setText(f"\u25a6 {cols}")
        self._save_cfg()
        self._relayout()

    def toggle_fs(self, checked):
        self.fullscreen_grid = checked
        self.btn_fs.setStyleSheet(
            "QPushButton { background:#5a9fd4; color:#fff; "
            "border:none; padding:0; font-size:13px; }" if checked else "")
        self._relayout()

    def _close_fs(self):
        if self.fullscreen_grid:
            self.btn_fs.setChecked(False)
            self.toggle_fs(False)

    def toggle_mode(self):
        if self.mode == "online":
            self.mode = "local"
            self.btn_mode.setText(T["btn_online"])
            self.load_local()
        else:
            self.mode = "online"
            self.btn_mode.setText(T["btn_downloaded"])
            self.refresh()

    def search_now(self):
        self.current_page = 1
        self.refresh()

    def go_home(self):
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.current_page = 1
        if self.mode == "local":
            self.mode = "online"
            self.btn_mode.setText(T["btn_downloaded"])
        self.refresh()

    def choose_folder(self):
        start = str(self.download_folder or Path.home())
        f = QFileDialog.getExistingDirectory(self,
                                             "📁", start)
        if f:
            self.download_folder = Path(f)
            self.download_folder.mkdir(parents=True, exist_ok=True)
            self._save_cfg()
            if self.mode == "local":
                self.load_local()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def _on_thumb(self, wid, img):
        if img is None or img.isNull():
            return
        self._pending_thumbs[wid] = img
        if not self._thumb_flush.isActive():
            self._thumb_flush.start()

    def _flush_thumbs(self):
        if not self._pending_thumbs:
            return
        sb = self.scroll.verticalScrollBar()
        saved = sb.value()
        for wid, img in self._pending_thumbs.items():
            self.thumbs[wid] = img
            card = self.cards.get(wid)
            if card is not None:
                try:
                    # Widget hali hayotmi?
                    card.width()  # RuntimeError: wrapped C/C++ object deleted
                    card.set_pixmap(img)
                except (RuntimeError, Exception):
                    pass
            try:
                self.dl_list.set_thumb(wid, img)
            except Exception:
                pass
        self._pending_thumbs.clear()
        QTimer.singleShot(0, lambda: sb.setValue(saved))

    def _stop_thumbs(self):
        if self.thumb_loader is not None:
            try:
                self.thumb_loader.loaded.disconnect()
            except Exception:
                pass
            try:
                self.thumb_loader.stop()
            except Exception:
                pass
            # Thread to'liq to'xtaguncha kutamiz
            try:
                if self.thumb_loader.isRunning():
                    self.thumb_loader.wait(3000)
            except Exception:
                pass
            self.thumb_loader = None

    def _start_thumbs(self):
        self._stop_thumbs()
        pairs = [(w["id"], w["thumb"]) for w in self.items
                 if w.get("thumb") and w["id"] not in self.thumbs]
        if not pairs:
            return
        self.thumb_loader = ThumbLoaderPool(pairs, THUMB_PX, THUMB_WORKERS)
        self.thumb_loader.loaded.connect(self._on_thumb)
        self.thumb_loader.start()

    def refresh(self):
        if self.mode == "local":
            self.load_local()
            return
        if not self.download_folder:
            self.choose_folder()
            return
        page = self.current_page
        self.status.showMessage(T.get("loading", "Loading..."))
        self._clear()
        self.cards.clear()
        self.thumbs.clear()
        self._pending_thumbs.clear()
        self.items = []
        self._stop_thumbs()
        if self.wh_worker and self.wh_worker.isRunning():
            try:
                self.wh_worker.finished.disconnect()
                self.wh_worker.error.disconnect()
            except Exception:
                pass
            self.wh_worker.quit()
            self.wh_worker.wait()
        self.wh_worker = WallhavenWorker(
            query=self.search.text().strip(),
            categories=self._cats_bits(),
            purity=self._purity_bits(),
            sorting=self._sort_param(),
            page=page, api_key=get_api_key())
        self.wh_worker.finished.connect(self._on_results)
        self.wh_worker.error.connect(self._on_err)
        self.wh_worker.start()

    def _on_results(self, items, last_page):
        self.total_pages = max(1, last_page)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self.items = items
        self.status.showMessage("{} images".format(len(items)))
        self._build_cards()
        self._start_thumbs()
        self._build_pagination()
        self._update_page_label()

    def _on_err(self, msg):
        self.status.showMessage(f"{T['error']}: {msg}")

    def _update_page_label(self):
        if self.mode == "online" and self.total_pages > 1:
            self.page_lbl.setText(
                "Page {} / {}".format(self.current_page, self.total_pages))
        else:
            self.page_lbl.setText("")

    def _page_btn_style(self, active=False):
        if active:
            return ("QPushButton { background: #5a9fd4; color: #fff; "
                    "border: 1px solid #ffffff; border-radius: 11px; "
                    "font-weight: bold; font-size: 14px; padding: 0; }")
        return ("QPushButton { background: transparent; color: #c8c8c8; "
                "border: 1px solid #ffffff; border-radius: 11px; "
                "font-size: 13px; padding: 0; } "
                "QPushButton:hover { background: rgba(255,255,255,0.10); "
                "color: #fff; }")

    def _nav_btn_style(self):
        return ("QPushButton { background: transparent; color: #c8c8c8; "
                "border: 1px solid #ffffff; border-radius: 11px; "
                "font-size: 14px; padding: 0; } "
                "QPushButton:hover { background: rgba(255,255,255,0.10); "
                "color: #fff; }")

    def _ellipsis_style(self):
        return ("QLabel { background: transparent; color: #666; "
                "font-size: 14px; font-weight: bold; border: none; }")

    def _get_page_numbers(self, current, total):
        MAX = 13
        if total <= MAX:
            return list(range(1, total + 1))
        WINDOW = 5
        EDGE = 12
        if current <= EDGE:
            return list(range(1, EDGE + 1)) + ['...'] + [total]
        if current >= total - EDGE + 1:
            return [1, '...'] + list(range(total - EDGE + 1, total + 1))
        return ([1, '...'] +
                list(range(current - WINDOW, current + WINDOW + 1)) +
                ['...', total])

    def _build_pagination(self):
        while self.pagination_layout.count():
            ch = self.pagination_layout.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()
        if self.mode == "local" or self.total_pages <= 1:
            self.pagination_widget.hide()
            return

        H = 32
        NAV_W = 40
        ELLIPSIS_W = 24

        def num_w(text, active=False):
            w = 16 + 9 * len(text)
            if w < 34:
                w = 34
            if active:
                w += 6
            return w

        if self.current_page > 1:
            b = QPushButton("\u25c0")
            b.setStyleSheet(self._nav_btn_style())
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedSize(NAV_W, H)
            b.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
            self.pagination_layout.addWidget(b)

        for n in self._get_page_numbers(self.current_page, self.total_pages):
            if n == '...':
                lbl = QLabel("\u2026")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFixedSize(ELLIPSIS_W, H)
                lbl.setStyleSheet(self._ellipsis_style())
                self.pagination_layout.addWidget(lbl)
            else:
                txt = str(n)
                b = QPushButton(txt)
                is_active = (n == self.current_page)
                b.setStyleSheet(self._page_btn_style(active=is_active))
                b.setCursor(Qt.PointingHandCursor)
                w = num_w(txt, active=is_active)
                b.setFixedSize(w, H)
                if not is_active:
                    b.clicked.connect(lambda _, x=n: self.go_to_page(x))
                self.pagination_layout.addWidget(b)

        if self.current_page < self.total_pages:
            b = QPushButton("\u25b6")
            b.setStyleSheet(self._nav_btn_style())
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedSize(NAV_W, H)
            b.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
            self.pagination_layout.addWidget(b)

        self.pagination_widget.show()

    def _open_goto_dialog(self):
        if self.mode != "online" or self.total_pages <= 1:
            return
        n, ok = QInputDialog.getInt(
            self, "Go to page",
            f"Enter page number (1 \u2013 {self.total_pages}):",
            self.current_page, 1, self.total_pages, 1)
        if ok:
            self.go_to_page(n)

    def go_to_page(self, page):
        if self.mode != "online":
            return
        if page < 1 or page > self.total_pages:
            return
        if page == self.current_page:
            return
        self.current_page = page
        self.status.showMessage(T.get("loading", "Loading..."))
        self._clear()
        self.cards.clear()
        self._pending_thumbs.clear()
        self.scroll.verticalScrollBar().setValue(0)
        self._stop_thumbs()
        if self.wh_worker and self.wh_worker.isRunning():
            try:
                self.wh_worker.finished.disconnect()
                self.wh_worker.error.disconnect()
            except Exception:
                pass
            self.wh_worker.quit()
            self.wh_worker.wait()
        self.wh_worker = WallhavenWorker(
            query=self.search.text().strip(),
            categories=self._cats_bits(),
            purity=self._purity_bits(),
            sorting=self._sort_param(),
            page=page, api_key=get_api_key())
        self.wh_worker.finished.connect(self._on_results)
        self.wh_worker.error.connect(self._on_err)
        self.wh_worker.start()

    def load_local(self):
        if not self.download_folder or not self.download_folder.is_dir():
            self.items = []
            self._build_cards()
            self.pagination_widget.hide()
            self.page_lbl.setText("")
            self.status.showMessage("No results")
            return
        self.status.showMessage(T.get("loading", "Loading..."))
        self._clear()
        self.cards.clear()
        self.thumbs.clear()
        self._pending_thumbs.clear()
        self.page_lbl.setText("")
        self._stop_thumbs()
        files = []
        for p in self.download_folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXT:
                files.append(p)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        self.items = [{"id": p.stem, "url": str(p), "thumb": str(p),
                       "resolution": "", "_local": True,
                       "_path": str(p)} for p in files]
        self.status.showMessage("{} images".format(len(self.items)))
        self._build_cards()
        self.pagination_widget.hide()
        pairs = [(w["id"], w["thumb"]) for w in self.items
                 if w["id"] not in self.thumbs]
        if pairs:
            self.thumb_loader = ThumbLoaderPool(pairs, THUMB_PX, THUMB_WORKERS)
            self.thumb_loader.loaded.connect(self._on_thumb)
            self.thumb_loader.start()

    def _clear(self):
        while self.grid.count():
            ch = self.grid.takeAt(0)
            w = ch.widget()
            if w:
                try:
                    w.setParent(None)
                    w.deleteLater()
                except Exception:
                    pass
        # Event loop ga navbat berish
        QApplication.processEvents()

    def _calc_card_size(self):
        avail = self.scroll.viewport().width() - 10
        cols = 1 if self.fullscreen_grid else self.grid_cols
        spacing = 10
        w = max(140, (avail - spacing * (cols - 1)) // cols)
        h = int(w * 9 / 16)
        # Downloads indicator kengligini karta kengligiga moslash
        if hasattr(self, "dl_indicator"):
            try:
                self.dl_indicator.set_card_width(w)
            except Exception:
                pass
        return w, h

    def _is_current_wallpaper(self, wid):
        if not self.current_wallpaper_id:
            return False
        norm = wid.replace("wallhaven-", "")
        cur = self.current_wallpaper_id.replace("wallhaven-", "")
        return norm == cur

    def _build_cards(self):
        self._clear()
        self.cards.clear()
        if not self.items:
            return
        cols = 1 if self.fullscreen_grid else self.grid_cols
        w, h = self._calc_card_size()
        for i, item in enumerate(self.items):
            r, c = divmod(i, cols)
            if item.get("_local"):
                is_dl = True
            else:
                is_dl = self._is_downloaded(item["id"])
            is_cur = self._is_current_wallpaper(item["id"])
            cached_thumb = self.thumbs.get(item["id"])
            card = WallpaperCard(item, is_downloaded=is_dl,
                                 is_current=is_cur, card_size=(w, h),
                                 initial_pixmap=cached_thumb)
            card.clicked.connect(self.open_viewer)
            card.download_clicked.connect(self.do_download)
            card.set_bg_clicked.connect(self.do_set_bg)
            card.remove_clicked.connect(self.remove_wallpaper)
            if item["id"] in self.downloads:
                worker = self.downloads[item["id"]]
                state = ("paused" if not worker._pause.is_set()
                         else "downloading")
                card.set_download_state(state,
                                        getattr(worker, "_last_pct", 0))
            self.grid.addWidget(card, r, c)
            self.cards[item["id"]] = card

    def _relayout(self):
        if not self.items or not self.cards:
            return
        cols = 1 if self.fullscreen_grid else self.grid_cols
        w, h = self._calc_card_size()
        for i, item in enumerate(self.items):
            card = self.cards.get(item["id"])
            if not card:
                continue
            r, c = divmod(i, cols)
            card.setFixedSize(w, h)
            self.grid.addWidget(card, r, c)

    def eventFilter(self, obj, event):
        if obj is self.scroll.viewport() and event.type() == QEvent.Resize:
            self._resize_timer.start(150)
        # History ochiq bo'lganda bosishlarni tekshirish
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, "dl_list") and self.dl_list.isVisible():
                try:
                    widget = QApplication.widgetAt(event.globalPos())
                    inside = False
                    w = widget
                    while w is not None:
                        if w is self.dl_list or w is self.dl_indicator:
                            inside = True
                            break
                        w = w.parent()
                    if not inside:
                        self.dl_list.hide()
                except Exception:
                    pass
        return super().eventFilter(obj, event)

    def _find_downloaded_path(self, wid):
        if not self.download_folder or not self.download_folder.is_dir():
            return None
        for p in self.download_folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXT:
                if p.stem == wid or p.stem == f"wallhaven-{wid}":
                    return p
        return None

    def _is_downloaded(self, wid):
        return self._find_downloaded_path(wid) is not None

    def _dl_pause(self, wid):
        w = self.downloads.get(wid)
        if w:
            w.pause()

    def _dl_resume(self, wid):
        w = self.downloads.get(wid)
        if w:
            w.resume()

    def _dl_cancel(self, wid):
        w = self.downloads.get(wid)
        if w:
            w.cancel()
        self.downloads.pop(wid, None)
        card = self.cards.get(wid)
        if card:
            card.set_download_state("idle")
        self._refresh_dl_bar()

    def do_download(self, wid, with_dialog=False):
        item = next((w for w in self.items if w["id"] == wid), None)
        if not item:
            return
        if wid in self.downloads and self.downloads[wid].isRunning():
            self.status.showMessage(f"Already downloading: {wid}")
            return
        folder = self.download_folder
        if with_dialog:
            f = QFileDialog.getExistingDirectory(
                self, "Choose another folder",
                str(folder or Path.home()))
            if not f:
                return
            folder = Path(f)
        if not folder:
            self.choose_folder()
            folder = self.download_folder
            if not folder:
                return
        folder.mkdir(parents=True, exist_ok=True)
        if item.get("_local"):
            try:
                shutil.copy2(item["_path"],
                             folder / Path(item["_path"]).name)
                self.status.showMessage(
                    "✅ Downloaded: {}".format(Path(item["_path"]).name))
            except Exception as e:
                QMessageBox.critical(self, T.get("msg_download_error", "Download error"), str(e))
            return
        ext = Path(item["url"]).suffix or ".jpg"
        filename = f"wallhaven-{wid}{ext}"
        worker = DownloadWorker(wid, item["url"], folder, filename)
        worker.progress.connect(self._on_dl_progress)
        worker.finished.connect(self._on_downloaded)
        worker.error.connect(self._on_dl_error)
        worker.state.connect(self._on_dl_state)
        self.downloads[wid] = worker
        thumb_img = self.thumbs.get(wid)
        self.dl_list.add_download(wid, filename, thumb_img)
        self._refresh_dl_bar()
        card = self.cards.get(wid)
        if card:
            card.set_download_state("downloading", 0)
        worker.start()
        self.status.showMessage(f"\u2b07 {wid} ...")

    def _on_dl_progress(self, wid, got, total):
        pct = int(got * 100 / total) if total > 0 else 0
        worker = self.downloads.get(wid)
        if worker:
            worker._last_pct = pct
        self.dl_list.update_progress(wid, got, total)
        card = self.cards.get(wid)
        if card:
            state = ("paused"
                     if (worker and not worker._pause.is_set())
                     else "downloading")
            card.set_download_state(state, pct)

    def _on_dl_state(self, wid, state):
        self.dl_list.set_state(wid, state)
        self._refresh_dl_bar()
        card = self.cards.get(wid)
        if card:
            if state == "downloading":
                card.set_download_state(
                    "downloading",
                    getattr(self.downloads.get(wid), "_last_pct", 0))
            elif state == "paused":
                card.set_download_state(
                    "paused",
                    getattr(self.downloads.get(wid), "_last_pct", 0))
            elif state == "done":
                card.set_download_state("done")
            elif state == "error":
                card.set_download_state("error")
            elif state == "cancelled":
                card.set_download_state("idle")

    def _on_dl_error(self, wid, msg):
        QMessageBox.critical(self, T.get("msg_download_error", "Download error"), msg)

    def _on_downloaded(self, wid, path):
        self.status.showMessage("✅ Downloaded: {}".format(Path(path).name))
        w = self.downloads.pop(wid, None)
        if w:
            w.deleteLater()
        sb = self.scroll.verticalScrollBar()
        saved = sb.value()
        self._replace_card(wid)
        self._refresh_dl_bar()
        QTimer.singleShot(0, lambda: sb.setValue(saved))
        QTimer.singleShot(50, lambda: sb.setValue(saved))

    def _replace_card(self, wid):
        card = self.cards.get(wid)
        if not card:
            return
        try:
            card.width()  # valid?
        except Exception:
            return
        item = next((w for w in self.items if w["id"] == wid), None)
        if not item:
            return
        sb = self.scroll.verticalScrollBar()
        saved_pos = sb.value()
        try:
            self.grid_holder.setUpdatesEnabled(False)
            idx = self.items.index(item)
            cols = 1 if self.fullscreen_grid else self.grid_cols
            r, c = divmod(idx, cols)
            w, h = self._calc_card_size()
            was_current = card.is_current
            cached_thumb = self.thumbs.get(wid)
            try:
                card.setParent(None)
                card.deleteLater()
            except Exception:
                pass
            new_card = WallpaperCard(item, is_downloaded=True,
                                     is_current=was_current,
                                     card_size=(w, h),
                                     initial_pixmap=cached_thumb)
            new_card.clicked.connect(self.open_viewer)
            new_card.download_clicked.connect(self.do_download)
            new_card.set_bg_clicked.connect(self.do_set_bg)
            new_card.remove_clicked.connect(self.remove_wallpaper)
            new_card.set_download_state("done")
            self.grid.addWidget(new_card, r, c)
            self.cards[wid] = new_card
        finally:
            try:
                self.grid_holder.setUpdatesEnabled(True)
            except Exception:
                pass
        QTimer.singleShot(0, lambda: sb.setValue(saved_pos))
        QTimer.singleShot(50, lambda: sb.setValue(saved_pos))

    def _replace_card_undownloaded(self, wid):
        card = self.cards.get(wid)
        if not card:
            return
        item = next((w for w in self.items if w["id"] == wid), None)
        if not item:
            return
        idx = self.items.index(item)
        cols = 1 if self.fullscreen_grid else self.grid_cols
        r, c = divmod(idx, cols)
        w, h = self._calc_card_size()
        cached_thumb = self.thumbs.get(wid)
        if cached_thumb is None and card._pixmap is not None:
            cached_thumb = card._pixmap.toImage()
            self.thumbs[wid] = cached_thumb
        card.setParent(None)
        card.deleteLater()
        new_card = WallpaperCard(item, is_downloaded=False,
                                 is_current=False, card_size=(w, h),
                                 initial_pixmap=cached_thumb)
        new_card.clicked.connect(self.open_viewer)
        new_card.download_clicked.connect(self.do_download)
        new_card.set_bg_clicked.connect(self.do_set_bg)
        new_card.remove_clicked.connect(self.remove_wallpaper)
        self.grid.addWidget(new_card, r, c)
        self.cards[wid] = new_card

    def remove_wallpaper(self, wid):
        path = self._find_downloaded_path(wid)
        if not path or not path.exists():
            self._replace_card_undownloaded(wid)
            return
        name = path.name
        dlg = ConfirmDialog(
            self,
            T["confirm_delete_title"],
            T["confirm_delete_body"].format(name),
            yes_text=T["btn_yes"],
            no_text=T["btn_no"])
        dlg.exec_()
        if dlg.result_choice != ConfirmDialog.YES:
            return
        # Thread to'xtatish (fayl o'chirishdan OLDIN)
        self._stop_thumbs()
        try:
            path.unlink()
        except Exception as e:
            QMessageBox.critical(self, T.get("error_title", "Error"), str(e))
            return
        if self._is_current_wallpaper(wid):
            self.current_wallpaper_id = None
            self._save_cfg()
        self.status.showMessage("🗑 Removed: {}".format(name))
        if self.mode == "local":
            # Deferred reload — event handler tugagach
            QTimer.singleShot(80, self.load_local)
        else:
            self._replace_card_undownloaded(wid)

    def _mark_as_current(self, wid):
        print(f"[mark] current_wallpaper_id={wid}")
        old = self.current_wallpaper_id
        self.current_wallpaper_id = wid
        if old and old in self.cards:
            try:
                self.cards[old].set_current(False)
            except Exception as e:
                print(f"[mark] old card error: {e}")
        if wid in self.cards:
            try:
                self.cards[wid].set_current(True)
                print(f"[mark] card updated: {wid}")
            except Exception as e:
                print(f"[mark] new card error: {e}")
        self._save_cfg()


    def do_set_bg(self, wid):
        print(f"[set_bg] wid={wid}")
        path = self._find_downloaded_path(wid)
        if not path and self.download_folder:
            for p in self.download_folder.rglob("*"):
                if p.is_file() and p.stem.replace("wallhaven-", "") == wid:
                    path = p
                    break
        if not path or not path.exists():
            QMessageBox.warning(self, T.get("error_title", "Error"),
                                "File not found. Download first.")
            return
        # Cache'ga nusxa
        cached = self._cache_current_wallpaper(path)
        use_path = cached if cached else path
        print(f"[set_bg] use_path={use_path}")
        ok = set_wallpaper(str(use_path))
        print(f"[set_bg] result={ok}")
        if ok:
            self.status.showMessage(f"Wallpaper set: {path.name}")
            self._mark_as_current(wid)
        else:
            QMessageBox.critical(self, T.get("msg_failed", "Failed"),
                                 f"Path: {use_path}")


    def _cache_current_wallpaper(self, source_path):
        """Fon rasmini cache'ga nusxalaydi va validatsiya qiladi."""
        try:
            src = Path(source_path)
            if not src.is_file():
                print(f"[cache] source not found: {src}")
                return None
            # Fayl hajmi tekshirish
            if src.stat().st_size < 100:
                print(f"[cache] source too small: {src}")
                return None
            # Rasm validatsiyasi (PIL orqali)
            try:
                from PIL import Image as _PILImage
                with _PILImage.open(str(src)) as im:
                    im.verify()
            except Exception as e:
                print(f"[cache] image invalid: {e}")
                return None

            CURRENT_WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
            # Eski fayllarni o'chirish
            for old in CURRENT_WALLPAPER_DIR.iterdir():
                if old.name.startswith("current_wallpaper"):
                    try:
                        old.unlink()
                    except Exception:
                        pass
            ext = src.suffix.lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
                ext = ".jpg"
            target = CURRENT_WALLPAPER_DIR / f"current_wallpaper{ext}"
            shutil.copy2(str(src), str(target))
            # Nusxa to'g'ri ekanligini tekshirish
            if not target.is_file() or target.stat().st_size < 100:
                print(f"[cache] copy failed: {target}")
                return None
            print(f"[cache] cached: {target}")
            return target
        except Exception as e:
            print(f"[cache] error: {e}")
            return None


    def open_viewer(self, wid):
        idx = next((i for i, w in enumerate(self.items)
                    if w["id"] == wid), -1)
        if idx < 0:
            return
        v = ImageViewer(
            items=self.items, index=idx, parent=self,
            is_downloaded_func=lambda w: self._find_downloaded_path(w),
            do_download_func=lambda w, d=False: self.do_download(w, d),
            set_bg_func=lambda w: self.do_set_bg(w),
            thumb_cache=self.thumbs)
        v.exec_()
        for wid2, card in list(self.cards.items()):
            path = self._find_downloaded_path(wid2)
            if path and not card.is_downloaded:
                self._replace_card(wid2)

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName("uzAlhaitham's wallpaper Selector")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
