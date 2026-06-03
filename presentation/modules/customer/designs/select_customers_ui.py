from PySide6.QtWidgets import ( QAbstractScrollArea, QLabel, QGridLayout, QFrame, QSizePolicy, QWidget, QVBoxLayout,
                                QHBoxLayout, QSpacerItem, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                                QAbstractItemView, QGroupBox)
from PySide6.QtCore import Qt, QSize, QRect, QCoreApplication, QMetaObject
from PySide6.QtGui import  QIcon, QCursor, QFont

class Ui_Temp_Select_Customers(object):
    def setupUi(self, Temp_Select_Customers):
        if not Temp_Select_Customers.objectName():
            Temp_Select_Customers.setObjectName(u"Temp_Select_Customers")
        Temp_Select_Customers.resize(670, 531)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Temp_Select_Customers.sizePolicy().hasHeightForWidth())
        Temp_Select_Customers.setSizePolicy(sizePolicy)
        Temp_Select_Customers.setMinimumSize(QSize(670, 531))
        Temp_Select_Customers.setMaximumSize(QSize(670, 16777215))
        Temp_Select_Customers.setStyleSheet(u"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QDialog */\n"
"QDialog#Temp_Select_Customers {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 86, 115, 255), stop:1 rgba(55, 55,55, 255));}\n"
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
"}")
        self.gridLayout_2 = QGridLayout(Temp_Select_Customers)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(12, -1, 14, -1)
        self.label_headboard = QLabel(Temp_Select_Customers)
        self.label_headboard.setObjectName(u"label_headboard")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_headboard.sizePolicy().hasHeightForWidth())
        self.label_headboard.setSizePolicy(sizePolicy1)
        self.label_headboard.setMinimumSize(QSize(270, 41))
        self.label_headboard.setMaximumSize(QSize(16777215, 50))
        font = QFont()
        font.setFamilies([u"Segoe UI Black"])
        font.setPointSize(24)
        font.setBold(True)
        self.label_headboard.setFont(font)
        self.label_headboard.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_3.addWidget(self.label_headboard)

        self.horizontalSpacer_2 = QSpacerItem(315, 48, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.btn_refresh_panel = QPushButton(Temp_Select_Customers)
        self.btn_refresh_panel.setObjectName(u"btn_refresh_panel")
        sizePolicy.setHeightForWidth(self.btn_refresh_panel.sizePolicy().hasHeightForWidth())
        self.btn_refresh_panel.setSizePolicy(sizePolicy)
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

        self.horizontalLayout_3.addWidget(self.btn_refresh_panel)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, -1, 8, 8)
        self.btn_add_customer = QPushButton(Temp_Select_Customers)
        self.btn_add_customer.setObjectName(u"btn_add_customer")
        self.btn_add_customer.setMinimumSize(QSize(120, 40))
        self.btn_add_customer.setMaximumSize(QSize(120, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Black"])
        font1.setPointSize(11)
        self.btn_add_customer.setFont(font1)
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
        icon1 = QIcon()
        icon1.addFile(u":/resources/resources/icons/sys_user_cheerful.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_add_customer.setIcon(icon1)
        self.btn_add_customer.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.btn_add_customer)

        self.horizontalSpacer = QSpacerItem(250, 48, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.groupbox_search = QGroupBox(Temp_Select_Customers)
        self.groupbox_search.setObjectName(u"groupbox_search")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupbox_search.sizePolicy().hasHeightForWidth())
        self.groupbox_search.setSizePolicy(sizePolicy2)
        self.groupbox_search.setMinimumSize(QSize(290, 60))
        self.groupbox_search.setMaximumSize(QSize(300, 60))
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
        sizePolicy2.setHeightForWidth(self.linedit_search.sizePolicy().hasHeightForWidth())
        self.linedit_search.setSizePolicy(sizePolicy2)
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


        self.horizontalLayout_2.addWidget(self.groupbox_search)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.frame_container_selector = QFrame(Temp_Select_Customers)
        self.frame_container_selector.setObjectName(u"frame_container_selector")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_container_selector.sizePolicy().hasHeightForWidth())
        self.frame_container_selector.setSizePolicy(sizePolicy3)
        self.frame_container_selector.setMinimumSize(QSize(670, 411))
        self.frame_container_selector.setMaximumSize(QSize(670, 411))
        self.frame_container_selector.setStyleSheet(u"")
        self.frame_container_selector.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_container_selector.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_container_selector)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 10)
        self.qtable_customers = QTableWidget(self.frame_container_selector)
        if (self.qtable_customers.columnCount() < 5):
            self.qtable_customers.setColumnCount(5)
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Black"])
        font4.setPointSize(10)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font4);
        self.qtable_customers.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font4);
        self.qtable_customers.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font4);
        self.qtable_customers.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font4);
        self.qtable_customers.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font3);
        self.qtable_customers.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.qtable_customers.setObjectName(u"qtable_customers")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.qtable_customers.sizePolicy().hasHeightForWidth())
        self.qtable_customers.setSizePolicy(sizePolicy4)
        self.qtable_customers.setMinimumSize(QSize(0, 310))
        font5 = QFont()
        font5.setPointSize(10)
        self.qtable_customers.setFont(font5)
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
        self.qtable_customers.setColumnCount(5)
        self.qtable_customers.horizontalHeader().setCascadingSectionResizes(True)
        self.qtable_customers.horizontalHeader().setMinimumSectionSize(80)
        self.qtable_customers.horizontalHeader().setDefaultSectionSize(107)
        self.qtable_customers.horizontalHeader().setHighlightSections(True)
        self.qtable_customers.horizontalHeader().setStretchLastSection(False)
        self.qtable_customers.verticalHeader().setVisible(False)
        self.qtable_customers.verticalHeader().setCascadingSectionResizes(False)
        self.qtable_customers.verticalHeader().setMinimumSectionSize(35)
        self.qtable_customers.verticalHeader().setDefaultSectionSize(35)

        self.gridLayout.addWidget(self.qtable_customers, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, -1, 2, -1)
        self.groupBox_action = QGroupBox(self.frame_container_selector)
        self.groupBox_action.setObjectName(u"groupBox_action")
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
        self.label_select.setMinimumSize(QSize(180, 40))
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
        self.btn_ok_select.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        font7 = QFont()
        font7.setFamilies([u"Segoe UI Black"])
        font7.setPointSize(11)
        font7.setBold(True)
        font7.setItalic(False)
        font7.setUnderline(False)
        self.btn_cancel_select.setFont(font7)
        self.btn_cancel_select.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
"\n"
"QPushButton:disabled {\n"
"color: #d5d5d5;\n"
"background-color: #6a6a6a;\n"
"border: 1px solid  #00aa00;\n"
"}")

        self.horizontalLayout_4.addWidget(self.btn_cancel_select)


        self.horizontalLayout.addWidget(self.groupBox_action)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_container_selector, 2, 0, 1, 1)


        self.retranslateUi(Temp_Select_Customers)

        QMetaObject.connectSlotsByName(Temp_Select_Customers)
    # setupUi

    def retranslateUi(self, Temp_Select_Customers):
        Temp_Select_Customers.setWindowTitle(QCoreApplication.translate("Temp_Select_Customers", u"Dialog", None))
        self.label_headboard.setText(QCoreApplication.translate("Temp_Select_Customers", u"Buscar Cliente", None))
        self.btn_refresh_panel.setText("")
        self.btn_add_customer.setText(QCoreApplication.translate("Temp_Select_Customers", u" Cliente", None))
        self.groupbox_search.setTitle(QCoreApplication.translate("Temp_Select_Customers", u"Busqueda Rapida", None))
#if QT_CONFIG(tooltip)
        self.linedit_search.setToolTip(QCoreApplication.translate("Temp_Select_Customers", u"Introduce minimo 2 letras.", None))
#endif // QT_CONFIG(tooltip)
        self.linedit_search.setText("")
        self.btn_search.setText(QCoreApplication.translate("Temp_Select_Customers", u"Consultar", None))
        ___qtablewidgetitem = self.qtable_customers.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Temp_Select_Customers", u"ID", None));
        ___qtablewidgetitem1 = self.qtable_customers.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Temp_Select_Customers", u"Nombre / Razon Social", None));
        ___qtablewidgetitem2 = self.qtable_customers.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Temp_Select_Customers", u"C.I / RUC", None));
        ___qtablewidgetitem3 = self.qtable_customers.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Temp_Select_Customers", u"Telefono", None));
        ___qtablewidgetitem4 = self.qtable_customers.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Temp_Select_Customers", u"Email", None));
        self.groupBox_action.setTitle(QCoreApplication.translate("Temp_Select_Customers", u"Acci\u00f3n", None))
        self.label_select.setText(QCoreApplication.translate("Temp_Select_Customers", u"Ning\u00fan cliente seleccionado", None))
#if QT_CONFIG(tooltip)
        self.btn_ok_select.setToolTip(QCoreApplication.translate("Temp_Select_Customers", u"Aceptar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_ok_select.setText(QCoreApplication.translate("Temp_Select_Customers", u"\u2714 Seleccionar", None))
#if QT_CONFIG(tooltip)
        self.btn_cancel_select.setToolTip(QCoreApplication.translate("Temp_Select_Customers", u"Cancelar la operacion", None))
#endif // QT_CONFIG(tooltip)
        self.btn_cancel_select.setText(QCoreApplication.translate("Temp_Select_Customers", u"\u2715 Cancelar", None))
    # retranslateUi

