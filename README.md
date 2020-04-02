# Sonoff Devices DIY Tools

(@Follows the BSD open source license)

## Introduction

Sonoff Devices DIY Tools is used for SONOFF Devices(Basic R3，RFR3 and Mini) control via LAN.

PS: 

firmware version 3.3.0 and 3.4.0 refer to the protocol v1.4

firmware version 3.5.0 refer to the protocol v2.0, as the set up procedure changed, the tool can not be used for the device with firmware 3.5.0. In 3.5.0, the device can be set as a AP and accessed with URL of http://10.10.7.1/ 

AP access point:

```
SSID: ITEAD-xxxxxxx
Password: 12345678
```

Rest API:

- Set devices ON and OFF

- Set the "Power On State" of the devices

- Set inching state and inching time of the devices

- Modify the LAN info (SSID and Password) of the device

- Flash the firmware via OTA

- Get the device info

  

## Directory Information

- /code
- /tool
- /other

/code：Sonoff Devices DIY Tools source code

(Clone the file in this folder and revise what you want)

/tool：Source code compiled exe. file

(You can download and run the exe. file in this folder, win10 is recommended )

/other：Sonoff Devices DIY Tools related documentations

(Documentations related with Sonoff DIY Mode API protocol and others)



### Welcome Issues
