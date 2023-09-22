#!/usr/bin/python3

from time import sleep
from network.rpi_rf import RFDevice
import os
import configparser


config = configparser.ConfigParser()
rf_codes_config = configparser.ConfigParser()
config.read('settings.ini')
rf_codes_config.read('rf_code.ini')

#  logging setting read
logging_status = config.get('HOME_REMOTE', 'logging')
if logging_status == "on" or logging_status == "min":
    import logging

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='home_remote.log',
                        )


def logging_for_me(a):
    if logging_status == "on":
        logging.info(a)
    else:
        pass


rfdevice = RFDevice(17, tx_proto=1, tx_length=350)
rfdevice.enable_tx()


class Connecting:
    def __init__(self, ip_address=None, rf_on=None, rf_off=None, username=None, macaddress=None):
        # self.switch = switch
        self.ip_address = ip_address

        if rf_on is not None:
            self.rf_on = int(rf_on)
        if rf_off is not None:
            self.rf_off = int(rf_off)
        if rf_off is None:
            self.rf_on = None
        if rf_off is None:
            self.rf_off = None

        self.username = username
        self.macaddress = macaddress

        self.status = 0  # on/off
        self.reboot_protection = 0
        self.missed = 0  # because of start log "pi3kitchen is up"

    def check_online(self, ping_cycle=1):
        """
        If missed goes in if condition.
        """
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

    def wake_on_lan(self):
        """
        Send wake-on-LAN package in subnet with MAC-Address
        It is also possible to send a wake-on-LAN package in another subnet.
        To another subnet will work with:
        TODO: "-i self.macaddress" argument should be in xxx.xxx.xxx.255 form?
        os.system("wakeonlan -i " + self.macaddress + " " + self.macaddress)
        """
        # TODO: check wakeonlan works with sudo or not!
        os.system("wakeonlan " + self.macaddress)
        logging_for_me("Send wake-on-LAN package to " + self.macaddress)

    def shutdown_fn(self):
        os.system("sudo -u pi /usr/bin/ssh -i ~/.ssh/id_rsa -l " + self.username + " " + self.ip_address + " > /dev/null")
        logging_for_me("Sent shutdown command to: " + self.ip_address)

    def on(self):
        """
        if username filled in, then will wake-on-LAN function active
        Example -> debian-kammer, it has no rf-socket.
        if rf_off filled in, then will rf function activ
        Example -> stammem speakers. They have no shutdown function and wake-up function
        """
        if self.macaddress is not None:
            self.wake_on_lan()

        if self.rf_on is not None:
            for x in range(5):
                rfdevice.tx_code(self.rf_on)
                sleep(0.1)
        return 1

    def off(self, socket=0):
        """
        if username filled in, then will shut down function active
        Example -> debian-kammer, it has no rf-socket.
        if rf_off filled in, then will rf function activ
        Example -> stammem speakers. They have no shutdown function
        if both filled in, then will both function activ.
        Example -> raspi will goes down wait 20 seconds and then the socket will be turned off
        sleep(20) disabled
        """
        if self.username is not None:
            self.shutdown_fn()

        # if self.macaddress is None and socket == 0:
        #     sleep(20)

        if self.rf_off is not None:
            for x in range(5):
                rfdevice.tx_code(self.rf_off)
                sleep(0.1)
        return 0

    def check_autostart(self):
        """
        If missed goes in if condition.
        """
        if os.system("ping -c 1 -W 1 " + self.ip_address + " > /dev/null 2>&1"):
            self.reboot_protection += 1

            if self.reboot_protection == 2 or self.reboot_protection == 10:
                self.missed = 0

            if self.reboot_protection > 120:  # counter reset
                self.reboot_protection = 0

            # self.missed should stay after if conditions
            self.missed += 1

        else:
            self.status = 1
            self.missed = 0

        if self.missed == 5:
            if self.macaddress is not None:
                self.wake_on_lan()

            if self.rf_off is not None:
                self.off()  # pi3kitchen is off, should just electric off
                sleep(3)
                self.on()

            self.status = 1

        return self.status
