# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'help_page.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_HelpPage(object):
    def setupUi(self, HelpPage):
        if not HelpPage.objectName():
            HelpPage.setObjectName(u"HelpPage")
        HelpPage.resize(640, 480)
        self.verticalLayout = QVBoxLayout(HelpPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(HelpPage)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.versionLabel = QLabel(self.frame)
        self.versionLabel.setObjectName(u"versionLabel")

        self.verticalLayout_2.addWidget(self.versionLabel)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(HelpPage)

        QMetaObject.connectSlotsByName(HelpPage)
    # setupUi

    def retranslateUi(self, HelpPage):
        HelpPage.setWindowTitle(QCoreApplication.translate("HelpPage", u"Form", None))
        self.versionLabel.setText(QCoreApplication.translate("HelpPage", u"Version : 0.0.0", None))
    # retranslateUi

