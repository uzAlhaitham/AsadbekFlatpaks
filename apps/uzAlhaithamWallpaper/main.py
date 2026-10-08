#!/usr/bin/env python3
"""
main_animated.py — TEST animated version.

Animatsiyalar:
  • Card hover zoom + fade-in (stagger)
  • Scroll-to-top smooth
  • ImageViewer: fade-in, zoom, pan, Fit/100%
  • UI bars slide-in/out
  • Card click ripple
  • Pagination button press animation
  • Loading spinner (during load)
"""

import sys
from PyQt5.QtCore import (
    Qt, QTimer, QVariantAnimation, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QPoint, QRectF
)
from PyQt5.QtGui import (
    QColor, QBrush, QPixmap, QKeySequence, QPainter, QPen,
    QConicalGradient
)
from PyQt5.QtWidgets import (
    QGraphicsOpacityEffect, QGraphicsView, QGraphicsScene,
    QFrame, QPushButton, QShortcut, QWidget
)

import main_base as base


# ══════════════════════════════════════════════════════════════════
#  ZOOM VIEW
# ══════════════════════════════════════════════════════════════════
class ZoomView(QGraphicsView):
    ZOOM_MIN = 0.05
    ZOOM_MAX = 8.0
    ZOOM_STEP = 1.15

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHints(QPainter.SmoothPixmapTransform
                            | QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QGraphicsView {
                background: transparent;
                border: none;
            }

            /* Vertikal scrollbar */
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.2);
                width: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(200, 200, 200, 0.7);
                border-radius: 5px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(220, 220, 220, 0.9);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(90, 159, 212, 0.95);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background: transparent;
                height: 0;
                width: 0;
                border: none;
            }

            /* Gorizontal scrollbar */
            QScrollBar:horizontal {
                background: rgba(0, 0, 0, 0.2);
                height: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: rgba(200, 200, 200, 0.7);
                border-radius: 5px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(220, 220, 220, 0.9);
            }
            QScrollBar::handle:horizontal:pressed {
                background: rgba(90, 159, 212, 0.95);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                background: transparent;
                height: 0;
                width: 0;
                border: none;
            }

            /* Corner (scrollbarlar kesishgan joy) */
            QAbstractScrollArea::corner {
                background: rgba(0, 0, 0, 0.2);
                border: none;
            }
        """)
        self._scene = QGraphicsScene(self)
        self._scene.setBackgroundBrush(QBrush(Qt.transparent))
        self.setScene(self._scene)

        # Viewport va widget background to'liq shaffof
        self.setStyleSheet("background: transparent; border: none;")
        self.setBackgroundBrush(QBrush(Qt.transparent))
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
        self.viewport().setStyleSheet("background: transparent;")


        # Scrollbar'larga to'g'ridan-to'g'ri shaffof style
        scrollbar_style = """
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.02);
                width: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(200, 200, 200, 0.5);
                border-radius: 5px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(220, 220, 220, 0.8);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0;
                border: none;
            }

            QScrollBar:horizontal {
                background: rgba(255, 255, 255, 0.02);
                height: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: rgba(200, 200, 200, 0.5);
                border-radius: 5px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(220, 220, 220, 0.8);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                width: 0;
                border: none;
            }
        """

        self.horizontalScrollBar().setStyleSheet(scrollbar_style)
        self.verticalScrollBar().setStyleSheet(scrollbar_style)
        self.horizontalScrollBar().setAttribute(Qt.WA_TranslucentBackground)
        self.verticalScrollBar().setAttribute(Qt.WA_TranslucentBackground)
        # Corner widget
        self.setCornerWidget = None  # default corner

        # Rasm yuklanganda sceneRect'ni rasmga moslashtiradi


        # Scrollbar'larga to'g'ridan-to'g'ri shaffof style
        scrollbar_style = """
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.02);
                width: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(200, 200, 200, 0.5);
                border-radius: 5px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(220, 220, 220, 0.8);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0;
                border: none;
            }

            QScrollBar:horizontal {
                background: rgba(255, 255, 255, 0.02);
                height: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: rgba(200, 200, 200, 0.5);
                border-radius: 5px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(220, 220, 220, 0.8);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                width: 0;
                border: none;
            }
        """

        self.horizontalScrollBar().setStyleSheet(scrollbar_style)
        self.verticalScrollBar().setStyleSheet(scrollbar_style)
        self.horizontalScrollBar().setAttribute(Qt.WA_TranslucentBackground)
        self.verticalScrollBar().setAttribute(Qt.WA_TranslucentBackground)
        # Corner widget
        self.setCornerWidget = None  # default corner

        # Rasm yuklanganda sceneRect'ni rasmga moslashtiradi

        self._item = None
        self._zoom = 1.0
        self._fit_mode = True

        # ═══════════════════════════════════════════════════════
        #  SCROLLBAR STYLES — to'g'ridan-to'g'ri widget'larga
        # ═══════════════════════════════════════════════════════
        _sb_style = '''
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(220, 220, 220, 0.55);
                border-radius: 5px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(220, 220, 220, 0.85);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(90, 159, 212, 0.95);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background: transparent;
                height: 0;
                width: 0;
                border: none;
            }

            QScrollBar:horizontal {
                background: transparent;
                height: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: rgba(220, 220, 220, 0.55);
                border-radius: 5px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(220, 220, 220, 0.85);
            }
            QScrollBar::handle:horizontal:pressed {
                background: rgba(90, 159, 212, 0.95);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                background: transparent;
                height: 0;
                width: 0;
                border: none;
            }
        '''

        self.horizontalScrollBar().setStyleSheet(_sb_style)
        self.verticalScrollBar().setStyleSheet(_sb_style)

        # Viewport va fon shaffof
        self.setStyleSheet("QGraphicsView { background: transparent; border: none; }")
        self.setBackgroundBrush(QBrush(Qt.transparent))
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.viewport().setStyleSheet("background: transparent;")
        self.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
        self.viewport().setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        # Corner widget ham shaffof
        self.setCornerWidget = None  # default corner ishlatiladi

    def set_image(self, image):
        pm = QPixmap.fromImage(image)
        self._scene.clear()
        self._item = self._scene.addPixmap(pm)
        self._scene.setSceneRect(self._item.boundingRect())
        self._fit_mode = True
        self.fit_to_screen()

    def fit_to_screen(self):
        if self._item is None:
            return
        self.resetTransform()
        self.fitInView(self._item, Qt.KeepAspectRatioByExpanding)
        self._fit_mode = True
        self.centerOn(self._item)
        parent = self._parent_iv()
        if parent is not None:
            parent._raise_bars()

    def zoom_100(self):
        if self._item is None:
            return
        self.resetTransform()
        self._zoom = 1.0
        self._fit_mode = False
        self.centerOn(self._item)
        parent = self._parent_iv()
        if parent is not None:
            parent._raise_bars()

    def wheelEvent(self, event):
        if self._item is None:
            event.accept()
            return
        delta = event.angleDelta().y()
        if delta == 0:
            event.accept()
            return

        factor = self.ZOOM_STEP if delta > 0 else 1.0 / self.ZOOM_STEP
        new_zoom = self._zoom * factor
        if new_zoom < self.ZOOM_MIN or new_zoom > self.ZOOM_MAX:
            event.accept()
            return

        self._fit_mode = False
        self.scale(factor, factor)
        self._zoom = new_zoom
        parent = self._parent_iv()
        if parent is not None:
            parent._raise_bars()
        event.accept()

    # ── Mouse events ──
    WINDOW_DRAG_ZONE = 40

    def _parent_iv(self):
        w = self.parent()
        while w is not None and not isinstance(w, AnimatedImageViewer):
            w = w.parent()
        return w

    def mousePressEvent(self, e):
        # Faqat chap tugma rasm pan uchun (resize/drag OS tomonidan)
        if e.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(e)
        else:
            e.ignore()

    def mouseMoveEvent(self, e):
        # Faqat UI timer reset
        parent = self._parent_iv()
        if parent is not None:
            try:
                parent._show_ui()
                if hasattr(parent, "_hide_timer"):
                    parent._hide_timer.start(2000)
            except Exception:
                pass
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        # Double-click -> Fit toggle
        parent = self._parent_iv()
        if parent is not None and e.button() == Qt.LeftButton:
            parent._zoom_view.fit_to_screen()
            e.accept()
            return
        e.ignore()

    def enterEvent(self, e):
        parent = self._parent_iv()
        if parent is not None:
            try:
                parent._show_ui()
                if hasattr(parent, "_hide_timer"):
                    parent._hide_timer.start(2000)
            except Exception:
                pass
        super().enterEvent(e)

    def leaveEvent(self, e):
        parent = self._parent_iv()
        if parent is not None:
            try:
                if hasattr(parent, "_hide_timer"):
                    parent._hide_timer.start(2000)
            except Exception:
                pass
        super().leaveEvent(e)


# ══════════════════════════════════════════════════════════════════
#  RIPPLE — Card bosilganda to'lqin
# ══════════════════════════════════════════════════════════════════
class RippleOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._radius = 0
        self._max_radius = 0
        self._center = QPoint(0, 0)
        self._opacity = 0.0
        self.hide()

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(800)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)

    def trigger(self, pos):
        self._center = pos
        w, h = self.width(), self.height()
        # Eng uzoq burchakgacha masofa
        corners = [QPoint(0, 0), QPoint(w, 0), QPoint(0, h), QPoint(w, h)]
        self._max_radius = max(
            ((pos.x() - c.x()) ** 2 + (pos.y() - c.y()) ** 2) ** 0.5
            for c in corners)
        self._radius = 0
        self._opacity = 0.55
        self.show()
        self.raise_()
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _on_anim(self, t):
        t = float(t)
        self._radius = self._max_radius * t
        self._opacity = 0.55 * (1.0 - t)
        self.update()
        if t >= 1.0:
            self.hide()

    def paintEvent(self, e):
        if self._radius <= 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        color = QColor(255, 255, 255)
        color.setAlphaF(self._opacity)
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(self._center, int(self._radius), int(self._radius))


# ══════════════════════════════════════════════════════════════════
#  1. CARD — hover zoom + fade-in + click ripple
# ══════════════════════════════════════════════════════════════════
class AnimatedWallpaperCard(base.WallpaperCard):
    ZOOM_DURATION = 400
    FADE_DURATION = 700

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._zoom_anim = QVariantAnimation(self)
        self._zoom_anim.setDuration(self.ZOOM_DURATION)
        self._zoom_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._zoom_anim.valueChanged.connect(self._on_zoom_value)

        # Ripple overlay
        self._ripple = RippleOverlay(self)
        self._ripple.setGeometry(0, 0, self.width(), self.height())

    def _on_zoom_value(self, value):
        self._zoom = float(value)
        self._cache_key = None
        self._render()

    def _animate_zoom_to(self, target):
        self._zoom_anim.stop()
        self._zoom_anim.setStartValue(float(self._zoom))
        self._zoom_anim.setEndValue(float(target))
        self._zoom_anim.start()

    def enterEvent(self, e):
        self._animate_zoom_to(self.ZOOM)
        self.hover_bar.show()
        self.hover_bar.raise_()
        if self.remove_btn.isVisible():
            self.remove_btn.raise_()

    def leaveEvent(self, e):
        self._animate_zoom_to(1.0)
        self.hover_bar.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "_ripple"):
            self._ripple.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            pos = e.pos()
            # Tugmalar ustida emas
            if not (self.hover_bar.isVisible()
                    and self.hover_bar.geometry().contains(pos)):
                self._ripple.trigger(pos)
        super().mousePressEvent(e)

    def fade_in(self, delay=0):
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(self.FADE_DURATION)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: self.setGraphicsEffect(None))

        self._fade_anim = anim
        if delay > 0:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()


# ══════════════════════════════════════════════════════════════════
#  Pagination tugmalar uchun press animatsiya
# ══════════════════════════════════════════════════════════════════
def _install_button_press_anim(btn):
    """Bosilganda botish, qo'yib yuborganda ko'tarilish."""
    if getattr(btn, "_press_anim_installed", False):
        return
    btn._press_anim_installed = True

    orig_geo_func = None  # geometry animatsiyasi ishlatilmaydi

    def press_in():
        a = QPropertyAnimation(btn, b"geometry", btn)
        g = btn.geometry()
        small = g.adjusted(2, 2, -2, -2)
        a.setDuration(150)
        a.setStartValue(g)
        a.setEndValue(small)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        btn._press_a = a

    def press_out():
        a = QPropertyAnimation(btn, b"geometry", btn)
        g = btn.geometry()
        big = g.adjusted(-2, -2, 2, 2)
        a.setDuration(220)
        a.setStartValue(g)
        a.setEndValue(big)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        btn._press_a = a

    btn.pressed.connect(press_in)
    btn.released.connect(press_out)


# ══════════════════════════════════════════════════════════════════
#  2. MAIN WINDOW
# ══════════════════════════════════════════════════════════════════
class AnimatedMainWindow(base.MainWindow):

    def _build_cards(self):
        super()._build_cards()
        for i, card in enumerate(self.cards.values()):
            if hasattr(card, "fade_in"):
                card.fade_in(delay=i * 60)

    def refresh(self):
        super().refresh()
        QTimer.singleShot(50, self._animate_scroll_to_top)

    def _animate_scroll_to_top(self):
        sb = self.scroll.verticalScrollBar()
        if sb.value() == 0:
            return
        anim = QPropertyAnimation(sb, b"value", self)
        anim.setDuration(650)
        anim.setStartValue(sb.value())
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._scroll_anim = anim

    def _build_pagination(self):
        super()._build_pagination()
        # Pagination tugmalar uchun press animatsiya
        for i in range(self.pagination_layout.count()):
            w = self.pagination_layout.itemAt(i).widget()
            if isinstance(w, QPushButton):
                _install_button_press_anim(w)


# ══════════════════════════════════════════════════════════════════
#  LOADING SPINNER
# ══════════════════════════════════════════════════════════════════
class SpinnerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.hide()

    def start(self):
        self._timer.start(50)
        self.show()
        self.raise_()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _tick(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -4)
        pen = QPen(QColor("#5a9fd4"))
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, int(self._angle * 16), int(120 * 16))


# ══════════════════════════════════════════════════════════════════
#  3. IMAGE VIEWER
# ══════════════════════════════════════════════════════════════════
class AnimatedImageViewer(base.ImageViewer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Yashirin img_label
        self.img_label.hide()
        self.img_label.move(-10000, -10000)

        # Zoom view
        self._zoom_view = ZoomView(self)
        self._zoom_view.setGeometry(0, 0, self.width(), self.height())
        self._zoom_view.hide()

        # Spinner
        self._spinner = SpinnerWidget(self)
        self._spinner.setFixedSize(40, 40)

        # Fit / 100% tugmalar
        self._btn_fit = self._mk_text_btn("Fit")
        self._btn_fit.setToolTip("Fit to screen (F)")
        self._btn_fit.clicked.connect(self._zoom_view.fit_to_screen)
        _install_button_press_anim(self._btn_fit)

        self._btn_100 = self._mk_text_btn("100%")
        self._btn_100.setToolTip("Original size (1)")
        self._btn_100.clicked.connect(self._zoom_view.zoom_100)
        _install_button_press_anim(self._btn_100)

        tb_lay = self.top_bar.layout()
        tb_lay.insertWidget(0, self._btn_fit)
        tb_lay.insertWidget(1, self._btn_100)
        self.top_bar.adjustSize()
        self._position_bars()

        # Shortcuts
        QShortcut(QKeySequence("F"), self, self._zoom_view.fit_to_screen)
        QShortcut(QKeySequence("1"), self, self._zoom_view.zoom_100)

        # Scrollbar'larni to'g'ridan-to'g'ri shaffof qilamiz
        for sb in (self._zoom_view.horizontalScrollBar(),
                   self._zoom_view.verticalScrollBar()):
            sb.setStyleSheet("""
                QScrollBar { background: transparent; border: none; }
                QScrollBar::handle {
                    background: rgba(200,200,200,0.5);
                    border-radius: 5px;
                    margin: 2px;
                }
                QScrollBar::handle:hover {
                    background: rgba(220,220,220,0.8);
                }
                QScrollBar::add-line, QScrollBar::sub-line,
                QScrollBar::add-page, QScrollBar::sub-page {
                    background: transparent; border: none;
                    width: 0; height: 0;
                }
                QScrollBar::up-arrow, QScrollBar::down-arrow,
                QScrollBar::left-arrow, QScrollBar::right-arrow {
                    background: transparent; border: none;
                }
            """)

        self._zoom_view.horizontalScrollBar().valueChanged.connect(
            self._raise_bars)
        self._zoom_view.verticalScrollBar().valueChanged.connect(
            self._raise_bars)

    def _mk_text_btn(self, text):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(34)
        b.setMinimumWidth(56)
        b.setStyleSheet("""
            QPushButton { background: rgba(35,35,35,0.85);
                color:#e8e8e8; border:1px solid #ffffff;
                border-radius: 11px; font-size: 12px;
                font-weight: bold; padding: 0 12px; }
            QPushButton:hover { background: rgba(55,55,55,1.0); }
        """)
        return b

    def _apply_scrollbar_style(self):
        """Scrollbar'larga shaffof style qayta qo'llash."""
        if not hasattr(self, "_zoom_view"):
            return
        sb = self._zoom_view
        sb_style = """
            QScrollBar {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical { width: 10px; }
            QScrollBar:horizontal { height: 10px; }
            QScrollBar::handle {
                background: rgba(220, 220, 220, 0.55);
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:hover {
                background: rgba(220, 220, 220, 0.85);
            }
            QScrollBar::add-line, QScrollBar::sub-line,
            QScrollBar::add-page, QScrollBar::sub-page {
                background: transparent;
                border: none;
                width: 0; height: 0;
            }
            QScrollBar::up-arrow, QScrollBar::down-arrow,
            QScrollBar::left-arrow, QScrollBar::right-arrow {
                background: transparent;
                border: none;
            }
        """
        sb.horizontalScrollBar().setStyleSheet(sb_style)
        sb.verticalScrollBar().setStyleSheet(sb_style)
        sb.viewport().setStyleSheet("background: transparent;")
        sb.viewport().setAutoFillBackground(False)

    def _raise_bars(self):
        try:
            self._position_bars()
            if self.top_bar.isHidden():
                self.top_bar.show()
            if self.bar.isHidden():
                self.bar.show()
            self.top_bar.raise_()
            self.bar.raise_()
            if hasattr(self, "_hide_timer"):
                self._hide_timer.start(2000)
        except Exception:
            pass

    # ---------- Rendering ----------
    def _on_full_loaded(self, img):
        if img is None or img.isNull():
            return
        self._pix = img
        if img.height() > 0:
            self._aspect = img.width() / img.height()
        self._zoom_view.set_image(img)
        # Scrollbar shaffofligini qayta qo'llash (set_image reset qilishi mumkin)
        self._apply_scrollbar_style()
        self._zoom_view.show()
        self._zoom_view.raise_()
        self._spinner.stop()
        self._position_bars()
        self._zoom_view.setFocus()

    def _on_full_error(self, msg):
        self._spinner.stop()
        super()._on_full_error(msg)

    def _load(self):
        # Loading boshlanganda spinner'ni ko'rsatamiz (agar mavjud bo'lsa)
        spinner = getattr(self, "_spinner", None)
        if spinner is not None:
            spinner.start()
            spinner.setFixedSize(40, 40)
            spinner.move(
                (self.width() - 40) // 2,
                (self.height() - 40) // 2)
        super()._load()

    def _update(self):
        pass

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._zoom_view.setGeometry(0, 0, self.width(), self.height())
        self._spinner.move(
            (self.width() - 40) // 2,
            (self.height() - 40) // 2)
        if self._zoom_view._fit_mode:
            QTimer.singleShot(0, self._zoom_view.fit_to_screen)
        self._position_bars()

    def showEvent(self, e):
        super().showEvent(e)
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(450)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: self.setGraphicsEffect(None))
        anim.start()
        self._fade_anim = anim


# ══════════════════════════════════════════════════════════════════
#  4. SETTINGS DIALOG
# ══════════════════════════════════════════════════════════════════
class AnimatedSettingsDialog(base.SettingsDialog):

    def showEvent(self, e):
        super().showEvent(e)
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)

        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(450)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)
        fade.finished.connect(lambda: self.setGraphicsEffect(None))
        self._fade_anim = fade
        fade.start()


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    base.WallpaperCard = AnimatedWallpaperCard
    base.MainWindow = AnimatedMainWindow
    base.ImageViewer = AnimatedImageViewer
    base.SettingsDialog = AnimatedSettingsDialog
    base.main()


if __name__ == "__main__":
    main()
