# -*- coding: utf-8 -*-
"""
    This file integrates all the code to control the UI interface.(this file is the startup file)
    class：
        MainWindow：The device information obtained by MDNS(mdns) is expressed in the interface window,
                    Parses the user's input(lan_ewlink_api and Dialog_text).
"""


import sys
import time
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from tool_01DIY85_ui import *
from mdns import mDNS_BrowserThread, MyListener
from lan_ewlink_api import *
from Dialog_text import RootDialog, SetTimeDialog, WIFIDialog, resultDialog


class MainWindow(QMainWindow):
    """ main window """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.myThread = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.result_ui = False
        self.thread_number = 0
        self.send_result = {}
        self.ID_list = []
        self.table_all_sub = []
        # All device information in the interface list
        self.UI_sub_info = {}
        self.sub_total = 0
        self.mDNS_info_sta = {}
        # The name of the device selected by the user
        self.select_name = []
        # One thread is dedicated to MDNS information
        self.BrowserThread = mDNS_BrowserThread(
            parent=None, func_task=self.mDNS_info_sta)
        # Sets the signal tube correlation function
        self.BrowserThread.get_sub_new.connect(self.thread_deal_mDNS_new)
        self.BrowserThread.start()
        # Draw table
        self.add_line_item()
        # Set the signal function triggered by the table
        self.ui.tableWidget.cellClicked.connect(self.table_check)
        self.show()
        self.setWindowTitle("DIY tool(v3.3.0)")
        self.ui.pB_ON.clicked.connect(self.set_ON)
        self.ui.pB_OFF.clicked.connect(self.set_OFF)
        self.ui.pB_UP_ON.clicked.connect(self.set_power_up_ON)
        self.ui.pB_UP_KEEP.clicked.connect(self.set_power_up_KEEP)
        self.ui.pB_UP_OFF.clicked.connect(self.set_power_up_OFF)
        self.ui.pB_SET_POINT.clicked.connect(self.set_POINT)
        self.ui.ROOT.clicked.connect(self.set_root)
        self.ui.MODIFY_SSID_PASSWORD.clicked.connect(self.set_wifi)
        self.ui.pB_all.clicked.connect(self.check_all)
        self.ui.pB_inverse.clicked.connect(self.check_not)
        self.ui.pB_cancel.clicked.connect(self.out_check)
        self.ui.pB_info.clicked.connect(self.get_info)
        self.ui.pB_signal.clicked.connect(self.get_signal)

    def closeEvent(self,event):
        print("clean all")
        event.accept()
        os._exit(0)

    def get_signal(self):
        self.run_detection(command_num=7,b="null")

    def get_info(self):
        self.run_detection(command_num=8,b="null")

    def set_ON(self):
        """"Sets the device selected by the user to on"""
        self.run_detection(command_num=0, b="null")

    def set_OFF(self):
        """" Sets the device selected by the user to off """
        self.run_detection(command_num=1, b="null")

    def set_power_up_KEEP(self):
        """Set “power up state out is KEEP“ of all selected devices by user ."""
        self.run_detection(command_num=2, b="null")

    def set_power_up_ON(self):
        """Set all devices selected by the user to [power-on-state-on]"""
        self.run_detection(command_num=3, b="null")

    def set_power_up_OFF(self):
        """Set “power up state out is OFF“ of all selected devices by user ."""
        self.run_detection(command_num=4, b="null")

    def set_POINT(self):
        """Set the inching time of all selected devices by user ."""
        # Check if the user has selected the device
        if len(self.select_name) <= 0:
            QMessageBox.information(
                self,
                "Sending failed ",
                "No device selected yet！",
                QMessageBox.Yes,
                QMessageBox.Yes)
            return
        vrg = {}
        # The pop-up dialog box waits for user input
        set_time_dialog = SetTimeDialog()
        set_time_dialog.show()
        ret = set_time_dialog.exec_()
        if ret:
            if set_time_dialog.set_sta:
                all_time = set_time_dialog.all_time()
                print("all_time", all_time)
                if all_time == 0:
                    QMessageBox.critical(
                        self, "set time fail", "input time error!")
                    return
                vrg["pulseWidth"] = all_time
                vrg["pulse"] = "on"
            else:
                vrg["pulse"] = "off"
                vrg["pulseWidth"] = 500
            set_time_dialog.destroy()
            self.run_detection(command_num=5, command_vrg=vrg)

    def set_POINT_a_sub(self, sub_id):
        """
        Set the inching time of all selected devices by user .
        :param sub_id: You need to set the device ID for the inching mode
        :return:
        """
        # Parses the mDNS to get the inching information to the current device
        # and adds it to the dialog box
        vrg = {}
        pass
        vrg["pulse"] = "on"
        sub_info = self.mDNS_info_sta[sub_id]
        all_time = sub_info["pulseWidth"]
        min_time = all_time // 60000
        sec_time = all_time % 60000 // 1000
        if all_time % 1000 == 500:
            sec_sta = True
        else:
            sec_sta = False
        if sub_info["pulse"]:
            sta = True
        else:
            sta = False
        #  The pop-up dialog box waits for user input
        set_time_dialog = SetTimeDialog(
            min=min_time, sec=sec_time, pulse=sta, sec_sta=sec_sta)
        set_time_dialog.show()
        ret = set_time_dialog.exec_()
        if ret != 0:
            all_time = set_time_dialog.all_time()
            print("all_time", all_time)
            if all_time == 0:
                QMessageBox.critical(
                    self, "set time fail", "input time error!")
                return
            if set_time_dialog.set_sta:
                vrg["pulseWidth"] = all_time
                vrg["pulse"] = "on"
            else:
                vrg["pulse"] = "off"
                vrg["pulseWidth"] = all_time
            # print("send：", vrg)
            self.run_a_dev(sub_id, command_num=5, command_vrg=vrg)
        set_time_dialog.destroy()

    def set_wifi(self):
        """Set SSID and password for batch devices"""
        # Check if the user has selected the device
        if len(self.select_name) <= 0:
            QMessageBox.information(
                self,
                "Sending failed",
                "No device selected yet！",
                QMessageBox.Yes,
                QMessageBox.Yes)
            return
        #  The pop-up dialog box waits for user input
        dialog = WIFIDialog()
        dialog.show()
        ret = dialog.exec_()
        if ret:
            wifi_name = dialog.name()
            wifi_password = dialog.password()
            print(wifi_name)
            print(wifi_password)
            vrg = {"SSID": wifi_name, "password": wifi_password}
            self.run_detection(command_num=6, command_vrg=vrg)
        dialog.destroy()

    def set_root(self):
        """Go into root mode"""
        dialog = RootDialog(b=self.mDNS_info_sta)
        dialog.show()
        dialog.exec_()
        dialog.destroy()

    def thread_deal_mDNS_new(self, cur_new_str):
        """
        Used to receive and process information from the mDNS thread
        :param cur_new_str: Data from the QTthread(mDNS)
        :return: None
        """
        # cur_new_str   （info.name ip port data）"\n" is the interval between
        # each parameter
        new_list = cur_new_str.splitlines()
        name = new_list[0]
        if new_list[1] == "DEL":
            if name in self.mDNS_info_sta:
                del self.mDNS_info_sta[name]
                del self.UI_sub_info[name]
                self.flash_name_id_to_ui()
            return
        ip = new_list[1]
        port = new_list[2]
        data_info = eval(new_list[3])
        data = eval(str(data_info[b'data1'], encoding="utf8"))
        if "off" in data["switch"]:
            switch = False
        else:
            switch = True

        if "off" in data["pulse"]:
            pulse = False
        else:
            pulse = True
        self.mDNS_info_sta[name] = {
            "ip": ip,
            "port": port,
            "switch": switch,
            "startup": data["startup"],
            "pulse": pulse,
            "pulseWidth": data["pulseWidth"],
            "rssi": data["rssi"]}
        print(name, ">>>", self.mDNS_info_sta[name])
        self.new_sub_to_ui()

    def new_sub_to_ui(self):
        """
        Check the mDNS_info_sta dictionary for new devices, and if so, add them to the UI_sub_info dictionary
        """
        for x in self.mDNS_info_sta.keys():
            if x not in self.UI_sub_info.keys():
                self.UI_sub_info[x] = {
                    "usr_name": x,
                    "line_num": self.sub_total,
                    "select_state": False}
                self.sub_total += 1
                self.table_all_sub.append(x)
        self.add_line_item()

    def flash_name_id_to_ui(self):
        """
        Sort the devices for UI_sub_info
        """
        num = 0
        for x in self.mDNS_info_sta.keys():
            sub_info = self.UI_sub_info[x]
            sub_info["line_num"] = num
            self.UI_sub_info[x] = sub_info
            self.table_all_sub.append(x)
            num += 1
        self.sub_total = num
        self.add_line_item()

    def table_check(self, b, c):
        """
        The processing table is clicked on row B, column C
        """
        print("row", b, "column", c)
        self.ui.tableWidget.item(b, c).setSelected(False)
        # Find the corresponding name
        for x in self.UI_sub_info.keys():
            cur_sub = self.UI_sub_info[x]
            if b == cur_sub["line_num"]:
                if c == 0:
                    if cur_sub["select_state"]:
                        cur_sub["select_state"] = False
                        self.ui.tableWidget.item(
                            b, 0).setBackgroundColor(
                            QColor(
                                255, 255, 255))
                        self.select_name.remove(x)
                    else:
                        cur_sub["select_state"] = True
                        self.ui.tableWidget.item(
                            b, 0).setBackgroundColor(
                            QColor(
                                0, 0, 255))
                        self.select_name.append(x)
                elif c == 1:
                    self.change_usr_name(x)
                elif c == 2:
                    self.run_a_dev(sub_id=x, command_num=0, b="null")
                elif c == 3:
                    self.run_a_dev(sub_id=x, command_num=1, b="null")
                elif c == 4:
                    self.run_a_dev(sub_id=x, command_num=3, b="null")
                elif c == 5:
                    self.run_a_dev(sub_id=x, command_num=4, b="null")
                elif c == 6:
                    self.run_a_dev(sub_id=x, command_num=2, b="null")
                elif c == 7:
                    self.set_POINT_a_sub(x)

    def change_usr_name(self, sub_name):
        """
        Handle changing names
        :param sub_name: equipment ID
        :return:
        """
        new_name, ok = QInputDialog.getText(self, "input name", "name:")
        if ok:
            print(sub_name, "--->", new_name)
            cur_sub_ui_info = self.UI_sub_info[sub_name]
            cur_sub_ui_info["usr_name"] = str(new_name)
            self.UI_sub_info[sub_name] = cur_sub_ui_info
            self.add_line_item()

    def add_line_item(self):
        """
        Brush the table according to the UI_sub_info dictionary
        """
        # Count all devices
        item_all_num = len(self.UI_sub_info)
        # Sets the total number of rows
        self.ui.tableWidget.setRowCount(item_all_num)
        # Set the number of columns(id|Modify the
        # name|ON|OFF|Power-on-state-ON|OFF|KEEP|SET INCH)
        self.ui.tableWidget.setColumnCount(9)
        # Draw table
        for x in self.UI_sub_info.keys():
            # print("get sub_name %s"%x)
            cur_sub = self.UI_sub_info[x]
            # print("cur_sub info %s"%cur_sub)
            line_num = cur_sub["line_num"]
            select_state = cur_sub["select_state"]
            name = cur_sub["usr_name"]
            sub_sta_info = self.mDNS_info_sta[x]
            # print("sub_sta_info info %s"%sub_sta_info)
            # Fill in the name of the equipment
            new_name = QTableWidgetItem(name)
            self.ui.tableWidget.setItem(line_num, 0, new_name)
            # Enter the modify name button
            edit_name = QTableWidgetItem("Edit name")
            self.ui.tableWidget.setItem(line_num, 1, edit_name)
            # Fill in the "ON" button
            b_on = QTableWidgetItem("ON")
            self.ui.tableWidget.setItem(line_num, 2, b_on)
            b_off = QTableWidgetItem("OFF")
            self.ui.tableWidget.setItem(line_num, 3, b_off)
            # Fill in the "power on" button
            b_p_on = QTableWidgetItem("Power-on-state-ON")
            self.ui.tableWidget.setItem(line_num, 4, b_p_on)
            b_p_off = QTableWidgetItem("Power-on-state-OFF")
            self.ui.tableWidget.setItem(line_num, 5, b_p_off)
            b_p_keep = QTableWidgetItem("Power-on-state-KEEP")
            self.ui.tableWidget.setItem(line_num, 6, b_p_keep)
            # Fill in the "Inching" button
            b_inch = QTableWidgetItem("Inching")
            self.ui.tableWidget.setItem(line_num, 7, b_inch)
			# rssi
            newresultBItem=QTableWidgetItem(str(sub_sta_info["rssi"]))
            self.ui.tableWidget.setItem(line_num,8,newresultBItem)
            # Color according to the device information
            if select_state:
                self.ui.tableWidget.item(
                    line_num, 0).setBackgroundColor(
                    QColor(
                        0, 0, 255))
            else:
                self.ui.tableWidget.item(
                    line_num, 0).setBackgroundColor(
                    QColor(
                        255, 255, 255))

            if sub_sta_info["switch"]:
                self.ui.tableWidget.item(
                    line_num, 2).setBackgroundColor(
                    QColor(
                        255, 0, 255))
            else:
                self.ui.tableWidget.item(
                    line_num, 3).setBackgroundColor(
                    QColor(
                        0, 255, 255))
            if sub_sta_info["startup"] is "on":
                self.ui.tableWidget.item(
                    line_num, 4).setBackgroundColor(
                    QColor(
                        0, 128, 0))
            elif sub_sta_info["startup"] is "off":
                self.ui.tableWidget.item(
                    line_num, 5).setBackgroundColor(
                    QColor(
                        0, 128, 0))
            elif sub_sta_info["startup"] is "stay":
                self.ui.tableWidget.item(
                    line_num, 6).setBackgroundColor(
                    QColor(
                        0, 128, 0))
        self.ui.tableWidget.horizontalHeader().setVisible(False)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        # Sets the table not to be edited
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def result_to_ui(self, result_str):
        """
        Process the information returned by the thread of execution
        :param result_str:Data from the QTthread
        :return: None
        """
        if "END" in result_str:
            # self.ui.pushButton.setDisabled(0)
            self.thread_number -= 1
            if self.result_ui:
                print("get：%s" % self.send_result)
                result_ui = resultDialog(info=self.send_result)
                result_ui.show()
                result_ui.exec_()
                result_ui.destroy()
                self.result_ui = False
            self.send_result = {}
            return
        result_list = result_str.split("\n")
        print("The return value is received：", result_list)
		self.send_result[result_list[0]]=eval(result_list[1])


    def run_detection(self, command_num, **comand_vrg):
        """
        Pass the user selected device list and all device
         information to the thread of execution, which processes it
        :param command_num:Order number
        :param comand_vrg:Parameters required to execute the command
        :return: None
        """
        if len(self.select_name) <= 0:
            QMessageBox.information(
                self,
                "Sending failed",
                "No device selected yet！",
                QMessageBox.Yes,
                QMessageBox.Yes)
            return
        dicta = {
            "info": self.mDNS_info_sta,
            "select_name_list": self.select_name}
        pass
        dicta["command_num"] = command_num
        dicta["command_vrg"] = comand_vrg
        self.result_ui = True
        if self.thread_number <= 0:
            self.thread_number += 1
            self.myThread = ThreadForQT(parent=None, **dicta)
            # Sets the signal tube correlation function
            self.myThread.run_test_Thread.connect(self.result_to_ui)
            self.myThread.start()
        else:
            QMessageBox.information(
                self,
                "error",
                "There is data being sent, please do not operate frequently！",
                QMessageBox.Yes,
                QMessageBox.Yes)

    def run_a_dev(self, sub_id, command_num, **comand_vrg):
        """
        Passes the user selected device list and individual device
        information to the thread
        :param sub_id: The ID of the target device
        :param command_num:Order number
        :param comand_vrg:Parameters required to execute the command
        :return:None
        """
        print("run_a_dev：", sub_id)
        sud_id_tmp = [sub_id]
        dicta = {"info": self.mDNS_info_sta, "select_name_list": sud_id_tmp}
        pass
        dicta["command_num"] = command_num
        dicta["command_vrg"] = comand_vrg
        self.result_ui = False
        if self.thread_number <= 0:
            self.thread_number += 1

            self.myThread = ThreadForQT(parent=None, **dicta)
            self.myThread.run_test_Thread.connect(self.result_to_ui)
            self.myThread.start()
        else:
            QMessageBox.information(
                self,
                "error",
                "There is data being sent, please do not operate frequently！",
                QMessageBox.Yes,
                QMessageBox.Yes)

    def check_all(self):
        """Select all handler functions"""
        for x in self.UI_sub_info.keys():
            cur_sub = self.UI_sub_info[x]
            print("name:", cur_sub)
            cur_sub["select_state"] = True
            if x not in self.select_name:
                self.select_name.append(x)

    def check_not(self):
        """Reverse select handler"""
        for x in self.UI_sub_info.keys():
            cur_sub = self.UI_sub_info[x]
            print("name:", cur_sub)
            if cur_sub["select_state"]:
                cur_sub["select_state"] = False
                self.select_name.remove(x)
            else:
                cur_sub["select_state"] = True
                self.select_name.append(x)

    def out_check(self):
        """Uncheck the handler function"""
        for x in self.UI_sub_info.keys():
            cur_sub = self.UI_sub_info[x]
            print("name:", cur_sub)
            cur_sub["select_state"] = False
        self.select_name = []

    def write_log(self, log_data):
        """
        Output log file
        :param log_data: Log data
        :return:None
        """

        cur_log = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()) + log_data + "\r\n"
        try:
            with open("UI_log.txt", "a+") as log:
                log.write(cur_log)
        except BaseException:
            print("main_window_error")


def main():
    app = QApplication(sys.argv)
    app_ui = MainWindow()
    app_ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
