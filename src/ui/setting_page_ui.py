# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_page.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_SettingPage(object):
    def setupUi(self, SettingPage):
        if not SettingPage.objectName():
            SettingPage.setObjectName(u"SettingPage")
        SettingPage.resize(640, 480)
        self.verticalLayout = QVBoxLayout(SettingPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(SettingPage)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(16777215, 200))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.SerialPortScrollArea = QScrollArea(self.groupBox)
        self.SerialPortScrollArea.setObjectName(u"SerialPortScrollArea")
        self.SerialPortScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 247, 162))
        self.SerialPortScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.SerialPortScrollArea)

        self.widget = QWidget(self.groupBox)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.SerialRefreshButton = QPushButton(self.widget)
        self.SerialRefreshButton.setObjectName(u"SerialRefreshButton")

        self.verticalLayout_2.addWidget(self.SerialRefreshButton)

        self.SerialConnectButton = QPushButton(self.widget)
        self.SerialConnectButton.setObjectName(u"SerialConnectButton")

        self.verticalLayout_2.addWidget(self.SerialConnectButton)


        self.horizontalLayout.addWidget(self.widget)

        self.horizontalSpacer = QSpacerItem(245, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(SettingPage)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.pushButton_3 = QPushButton(self.groupBox_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(180, 80, 75, 24))

        self.verticalLayout.addWidget(self.groupBox_2)


        self.retranslateUi(SettingPage)

        QMetaObject.connectSlotsByName(SettingPage)
    # setupUi

    def retranslateUi(self, SettingPage):
        SettingPage.setWindowTitle(QCoreApplication.translate("SettingPage", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingPage", u"Serial Port", None))
        self.SerialRefreshButton.setText(QCoreApplication.translate("SettingPage", u"\uc0c8\ub85c\uace0\uce68", None))
        self.SerialConnectButton.setText(QCoreApplication.translate("SettingPage", u"\uc5f0\uacb0", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingPage", u"BT node", None))
        self.pushButton_3.setText(QCoreApplication.translate("SettingPage", u"PushButton", None))
    # retranslateUi

