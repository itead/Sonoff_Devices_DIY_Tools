# -*- coding: utf-8 -*-
"""
    This module is mainly used to send HTTP(POST) requests to devices
    class:
        ThreadForQT(Classes based on QT threads)
"""
import time
import time
import requests
import json
from PySide2.QtCore import *


class Http_API(object):
    """
    Used to send an HTTP post request to the device
    send_error = The error code corresponding to the failure to send
    send_text = A message sent out
    send_response = Data sent and returned
    function：
    postRequest：Send a post request

    """

    def __init__(self):
        self.send_error = 0
        self.send_text = ""
        self.send_response = ""

    def postRequest(self, url=None, data=None):
        """
        Only a simple HTTP(post) sending function is implemented
        Request is made with HTTP (port)
        :param url:sent to http://ip:port/location,
        :param data: data segment
        :return:
        """
        ret = {}
        # Here you need to add data with or without checksum and url with or
        # without checksum
        json_str = json.dumps(data)
        print("send ING", json_str)
        self.send_text = json_str
        self.write_log("send ING")
        self.write_log(self.send_text)
        response = requests.post(url=url, data=json.dumps(data), timeout=10)
        self.send_response = response
        print("RETURN response：", response.text)
        self.write_log("RETURN response")
        self.write_log(response.text)
        ret["result"] = True
        ret["text"] = response.text
        return ret

    def write_log(self, log_data):
        """
        Write to log file
        :param log_data:LOG Data
        :return:None
        """
        cur_log = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()) + log_data + "\r\n"
        try:
            with open("log.txt", "a+") as log:
                log.write(cur_log)
        except BaseException:
            print("lan_ewlink_api_error")


class ThreadForQT(QThread):
    """
    Classes based on QT threads
    What it does: sends the corresponding command over HTTP to the device.
        This is to parse the user's actions on the interface into corresponding instructions (protocol documents),
        and then call Http_API(postRequest) to send to the corresponding IP and post address
    Process:
        1. Analyze the information from the interface thread;
        2. Assemble url and data;
        3. Call Http_API(postRequest) to send out
    Run_test_Thread = Signal(STR) passes the completion of the execution to the interface thread

    Initialize the incoming variable：
        info：Information on all devices(ID IP PORT)
        select_name_list：The device selected by the user
        command_num：Order number
        command_vrg：Parameters required by the command

    function：
        performer_func：Execute the send command
        def set_OUT(self,**info):The function that sets the output of the device
        def set_power_up_state(self,**info):Set the function of the power on the device
        def get_signal_intensity(self,**info):Function to get the current wifi strength of the device
        def set_point_sewidth(self,**info):Set the function that the device points to
        def set_wifi(self,**info):Function to set the device wifi

        def set_unlock(self,**info):Set device unlock function!!!
                                    The device will send data to the escalation server!!!
                                    The equipment is no longer under warranty!!!

        def set_ota_flash(self,**info):Set the firmware download address on the device LAN
                                        (you need to set the device unlocking first)
    """
    run_test_Thread = Signal(str)

    def __init__(self, parent=None, **func_task):
        super(ThreadForQT, self).__init__(parent)
        # Device information (deviceID IP PORT)
        print("func_task", str(func_task))
        self.all_info_dict = func_task["info"]
        # The user selects the device list
        self.all_dev_id = func_task["select_name_list"]
        print(self.all_dev_id)
        # Gets the command to execute
        self. command_num = func_task["command_num"]
        # Parameters required to execute the command
        vrg = func_task["command_vrg"]
        if "command_vrg" in vrg:
            self.command_vrg = vrg["command_vrg"]
        else:
            self.command_vrg = {"b": "null"}
        # print("ThreadForQT，func_task==%s" % func_task)
        # print("ThreadForQT，self. command_vrg==%s" % self. command_vrg)
        self.ht = Http_API()

    def __def__(self):
        self.wait()

    def run(self):
        """
        The function thread runs the function
        Execute the corresponding command based on the parameters passed during initialization
        """
        for x in self.all_dev_id:
            # Resolve out the device ID
            print("#device ID", x)
            ret = x + "\n" + str(self.performer_func(x)) + "\n"
            # Feedback the result
            self.run_test_Thread.emit(ret)
        # The end of the thread
        self.run_test_Thread.emit("END")

    def performer_func(self, sub_id):
        cur_sub_info = self.all_info_dict[sub_id]
        print("performer_func", cur_sub_info)
        port = cur_sub_info["port"]
        ip = cur_sub_info["ip"]
        ret = 999
        if self. command_num == 0:
            # 0 command（"ON"）
            ret = self.set_OUT(OUT=True, ip=ip, port=port, sub_id=sub_id)
        elif self. command_num == 1:
            # 1 command（"OFF"）
            ret = self.set_OUT(OUT=False, ip=ip, port=port, sub_id=sub_id)
        elif self. command_num == 2:
            # 2 command（"Power-on-state-KEEP"）
            ret = self.set_power_up_state(
                state=2, ip=ip, port=port, sub_id=sub_id)
        elif self. command_num == 3:
            # 3 command（"Power-on-state-ON"）
            ret = self.set_power_up_state(
                state=1, ip=ip, port=port, sub_id=sub_id)
        elif self. command_num == 4:
            # 4 command（"Power-on-state-OFF"）
            ret = self.set_power_up_state(
                state=0, ip=ip, port=port, sub_id=sub_id)
        elif self. command_num == 5:
            # 5 command（"SET INCH"）
            ret = self.set_point_sewidth(
                pulseWidth=self. command_vrg["pulseWidth"],
                pulse=self. command_vrg["pulse"],
                ip=ip,
                port=port,
                sub_id=sub_id)
        elif self. command_num == 6:
            # 6 command（"Change SSID"）
            ret = self.set_wifi(
                ssid=self. command_vrg["SSID"],
                password=self. command_vrg["password"],
                ip=ip,
                port=port,
                sub_id=sub_id)
        elif self. command_num == 7:
            # 7 command（"ROOT"）
            ret=self.get_signal_intensity(ip=ip,port=port,sub_id=sub_id)
        elif self. command_num==8:
            #8命令（获取设备状态信息）
            ret=self.get_dev_info_api(ip=ip,port=port,sub_id=sub_id)
        elif self. command_num==9:
            #9命令（解锁ota）
            print("self.command_vrg==",self.command_vrg)
            ret=self.set_unlock(ip=ip,port=port,sub_id=sub_id)
            print("ret",ret)
            if ret['error'] == 0:
                #10命令（发送升级信息）
                ret=self.set_ota_flash(sha256sum= self.command_vrg["sha256sum"], sever_ip= self.command_vrg["sever_ip"], sever_port=self. command_vrg["sever_port"], ip=ip, port=port, sub_id=sub_id)
        return ret

    def send_data(self, send_url, send_data):
        """
        send data to device by HTTP PORT
        """
        #try:
        print("send：",send_url,str(send_data))
        response =self.ht.postRequest(send_url,send_data)
        print("response：",str(response))
        if response["result"]:
            return json.loads(response["text"])
        else:
            return 1

    def set_OUT(self, **info):
        """
        Set the lights on and off
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    OUT(bool)The state that requires the device to be set
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        out_sta = info["OUT"]
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/switch"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        if out_sta:
            data["data"]=	{"switch": "on"}
        else:
            data["data"]=	{"switch": "off"}
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def set_power_up_state(self, **info):
        """
        Set the output state of the device when it is powered on
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    state(int)The state that requires the device to be set(0:off 1:on 2:keep )
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        state = info["state"]
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/startup"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        if(state== 0):
            data["data"]=	{"startup": "off"}
        elif (state== 1):
            data["data"]=	{"startup": "on"}
        elif (state== 2):
            data["data"]=	{"startup": "stay"}
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def get_signal_intensity(self, **info):
        """
        Get the signal strength of the device
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/signal_strength"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        data["data"] = { }
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def set_point_sewidth(self, **info):
        """
        Set the device's inching mode
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    pulseWidth(int)Delay millisecond(500-36000000)
                    pulse(str)Inching mode("on" or "off")
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        pulseWidth = info["pulseWidth"]
        pulse = info["pulse"]
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/pulse"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        data["data"]=	{"pulse": pulse,"pulseWidth": pulseWidth}
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def set_wifi(self, **info):
        """
        Set the device's SSID info(SSID and password)
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    ssid(srt)new wifi SSID
                    password(str)new wifi password
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        ssid = info["ssid"]
        password = info["password"]
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/wifi"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        data["data"]=	{"ssid": ssid, "password":  password}
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def set_unlock(self, **info):
        """
        Set the device's UNLOCK
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        sub_dict = info
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/ota_unlock"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        data["data"]=	{ }
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)

    def set_ota_flash(self, **info):
        """
        Set the device's UNLOCK
        Process: 1. Assembly url.
                 2. Assemble data.
                 3. Call Http_API(postRequest) to send.

        :param info:
                    sever_ip(str)IP of the firmware server
                    sever_port(int) Port number of the firmware server
                    sha256sum(str) SHA256 check value for the entire file
                    ip(str)The IP address of the device
                    port(int)The port number of the device
                    sub_id(str)The id number of the device
        :return:
        """
        sub_dict = info
        data = {}
        # 1. Assembly url.
        url = "http://" + info["ip"] + ":" + \
            str(info["port"]) + "/zeroconf/ota_flash"
        # 2. Assemble data.
        data["sequence"] = str(int(time.time()))
        sub_id = info["sub_id"]
        data["deviceid"] = sub_id
        data["data"]=	{ }
        # 3. Call Http_API(postRequest) to send.
        return self.send_data(send_url=url, send_data=data)


    def get_dev_info_api(self,**info):
        """
        get device info 
        """
        sub_dict=info
        data={}
        #把组装好url
        url="http://"+info["ip"]+":"+str(info["port"])+"/zeroconf/info"
        #组装好data
        sub_id=info["sub_id"]
        data["deviceid"]=sub_id
        data["data"]=	{ }
        return self.send_data(send_url=url, send_data=data)
