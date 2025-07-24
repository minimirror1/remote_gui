# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTimeEdit, QVBoxLayout,
    QWidget)
import _icons_rc

class Ui_ConfigPage(object):
    def setupUi(self, ConfigPage):
        if not ConfigPage.objectName():
            ConfigPage.setObjectName(u"ConfigPage")
        ConfigPage.resize(800, 600)
        self.verticalLayout = QVBoxLayout(ConfigPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(ConfigPage)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 768, 653))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.basicInfoGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.basicInfoGroupBox.setObjectName(u"basicInfoGroupBox")
        font = QFont()
        font.setFamilies([u"\ub098\ub214\uace0\ub515"])
        font.setPointSize(12)
        font.setBold(True)
        self.basicInfoGroupBox.setFont(font)
        self.basicInfoFormLayout = QFormLayout(self.basicInfoGroupBox)
        self.basicInfoFormLayout.setObjectName(u"basicInfoFormLayout")
        self.countryLabel = QLabel(self.basicInfoGroupBox)
        self.countryLabel.setObjectName(u"countryLabel")

        self.basicInfoFormLayout.setWidget(0, QFormLayout.LabelRole, self.countryLabel)

        self.countryLineEdit = QLineEdit(self.basicInfoGroupBox)
        self.countryLineEdit.setObjectName(u"countryLineEdit")

        self.basicInfoFormLayout.setWidget(0, QFormLayout.FieldRole, self.countryLineEdit)

        self.regionLabel = QLabel(self.basicInfoGroupBox)
        self.regionLabel.setObjectName(u"regionLabel")

        self.basicInfoFormLayout.setWidget(1, QFormLayout.LabelRole, self.regionLabel)

        self.regionLineEdit = QLineEdit(self.basicInfoGroupBox)
        self.regionLineEdit.setObjectName(u"regionLineEdit")

        self.basicInfoFormLayout.setWidget(1, QFormLayout.FieldRole, self.regionLineEdit)

        self.storeNameLabel = QLabel(self.basicInfoGroupBox)
        self.storeNameLabel.setObjectName(u"storeNameLabel")

        self.basicInfoFormLayout.setWidget(2, QFormLayout.LabelRole, self.storeNameLabel)

        self.storeNameLineEdit = QLineEdit(self.basicInfoGroupBox)
        self.storeNameLineEdit.setObjectName(u"storeNameLineEdit")

        self.basicInfoFormLayout.setWidget(2, QFormLayout.FieldRole, self.storeNameLineEdit)


        self.verticalLayout_2.addWidget(self.basicInfoGroupBox)

        self.businessHoursGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.businessHoursGroupBox.setObjectName(u"businessHoursGroupBox")
        self.businessHoursGroupBox.setFont(font)
        self.businessHoursGridLayout = QGridLayout(self.businessHoursGroupBox)
        self.businessHoursGridLayout.setObjectName(u"businessHoursGridLayout")
        self.mondayLabel = QLabel(self.businessHoursGroupBox)
        self.mondayLabel.setObjectName(u"mondayLabel")

        self.businessHoursGridLayout.addWidget(self.mondayLabel, 0, 0, 1, 1)

        self.mondayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.mondayStartTimeEdit.setObjectName(u"mondayStartTimeEdit")
        self.mondayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.mondayStartTimeEdit, 0, 1, 1, 1)

        self.mondayToLabel = QLabel(self.businessHoursGroupBox)
        self.mondayToLabel.setObjectName(u"mondayToLabel")

        self.businessHoursGridLayout.addWidget(self.mondayToLabel, 0, 2, 1, 1)

        self.mondayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.mondayEndTimeEdit.setObjectName(u"mondayEndTimeEdit")
        self.mondayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.mondayEndTimeEdit, 0, 3, 1, 1)

        self.mondayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.mondayClosedCheckBox.setObjectName(u"mondayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.mondayClosedCheckBox, 0, 4, 1, 1)

        self.tuesdayLabel = QLabel(self.businessHoursGroupBox)
        self.tuesdayLabel.setObjectName(u"tuesdayLabel")

        self.businessHoursGridLayout.addWidget(self.tuesdayLabel, 1, 0, 1, 1)

        self.tuesdayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.tuesdayStartTimeEdit.setObjectName(u"tuesdayStartTimeEdit")
        self.tuesdayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.tuesdayStartTimeEdit, 1, 1, 1, 1)

        self.tuesdayToLabel = QLabel(self.businessHoursGroupBox)
        self.tuesdayToLabel.setObjectName(u"tuesdayToLabel")

        self.businessHoursGridLayout.addWidget(self.tuesdayToLabel, 1, 2, 1, 1)

        self.tuesdayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.tuesdayEndTimeEdit.setObjectName(u"tuesdayEndTimeEdit")
        self.tuesdayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.tuesdayEndTimeEdit, 1, 3, 1, 1)

        self.tuesdayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.tuesdayClosedCheckBox.setObjectName(u"tuesdayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.tuesdayClosedCheckBox, 1, 4, 1, 1)

        self.wednesdayLabel = QLabel(self.businessHoursGroupBox)
        self.wednesdayLabel.setObjectName(u"wednesdayLabel")

        self.businessHoursGridLayout.addWidget(self.wednesdayLabel, 2, 0, 1, 1)

        self.wednesdayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.wednesdayStartTimeEdit.setObjectName(u"wednesdayStartTimeEdit")
        self.wednesdayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.wednesdayStartTimeEdit, 2, 1, 1, 1)

        self.wednesdayToLabel = QLabel(self.businessHoursGroupBox)
        self.wednesdayToLabel.setObjectName(u"wednesdayToLabel")

        self.businessHoursGridLayout.addWidget(self.wednesdayToLabel, 2, 2, 1, 1)

        self.wednesdayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.wednesdayEndTimeEdit.setObjectName(u"wednesdayEndTimeEdit")
        self.wednesdayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.wednesdayEndTimeEdit, 2, 3, 1, 1)

        self.wednesdayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.wednesdayClosedCheckBox.setObjectName(u"wednesdayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.wednesdayClosedCheckBox, 2, 4, 1, 1)

        self.thursdayLabel = QLabel(self.businessHoursGroupBox)
        self.thursdayLabel.setObjectName(u"thursdayLabel")

        self.businessHoursGridLayout.addWidget(self.thursdayLabel, 3, 0, 1, 1)

        self.thursdayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.thursdayStartTimeEdit.setObjectName(u"thursdayStartTimeEdit")
        self.thursdayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.thursdayStartTimeEdit, 3, 1, 1, 1)

        self.thursdayToLabel = QLabel(self.businessHoursGroupBox)
        self.thursdayToLabel.setObjectName(u"thursdayToLabel")

        self.businessHoursGridLayout.addWidget(self.thursdayToLabel, 3, 2, 1, 1)

        self.thursdayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.thursdayEndTimeEdit.setObjectName(u"thursdayEndTimeEdit")
        self.thursdayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.thursdayEndTimeEdit, 3, 3, 1, 1)

        self.thursdayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.thursdayClosedCheckBox.setObjectName(u"thursdayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.thursdayClosedCheckBox, 3, 4, 1, 1)

        self.fridayLabel = QLabel(self.businessHoursGroupBox)
        self.fridayLabel.setObjectName(u"fridayLabel")

        self.businessHoursGridLayout.addWidget(self.fridayLabel, 4, 0, 1, 1)

        self.fridayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.fridayStartTimeEdit.setObjectName(u"fridayStartTimeEdit")
        self.fridayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.fridayStartTimeEdit, 4, 1, 1, 1)

        self.fridayToLabel = QLabel(self.businessHoursGroupBox)
        self.fridayToLabel.setObjectName(u"fridayToLabel")

        self.businessHoursGridLayout.addWidget(self.fridayToLabel, 4, 2, 1, 1)

        self.fridayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.fridayEndTimeEdit.setObjectName(u"fridayEndTimeEdit")
        self.fridayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.fridayEndTimeEdit, 4, 3, 1, 1)

        self.fridayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.fridayClosedCheckBox.setObjectName(u"fridayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.fridayClosedCheckBox, 4, 4, 1, 1)

        self.saturdayLabel = QLabel(self.businessHoursGroupBox)
        self.saturdayLabel.setObjectName(u"saturdayLabel")

        self.businessHoursGridLayout.addWidget(self.saturdayLabel, 5, 0, 1, 1)

        self.saturdayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.saturdayStartTimeEdit.setObjectName(u"saturdayStartTimeEdit")
        self.saturdayStartTimeEdit.setTime(QTime(10, 0, 0))

        self.businessHoursGridLayout.addWidget(self.saturdayStartTimeEdit, 5, 1, 1, 1)

        self.saturdayToLabel = QLabel(self.businessHoursGroupBox)
        self.saturdayToLabel.setObjectName(u"saturdayToLabel")

        self.businessHoursGridLayout.addWidget(self.saturdayToLabel, 5, 2, 1, 1)

        self.saturdayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.saturdayEndTimeEdit.setObjectName(u"saturdayEndTimeEdit")
        self.saturdayEndTimeEdit.setTime(QTime(16, 0, 0))

        self.businessHoursGridLayout.addWidget(self.saturdayEndTimeEdit, 5, 3, 1, 1)

        self.saturdayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.saturdayClosedCheckBox.setObjectName(u"saturdayClosedCheckBox")

        self.businessHoursGridLayout.addWidget(self.saturdayClosedCheckBox, 5, 4, 1, 1)

        self.sundayLabel = QLabel(self.businessHoursGroupBox)
        self.sundayLabel.setObjectName(u"sundayLabel")

        self.businessHoursGridLayout.addWidget(self.sundayLabel, 6, 0, 1, 1)

        self.sundayStartTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.sundayStartTimeEdit.setObjectName(u"sundayStartTimeEdit")
        self.sundayStartTimeEdit.setTime(QTime(9, 0, 0))

        self.businessHoursGridLayout.addWidget(self.sundayStartTimeEdit, 6, 1, 1, 1)

        self.sundayToLabel = QLabel(self.businessHoursGroupBox)
        self.sundayToLabel.setObjectName(u"sundayToLabel")

        self.businessHoursGridLayout.addWidget(self.sundayToLabel, 6, 2, 1, 1)

        self.sundayEndTimeEdit = QTimeEdit(self.businessHoursGroupBox)
        self.sundayEndTimeEdit.setObjectName(u"sundayEndTimeEdit")
        self.sundayEndTimeEdit.setTime(QTime(18, 0, 0))

        self.businessHoursGridLayout.addWidget(self.sundayEndTimeEdit, 6, 3, 1, 1)

        self.sundayClosedCheckBox = QCheckBox(self.businessHoursGroupBox)
        self.sundayClosedCheckBox.setObjectName(u"sundayClosedCheckBox")
        self.sundayClosedCheckBox.setChecked(True)

        self.businessHoursGridLayout.addWidget(self.sundayClosedCheckBox, 6, 4, 1, 1)


        self.verticalLayout_2.addWidget(self.businessHoursGroupBox)

        self.programSettingsGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.programSettingsGroupBox.setObjectName(u"programSettingsGroupBox")
        self.programSettingsGroupBox.setFont(font)
        self.programSettingsFormLayout = QFormLayout(self.programSettingsGroupBox)
        self.programSettingsFormLayout.setObjectName(u"programSettingsFormLayout")
        self.scheduleFunctionLabel = QLabel(self.programSettingsGroupBox)
        self.scheduleFunctionLabel.setObjectName(u"scheduleFunctionLabel")

        self.programSettingsFormLayout.setWidget(0, QFormLayout.LabelRole, self.scheduleFunctionLabel)

        self.scheduleFunctionCheckBox = QCheckBox(self.programSettingsGroupBox)
        self.scheduleFunctionCheckBox.setObjectName(u"scheduleFunctionCheckBox")
        self.scheduleFunctionCheckBox.setChecked(True)

        self.programSettingsFormLayout.setWidget(0, QFormLayout.FieldRole, self.scheduleFunctionCheckBox)

        self.syncTimeLabel = QLabel(self.programSettingsGroupBox)
        self.syncTimeLabel.setObjectName(u"syncTimeLabel")

        self.programSettingsFormLayout.setWidget(1, QFormLayout.LabelRole, self.syncTimeLabel)

        self.syncTimeDoubleSpinBox = QDoubleSpinBox(self.programSettingsGroupBox)
        self.syncTimeDoubleSpinBox.setObjectName(u"syncTimeDoubleSpinBox")
        self.syncTimeDoubleSpinBox.setMinimum(100.000000000000000)
        self.syncTimeDoubleSpinBox.setMaximum(10000.000000000000000)
        self.syncTimeDoubleSpinBox.setSingleStep(100.000000000000000)
        self.syncTimeDoubleSpinBox.setValue(1500.000000000000000)

        self.programSettingsFormLayout.setWidget(1, QFormLayout.FieldRole, self.syncTimeDoubleSpinBox)


        self.verticalLayout_2.addWidget(self.programSettingsGroupBox)

        self.logSettingsGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.logSettingsGroupBox.setObjectName(u"logSettingsGroupBox")
        self.logSettingsGroupBox.setFont(font)
        self.logSettingsFormLayout = QFormLayout(self.logSettingsGroupBox)
        self.logSettingsFormLayout.setObjectName(u"logSettingsFormLayout")
        self.enableLogFileLabel = QLabel(self.logSettingsGroupBox)
        self.enableLogFileLabel.setObjectName(u"enableLogFileLabel")

        self.logSettingsFormLayout.setWidget(0, QFormLayout.LabelRole, self.enableLogFileLabel)

        self.enableLogFileCheckBox = QCheckBox(self.logSettingsGroupBox)
        self.enableLogFileCheckBox.setObjectName(u"enableLogFileCheckBox")
        self.enableLogFileCheckBox.setChecked(True)

        self.logSettingsFormLayout.setWidget(0, QFormLayout.FieldRole, self.enableLogFileCheckBox)


        self.verticalLayout_2.addWidget(self.logSettingsGroupBox)

        self.configVersionGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.configVersionGroupBox.setObjectName(u"configVersionGroupBox")
        self.configVersionGroupBox.setFont(font)
        self.configVersionFormLayout = QFormLayout(self.configVersionGroupBox)
        self.configVersionFormLayout.setObjectName(u"configVersionFormLayout")
        self.configVersionLabel = QLabel(self.configVersionGroupBox)
        self.configVersionLabel.setObjectName(u"configVersionLabel")

        self.configVersionFormLayout.setWidget(0, QFormLayout.LabelRole, self.configVersionLabel)

        self.configVersionLineEdit = QLineEdit(self.configVersionGroupBox)
        self.configVersionLineEdit.setObjectName(u"configVersionLineEdit")
        self.configVersionLineEdit.setReadOnly(True)

        self.configVersionFormLayout.setWidget(0, QFormLayout.FieldRole, self.configVersionLineEdit)


        self.verticalLayout_2.addWidget(self.configVersionGroupBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.buttonFrame = QFrame(ConfigPage)
        self.buttonFrame.setObjectName(u"buttonFrame")
        self.buttonFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.buttonFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.buttonLayout = QHBoxLayout(self.buttonFrame)
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.loadButton = QPushButton(self.buttonFrame)
        self.loadButton.setObjectName(u"loadButton")
        self.loadButton.setMinimumSize(QSize(100, 30))
        icon = QIcon()
        icon.addFile(u":/feather/icons/feather/folder-open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.loadButton.setIcon(icon)

        self.buttonLayout.addWidget(self.loadButton)

        self.saveButton = QPushButton(self.buttonFrame)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMinimumSize(QSize(100, 30))
        icon1 = QIcon()
        icon1.addFile(u":/feather/icons/feather/save.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.saveButton.setIcon(icon1)

        self.buttonLayout.addWidget(self.saveButton)

        self.resetButton = QPushButton(self.buttonFrame)
        self.resetButton.setObjectName(u"resetButton")
        self.resetButton.setMinimumSize(QSize(100, 30))
        icon2 = QIcon()
        icon2.addFile(u":/feather/icons/feather/refresh-cw.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.resetButton.setIcon(icon2)

        self.buttonLayout.addWidget(self.resetButton)


        self.verticalLayout.addWidget(self.buttonFrame)


        self.retranslateUi(ConfigPage)

        QMetaObject.connectSlotsByName(ConfigPage)
    # setupUi

    def retranslateUi(self, ConfigPage):
        ConfigPage.setWindowTitle(QCoreApplication.translate("ConfigPage", u"Configuration", None))
        self.basicInfoGroupBox.setTitle(QCoreApplication.translate("ConfigPage", u"\uae30\ubcf8 \uc815\ubcf4", None))
        self.countryLabel.setText(QCoreApplication.translate("ConfigPage", u"\uad6d\uac00:", None))
        self.countryLineEdit.setText(QCoreApplication.translate("ConfigPage", u"\ub300\ud55c\ubbfc\uad6d", None))
        self.regionLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc9c0\uc5ed:", None))
        self.regionLineEdit.setText(QCoreApplication.translate("ConfigPage", u"\uc11c\uc6b8\ud2b9\ubcc4\uc2dc", None))
        self.storeNameLabel.setText(QCoreApplication.translate("ConfigPage", u"\ub9e4\uc7a5\uba85:", None))
        self.storeNameLineEdit.setText(QCoreApplication.translate("ConfigPage", u"\uc2dc\uc2a4\ud14c\ubbf9 \ubcf8\uc810", None))
        self.businessHoursGroupBox.setTitle(QCoreApplication.translate("ConfigPage", u"\uc601\uc5c5 \uc2dc\uac04", None))
        self.mondayLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc6d4\uc694\uc77c:", None))
        self.mondayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.mondayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.mondayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.mondayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.tuesdayLabel.setText(QCoreApplication.translate("ConfigPage", u"\ud654\uc694\uc77c:", None))
        self.tuesdayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.tuesdayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.tuesdayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.tuesdayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.wednesdayLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc218\uc694\uc77c:", None))
        self.wednesdayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.wednesdayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.wednesdayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.wednesdayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.thursdayLabel.setText(QCoreApplication.translate("ConfigPage", u"\ubaa9\uc694\uc77c:", None))
        self.thursdayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.thursdayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.thursdayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.thursdayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.fridayLabel.setText(QCoreApplication.translate("ConfigPage", u"\uae08\uc694\uc77c:", None))
        self.fridayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.fridayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.fridayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.fridayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.saturdayLabel.setText(QCoreApplication.translate("ConfigPage", u"\ud1a0\uc694\uc77c:", None))
        self.saturdayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.saturdayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.saturdayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.saturdayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.sundayLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc77c\uc694\uc77c:", None))
        self.sundayStartTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.sundayToLabel.setText(QCoreApplication.translate("ConfigPage", u" ~ ", None))
        self.sundayEndTimeEdit.setDisplayFormat(QCoreApplication.translate("ConfigPage", u"HH:mm", None))
        self.sundayClosedCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud734\ubb34", None))
        self.programSettingsGroupBox.setTitle(QCoreApplication.translate("ConfigPage", u"\ud504\ub85c\uadf8\ub7a8 \uc124\uc815", None))
        self.scheduleFunctionLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc2a4\ucf00\uc904 \uae30\ub2a5:", None))
        self.scheduleFunctionCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud65c\uc131\ud654", None))
        self.syncTimeLabel.setText(QCoreApplication.translate("ConfigPage", u"\ub3d9\uae30\ud654 \uc2dc\uac04 (ms):", None))
        self.logSettingsGroupBox.setTitle(QCoreApplication.translate("ConfigPage", u"\ub85c\uadf8 \uc124\uc815", None))
        self.enableLogFileLabel.setText(QCoreApplication.translate("ConfigPage", u"\ub85c\uadf8 \ud30c\uc77c \uc0dd\uc131:", None))
        self.enableLogFileCheckBox.setText(QCoreApplication.translate("ConfigPage", u"\ud65c\uc131\ud654", None))
        self.configVersionGroupBox.setTitle(QCoreApplication.translate("ConfigPage", u"\uc124\uc815 \ubc84\uc804", None))
        self.configVersionLabel.setText(QCoreApplication.translate("ConfigPage", u"\uc124\uc815 \ubc84\uc804:", None))
        self.configVersionLineEdit.setText(QCoreApplication.translate("ConfigPage", u"1.0.0", None))
        self.loadButton.setText(QCoreApplication.translate("ConfigPage", u"\ubd88\ub7ec\uc624\uae30", None))
        self.saveButton.setText(QCoreApplication.translate("ConfigPage", u"\uc800\uc7a5", None))
        self.resetButton.setText(QCoreApplication.translate("ConfigPage", u"\ucd08\uae30\ud654", None))
    # retranslateUi

