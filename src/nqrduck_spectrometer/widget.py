# Form implementation generated from reading ui file '../Modules/nqrduck-spectrometer/src/nqrduck_spectrometer/resources/spectrometer_widget.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1920, 1080)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stackedWidgetSettings = QtWidgets.QStackedWidget(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidgetSettings.sizePolicy().hasHeightForWidth())
        self.stackedWidgetSettings.setSizePolicy(sizePolicy)
        self.stackedWidgetSettings.setAutoFillBackground(True)
        self.stackedWidgetSettings.setObjectName("stackedWidgetSettings")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.stackedWidgetSettings.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.stackedWidgetSettings.addWidget(self.page_4)
        self.horizontalLayout.addWidget(self.stackedWidgetSettings)
        self.stackedWidgetPulseProgrammer = QtWidgets.QStackedWidget(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidgetPulseProgrammer.sizePolicy().hasHeightForWidth())
        self.stackedWidgetPulseProgrammer.setSizePolicy(sizePolicy)
        self.stackedWidgetPulseProgrammer.setAutoFillBackground(True)
        self.stackedWidgetPulseProgrammer.setObjectName("stackedWidgetPulseProgrammer")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.stackedWidgetPulseProgrammer.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidgetPulseProgrammer.addWidget(self.page_2)
        self.horizontalLayout.addWidget(self.stackedWidgetPulseProgrammer)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
