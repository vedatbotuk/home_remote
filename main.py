#!/usr/bin/python3

from time import sleep
import configparser
import network as network

#  here comes global variables
c_exception = 0
debiankammer_status = 0
network_status = 0
some_one_at_home = 0
ip_smartphone = []


# settings read
# USER VARIABLES FROM .ini CONFIG FILE

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
# stammen_pink_host = config.get('HOME_REMOTE', 'stammen_pink_host')
# stammen_green_host = config.get('HOME_REMOTE', 'stammen_green_host')
debiankammer_ip = config.get('HOME_REMOTE', 'debiankammer_ip')
debiankammer_mac = config.get('HOME_REMOTE', 'debiankammer_mac')
debiankammer_username = config.get('HOME_REMOTE', 'debiankammer_username')

# settings read end


# devices
debiankammer = network.Connecting(ip_address=debiankammer_ip, macaddress=debiankammer_mac, username=debiankammer_username)
# stammen_pink = network.Connecting(stammen_pink_host,
#                                   rf_codes_config.get('CODES', 'stammen_pink_on'),
#                                   rf_codes_config.get('CODES', 'stammen_pink_off'))  # host will be not used
# stammen_green = network.Connecting(stammen_green_host,
#                                    rf_codes_config.get('CODES', 'stammen_green_on'),
#                                    rf_codes_config.get('CODES', 'stammen_green_off'))  # host will be not used
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


def wait_for_system_off():
    global debiankammer_status
    global network_status
    global some_one_at_home

    while True:
        sys_state = 1
        network_check()
        some_one_at_home = smartphones.check_online(ping_cycle)
        if network_status == 1:
            if not debiankammer.check_autostart():
                debiankammer_status = 0
            else:
                debiankammer_status = 1

            if some_one_at_home == 0:
                logging_for_me("Nobody at home")
                logging_for_me(">>> System goes off >>>")
                logging_for_me("debian-kammer and stammen go down")
                debiankammer_status = debiankammer.off()

                if debiankammer_status == 0:
                    sys_state = 0
                else:
                    logging_for_me("System off not completed")
                    sleep(3)

        if sys_state == 0:
            logging_for_me("<<< System goes off <<<")
            break
        sleep(30)


def wait_for_system_on():
    global debiankammer_status
    global network_status
    global some_one_at_home

    while True:
        sys_state = 0
        network_check()
        some_one_at_home = smartphones.check_online()
        if network_status == 1:
            if some_one_at_home == 1:
                sys_state = 1
                logging_for_me(">>> System goes on >>>")
                debiankammer_status = debiankammer.on()
                logging_for_me("debian-kammer goes on")
        else:
            logging_for_me("Network status: OFF")

        if sys_state == 1:
            logging_for_me("<<< System goes on <<<")
            break

        sleep(30)


def system_start():
    global some_one_at_home
    global debiankammer_status
    global network_status

    logging.info("")
    logging.info("START SYSTEM")

    # sleep(20)  # reboot waiting because of network

    network_check()

    if network_status == 1:
        logging_for_me("Network status: ON")
        debiankammer_status = debiankammer.check_online()  # check debian-kammer. important for switch off
        some_one_at_home = smartphones.check_online()
    else:
        logging_for_me("Network status: OFF")

    if some_one_at_home == 1:
        logging_for_me("Someone at home")
        if debiankammer_status == 0:
            logging_for_me("debian-kammer is down")
            logging_for_me("debian-kammer goes on")
            debiankammer.on()
        else:
            logging_for_me("debian-kammer is already up")

    else:
        logging_for_me("System status: OFF -> Nobody at home")
        if debiankammer_status == 1:
            logging_for_me("debian-kammer activ")
            logging_for_me("debian-kammer should go down")
            debiankammer.off()


# here start the main ####
if __name__ == "__main__":

    system_start()
    sleep(30)

    while True:
        try:
            sleep(0.2)
            if some_one_at_home == 1:
                wait_for_system_off()

            sleep(0.2)
            if some_one_at_home == 0:
                wait_for_system_on()

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
