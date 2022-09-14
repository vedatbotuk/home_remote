#!/usr/bin/python3

from time import sleep
import configparser
import network as network

#  here comes global variables
c_exception = 0
pi3kitchen_status = 0
network_status = 0
some_one_at_home = 0
ip_smartphone = []


# settings read
# USER VARIABLES FROM .ini CONFIG FILE

config = configparser.ConfigParser()
config.read('/home/pi/home_remote3/trunk/settings.ini')


#  logging setting read
logging_status = config.get('HOME_REMOTE', 'logging')
if logging_status == "on" or logging_status == "min":
    import logging

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/var/log/my_projekts/home_remote.log',
                        )

#  here settings for checkip on/off
ping_cycle = config.getint('HOME_REMOTE', 'ping_cycle')
try:
    ip_smartphone.append(config.get('HOME_REMOTE', 'ip0'))
    ip_smartphone.append(config.get('HOME_REMOTE', 'ip1'))
    ip_smartphone.append(config.get('HOME_REMOTE', 'ip2'))
    ip_smartphone.append(config.get('HOME_REMOTE', 'ip3'))
    ip_smartphone.append(config.get('HOME_REMOTE', 'ip4'))
except configparser.NoOptionError:
    # logging.error("Could not add all ips")
    pass


router_host = config.get('HOME_REMOTE', 'router_host')
omada_host = config.get('HOME_REMOTE', 'omada_host')
stammen_pink_host = config.get('HOME_REMOTE', 'stammen_pink_host')
stammen_green_host = config.get('HOME_REMOTE', 'stammen_green_host')
pi3kitchen_ip = config.get('HOME_REMOTE', 'pi3kitchen_ip')

# settings read end


# devices
pi3kitwchen = network.Connecting(pi3kitchen_ip, 1, 1, 1)
stammen_pink = network.Connecting(stammen_pink_host, 1, 1)  # host will be not used
stammen_green = network.Connecting(stammen_green_host, 1, 1)  # host will be not used
omada = network.Connecting(omada_host)
router = network.Connecting(router_host)
smartphones = network.Connecting(ip_smartphone)


def logging_for_me(a):
    if logging_status == "on":
        logging.info(a)
    else:
        pass


def network_check():
    global network_status
    if omada.check_online() == 1 and router.check_online() == 1:
        network_status = 1
    else:
        network_status = 0


def system_on():
    global pi3kitchen_status
    global network_status
    global some_one_at_home

    while True:
        sys_state = 0
        sleep(0.2)
        network_check()
        if network_status == 1:
            pi3kitchen_status = pi3kitchen.check_autostart()

        some_one_at_home = smartphones.check_online(ping_cycle)
        for x in range(150):
            sleep(0.2)
            if some_one_at_home == 0:
                logging_for_me("")
                logging_for_me(">>> system goes off >>>")

                logging_for_me("pi3kitchen and stammen go down")

                pi3kitchen_status = pi3kitchen.off()
                stammen_pink.off()
                stammen_green.off()

                pi3kitchen_status = pi3kitchen.check_online()  # proction if signal not sent,
                #  and electric not down

                if pi3kitchen_status == 0:
                    sys_state = 1
                    break
                else:
                    logging_for_me("system off not completed")
                    sleep(3)

        if sys_state == 1:
            logging_for_me("<<< system goes off <<<")
            sleep(3)
            break


def system_off():
    global pi3kitchen_status
    global network_status
    global some_one_at_home

    while True:
        sys_state = 0
        network_check()
        some_one_at_home = smartphones.check_online(ping_cycle)
        sleep(0.2)
        for x in range(150):
            sleep(0.2)
            if some_one_at_home == 1:

                sleep(0.1)

                logging_for_me("")
                logging_for_me(">>> system goes on >>>")

                pi3kitchen_status = pi3kitchen.on()
                stammen_pink.on()
                stammen_green.on()

                logging_for_me("pi3kitchen and stammen starting")

                sleep(5)
                sys_state = 1
                break

        if sys_state == 1:
            logging_for_me("<<< system goes on <<<")
            logging_for_me("")
            sleep(3)
            break


def system_start():
    global some_one_at_home
    global pi3kitchen_status
    global network_status

    logging.info("")
    logging.info("START SYSTEM")

    sleep(20)  # reboot waiting because of network

    network_check()

    if network_status == 1:
        pi3kitchen_status = pi3kitchen.check_online()  # check pi3kitchen. important for switch off
        some_one_at_home = smartphones.check_online()

    if some_one_at_home == 1:  # is switch on
        logging_for_me("system status on")
        if pi3kitchen_status == 0:
            logging_for_me("pi3kitchen is down")

        logging_for_me("pi3kitchen and stammen sockets go on")
        pi3kitchen.on()
        stammen_pink.on()
        stammen_green.on()

        logging_for_me("")

    else:  # switch off
        logging_for_me("system status off")
        if pi3kitchen_status == 1:
            pi3kitchen_status = pi3kitchen.off()
            logging_for_me("pi3kitchen goes down")

        pi3kitchen.off(socket=1)  # if steckdose on, and pi3kitchen off, protection off
        stammen_pink.off()
        stammen_green.off()
        logging_for_me("pi3kitchen and stammen sockets go off")
        logging_for_me("")


# here start the main ####

if __name__ == "__main__":

    system_start()

    while True:
        try:
            sleep(0.2)
            if some_one_at_home == 1:
                system_on()

            sleep(0.2)
            if some_one_at_home == 0:
                system_off()

        except Exception as e:
            logging.error(">>>Exception>>>")
            sleep(0.1)
            logging.error('Failed.', exc_info=e)
            sleep(10)
            c_exception += 1
            if c_exception > 2:
                logging.error("<<<Exception & EXIT<<<")
                break
            logging.error("<<<Exception<<<")
            system_start()
