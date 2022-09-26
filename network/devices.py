#!/usr/bin/python3

from time import sleep
from network.rpi_rf import RFDevice
import os

rfdevice = RFDevice(17, tx_proto=1, tx_length=350)
rfdevice.enable_tx()

def shutdown_fn():
    os.system("sudo /usr/local/bin/pi3kitcendown.sh > /dev/null 2>&1")

class Connecting:
    def __init__(self, ip_address = None, rf_on = None, rf_off = None, shutdown = 0):
        # self.switch = switch
        self.ip_address = ip_address

        if rf_on or rf_off:
            self.rf_on = int(rf_on)
            self.rf_off = int(rf_off)

        self.shutdown = shutdown

        self.status = 0              # on/off
        self.reboot_protection = 0
        self.missed = 1              # because of start log "pi3kitchen is up"

    def check_online(self, ping_cycle=1):

        if not isinstance(self.ip_address, list):

            if os.system("ping -c 1 -W 1 " + self.ip_address + " > /dev/null 2>&1"):
                self.missed += 1
            else:
                self.status = 1
                self.missed = 0

            if self.missed == ping_cycle:
                self.status = 0

            return self.status

        else:
            for x in range(0, len(self.ip_address)):
                if os.system("ping -c 1 -W 1 " + self.ip_address[x] + " > /dev/null 2>&1"):
                    self.missed += 1

                else:
                    self.status = 1
                    self.missed = 0
                    return self.status

                if self.missed == len(self.ip_address) * ping_cycle * 2:
                    self.status = 0

            return self.status


    def on(self):
        for x in range(5):
            rfdevice.tx_code(self.rf_on)
            sleep(0.1)
        return 1

    def off(self, socket=0):

        if self.shutdown == 1 and socket == 0:
            shutdown_fn()
            sleep(20)

        for x in range(5):
            rfdevice.tx_code(self.rf_off)
            sleep(0.1)
        return 0

    def check_autostart(self, ping_cycle=4):

        if os.system("ping -c 1 -W 1 " + self.ip_address + " > /dev/null 2>&1"):
            self.missed += 1
            self.reboot_protection += 1

            if self.reboot_protection == 5 or self.reboot_protection == 10 or self.reboot_protection > 120:
                self.missed = 0

            if self.reboot_protection > 120:  # counter reset
                self.reboot_protection = 0

        else:
            self.status = 1
            self.missed = 0

        if self.missed == ping_cycle:
            self.off()  # pi3kitchen is off, should just electric off
            sleep(3)
            self.on()
            self.status = 1
            self.missed += 1  # so that not again goes in this loop  in this loop

        return self.status
