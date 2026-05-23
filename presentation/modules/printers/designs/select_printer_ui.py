from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
    QSize,Qt)
from PySide6.QtGui import (QBrush, QColor,  QCursor,
    QFont, QIcon, QPalette)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, 
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_Temp_Select_Printers(object):
    def setupUi(self, Temp_Select_Printers):
        if not Temp_Select_Printers.objectName():
            Temp_Select_Printers.setObjectName(u"Temp_Select_Printers")
        Temp_Select_Printers.resize(800, 547)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Temp_Select_Printers.sizePolicy().hasHeightForWidth())
        Temp_Select_Printers.setSizePolicy(sizePolicy)
        Temp_Select_Printers.setMinimumSize(QSize(800, 547))
        Temp_Select_Printers.setMaximumSize(QSize(800, 16777215))
        Temp_Select_Printers.setStyleSheet(u"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QDialog */\n"
"QDialog#Temp_Select_Printers {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 86, 115, 255), stop:1 rgba(55, 55,55, 255));}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QGroupBox */\n"
"QGroupBox#groupbox_search{\n"
"margin-top: 1ex;\n"
"padding-top: 2px; \n"
"border: 1px solid rgb(255, 255, 255);\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"}\n"
"QGroupBox:title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding:  0px 2px 0px 2px;\n"
"}\n"
"\n"
"/* Estilos para todos los QLineEdit de b\u00fasqueda (search, search_2, search_3, search_4) */\n"
"QLineEdit#linedit_search {\n"
"    background-color: rgb(255, 255, 255);\n"
"    color: rgb(0, 0, 0);\n"
"    border-top-left-radius: 5px;\n"
"    border-bottom-left-radius: 5px;\n"
"    border-top-right-radius: 0"
                        "px;\n"
"    border-bottom-right-radius: 0px;\n"
"    border-top: 1px solid black;\n"
"    border-bottom: 1px solid black;\n"
"    border-left: 1px solid black;\n"
"}\n"
"/* Estilos para todos los botones de b\u00fasqueda (btn_search, btn_search_2, btn_search_3, btn_search_4) */\n"
"QPushButton#btn_search {\n"
"    border-radius: 0px;\n"
"    background-color: #46aa8f;\n"
"    color: rgb(255, 255, 255);\n"
"    border: 1px solid black;\n"
"	border-top-right-radius: 5px;\n"
"	border-bottom-right-radius: 5px;\n"
"}\n"
"/* Estilos hover para todos los botones de b\u00fasqueda y limpieza */\n"
"QPushButton#btn_search:hover{\n"
"    background-color: rgb(0, 170, 240);\n"
"    border-color: rgb(52, 59, 72);\n"
"}\n"
"/* Estilos pressed para todos los botones de b\u00fasqueda y limpieza */\n"
"QPushButton#btn_search:pressed {\n"
"    background-color: rgb(255, 170, 0);\n"
"    border-color: rgb(43, 50, 61);\n"
"}")
        self.gridLayout_2 = QGridLayout(Temp_Select_Printers)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Temp_Select_Printers)
        self.frame.setObjectName(u"frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setMinimumSize(QSize(800, 420))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(2, 0, 2, 10)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.qtable_printers = QTableWidget(self.frame)
        if (self.qtable_printers.columnCount() < 5):
            self.qtable_printers.setColumnCount(5)
        font = QFont()
        font.setFamilies([u"Segoe UI Black"])
        font.setPointSize(10)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font);
        self.qtable_printers.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font);
        self.qtable_printers.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font);
        self.qtable_printers.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font);
        self.qtable_printers.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Black"])
        font1.setPointSize(10)
        font1.setBold(True)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font1);
        self.qtable_printers.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.qtable_printers.setObjectName(u"qtable_printers")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.qtable_printers.sizePolicy().hasHeightForWidth())
        self.qtable_printers.setSizePolicy(sizePolicy2)
        self.qtable_printers.setMinimumSize(QSize(530, 320))
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
        self.qtable_printers.setPalette(palette)
        font2 = QFont()
        font2.setPointSize(10)
        self.qtable_printers.setFont(font2)
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
        self.qtable_printers.setSortingEnabled(True)
        self.qtable_printers.setRowCount(0)
        self.qtable_printers.setColumnCount(5)
        self.qtable_printers.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_printers.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_printers.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_printers.horizontalHeader().setHighlightSections(True)
        self.qtable_printers.horizontalHeader().setStretchLastSection(False)
        self.qtable_printers.verticalHeader().setVisible(False)
        self.qtable_printers.verticalHeader().setMinimumSectionSize(32)
        self.qtable_printers.verticalHeader().setDefaultSectionSize(32)

        self.horizontalLayout_3.addWidget(self.qtable_printers)

        self.line_separator = QFrame(self.frame)
        self.line_separator.setObjectName(u"line_separator")
        self.line_separator.setFrameShape(QFrame.Shape.VLine)
        self.line_separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_3.addWidget(self.line_separator)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_printer_details_title = QLabel(self.frame)
        self.label_printer_details_title.setObjectName(u"label_printer_details_title")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_printer_details_title.sizePolicy().hasHeightForWidth())
        self.label_printer_details_title.setSizePolicy(sizePolicy3)
        self.label_printer_details_title.setMinimumSize(QSize(230, 41))
        self.label_printer_details_title.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_printer_details_title)

        self.textEdit_details_printer = QTextEdit(self.frame)
        self.textEdit_details_printer.setObjectName(u"textEdit_details_printer")
        self.textEdit_details_printer.setMinimumSize(QSize(230, 171))
        self.textEdit_details_printer.setStyleSheet(u"")
        self.textEdit_details_printer.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.textEdit_details_printer)

        self.label_printer_consumo = QLabel(self.frame)
        self.label_printer_consumo.setObjectName(u"label_printer_consumo")
        sizePolicy3.setHeightForWidth(self.label_printer_consumo.sizePolicy().hasHeightForWidth())
        self.label_printer_consumo.setSizePolicy(sizePolicy3)
        self.label_printer_consumo.setMinimumSize(QSize(230, 41))
        self.label_printer_consumo.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_printer_consumo)

        self.label_printer_operation_price = QLabel(self.frame)
        self.label_printer_operation_price.setObjectName(u"label_printer_operation_price")
        sizePolicy3.setHeightForWidth(self.label_printer_operation_price.sizePolicy().hasHeightForWidth())
        self.label_printer_operation_price.setSizePolicy(sizePolicy3)
        self.label_printer_operation_price.setMinimumSize(QSize(230, 41))
        self.label_printer_operation_price.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_printer_operation_price)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(2, -1, 2, -1)
        self.groupBox_action = QGroupBox(self.frame)
        self.groupBox_action.setObjectName(u"groupBox_action")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.groupBox_action.sizePolicy().hasHeightForWidth())
        self.groupBox_action.setSizePolicy(sizePolicy4)
        self.groupBox_action.setMinimumSize(QSize(0, 85))
        font3 = QFont()
        font3.setBold(False)
        self.groupBox_action.setFont(font3)
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_action)
        self.horizontalLayout_4.setSpacing(12)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(12, 3, 12, 10)
        self.label_select = QLabel(self.groupBox_action)
        self.label_select.setObjectName(u"label_select")
        sizePolicy.setHeightForWidth(self.label_select.sizePolicy().hasHeightForWidth())
        self.label_select.setSizePolicy(sizePolicy)
        self.label_select.setMinimumSize(QSize(210, 40))
        self.label_select.setStyleSheet(u"")
        self.label_select.setScaledContents(True)

        self.horizontalLayout_4.addWidget(self.label_select)

        self.horizontalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.btn_ok_select = QPushButton(self.groupBox_action)
        self.btn_ok_select.setObjectName(u"btn_ok_select")
        self.btn_ok_select.setMinimumSize(QSize(120, 40))
        self.btn_ok_select.setMaximumSize(QSize(120, 40))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Black"])
        font4.setPointSize(11)
        self.btn_ok_select.setFont(font4)
        self.btn_ok_select.setStyleSheet(u"QPushButton {\n"
"color: #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #7ad17a;\n"
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
"}")

        self.horizontalLayout_4.addWidget(self.btn_ok_select)

        self.btn_cancel_select = QPushButton(self.groupBox_action)
        self.btn_cancel_select.setObjectName(u"btn_cancel_select")
        self.btn_cancel_select.setMinimumSize(QSize(120, 40))
        self.btn_cancel_select.setMaximumSize(QSize(120, 40))
        font5 = QFont()
        font5.setFamilies([u"Segoe UI Black"])
        font5.setPointSize(11)
        font5.setBold(True)
        font5.setItalic(False)
        font5.setUnderline(False)
        self.btn_cancel_select.setFont(font5)
        self.btn_cancel_select.setStyleSheet(u"QPushButton {\n"
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
"")

        self.horizontalLayout_4.addWidget(self.btn_cancel_select)


        self.horizontalLayout_7.addWidget(self.groupBox_action)


        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 8)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, -1, 14, -1)
        self.label_headboard = QLabel(Temp_Select_Printers)
        self.label_headboard.setObjectName(u"label_headboard")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_headboard.sizePolicy().hasHeightForWidth())
        self.label_headboard.setSizePolicy(sizePolicy5)
        self.label_headboard.setMinimumSize(QSize(270, 50))
        self.label_headboard.setMaximumSize(QSize(16777215, 50))
        font6 = QFont()
        font6.setFamilies([u"Segoe UI Black"])
        font6.setPointSize(24)
        font6.setBold(True)
        self.label_headboard.setFont(font6)
        self.label_headboard.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.label_headboard)

        self.horizontalSpacer_2 = QSpacerItem(220, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.btn_refresh_panel = QPushButton(Temp_Select_Printers)
        self.btn_refresh_panel.setObjectName(u"btn_refresh_panel")
        self.btn_refresh_panel.setMinimumSize(QSize(29, 29))
        self.btn_refresh_panel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_refresh_panel.setStyleSheet(u"QPushButton {\n"
"	border: 1px solid rgb(52, 59, 72);\n"
"	border-radius: 14px; \n"
"	background-color: #46aa8f;\n"
"}            \n"
"QPushButton:hover {\n"
"	background-color: #69cdff;\n"
"	border: 1px solid rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed { \n"
"	border-radius: 14px;  \n"
"	background-color: #ffaa00;\n"
"	border: 6px solid transparent;\n"
"}\n"
"QPushButton:disabled { \n"
"	background-color: #92a1a2;\n"
"	opacity: 0.5;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/resources/resources/icons/sys_refresh_alt_fat.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_refresh_panel.setIcon(icon)
        self.btn_refresh_panel.setIconSize(QSize(18, 18))
#if QT_CONFIG(shortcut)
        self.btn_refresh_panel.setShortcut(u"")
#endif // QT_CONFIG(shortcut)

        self.horizontalLayout_2.addWidget(self.btn_refresh_panel)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout.setContentsMargins(8, 0, 8, 0)
        self.btn_add_printer = QPushButton(Temp_Select_Printers)
        self.btn_add_printer.setObjectName(u"btn_add_printer")
        self.btn_add_printer.setMinimumSize(QSize(125, 40))
        self.btn_add_printer.setMaximumSize(QSize(125, 41))
        self.btn_add_printer.setFont(font4)
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
        icon1 = QIcon()
        icon1.addFile(u":/resources/resources/icons/sys_plus_circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_add_printer.setIcon(icon1)
        self.btn_add_printer.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.btn_add_printer)

        self.horizontalSpacer = QSpacerItem(380, 60, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groupbox_search = QGroupBox(Temp_Select_Printers)
        self.groupbox_search.setObjectName(u"groupbox_search")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.groupbox_search.sizePolicy().hasHeightForWidth())
        self.groupbox_search.setSizePolicy(sizePolicy6)
        self.groupbox_search.setMinimumSize(QSize(0, 60))
        self.groupbox_search.setMaximumSize(QSize(320, 60))
        font7 = QFont()
        font7.setBold(True)
        font7.setItalic(False)
        font7.setUnderline(False)
        font7.setStrikeOut(False)
        self.groupbox_search.setFont(font7)
        self.groupbox_search.setStyleSheet(u"")
        self.groupbox_search.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_21 = QVBoxLayout(self.groupbox_search)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.linedit_search = QLineEdit(self.groupbox_search)
        self.linedit_search.setObjectName(u"linedit_search")
        sizePolicy5.setHeightForWidth(self.linedit_search.sizePolicy().hasHeightForWidth())
        self.linedit_search.setSizePolicy(sizePolicy5)
        self.linedit_search.setMinimumSize(QSize(0, 24))
        self.linedit_search.setMaximumSize(QSize(16777215, 24))
        self.linedit_search.setStyleSheet(u"")

        self.horizontalLayout_10.addWidget(self.linedit_search)

        self.btn_search = QPushButton(self.groupbox_search)
        self.btn_search.setObjectName(u"btn_search")
        self.btn_search.setMinimumSize(QSize(80, 24))
        self.btn_search.setMaximumSize(QSize(16777215, 24))
        self.btn_search.setFont(font1)
        self.btn_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search.setStyleSheet(u"")

        self.horizontalLayout_10.addWidget(self.btn_search)


        self.verticalLayout_21.addLayout(self.horizontalLayout_10)


        self.horizontalLayout.addWidget(self.groupbox_search)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(Temp_Select_Printers)

        QMetaObject.connectSlotsByName(Temp_Select_Printers)
    # setupUi

    def retranslateUi(self, Temp_Select_Printers):
        Temp_Select_Printers.setWindowTitle(QCoreApplication.translate("Temp_Select_Printers", u"Dialog", None))
        ___qtablewidgetitem = self.qtable_printers.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Temp_Select_Printers", u"ID", None));
        ___qtablewidgetitem1 = self.qtable_printers.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Temp_Select_Printers", u"Descripcion", None));
        ___qtablewidgetitem2 = self.qtable_printers.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Temp_Select_Printers", u"Modelo", None));
        ___qtablewidgetitem3 = self.qtable_printers.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Temp_Select_Printers", u"Marca", None));
        ___qtablewidgetitem4 = self.qtable_printers.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Temp_Select_Printers", u"Status", None));
        self.label_printer_details_title.setText(QCoreApplication.translate("Temp_Select_Printers", u"Detalles del Printer:", None))
        self.label_printer_consumo.setText(QCoreApplication.translate("Temp_Select_Printers", u"Consumo: No seleccionado", None))
        self.label_printer_operation_price.setText(QCoreApplication.translate("Temp_Select_Printers", u"Precio de operacion: No seleccionado", None))
        self.groupBox_action.setTitle(QCoreApplication.translate("Temp_Select_Printers", u"Acci\u00f3n", None))
        self.label_select.setText(QCoreApplication.translate("Temp_Select_Printers", u"Ning\u00fana impresora seleccionada", None))
#if QT_CONFIG(tooltip)
        self.btn_ok_select.setToolTip(QCoreApplication.translate("Temp_Select_Printers", u"Aceptar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_ok_select.setText(QCoreApplication.translate("Temp_Select_Printers", u"\u2714 Seleccionar", None))
#if QT_CONFIG(tooltip)
        self.btn_cancel_select.setToolTip(QCoreApplication.translate("Temp_Select_Printers", u"Cancelar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cancel_select.setText(QCoreApplication.translate("Temp_Select_Printers", u"\u2715 Cancelar", None))
        self.label_headboard.setText(QCoreApplication.translate("Temp_Select_Printers", u"Seleccionar Printer", None))
        self.btn_refresh_panel.setText("")
        self.btn_add_printer.setText(QCoreApplication.translate("Temp_Select_Printers", u" Printer", None))
        self.groupbox_search.setTitle(QCoreApplication.translate("Temp_Select_Printers", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search.setToolTip(QCoreApplication.translate("Temp_Select_Printers", u"Introduce minimo 2 letras.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search.setText("")
        self.btn_search.setText(QCoreApplication.translate("Temp_Select_Printers", u"Consultar", None))
    # retranslateUi

