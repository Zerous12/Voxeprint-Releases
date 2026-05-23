from PySide6.QtCore import Qt, QPointF, QVariantAnimation, QThread, Signal, Slot
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget
import math
import threading
from time import perf_counter

from core.utils.logger import logger


class _AsyncWorker(QThread):
    """Hilo auxiliar interno para ejecutar trabajo pesado sin bloquear la UI."""
    done = Signal(object, object)  # (resultado, excepcion)

    def __init__(self, fn, args, kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.done.emit(result, None)
        except Exception as exc:
            logger.log_exception("AsyncWorker", exc, f"{self._fn.__name__}")
            self.done.emit(None, exc)


class WaitingCircle(QWidget):
    def __init__(self, parent=None, radius=21, segment_radius=7, colors=None):
        super().__init__(parent)
        # Configuración de ventana para estar sobre todo y ser transparente
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.radius = radius
        self.segment_radius = segment_radius
        self.num_segments = 7
        self.colors = colors or [QColor(0, 120, 215), QColor(0, 200, 50), QColor(0, 188, 212),
                                 QColor(255, 255, 0), QColor(255, 87, 34), QColor(244, 67, 54), QColor(156, 39, 176)]

        # Tamaño basado en la geometría para evitar recortes
        self.widget_diameter = 2 * (self.radius + self.segment_radius + 5)
        self.setFixedSize(self.widget_diameter, self.widget_diameter)

        self.angle_offset = 0

        # Animación de rotación
        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setDuration(1500)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self._on_animation_updated)

        # Métricas de diagnóstico para detectar microcortes del loop de UI.
        self._last_frame_ts = None
        self._last_stutter_log_ts = 0.0
        self._stutter_threshold_ms = 80.0
        self._run_started_ts = 0.0

        # Estado para run_async
        self._on_result_callback = None
        self._worker = None

    def _on_animation_updated(self, value):
        now_ts = perf_counter()
        if self._last_frame_ts is not None:
            frame_delta_ms = (now_ts - self._last_frame_ts) * 1000
            if frame_delta_ms >= self._stutter_threshold_ms and (now_ts - self._last_stutter_log_ts) >= 0.5:
                self._last_stutter_log_ts = now_ts
                logger.warning(
                    "WaitingCircle",
                    (
                        f"ui_frame_stutter frame_ms={frame_delta_ms:.1f} "
                        f"qt_thread={id(QThread.currentThread())} py_thread={threading.get_ident()}"
                    )
                )
        self._last_frame_ts = now_ts
        self.angle_offset = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        center = QPointF(self.width() / 2, self.height() / 2)

        for s in range(self.num_segments):
            seg_angle = s * (360 / self.num_segments) + self.angle_offset
            rad = math.radians(seg_angle)
            x = center.x() + math.cos(rad) * self.radius
            y = center.y() + math.sin(rad) * self.radius
            painter.setBrush(self.colors[s % len(self.colors)])
            painter.drawEllipse(QPointF(x, y), self.segment_radius, self.segment_radius)
        painter.end()

    def superposition(self, enabled: bool):
        if enabled:
            self._recenter()
            self.show()
            self.raise_()
        else:
            self.close()

    def _recenter(self):
        """Centra el widget perfectamente sobre su padre."""
        if self.parent():
            p_rect = self.parent().rect()
            p_pos = self.parent().mapToGlobal(p_rect.topLeft())
            self.move(
                p_pos.x() + (p_rect.width() - self.width()) // 2,
                p_pos.y() + (p_rect.height() - self.height()) // 2
            )

    def start(self):
        """Inicia la animación de espera."""
        self._run_started_ts = perf_counter()
        self._last_frame_ts = None
        self.animation.start()

    def stop(self):
        """Detiene la animación y cierra el overlay."""
        self.animation.stop()
        self.close()

    def run_async(self, fn, on_result, *args, **kwargs):
        """
        Muestra la animación, ejecuta `fn` en un hilo secundario y al terminar
        detiene la animación y llama a `on_result(result, error)` en el hilo principal.
        """
        self.start()
        self._on_result_callback = on_result
        self._worker = _AsyncWorker(fn, args, kwargs)
        self._worker.done.connect(self._on_worker_done)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    @Slot(object, object)
    def _on_worker_done(self, result, error):
        """Slot ejecutado en el hilo principal gracias a AutoConnection con QObject."""
        callback = self._on_result_callback
        self._on_result_callback = None
        self.stop()
        if callback:
            callback(result, error)

    @Slot()
    def _on_worker_finished(self):
        """Limpia el worker cuando el hilo termina."""
        if self._worker:
            worker = self._worker
            self._worker = None
            worker.deleteLater()
