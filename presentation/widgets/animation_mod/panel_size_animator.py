from PySide6.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PySide6.QtWidgets import QWidget

class PanelSizeAnimator:
    """
    Animador profesional para paneles tipo QWidget.
    Permite animar en paralelo el ancho de la ventana principal y el panel, y luego la altura del panel.
    """
    def __init__(self, main_window: QWidget, panel: QWidget,
                 collapsed_width: int, expanded_width: int,
                 collapsed_height: int, expanded_height: int,
                 duration: int = 350, panel_duration: int = 300):
        self.main_window = main_window
        self.panel = panel
        self.collapsed_width = collapsed_width
        self.expanded_width = expanded_width
        self.collapsed_height = collapsed_height
        self.expanded_height = expanded_height
        self.duration = duration
        self.panel_duration = panel_duration
        self._anim_group = None
        self._anim_panel_height = None

    def open(self, on_finished=None):
        """
        Abre el panel: primero expande anchos en paralelo, luego la altura del panel.
        """
        self.panel.setMaximumHeight(self.collapsed_height)
        self.panel.setVisible(True)
        self._animate_widths(self.collapsed_width, self.expanded_width,
                            self.collapsed_width, self.expanded_width,
                            self.duration,
                            lambda: self._animate_panel_height(self.collapsed_height, self.expanded_height, True, on_finished))

    def close(self, on_finished=None):
        """
        Cierra el panel: primero colapsa anchos en paralelo, luego colapsa la altura.
        """
        def after_widths():
            self._animate_panel_height(self.expanded_height, self.collapsed_height, False, on_finished)
        self._animate_widths(self.expanded_width, self.collapsed_width,
                            self.expanded_width, self.collapsed_width,
                            self.duration, after_widths)

    def _animate_widths(self, start_main, end_main, start_panel, end_panel, duration, on_finished=None):
        anim_min_w = QPropertyAnimation(self.main_window, b"minimumWidth")
        anim_min_w.setDuration(duration)
        anim_min_w.setStartValue(start_main)
        anim_min_w.setEndValue(end_main)
        anim_min_w.setEasingCurve(QEasingCurve.Type.InOutQuart)

        anim_max_w = QPropertyAnimation(self.main_window, b"maximumWidth")
        anim_max_w.setDuration(duration)
        anim_max_w.setStartValue(start_main)
        anim_max_w.setEndValue(end_main)
        anim_max_w.setEasingCurve(QEasingCurve.Type.InOutQuart)

        anim_panel_w = QPropertyAnimation(self.panel, b"maximumWidth")
        anim_panel_w.setDuration(duration)
        anim_panel_w.setStartValue(start_panel)
        anim_panel_w.setEndValue(end_panel)
        anim_panel_w.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self._anim_group = QParallelAnimationGroup(self.main_window)
        self._anim_group.addAnimation(anim_min_w)
        self._anim_group.addAnimation(anim_max_w)
        self._anim_group.addAnimation(anim_panel_w)
        if on_finished:
            self._anim_group.finished.connect(on_finished)
        self._anim_group.start()

    def _animate_panel_height(self, start_h, end_h, show, on_finished=None):
        if self._anim_panel_height:
            self._anim_panel_height.stop()
        if show:
            self.panel.setVisible(True)
        self._anim_panel_height = QPropertyAnimation(self.panel, b"maximumHeight")
        self._anim_panel_height.setDuration(self.panel_duration)
        self._anim_panel_height.setStartValue(start_h)
        self._anim_panel_height.setEndValue(end_h)
        self._anim_panel_height.setEasingCurve(QEasingCurve.Type.OutExpo)
        def _finish():
            if not show:
                self.panel.setVisible(False)
            if on_finished:
                on_finished()
        self._anim_panel_height.finished.connect(_finish)
        self._anim_panel_height.start()
