#!/usr/bin/env python
#  -*- coding: utf-8 -*-

# Copyright (C) 2016 - 2018 - BenBaptist and Wrapper.py developer(s).
# https://github.com/benbaptist/minecraft-wrapper
# This program is distributed under the terms of the GNU
# General Public License, version 3 or later.

import os
import sys
from core.wrapper import Wrapper
from api.helpers import getjsonfile
from utils.log import configure_logger
from utils.crypt import get_passphrase
import argparse

parser = argparse.ArgumentParser(
    description='Wrapper.py startup arguments',
    epilog='Created by SurestTexas00')

parser.add_argument('--encoding', "-e", default='utf-8',
                    action='store_true', help=' Specify an encoding'
                                              ' (other than utf-8)')
parser.add_argument('--betterconsole', "-b", default=False,
                    action='store_true', help='Use "better '
                    ' console" feature to anchor your imput at'
                    ' the bottom of the console (anti- scroll-away'
                    ' feature)')

parser.add_argument('--passphrase', "-p", type=str, default="wrong",
                    help='Passphrase used to encrypt sensitive information in '
                         'Wrapper.  Please use as fairly long phrase '
                         '(minimum is 8 characters).  If not specified, '
                         'or incorrectly supplied, Wrapper will prompt '
                         'for a new passphrase before starting! ')

args = parser.parse_args()

version = sys.version_info
VERSION = version[0]
SUBVER = version[1]
MICRO = version[2]

PY3 = VERSION > 2
MINSUB = 7
if PY3:
    MINSUB = 4


def main(wrapper_start_args):
    # same as old 'use-readline = True'
    better_console = wrapper_start_args.betterconsole
    encoding = wrapper_start_args.encoding

    config = getjsonfile("wrapper.properties", ".", encodedas=encoding)

    if config and "Misc" in config:
        if "use-betterconsole" in config["Misc"]:
            # use readline = not using better_console
            better_console = (config["Misc"]["use-betterconsole"])

    configure_logger(betterconsole=better_console)

    # develop master passphrase for wrapper
    secret_key = wrapper_start_args.passphrase
    if len(secret_key) < 8:
        secret_key = get_passphrase(
            'please input a master passphrase for Wrapper.  This passphrase '
            'will be used to encrypt sensitive information in Wrapper.\n>')

    # __init__ wrapper and set up logging
    wrapper = Wrapper(secret_key)
    log = wrapper.log

    # start first wrapper log entry
    log.info("Wrapper.py started - Version %s", wrapper.getbuildstring())
    log.debug("Wrapper is using Python %s.%s.%s.", VERSION, SUBVER, MICRO)

    # flag python version problems
    if SUBVER < MINSUB:
        log.warning(
            "You are using Python %s.%s.  There are Wrapper dependencies"
            " and methods that may require a minimum version of %s.%s."
            " Please press <y> and <Enter> to acknowledge and continue"
            " (anything else to exit)..." %
            (VERSION, SUBVER, VERSION, MINSUB))
        userstdin = sys.stdin.readline().strip()
        if userstdin.lower() != "y":
            print("bye..")
            sys.exit(1)

    # start wrapper
    # noinspection PyBroadException
    try:
        wrapper.start()

    except SystemExit:
        if not wrapper.configManager.exit:
            os.system("reset")
        wrapper.plugins.disableplugins()
        wrapper.alerts.ui_process_alerts(
            "Wrapper called SystemExit exception",
            blocking=True
        )

        # save-all is required to have a flush argument
        wrapper.javaserver.console("save-all flush")
        wrapper.javaserver.stop("Wrapper.py received shutdown signal - bye")
        wrapper.haltsig.halt = True

    except ImportWarning as ex:
        crash_mess = ("Wrapper.py Could not start due to missing requests "
                      "module: \n%s" % ex)
        wrapper.alerts.ui_process_alerts(crash_mess, blocking=True)
        log.critical(crash_mess)

    except Exception as ex:
        crash_mess = ("Wrapper crashed - stopping server to be safe (%s)" % ex)
        wrapper.alerts.ui_process_alerts(crash_mess, blocking=True)
        log.critical("Wrapper.py crashed - stopping server to be safe (%s)",
                     ex, exc_info=True)
        wrapper.haltsig.halt = True
        wrapper.plugins.disableplugins()
        try:
            wrapper.javaserver.stop("Wrapper.py crashed - please contact"
                                    " the server host as soon as possible")
        except AttributeError as exc:
            log.critical("Wrapper has no server instance. Server is likely "
                         "killed but could still be running, or it "
                         "might be corrupted! (%s)", exc, exc_info=True)


if __name__ == "__main__":
    main(args)
