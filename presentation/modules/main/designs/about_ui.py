from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont, QPixmap, QCursor)
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QLayout, QPushButton, QSizePolicy, 
                               QSpacerItem, QVBoxLayout, QWidget)
from PySide6.QtGui import (QIcon)

class Ui_Dialog_About(object):
    def setupUi(self, Dialog_About):
        if not Dialog_About.objectName():
            Dialog_About.setObjectName(u"Dialog_About")
        Dialog_About.resize(585, 613)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog_About.sizePolicy().hasHeightForWidth())
        Dialog_About.setSizePolicy(sizePolicy)
        Dialog_About.setMinimumSize(QSize(585, 613))
        Dialog_About.setMaximumSize(QSize(585, 613))
        Dialog_About.setStyleSheet(u"QDialog#Dialog_About {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 86, 115, 255), stop:1 rgba(90, 90, 90, 255));\n"
"}\n"
"\n"
"QFrame #top_logo {\n"
"	background-color:  transparent;\n"
"}\n"
"\n"
"QFrame #frame_credits {\n"
"		Border: none;\n"
"		background-color:  #5a5a5a;\n"
"}\n"
"\n"
"QLabel { \n"
"	color: #ffffff;\n"
"	background-color: transparent;\n"
"}")
        self.frame_credits = QFrame(Dialog_About)
        self.frame_credits.setObjectName(u"frame_credits")
        self.frame_credits.setEnabled(True)
        self.frame_credits.setGeometry(QRect(-1, 117, 587, 451))
        sizePolicy.setHeightForWidth(self.frame_credits.sizePolicy().hasHeightForWidth())
        self.frame_credits.setSizePolicy(sizePolicy)
        self.frame_credits.setStyleSheet(u"")
        self.frame_credits.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_credits.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_credits.setLineWidth(1)
        self.gridLayout = QGridLayout(self.frame_credits)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(338, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.label_license = QLabel(self.frame_credits)
        self.label_license.setObjectName(u"label_license")
        sizePolicy.setHeightForWidth(self.label_license.sizePolicy().hasHeightForWidth())
        self.label_license.setSizePolicy(sizePolicy)
        self.label_license.setMinimumSize(QSize(60, 25))
        self.label_license.setStyleSheet(u"")
        self.label_license.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_license)

        self.label_worklog = QLabel(self.frame_credits)
        self.label_worklog.setObjectName(u"label_worklog")
        sizePolicy.setHeightForWidth(self.label_worklog.sizePolicy().hasHeightForWidth())
        self.label_worklog.setSizePolicy(sizePolicy)
        self.label_worklog.setMinimumSize(QSize(125, 25))
        self.label_worklog.setStyleSheet(u"")
        self.label_worklog.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_worklog)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.line_separator_2 = QFrame(self.frame_credits)
        self.line_separator_2.setObjectName(u"line_separator_2")
        self.line_separator_2.setMinimumSize(QSize(587, 2))
        self.line_separator_2.setMaximumSize(QSize(587, 2))
        self.line_separator_2.setStyleSheet(u"background-color: #ff8041;")
        self.line_separator_2.setFrameShape(QFrame.Shape.HLine)
        self.line_separator_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_separator_2, 2, 0, 1, 1)

        self.scroll_widget = QWidget(self.frame_credits)
        self.scroll_widget.setObjectName(u"scroll_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scroll_widget.sizePolicy().hasHeightForWidth())
        self.scroll_widget.setSizePolicy(sizePolicy1)
        self.scroll_widget.setMinimumSize(QSize(585, 420))
        self.scroll_widget.setMaximumSize(QSize(585, 420))
        self.scroll_widget.setStyleSheet(u"")

        self.gridLayout.addWidget(self.scroll_widget, 0, 0, 1, 1)

        self.line_separator = QFrame(Dialog_About)
        self.line_separator.setObjectName(u"line_separator")
        self.line_separator.setGeometry(QRect(0, 55, 587, 2))
        self.line_separator.setMinimumSize(QSize(0, 2))
        self.line_separator.setMaximumSize(QSize(16777215, 2))
        self.line_separator.setStyleSheet(u"background-color: #ff8041;")
        self.line_separator.setFrameShape(QFrame.Shape.HLine)
        self.line_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layoutWidget = QWidget(Dialog_About)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(1, 1, 581, 54))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 0, 8, 0)
        self.top_logo = QFrame(self.layoutWidget)
        self.top_logo.setObjectName(u"top_logo")
        self.top_logo.setMinimumSize(QSize(50, 50))
        self.top_logo.setMaximumSize(QSize(50, 50))
#if QT_CONFIG(accessibility)
        self.top_logo.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.top_logo.setStyleSheet(u"")
        self.top_logo.setFrameShape(QFrame.Shape.NoFrame)
        self.top_logo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.top_logo)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_logo_app = QLabel(self.top_logo)
        self.label_logo_app.setObjectName(u"label_logo_app")
        sizePolicy1.setHeightForWidth(self.label_logo_app.sizePolicy().hasHeightForWidth())
        self.label_logo_app.setSizePolicy(sizePolicy1)
        self.label_logo_app.setStyleSheet(u"image: url(:/resources/resources/images/voxeprint_mini.png);")
        self.label_logo_app.setPixmap(QPixmap(u":/images/images/images/Refri.png"))
        self.label_logo_app.setScaledContents(True)

        self.gridLayout_2.addWidget(self.label_logo_app, 0, 0, 1, 1)


        self.horizontalLayout.addWidget(self.top_logo)

        self.label_title_app = QLabel(self.layoutWidget)
        self.label_title_app.setObjectName(u"label_title_app")
        self.label_title_app.setMinimumSize(QSize(140, 50))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label_title_app.setFont(font)
#if QT_CONFIG(accessibility)
        self.label_title_app.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.label_title_app.setStyleSheet(u"")
        self.label_title_app.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_title_app)

        self.horizontalSpacer = QSpacerItem(100, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_version_build = QLabel(self.layoutWidget)
        self.label_version_build.setObjectName(u"label_version_build")
        self.label_version_build.setMinimumSize(QSize(135, 25))
        self.label_version_build.setMaximumSize(QSize(16777215, 25))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.label_version_build.setFont(font1)
        self.label_version_build.setStyleSheet(u"")
        self.label_version_build.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.label_version_build)

        self.label_bit_date = QLabel(self.layoutWidget)
        self.label_bit_date.setObjectName(u"label_bit_date")
        self.label_bit_date.setMinimumSize(QSize(135, 25))
        self.label_bit_date.setMaximumSize(QSize(135, 25))
        font2 = QFont()
        font2.setPointSize(10)
        self.label_bit_date.setFont(font2)
        self.label_bit_date.setStyleSheet(u"")
        self.label_bit_date.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.label_bit_date)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.btn_close_about = QPushButton(Dialog_About)
        self.btn_close_about.setObjectName(u"btn_close_about")
        self.btn_close_about.setGeometry(QRect(474, 575, 100, 30))
        self.btn_search_updates = QPushButton(Dialog_About)
        self.btn_search_updates.setObjectName(u"btn_search_updates")
        self.btn_search_updates.setGeometry(QRect(12, 575, 160, 30))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_search_updates.sizePolicy().hasHeightForWidth())
        self.btn_search_updates.setSizePolicy(sizePolicy2)
        self.btn_search_updates.setMinimumSize(QSize(160, 30))
        self.btn_search_updates.setMaximumSize(QSize(165, 30))
        icon = QIcon()
        icon.addFile(u":/resources/resources/icons/sys_refresh_alt_fat.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_search_updates.setIcon(icon)
        self.layoutWidget1 = QWidget(Dialog_About)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 58, 571, 63))
        self.horizontalLayout_4 = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.gridLayout_3.setVerticalSpacing(0)
        self.label_autor = QLabel(self.layoutWidget1)
        self.label_autor.setObjectName(u"label_autor")
        sizePolicy.setHeightForWidth(self.label_autor.sizePolicy().hasHeightForWidth())
        self.label_autor.setSizePolicy(sizePolicy)
        self.label_autor.setMinimumSize(QSize(65, 25))
        self.label_autor.setMaximumSize(QSize(16777215, 25))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        font3.setBold(True)
        self.label_autor.setFont(font3)
        self.label_autor.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.label_autor, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_autor_name = QLabel(self.layoutWidget1)
        self.label_autor_name.setObjectName(u"label_autor_name")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_autor_name.sizePolicy().hasHeightForWidth())
        self.label_autor_name.setSizePolicy(sizePolicy3)
        self.label_autor_name.setMaximumSize(QSize(16777215, 25))
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(True)
        self.label_autor_name.setFont(font4)
        self.label_autor_name.setStyleSheet(u"")

        self.horizontalLayout_2.addWidget(self.label_autor_name)

        self.btn_github = QPushButton(self.layoutWidget1)
        self.btn_github.setObjectName(u"btn_github")
        sizePolicy.setHeightForWidth(self.btn_github.sizePolicy().hasHeightForWidth())
        self.btn_github.setSizePolicy(sizePolicy)
        self.btn_github.setMinimumSize(QSize(24, 24))
        self.btn_github.setMaximumSize(QSize(24, 24))
        self.btn_github.setFont(font2)
        self.btn_github.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_2.addWidget(self.btn_github)

        self.horizontalSpacer_4 = QSpacerItem(5, 25, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)

        self.label_contact = QLabel(self.layoutWidget1)
        self.label_contact.setObjectName(u"label_contact")
        sizePolicy.setHeightForWidth(self.label_contact.sizePolicy().hasHeightForWidth())
        self.label_contact.setSizePolicy(sizePolicy)
        self.label_contact.setMinimumSize(QSize(65, 25))
        self.label_contact.setMaximumSize(QSize(75, 25))
        self.label_contact.setFont(font3)
        self.label_contact.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.label_contact, 1, 0, 1, 1)

        self.label_autor_mail = QLabel(self.layoutWidget1)
        self.label_autor_mail.setObjectName(u"label_autor_mail")
        sizePolicy.setHeightForWidth(self.label_autor_mail.sizePolicy().hasHeightForWidth())
        self.label_autor_mail.setSizePolicy(sizePolicy)
        self.label_autor_mail.setMinimumSize(QSize(210, 25))
        self.label_autor_mail.setMaximumSize(QSize(16777215, 25))
        self.label_autor_mail.setFont(font4)
        self.label_autor_mail.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.label_autor_mail, 1, 1, 1, 1)


        self.horizontalLayout_4.addLayout(self.gridLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(270, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.retranslateUi(Dialog_About)

        QMetaObject.connectSlotsByName(Dialog_About)
    # setupUi

    def retranslateUi(self, Dialog_About):
        Dialog_About.setWindowTitle(QCoreApplication.translate("Dialog_About", u"Dialog", None))
        self.label_license.setText(QCoreApplication.translate("Dialog_About", u"Licencia", None))
        self.label_worklog.setText(QCoreApplication.translate("Dialog_About", u"Registro de cambios", None))
        self.label_logo_app.setText("")
        self.label_title_app.setText(QCoreApplication.translate("Dialog_About", u"VoxePrint", None))
        self.label_version_build.setText(QCoreApplication.translate("Dialog_About", u"v1.00, build 2390", None))
        self.label_bit_date.setText(QCoreApplication.translate("Dialog_About", u"64-bit (10.10.2025)", None))
        self.btn_close_about.setText(QCoreApplication.translate("Dialog_About", u"Cerrar", None))
        self.btn_search_updates.setText(QCoreApplication.translate("Dialog_About", u" Buscar actualizaciones", None))
        self.label_autor.setText(QCoreApplication.translate("Dialog_About", u"Autor:", None))
        self.label_autor_name.setText(QCoreApplication.translate("Dialog_About", u"Autor-Name", None))
        self.btn_github.setText("")
        self.label_contact.setText(QCoreApplication.translate("Dialog_About", u"Contacto:", None))
        self.label_autor_mail.setText(QCoreApplication.translate("Dialog_About", u"Mail-Contact", None))
    # retranslateUi


