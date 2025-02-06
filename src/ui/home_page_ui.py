# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_page.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
import _icons_rc

class Ui_HomePage(object):
    def setupUi(self, HomePage):
        if not HomePage.objectName():
            HomePage.setObjectName(u"HomePage")
        HomePage.resize(859, 669)
        self.verticalLayout = QVBoxLayout(HomePage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_2 = QFrame(HomePage)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 25))
        font = QFont()
        font.setFamilies([u"\ub098\ub214\uace0\ub515"])
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout_2.addWidget(self.label)

        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.label_3 = QLabel(self.frame_4)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)


        self.verticalLayout_2.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.frame_5)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)


        self.verticalLayout_2.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_2)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(self.frame_6)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.label_7 = QLabel(self.frame_6)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_4.addWidget(self.label_7)


        self.verticalLayout_2.addWidget(self.frame_6)


        self.horizontalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(HomePage)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget = QWidget(self.frame_3)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(16777215, 25))
        self.horizontalLayout_5 = QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMaximumSize(QSize(16777215, 25))
        self.label_8.setFont(font)

        self.horizontalLayout_5.addWidget(self.label_8)

        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMaximumSize(QSize(50, 16777215))
        icon = QIcon()
        icon.addFile(u":/material_design/icons/material_design/auto_fix_off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_high.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_off.png", QSize(), QIcon.Mode.Disabled, QIcon.State.Off)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_high.png", QSize(), QIcon.Mode.Disabled, QIcon.State.On)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_off.png", QSize(), QIcon.Mode.Active, QIcon.State.Off)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_high.png", QSize(), QIcon.Mode.Active, QIcon.State.On)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_off.png", QSize(), QIcon.Mode.Selected, QIcon.State.Off)
        icon.addFile(u":/material_design/icons/material_design/auto_fix_high.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.pushButton.setIcon(icon)
        self.pushButton.setCheckable(True)

        self.horizontalLayout_5.addWidget(self.pushButton)


        self.verticalLayout_3.addWidget(self.widget)

        self.frame_7 = QFrame(self.frame_3)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_9 = QLabel(self.frame_7)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_6.addWidget(self.label_9)

        self.MainPowerButton = QPushButton(self.frame_7)
        self.MainPowerButton.setObjectName(u"MainPowerButton")
        self.MainPowerButton.setMinimumSize(QSize(75, 21))
        self.MainPowerButton.setMaximumSize(QSize(75, 21))
        icon1 = QIcon()
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Disabled, QIcon.State.Off)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Disabled, QIcon.State.On)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Active, QIcon.State.Off)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Active, QIcon.State.On)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_Off.png", QSize(), QIcon.Mode.Selected, QIcon.State.Off)
        icon1.addFile(u":/font_awesome_solid/icons/user/Checkbox_On.png", QSize(), QIcon.Mode.Selected, QIcon.State.On)
        self.MainPowerButton.setIcon(icon1)
        self.MainPowerButton.setIconSize(QSize(75, 75))
        self.MainPowerButton.setCheckable(True)
        self.MainPowerButton.setChecked(False)
        self.MainPowerButton.setAutoRepeat(False)

        self.horizontalLayout_6.addWidget(self.MainPowerButton)

        self.MainPowerIndicator = QLabel(self.frame_7)
        self.MainPowerIndicator.setObjectName(u"MainPowerIndicator")
        self.MainPowerIndicator.setMinimumSize(QSize(25, 25))
        self.MainPowerIndicator.setMaximumSize(QSize(25, 25))
        self.MainPowerIndicator.setPixmap(QPixmap(u":/font_awesome_solid/icons/user/status_led_y.png"))
        self.MainPowerIndicator.setScaledContents(True)

        self.horizontalLayout_6.addWidget(self.MainPowerIndicator)


        self.verticalLayout_3.addWidget(self.frame_7)


        self.horizontalLayout.addWidget(self.frame_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.frame = QFrame(HomePage)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(HomePage)

        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.label.setText(QCoreApplication.translate("HomePage", u"\ub3d9\uc791 \uc0c1\ud0dc", None))
        self.label_2.setText(QCoreApplication.translate("HomePage", u"\uc5f0\uc18d \uad6c\ub3d9 \uc2dc\uac04", None))
        self.label_3.setText(QCoreApplication.translate("HomePage", u"00h00m00s", None))
        self.label_4.setText(QCoreApplication.translate("HomePage", u"\ud68c\ucc28", None))
        self.label_5.setText(QCoreApplication.translate("HomePage", u"0/0", None))
        self.label_6.setText(QCoreApplication.translate("HomePage", u"\uc5d0\ub108\uc9c0", None))
        self.label_7.setText(QCoreApplication.translate("HomePage", u"000V / 000A / 000W", None))
        self.label_8.setText(QCoreApplication.translate("HomePage", u"\uc81c\uc5b4", None))
        self.pushButton.setText("")
        self.label_9.setText(QCoreApplication.translate("HomePage", u"\uba54\uc778 \uc804\uc6d0", None))
        self.MainPowerButton.setText("")
        self.MainPowerIndicator.setText("")
    # retranslateUi

