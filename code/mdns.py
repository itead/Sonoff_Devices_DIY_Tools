# -*- coding: utf-8 -*-
"""
    This module is dedicated to MDNS
    class：
        mDNS_BrowserThread(Used to continuously check mDNS)
"""

import time
from zeroconf import ServiceBrowser, Zeroconf
from PySide2.QtCore import *


class mDNS_BrowserThread(QThread):
    """
    This is a QT thread that gets the MDNS information and sends it to the UI thread via the get_sub_new signal.

    """
    get_sub_new = Signal(str)

    def __init__(self, parent=None, **func_task):
        super(mDNS_BrowserThread, self).__init__(parent)
        self.ID_list = []
        self.zeroconf = Zeroconf()
        self.listener = MyListener()

    def __def__(self):
        self.wait()

    def run(self):
        """
        The data of the searched device is refreshed every second,
         and each update is converted into a string and sent to the interface(name ip port data)
        """
        print("mDNS_BrowserThread start !")
        browser = ServiceBrowser(
            self.zeroconf,
            "_ewelink._tcp.local.",
            listener=self.listener)
        while True:
            if self.listener.all_sub_num > 0:
                # Copy from the listener's dictionary to the current file
                dict = self.listener.all_info_dict.copy()
                for x in dict.keys():
                    # print("new updata ID：",x[8:18])
                    info = dict[x]
                    info = self.zeroconf.get_service_info(info.type, x)
                    print("updata", x, "info", "len", len(str(info)), info)
                    if info is not None:
                        data = info.properties
                        cur_str = x[8:18] + "\n" + self.parseAddress(
                            info.address) + "\n" + str(info.port) + "\n" + str(data)
                        self.get_sub_new.emit(cur_str)
            # Send deleted devices
            if len(self.listener.all_del_sub) > 0:
                for x in self.listener.all_del_sub:
                    cur_str = x[8:18] + "\nDEL"
                    self.get_sub_new.emit(cur_str)
            time.sleep(0.5)

    def parseAddress(self, address):
        """
        Resolve the IP address of the device
        :param address:
        :return: add_str
        """
        add_list = []
        for i in range(4):
            add_list.append(int(address.hex()[(i * 2):(i + 1) * 2], 16))
        add_str = str(add_list[0]) + "." + str(add_list[1]) + \
            "." + str(add_list[2]) + "." + str(add_list[3])
        return add_str


class MyListener(object):
    """
    This class is used for the mDNS browsing discovery device, including calling the remove_service and add_service
    properties to ServiceBrowser, and also contains broadcasts for querying and updating existing devices.
        Dictionary
        all_info_dict:Qualified device information in the current network     [keys:info.name，val:info]
    """

    def __init__(self):
        self.all_del_sub = []
        self.all_info_dict = {}
        self.all_sub_num = 0
        self.new_sub = False

    def remove_service(self, zeroconf, type, name):
        """
        This function is called for ServiceBrowser.
        This function is triggered when ServiceBrowser discovers that some device has logged out
        """
        print("inter remove_service()")
        self.all_sub_num -= 1
        del self.all_info_dict[name]
        self.all_del_sub.append(name)
        print("self.all_info_dict[name]", self.all_info_dict)
        print("Service %s removed" % (name))

    def add_service(self, zeroconf, type, name):
        """
        This function is called for ServiceBrowser.This function is triggered when ServiceBrowser finds a new device
        When a subdevice is found, the device information is stored into the all_info_dict
        """
        self.new_sub = True
        print("inter add_service()")
        self.all_sub_num += 1
        info = zeroconf.get_service_info(type, name)
        if info.properties[b'type'] == b'diy_plug':
            self.all_info_dict[name] = info
            if name in self.all_del_sub:
                self.all_del_sub.remove(name)
                print("Service %s added, service info: %s" % (name, info))

    def flash_all_sub_info(self,):
        """
        Update all found subdevice information
        """
        info_list = list(self.all_info_dict.keys())
        for x in info_list:
            current_info = all_info_dict[x]
            name = current_info["name"]
            type = current_info["type"]
            info = zeroconf.get_service_info(type=type, name=name)
            current_info["info"] = info
            self.all_info_dict[x] = current_info["info"]
            
def main():
        zeroconf=Zeroconf()
        listener=MyListener()
        browser = ServiceBrowser(zeroconf, "_ewelink._tcp.local.",listener= listener)
        while True:
             if listener.all_sub_num>0:
                    dict=listener.all_info_dict.copy()
                    for x in dict.keys():
                        info=dict[x]
                        info=zeroconf.get_service_info(info.type,x)
                        if info!= None:
                            data=info.properties
                            cur_str=str(data)
                            print(cur_str)
                time.sleep(0.5)

                
if __name__ == "__main__":
    main()
