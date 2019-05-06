# -*- coding: utf-8 -*-
"""
    This module is about server threads
    class：
        SeverThreadForQT:(Based on QThread)
"""
from socket import *
import json
from PySide2.QtCore import *


class SeverThreadForQT(QThread):
    """
    This class handles data transfer using sockets directly
    __init__:It must be initialized with server_ip and server_post
    run:Block waiting for device connection, one device at a time
    ota_state_Thread: signal

    """
    ota_state_Thread = Signal(str)

    def __init__(self, parent=None, **func_task):
        super(SeverThreadForQT, self).__init__(parent)
        HOST = func_task["server_ip"]
        PORT = func_task["server_port"]
        ADDR = (HOST, PORT)
        # Create socket
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sockfd.bind(ADDR)
        self.count_bin_len()

    def __def__(self):
        self.wait()

    def run(self):
        self.sockfd.listen(5)
        # The loop waits for the client link
        while True:
            try:
                self.connfd, addr = self.sockfd.accept()
            except KeyboardInterrupt:
                sockfd.close()
                return
            except Exception as e:
                print(e)
                continue
            print("Client login:", addr)
            while True:
                try:
                    data = self.connfd.recv(1024).decode()
                    print("len ：", str(len(data)))
                    print("Receive ：%s" % data)
                    if "GET" in data:
                        self.do_GET(data)
                    elif "POST" in data:
                        self.do_POST(data)
                        return
                    else:
                        print("The client sends an error instruction")
                except BaseException:
                    self.ota_state_Thread.emit("ERR\n\n0")
                    break

    def count_bin_len(self):
        """
        Calculate the size of the firmware
        :return: None
        """
        with open("itead.bin", 'rb') as file_obj:
            img = file_obj.read()
            self.bin_len = len(img)

    def do_GET(self, data):
        print("Handle GET requests for devices")
        # Find the digital segment after "bytes="
        all_read = self.get_range_bytes(data)
        if all_read == -1:
            print("NOT FIND", data)
            return
        with open("itead.bin", 'rb') as file_obj:
            file_obj.seek(all_read[0], 0)
            self.img = file_obj.read(all_read[1] - all_read[0] + 1)
        # Open the file, read the corresponding data segment sent out
        print("HEAD：", len(self.img), "ALL LEN：", str(self.bin_len))
        # The header that assembles the HTTP data
        send_data = 'HTTP/1.1 206 Partial Content\r\n' + \
            'Content-type: application/octet-stream\r\n'
        send_Range = "bytes=" + \
            str(all_read[0]) + "-" + str(all_read[1]) + "/" + str(self.bin_len)
        send_data += 'Content-Length: ' + \
            str(len(self.img)) + '\r\n' + 'Content-Range: ' + send_Range + "\r\n\r\n"
        self.ckeck_finsh(all_read[1])
        self.my_send_head(send_data)
        print("send_data", str(send_data))
        self.connfd.send(self.img)
        print("send_data", str(self.img))
        get_new = "get\n\n" + str(self.updata_get_rata(all_read[0]) + 1)
        print(get_new)
        self.ota_state_Thread.emit(get_new)

    def ckeck_finsh(self, end_seek):
        if(self.bin_len - 1) == end_seek:
            self.send_over_flg = True
        else:
            self.send_over_flg = False

    def my_send_head(self, data):
        self.connfd.send(bytes(data, "ASCII"))

    def get_range_bytes(self, re_data):
        print(re_data, type(re_data), len(re_data))
        start_index = re_data.find("bytes") + 6
        data_f = re_data[start_index:].splitlines()
        start_read, end_read = data_f[0].split("-")
        print("开始位置：", start_read, "结束位置：", end_read)
        return [int(start_read), int(end_read)]

    def do_POST(self, data):
        print("post:", data)
        json_data = json.loads(self.find_post_json(data))
        print("json_data", json_data)
        if "error" in json_data:
            if json_data["error"] == 0:
                if self.send_over_flg:
                    print("To complete the transfer")
                    post_new = "post\n\n0"
                else:
                    print("Download failed")
                    post_new = "post\n\n1"
                print(post_new)
                self.ota_state_Thread.emit(post_new)
                print("To complete the transfer")
            elif json_data["error"] == 404:
                post_new = "post\n\n404"
                print(post_new)
                self.ota_state_Thread.emit(post_new)
                print("Download failed")
            elif json_data["error"] == 406:
                post_new = "post\n\n406"
                print(post_new)
                self.ota_state_Thread.emit(post_new)
                print("Error issuing upgrade message")
            elif json_data["error"] == 409:
                post_new = "post\n\n409"
                print(post_new)
                self.ota_state_Thread.emit(post_new)
                print("Check failure")
            elif json_data["error"] == 410:
                post_new = "post\n\n410"
                print(post_new)
                self.ota_state_Thread.emit(post_new)
                print("Internal error of equipment")

    def find_post_json(self, data):
        """
        Find the json data in the data section
        :param data:Data to look up
        :return:(str) "null"  or json"{ key: val   }"
        """
        if "{" in data:
            json_sta_index = data.find("{")
        else:
            return "null"
        if "}" in data:
            json_end_index = data.find("}")
        else:
            return "error data pool"
        return data[json_sta_index:json_end_index + 1]

    def updata_get_rata(self, new_seek):
        """
        Update firmware transfer progress
        :param new_seek:
        :return: (int) Percentage of current updates
        """
        return new_seek / self.bin_len * 100
