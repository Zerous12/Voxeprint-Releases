from PySide6.QtCore import (QCoreApplication,QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont, QIcon, QCursor)
from PySide6.QtWidgets import (QFrame, QGridLayout, QGroupBox, QVBoxLayout ,QHBoxLayout,QWidget , 
                               QLabel, QPushButton, QSizePolicy, QSpacerItem, QLayout)



class Ui_Dialog_Preview_Pdf(object):
    def setupUi(self, Dialog_Preview_Pdf):
        if not Dialog_Preview_Pdf.objectName():
            Dialog_Preview_Pdf.setObjectName(u"Dialog_Preview_Pdf")
        Dialog_Preview_Pdf.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Preview_Pdf.setEnabled(True)
        Dialog_Preview_Pdf.resize(849, 685)
        Dialog_Preview_Pdf.setMinimumSize(QSize(849, 685))
        Dialog_Preview_Pdf.setStyleSheet(u"QDialog#Dialog_Preview_Pdf {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 86, 115, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}")
        Dialog_Preview_Pdf.setModal(True)
        self.frame_view = QFrame(Dialog_Preview_Pdf)
        self.frame_view.setObjectName(u"frame_view")
        self.frame_view.setGeometry(QRect(-1, 66, 852, 621))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_view.sizePolicy().hasHeightForWidth())
        self.frame_view.setSizePolicy(sizePolicy)
        self.frame_view.setMinimumSize(QSize(852, 621))
        self.frame_view.setStyleSheet(u"")
        self.frame_view.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_view.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_view.setLineWidth(1)
        self.gridLayout = QGridLayout(self.frame_view)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.horizontalSpacer = QSpacerItem(40, 60, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.groupBox_action = QGroupBox(self.frame_view)
        self.groupBox_action.setObjectName(u"groupBox_action")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_action.sizePolicy().hasHeightForWidth())
        self.groupBox_action.setSizePolicy(sizePolicy1)
        self.groupBox_action.setMinimumSize(QSize(278, 78))
        self.groupBox_action.setMaximumSize(QSize(181, 16777215))
        font = QFont()
        font.setBold(False)
        self.groupBox_action.setFont(font)
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_action)
        self.horizontalLayout_4.setSpacing(10)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.btn_save_doc = QPushButton(self.groupBox_action)
        self.btn_save_doc.setObjectName(u"btn_save_doc")
        self.btn_save_doc.setMinimumSize(QSize(120, 40))
        self.btn_save_doc.setMaximumSize(QSize(120, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Black"])
        font1.setPointSize(11)
        self.btn_save_doc.setFont(font1)
        self.btn_save_doc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_doc.setStyleSheet(u"QPushButton {\n"
"color: #e6fdff;\n"
"border: 1px solid #bcbcbc  ;\n"
"border-radius: 5px; \n"
"background-color:  #6cb86c;\n"
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

        self.horizontalLayout_4.addWidget(self.btn_save_doc)

        self.btn_out_viewer = QPushButton(self.groupBox_action)
        self.btn_out_viewer.setObjectName(u"btn_out_viewer")
        self.btn_out_viewer.setMinimumSize(QSize(120, 40))
        self.btn_out_viewer.setMaximumSize(QSize(120, 41))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI Black"])
        font2.setPointSize(11)
        font2.setBold(True)
        font2.setItalic(False)
        font2.setUnderline(False)
        self.btn_out_viewer.setFont(font2)
        self.btn_out_viewer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_out_viewer.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_4.addWidget(self.btn_out_viewer)


        self.horizontalLayout_2.addWidget(self.groupBox_action)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.groupbox_preview = QGroupBox(self.frame_view)
        self.groupbox_preview.setObjectName(u"groupbox_preview")
        self.groupbox_preview.setEnabled(True)
        sizePolicy.setHeightForWidth(self.groupbox_preview.sizePolicy().hasHeightForWidth())
        self.groupbox_preview.setSizePolicy(sizePolicy)
        self.groupbox_preview.setMinimumSize(QSize(801, 500))
        self.groupbox_preview.setAutoFillBackground(False)
        self.groupbox_preview.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.gridLayout_3 = QGridLayout(self.groupbox_preview)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(5)
        self.gridLayout_3.setVerticalSpacing(15)
        self.gridLayout_3.setContentsMargins(5, 20, 5, 5)
        self.container_pdf_view = QWidget(self.groupbox_preview)
        self.container_pdf_view.setObjectName(u"container_pdf_view")
        sizePolicy.setHeightForWidth(self.container_pdf_view.sizePolicy().hasHeightForWidth())
        self.container_pdf_view.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.container_pdf_view, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupbox_preview, 0, 0, 1, 1)

        self.widget_headboard = QWidget(Dialog_Preview_Pdf)
        self.widget_headboard.setObjectName(u"widget_headboard")
        self.widget_headboard.setGeometry(QRect(11, 1, 300, 66))
        sizePolicy1.setHeightForWidth(self.widget_headboard.sizePolicy().hasHeightForWidth())
        self.widget_headboard.setSizePolicy(sizePolicy1)
        self.widget_headboard.setMinimumSize(QSize(300, 66))
        self.gridLayout_2 = QGridLayout(self.widget_headboard)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.print_pdf = QPushButton(self.widget_headboard)
        self.print_pdf.setObjectName(u"print_pdf")
        sizePolicy1.setHeightForWidth(self.print_pdf.sizePolicy().hasHeightForWidth())
        self.print_pdf.setSizePolicy(sizePolicy1)
        self.print_pdf.setMinimumSize(QSize(30, 30))
        self.print_pdf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.print_pdf.setStyleSheet(u"QPushButton {\n"
"color: #000000;\n"
"border: 1px solid transparent ;\n"
"border-radius: 5px; \n"
"background-color:  transparent;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #f6b565;\n"
"border: 1px solid #7f8c8d;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 2px solid transparent ;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/resources/resources/icons/sys_print_alt.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.print_pdf.setIcon(icon)
        self.print_pdf.setIconSize(QSize(26, 26))

        self.gridLayout_2.addWidget(self.print_pdf, 0, 4, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 0, 1, 1, 1)

        self.save_us_pdf = QPushButton(self.widget_headboard)
        self.save_us_pdf.setObjectName(u"save_us_pdf")
        sizePolicy1.setHeightForWidth(self.save_us_pdf.sizePolicy().hasHeightForWidth())
        self.save_us_pdf.setSizePolicy(sizePolicy1)
        self.save_us_pdf.setMinimumSize(QSize(30, 30))
        self.save_us_pdf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_us_pdf.setStyleSheet(u"QPushButton {\n"
"color: #000000;\n"
"border: 1px solid transparent ;\n"
"border-radius: 5px; \n"
"background-color:  transparent;\n"
"}\n"
"            \n"
"QPushButton:hover {\n"
"color: #ffffff;\n"
"background-color: #f6b565;\n"
"border: 1px solid #7f8c8d;\n"
"}\n"
"\n"
"QPushButton:pressed { \n"
"color: #ffffff;\n"
"background-color: #ffaa00;\n"
"border: 2px solid transparent ;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/resources/resources/icons/sys_file_download.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.save_us_pdf.setIcon(icon1)
        self.save_us_pdf.setIconSize(QSize(26, 26))

        self.gridLayout_2.addWidget(self.save_us_pdf, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(10, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 0, 3, 1, 1)

        self.label_headboard = QLabel(self.widget_headboard)
        self.label_headboard.setObjectName(u"label_headboard")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_headboard.sizePolicy().hasHeightForWidth())
        self.label_headboard.setSizePolicy(sizePolicy2)
        self.label_headboard.setMinimumSize(QSize(0, 55))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI Black"])
        font3.setPointSize(24)
        font3.setBold(True)
        self.label_headboard.setFont(font3)
        self.label_headboard.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.gridLayout_2.addWidget(self.label_headboard, 0, 0, 1, 1)

        self.label_quote_num = QLabel(Dialog_Preview_Pdf)
        self.label_quote_num.setObjectName(u"label_quote_num")
        self.label_quote_num.setGeometry(QRect(585, 5, 255, 55))
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_quote_num.sizePolicy().hasHeightForWidth())
        self.label_quote_num.setSizePolicy(sizePolicy3)
        self.label_quote_num.setMinimumSize(QSize(255, 55))
        self.label_quote_num.setMaximumSize(QSize(16777215, 55))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Black"])
        font4.setPointSize(20)
        self.label_quote_num.setFont(font4)
        self.label_quote_num.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.label_quote_num.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_quote_num.setScaledContents(True)

        self.retranslateUi(Dialog_Preview_Pdf)

        QMetaObject.connectSlotsByName(Dialog_Preview_Pdf)
    # setupUi

    def retranslateUi(self, Dialog_Preview_Pdf):
        Dialog_Preview_Pdf.setWindowTitle(QCoreApplication.translate("Dialog_Preview_Pdf", u"Dialog", None))
        self.groupBox_action.setTitle(QCoreApplication.translate("Dialog_Preview_Pdf", u"Acci\u00f3n", None))
#if QT_CONFIG(tooltip)
        self.btn_save_doc.setToolTip(QCoreApplication.translate("Dialog_Preview_Pdf", u"Guardar presupuesto", None))
#endif // QT_CONFIG(tooltip)
        self.btn_save_doc.setText(QCoreApplication.translate("Dialog_Preview_Pdf", u"Guardar", None))
#if QT_CONFIG(tooltip)
        self.btn_out_viewer.setToolTip(QCoreApplication.translate("Dialog_Preview_Pdf", u"Cancelar", None))
#endif // QT_CONFIG(tooltip)
        self.btn_out_viewer.setText(QCoreApplication.translate("Dialog_Preview_Pdf", u"Cancelar", None))
        self.groupbox_preview.setTitle(QCoreApplication.translate("Dialog_Preview_Pdf", u"Previsualizaci\u00f3n", None))
#if QT_CONFIG(tooltip)
        self.print_pdf.setToolTip(QCoreApplication.translate("Dialog_Preview_Pdf", u"Imprimir PDF", None))
#endif // QT_CONFIG(tooltip)
        self.print_pdf.setText("")
#if QT_CONFIG(tooltip)
        self.save_us_pdf.setToolTip(QCoreApplication.translate("Dialog_Preview_Pdf", u"Descargar PDF", None))
#endif // QT_CONFIG(tooltip)
        self.save_us_pdf.setText("")
        self.label_headboard.setText(QCoreApplication.translate("Dialog_Preview_Pdf", u"PDF Viewer  ", None))
        self.label_quote_num.setText("")
    # retranslateUi






