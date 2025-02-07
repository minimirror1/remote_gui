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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget)
import _icons_rc

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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 391, 162))
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

        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(100, 0))
        self.frame.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 20))
        self.label.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_3.addWidget(self.label)

        self.sync_ms_spinBox = QSpinBox(self.frame)
        self.sync_ms_spinBox.setObjectName(u"sync_ms_spinBox")
        self.sync_ms_spinBox.setMinimum(200)
        self.sync_ms_spinBox.setMaximum(5000)
        self.sync_ms_spinBox.setSingleStep(50)

        self.verticalLayout_3.addWidget(self.sync_ms_spinBox)

        self.sync_enable = QPushButton(self.frame)
        self.sync_enable.setObjectName(u"sync_enable")
        self.sync_enable.setMinimumSize(QSize(75, 21))
        self.sync_enable.setMaximumSize(QSize(75, 21))
        icon = QIcon()
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Disabled, QIcon.State.Off)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Disabled, QIcon.State.On)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Active, QIcon.State.Off)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Active, QIcon.State.On)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Selected, QIcon.State.Off)
        icon.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.sync_enable.setIcon(icon)
        self.sync_enable.setIconSize(QSize(75, 75))
        self.sync_enable.setCheckable(True)
        self.sync_enable.setChecked(False)
        self.sync_enable.setAutoRepeat(False)

        self.verticalLayout_3.addWidget(self.sync_enable)


        self.horizontalLayout.addWidget(self.frame)


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
        self.label.setText(QCoreApplication.translate("SettingPage", u"sync \uc8fc\uae30 (ms)", None))
        self.sync_enable.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingPage", u"GroupBox", None))
        self.pushButton_3.setText(QCoreApplication.translate("SettingPage", u"PushButton", None))
    # retranslateUi

