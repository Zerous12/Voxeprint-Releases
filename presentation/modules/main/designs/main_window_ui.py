from PySide6.QtCore import (QSize, Qt, QCoreApplication, QRect, QMetaObject)
from PySide6.QtGui import (QFont, QIcon,QCursor, QPixmap, QPalette, QColor, QBrush)
from PySide6.QtWidgets import (QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout, QAbstractSpinBox,
                                QPushButton, QFrame, QLabel, QTabWidget, QCheckBox, QComboBox,
                                QLineEdit, QSpinBox, QPlainTextEdit, QTextEdit, QGroupBox,
                                QTableWidgetItem, QSpacerItem, QGridLayout, QTableWidget, QLayout,
                                QAbstractItemView, QAbstractScrollArea, QDateEdit, QDoubleSpinBox, QToolButton,
                                QScrollBar, QCalendarWidget, QRadioButton, QStackedWidget)


class Ui_MainPanel(object):
    def setupUi(self, MainPanel):
        if not MainPanel.objectName():
            MainPanel.setObjectName(u"MainPanel")
        MainPanel.setWindowModality(Qt.WindowModality.WindowModal)
        MainPanel.resize(971, 706)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainPanel.sizePolicy().hasHeightForWidth())
        MainPanel.setSizePolicy(sizePolicy)
        MainPanel.setMinimumSize(QSize(652, 705))
        MainPanel.setStyleSheet(u"")
        MainPanel.setIconSize(QSize(28, 28))
        MainPanel.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.styleSheet = QWidget(MainPanel)
        self.styleSheet.setObjectName(u"styleSheet")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet(u"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"\n"
"SET APP STYLESHEET - FULL STYLES HERE\n"
"DARK THEME - BELIZER COLOR BASED\n"
"\n"
"///////////////////////////////////////////////////////////////////////////////////////////////// */\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QStackedWidget*/\n"
"QStackedWidget > QWidget {\n"
"background-color: transparent;\n"
"color: rgb(255, 255, 255);\n"
"}\n"
"QFrame#frame_content{\n"
"border: none;\n"
"background-color: transparent;\n"
"}\n"
"QFrame#frame_ajust{\n"
"border: none;\n"
"background-color: #026467;\n"
"}\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Bg App */\n"
"#bgApp{	\n"
"	background-color: rgb(30, 90, 125);\n"
"	border: 1px solid rgb(44, 49, 58);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
""
                        "Left Menu */\n"
"#leftMenuBg {	\n"
"	background-color: rgb(33, 37, 43);		\n"
"}\n"
"#topLogo {\n"
"	background-color: rgb(33, 37, 43);		\n"
"}\n"
"#titleLeftApp { \n"
"font: 63 12pt \"Segoe UI Semibold\"; \n"
"color: rgb(255, 255, 255);\n"
" }\n"
"#titleLeftDescription { \n"
"font: 8pt \"Segoe UI\"; \n"
"color: rgb(43, 150, 108);\n"
"} \n"
"/* Title Menu */\n"
"#titleRightInfo { padding-left: 10px;\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Content App */\n"
"#contentTopBg{	\n"
"	background-color: rgb(33, 37, 43);	\n"
"}\n"
"#contentBottom{\n"
"	border-top: 3px solid rgb(44, 49, 58);\n"
"}\n"
"/* Bottom Bar */\n"
"#bottomBar { background-color: rgb(44, 49, 58); }\n"
"#bottomBar QLabel { font-size: 11px; color: rgb(113, 126, 149); padding-left: 10px; padding-right: 10px; padding-bottom: 2px; }\n"
"\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"CheckBox */\n"
"QCheckBox"
                        "::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background: 3px solid rgb(52, 59, 72);\n"
"	border: 3px solid rgb(52, 59, 72);		\n"
"	image: url(:/resources/resources/icons/sys_select.svg);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"RadioButton */\n"
"QRadioButton::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"\n"
"QRadioButton::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"\n"
"QRadioButton::indicator:checked {\n"
"    background: 3px solid rgb(94, 106, 130);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"}\n"
"/* /////////////////////////////////////////////"
                        "////////////////////////////////////////////////////\n"
"ComboBox */\n"
"QComboBox {\n"
"	border-radius: 5px;\n"
"	padding: 2px 2px 2px 8px ;	\n"
"}\n"
"QComboBox:disabled {\n"
"    border-radius: 5px;\n"
"    padding: 2px 2px 2px 8px ;	\n"
"}\n"
"QComboBox::drop-down {\n"
"	subcontrol-origin: padding;\n"
"	subcontrol-position: top right;\n"
"	width: 26px; 	\n"
"	padding: 3px 2px 3px 2px ;	\n"
"	border-radius: 3px;\n"
"	image: url(:/resources/resources/icons/sys_arrow_down.svg);\n"
"	background-color: rgb(33, 37, 43);\n"
" }\n"
"\n"
"QComboBox::drop-down:hover { \n"
"	background-color: #7bd17b;\n"
"}\n"
"\n"
"QComboBox::drop-down:pressed {  \n"
"    background-color: rgb(246, 181, 101);\n"
"}\n"
"QComboBox QAbstractItemView{	\n"
"	border-radius: 3px;\n"
"}\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QListView */\n"
"QListView {	\n"
"	padding: 2px;\n"
"  	outline: 0px;\n"
"}\n"
"\n"
"QListView::item { \n"
"	padding: 2px;\n"
"}\n"
"\n"
"/* ////////"
                        "/////////////////////////////////////////////////////////////////////////////////////////\n"
"ScrollBars */\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 8px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: #7f8c8d;\n"
"    min-width: 25px;\n"
"	border-radius: 4px;\n"
"}\n"
"QScrollBar::handle:horizontal:hover {\n"
"   background-color: #46aa8f;   \n"
"}\n"
"QScrollBar::handle:horizontal:pressed {\n"
"   background-color:  #58d2b2;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-right-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-bottom-left"
                        "-radius: 4px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::left-arrow:horizontal {\n"
"    border-top-left-radius: 4px;\n"
"    border-bottom-left-radius: 4px;\n"
"}\n"
"QScrollBar::right-arrow:horizontal {\n"
"    border-top-right-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"}\n"
"QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {\n"
"    background: none;\n"
"}\n"
"QScrollBar::left-arrow:horizontal:hover, QScrollBar::right-arrow:horizontal:hover {\n"
"    background: #46aa8f;\n"
"}\n"
"QScrollBar::left-arrow:horizontal:pressed, QScrollBar::right-arrow:horizontal:pressed {\n"
"    background: #58d2b2;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal{\n"
"     background: none;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 8px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {\n"
"	background: #7f8c8d"
                        ";\n"
"    min-height: 25px;\n"
"	border-radius: 4px;\n"
" }\n"
" QScrollBar::handle:vertical:hover {\n"
"	background-color: #46aa8f;   \n"
" }\n"
"QScrollBar::handle:vertical:pressed {\n"
"	background-color:  #58d2b2;   \n"
" }\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"    subcontrol-position: bottom;\n"
"    subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"    subcontrol-position: top;\n"
"    subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::up-arrow:vertical{\n"
"  border-top-left-radius: 4px;\n"
"  border-top-right-radius: 4px;\n"
"}\n"
"QScrollBar::down-arrow:vertical {\n"
"   border-bottom-left-radius: 4px;\n"
"   border-bottom-right-radius: 4px;\n"
" }\n"
" QScrollBar::up-a"
                        "rrow:vertical, QScrollBar::down-arrow:vertical {\n"
"    background: none;\n"
" }\n"
" QScrollBar::up-arrow:vertical:hover, QScrollBar::down-arrow:vertical:hover {\n"
"    background: #46aa8f;\n"
" }\n"
"QScrollBar::up-arrow:vertical:pressed, QScrollBar::down-arrow:vertical:pressed {\n"
"     background: #58d2b2;\n"
" }\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"CalendarWidget */\n"
"QDateEdit {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(255, 255, 255);\n"
"	border-radius: 5px;\n"
"	border: 1px solid rgb(33, 37, 43);\n"
"	padding: 2px;\n"
"	padding-left: 8px;\n"
"}\n"
"QDateEdit::drop-down {\n"
"	subcontrol-origin: padding;\n"
"	subcontrol-position: top right;\n"
"	width: 25px; \n"
"	border-left-width: 3px;\n"
"	border-left-color: rgb(33, 37, 43);\n"
"	border-left-style: solid;\n"
"	border-top-right-radius: 3px;\n"
"	border-bottom"
                        "-right-radius: 3px;		\n"
"	image: url(:/resources/resources/icons/sys_calendar_1.svg);\n"
"	background-color: rgb(33, 37, 43);	\n"
" }\n"
"QDateEdit::drop-down:selected {\n"
"    border-left-color:  rgb(0, 163, 245);\n"
"	background-color: rgb(0, 163, 245);\n"
"}\n"
"\n"
"QDateEdit::drop-down:pressed {\n"
"    border-left-color:   rgb(246, 181, 101);\n"
"    background-color: rgb(246, 181, 101);\n"
"}\n"
"\n"
"QCalendarWidget QTableView {\n"
"    alternate-background-color: transparent;  	\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar {\n"
"	background-color: rgb(33, 37, 43);\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	border-bottom: 0px;\n"
"	border-top-left-radius: 5px;\n"
"	border-top-right-radius: 5px;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_prevmonth,\n"
"QCalendarWidget QWidget#qt_calendar_nextmonth{\n"
"	border: none;\n"
"	qproperty-icon: none;\n"
"	min-width: 16px;\n"
"	max-width: 16px;\n"
"	min-height: 16px;\n"
"	max-height: 16px;\n"
"	border-radius: 3px;\n"
"	background-colo"
                        "r: transparent;\n"
"	padding: 5px;\n"
"	}\n"
"QCalendarWidget QWidget#qt_calendar_nextmonth{\n"
"	margin-right: 5px; \n"
"	padding-left: 5px;	\n"
"	image: url(:/resources/resources/icons/sys_arrow_right.svg);	\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_prevmonth{\n"
"	margin-left: 5px;		\n"
"	image: url(:/resources/resources/icons/sys_arrow_left.svg);\n"
"} \n"
"QCalendarWidget QWidget#qt_calendar_prevmonth:hover,\n"
"QCalendarWidget QWidget#qt_calendar_nextmonth:hover{\n"
"	background-color: #46aac4;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_prevmonth:pressed,\n"
"QCalendarWidget QWidget#qt_calendar_nextmonth:pressed{\n"
"	background-color: #ffaa00;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearbutton{\n"
"	color: rgb(255, 255, 255);\n"
"	font-size: 13px;\n"
"	border-radius: 3px;\n"
"	background-color: transparent;\n"
"	padding: 0px 10px;\n"
"	margin-left: 15px;\n"
"	margin-top: 5px;\n"
"	margin-bottom: 5px;\n"
"	margin-right: 5px;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_monthbutton{\n"
"	wid"
                        "th: 70px;\n"
"	min-height: 22px;\n"
"	max-height: 22px;\n"
"	color: rgb(255, 255, 255);\n"
"	font-size: 13px;\n"
"	background-color: transparent;\n"
"	border-radius: 3px;\n"
"	padding: 5px 6px;\n"
"	margin-top: 5px;\n"
"	margin-bottom: 5px;\n"
"	margin-right: 20px;\n"
"	margin-left: 1px;	\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_yearbutton:hover,\n"
"QCalendarWidget QWidget#qt_calendar_monthbutton:hover{\n"
"	background-color: #46aac4;\n"
"	color: #ffffff;\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_yearbutton:pressed,\n"
"QCalendarWidget QWidget#qt_calendar_monthbutton:pressed{\n"
"	background-color: #46aa8f;\n"
"	color: #ffffff;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearedit{\n"
"	width: 60px;\n"
"	color: rgb(255, 255, 255);\n"
"	background-color: transparent;\n"
"	font-size: 14px;\n"
"	font-weight: bold;	\n"
"	margin-left: 5px;\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::down-button,\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::up-button{\n"
"	qproperty-icon: n"
                        "one;\n"
"	width: 16px;\n"
"	height: 16px;\n"
"	border-radius: 14px;	\n"
"	padding: 6px;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::down-button:hover,\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::up-button:hover{\n"
"	background-color: #46aac4;\n"
"	color: #ffffff;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::down-button:pressed,\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::up-button:pressed{\n"
"	background-color: #ffaa00;\n"
"	color: #ffffff;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::down-button{	\n"
"	image: url(:/resources/resources/icons/sys_caret_down_alt.svg);\n"
"	subcontrol-position: left;\n"
"	subcontrol-origin: margin;\n"
"	margin-top: 0px;\n"
"	margin-bottom: 0px;\n"
"	margin-right: 0px;\n"
"	margin-left: 0px;	\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_yearedit::up-button{\n"
"	image: url(:/resources/resources/icons/sys_caret_up_alt.svg);\n"
"	subcontrol-position: right;\n"
"	subcontrol-origin: margin; 	\n"
"	margin-top: 0px;\n"
"	margin-bottom: 0p"
                        "x;\n"
"	margin-right: 0px;\n"
"	margin-left: 0px;	\n"
"}\n"
"\n"
"QCalendarWidget QWidget#qt_calendar_calendarview{\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	border-top: transparent;\n"
"	border-top-left-radius: 0px;\n"
"	border-top-right-radius: 0px;\n"
"	border-bottom-left-radius: 2px;\n"
"	border-bottom-right-radius: 2px;\n"
"	padding: 0px 0px 0px 0px;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_calendarview::item:hover{\n"
"	border-radius: 3px;\n"
"	background-color: rgb(0, 170, 255);\n"
"	color: #ffffff;\n"
"}\n"
"QCalendarWidget QWidget#qt_calendar_calendarview::item:selected{\n"
"	border-radius: 3px;\n"
"	background-color: rgb(0, 170, 127);\n"
"}\n"
"QCalendarWidget QMenu {  \n"
"	margin: 2px;\n"
"	border-radius:  3px;\n"
"}\n"
"QCalendarWidget QMenu::item {\n"
"    padding: 2px 25px 2px 20px;\n"
"    border: 1px solid transparent;\n"
"}\n"
"QCalendarWidget QMenu::item:enabled:selected {    \n"
"    background: #009fef;\n"
"	color: #ffffff;\n"
"}\n"
"QCalendarWidget QMenu::item:enabled:pressed {\n"
""
                        "    background-color: #ffaa00;\n"
"}\n"
"\n"
"QCalendarWidget QMenu::icon:checked {\n"
"    background: gray;\n"
"    border: 1px inset gray;\n"
"    position: absolute;\n"
"    top: 1px;\n"
"    right: 1px;\n"
"    bottom: 1px;\n"
"    left: 1px;\n"
"}\n"
"QCalendarWidget QMenu::separator {\n"
"    height: 1px;\n"
"    background: #4f4f4f;\n"
"    margin-left: 10px;\n"
"    margin-right: 5px;\n"
"}\n"
"QCalendarWidget QMenu::indicator {\n"
"    width: 13px;\n"
"    height: 13px;\n"
"}\n"
"QCalendarWidget QMenu::item:disabled {\n"
"	color: #a2a2a2;\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Sliders */\n"
"QSlider::groove:horizontal {\n"
"    border-radius: 5px;\n"
"    height: 10px;\n"
"	margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"\n"
"QSlider::groove:horizontal:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    background-color: rgb(77,219,196);\n"
"    border: none;"
                        "\n"
"    height: 10px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"    background-color: rgb(195, 155, 255);\n"
"}\n"
"\n"
"QSlider::handle:horizontal:pressed {\n"
"    background-color: rgb(255, 121, 198);\n"
"}\n"
"\n"
"QSlider::groove:vertical {\n"
"    border-radius: 5px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"\n"
"QSlider::groove:vertical:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"\n"
"QSlider::handle:vertical {\n"
"    background-color: rgb(189, 147, 249);\n"
"	border: none;\n"
"    height: 10px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover {\n"
"    background-color: rgb(195, 155, 255);\n"
"}\n"
"\n"
"QSlider::handle:vertical:pressed {\n"
"    background-color: rgb(255, 121, 198);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////"
                        "\n"
"QTabWidget */\n"
"\n"
"QTabWidget > QTabBar::tab {\n"
"    font-weight: bold;\n"
"    background-color: rgb(43, 43, 43);\n"
"	border: 2px solid transparent;\n"
"    padding: 6px;\n"
"    border-top-left-radius: 5px;\n"
"    border-top-right-radius: 5px;\n"
"}\n"
"\n"
"QTabWidget > QTabBar::tab:selected {	\n"
"	border-top-color: #00aaff;\n"
"	min-width: 120px;\n"
"}\n"
"\n"
"QTabWidget > QTabBar::tab:hover {	\n"
"	border-top-color: #ffaa00;\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QDoubleSpinBox */\n"
"\n"
"QDoubleSpinBox:down-button{		\n"
"	image: url(:/resources/resources/icons/sys_arrow_down.svg);\n"
"	background-color: rgb(33, 37, 43);\n"
"   \n"
"}\n"
"QDoubleSpinBox:up-button{	\n"
"	image: url(:/resources/resources/icons/sys_arrow_up.svg);\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"\n"
"QDoubleSpinBox:up-button {\n"
"    border-color: transparent;\n"
"    width: 30px;\n"
"    height: 10px;\n"
"    border-top-left-ra"
                        "dius: 3px;\n"
"    border-top-right-radius: 3px;\n"
"    border-bottom-left-radius: 0px;\n"
"    border-bottom-right-radius: 0px;\n"
"}\n"
"QDoubleSpinBox:down-button {\n"
"    border-color: transparent;\n"
"    width: 30px;\n"
"    height: 10px;\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 0px;\n"
"    border-bottom-left-radius: 3px;\n"
"    border-bottom-right-radius: 3px;\n"
"}\n"
"\n"
"QDoubleSpinBox:down-button:hover,\n"
"QDoubleSpinBox:up-button:hover{\n"
"	background-color: #7bd17b;\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QDoubleSpinBox:down-button:hover:pressed,\n"
"QDoubleSpinBox:up-button:pressed{\n"
"	background-color: #ffaa00;\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QSpinBox */\n"
"\n"
"QSpinBox:down-button{		\n"
"	image: url(:/resources/resources/icons/sys_arrow_down.svg);\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"\n"
"QSpinBox:up-button{	\n"
"	ima"
                        "ge: url(:/resources/resources/icons/sys_arrow_up.svg);\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"QSpinBox:up-button {\n"
"    width: 30px;\n"
"    height: 10px;\n"
"    border-top-left-radius: 3px;\n"
"    border-top-right-radius: 3px;\n"
"    border-bottom-left-radius: 0px;\n"
"    border-bottom-right-radius: 0px;\n"
"}\n"
"QSpinBox:down-button {\n"
"   \n"
"    width: 30px;\n"
"    height: 10px;\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 0px;\n"
"    border-bottom-left-radius: 3px;\n"
"    border-bottom-right-radius: 3px;\n"
"}\n"
"\n"
"QSpinBox:down-button:hover,\n"
"QSpinBox:up-button:hover{\n"
"	background-color: #7bd17b;\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QSpinBox:down-button:hover:pressed,\n"
"QSpinBox:up-button:pressed{\n"
"	background-color: #ffaa00;\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Menu */\n"
"QMenu{\n"
"    margin: 2px;\n"
"	border-radius:  "
                        "3px;\n"
"}\n"
"QMenu::item {\n"
"    padding: 2px 25px 2px 20px;\n"
"    border: 1px solid transparent;\n"
"}\n"
"QMenu::item:enabled:selected {    \n"
"    background: #009fef;\n"
"	color: #ffffff;\n"
"}\n"
"QMenu::icon:checked {\n"
"    background: gray;\n"
"    border: 1px inset gray;\n"
"    position: absolute;\n"
"    top: 1px;\n"
"    right: 1px;\n"
"    bottom: 1px;\n"
"    left: 1px;\n"
"}\n"
"QMenu::separator {\n"
"    height: 1px;\n"
"    background: #4f4f4f;\n"
"    margin-left: 10px;\n"
"    margin-right: 5px;\n"
"}\n"
"QMenu::indicator {\n"
"    width: 13px;\n"
"    height: 13px;\n"
"}\n"
"QMenu::item:disabled {\n"
"	color: #a2a2a2;\n"
"}\n"
"QMenu::item:enabled:pressed {\n"
"    background-color: #ffaa00;\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QGroupBox */\n"
"QGroupBox {\n"
"margin-top: 1ex;\n"
"padding-top: 2px; \n"
"border: 1px solid ;\n"
"border-radius: 5px;\n"
"border-color:#003f50;\n"
"background-color: transpa"
                        "rent;\n"
"}\n"
"QGroupBox:title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding:  0px 2px 0px 2px;\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QTableWidget */\n"
"QTableWidget {	\n"
"	background-color: transparent;\n"
"	padding: 2px;\n"
"	border-radius: 5px;\n"
"	gridline-color: rgb(35, 35, 35);\n"
"	border-bottom: 1px solid rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item {\n"
"	font-size: 10px;\n"
"	font-family: \"Segoe UI\";\n"
"	font-weight: normal;\n"
"	border-color: rgb(44, 49, 60);\n"
"	padding-left: 5px;\n"
"	padding-right: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"	background-color: rgb(255, 255, 255);\n"
"	color: rgb(33, 37, 43);\n"
"}\n"
"\n"
"QTableWidget::item:selected {	\n"
"	background-color: rgb(0, 50,120);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"QTableWidget::horizontalHeader {	\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"\n"
"QHeaderView {\n"
" background-color: transparent;\n"
"}\n"
""
                        "QHeaderView::section {\n"
"	max-width: 30px;\n"
"	border: 1px solid rgb(44, 49, 58);\n"
"	border-style: none;\n"
"    border-bottom: 1px solid rgb(44, 49, 60);\n"
"    border-right: 1px solid rgb(44, 49, 60);\n"
"}\n"
"\n"
"QHeaderView::section:horizontal {\n"
"	color: rgb(255, 255, 255);\n"
"    border: 1px solid rgb(33, 37, 43);\n"
"	background-color: rgb(33, 37, 43);\n"
"	padding: 1px;\n"
"	border-top-left-radius: 3px;\n"
"    border-top-right-radius: 3px;\n"
"}\n"
"QHeaderView::section:vertical {\n"
"    border: 1px solid rgb(44, 49, 60);\n"
"}\n"
"\n"
"/* Estilos para todos los QLineEdit de b\u00fasqueda (search, search_2, search_3, search_4) */\n"
"QLineEdit#linedit_search,\n"
"QLineEdit#linedit_search_2,\n"
"QLineEdit#linedit_search_3,\n"
"QLineEdit#linedit_search_4 {\n"
"    background-color: rgb(255, 255, 255);\n"
"    color: rgb(0, 0, 0);\n"
"    border-top-left-radius: 5px;\n"
"    border-bottom-left-radius: 5px;\n"
"    border-top-right-radius: 0px;\n"
"    border-bottom-right-radius: 0px;\n"
"    "
                        "border-top: 1px solid black;\n"
"    border-bottom: 1px solid black;\n"
"    border-left: 1px solid black;\n"
"}\n"
"\n"
"/* Estilos para todos los botones de b\u00fasqueda (btn_search, btn_search_2, btn_search_3, btn_search_4) */\n"
"QPushButton#btn_search,\n"
"QPushButton#btn_search_2,\n"
"QPushButton#btn_search_3,\n"
"QPushButton#btn_search_4 {\n"
"    border-radius: 0px;\n"
"    background-color: #46aa8f;\n"
"    color: #ffffff;\n"
"    border-top: 1px solid black;\n"
"    border-bottom: 1px solid black;\n"
"    border-left: 1px solid black;\n"
"}\n"
"\n"
"/* Estilos para todos los botones de limpieza (btn_cleaner, btn_cleaner_2, btn_cleaner_3, btn_cleaner_4) */\n"
"QPushButton#btn_cleaner,\n"
"QPushButton#btn_cleaner_2,\n"
"QPushButton#btn_cleaner_3,\n"
"QPushButton#btn_cleaner_4 {\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"    background-color: #46aa8f;\n"
"    color: #ffffff;\n"
"    border-top: 1px solid black;\n"
"    border-bottom: 1px solid black;\n"
"    bord"
                        "er-left: 1px solid black;\n"
"    border-right: 1px solid black;\n"
"}\n"
"\n"
"/* Estilos hover para todos los botones de b\u00fasqueda y limpieza del buscador */\n"
"QPushButton#btn_search:hover,\n"
"QPushButton#btn_search_2:hover,\n"
"QPushButton#btn_search_3:hover,\n"
"QPushButton#btn_search_4:hover,\n"
"QPushButton#btn_cleaner:hover,\n"
"QPushButton#btn_cleaner_2:hover,\n"
"QPushButton#btn_cleaner_3:hover,\n"
"QPushButton#btn_cleaner_4:hover {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-color: rgb(52, 59, 72);\n"
"}\n"
"\n"
"/* Estilos pressed para todos los botones de b\u00fasqueda y limpieza del buscador*/\n"
"QPushButton#btn_search:pressed,\n"
"QPushButton#btn_search_2:pressed,\n"
"QPushButton#btn_search_3:pressed,\n"
"QPushButton#btn_search_4:pressed,\n"
"QPushButton#btn_cleaner:pressed,\n"
"QPushButton#btn_cleaner_2:pressed,\n"
"QPushButton#btn_cleaner_3:pressed,\n"
"QPushButton#btn_cleaner_4:pressed {\n"
"    background-color: rgb(255, 170, 0);\n"
"    border-color: rgb(43, 50, 61);\n"
""
                        "}\n"
"\n"
"/* Estilos para todos los botones de limpieza y seleccionador del main */\n"
"QPushButton#btn_select_client,\n"
"QPushButton#btn_select_printer_3d {\n"
"    border-top-left-radius: 5px;\n"
"	 border-bottom-left-radius: 5px;\n"
"    background-color: #46aa8f;\n"
"    color: #ffffff;\n"
"    border-top: 1px solid rgb(52, 59, 72);\n"
"    border-bottom: 1px solid rgb(52, 59, 72);\n"
"    border-left: 1px solid rgb(52, 59, 72);\n"
"}\n"
"QPushButton#btn_select_filament,\n"
"QPushButton#btn_load_gcode {\n"
"  	border-radius: 5px;\n"
"    background-color: #46aa8f;\n"
"    color: #ffffff;\n"
"    border: 1px solid rgb(52, 59, 72);\n"
"}\n"
"\n"
"QPushButton#btn_cleaner_client,\n"
"QPushButton#btn_cleaner_printer_3d\n"
" {\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"    background-color: #46aa8f;\n"
"	color: #ffffff;\n"
"    border: 1px solid rgb(52, 59, 72);\n"
"    border-left: 1px solid rgb(52, 59, 72);\n"
"    border-right: 1px solid rgb(52, 59, 72);\n"
"	border-b"
                        "ottom: 1px solid rgb(52, 59, 72);\n"
"}\n"
"\n"
"/* Estilos hover para todos los botones de seleccionador y limpieza del main */\n"
"QPushButton#btn_select_client:hover,\n"
"QPushButton#btn_select_filament:hover,\n"
"QPushButton#btn_load_gcode:hover,\n"
"QPushButton#btn_select_printer_3d:hover,\n"
"QPushButton#btn_cleaner_client:hover,\n"
"QPushButton#btn_cleaner_printer_3d:hover  {\n"
"    background-color: #00aaf0;\n"
"    border-color: rgb(52, 59, 72);\n"
"}\n"
"\n"
"/* Estilos pressed para todos los botones de  seleccionador y limpieza del main */\n"
"QPushButton#btn_select_client:pressed,\n"
"QPushButton#btn_select_filament:pressed,\n"
"QPushButton#btn_load_gcode:pressed,\n"
"QPushButton#btn_select_printer_3d:pressed,\n"
"QPushButton#btn_cleaner_client:pressed,\n"
"QPushButton#btn_cleaner_printer_3d:pressed {\n"
"    background-color: #ffaa00;\n"
"    border-color: #69cdff;\n"
"}\n"
"\n"
"/* Estilos pressed para todos los perfiles cargados de filamento del main */\n"
"\n"
"\n"
"QPushButton#btn_filament_1,"
                        "\n"
"QPushButton#btn_filament_2,\n"
"QPushButton#btn_filament_3,\n"
"QPushButton#btn_filament_4,\n"
"QPushButton#btn_filament_5,\n"
"QPushButton#btn_filament_6 {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    color: white;\n"
"	border-radius: 2px;\n"
"	background: qlineargradient(\n"
"        x1:0, y1:1, x2:1, y2:0,\n"
"        stop:0 #bcbcbc,\n"
"        stop:0.80 #bcbcbc,\n"
"        stop:0.80 transparent,\n"
"        stop:1 transparent\n"
"    );    \n"
"}\n"
"\n"
"\n"
"\n"
"")
        self.gridLayout_6 = QGridLayout(self.styleSheet)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.bgApp = QFrame(self.styleSheet)
        self.bgApp.setObjectName(u"bgApp")
        self.bgApp.setEnabled(True)
        self.bgApp.setStyleSheet(u"")
        self.bgApp.setFrameShape(QFrame.Shape.NoFrame)
        self.bgApp.setFrameShadow(QFrame.Shadow.Raised)
        self.appLayout = QHBoxLayout(self.bgApp)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName(u"appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.contentBox = QFrame(self.bgApp)
        self.contentBox.setObjectName(u"contentBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.contentBox.sizePolicy().hasHeightForWidth())
        self.contentBox.setSizePolicy(sizePolicy1)
        self.contentBox.setMinimumSize(QSize(0, 0))
        self.contentBox.setFrameShape(QFrame.Shape.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.contentTopBg = QFrame(self.contentBox)
        self.contentTopBg.setObjectName(u"contentTopBg")
        self.contentTopBg.setMinimumSize(QSize(0, 50))
        self.contentTopBg.setMaximumSize(QSize(16777215, 50))
        self.contentTopBg.setStyleSheet(u"")
        self.contentTopBg.setFrameShape(QFrame.Shape.NoFrame)
        self.contentTopBg.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.contentTopBg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.leftBox = QFrame(self.contentTopBg)
        self.leftBox.setObjectName(u"leftBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy2)
        self.leftBox.setMinimumSize(QSize(0, 0))
        self.leftBox.setFrameShape(QFrame.Shape.NoFrame)
        self.leftBox.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.leftBox)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 8, 0)
        self.topLogoInfo = QFrame(self.leftBox)
        self.topLogoInfo.setObjectName(u"topLogoInfo")
        sizePolicy.setHeightForWidth(self.topLogoInfo.sizePolicy().hasHeightForWidth())
        self.topLogoInfo.setSizePolicy(sizePolicy)
        self.topLogoInfo.setMinimumSize(QSize(180, 50))
        self.topLogoInfo.setMaximumSize(QSize(220, 50))
        self.topLogoInfo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.topLogoInfo.setStyleSheet(u"")
        self.topLogoInfo.setFrameShape(QFrame.Shape.NoFrame)
        self.topLogoInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_9 = QGridLayout(self.topLogoInfo)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setHorizontalSpacing(2)
        self.gridLayout_9.setVerticalSpacing(0)
        self.gridLayout_9.setContentsMargins(8, 0, 0, 0)
        self.topLogo = QFrame(self.topLogoInfo)
        self.topLogo.setObjectName(u"topLogo")
        sizePolicy1.setHeightForWidth(self.topLogo.sizePolicy().hasHeightForWidth())
        self.topLogo.setSizePolicy(sizePolicy1)
        self.topLogo.setMinimumSize(QSize(42, 42))
        self.topLogo.setMaximumSize(QSize(42, 42))
#if QT_CONFIG(accessibility)
        self.topLogo.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.topLogo.setFrameShape(QFrame.Shape.NoFrame)
        self.topLogo.setFrameShadow(QFrame.Shadow.Raised)
        self.toplogo_label = QLabel(self.topLogo)
        self.toplogo_label.setObjectName(u"toplogo_label")
        self.toplogo_label.setGeometry(QRect(0, 0, 41, 41))
        sizePolicy.setHeightForWidth(self.toplogo_label.sizePolicy().hasHeightForWidth())
        self.toplogo_label.setSizePolicy(sizePolicy)
        self.toplogo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toplogo_label.setStyleSheet(u"image: url(:/resources/resources/images/voxeprint_mini.png);")
        self.toplogo_label.setPixmap(QPixmap(u":/images/images/images/Refri.png"))
        self.toplogo_label.setScaledContents(True)

        self.gridLayout_9.addWidget(self.topLogo, 0, 0, 1, 1)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.titleLeftApp = QLabel(self.topLogoInfo)
        self.titleLeftApp.setObjectName(u"titleLeftApp")
        sizePolicy.setHeightForWidth(self.titleLeftApp.sizePolicy().hasHeightForWidth())
        self.titleLeftApp.setSizePolicy(sizePolicy)
#if QT_CONFIG(accessibility)
        self.titleLeftApp.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.titleLeftApp.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_5.addWidget(self.titleLeftApp)

        self.titleLeftDescription = QLabel(self.topLogoInfo)
        self.titleLeftDescription.setObjectName(u"titleLeftDescription")
        sizePolicy.setHeightForWidth(self.titleLeftDescription.sizePolicy().hasHeightForWidth())
        self.titleLeftDescription.setSizePolicy(sizePolicy)
        self.titleLeftDescription.setMaximumSize(QSize(16777215, 16))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(8)
        font1.setBold(False)
        font1.setItalic(False)
        self.titleLeftDescription.setFont(font1)
#if QT_CONFIG(accessibility)
        self.titleLeftDescription.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.titleLeftDescription.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_5.addWidget(self.titleLeftDescription)


        self.gridLayout_9.addLayout(self.verticalLayout_5, 0, 1, 1, 1)


        self.horizontalLayout_3.addWidget(self.topLogoInfo)

        self.horizontalSpacer_9 = QSpacerItem(40, 50, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_9)

        self.titleRightInfo = QLabel(self.leftBox)
        self.titleRightInfo.setObjectName(u"titleRightInfo")
        sizePolicy1.setHeightForWidth(self.titleRightInfo.sizePolicy().hasHeightForWidth())
        self.titleRightInfo.setSizePolicy(sizePolicy1)
        self.titleRightInfo.setMaximumSize(QSize(380, 45))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI Black"])
        font2.setPointSize(10)
        font2.setBold(False)
        font2.setItalic(False)
        font2.setStrikeOut(False)
        font2.setKerning(True)
        font2.setStyleStrategy(QFont.PreferDefault)
        self.titleRightInfo.setFont(font2)
        self.titleRightInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.titleRightInfo)


        self.horizontalLayout.addWidget(self.leftBox)

        self.horizontalSpacer_12 = QSpacerItem(40, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_12)

        self.btn_settings_app = QPushButton(self.contentTopBg)
        self.btn_settings_app.setObjectName(u"btn_settings_app")
        self.btn_settings_app.setMinimumSize(QSize(30, 30))
        self.btn_settings_app.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings_app.setStyleSheet(u"QPushButton {\n"
"border-radius: 15px; \n"
"border:  none;\n"
"background-color: transparent;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"background-color: rgb(0, 170, 255);\n"
"border: 2px solid transparent;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	border-radius: 15px;  \n"
"	background-color: rgb(255, 170, 0);\n"
"	border: 6px solid transparent;\n"
"}\n"
"")
        icon = QIcon()
        icon.addFile(u":/resources/resources/icons/sys_cog_wheel_silhouette.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_settings_app.setIcon(icon)
        self.btn_settings_app.setIconSize(QSize(21, 21))
#if QT_CONFIG(shortcut)
        self.btn_settings_app.setShortcut(u"")
#endif // QT_CONFIG(shortcut)

        self.horizontalLayout.addWidget(self.btn_settings_app)


        self.verticalLayout_2.addWidget(self.contentTopBg)

        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName(u"contentBottom")
        self.contentBottom.setFrameShape(QFrame.Shape.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.content = QFrame(self.contentBottom)
        self.content.setObjectName(u"content")
        self.content.setStyleSheet(u"")
        self.content.setFrameShape(QFrame.Shape.NoFrame)
        self.content.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.content)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 8, 0, 0)
        self.frame_content = QFrame(self.content)
        self.frame_content.setObjectName(u"frame_content")
        self.frame_content.setMinimumSize(QSize(651, 620))
        self.frame_content.setStyleSheet(u"")
        self.frame_content.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_content.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_content)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.frame_content)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy3)
        self.tabWidget.setMinimumSize(QSize(651, 620))
        self.tabWidget.setMaximumSize(QSize(651, 625))
        self.tabWidget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setStyleSheet(u"")
        self.tab_one = QWidget()
        self.tab_one.setObjectName(u"tab_one")
        self.gridLayout_8 = QGridLayout(self.tab_one)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(-1, 0, -1, 2)
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setHorizontalSpacing(6)
        self.gridLayout_7.setVerticalSpacing(1)
        self.gridLayout_7.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, -1)
        self.groupbox_autofill = QGroupBox(self.tab_one)
        self.groupbox_autofill.setObjectName(u"groupbox_autofill")
        sizePolicy.setHeightForWidth(self.groupbox_autofill.sizePolicy().hasHeightForWidth())
        self.groupbox_autofill.setSizePolicy(sizePolicy)
        self.groupbox_autofill.setMinimumSize(QSize(308, 196))
        self.thumbnail_gcode_label = QLabel(self.groupbox_autofill)
        self.thumbnail_gcode_label.setObjectName(u"thumbnail_gcode_label")
        self.thumbnail_gcode_label.setGeometry(QRect(30, 66, 120, 120))
        sizePolicy.setHeightForWidth(self.thumbnail_gcode_label.sizePolicy().hasHeightForWidth())
        self.thumbnail_gcode_label.setSizePolicy(sizePolicy)
        self.thumbnail_gcode_label.setMinimumSize(QSize(116, 116))
        font3 = QFont()
        font3.setPointSize(10)
        self.thumbnail_gcode_label.setFont(font3)
        self.thumbnail_gcode_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.btn_load_gcode = QPushButton(self.groupbox_autofill)
        self.btn_load_gcode.setObjectName(u"btn_load_gcode")
        self.btn_load_gcode.setGeometry(QRect(186, 11, 100, 25))
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_load_gcode.sizePolicy().hasHeightForWidth())
        self.btn_load_gcode.setSizePolicy(sizePolicy4)
        self.btn_load_gcode.setMinimumSize(QSize(0, 25))
        self.btn_load_gcode.setMaximumSize(QSize(110, 25))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Black"])
        font4.setPointSize(10)
        font4.setBold(False)
        self.btn_load_gcode.setFont(font4)
        self.btn_load_gcode.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_load_gcode.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/resources/resources/icons/sys_arrow_circle_up_right.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_load_gcode.setIcon(icon1)
        self.btn_load_gcode.setIconSize(QSize(21, 21))
        self.linedit_desc_gcode = QLineEdit(self.groupbox_autofill)
        self.linedit_desc_gcode.setObjectName(u"linedit_desc_gcode")
        self.linedit_desc_gcode.setGeometry(QRect(20, 40, 261, 21))
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        font5.setPointSize(10)
        self.linedit_desc_gcode.setFont(font5)
        self.linedit_desc_gcode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.linedit_desc_gcode.setMaxLength(150)
        self.linedit_desc_gcode.setFrame(False)
        self.linedit_desc_gcode.setReadOnly(True)
        self.label_desc_proyect_mf = QLabel(self.groupbox_autofill)
        self.label_desc_proyect_mf.setObjectName(u"label_desc_proyect_mf")
        self.label_desc_proyect_mf.setGeometry(QRect(20, 20, 101, 16))
        font6 = QFont()
        font6.setPointSize(10)
        font6.setBold(True)
        self.label_desc_proyect_mf.setFont(font6)
        self.textEdit_details_gcode = QTextEdit(self.groupbox_autofill)
        self.textEdit_details_gcode.setObjectName(u"textEdit_details_gcode")
        self.textEdit_details_gcode.setGeometry(QRect(161, 70, 120, 110))
        self.textEdit_details_gcode.setFont(font3)
        self.textEdit_details_gcode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_details_gcode.setAcceptDrops(False)
        self.textEdit_details_gcode.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_details_gcode.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_gcode.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_gcode.setReadOnly(True)
        self.textEdit_details_gcode.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout_4.addWidget(self.groupbox_autofill)

        self.stacked_filament_mode = QStackedWidget(self.tab_one)
        self.stacked_filament_mode.setObjectName(u"stacked_filament_mode")
        sizePolicy.setHeightForWidth(self.stacked_filament_mode.sizePolicy().hasHeightForWidth())
        self.stacked_filament_mode.setSizePolicy(sizePolicy)
        self.stacked_filament_mode.setMinimumSize(QSize(308, 150))
        self.stacked_filament_mode.setFrameShadow(QFrame.Shadow.Sunken)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.groupbox_multi_filament = QGroupBox(self.page_2)
        self.groupbox_multi_filament.setObjectName(u"groupbox_multi_filament")
        self.groupbox_multi_filament.setGeometry(QRect(0, 0, 308, 150))
        sizePolicy.setHeightForWidth(self.groupbox_multi_filament.sizePolicy().hasHeightForWidth())
        self.groupbox_multi_filament.setSizePolicy(sizePolicy)
        self.groupbox_multi_filament.setMinimumSize(QSize(308, 150))
        font7 = QFont()
        font7.setBold(False)
        font7.setItalic(False)
        font7.setUnderline(False)
        font7.setStrikeOut(False)
        self.groupbox_multi_filament.setFont(font7)
        self.label_desc_multi_filament = QLabel(self.groupbox_multi_filament)
        self.label_desc_multi_filament.setObjectName(u"label_desc_multi_filament")
        self.label_desc_multi_filament.setGeometry(QRect(20, 20, 101, 16))
        font8 = QFont()
        font8.setPointSize(10)
        font8.setBold(True)
        font8.setItalic(False)
        font8.setUnderline(False)
        font8.setStrikeOut(False)
        self.label_desc_multi_filament.setFont(font8)
        self.combox_desc_multi_filament = QComboBox(self.groupbox_multi_filament)
        self.combox_desc_multi_filament.setObjectName(u"combox_desc_multi_filament")
        self.combox_desc_multi_filament.setEnabled(False)
        self.combox_desc_multi_filament.setGeometry(QRect(20, 40, 236, 22))
        font9 = QFont()
        font9.setPointSize(10)
        font9.setBold(False)
        font9.setItalic(False)
        font9.setUnderline(False)
        font9.setStrikeOut(False)
        self.combox_desc_multi_filament.setFont(font9)
        self.combox_desc_multi_filament.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.combox_desc_multi_filament.setMaxVisibleItems(8)
        self.layoutWidget_2 = QWidget(self.groupbox_multi_filament)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(20, 60, 261, 91))
        self.horizontalLayout_10 = QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.textEdit_details_multi_filament_select = QTextEdit(self.layoutWidget_2)
        self.textEdit_details_multi_filament_select.setObjectName(u"textEdit_details_multi_filament_select")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.textEdit_details_multi_filament_select.sizePolicy().hasHeightForWidth())
        self.textEdit_details_multi_filament_select.setSizePolicy(sizePolicy5)
        self.textEdit_details_multi_filament_select.setMinimumSize(QSize(161, 76))
        self.textEdit_details_multi_filament_select.setMaximumSize(QSize(261, 76))
        self.textEdit_details_multi_filament_select.setFont(font9)
        self.textEdit_details_multi_filament_select.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_details_multi_filament_select.setAcceptDrops(False)
        self.textEdit_details_multi_filament_select.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_details_multi_filament_select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_multi_filament_select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_multi_filament_select.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.horizontalLayout_10.addWidget(self.textEdit_details_multi_filament_select)

        self.widget = QWidget(self.layoutWidget_2)
        self.widget.setObjectName(u"widget")
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QSize(91, 74))
        self.widget.setMaximumSize(QSize(91, 74))
        self.gridLayout_10 = QGridLayout(self.widget)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setHorizontalSpacing(6)
        self.gridLayout_10.setVerticalSpacing(0)
        self.gridLayout_10.setContentsMargins(2, 2, 2, 2)
        self.btn_filament_5 = QPushButton(self.widget)
        self.btn_filament_5.setObjectName(u"btn_filament_5")
        self.btn_filament_5.setMinimumSize(QSize(0, 25))
        self.btn_filament_5.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_5.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_10.addWidget(self.btn_filament_5, 1, 1, 1, 1)

        self.btn_filament_3 = QPushButton(self.widget)
        self.btn_filament_3.setObjectName(u"btn_filament_3")
        self.btn_filament_3.setMinimumSize(QSize(0, 25))
        self.btn_filament_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_3.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_10.addWidget(self.btn_filament_3, 0, 2, 1, 1)

        self.btn_filament_2 = QPushButton(self.widget)
        self.btn_filament_2.setObjectName(u"btn_filament_2")
        self.btn_filament_2.setMinimumSize(QSize(0, 25))
        self.btn_filament_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_2.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.btn_filament_2.setStyleSheet(u"")

        self.gridLayout_10.addWidget(self.btn_filament_2, 0, 1, 1, 1)

        self.btn_filament_6 = QPushButton(self.widget)
        self.btn_filament_6.setObjectName(u"btn_filament_6")
        self.btn_filament_6.setMinimumSize(QSize(0, 25))
        self.btn_filament_6.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_6.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_10.addWidget(self.btn_filament_6, 1, 2, 1, 1)

        self.btn_filament_4 = QPushButton(self.widget)
        self.btn_filament_4.setObjectName(u"btn_filament_4")
        self.btn_filament_4.setMinimumSize(QSize(0, 25))
        self.btn_filament_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_4.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_10.addWidget(self.btn_filament_4, 1, 0, 1, 1)

        self.btn_filament_1 = QPushButton(self.widget)
        self.btn_filament_1.setObjectName(u"btn_filament_1")
        self.btn_filament_1.setMinimumSize(QSize(0, 25))
        self.btn_filament_1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_filament_1.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.btn_filament_1.setStyleSheet(u"")

        self.gridLayout_10.addWidget(self.btn_filament_1, 0, 0, 1, 1)


        self.horizontalLayout_10.addWidget(self.widget)

        self.alert_mutifilament_label = QLabel(self.groupbox_multi_filament)
        self.alert_mutifilament_label.setObjectName(u"alert_mutifilament_label")
        self.alert_mutifilament_label.setGeometry(QRect(275, 10, 21, 21))
        sizePolicy.setHeightForWidth(self.alert_mutifilament_label.sizePolicy().hasHeightForWidth())
        self.alert_mutifilament_label.setSizePolicy(sizePolicy)
        self.alert_mutifilament_label.setMinimumSize(QSize(21, 21))
        self.alert_mutifilament_label.setMaximumSize(QSize(20, 20))
        self.btn_multicolor_search = QPushButton(self.groupbox_multi_filament)
        self.btn_multicolor_search.setObjectName(u"btn_multicolor_search")
        self.btn_multicolor_search.setEnabled(True)
        self.btn_multicolor_search.setGeometry(QRect(260, 40, 26, 22))
        sizePolicy.setHeightForWidth(self.btn_multicolor_search.sizePolicy().hasHeightForWidth())
        self.btn_multicolor_search.setSizePolicy(sizePolicy)
        self.btn_multicolor_search.setMinimumSize(QSize(26, 22))
        font10 = QFont()
        font10.setFamilies([u"Segoe UI Black"])
        font10.setPointSize(10)
        font10.setBold(False)
        font10.setItalic(False)
        font10.setUnderline(False)
        font10.setStrikeOut(False)
        self.btn_multicolor_search.setFont(font10)
        self.btn_multicolor_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_multicolor_search.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/resources/resources/icons/sys_circle_ok_plus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_multicolor_search.setIcon(icon2)
        self.btn_multicolor_search.setIconSize(QSize(18, 18))
        self.stacked_filament_mode.addWidget(self.page_2)
        self.filament_page = QWidget()
        self.filament_page.setObjectName(u"filament_page")
        self.gridLayout_11 = QGridLayout(self.filament_page)
        self.gridLayout_11.setSpacing(0)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setContentsMargins(0, 0, 0, 0)
        self.groupbox_filament = QGroupBox(self.filament_page)
        self.groupbox_filament.setObjectName(u"groupbox_filament")
        sizePolicy.setHeightForWidth(self.groupbox_filament.sizePolicy().hasHeightForWidth())
        self.groupbox_filament.setSizePolicy(sizePolicy)
        self.groupbox_filament.setMinimumSize(QSize(308, 150))
        self.groupbox_filament.setFont(font7)
        self.label_desc = QLabel(self.groupbox_filament)
        self.label_desc.setObjectName(u"label_desc")
        self.label_desc.setGeometry(QRect(20, 20, 101, 16))
        self.label_desc.setFont(font8)
        self.btn_select_filament = QPushButton(self.groupbox_filament)
        self.btn_select_filament.setObjectName(u"btn_select_filament")
        self.btn_select_filament.setGeometry(QRect(186, 11, 100, 25))
        sizePolicy4.setHeightForWidth(self.btn_select_filament.sizePolicy().hasHeightForWidth())
        self.btn_select_filament.setSizePolicy(sizePolicy4)
        self.btn_select_filament.setMinimumSize(QSize(0, 25))
        self.btn_select_filament.setMaximumSize(QSize(110, 25))
        self.btn_select_filament.setFont(font10)
        self.btn_select_filament.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_filament.setStyleSheet(u"")
        self.btn_select_filament.setIcon(icon2)
        self.btn_select_filament.setIconSize(QSize(18, 18))
        self.combox_desc_filament = QComboBox(self.groupbox_filament)
        self.combox_desc_filament.setObjectName(u"combox_desc_filament")
        self.combox_desc_filament.setEnabled(False)
        self.combox_desc_filament.setGeometry(QRect(20, 40, 261, 22))
        self.combox_desc_filament.setFont(font9)
        self.combox_desc_filament.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.combox_desc_filament.setMaxVisibleItems(8)
        self.textEdit_details_filament_select = QTextEdit(self.groupbox_filament)
        self.textEdit_details_filament_select.setObjectName(u"textEdit_details_filament_select")
        self.textEdit_details_filament_select.setGeometry(QRect(21, 67, 168, 76))
        sizePolicy5.setHeightForWidth(self.textEdit_details_filament_select.sizePolicy().hasHeightForWidth())
        self.textEdit_details_filament_select.setSizePolicy(sizePolicy5)
        self.textEdit_details_filament_select.setMinimumSize(QSize(161, 76))
        self.textEdit_details_filament_select.setMaximumSize(QSize(261, 76))
        self.textEdit_details_filament_select.setFont(font9)
        self.textEdit_details_filament_select.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_details_filament_select.setAcceptDrops(False)
        self.textEdit_details_filament_select.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_details_filament_select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_filament_select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_filament_select.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_11.addWidget(self.groupbox_filament, 0, 0, 1, 1)

        self.stacked_filament_mode.addWidget(self.filament_page)

        self.verticalLayout_4.addWidget(self.stacked_filament_mode)

        self.groupBox_post = QGroupBox(self.tab_one)
        self.groupBox_post.setObjectName(u"groupBox_post")
        sizePolicy.setHeightForWidth(self.groupBox_post.sizePolicy().hasHeightForWidth())
        self.groupBox_post.setSizePolicy(sizePolicy)
        self.groupBox_post.setMinimumSize(QSize(308, 144))
        self.label_type_post = QLabel(self.groupBox_post)
        self.label_type_post.setObjectName(u"label_type_post")
        self.label_type_post.setGeometry(QRect(20, 50, 201, 16))
        self.label_type_post.setFont(font6)
        self.combox_type_post = QComboBox(self.groupBox_post)
        self.combox_type_post.setObjectName(u"combox_type_post")
        self.combox_type_post.setEnabled(True)
        self.combox_type_post.setGeometry(QRect(100, 80, 181, 22))
        self.combox_type_post.setFont(font3)
        self.combox_type_post.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.combox_type_post.setMaxVisibleItems(8)
        self.checkbox_post = QCheckBox(self.groupBox_post)
        self.checkbox_post.setObjectName(u"checkbox_post")
        self.checkbox_post.setGeometry(QRect(150, 15, 61, 21))
        self.checkbox_post.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_post_on = QLabel(self.groupBox_post)
        self.label_post_on.setObjectName(u"label_post_on")
        self.label_post_on.setGeometry(QRect(20, 20, 111, 16))
        self.label_post_on.setFont(font6)
        self.label_post = QLabel(self.groupBox_post)
        self.label_post.setObjectName(u"label_post")
        self.label_post.setGeometry(QRect(20, 115, 91, 21))
        self.label_post.setFont(font3)
        self.doublespinbox_post_price = QDoubleSpinBox(self.groupBox_post)
        self.doublespinbox_post_price.setObjectName(u"doublespinbox_post_price")
        self.doublespinbox_post_price.setGeometry(QRect(120, 115, 161, 22))
        sizePolicy4.setHeightForWidth(self.doublespinbox_post_price.sizePolicy().hasHeightForWidth())
        self.doublespinbox_post_price.setSizePolicy(sizePolicy4)
        self.doublespinbox_post_price.setFont(font3)
        self.doublespinbox_post_price.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.doublespinbox_post_price.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.label_post_range = QLabel(self.groupBox_post)
        self.label_post_range.setObjectName(u"label_post_range")
        self.label_post_range.setGeometry(QRect(20, 80, 61, 21))
        self.label_post_range.setFont(font3)

        self.verticalLayout_4.addWidget(self.groupBox_post)


        self.gridLayout_7.addLayout(self.verticalLayout_4, 0, 0, 1, 2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.groupbox_client = QGroupBox(self.tab_one)
        self.groupbox_client.setObjectName(u"groupbox_client")
        self.groupbox_client.setMinimumSize(QSize(308, 100))
        self.groupbox_client.setMaximumSize(QSize(16777215, 100))
        self.groupbox_client.setFont(font7)
        self.groupbox_client.setStyleSheet(u"")
        self.label_client_razon_social = QLabel(self.groupbox_client)
        self.label_client_razon_social.setObjectName(u"label_client_razon_social")
        self.label_client_razon_social.setGeometry(QRect(20, 20, 101, 16))
        self.label_client_razon_social.setFont(font8)
        self.checkbox_client_optional = QCheckBox(self.groupbox_client)
        self.checkbox_client_optional.setObjectName(u"checkbox_client_optional")
        self.checkbox_client_optional.setGeometry(QRect(210, 64, 90, 31))
        self.checkbox_client_optional.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.checkbox_client_optional.setStyleSheet(u"")
        self.checkbox_client_optional.setChecked(True)
        self.textEdit_name_client_select = QTextEdit(self.groupbox_client)
        self.textEdit_name_client_select.setObjectName(u"textEdit_name_client_select")
        self.textEdit_name_client_select.setGeometry(QRect(20, 40, 261, 22))
        self.textEdit_name_client_select.setFont(font3)
        self.textEdit_name_client_select.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_name_client_select.setAcceptDrops(False)
        self.textEdit_name_client_select.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_name_client_select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_name_client_select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_name_client_select.setReadOnly(True)
        self.textEdit_name_client_select.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.textEdit_ruc_ci_client_select = QTextEdit(self.groupbox_client)
        self.textEdit_ruc_ci_client_select.setObjectName(u"textEdit_ruc_ci_client_select")
        self.textEdit_ruc_ci_client_select.setGeometry(QRect(18, 62, 181, 22))
        self.textEdit_ruc_ci_client_select.setFont(font3)
        self.textEdit_ruc_ci_client_select.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_ruc_ci_client_select.setAcceptDrops(False)
        self.textEdit_ruc_ci_client_select.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_ruc_ci_client_select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_ruc_ci_client_select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_ruc_ci_client_select.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layoutWidget = QWidget(self.groupbox_client)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(163, 10, 121, 27))
        self.horizontalLayout_11 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.btn_select_client = QPushButton(self.layoutWidget)
        self.btn_select_client.setObjectName(u"btn_select_client")
        sizePolicy4.setHeightForWidth(self.btn_select_client.sizePolicy().hasHeightForWidth())
        self.btn_select_client.setSizePolicy(sizePolicy4)
        self.btn_select_client.setMinimumSize(QSize(0, 25))
        self.btn_select_client.setMaximumSize(QSize(95, 25))
        font11 = QFont()
        font11.setFamilies([u"Segoe UI Black"])
        font11.setPointSize(10)
        font11.setBold(True)
        self.btn_select_client.setFont(font11)
        self.btn_select_client.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_client.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u":/resources/resources/icons/sys_user_attached.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_select_client.setIcon(icon3)
        self.btn_select_client.setIconSize(QSize(19, 20))

        self.horizontalLayout_11.addWidget(self.btn_select_client)

        self.btn_cleaner_client = QPushButton(self.layoutWidget)
        self.btn_cleaner_client.setObjectName(u"btn_cleaner_client")
        sizePolicy.setHeightForWidth(self.btn_cleaner_client.sizePolicy().hasHeightForWidth())
        self.btn_cleaner_client.setSizePolicy(sizePolicy)
        self.btn_cleaner_client.setMinimumSize(QSize(24, 25))
        self.btn_cleaner_client.setMaximumSize(QSize(95, 25))
        font12 = QFont()
        font12.setFamilies([u"Segoe UI Black"])
        font12.setPointSize(10)
        self.btn_cleaner_client.setFont(font12)
        self.btn_cleaner_client.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon4 = QIcon()
        icon4.addFile(u":/resources/resources/icons/sys_broom.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_cleaner_client.setIcon(icon4)
        self.btn_cleaner_client.setIconSize(QSize(16, 16))

        self.horizontalLayout_11.addWidget(self.btn_cleaner_client)


        self.verticalLayout_3.addWidget(self.groupbox_client)

        self.groupbox_printer_info = QGroupBox(self.tab_one)
        self.groupbox_printer_info.setObjectName(u"groupbox_printer_info")
        self.groupbox_printer_info.setMinimumSize(QSize(308, 125))
        self.groupbox_printer_info.setFont(font7)
        self.label_desc_printer = QLabel(self.groupbox_printer_info)
        self.label_desc_printer.setObjectName(u"label_desc_printer")
        self.label_desc_printer.setGeometry(QRect(20, 20, 101, 16))
        self.label_desc_printer.setFont(font6)
        self.combox_desc_printer = QComboBox(self.groupbox_printer_info)
        self.combox_desc_printer.setObjectName(u"combox_desc_printer")
        self.combox_desc_printer.setEnabled(False)
        self.combox_desc_printer.setGeometry(QRect(20, 40, 261, 22))
        self.combox_desc_printer.setFont(font3)
        self.combox_desc_printer.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.combox_desc_printer.setMaxVisibleItems(8)
        self.textEdit_details_printer_select = QTextEdit(self.groupbox_printer_info)
        self.textEdit_details_printer_select.setObjectName(u"textEdit_details_printer_select")
        self.textEdit_details_printer_select.setGeometry(QRect(18, 63, 261, 61))
        sizePolicy.setHeightForWidth(self.textEdit_details_printer_select.sizePolicy().hasHeightForWidth())
        self.textEdit_details_printer_select.setSizePolicy(sizePolicy)
        self.textEdit_details_printer_select.setMinimumSize(QSize(261, 55))
        self.textEdit_details_printer_select.setFont(font3)
        self.textEdit_details_printer_select.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.textEdit_details_printer_select.setAcceptDrops(False)
        self.textEdit_details_printer_select.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_details_printer_select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_printer_select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_details_printer_select.setReadOnly(True)
        self.textEdit_details_printer_select.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layoutWidget1 = QWidget(self.groupbox_printer_info)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(165, 10, 121, 27))
        self.horizontalLayout_12 = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.btn_select_printer_3d = QPushButton(self.layoutWidget1)
        self.btn_select_printer_3d.setObjectName(u"btn_select_printer_3d")
        sizePolicy4.setHeightForWidth(self.btn_select_printer_3d.sizePolicy().hasHeightForWidth())
        self.btn_select_printer_3d.setSizePolicy(sizePolicy4)
        self.btn_select_printer_3d.setMinimumSize(QSize(0, 25))
        self.btn_select_printer_3d.setMaximumSize(QSize(95, 25))
        self.btn_select_printer_3d.setFont(font4)
        self.btn_select_printer_3d.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_printer_3d.setStyleSheet(u"")
        self.btn_select_printer_3d.setIcon(icon2)
        self.btn_select_printer_3d.setIconSize(QSize(18, 18))

        self.horizontalLayout_12.addWidget(self.btn_select_printer_3d)

        self.btn_cleaner_printer_3d = QPushButton(self.layoutWidget1)
        self.btn_cleaner_printer_3d.setObjectName(u"btn_cleaner_printer_3d")
        sizePolicy.setHeightForWidth(self.btn_cleaner_printer_3d.sizePolicy().hasHeightForWidth())
        self.btn_cleaner_printer_3d.setSizePolicy(sizePolicy)
        self.btn_cleaner_printer_3d.setMinimumSize(QSize(24, 25))
        self.btn_cleaner_printer_3d.setMaximumSize(QSize(95, 25))
        self.btn_cleaner_printer_3d.setFont(font12)
        self.btn_cleaner_printer_3d.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cleaner_printer_3d.setIcon(icon4)
        self.btn_cleaner_printer_3d.setIconSize(QSize(16, 16))

        self.horizontalLayout_12.addWidget(self.btn_cleaner_printer_3d)


        self.verticalLayout_3.addWidget(self.groupbox_printer_info)

        self.groupbox_piece_info = QGroupBox(self.tab_one)
        self.groupbox_piece_info.setObjectName(u"groupbox_piece_info")
        self.groupbox_piece_info.setMinimumSize(QSize(308, 191))
        self.label_time_print = QLabel(self.groupbox_piece_info)
        self.label_time_print.setObjectName(u"label_time_print")
        self.label_time_print.setGeometry(QRect(20, 20, 231, 16))
        self.label_time_print.setFont(font6)
        self.label_gram_filament = QLabel(self.groupbox_piece_info)
        self.label_gram_filament.setObjectName(u"label_gram_filament")
        self.label_gram_filament.setGeometry(QRect(20, 85, 231, 16))
        self.label_gram_filament.setFont(font6)
        self.spinbox_gram_piece = QSpinBox(self.groupbox_piece_info)
        self.spinbox_gram_piece.setObjectName(u"spinbox_gram_piece")
        self.spinbox_gram_piece.setGeometry(QRect(120, 105, 161, 22))
        sizePolicy4.setHeightForWidth(self.spinbox_gram_piece.sizePolicy().hasHeightForWidth())
        self.spinbox_gram_piece.setSizePolicy(sizePolicy4)
        self.spinbox_gram_piece.setFont(font3)
        self.spinbox_gram_piece.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinbox_gram_piece.setMinimum(1)
        self.spinbox_gram_piece.setMaximum(99999999)
        self.spinbox_gram_piece.setValue(1)
        self.label = QLabel(self.groupbox_piece_info)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 105, 91, 21))
        self.label.setFont(font3)
        self.label_hour = QLabel(self.groupbox_piece_info)
        self.label_hour.setObjectName(u"label_hour")
        self.label_hour.setGeometry(QRect(20, 50, 41, 21))
        self.label_hour.setFont(font3)
        self.spinbox_cant_piece = QSpinBox(self.groupbox_piece_info)
        self.spinbox_cant_piece.setObjectName(u"spinbox_cant_piece")
        self.spinbox_cant_piece.setGeometry(QRect(120, 160, 161, 22))
        sizePolicy4.setHeightForWidth(self.spinbox_cant_piece.sizePolicy().hasHeightForWidth())
        self.spinbox_cant_piece.setSizePolicy(sizePolicy4)
        self.spinbox_cant_piece.setFont(font3)
        self.spinbox_cant_piece.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinbox_cant_piece.setMinimum(1)
        self.spinbox_cant_piece.setMaximum(99999999)
        self.spinbox_cant_piece.setValue(1)
        self.label_price_product_2 = QLabel(self.groupbox_piece_info)
        self.label_price_product_2.setObjectName(u"label_price_product_2")
        self.label_price_product_2.setGeometry(QRect(20, 140, 231, 16))
        self.label_price_product_2.setFont(font6)
        self.label_3 = QLabel(self.groupbox_piece_info)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 160, 91, 21))
        self.label_3.setFont(font3)
        self.label_minute = QLabel(self.groupbox_piece_info)
        self.label_minute.setObjectName(u"label_minute")
        self.label_minute.setGeometry(QRect(140, 50, 61, 21))
        self.label_minute.setFont(font3)
        self.spinbox_time_minute_piece = QSpinBox(self.groupbox_piece_info)
        self.spinbox_time_minute_piece.setObjectName(u"spinbox_time_minute_piece")
        self.spinbox_time_minute_piece.setGeometry(QRect(210, 50, 71, 22))
        sizePolicy4.setHeightForWidth(self.spinbox_time_minute_piece.sizePolicy().hasHeightForWidth())
        self.spinbox_time_minute_piece.setSizePolicy(sizePolicy4)
        self.spinbox_time_minute_piece.setMaximumSize(QSize(71, 22))
        self.spinbox_time_minute_piece.setFont(font3)
        self.spinbox_time_minute_piece.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinbox_time_minute_piece.setMinimum(0)
        self.spinbox_time_minute_piece.setMaximum(60)
        self.spinbox_time_minute_piece.setSingleStep(1)
        self.spinbox_time_minute_piece.setValue(0)
        self.spinbox_time_hour_piece = QSpinBox(self.groupbox_piece_info)
        self.spinbox_time_hour_piece.setObjectName(u"spinbox_time_hour_piece")
        self.spinbox_time_hour_piece.setGeometry(QRect(65, 50, 71, 22))
        sizePolicy4.setHeightForWidth(self.spinbox_time_hour_piece.sizePolicy().hasHeightForWidth())
        self.spinbox_time_hour_piece.setSizePolicy(sizePolicy4)
        self.spinbox_time_hour_piece.setMaximumSize(QSize(71, 22))
        self.spinbox_time_hour_piece.setFont(font3)
        self.spinbox_time_hour_piece.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinbox_time_hour_piece.setMaximum(99999999)
        self.spinbox_time_hour_piece.setValue(0)

        self.verticalLayout_3.addWidget(self.groupbox_piece_info)

        self.groupBox_operations = QGroupBox(self.tab_one)
        self.groupBox_operations.setObjectName(u"groupBox_operations")
        self.groupBox_operations.setMaximumSize(QSize(308, 70))
        font13 = QFont()
        font13.setBold(False)
        self.groupBox_operations.setFont(font13)
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox_operations)
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(10, 14, 10, 14)
        self.btn_clear_all_selected = QPushButton(self.groupBox_operations)
        self.btn_clear_all_selected.setObjectName(u"btn_clear_all_selected")
        self.btn_clear_all_selected.setMinimumSize(QSize(70, 30))
        self.btn_clear_all_selected.setMaximumSize(QSize(120, 41))
        font14 = QFont()
        font14.setFamilies([u"Segoe UI Black"])
        font14.setPointSize(11)
        font14.setBold(True)
        font14.setItalic(False)
        font14.setUnderline(False)
        self.btn_clear_all_selected.setFont(font14)
        self.btn_clear_all_selected.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear_all_selected.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"background-color:  #f6b565;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #ffaa00;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"")
        self.btn_clear_all_selected.setIcon(icon4)

        self.horizontalLayout_8.addWidget(self.btn_clear_all_selected)

        self.btn_calculator = QPushButton(self.groupBox_operations)
        self.btn_calculator.setObjectName(u"btn_calculator")
        self.btn_calculator.setMinimumSize(QSize(30, 30))
        self.btn_calculator.setMaximumSize(QSize(120, 41))
        font15 = QFont()
        font15.setFamilies([u"Segoe UI Black"])
        font15.setPointSize(11)
        self.btn_calculator.setFont(font15)
        self.btn_calculator.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_calculator.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #dd99ff;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #bc37ff;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}")
        icon5 = QIcon()
        icon5.addFile(u":/resources/resources/icons/sys_calculator_bill.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_calculator.setIcon(icon5)

        self.horizontalLayout_8.addWidget(self.btn_calculator)

        self.btn_tuning = QPushButton(self.groupBox_operations)
        self.btn_tuning.setObjectName(u"btn_tuning")
        self.btn_tuning.setMinimumSize(QSize(30, 30))
        self.btn_tuning.setMaximumSize(QSize(120, 41))
        self.btn_tuning.setFont(font15)
        self.btn_tuning.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tuning.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #57577f;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"border: 1px solid #00aaff ;\n"
"background-color:#2f2f7f;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}")
        icon6 = QIcon()
        icon6.addFile(u":/resources/resources/icons/sys_app_settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_tuning.setIcon(icon6)

        self.horizontalLayout_8.addWidget(self.btn_tuning)


        self.verticalLayout_3.addWidget(self.groupBox_operations)


        self.gridLayout_7.addLayout(self.verticalLayout_3, 0, 2, 1, 1)

        self.groupBox_advance = QGroupBox(self.tab_one)
        self.groupBox_advance.setObjectName(u"groupBox_advance")
        sizePolicy.setHeightForWidth(self.groupBox_advance.sizePolicy().hasHeightForWidth())
        self.groupBox_advance.setSizePolicy(sizePolicy)
        self.groupBox_advance.setMinimumSize(QSize(200, 78))
        self.label_advance_on = QLabel(self.groupBox_advance)
        self.label_advance_on.setObjectName(u"label_advance_on")
        self.label_advance_on.setGeometry(QRect(20, 20, 61, 16))
        self.label_advance_on.setFont(font6)
        self.checkbox_advance = QCheckBox(self.groupBox_advance)
        self.checkbox_advance.setObjectName(u"checkbox_advance")
        self.checkbox_advance.setGeometry(QRect(100, 15, 61, 21))
        self.checkbox_advance.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.spinbox_advance = QSpinBox(self.groupBox_advance)
        self.spinbox_advance.setObjectName(u"spinbox_advance")
        self.spinbox_advance.setGeometry(QRect(110, 50, 71, 22))
        sizePolicy4.setHeightForWidth(self.spinbox_advance.sizePolicy().hasHeightForWidth())
        self.spinbox_advance.setSizePolicy(sizePolicy4)
        self.spinbox_advance.setMaximumSize(QSize(71, 22))
        self.spinbox_advance.setFont(font3)
        self.spinbox_advance.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.spinbox_advance.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spinbox_advance.setMinimum(0)
        self.spinbox_advance.setMaximum(100)
        self.spinbox_advance.setSingleStep(5)
        self.spinbox_advance.setValue(0)
        self.label_advance = QLabel(self.groupBox_advance)
        self.label_advance.setObjectName(u"label_advance")
        self.label_advance.setGeometry(QRect(20, 50, 81, 21))
        self.label_advance.setFont(font3)

        self.gridLayout_7.addWidget(self.groupBox_advance, 1, 0, 1, 1)

        self.groupBox_action = QGroupBox(self.tab_one)
        self.groupBox_action.setObjectName(u"groupBox_action")
        sizePolicy3.setHeightForWidth(self.groupBox_action.sizePolicy().hasHeightForWidth())
        self.groupBox_action.setSizePolicy(sizePolicy3)
        self.groupBox_action.setMinimumSize(QSize(161, 78))
        self.groupBox_action.setFont(font13)
        self.horizontalLayout_26 = QHBoxLayout(self.groupBox_action)
        self.horizontalLayout_26.setSpacing(10)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.btn_generate = QPushButton(self.groupBox_action)
        self.btn_generate.setObjectName(u"btn_generate")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.btn_generate.sizePolicy().hasHeightForWidth())
        self.btn_generate.setSizePolicy(sizePolicy6)
        self.btn_generate.setMinimumSize(QSize(145, 41))
        self.btn_generate.setMaximumSize(QSize(145, 41))
        self.btn_generate.setFont(font15)
        self.btn_generate.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_generate.setStyleSheet(u"QPushButton {\n"
" border-top-left-radius: 5px;\n"
"	 border-bottom-left-radius: 5px;\n"
"    background-color:  #6cb86c;\n"
"    color: #e6fdff;\n"
"    border-top: 1px solid #bcbcbc  ;\n"
"    border-bottom: 1px solid #bcbcbc  ;\n"
"    border-left: 1px solid #bcbcbc  ;\n"
"\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #00aa00;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #00aa00;\n"
"}\n"
"")
        icon7 = QIcon()
        icon7.addFile(u":/resources/resources/icons/sys_file_type_pdf.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_generate.setIcon(icon7)
        self.btn_generate.setIconSize(QSize(23, 23))

        self.horizontalLayout_14.addWidget(self.btn_generate)

        self.btn_select_type_doc = QToolButton(self.groupBox_action)
        self.btn_select_type_doc.setObjectName(u"btn_select_type_doc")
        self.btn_select_type_doc.setMinimumSize(QSize(24, 41))
        self.btn_select_type_doc.setMaximumSize(QSize(24, 41))
        self.btn_select_type_doc.setFont(font15)
        self.btn_select_type_doc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_type_doc.setStyleSheet(u"QToolButton {\n"
"    color: #e6fdff;\n"
"    border: 1px solid #bcbcbc;\n"
"    background-color: #6cb86c;\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"}\n"
"\n"
"QToolButton::menu-arrow    { image: none; }\n"
"QToolButton::menu-indicator { image: none; width: 0px; height: 0px; }\n"
"\n"
"QToolButton:hover {\n"
"    color: #ffffff;\n"
"    background-color: #00aa00;\n"
"    border: 1px solid #00aaff;\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    color: #ffffff;\n"
"    background-color: #ffaa00;\n"
"    border: 1px solid #69cdff;\n"
"}\n"
"\n"
"QToolButton:disabled {\n"
"    color: #d5d5d5;\n"
"    background-color: #6a6a6a;\n"
"    border: 1px solid #00aa00;\n"
"}")
        self.btn_select_type_doc.setText(u"")
        self.btn_select_type_doc.setIconSize(QSize(18, 18))
        self.btn_select_type_doc.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_select_type_doc.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btn_select_type_doc.setArrowType(Qt.ArrowType.DownArrow)

        self.horizontalLayout_14.addWidget(self.btn_select_type_doc)


        self.horizontalLayout_26.addLayout(self.horizontalLayout_14)

        self.btn_preview = QPushButton(self.groupBox_action)
        self.btn_preview.setObjectName(u"btn_preview")
        self.btn_preview.setMinimumSize(QSize(95, 30))
        self.btn_preview.setMaximumSize(QSize(110, 41))
        self.btn_preview.setFont(font15)
        self.btn_preview.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_preview.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #46aac4;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #009dc4;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid #009dc4;\n"
"}")
        icon8 = QIcon()
        icon8.addFile(u":/resources/resources/icons/sys_file_overview_alt.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_preview.setIcon(icon8)
        self.btn_preview.setIconSize(QSize(18, 18))

        self.horizontalLayout_26.addWidget(self.btn_preview)

        self.btn_close = QPushButton(self.groupBox_action)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setMinimumSize(QSize(95, 40))
        self.btn_close.setMaximumSize(QSize(95, 41))
        self.btn_close.setFont(font14)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setStyleSheet(u"QPushButton {\n"
"color: #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"background-color:  #f09292;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #be0000;\n"
"}")
        icon9 = QIcon()
        icon9.addFile(u":/resources/resources/icons/sys_logout_alt.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_close.setIcon(icon9)
        self.btn_close.setIconSize(QSize(18, 18))

        self.horizontalLayout_26.addWidget(self.btn_close)


        self.gridLayout_7.addWidget(self.groupBox_action, 1, 1, 1, 2)


        self.gridLayout_8.addLayout(self.gridLayout_7, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_one, "")
        self.tab_five = QWidget()
        self.tab_five.setObjectName(u"tab_five")
        self.gridLayout_4 = QGridLayout(self.tab_five)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(-1, 0, -1, 5)
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalSpacer_8 = QSpacerItem(198, 48, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_8)

        self.groupBox_operations_4 = QGroupBox(self.tab_five)
        self.groupBox_operations_4.setObjectName(u"groupBox_operations_4")
        sizePolicy.setHeightForWidth(self.groupBox_operations_4.sizePolicy().hasHeightForWidth())
        self.groupBox_operations_4.setSizePolicy(sizePolicy)
        self.groupBox_operations_4.setMinimumSize(QSize(271, 71))
        self.groupBox_operations_4.setFont(font13)
        self.horizontalLayout_21 = QHBoxLayout(self.groupBox_operations_4)
        self.horizontalLayout_21.setSpacing(10)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(14, 14, 14, 14)
        self.btn_open_quote = QPushButton(self.groupBox_operations_4)
        self.btn_open_quote.setObjectName(u"btn_open_quote")
        self.btn_open_quote.setMinimumSize(QSize(110, 30))
        self.btn_open_quote.setMaximumSize(QSize(120, 41))
        self.btn_open_quote.setFont(font15)
        self.btn_open_quote.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open_quote.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #be7dff;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #aa00ff;\n"
"border: 1px solid #00aaff;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #aa00ff;\n"
"}")
        icon10 = QIcon()
        icon10.addFile(u":/resources/resources/icons/sys_file_invoice_dollar_v1.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_open_quote.setIcon(icon10)

        self.horizontalLayout_21.addWidget(self.btn_open_quote)

        self.btn_delete_quote = QPushButton(self.groupBox_operations_4)
        self.btn_delete_quote.setObjectName(u"btn_delete_quote")
        self.btn_delete_quote.setMinimumSize(QSize(100, 30))
        self.btn_delete_quote.setMaximumSize(QSize(120, 41))
        self.btn_delete_quote.setFont(font14)
        self.btn_delete_quote.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_delete_quote.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"\n"
"background-color:  #f09292;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #be0000;\n"
"}")
        icon11 = QIcon()
        icon11.addFile(u":/resources/resources/icons/sys_trash_xmark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_delete_quote.setIcon(icon11)

        self.horizontalLayout_21.addWidget(self.btn_delete_quote)


        self.horizontalLayout_20.addWidget(self.groupBox_operations_4)


        self.gridLayout_4.addLayout(self.horizontalLayout_20, 7, 0, 1, 1)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.btn_report_quotes = QPushButton(self.tab_five)
        self.btn_report_quotes.setObjectName(u"btn_report_quotes")
        self.btn_report_quotes.setMinimumSize(QSize(125, 40))
        self.btn_report_quotes.setMaximumSize(QSize(125, 40))
        self.btn_report_quotes.setFont(font15)
        self.btn_report_quotes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_report_quotes.setStyleSheet(u"QPushButton {\n"
"color: #ffffff;\n"
"border: 1px solid rgb(52, 59, 72);\n"
"border-radius: 5px; \n"
"background-color: #46aa8f;\n"
"padding-left: 0px;\n"
"padding-right: 9px;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"background-color: #69cdff;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled { \n"
"background-color: #92a1a2;\n"
"opacity: 0.5;\n"
"}")
        icon12 = QIcon()
        icon12.addFile(u":/resources/resources/icons/sys_pie_graphic.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_report_quotes.setIcon(icon12)
        self.btn_report_quotes.setIconSize(QSize(21, 21))

        self.horizontalLayout_22.addWidget(self.btn_report_quotes)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_desde = QLabel(self.tab_five)
        self.label_desde.setObjectName(u"label_desde")

        self.horizontalLayout_23.addWidget(self.label_desde)

        self.datedit_desde = QDateEdit(self.tab_five)
        self.datedit_desde.setObjectName(u"datedit_desde")
        sizePolicy.setHeightForWidth(self.datedit_desde.sizePolicy().hasHeightForWidth())
        self.datedit_desde.setSizePolicy(sizePolicy)
        self.datedit_desde.setMinimumSize(QSize(115, 24))
        self.datedit_desde.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.datedit_desde.setCalendarPopup(True)

        self.horizontalLayout_23.addWidget(self.datedit_desde)


        self.verticalLayout.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_hasta = QLabel(self.tab_five)
        self.label_hasta.setObjectName(u"label_hasta")

        self.horizontalLayout_25.addWidget(self.label_hasta)

        self.datedit_hasta = QDateEdit(self.tab_five)
        self.datedit_hasta.setObjectName(u"datedit_hasta")
        sizePolicy.setHeightForWidth(self.datedit_hasta.sizePolicy().hasHeightForWidth())
        self.datedit_hasta.setSizePolicy(sizePolicy)
        self.datedit_hasta.setMinimumSize(QSize(115, 24))
        self.datedit_hasta.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.datedit_hasta.setCalendarPopup(True)

        self.horizontalLayout_25.addWidget(self.datedit_hasta)


        self.verticalLayout.addLayout(self.horizontalLayout_25)


        self.horizontalLayout_22.addLayout(self.verticalLayout)

        self.horizontalSpacer_4 = QSpacerItem(10, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_4)

        self.groupbox_search_4 = QGroupBox(self.tab_five)
        self.groupbox_search_4.setObjectName(u"groupbox_search_4")
        sizePolicy.setHeightForWidth(self.groupbox_search_4.sizePolicy().hasHeightForWidth())
        self.groupbox_search_4.setSizePolicy(sizePolicy)
        self.groupbox_search_4.setMinimumSize(QSize(320, 60))
        self.groupbox_search_4.setMaximumSize(QSize(320, 60))
        font16 = QFont()
        font16.setBold(True)
        font16.setItalic(False)
        font16.setUnderline(False)
        font16.setStrikeOut(False)
        self.groupbox_search_4.setFont(font16)
        self.groupbox_search_4.setStyleSheet(u"")
        self.groupbox_search_4.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_25 = QVBoxLayout(self.groupbox_search_4)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setSpacing(0)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.linedit_search_4 = QLineEdit(self.groupbox_search_4)
        self.linedit_search_4.setObjectName(u"linedit_search_4")
        self.linedit_search_4.setMinimumSize(QSize(0, 25))
        self.linedit_search_4.setMaximumSize(QSize(16777215, 25))
        self.linedit_search_4.setFont(font3)
        self.linedit_search_4.setStyleSheet(u"")

        self.horizontalLayout_27.addWidget(self.linedit_search_4)

        self.btn_search_4 = QPushButton(self.groupbox_search_4)
        self.btn_search_4.setObjectName(u"btn_search_4")
        sizePolicy4.setHeightForWidth(self.btn_search_4.sizePolicy().hasHeightForWidth())
        self.btn_search_4.setSizePolicy(sizePolicy4)
        self.btn_search_4.setMinimumSize(QSize(0, 25))
        self.btn_search_4.setMaximumSize(QSize(90, 25))
        self.btn_search_4.setFont(font11)
        self.btn_search_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search_4.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search_4.setStyleSheet(u"")
        icon13 = QIcon()
        icon13.addFile(u":/resources/resources/icons/sys_lupe.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_search_4.setIcon(icon13)
        self.btn_search_4.setIconSize(QSize(18, 18))

        self.horizontalLayout_27.addWidget(self.btn_search_4)

        self.btn_cleaner_4 = QPushButton(self.groupbox_search_4)
        self.btn_cleaner_4.setObjectName(u"btn_cleaner_4")
        sizePolicy.setHeightForWidth(self.btn_cleaner_4.sizePolicy().hasHeightForWidth())
        self.btn_cleaner_4.setSizePolicy(sizePolicy)
        self.btn_cleaner_4.setMinimumSize(QSize(24, 25))
        self.btn_cleaner_4.setMaximumSize(QSize(90, 25))
        self.btn_cleaner_4.setFont(font12)
        self.btn_cleaner_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cleaner_4.setIcon(icon4)
        self.btn_cleaner_4.setIconSize(QSize(16, 16))

        self.horizontalLayout_27.addWidget(self.btn_cleaner_4)


        self.verticalLayout_25.addLayout(self.horizontalLayout_27)


        self.horizontalLayout_22.addWidget(self.groupbox_search_4)


        self.gridLayout_4.addLayout(self.horizontalLayout_22, 2, 0, 1, 1)

        self.qtable_quote = QTableWidget(self.tab_five)
        if (self.qtable_quote.columnCount() < 6):
            self.qtable_quote.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font12);
        self.qtable_quote.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font12);
        self.qtable_quote.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font11);
        self.qtable_quote.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font12);
        self.qtable_quote.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font12);
        self.qtable_quote.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font12);
        self.qtable_quote.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.qtable_quote.setObjectName(u"qtable_quote")
        sizePolicy2.setHeightForWidth(self.qtable_quote.sizePolicy().hasHeightForWidth())
        self.qtable_quote.setSizePolicy(sizePolicy2)
        self.qtable_quote.setMinimumSize(QSize(612, 300))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush2 = QBrush(QColor(0, 0, 0, 255))
        brush2.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush2)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush3 = QBrush(QColor(255, 255, 255, 128))
        brush3.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush3)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush4 = QBrush(QColor(0, 0, 0, 255))
        brush4.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush3)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        brush5 = QBrush(QColor(0, 0, 0, 255))
        brush5.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush3)
#endif
        self.qtable_quote.setPalette(palette)
        self.qtable_quote.setFont(font3)
        self.qtable_quote.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.qtable_quote.setStyleSheet(u"")
        self.qtable_quote.setFrameShape(QFrame.Shape.NoFrame)
        self.qtable_quote.setFrameShadow(QFrame.Shadow.Sunken)
        self.qtable_quote.setLineWidth(1)
        self.qtable_quote.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.qtable_quote.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtable_quote.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.qtable_quote.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.qtable_quote.setIconSize(QSize(0, 0))
        self.qtable_quote.setShowGrid(True)
        self.qtable_quote.setGridStyle(Qt.PenStyle.SolidLine)
        self.qtable_quote.setSortingEnabled(True)
        self.qtable_quote.setRowCount(0)
        self.qtable_quote.setColumnCount(6)
        self.qtable_quote.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_quote.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_quote.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_quote.horizontalHeader().setHighlightSections(True)
        self.qtable_quote.horizontalHeader().setStretchLastSection(False)
        self.qtable_quote.verticalHeader().setVisible(False)
        self.qtable_quote.verticalHeader().setMinimumSectionSize(32)
        self.qtable_quote.verticalHeader().setDefaultSectionSize(32)

        self.gridLayout_4.addWidget(self.qtable_quote, 4, 0, 1, 1)

        self.textEdit_details_quotes = QTextEdit(self.tab_five)
        self.textEdit_details_quotes.setObjectName(u"textEdit_details_quotes")
        sizePolicy.setHeightForWidth(self.textEdit_details_quotes.sizePolicy().hasHeightForWidth())
        self.textEdit_details_quotes.setSizePolicy(sizePolicy)
        self.textEdit_details_quotes.setMinimumSize(QSize(625, 125))
        self.textEdit_details_quotes.setStyleSheet(u"")
        self.textEdit_details_quotes.setReadOnly(True)

        self.gridLayout_4.addWidget(self.textEdit_details_quotes, 6, 0, 1, 1)

        self.tabWidget.addTab(self.tab_five, "")
        self.tab_two = QWidget()
        self.tab_two.setObjectName(u"tab_two")
        self.gridLayout = QGridLayout(self.tab_two)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 0, -1, 5)
        self.qtable_filaments = QTableWidget(self.tab_two)
        if (self.qtable_filaments.columnCount() < 7):
            self.qtable_filaments.setColumnCount(7)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(3, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setFont(font12);
        self.qtable_filaments.setHorizontalHeaderItem(5, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setFont(font11);
        self.qtable_filaments.setHorizontalHeaderItem(6, __qtablewidgetitem12)
        self.qtable_filaments.setObjectName(u"qtable_filaments")
        sizePolicy2.setHeightForWidth(self.qtable_filaments.sizePolicy().hasHeightForWidth())
        self.qtable_filaments.setSizePolicy(sizePolicy2)
        self.qtable_filaments.setMinimumSize(QSize(612, 300))
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush3)
#endif
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush7 = QBrush(QColor(0, 0, 0, 255))
        brush7.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush7)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush3)
#endif
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        brush8 = QBrush(QColor(0, 0, 0, 255))
        brush8.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush8)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush3)
#endif
        self.qtable_filaments.setPalette(palette1)
        self.qtable_filaments.setFont(font3)
        self.qtable_filaments.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.qtable_filaments.setStyleSheet(u"")
        self.qtable_filaments.setFrameShape(QFrame.Shape.NoFrame)
        self.qtable_filaments.setFrameShadow(QFrame.Shadow.Sunken)
        self.qtable_filaments.setLineWidth(1)
        self.qtable_filaments.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.qtable_filaments.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtable_filaments.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.qtable_filaments.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.qtable_filaments.setIconSize(QSize(0, 0))
        self.qtable_filaments.setShowGrid(True)
        self.qtable_filaments.setGridStyle(Qt.PenStyle.SolidLine)
        self.qtable_filaments.setSortingEnabled(True)
        self.qtable_filaments.setRowCount(0)
        self.qtable_filaments.setColumnCount(7)
        self.qtable_filaments.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_filaments.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_filaments.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_filaments.horizontalHeader().setHighlightSections(True)
        self.qtable_filaments.horizontalHeader().setStretchLastSection(False)
        self.qtable_filaments.verticalHeader().setVisible(False)
        self.qtable_filaments.verticalHeader().setMinimumSectionSize(32)
        self.qtable_filaments.verticalHeader().setDefaultSectionSize(32)

        self.gridLayout.addWidget(self.qtable_filaments, 1, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_5 = QSpacerItem(198, 48, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_5)

        self.groupBox_operations_2 = QGroupBox(self.tab_two)
        self.groupBox_operations_2.setObjectName(u"groupBox_operations_2")
        sizePolicy.setHeightForWidth(self.groupBox_operations_2.sizePolicy().hasHeightForWidth())
        self.groupBox_operations_2.setSizePolicy(sizePolicy)
        self.groupBox_operations_2.setMinimumSize(QSize(390, 71))
        self.groupBox_operations_2.setFont(font13)
        self.horizontalLayout_17 = QHBoxLayout(self.groupBox_operations_2)
        self.horizontalLayout_17.setSpacing(10)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(14, 14, 14, 14)
        self.btn_add_more_filament = QPushButton(self.groupBox_operations_2)
        self.btn_add_more_filament.setObjectName(u"btn_add_more_filament")
        self.btn_add_more_filament.setMinimumSize(QSize(100, 30))
        self.btn_add_more_filament.setMaximumSize(QSize(116, 41))
        self.btn_add_more_filament.setFont(font15)
        self.btn_add_more_filament.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_more_filament.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #f6b565;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #ffaa00;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #ffaa00;\n"
"}")
        icon14 = QIcon()
        icon14.addFile(u":/resources/resources/icons/sys_product_quantity_plus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_add_more_filament.setIcon(icon14)
        self.btn_add_more_filament.setIconSize(QSize(18, 18))

        self.horizontalLayout_17.addWidget(self.btn_add_more_filament)

        self.btn_mod_filament = QPushButton(self.groupBox_operations_2)
        self.btn_mod_filament.setObjectName(u"btn_mod_filament")
        self.btn_mod_filament.setMinimumSize(QSize(110, 30))
        self.btn_mod_filament.setMaximumSize(QSize(116, 41))
        self.btn_mod_filament.setFont(font15)
        self.btn_mod_filament.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_mod_filament.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #46aac4;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #009dc4;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #009dc4;\n"
"}")
        icon15 = QIcon()
        icon15.addFile(u":/resources/resources/icons/sys_pencil.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_mod_filament.setIcon(icon15)

        self.horizontalLayout_17.addWidget(self.btn_mod_filament)

        self.btn_delete_filament = QPushButton(self.groupBox_operations_2)
        self.btn_delete_filament.setObjectName(u"btn_delete_filament")
        self.btn_delete_filament.setMinimumSize(QSize(100, 30))
        self.btn_delete_filament.setMaximumSize(QSize(116, 41))
        self.btn_delete_filament.setFont(font14)
        self.btn_delete_filament.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_delete_filament.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"\n"
"background-color:  #f09292;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #be0000;\n"
"}")
        self.btn_delete_filament.setIcon(icon11)

        self.horizontalLayout_17.addWidget(self.btn_delete_filament)


        self.horizontalLayout_9.addWidget(self.groupBox_operations_2)


        self.gridLayout.addLayout(self.horizontalLayout_9, 4, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.btn_add_filament = QPushButton(self.tab_two)
        self.btn_add_filament.setObjectName(u"btn_add_filament")
        self.btn_add_filament.setMinimumSize(QSize(125, 40))
        self.btn_add_filament.setMaximumSize(QSize(125, 41))
        self.btn_add_filament.setFont(font15)
        self.btn_add_filament.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_filament.setStyleSheet(u"QPushButton {\n"
"color: #ffffff;\n"
"border: 1px solid rgb(52, 59, 72);\n"
"border-radius: 5px; \n"
"background-color: #46aa8f;\n"
"padding-left: 0px;\n"
"padding-right: 9px;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"background-color: #69cdff;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled { \n"
"background-color: #92a1a2;\n"
"opacity: 0.5;\n"
"}")
        icon16 = QIcon()
        icon16.addFile(u":/resources/resources/icons/sys_plus_circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_add_filament.setIcon(icon16)
        self.btn_add_filament.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.btn_add_filament)

        self.horizontalSpacer = QSpacerItem(208, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.groupbox_search = QGroupBox(self.tab_two)
        self.groupbox_search.setObjectName(u"groupbox_search")
        sizePolicy.setHeightForWidth(self.groupbox_search.sizePolicy().hasHeightForWidth())
        self.groupbox_search.setSizePolicy(sizePolicy)
        self.groupbox_search.setMinimumSize(QSize(320, 60))
        self.groupbox_search.setMaximumSize(QSize(320, 60))
        self.groupbox_search.setFont(font16)
        self.groupbox_search.setStyleSheet(u"")
        self.groupbox_search.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_29 = QVBoxLayout(self.groupbox_search)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setSpacing(0)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.linedit_search = QLineEdit(self.groupbox_search)
        self.linedit_search.setObjectName(u"linedit_search")
        self.linedit_search.setMinimumSize(QSize(0, 25))
        self.linedit_search.setMaximumSize(QSize(16777215, 25))
        self.linedit_search.setFont(font3)
        self.linedit_search.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.linedit_search.setStyleSheet(u"")

        self.horizontalLayout_32.addWidget(self.linedit_search)

        self.btn_search = QPushButton(self.groupbox_search)
        self.btn_search.setObjectName(u"btn_search")
        sizePolicy4.setHeightForWidth(self.btn_search.sizePolicy().hasHeightForWidth())
        self.btn_search.setSizePolicy(sizePolicy4)
        self.btn_search.setMinimumSize(QSize(0, 25))
        self.btn_search.setMaximumSize(QSize(90, 25))
        self.btn_search.setFont(font11)
        self.btn_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search.setStyleSheet(u"")
        self.btn_search.setIcon(icon13)
        self.btn_search.setIconSize(QSize(18, 18))

        self.horizontalLayout_32.addWidget(self.btn_search)

        self.btn_cleaner = QPushButton(self.groupbox_search)
        self.btn_cleaner.setObjectName(u"btn_cleaner")
        sizePolicy.setHeightForWidth(self.btn_cleaner.sizePolicy().hasHeightForWidth())
        self.btn_cleaner.setSizePolicy(sizePolicy)
        self.btn_cleaner.setMinimumSize(QSize(24, 25))
        self.btn_cleaner.setMaximumSize(QSize(90, 25))
        self.btn_cleaner.setFont(font12)
        self.btn_cleaner.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cleaner.setIcon(icon4)
        self.btn_cleaner.setIconSize(QSize(16, 16))

        self.horizontalLayout_32.addWidget(self.btn_cleaner)


        self.verticalLayout_29.addLayout(self.horizontalLayout_32)


        self.horizontalLayout_2.addWidget(self.groupbox_search)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.textEdit_details_filament = QTextEdit(self.tab_two)
        self.textEdit_details_filament.setObjectName(u"textEdit_details_filament")
        sizePolicy.setHeightForWidth(self.textEdit_details_filament.sizePolicy().hasHeightForWidth())
        self.textEdit_details_filament.setSizePolicy(sizePolicy)
        self.textEdit_details_filament.setMinimumSize(QSize(625, 125))
        self.textEdit_details_filament.setStyleSheet(u"")
        self.textEdit_details_filament.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_details_filament, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_two, "")
        self.tab_three = QWidget()
        self.tab_three.setObjectName(u"tab_three")
        self.gridLayout_2 = QGridLayout(self.tab_three)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, -1, 5)
        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_6 = QSpacerItem(308, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_6)

        self.groupBox_operations_3 = QGroupBox(self.tab_three)
        self.groupBox_operations_3.setObjectName(u"groupBox_operations_3")
        sizePolicy.setHeightForWidth(self.groupBox_operations_3.sizePolicy().hasHeightForWidth())
        self.groupBox_operations_3.setSizePolicy(sizePolicy)
        self.groupBox_operations_3.setMinimumSize(QSize(271, 71))
        self.groupBox_operations_3.setFont(font13)
        self.horizontalLayout_18 = QHBoxLayout(self.groupBox_operations_3)
        self.horizontalLayout_18.setSpacing(10)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(14, 14, 14, 14)
        self.btn_mod_printer = QPushButton(self.groupBox_operations_3)
        self.btn_mod_printer.setObjectName(u"btn_mod_printer")
        self.btn_mod_printer.setMinimumSize(QSize(110, 30))
        self.btn_mod_printer.setMaximumSize(QSize(116, 41))
        self.btn_mod_printer.setFont(font15)
        self.btn_mod_printer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_mod_printer.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #46aac4;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #009dc4;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #009dc4;\n"
"}")
        self.btn_mod_printer.setIcon(icon15)

        self.horizontalLayout_18.addWidget(self.btn_mod_printer)

        self.btn_delete_printer = QPushButton(self.groupBox_operations_3)
        self.btn_delete_printer.setObjectName(u"btn_delete_printer")
        self.btn_delete_printer.setMinimumSize(QSize(100, 30))
        self.btn_delete_printer.setMaximumSize(QSize(116, 41))
        self.btn_delete_printer.setFont(font14)
        self.btn_delete_printer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_delete_printer.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"\n"
"background-color:  #f09292;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #be0000;\n"
"}")
        self.btn_delete_printer.setIcon(icon11)

        self.horizontalLayout_18.addWidget(self.btn_delete_printer)


        self.horizontalLayout_15.addWidget(self.groupBox_operations_3)


        self.gridLayout_2.addLayout(self.horizontalLayout_15, 4, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(2)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.btn_add_printer = QPushButton(self.tab_three)
        self.btn_add_printer.setObjectName(u"btn_add_printer")
        self.btn_add_printer.setMinimumSize(QSize(125, 40))
        self.btn_add_printer.setMaximumSize(QSize(125, 41))
        self.btn_add_printer.setFont(font15)
        self.btn_add_printer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_printer.setStyleSheet(u"QPushButton {\n"
"color: #ffffff;\n"
"border: 1px solid rgb(52, 59, 72);\n"
"border-radius: 5px; \n"
"background-color: #46aa8f;\n"
"padding-left: 0px;\n"
"padding-right: 9px;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"background-color: #69cdff;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled { \n"
"background-color: #92a1a2;\n"
"opacity: 0.5;\n"
"}")
        self.btn_add_printer.setIcon(icon16)
        self.btn_add_printer.setIconSize(QSize(20, 20))

        self.horizontalLayout_6.addWidget(self.btn_add_printer)

        self.horizontalSpacer_2 = QSpacerItem(208, 38, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.groupbox_search_2 = QGroupBox(self.tab_three)
        self.groupbox_search_2.setObjectName(u"groupbox_search_2")
        sizePolicy.setHeightForWidth(self.groupbox_search_2.sizePolicy().hasHeightForWidth())
        self.groupbox_search_2.setSizePolicy(sizePolicy)
        self.groupbox_search_2.setMinimumSize(QSize(320, 60))
        self.groupbox_search_2.setMaximumSize(QSize(320, 60))
        self.groupbox_search_2.setFont(font16)
        self.groupbox_search_2.setStyleSheet(u"")
        self.groupbox_search_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_26 = QVBoxLayout(self.groupbox_search_2)
        self.verticalLayout_26.setSpacing(0)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setSpacing(0)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.linedit_search_2 = QLineEdit(self.groupbox_search_2)
        self.linedit_search_2.setObjectName(u"linedit_search_2")
        self.linedit_search_2.setMinimumSize(QSize(0, 25))
        self.linedit_search_2.setMaximumSize(QSize(16777215, 25))
        self.linedit_search_2.setFont(font3)
        self.linedit_search_2.setStyleSheet(u"")

        self.horizontalLayout_28.addWidget(self.linedit_search_2)

        self.btn_search_2 = QPushButton(self.groupbox_search_2)
        self.btn_search_2.setObjectName(u"btn_search_2")
        sizePolicy4.setHeightForWidth(self.btn_search_2.sizePolicy().hasHeightForWidth())
        self.btn_search_2.setSizePolicy(sizePolicy4)
        self.btn_search_2.setMinimumSize(QSize(0, 25))
        self.btn_search_2.setMaximumSize(QSize(90, 25))
        self.btn_search_2.setFont(font11)
        self.btn_search_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search_2.setStyleSheet(u"")
        self.btn_search_2.setIcon(icon13)
        self.btn_search_2.setIconSize(QSize(18, 18))

        self.horizontalLayout_28.addWidget(self.btn_search_2)

        self.btn_cleaner_2 = QPushButton(self.groupbox_search_2)
        self.btn_cleaner_2.setObjectName(u"btn_cleaner_2")
        sizePolicy.setHeightForWidth(self.btn_cleaner_2.sizePolicy().hasHeightForWidth())
        self.btn_cleaner_2.setSizePolicy(sizePolicy)
        self.btn_cleaner_2.setMinimumSize(QSize(24, 25))
        self.btn_cleaner_2.setMaximumSize(QSize(90, 25))
        self.btn_cleaner_2.setFont(font12)
        self.btn_cleaner_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cleaner_2.setIcon(icon4)
        self.btn_cleaner_2.setIconSize(QSize(16, 16))

        self.horizontalLayout_28.addWidget(self.btn_cleaner_2)


        self.verticalLayout_26.addLayout(self.horizontalLayout_28)


        self.horizontalLayout_6.addWidget(self.groupbox_search_2)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)

        self.qtable_printers = QTableWidget(self.tab_three)
        if (self.qtable_printers.columnCount() < 7):
            self.qtable_printers.setColumnCount(7)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(0, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(1, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(2, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(3, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(4, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(5, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setFont(font12);
        self.qtable_printers.setHorizontalHeaderItem(6, __qtablewidgetitem19)
        self.qtable_printers.setObjectName(u"qtable_printers")
        sizePolicy2.setHeightForWidth(self.qtable_printers.sizePolicy().hasHeightForWidth())
        self.qtable_printers.setSizePolicy(sizePolicy2)
        self.qtable_printers.setMinimumSize(QSize(612, 300))
        palette2 = QPalette()
        palette2.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette2.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Active, QPalette.Text, brush)
        palette2.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush9 = QBrush(QColor(0, 0, 0, 255))
        brush9.setStyle(Qt.NoBrush)
        palette2.setBrush(QPalette.Active, QPalette.Base, brush9)
        palette2.setBrush(QPalette.Active, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Active, QPalette.PlaceholderText, brush3)
#endif
        palette2.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush10 = QBrush(QColor(0, 0, 0, 255))
        brush10.setStyle(Qt.NoBrush)
        palette2.setBrush(QPalette.Inactive, QPalette.Base, brush10)
        palette2.setBrush(QPalette.Inactive, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush3)
#endif
        palette2.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette2.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        brush11 = QBrush(QColor(0, 0, 0, 255))
        brush11.setStyle(Qt.NoBrush)
        palette2.setBrush(QPalette.Disabled, QPalette.Base, brush11)
        palette2.setBrush(QPalette.Disabled, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush3)
#endif
        self.qtable_printers.setPalette(palette2)
        self.qtable_printers.setFont(font3)
        self.qtable_printers.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.qtable_printers.setStyleSheet(u"")
        self.qtable_printers.setFrameShape(QFrame.Shape.NoFrame)
        self.qtable_printers.setFrameShadow(QFrame.Shadow.Sunken)
        self.qtable_printers.setLineWidth(1)
        self.qtable_printers.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.qtable_printers.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtable_printers.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.qtable_printers.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.qtable_printers.setIconSize(QSize(0, 0))
        self.qtable_printers.setShowGrid(True)
        self.qtable_printers.setGridStyle(Qt.PenStyle.SolidLine)
        self.qtable_printers.setSortingEnabled(False)
        self.qtable_printers.setRowCount(0)
        self.qtable_printers.setColumnCount(7)
        self.qtable_printers.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_printers.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_printers.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_printers.horizontalHeader().setHighlightSections(True)
        self.qtable_printers.horizontalHeader().setStretchLastSection(False)
        self.qtable_printers.verticalHeader().setVisible(False)
        self.qtable_printers.verticalHeader().setCascadingSectionResizes(False)
        self.qtable_printers.verticalHeader().setMinimumSectionSize(32)
        self.qtable_printers.verticalHeader().setDefaultSectionSize(32)

        self.gridLayout_2.addWidget(self.qtable_printers, 1, 0, 1, 1)

        self.textEdit_details_printer = QTextEdit(self.tab_three)
        self.textEdit_details_printer.setObjectName(u"textEdit_details_printer")
        sizePolicy.setHeightForWidth(self.textEdit_details_printer.sizePolicy().hasHeightForWidth())
        self.textEdit_details_printer.setSizePolicy(sizePolicy)
        self.textEdit_details_printer.setMinimumSize(QSize(625, 125))
        self.textEdit_details_printer.setStyleSheet(u"")
        self.textEdit_details_printer.setReadOnly(True)

        self.gridLayout_2.addWidget(self.textEdit_details_printer, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_three, "")
        self.tab_six = QWidget()
        self.tab_six.setObjectName(u"tab_six")
        self.gridLayout_3 = QGridLayout(self.tab_six)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 0, -1, 5)
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalSpacer_7 = QSpacerItem(318, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_7)

        self.groupBox_operations_5 = QGroupBox(self.tab_six)
        self.groupBox_operations_5.setObjectName(u"groupBox_operations_5")
        sizePolicy.setHeightForWidth(self.groupBox_operations_5.sizePolicy().hasHeightForWidth())
        self.groupBox_operations_5.setSizePolicy(sizePolicy)
        self.groupBox_operations_5.setMinimumSize(QSize(420, 71))
        self.groupBox_operations_5.setFont(font13)
        self.horizontalLayout_19 = QHBoxLayout(self.groupBox_operations_5)
        self.horizontalLayout_19.setSpacing(10)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(14, 14, 14, 14)
        self.btn_default_customer = QPushButton(self.groupBox_operations_5)
        self.btn_default_customer.setObjectName(u"btn_default_customer")
        self.btn_default_customer.setMinimumSize(QSize(140, 30))
        self.btn_default_customer.setMaximumSize(QSize(145, 41))
        self.btn_default_customer.setFont(font15)
        self.btn_default_customer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_default_customer.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"background-color: #727256;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #727219;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #727219;\n"
"}")
        icon17 = QIcon()
        icon17.addFile(u":/resources/resources/icons/sys_select.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_default_customer.setIcon(icon17)

        self.horizontalLayout_19.addWidget(self.btn_default_customer)

        self.btn_mod_customer = QPushButton(self.groupBox_operations_5)
        self.btn_mod_customer.setObjectName(u"btn_mod_customer")
        self.btn_mod_customer.setMinimumSize(QSize(110, 30))
        self.btn_mod_customer.setMaximumSize(QSize(116, 41))
        self.btn_mod_customer.setFont(font15)
        self.btn_mod_customer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_mod_customer.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #46aac4;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #009dc4;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #009dc4;\n"
"}")
        self.btn_mod_customer.setIcon(icon15)

        self.horizontalLayout_19.addWidget(self.btn_mod_customer)

        self.btn_delete_customer = QPushButton(self.groupBox_operations_5)
        self.btn_delete_customer.setObjectName(u"btn_delete_customer")
        self.btn_delete_customer.setMinimumSize(QSize(100, 30))
        self.btn_delete_customer.setMaximumSize(QSize(116, 41))
        self.btn_delete_customer.setFont(font14)
        self.btn_delete_customer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_delete_customer.setStyleSheet(u"QPushButton {\n"
"color:  #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"\n"
"background-color:  #f09292;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #be0000;\n"
"}")
        self.btn_delete_customer.setIcon(icon11)

        self.horizontalLayout_19.addWidget(self.btn_delete_customer)


        self.horizontalLayout_16.addWidget(self.groupBox_operations_5)


        self.gridLayout_3.addLayout(self.horizontalLayout_16, 4, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(2)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.btn_add_customer = QPushButton(self.tab_six)
        self.btn_add_customer.setObjectName(u"btn_add_customer")
        self.btn_add_customer.setMinimumSize(QSize(125, 40))
        self.btn_add_customer.setMaximumSize(QSize(125, 41))
        self.btn_add_customer.setFont(font15)
        self.btn_add_customer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_customer.setStyleSheet(u"QPushButton {\n"
"color: #ffffff;\n"
"border: 1px solid rgb(52, 59, 72);\n"
"border-radius: 5px; \n"
"background-color: #46aa8f;\n"
"padding-left: 0px;\n"
"padding-right: 9px;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"background-color: #69cdff;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"\n"
"QPushButton:disabled { \n"
"background-color: #92a1a2;\n"
"opacity: 0.5;\n"
"}")
        self.btn_add_customer.setIcon(icon16)
        self.btn_add_customer.setIconSize(QSize(20, 20))

        self.horizontalLayout_7.addWidget(self.btn_add_customer)

        self.horizontalSpacer_3 = QSpacerItem(208, 38, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_3)

        self.groupbox_search_3 = QGroupBox(self.tab_six)
        self.groupbox_search_3.setObjectName(u"groupbox_search_3")
        sizePolicy.setHeightForWidth(self.groupbox_search_3.sizePolicy().hasHeightForWidth())
        self.groupbox_search_3.setSizePolicy(sizePolicy)
        self.groupbox_search_3.setMinimumSize(QSize(320, 60))
        self.groupbox_search_3.setMaximumSize(QSize(320, 60))
        self.groupbox_search_3.setFont(font16)
        self.groupbox_search_3.setStyleSheet(u"")
        self.groupbox_search_3.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_27 = QVBoxLayout(self.groupbox_search_3)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.horizontalLayout_29 = QHBoxLayout()
        self.horizontalLayout_29.setSpacing(0)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.linedit_search_3 = QLineEdit(self.groupbox_search_3)
        self.linedit_search_3.setObjectName(u"linedit_search_3")
        self.linedit_search_3.setMinimumSize(QSize(0, 25))
        self.linedit_search_3.setMaximumSize(QSize(16777215, 25))
        self.linedit_search_3.setFont(font3)
        self.linedit_search_3.setStyleSheet(u"")

        self.horizontalLayout_29.addWidget(self.linedit_search_3)

        self.btn_search_3 = QPushButton(self.groupbox_search_3)
        self.btn_search_3.setObjectName(u"btn_search_3")
        sizePolicy4.setHeightForWidth(self.btn_search_3.sizePolicy().hasHeightForWidth())
        self.btn_search_3.setSizePolicy(sizePolicy4)
        self.btn_search_3.setMinimumSize(QSize(0, 25))
        self.btn_search_3.setMaximumSize(QSize(90, 25))
        self.btn_search_3.setFont(font11)
        self.btn_search_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search_3.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search_3.setStyleSheet(u"")
        self.btn_search_3.setIcon(icon13)
        self.btn_search_3.setIconSize(QSize(18, 18))

        self.horizontalLayout_29.addWidget(self.btn_search_3)

        self.btn_cleaner_3 = QPushButton(self.groupbox_search_3)
        self.btn_cleaner_3.setObjectName(u"btn_cleaner_3")
        sizePolicy.setHeightForWidth(self.btn_cleaner_3.sizePolicy().hasHeightForWidth())
        self.btn_cleaner_3.setSizePolicy(sizePolicy)
        self.btn_cleaner_3.setMinimumSize(QSize(24, 25))
        self.btn_cleaner_3.setMaximumSize(QSize(90, 25))
        self.btn_cleaner_3.setFont(font12)
        self.btn_cleaner_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cleaner_3.setIcon(icon4)
        self.btn_cleaner_3.setIconSize(QSize(16, 16))

        self.horizontalLayout_29.addWidget(self.btn_cleaner_3)


        self.verticalLayout_27.addLayout(self.horizontalLayout_29)


        self.horizontalLayout_7.addWidget(self.groupbox_search_3)


        self.gridLayout_3.addLayout(self.horizontalLayout_7, 0, 0, 1, 1)

        self.qtable_customers = QTableWidget(self.tab_six)
        if (self.qtable_customers.columnCount() < 6):
            self.qtable_customers.setColumnCount(6)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(1, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(2, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(3, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(4, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setFont(font12);
        self.qtable_customers.setHorizontalHeaderItem(5, __qtablewidgetitem25)
        self.qtable_customers.setObjectName(u"qtable_customers")
        sizePolicy2.setHeightForWidth(self.qtable_customers.sizePolicy().hasHeightForWidth())
        self.qtable_customers.setSizePolicy(sizePolicy2)
        self.qtable_customers.setMinimumSize(QSize(612, 300))
        palette3 = QPalette()
        palette3.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette3.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette3.setBrush(QPalette.Active, QPalette.Text, brush)
        palette3.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush12 = QBrush(QColor(0, 0, 0, 255))
        brush12.setStyle(Qt.NoBrush)
        palette3.setBrush(QPalette.Active, QPalette.Base, brush12)
        palette3.setBrush(QPalette.Active, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Active, QPalette.PlaceholderText, brush3)
#endif
        palette3.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette3.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette3.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette3.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush13 = QBrush(QColor(0, 0, 0, 255))
        brush13.setStyle(Qt.NoBrush)
        palette3.setBrush(QPalette.Inactive, QPalette.Base, brush13)
        palette3.setBrush(QPalette.Inactive, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush3)
#endif
        palette3.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette3.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette3.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette3.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        brush14 = QBrush(QColor(0, 0, 0, 255))
        brush14.setStyle(Qt.NoBrush)
        palette3.setBrush(QPalette.Disabled, QPalette.Base, brush14)
        palette3.setBrush(QPalette.Disabled, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush3)
#endif
        self.qtable_customers.setPalette(palette3)
        self.qtable_customers.setFont(font3)
        self.qtable_customers.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.qtable_customers.setStyleSheet(u"")
        self.qtable_customers.setFrameShape(QFrame.Shape.NoFrame)
        self.qtable_customers.setFrameShadow(QFrame.Shadow.Sunken)
        self.qtable_customers.setLineWidth(1)
        self.qtable_customers.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.qtable_customers.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtable_customers.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.qtable_customers.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.qtable_customers.setIconSize(QSize(0, 0))
        self.qtable_customers.setShowGrid(True)
        self.qtable_customers.setGridStyle(Qt.PenStyle.SolidLine)
        self.qtable_customers.setSortingEnabled(False)
        self.qtable_customers.setRowCount(0)
        self.qtable_customers.setColumnCount(6)
        self.qtable_customers.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_customers.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_customers.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_customers.horizontalHeader().setHighlightSections(True)
        self.qtable_customers.horizontalHeader().setStretchLastSection(False)
        self.qtable_customers.verticalHeader().setVisible(False)
        self.qtable_customers.verticalHeader().setCascadingSectionResizes(False)
        self.qtable_customers.verticalHeader().setMinimumSectionSize(32)
        self.qtable_customers.verticalHeader().setDefaultSectionSize(32)

        self.gridLayout_3.addWidget(self.qtable_customers, 1, 0, 1, 1)

        self.textEdit_details_customer = QTextEdit(self.tab_six)
        self.textEdit_details_customer.setObjectName(u"textEdit_details_customer")
        sizePolicy.setHeightForWidth(self.textEdit_details_customer.sizePolicy().hasHeightForWidth())
        self.textEdit_details_customer.setSizePolicy(sizePolicy)
        self.textEdit_details_customer.setMinimumSize(QSize(625, 125))
        self.textEdit_details_customer.setStyleSheet(u"")
        self.textEdit_details_customer.setReadOnly(True)

        self.gridLayout_3.addWidget(self.textEdit_details_customer, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_six, "")
        self.tab_four = QWidget()
        self.tab_four.setObjectName(u"tab_four")
        self.gridLayout_5 = QGridLayout(self.tab_four)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_ajust = QFrame(self.tab_four)
        self.frame_ajust.setObjectName(u"frame_ajust")
        sizePolicy5.setHeightForWidth(self.frame_ajust.sizePolicy().hasHeightForWidth())
        self.frame_ajust.setSizePolicy(sizePolicy5)
        self.frame_ajust.setStyleSheet(u"")
        self.frame_ajust.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_ajust.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_5.addWidget(self.frame_ajust, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_four, "")

        self.horizontalLayout_30.addWidget(self.tabWidget)


        self.horizontalLayout_4.addWidget(self.frame_content)

        self.content_process_view = QFrame(self.content)
        self.content_process_view.setObjectName(u"content_process_view")
        sizePolicy5.setHeightForWidth(self.content_process_view.sizePolicy().hasHeightForWidth())
        self.content_process_view.setSizePolicy(sizePolicy5)
        self.content_process_view.setMaximumSize(QSize(319, 620))
        self.gridLayout_13 = QGridLayout(self.content_process_view)
        self.gridLayout_13.setSpacing(0)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout_13.setContentsMargins(6, 28, 6, 8)
        self.groupbox_details = QGroupBox(self.content_process_view)
        self.groupbox_details.setObjectName(u"groupbox_details")
        sizePolicy5.setHeightForWidth(self.groupbox_details.sizePolicy().hasHeightForWidth())
        self.groupbox_details.setSizePolicy(sizePolicy5)
        self.groupbox_details.setMinimumSize(QSize(0, 0))
        self.groupbox_details.setMaximumSize(QSize(309, 590))
        self.gridLayout_12 = QGridLayout(self.groupbox_details)
        self.gridLayout_12.setSpacing(6)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(9, -1, 9, 9)
        self.plaintextedit_status = QPlainTextEdit(self.groupbox_details)
        self.plaintextedit_status.setObjectName(u"plaintextedit_status")
        font17 = QFont()
        font17.setPointSize(8)
        self.plaintextedit_status.setFont(font17)
        self.plaintextedit_status.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.plaintextedit_status.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.plaintextedit_status.setReadOnly(True)
        self.plaintextedit_status.setMaximumBlockCount(255)

        self.gridLayout_12.addWidget(self.plaintextedit_status, 0, 0, 1, 1)


        self.gridLayout_13.addWidget(self.groupbox_details, 0, 0, 1, 1)


        self.horizontalLayout_4.addWidget(self.content_process_view)

        self.content_process_view.raise_()
        self.frame_content.raise_()

        self.verticalLayout_6.addWidget(self.content)

        self.bottomBar = QFrame(self.contentBottom)
        self.bottomBar.setObjectName(u"bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 22))
        self.bottomBar.setMaximumSize(QSize(16777215, 22))
        self.bottomBar.setFrameShape(QFrame.Shape.NoFrame)
        self.bottomBar.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.bottomBar)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.donationLabel = QLabel(self.bottomBar)
        self.donationLabel.setObjectName(u"donationLabel")
        sizePolicy3.setHeightForWidth(self.donationLabel.sizePolicy().hasHeightForWidth())
        self.donationLabel.setSizePolicy(sizePolicy3)
        self.donationLabel.setMinimumSize(QSize(110, 22))
        font18 = QFont()
        font18.setFamilies([u"Segoe UI Black"])
        self.donationLabel.setFont(font18)
        self.donationLabel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.donationLabel.setScaledContents(True)
        self.donationLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.donationLabel)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_11)

        self.eventLabel_pb = QLabel(self.bottomBar)
        self.eventLabel_pb.setObjectName(u"eventLabel_pb")
        sizePolicy6.setHeightForWidth(self.eventLabel_pb.sizePolicy().hasHeightForWidth())
        self.eventLabel_pb.setSizePolicy(sizePolicy6)
        self.eventLabel_pb.setMinimumSize(QSize(120, 22))

        self.horizontalLayout_5.addWidget(self.eventLabel_pb)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)

        self.version = QLabel(self.bottomBar)
        self.version.setObjectName(u"version")
        self.version.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.version.setScaledContents(True)
        self.version.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.version)

        self.btn_toggle_panel = QPushButton(self.bottomBar)
        self.btn_toggle_panel.setObjectName(u"btn_toggle_panel")
        sizePolicy.setHeightForWidth(self.btn_toggle_panel.sizePolicy().hasHeightForWidth())
        self.btn_toggle_panel.setSizePolicy(sizePolicy)
        self.btn_toggle_panel.setMaximumSize(QSize(22, 22))
        self.btn_toggle_panel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle_panel.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.btn_toggle_panel.setStyleSheet(u"")
        icon18 = QIcon()
        icon18.addFile(u":/resources/resources/icons/sys_layout_sidebar_right_collapse_v1.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_toggle_panel.setIcon(icon18)
        self.btn_toggle_panel.setIconSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.btn_toggle_panel)


        self.verticalLayout_6.addWidget(self.bottomBar)


        self.verticalLayout_2.addWidget(self.contentBottom)


        self.appLayout.addWidget(self.contentBox)


        self.gridLayout_6.addWidget(self.bgApp, 0, 0, 1, 1)

        MainPanel.setCentralWidget(self.styleSheet)

        self.retranslateUi(MainPanel)

        self.tabWidget.setCurrentIndex(0)
        self.stacked_filament_mode.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainPanel)
    # setupUi

    def retranslateUi(self, MainPanel):
        MainPanel.setWindowTitle(QCoreApplication.translate("MainPanel", u"MainWindow", None))
#if QT_CONFIG(accessibility)
        self.contentTopBg.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.leftBox.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.topLogoInfo.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.toplogo_label.setText("")
        self.titleLeftApp.setText(QCoreApplication.translate("MainPanel", u"VoxePrint", None))
        self.titleLeftDescription.setText(QCoreApplication.translate("MainPanel", u"Manage \u2022 Quote \u2022 Print", None))
        self.titleRightInfo.setText(QCoreApplication.translate("MainPanel", u"Software Generador de Presupuestos", None))
        self.btn_settings_app.setText("")
        self.groupbox_autofill.setTitle(QCoreApplication.translate("MainPanel", u"Autocompletar (/)", None))
        self.thumbnail_gcode_label.setText("")
#if QT_CONFIG(tooltip)
        self.btn_load_gcode.setToolTip(QCoreApplication.translate("MainPanel", u"Carga G-code o 3MF", None))
#endif // QT_CONFIG(tooltip)
        self.btn_load_gcode.setText(QCoreApplication.translate("MainPanel", u"Proyecto", None))
        self.linedit_desc_gcode.setInputMask("")
        self.linedit_desc_gcode.setText("")
        self.linedit_desc_gcode.setPlaceholderText(QCoreApplication.translate("MainPanel", u"Descripci\u00f3n del Proyecto", None))
        self.label_desc_proyect_mf.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None))
        self.groupbox_multi_filament.setTitle(QCoreApplication.translate("MainPanel", u"Multi-Filamento (*)", None))
        self.label_desc_multi_filament.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None))
#if QT_CONFIG(tooltip)
        self.combox_desc_multi_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona un filamento", None))
#endif // QT_CONFIG(tooltip)
        self.combox_desc_multi_filament.setPlaceholderText(QCoreApplication.translate("MainPanel", u"Seleccionar  Filamento", None))
        self.textEdit_details_multi_filament_select.setHtml(QCoreApplication.translate("MainPanel", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.btn_filament_5.setText("")
        self.btn_filament_3.setText("")
        self.btn_filament_2.setText("")
        self.btn_filament_6.setText("")
        self.btn_filament_4.setText("")
        self.btn_filament_1.setText("")
        self.alert_mutifilament_label.setText("")
#if QT_CONFIG(tooltip)
        self.btn_multicolor_search.setToolTip(QCoreApplication.translate("MainPanel", u"Buscar filamento por tipo de material", None))
#endif // QT_CONFIG(tooltip)
        self.btn_multicolor_search.setText("")
        self.groupbox_filament.setTitle(QCoreApplication.translate("MainPanel", u"Filamento (*)", None))
        self.label_desc.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None))
#if QT_CONFIG(tooltip)
        self.btn_select_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona Filamento", None))
#endif // QT_CONFIG(tooltip)
        self.btn_select_filament.setText(QCoreApplication.translate("MainPanel", u" Filamento", None))
#if QT_CONFIG(tooltip)
        self.combox_desc_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona un filamento", None))
#endif // QT_CONFIG(tooltip)
        self.combox_desc_filament.setPlaceholderText(QCoreApplication.translate("MainPanel", u"Seleccionar  Filamento", None))
        self.textEdit_details_filament_select.setHtml(QCoreApplication.translate("MainPanel", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.groupBox_post.setTitle(QCoreApplication.translate("MainPanel", u"Acabado", None))
        self.label_type_post.setText(QCoreApplication.translate("MainPanel", u"Configuraci\u00f3n de Cotizaci\u00f3n (*)", None))
#if QT_CONFIG(tooltip)
        self.combox_type_post.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona la modalidad a cobrar", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_post.setText("")
        self.label_post_on.setText(QCoreApplication.translate("MainPanel", u"Post-procesado:", None))
#if QT_CONFIG(tooltip)
        self.label_post.setToolTip(QCoreApplication.translate("MainPanel", u"Monto total del post-procesado", None))
#endif // QT_CONFIG(tooltip)
        self.label_post.setText(QCoreApplication.translate("MainPanel", u"Monto [Gs.]:", None))
#if QT_CONFIG(tooltip)
        self.doublespinbox_post_price.setToolTip(QCoreApplication.translate("MainPanel", u"Ingrese el monto total del post-procesamiento", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_post_range.setToolTip(QCoreApplication.translate("MainPanel", u"Tipo de cotizacion", None))
#endif // QT_CONFIG(tooltip)
        self.label_post_range.setText(QCoreApplication.translate("MainPanel", u"Alcance:", None))
        self.groupbox_client.setTitle(QCoreApplication.translate("MainPanel", u"Cliente (/)", None))
        self.label_client_razon_social.setText(QCoreApplication.translate("MainPanel", u"Razon Social", None))
#if QT_CONFIG(tooltip)
        self.checkbox_client_optional.setToolTip(QCoreApplication.translate("MainPanel", u"Marcar cliente opcional", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_client_optional.setText(QCoreApplication.translate("MainPanel", u"Opcional", None))
        self.textEdit_name_client_select.setHtml(QCoreApplication.translate("MainPanel", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.textEdit_ruc_ci_client_select.setHtml(QCoreApplication.translate("MainPanel", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.btn_select_client.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona Cliente", None))
#endif // QT_CONFIG(tooltip)
        self.btn_select_client.setText(QCoreApplication.translate("MainPanel", u" Cliente", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner_client.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner_client.setText("")
        self.groupbox_printer_info.setTitle(QCoreApplication.translate("MainPanel", u"Impresora (*)", None))
        self.label_desc_printer.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None))
#if QT_CONFIG(tooltip)
        self.combox_desc_printer.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona una impresora", None))
#endif // QT_CONFIG(tooltip)
        self.combox_desc_printer.setPlaceholderText(QCoreApplication.translate("MainPanel", u"Seleccionar  Impresora", None))
        self.textEdit_details_printer_select.setHtml(QCoreApplication.translate("MainPanel", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.btn_select_printer_3d.setToolTip(QCoreApplication.translate("MainPanel", u"Selecciona Impresora", None))
#endif // QT_CONFIG(tooltip)
        self.btn_select_printer_3d.setText(QCoreApplication.translate("MainPanel", u" Printer3D", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner_printer_3d.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner_printer_3d.setText("")
        self.groupbox_piece_info.setTitle(QCoreApplication.translate("MainPanel", u"Pieza (*)", None))
#if QT_CONFIG(tooltip)
        self.label_time_print.setToolTip(QCoreApplication.translate("MainPanel", u"Tiempo de impresi\u00f3n por lotes", None))
#endif // QT_CONFIG(tooltip)
        self.label_time_print.setText(QCoreApplication.translate("MainPanel", u"Tiempo de impresion (*)", None))
#if QT_CONFIG(tooltip)
        self.label_gram_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Cantidad de gramos a utilizar por lote.", None))
#endif // QT_CONFIG(tooltip)
        self.label_gram_filament.setText(QCoreApplication.translate("MainPanel", u"Gramos de filamento (*)", None))
#if QT_CONFIG(tooltip)
        self.spinbox_gram_piece.setToolTip(QCoreApplication.translate("MainPanel", u"Ingrese la cantidad de gramos a utilizar por lote", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("MainPanel", u"Cantidad en gramos", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MainPanel", u"Cantidad [gr.]:", None))
#if QT_CONFIG(tooltip)
        self.label_hour.setToolTip(QCoreApplication.translate("MainPanel", u"Unidades", None))
#endif // QT_CONFIG(tooltip)
        self.label_hour.setText(QCoreApplication.translate("MainPanel", u"Horas:", None))
#if QT_CONFIG(tooltip)
        self.spinbox_cant_piece.setToolTip(QCoreApplication.translate("MainPanel", u"Ingrese el n\u00famero de lotes a imprimir", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_price_product_2.setToolTip(QCoreApplication.translate("MainPanel", u"N\u00famero de veces a imprimir por cama.", None))
#endif // QT_CONFIG(tooltip)
        self.label_price_product_2.setText(QCoreApplication.translate("MainPanel", u"N\u00ba de lotes ", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MainPanel", u"Cantidad en unidades", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainPanel", u"Cantidad [ud.]:", None))
#if QT_CONFIG(tooltip)
        self.label_minute.setToolTip(QCoreApplication.translate("MainPanel", u"Unidades", None))
#endif // QT_CONFIG(tooltip)
        self.label_minute.setText(QCoreApplication.translate("MainPanel", u" Minutos:", None))
#if QT_CONFIG(tooltip)
        self.spinbox_time_minute_piece.setToolTip(QCoreApplication.translate("MainPanel", u"Introduzca los minutos de impresi\u00f3n de la cortadora", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spinbox_time_hour_piece.setToolTip(QCoreApplication.translate("MainPanel", u"Introduzca las horas de impresi\u00f3n de la cortadora", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_operations.setTitle(QCoreApplication.translate("MainPanel", u"Operaciones", None))
#if QT_CONFIG(tooltip)
        self.btn_clear_all_selected.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar todos los datos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_clear_all_selected.setText(QCoreApplication.translate("MainPanel", u"Limpiar", None))
#if QT_CONFIG(tooltip)
        self.btn_calculator.setToolTip(QCoreApplication.translate("MainPanel", u"Realizar calculo", None))
#endif // QT_CONFIG(tooltip)
        self.btn_calculator.setText(QCoreApplication.translate("MainPanel", u"Calcular", None))
#if QT_CONFIG(tooltip)
        self.btn_tuning.setToolTip(QCoreApplication.translate("MainPanel", u"Parametrizar presupuesto", None))
#endif // QT_CONFIG(tooltip)
        self.btn_tuning.setText(QCoreApplication.translate("MainPanel", u" Param", None))
        self.groupBox_advance.setTitle(QCoreApplication.translate("MainPanel", u"Se\u00f1a", None))
        self.label_advance_on.setText(QCoreApplication.translate("MainPanel", u"Anticipo:", None))
        self.checkbox_advance.setText("")
#if QT_CONFIG(tooltip)
        self.spinbox_advance.setToolTip(QCoreApplication.translate("MainPanel", u"Ingrese el porcentaje del anticipo a solicitar", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_advance.setToolTip(QCoreApplication.translate("MainPanel", u"Porcentaje de anticipo", None))
#endif // QT_CONFIG(tooltip)
        self.label_advance.setText(QCoreApplication.translate("MainPanel", u"(%) aplicado:", None))
        self.groupBox_action.setTitle(QCoreApplication.translate("MainPanel", u"Acci\u00f3n", None))
#if QT_CONFIG(tooltip)
        self.btn_generate.setToolTip(QCoreApplication.translate("MainPanel", u"Generar presupuesto", None))
#endif // QT_CONFIG(tooltip)
        self.btn_generate.setText(QCoreApplication.translate("MainPanel", u" Generar PDF", None))
#if QT_CONFIG(tooltip)
        self.btn_select_type_doc.setToolTip(QCoreApplication.translate("MainPanel", u"Seleccionar tipo de documento a generar", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_preview.setToolTip(QCoreApplication.translate("MainPanel", u"Vista previa", None))
#endif // QT_CONFIG(tooltip)
        self.btn_preview.setText(QCoreApplication.translate("MainPanel", u" Preview", None))
#if QT_CONFIG(tooltip)
        self.btn_close.setToolTip(QCoreApplication.translate("MainPanel", u"Cerrar", None))
#endif // QT_CONFIG(tooltip)
        self.btn_close.setText(QCoreApplication.translate("MainPanel", u" Cerrar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_one), QCoreApplication.translate("MainPanel", u"Presupuesto", None))
        self.groupBox_operations_4.setTitle(QCoreApplication.translate("MainPanel", u"Operaciones", None))
#if QT_CONFIG(tooltip)
        self.btn_open_quote.setToolTip(QCoreApplication.translate("MainPanel", u"Ver archivo", None))
#endif // QT_CONFIG(tooltip)
        self.btn_open_quote.setText(QCoreApplication.translate("MainPanel", u" Archivo", None))
#if QT_CONFIG(tooltip)
        self.btn_delete_quote.setToolTip(QCoreApplication.translate("MainPanel", u"Eliminar archivo", None))
#endif // QT_CONFIG(tooltip)
        self.btn_delete_quote.setText(QCoreApplication.translate("MainPanel", u" Eliminar", None))
#if QT_CONFIG(tooltip)
        self.btn_report_quotes.setToolTip(QCoreApplication.translate("MainPanel", u"Generar reporte", None))
#endif // QT_CONFIG(tooltip)
        self.btn_report_quotes.setText(QCoreApplication.translate("MainPanel", u" Reportes", None))
        self.label_desde.setText(QCoreApplication.translate("MainPanel", u"Desde:", None))
        self.label_hasta.setText(QCoreApplication.translate("MainPanel", u"Hasta:", None))
        self.groupbox_search_4.setTitle(QCoreApplication.translate("MainPanel", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search_4.setToolTip(QCoreApplication.translate("MainPanel", u"Introduce minimo 3 digitos.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search_4.setText("")
        self.btn_search_4.setText(QCoreApplication.translate("MainPanel", u"Consultar", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner_4.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner_4.setText("")
        ___qtablewidgetitem = self.qtable_quote.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainPanel", u"ID", None));
        ___qtablewidgetitem1 = self.qtable_quote.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainPanel", u"N\u00famero", None));
        ___qtablewidgetitem2 = self.qtable_quote.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainPanel", u"Cliente", None));
        ___qtablewidgetitem3 = self.qtable_quote.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainPanel", u"Monto", None));
        ___qtablewidgetitem4 = self.qtable_quote.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainPanel", u"Fecha", None));
        ___qtablewidgetitem5 = self.qtable_quote.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainPanel", u"Archivo", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_five), QCoreApplication.translate("MainPanel", u"Historial", None))
        ___qtablewidgetitem6 = self.qtable_filaments.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainPanel", u"ID", None));
        ___qtablewidgetitem7 = self.qtable_filaments.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None));
        ___qtablewidgetitem8 = self.qtable_filaments.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainPanel", u"Stock", None));
        ___qtablewidgetitem9 = self.qtable_filaments.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainPanel", u"Tipo", None));
        ___qtablewidgetitem10 = self.qtable_filaments.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainPanel", u"Marca", None));
        ___qtablewidgetitem11 = self.qtable_filaments.horizontalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainPanel", u"Color", None));
        ___qtablewidgetitem12 = self.qtable_filaments.horizontalHeaderItem(6)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainPanel", u"Precio", None));
        self.groupBox_operations_2.setTitle(QCoreApplication.translate("MainPanel", u"Operaciones", None))
#if QT_CONFIG(tooltip)
        self.btn_add_more_filament.setToolTip(QCoreApplication.translate("MainPanel", u"A\u00f1adir filamento", None))
#endif // QT_CONFIG(tooltip)
        self.btn_add_more_filament.setText(QCoreApplication.translate("MainPanel", u" A\u00f1adir", None))
#if QT_CONFIG(tooltip)
        self.btn_mod_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Modificar filamento", None))
#endif // QT_CONFIG(tooltip)
        self.btn_mod_filament.setText(QCoreApplication.translate("MainPanel", u" Modificar", None))
#if QT_CONFIG(tooltip)
        self.btn_delete_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Eliminar filamento", None))
#endif // QT_CONFIG(tooltip)
        self.btn_delete_filament.setText(QCoreApplication.translate("MainPanel", u" Eliminar", None))
#if QT_CONFIG(tooltip)
        self.btn_add_filament.setToolTip(QCoreApplication.translate("MainPanel", u"Agregar nuevo filamento", None))
#endif // QT_CONFIG(tooltip)
        self.btn_add_filament.setText(QCoreApplication.translate("MainPanel", u" Filamento", None))
        self.groupbox_search.setTitle(QCoreApplication.translate("MainPanel", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search.setToolTip(QCoreApplication.translate("MainPanel", u"Introduce minimo 3 digitos.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search.setText("")
        self.btn_search.setText(QCoreApplication.translate("MainPanel", u"Consultar", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_two), QCoreApplication.translate("MainPanel", u"Inventario", None))
        self.groupBox_operations_3.setTitle(QCoreApplication.translate("MainPanel", u"Operaciones", None))
#if QT_CONFIG(tooltip)
        self.btn_mod_printer.setToolTip(QCoreApplication.translate("MainPanel", u"Modificar impresora", None))
#endif // QT_CONFIG(tooltip)
        self.btn_mod_printer.setText(QCoreApplication.translate("MainPanel", u" Modificar", None))
#if QT_CONFIG(tooltip)
        self.btn_delete_printer.setToolTip(QCoreApplication.translate("MainPanel", u"Eliminar Impresora", None))
#endif // QT_CONFIG(tooltip)
        self.btn_delete_printer.setText(QCoreApplication.translate("MainPanel", u" Eliminar", None))
#if QT_CONFIG(tooltip)
        self.btn_add_printer.setToolTip(QCoreApplication.translate("MainPanel", u"Agregar nueva impresora", None))
#endif // QT_CONFIG(tooltip)
        self.btn_add_printer.setText(QCoreApplication.translate("MainPanel", u" Printer", None))
        self.groupbox_search_2.setTitle(QCoreApplication.translate("MainPanel", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search_2.setToolTip(QCoreApplication.translate("MainPanel", u"Introduce minimo 3 digitos.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search_2.setText("")
        self.btn_search_2.setText(QCoreApplication.translate("MainPanel", u"Consultar", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner_2.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner_2.setText("")
        ___qtablewidgetitem13 = self.qtable_printers.horizontalHeaderItem(0)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainPanel", u"ID", None));
        ___qtablewidgetitem14 = self.qtable_printers.horizontalHeaderItem(1)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainPanel", u"Descripcion", None));
        ___qtablewidgetitem15 = self.qtable_printers.horizontalHeaderItem(2)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainPanel", u"Modelo", None));
        ___qtablewidgetitem16 = self.qtable_printers.horizontalHeaderItem(3)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainPanel", u"Marca", None));
        ___qtablewidgetitem17 = self.qtable_printers.horizontalHeaderItem(4)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainPanel", u"Consumo", None));
        ___qtablewidgetitem18 = self.qtable_printers.horizontalHeaderItem(5)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainPanel", u"Costo", None));
        ___qtablewidgetitem19 = self.qtable_printers.horizontalHeaderItem(6)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainPanel", u"Status", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_three), QCoreApplication.translate("MainPanel", u"Impresoras", None))
        self.groupBox_operations_5.setTitle(QCoreApplication.translate("MainPanel", u"Operaciones", None))
#if QT_CONFIG(tooltip)
        self.btn_default_customer.setToolTip(QCoreApplication.translate("MainPanel", u"Marcar cliente predeterminado", None))
#endif // QT_CONFIG(tooltip)
        self.btn_default_customer.setText(QCoreApplication.translate("MainPanel", u" Predeterminar", None))
#if QT_CONFIG(tooltip)
        self.btn_mod_customer.setToolTip(QCoreApplication.translate("MainPanel", u"Modificar cliente", None))
#endif // QT_CONFIG(tooltip)
        self.btn_mod_customer.setText(QCoreApplication.translate("MainPanel", u" Modificar", None))
#if QT_CONFIG(tooltip)
        self.btn_delete_customer.setToolTip(QCoreApplication.translate("MainPanel", u"Eliminar cliente", None))
#endif // QT_CONFIG(tooltip)
        self.btn_delete_customer.setText(QCoreApplication.translate("MainPanel", u" Eliminar", None))
#if QT_CONFIG(tooltip)
        self.btn_add_customer.setToolTip(QCoreApplication.translate("MainPanel", u"Agregar nuevo cliente", None))
#endif // QT_CONFIG(tooltip)
        self.btn_add_customer.setText(QCoreApplication.translate("MainPanel", u" Cliente", None))
        self.groupbox_search_3.setTitle(QCoreApplication.translate("MainPanel", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search_3.setToolTip(QCoreApplication.translate("MainPanel", u"Introduce minimo 3 digitos.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search_3.setText("")
        self.btn_search_3.setText(QCoreApplication.translate("MainPanel", u"Consultar", None))
#if QT_CONFIG(tooltip)
        self.btn_cleaner_3.setToolTip(QCoreApplication.translate("MainPanel", u"Limpiar campos", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cleaner_3.setText("")
        ___qtablewidgetitem20 = self.qtable_customers.horizontalHeaderItem(0)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainPanel", u"ID", None));
        ___qtablewidgetitem21 = self.qtable_customers.horizontalHeaderItem(1)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainPanel", u"Razon Social", None));
        ___qtablewidgetitem22 = self.qtable_customers.horizontalHeaderItem(2)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainPanel", u"RUC / CI", None));
        ___qtablewidgetitem23 = self.qtable_customers.horizontalHeaderItem(3)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainPanel", u"Telefono", None));
        ___qtablewidgetitem24 = self.qtable_customers.horizontalHeaderItem(4)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainPanel", u"Email", None));
        ___qtablewidgetitem25 = self.qtable_customers.horizontalHeaderItem(5)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainPanel", u"Preferencia", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_six), QCoreApplication.translate("MainPanel", u"Clientes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_four), QCoreApplication.translate("MainPanel", u"Ajustes", None))
        self.groupbox_details.setTitle(QCoreApplication.translate("MainPanel", u"Resumen", None))
        self.plaintextedit_status.setPlaceholderText(QCoreApplication.translate("MainPanel", u"Procesos", None))
#if QT_CONFIG(tooltip)
        self.donationLabel.setToolTip(QCoreApplication.translate("MainPanel", u"\u00a1Dona al desarrollador de este programa!", None))
#endif // QT_CONFIG(tooltip)
        self.donationLabel.setText(QCoreApplication.translate("MainPanel", u"Dona!", None))
        self.eventLabel_pb.setText(QCoreApplication.translate("MainPanel", u"Voxeprint3D", None))
#if QT_CONFIG(tooltip)
        self.version.setToolTip(QCoreApplication.translate("MainPanel", u"Version del software", None))
#endif // QT_CONFIG(tooltip)
        self.version.setText(QCoreApplication.translate("MainPanel", u"v1.1.2", None))
        self.btn_toggle_panel.setText("")
    # retranslateUi


