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
    QPlainTextEdit, QPushButton, QSizePolicy, QSlider,
    QVBoxLayout, QWidget)
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
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QSize(0, 0))
        self.frame_2.setMaximumSize(QSize(16777215, 16777215))
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

        self.runTimeLabel = QLabel(self.frame_4)
        self.runTimeLabel.setObjectName(u"runTimeLabel")

        self.horizontalLayout_2.addWidget(self.runTimeLabel)


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

        self.roundLabel = QLabel(self.frame_5)
        self.roundLabel.setObjectName(u"roundLabel")

        self.horizontalLayout_3.addWidget(self.roundLabel)


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

        self.energyLabel = QLabel(self.frame_6)
        self.energyLabel.setObjectName(u"energyLabel")

        self.horizontalLayout_4.addWidget(self.energyLabel)


        self.verticalLayout_2.addWidget(self.frame_6)


        self.horizontalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(HomePage)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMinimumSize(QSize(0, 0))
        self.frame_3.setMaximumSize(QSize(16777215, 16777215))
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

        self.frame_8 = QFrame(self.frame_3)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_9 = QLabel(self.frame_8)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_7.addWidget(self.label_9)

        self.MainPowerButton = QPushButton(self.frame_8)
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

        self.horizontalLayout_7.addWidget(self.MainPowerButton)

        self.MainPowerIndicator = QLabel(self.frame_8)
        self.MainPowerIndicator.setObjectName(u"MainPowerIndicator")
        self.MainPowerIndicator.setMinimumSize(QSize(25, 25))
        self.MainPowerIndicator.setMaximumSize(QSize(25, 25))
        self.MainPowerIndicator.setPixmap(QPixmap(u":/font_awesome_solid/icons/user/status_led_y.png"))
        self.MainPowerIndicator.setScaledContents(True)

        self.horizontalLayout_7.addWidget(self.MainPowerIndicator)

        self.mainPowerCountDownLabel = QLabel(self.frame_8)
        self.mainPowerCountDownLabel.setObjectName(u"mainPowerCountDownLabel")
        self.mainPowerCountDownLabel.setMaximumSize(QSize(100, 16777215))
        self.mainPowerCountDownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_7.addWidget(self.mainPowerCountDownLabel)


        self.verticalLayout_3.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.frame_3)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_9)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget_2 = QWidget(self.frame_9)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_8 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(9, 0, 9, 0)
        self.motionCurrentTimeLabel = QLabel(self.widget_2)
        self.motionCurrentTimeLabel.setObjectName(u"motionCurrentTimeLabel")

        self.horizontalLayout_8.addWidget(self.motionCurrentTimeLabel)

        self.motionTimeHorizontalSlider = QSlider(self.widget_2)
        self.motionTimeHorizontalSlider.setObjectName(u"motionTimeHorizontalSlider")
        self.motionTimeHorizontalSlider.setMinimumSize(QSize(0, 0))
        self.motionTimeHorizontalSlider.setMaximumSize(QSize(300, 16777215))
        self.motionTimeHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_8.addWidget(self.motionTimeHorizontalSlider)

        self.motionEndTimeLabel = QLabel(self.widget_2)
        self.motionEndTimeLabel.setObjectName(u"motionEndTimeLabel")

        self.horizontalLayout_8.addWidget(self.motionEndTimeLabel)


        self.verticalLayout_4.addWidget(self.widget_2)

        self.widget_3 = QWidget(self.frame_9)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.playButton = QPushButton(self.widget_3)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setMinimumSize(QSize(0, 30))
        self.playButton.setMaximumSize(QSize(30, 30))
        icon2 = QIcon()
        icon2.addFile(u":/feather/icons/feather/play-circle.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.playButton.setIcon(icon2)

        self.horizontalLayout_9.addWidget(self.playButton)

        self.pauseButton = QPushButton(self.widget_3)
        self.pauseButton.setObjectName(u"pauseButton")
        self.pauseButton.setMinimumSize(QSize(0, 30))
        self.pauseButton.setMaximumSize(QSize(30, 30))
        icon3 = QIcon()
        icon3.addFile(u":/feather/icons/feather/pause-circle.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pauseButton.setIcon(icon3)

        self.horizontalLayout_9.addWidget(self.pauseButton)

        self.stopButton = QPushButton(self.widget_3)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setMinimumSize(QSize(0, 30))
        self.stopButton.setMaximumSize(QSize(30, 30))
        icon4 = QIcon()
        icon4.addFile(u":/feather/icons/feather/stop-circle.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.stopButton.setIcon(icon4)

        self.horizontalLayout_9.addWidget(self.stopButton)

        self.repeatButton = QPushButton(self.widget_3)
        self.repeatButton.setObjectName(u"repeatButton")
        self.repeatButton.setMinimumSize(QSize(0, 30))
        self.repeatButton.setMaximumSize(QSize(30, 30))
        icon5 = QIcon()
        icon5.addFile(u":/font_awesome_solid/icons/font_awesome/solid/rotate-off.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon5.addFile(u":/font_awesome_solid/icons/font_awesome/solid/rotate.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        icon5.addFile(u":/font_awesome_solid/icons/font_awesome/solid/rotate-off.png", QSize(), QIcon.Mode.Disabled, QIcon.State.Off)
        self.repeatButton.setIcon(icon5)
        self.repeatButton.setCheckable(True)

        self.horizontalLayout_9.addWidget(self.repeatButton)


        self.verticalLayout_4.addWidget(self.widget_3)


        self.verticalLayout_3.addWidget(self.frame_9)


        self.horizontalLayout.addWidget(self.frame_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.frame_7 = QFrame(HomePage)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy)
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_6.addWidget(self.frame_7)

        self.frame = QFrame(HomePage)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(16777215, 25))
        self.label_3.setFont(font)

        self.verticalLayout_5.addWidget(self.label_3)

        self.plainTextEdit = QPlainTextEdit(self.frame)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout_5.addWidget(self.plainTextEdit)


        self.horizontalLayout_6.addWidget(self.frame)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.retranslateUi(HomePage)

        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.label.setText(QCoreApplication.translate("HomePage", u"\ub3d9\uc791 \uc0c1\ud0dc", None))
        self.label_2.setText(QCoreApplication.translate("HomePage", u"\uc5f0\uc18d \uad6c\ub3d9 \uc2dc\uac04", None))
        self.runTimeLabel.setText(QCoreApplication.translate("HomePage", u"00h00m00s", None))
        self.label_4.setText(QCoreApplication.translate("HomePage", u"\ud68c\ucc28", None))
        self.roundLabel.setText(QCoreApplication.translate("HomePage", u"0/0", None))
        self.label_6.setText(QCoreApplication.translate("HomePage", u"\uc5d0\ub108\uc9c0", None))
        self.energyLabel.setText(QCoreApplication.translate("HomePage", u"000V / 000A / 000W", None))
        self.label_8.setText(QCoreApplication.translate("HomePage", u"\uc81c\uc5b4", None))
        self.pushButton.setText("")
        self.label_9.setText(QCoreApplication.translate("HomePage", u"\uba54\uc778 \uc804\uc6d0", None))
        self.MainPowerButton.setText("")
        self.MainPowerIndicator.setText("")
        self.mainPowerCountDownLabel.setText("")
        self.motionCurrentTimeLabel.setText(QCoreApplication.translate("HomePage", u"00:00:00", None))
        self.motionEndTimeLabel.setText(QCoreApplication.translate("HomePage", u"00:00:00", None))
        self.playButton.setText("")
        self.pauseButton.setText("")
        self.stopButton.setText("")
        self.repeatButton.setText("")
        self.label_3.setText(QCoreApplication.translate("HomePage", u"\ud130\ubbf8\ub110", None))
    # retranslateUi

