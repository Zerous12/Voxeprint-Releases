from PySide6.QtCore import (QCoreApplication, 
                            QMetaObject, QRect,QSize, Qt)
from PySide6.QtWidgets import (QLabel, QGridLayout, QProgressBar, 
                               QSizePolicy, QWidget)

class Ui_intro_panel(object):
    def setupUi(self, intro_panel):
        if not intro_panel.objectName():
            intro_panel.setObjectName(u"intro_panel")
        intro_panel.resize(486, 437)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(intro_panel.sizePolicy().hasHeightForWidth())
        intro_panel.setSizePolicy(sizePolicy)
        intro_panel.setMinimumSize(QSize(486, 437))
        intro_panel.setStyleSheet(u"QWidget #intro_panel{\n"
"background-color: #000000;\n"
"}\n"
"\n"
"")
        self.gridLayout = QGridLayout(intro_panel)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 9, 0)
        self.logo_bk = QWidget(intro_panel)
        self.logo_bk.setObjectName(u"logo_bk")
        self.logo_bk.setMaximumSize(QSize(16777215, 16777215))
        self.logo_bk.setStyleSheet(u"#logo_bk {image: url(:/resources/resources/images/voxeprint_logo.png);}\n"
"QLabel {\n"
"background-color: transparent;\n"
"border: none;\n"
"}")
        self.progress_bar = QProgressBar(self.logo_bk)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setGeometry(QRect(33, 320, 422, 20))
        self.progress_bar.setMinimumSize(QSize(422, 20))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.logo_loaded = QLabel(self.logo_bk)
        self.logo_loaded.setObjectName(u"logo_loaded")
        self.logo_loaded.setGeometry(QRect(33, 340, 421, 20))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.logo_loaded.sizePolicy().hasHeightForWidth())
        self.logo_loaded.setSizePolicy(sizePolicy1)
        self.logo_loaded.setMinimumSize(QSize(412, 20))
        self.logo_loaded.setStyleSheet(u"")
        self.logo_loaded.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.logo_bk, 0, 0, 1, 1)


        self.retranslateUi(intro_panel)

        QMetaObject.connectSlotsByName(intro_panel)
    # setupUi

    def retranslateUi(self, intro_panel):
        intro_panel.setWindowTitle(QCoreApplication.translate("intro_panel", u"Form", None))
        self.logo_loaded.setText("")
    # retranslateUi

