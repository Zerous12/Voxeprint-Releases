from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
    QSize,Qt)
from PySide6.QtGui import (QBrush, QColor,  QCursor,
    QFont, QIcon, QPalette)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, 
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_Temp_Select_Filaments(object):
    def setupUi(self, Temp_Select_Filaments):
        if not Temp_Select_Filaments.objectName():
            Temp_Select_Filaments.setObjectName(u"Temp_Select_Filaments")
        Temp_Select_Filaments.resize(800, 547)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Temp_Select_Filaments.sizePolicy().hasHeightForWidth())
        Temp_Select_Filaments.setSizePolicy(sizePolicy)
        Temp_Select_Filaments.setMinimumSize(QSize(800, 547))
        Temp_Select_Filaments.setMaximumSize(QSize(800, 16777215))
        Temp_Select_Filaments.setStyleSheet(u"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QDialog */\n"
"QDialog#Temp_Select_Filaments {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 86, 115, 255), stop:1 rgba(55, 55,55, 255));}\n"
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
"    border-top-right-radius: "
                        "0px;\n"
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
"}\n"
"\n"
"")
        self.gridLayout_2 = QGridLayout(Temp_Select_Filaments)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 0, 8)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, -1, 14, -1)
        self.label_headboard = QLabel(Temp_Select_Filaments)
        self.label_headboard.setObjectName(u"label_headboard")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_headboard.sizePolicy().hasHeightForWidth())
        self.label_headboard.setSizePolicy(sizePolicy1)
        self.label_headboard.setMinimumSize(QSize(270, 50))
        self.label_headboard.setMaximumSize(QSize(16777215, 50))
        font = QFont()
        font.setFamilies([u"Segoe UI Black"])
        font.setPointSize(24)
        font.setBold(True)
        self.label_headboard.setFont(font)
        self.label_headboard.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.label_headboard)

        self.horizontalSpacer_2 = QSpacerItem(220, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.btn_refresh_panel = QPushButton(Temp_Select_Filaments)
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
        self.btn_add_filament = QPushButton(Temp_Select_Filaments)
        self.btn_add_filament.setObjectName(u"btn_add_filament")
        self.btn_add_filament.setMinimumSize(QSize(125, 40))
        self.btn_add_filament.setMaximumSize(QSize(125, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Black"])
        font1.setPointSize(11)
        self.btn_add_filament.setFont(font1)
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
        icon1 = QIcon()
        icon1.addFile(u":/resources/resources/icons/sys_plus_circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_add_filament.setIcon(icon1)
        self.btn_add_filament.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.btn_add_filament)

        self.horizontalSpacer = QSpacerItem(380, 60, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groupbox_search = QGroupBox(Temp_Select_Filaments)
        self.groupbox_search.setObjectName(u"groupbox_search")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupbox_search.sizePolicy().hasHeightForWidth())
        self.groupbox_search.setSizePolicy(sizePolicy2)
        self.groupbox_search.setMinimumSize(QSize(0, 60))
        self.groupbox_search.setMaximumSize(QSize(320, 60))
        font2 = QFont()
        font2.setBold(True)
        font2.setItalic(False)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        self.groupbox_search.setFont(font2)
        self.groupbox_search.setStyleSheet(u"")
        self.groupbox_search.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayout_21 = QVBoxLayout(self.groupbox_search)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.linedit_search = QLineEdit(self.groupbox_search)
        self.linedit_search.setObjectName(u"linedit_search")
        sizePolicy1.setHeightForWidth(self.linedit_search.sizePolicy().hasHeightForWidth())
        self.linedit_search.setSizePolicy(sizePolicy1)
        self.linedit_search.setMinimumSize(QSize(0, 25))
        self.linedit_search.setMaximumSize(QSize(16777215, 24))
        self.linedit_search.setStyleSheet(u"")

        self.horizontalLayout_10.addWidget(self.linedit_search)

        self.btn_search = QPushButton(self.groupbox_search)
        self.btn_search.setObjectName(u"btn_search")
        self.btn_search.setMinimumSize(QSize(80, 25))
        self.btn_search.setMaximumSize(QSize(16777215, 24))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI Black"])
        font3.setPointSize(10)
        font3.setBold(True)
        self.btn_search.setFont(font3)
        self.btn_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_search.setStyleSheet(u"")

        self.horizontalLayout_10.addWidget(self.btn_search)


        self.verticalLayout_21.addLayout(self.horizontalLayout_10)


        self.horizontalLayout.addWidget(self.groupbox_search)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.frame_container_selector = QFrame(Temp_Select_Filaments)
        self.frame_container_selector.setObjectName(u"frame_container_selector")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_container_selector.sizePolicy().hasHeightForWidth())
        self.frame_container_selector.setSizePolicy(sizePolicy3)
        self.frame_container_selector.setMinimumSize(QSize(800, 420))
        self.frame_container_selector.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_container_selector.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_container_selector)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 10)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.qtable_filament = QTableWidget(self.frame_container_selector)
        if (self.qtable_filament.columnCount() < 6):
            self.qtable_filament.setColumnCount(6)
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Black"])
        font4.setPointSize(10)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font4);
        self.qtable_filament.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font4);
        self.qtable_filament.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font4);
        self.qtable_filament.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font4);
        self.qtable_filament.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font4);
        self.qtable_filament.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font3);
        self.qtable_filament.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.qtable_filament.setObjectName(u"qtable_filament")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.qtable_filament.sizePolicy().hasHeightForWidth())
        self.qtable_filament.setSizePolicy(sizePolicy4)
        self.qtable_filament.setMinimumSize(QSize(530, 320))
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
        self.qtable_filament.setPalette(palette)
        font5 = QFont()
        font5.setPointSize(10)
        self.qtable_filament.setFont(font5)
        self.qtable_filament.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.qtable_filament.setStyleSheet(u"")
        self.qtable_filament.setFrameShape(QFrame.Shape.NoFrame)
        self.qtable_filament.setFrameShadow(QFrame.Shadow.Sunken)
        self.qtable_filament.setLineWidth(1)
        self.qtable_filament.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.qtable_filament.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.qtable_filament.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.qtable_filament.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.qtable_filament.setIconSize(QSize(0, 0))
        self.qtable_filament.setShowGrid(True)
        self.qtable_filament.setGridStyle(Qt.PenStyle.SolidLine)
        self.qtable_filament.setSortingEnabled(True)
        self.qtable_filament.setRowCount(0)
        self.qtable_filament.setColumnCount(6)
        self.qtable_filament.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_filament.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_filament.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_filament.horizontalHeader().setHighlightSections(True)
        self.qtable_filament.horizontalHeader().setStretchLastSection(False)
        self.qtable_filament.verticalHeader().setVisible(False)
        self.qtable_filament.verticalHeader().setMinimumSectionSize(32)
        self.qtable_filament.verticalHeader().setDefaultSectionSize(32)

        self.horizontalLayout_3.addWidget(self.qtable_filament)

        self.line_separator = QFrame(self.frame_container_selector)
        self.line_separator.setObjectName(u"line_separator")
        self.line_separator.setFrameShape(QFrame.Shape.VLine)
        self.line_separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_3.addWidget(self.line_separator)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_filament_details_title = QLabel(self.frame_container_selector)
        self.label_filament_details_title.setObjectName(u"label_filament_details_title")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_filament_details_title.sizePolicy().hasHeightForWidth())
        self.label_filament_details_title.setSizePolicy(sizePolicy5)
        self.label_filament_details_title.setMinimumSize(QSize(230, 41))
        self.label_filament_details_title.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_filament_details_title)

        self.textEdit_details_filament = QTextEdit(self.frame_container_selector)
        self.textEdit_details_filament.setObjectName(u"textEdit_details_filament")
        self.textEdit_details_filament.setMinimumSize(QSize(230, 171))
        self.textEdit_details_filament.setStyleSheet(u"")
        self.textEdit_details_filament.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.textEdit_details_filament)

        self.label_filament_stock = QLabel(self.frame_container_selector)
        self.label_filament_stock.setObjectName(u"label_filament_stock")
        sizePolicy5.setHeightForWidth(self.label_filament_stock.sizePolicy().hasHeightForWidth())
        self.label_filament_stock.setSizePolicy(sizePolicy5)
        self.label_filament_stock.setMinimumSize(QSize(230, 41))
        self.label_filament_stock.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_filament_stock)

        self.label_filament_price = QLabel(self.frame_container_selector)
        self.label_filament_price.setObjectName(u"label_filament_price")
        sizePolicy5.setHeightForWidth(self.label_filament_price.sizePolicy().hasHeightForWidth())
        self.label_filament_price.setSizePolicy(sizePolicy5)
        self.label_filament_price.setMinimumSize(QSize(230, 41))
        self.label_filament_price.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.label_filament_price)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(2, -1, 2, -1)
        self.groupBox_action = QGroupBox(self.frame_container_selector)
        self.groupBox_action.setObjectName(u"groupBox_action")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.groupBox_action.sizePolicy().hasHeightForWidth())
        self.groupBox_action.setSizePolicy(sizePolicy6)
        self.groupBox_action.setMinimumSize(QSize(0, 85))
        font6 = QFont()
        font6.setBold(False)
        self.groupBox_action.setFont(font6)
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

        self.horizontalSpacer_3 = QSpacerItem(0, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.btn_ok_select = QPushButton(self.groupBox_action)
        self.btn_ok_select.setObjectName(u"btn_ok_select")
        self.btn_ok_select.setMinimumSize(QSize(120, 40))
        self.btn_ok_select.setMaximumSize(QSize(120, 40))
        self.btn_ok_select.setFont(font1)
        self.btn_ok_select.setStyleSheet(u"QPushButton {\n"
"color: #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #7ad17a;\n"
"}            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #00aa00;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
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
        font7 = QFont()
        font7.setFamilies([u"Segoe UI Black"])
        font7.setPointSize(11)
        font7.setBold(True)
        font7.setItalic(False)
        font7.setUnderline(False)
        self.btn_cancel_select.setFont(font7)
        self.btn_cancel_select.setStyleSheet(u"QPushButton {\n"
"color: #e6fdff;\n"
"border: 1px solid #bcbcbc ;\n"
"border-radius: 5px; \n"
"background-color:  #f09292;\n"
"}            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color:  #be0000;\n"
"border: 1px solid #00aaff ;\n"
"}\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ff0000;\n"
"border: 1px solid #69cdff ;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.btn_cancel_select)


        self.horizontalLayout_5.addWidget(self.groupBox_action)


        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_container_selector, 1, 0, 1, 1)


        self.retranslateUi(Temp_Select_Filaments)

        QMetaObject.connectSlotsByName(Temp_Select_Filaments)
    # setupUi

    def retranslateUi(self, Temp_Select_Filaments):
        Temp_Select_Filaments.setWindowTitle(QCoreApplication.translate("Temp_Select_Filaments", u"Dialog", None))
        self.label_headboard.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Seleccionar Filamento", None))
        self.btn_refresh_panel.setText("")
        self.btn_add_filament.setText(QCoreApplication.translate("Temp_Select_Filaments", u" Filamento", None))
        self.groupbox_search.setTitle(QCoreApplication.translate("Temp_Select_Filaments", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search.setToolTip(QCoreApplication.translate("Temp_Select_Filaments", u"Introduce minimo 2 letras.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search.setText("")
        self.btn_search.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Consultar", None))
        ___qtablewidgetitem = self.qtable_filament.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Temp_Select_Filaments", u"ID", None));
        ___qtablewidgetitem1 = self.qtable_filament.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Descripcion", None));
        ___qtablewidgetitem2 = self.qtable_filament.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Tipo", None));
        ___qtablewidgetitem3 = self.qtable_filament.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Marca", None));
        ___qtablewidgetitem4 = self.qtable_filament.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Color", None));
        ___qtablewidgetitem5 = self.qtable_filament.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Status", None));
        self.label_filament_details_title.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Detalles del Filamento:", None))
        self.label_filament_stock.setText(QCoreApplication.translate("Temp_Select_Filaments", u" Stock: No seleccionado", None))
        self.label_filament_price.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Precio: No seleccionado", None))
        self.groupBox_action.setTitle(QCoreApplication.translate("Temp_Select_Filaments", u"Acci\u00f3n", None))
        self.label_select.setText(QCoreApplication.translate("Temp_Select_Filaments", u"Ning\u00fan filamento seleccionado", None))
#if QT_CONFIG(tooltip)
        self.btn_ok_select.setToolTip(QCoreApplication.translate("Temp_Select_Filaments", u"Aceptar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_ok_select.setText(QCoreApplication.translate("Temp_Select_Filaments", u"\u2714 Seleccionar", None))
#if QT_CONFIG(tooltip)
        self.btn_cancel_select.setToolTip(QCoreApplication.translate("Temp_Select_Filaments", u"Cancelar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cancel_select.setText(QCoreApplication.translate("Temp_Select_Filaments", u"\u2715 Cancelar", None))
    # retranslateUi

