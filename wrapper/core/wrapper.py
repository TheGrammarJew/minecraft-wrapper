# -*- coding: utf-8 -*-

# py3 non-compliant at runtime

import json
import signal
import hashlib
import threading
import time
import os
import logging
import socket
import sys  # used to pass sys.argv to server

import core.buildinfo as version_info
import proxy.base as proxy
import management.web as manageweb

from utils.helpers import getargs, getargsafter, readout
from api.base import API
from core.mcuuid import MCUUID
from core.config import Config
from core.irc import IRC
from core.mcserver import MCServer
from core.scripts import Scripts
from core.plugins import Plugins
from core.commands import Commands
from core.events import Events
from core.storage import Storage
from core.exceptions import UnsupportedOSException, InvalidServerStateError

# from management.dashboard import Web as Managedashboard  # presently unused

try:
    import readline
except ImportError:
    readline = False

try:
    import requests
except ImportError:
    requests = False

try:  # Manually define a raw input builtin that works indentically on PY2 and PY3
    rawinput = raw_input
except NameError:
    rawinput = input


class Wrapper:

    def __init__(self):
        self.log = logging.getLogger('Wrapper.py')
        self.configManager = Config()
        self.configManager.loadconfig()  # Load initially for storage object
        self.encoding = self.configManager.config["General"]["encoding"]  # This was to allow alternate encodings
        self.server = None
        self.api = None
        self.irc = None
        self.scripts = None
        self.web = None
        self.proxy = False
        self.halt = False
        self.update = False
        self.storage = Storage("main", encoding=self.encoding)
        self.permissions = Storage("permissions", encoding=self.encoding)
        self.usercache = Storage("usercache", encoding=self.encoding)

        self.plugins = Plugins(self)
        self.commands = Commands(self)
        self.events = Events(self)
        self.permission = {}
        self.help = {}
        self.config = {}

        if not readline:
            self.log.warning("'readline' not imported.")

        if not requests and self.configManager.config["Proxy"]["proxy-enabled"]:
            self.log.error("You must have the requests module installed to run in proxy mode!")
            return

    def isonlinemode(self):
        """
        :returns: Whether the server OR (for proxy mode) wrapper is in online mode.
        This should normally 'always' render True, unless you want hackers coming on :(
        not sure what circumstances you would want a different confguration...
        """
        if self.config["Proxy"]["proxy-enabled"]:
            # if wrapper is using proxy mode (which should be set to online)
            return self.config["Proxy"]["online-mode"]
        if self.server is not None:
            if self.server.onlineMode:
                return True  # if local server is online-mode
        return False

    @staticmethod
    def isipv4address(addr):
        try:
            socket.inet_aton(addr)  # Attempts to convert to an IPv4 address
        except socket.error:  # If it fails, the ip is not in a valid format
            return False
        return True

    @staticmethod
    def formatuuid(playeruuid):
        """
        Takes player's uuid with no dashes and returns it with the dashes
        :param playeruuid: string of player uuid with no dashes (such as you might get back from Mojang)
        :return: string hex format "8-4-4-4-12"
        """
        return MCUUID(bytes=playeruuid.decode("hex")).string

    @staticmethod
    def getuuidfromname(name):
        """
        :param name: should be passed as "OfflinePlayer:<playername>" to get the correct (offline) vanilla server uuid
        :return: a MCUUID object based on the name
        """
        m = hashlib.md5()
        m.update(name)
        d = bytearray(m.digest())
        d[6] &= 0x0f
        d[6] |= 0x30
        d[8] &= 0x3f
        d[8] |= 0x80
        return MCUUID(bytes=str(d))

    def accepteula(self):
        if os.path.isfile("eula.txt"):
            self.log.debug("Checking EULA agreement...")
            with open("eula.txt", "r") as f:
                eula = f.read()

            if "false" in eula:
                # if forced, should be at info level since acceptance is a legal matter.
                self.log.warning("EULA agreement was not accepted, accepting on your behalf...")
                with open("eula.txt", "w") as f:
                    f.write(eula.replace("false", "true"))

            self.log.debug("EULA agreement has been accepted.")

    def getuuidbyusername(self, username, forcepoll=False):
        """
        Lookup user's UUID using the username. Primarily searches the wrapper usercache.  If record is
        older than 30 days (or cannot be found in the cache), it will poll Mojang and also attempt a full
        update of the cache using getusernamebyuuid as well.

        :param username:  username as string
        :param forcepoll:  force polling even if record has been cached in past 30 days
        :returns: returns the online/Mojang MCUUID object from the given name. Updates the wrapper usercache.json
                Yields False if failed.
        """
        frequency = 2592000  # 30 days.
        if forcepoll:
            frequency = 3600  # do not allow more than hourly
        user_uuid_matched = None
        for useruuid in self.usercache:  # try wrapper cache first
            if username == self.usercache.key(useruuid)["localname"]:
                # This search need only be done by 'localname', which is always populated and is always
                # the same as the 'name', unless a localname has been assigned on the server (such as
                # when "falling back' on an old name).'''
                if (time.time() - self.usercache.key(useruuid)["time"]) < frequency:
                    return MCUUID(useruuid)
                # if over the time frequency, it needs to be updated by using actual last polled name.
                username = self.usercache.key(useruuid)["name"]
                user_uuid_matched = useruuid  # cache for later in case multiple name changes require a uuid lookup.

        # try mojang  (a new player or player changed names.)
        r = requests.get("https://api.mojang.com/users/profiles/minecraft/%s" % username)
        if r.status_code == 200:
            useruuid = self.formatuuid(r.json()["id"])  # returns a string uuid with dashes
            correctcapname = r.json()["name"]
            if username != correctcapname:  # this code may not be needed if problems with /perms are corrected.
                self.log.warning("%s's name is not correctly capitalized (offline name warning!)", correctcapname)
            # This should only run subject to the above frequency (hence use of forcepoll=True)
            nameisnow = self.getusernamebyuuid(useruuid, forcepoll=True)
            if nameisnow:
                return MCUUID(useruuid)
            return False
        elif r.status_code == 204:  # try last matching UUID instead.  This will populate current name back in 'name'
            if user_uuid_matched:
                nameisnow = self.getusernamebyuuid(user_uuid_matched, forcepoll=True)
                if nameisnow:
                    return MCUUID(user_uuid_matched)
                return False
        else:
            return False  # No other options but to fail request

    def getusernamebyuuid(self, useruuid, forcepoll=False):
        """
        Returns the username from the specified UUID.
        If the player has never logged in before and isn't in the user cache, it will poll Mojang's API.
        Polling is restricted to once per day.
        Updates will be made to the wrapper usercache.json when this function is executed.

        :param useruuid:  string UUID
        :param forcepoll:  force polling even if record has been cached in past 30 days.

        :returns: returns the username from the specified uuid, else returns False if failed.
        """
        frequency = 2592000  # if called directly, can update cache daily (refresh names list, etc)
        if forcepoll:
            frequency = 600  # 10 minute limit
        names = self._pollmojanguuid(useruuid)
        numbofnames = len(names)
        if self.usercache.key(useruuid):  # if user is in the cache...
            # and was recently polled...
            if int((time.time() - self.usercache.key(useruuid)["time"])) < frequency:
                return self.usercache.key(useruuid)["name"]  # dont re-poll if same time frame (daily = 86400).
            else:
                if not names or names is None:  # service might be down.. not a huge deal, we'll re-poll another time
                    self.usercache.key(useruuid)["time"] = time.time() - frequency + 7200  # may try again in 2 hours
                    return self.usercache.key(useruuid)["name"]
                # continue on and poll... because user is not in cache or is old record that needs re-polled
        # else:  # user is not in cache
        if not names or names is None or numbofnames == 0:  # mojang service failed or UUID not found
            return False
        pastnames = []
        if useruuid not in self.usercache:
            self.usercache[useruuid] = {
                "time": time.time(),
                "original": None,
                "name": None,
                "online": True,
                "localname": None,
                "IP": None,
                "names": []
            }
        for i in range(0, numbofnames):
            if "changedToAt" not in names[i]:  # find the original name
                self.usercache[useruuid]["original"] = names[i]["name"]
                self.usercache[useruuid]["online"] = True
                self.usercache[useruuid]["time"] = time.time()
                if numbofnames == 1:  # The user has never changed their name
                    self.usercache[useruuid]["name"] = names[i]["name"]
                    if self.usercache[useruuid]["localname"] is None:
                        self.usercache[useruuid]["localname"] = names[i]["name"]
                    break
            else:
                # Convert java milleseconds to time.time seconds
                changetime = names[i]["changedToAt"] / 1000
                oldname = names[i]["name"]
                if len(pastnames) == 0:
                    pastnames.append({"name": oldname, "date": changetime})
                    continue
                if changetime > pastnames[0]["date"]:
                    pastnames.insert(0, {"name": oldname, "date": changetime})
                else:
                    pastnames.append({"name": oldname, "date": changetime})
        self.usercache[useruuid]["names"] = pastnames
        if numbofnames > 1:
            self.usercache[useruuid]["name"] = pastnames[0]["name"]
            if self.usercache[useruuid]["localname"] is None:
                self.usercache[useruuid]["localname"] = pastnames[0]["name"]
        return self.usercache[useruuid]["localname"]

    def _pollmojanguuid(self, useruuid):
        """
        attempts to poll Mojang with the UUID
        :param useruuid: string uuid with dashes
        :returns:
                None - Most likely a bad UUID
                False - Mojang down or operating in limited fashion
                - otherwise, a list of names...
        """

        r = requests.get("https://api.mojang.com/user/profiles/%s/names" % useruuid.replace("-", ""))
        if r.status_code == 200:
            return r.json()
        else:
            rx = requests.get("https://status.mojang.com/check")
            if rx.status_code == 200:
                rx = rx.json()
                for i in range(0, len(rx)):
                    if "account.mojang.com" in rx[i]:
                        if rx[i]["account.mojang.com"] == "green":
                            self.log.warning("Mojang accounts is green, but request failed - have you "
                                             "over-polled (large busy server) or supplied an incorrect UUID??")
                            self.log.warning("uuid: %s", useruuid)
                            self.log.warning("response: \n%s", str(rx))
                            return None
                        elif rx[i]["account.mojang.com"] in ("yellow", "red"):
                            self.log.warning("Mojang accounts is experiencing issues (%s).",
                                             rx[i]["account.mojang.com"])
                            return False
                        self.log.warning("Mojang Status found, but corrupted or in an unexpected format (status "
                                         "code %s)", r.status_code)
                        return False
                    else:
                        self.log.warning("Mojang Status not found - no internet connection, perhaps? "
                                         "(status code %s)", rx.status_code)
                        return self.usercache[useruuid]["name"]
            
    def getusername(self, arguseruuid):  # We should see about getting rid of this wrapper
        """
        :param arguseruuid - the string or MCUUID representation of the player uuid.

        used by commands.py in commands-playerstats and in api/minecraft.getAllPlayers
        mostly a wrapper for getusernamebyuuid which also checks the offline server usercache...
        """
        if "MCUUID" in str(type(arguseruuid)):
            useruuid = arguseruuid.string
        else:
            useruuid = arguseruuid

        if self.isonlinemode():
            name = self.getusernamebyuuid(useruuid)
            if name:
                return self.usercache[useruuid]["localname"]
            return False
        else:
            # this is the server's usercache.json (not the cache in wrapper-data)
            with open("usercache.json", "r") as f:
                cache = json.loads(f.read())
            for user in cache:
                if user["uuid"] == useruuid:
                    if useruuid not in self.usercache:
                        self.usercache[useruuid] = {
                            "time": time.time(), 
                            "name": None
                        }
                    if user["name"] != self.usercache[useruuid]["name"]:
                        self.usercache[useruuid]["name"] = user["name"]
                        self.usercache[useruuid]["online"] = False
                        self.usercache[useruuid]["time"] = time.time()
                    return user["name"]

    def getuuid(self, username):  # We should see about getting rid of this wrapper  # agreed!
        pass
    # """
#        :param username - string of user's name
#        :returns a MCUUID object, which means UUIDfromname and getuuidbyusername must return MCUUID obejcts
#        """
#        if not self.isonlinemode():  # both server and wrapper in offline...
#            return self.getuuidfromname("OfflinePlayer:%s" % username)
#
#        # proxy mode is off / not working
#        if not self.proxy:
#            with open("usercache.json", "r") as f:  # read offline server cache first
#                cache = json.loads(f.read())
#            for user in cache:
#                if user["name"] == username:
#                    return MCUUID(user["uuid"])
#        else:
#            # proxy mode is on... poll mojang and wrapper cache
#            search = self.getuuidbyusername(username)
#            if not search:
#                self.log.warning("Server online but unable to getuuid (even by polling!) for username: %s - "
#                                 "returned an Offline uuid...", username)
#                return self.getuuidfromname("OfflinePlayer:%s" % username)
#            else:
#                return search
#        # if both if and else fail to deliver a uuid create offline uuid:
#        return self.getuuidfromname("OfflinePlayer:%s" % username)

    def listplugins(self):
        self.log.info("List of Wrapper.py plugins installed:")
        for plid in self.plugins:
            plugin = self.plugins[plid]
            if plugin["good"]:
                name = plugin["name"]
                summary = plugin["summary"]
                if summary is None:
                    summary = "No description available for this plugin"

                version = plugin["version"]
                readout(name, summary, separator=(" - v%s - " % ".".join([str(_) for _ in version])))
                # self.log.info("%s v%s - %s", name, ".".join([str(_) for _ in version]), summary)
            else:
                self.log.info("%s failed to load!", plugin)

    def start(self):
        # Reload configuration each time server starts in order to detect changes
        self.configManager.loadconfig()
        self.config = self.configManager.config

        signal.signal(signal.SIGINT, self.sigint)
        signal.signal(signal.SIGTERM, self.sigint)

        self.api = API(self, "Wrapper.py")
        self._registerwrappershelp()

        # This is not the actual server... the MCServer class is
        self.server = MCServer(sys.argv, self.log, self.configManager.config, self)
        self.server.init()

        self.plugins.loadplugins()

        if self.config["IRC"]["irc-enabled"]:
            self.irc = IRC(self.server, self.config, self.log, self)
            t = threading.Thread(target=self.irc.init, args=())
            t.daemon = True
            t.start()

        if self.config["Web"]["web-enabled"]:
            if manageweb.pkg_resources and manageweb.requests:
                self.web = manageweb.Web(self)
                t = threading.Thread(target=self.web.wrap, args=())
                t.daemon = True
                t.start()
            else:
                self.log.error("Web remote could not be started because you do not have the required modules "
                               "installed: pkg_resources")
                self.log.error("Hint: http://stackoverflow.com/questions/7446187")

        if len(sys.argv) < 2:
            self.server.args = self.configManager.config["General"]["command"].split(" ")
        else:
            # I think this allows you to run the server java command directly from the python prompt
            self.server.args = sys.argv[1:]

        consoledaemon = threading.Thread(target=self.console, args=())
        consoledaemon.daemon = True
        consoledaemon.start()

        t = threading.Thread(target=self.timer, args=())
        t.daemon = True
        t.start()

        if self.config["General"]["shell-scripts"]:
            if os.name in ("posix", "mac"):
                self.scripts = Scripts(self)
            else:
                self.log.error("Sorry, but shell scripts only work on *NIX-based systems! If you are using a "
                               "*NIX-based system, please file a bug report.")

        if self.config["Proxy"]["proxy-enabled"]:
            t = threading.Thread(target=self.startproxy, args=())
            t.daemon = True
            t.start()

        if self.config["General"]["auto-update-wrapper"]:
            t = threading.Thread(target=self.checkfordevupdate, args=())
            t.daemon = True
            t.start()

        self.server.__handle_server__()
        self.plugins.disableplugins()

    def startproxy(self):
        self.proxy = proxy.Proxy(self)
        if proxy.requests:  # requests will be set to False if requests or any crptography is missing.
            proxythread = threading.Thread(target=self.proxy.host, args=())
            proxythread.daemon = True
            proxythread.start()
        else:
            self.log.error("Proxy mode could not be started because you do not have one or more of the following "
                           "modules installed: pycrypto and requests")

    def sigint(*args):  # doing this allows the calling function to pass extra args without defining/using them here
        self = args[0]  # .. as we are onnly interested in the self component
        self.shutdown()

    def shutdown(self, status=0):
        self.halt = True
        self.server.stop(reason="Wrapper.py Shutting Down", save=False)
        time.sleep(1)
        sys.exit(status)

    def reboot(self):
        self.halt = True
        os.system(" ".join(sys.argv) + "&")

    @staticmethod
    def getbuildstring():
        if version_info.__branch__ == "dev":
            return "%s (development build #%d)" % (version_info.__version__, version_info.__build__)
        else:
            return "%s (stable)" % version_info.__version__

    def checkfordevupdate(self):
        if not requests:
            self.log.error("Can't automatically check for new Wrapper.py versions because you do not have the "
                           "requests module installed!")
            return
        while not self.halt:
            time.sleep(3600)
            self.checkforupdate(True)

    def checkforupdate(self, auto):
        self.log.info("Checking for new builds...")
        update = self.getwrapperupdate()
        if update:
            version, build, repotype = update
            if repotype == "dev":
                if auto and not self.config["General"]["auto-update-dev-build"]:
                    self.log.info("New Wrapper.py development build #%d available for download! (currently on #%d)",
                                  build, version_info.__build__)
                    self.log.info("Because you are running a development build, you must manually update "
                                  "Wrapper.py. To update Wrapper.py manually, please type /update-wrapper.")
                else:
                    self.log.info("New Wrapper.py development build #%d available! Updating... (currently on #%d)",
                                  build, version_info.__build__)
                self.performupdate(version, build, repotype)
            else:
                self.log.info("New Wrapper.py stable %s available! Updating... (currently on %s)",
                              ".".join([str(_) for _ in version]), version_info.__version__)
                self.performupdate(version, build, repotype)
        else:
            self.log.info("No new versions available.")

    def getwrapperupdate(self, repotype=None):
        if repotype is None:
            repotype = version_info.__branch__
        if repotype == "dev":
            r = requests.get("https://raw.githubusercontent.com/benbaptist/minecraft-wrapper/development/build/"
                             "version.json")
            if r.status_code == 200:
                data = r.json()
                if self.update:
                    if self.update > data["build"]:
                        return False
                if data["build"] > version_info.__build__ and data["repotype"] == "dev":
                    return data["version"], data["build"], data["repotype"]
                else:
                    return False
            else:
                self.log.warning("Failed to check for updates - are you connected to the internet? "
                                 "(Status Code %d)", r.status_code)
                
        else:
            r = requests.get("https://raw.githubusercontent.com/benbaptist/minecraft-wrapper/master/build/"
                             "version.json")
            if r.status_code == 200:
                data = r.json()
                if self.update:
                    if self.update > data["build"]:
                        return False
                if data["build"] > version_info.__build__ and data["repotype"] == "stable":
                    return data["version"], data["build"], data["repotype"]
                else:
                    return False
            else:
                self.log.warning("Failed to check for updates - are you connected to the internet? (Status Code %d)",
                                 r.status_code)
        return False

    def performupdate(self, version, build, repotype):
        if repotype == "dev":
            repo = "development"
        else:
            repo = "master"
        wrapperhash = requests.get("https://raw.githubusercontent.com/benbaptist/minecraft-wrapper/%s/build"
                                   "/Wrapper.py.md5" % repo)
        wrapperfile = requests.get("https://raw.githubusercontent.com/benbaptist/minecraft-wrapper/%s/Wrapper.py"
                                   % repo)
        if wrapperhash.status_code == 200 and wrapperfile.status_code == 200:
            self.log.info("Verifying Wrapper.py...")
            if hashlib.md5(wrapperfile.content).hexdigest() == wrapperhash.text:
                self.log.info("Update file successfully verified. Installing...")
                with open(sys.argv[0], "w") as f:
                    f.write(wrapperfile)
                self.log.info("Wrapper.py %s (#%d) installed. Please reboot Wrapper.py.",
                              ".".join([str(_) for _ in version]), build)
                self.update = build
                return True
            else:
                return False
        else:
            self.log.error("Failed to update due to an internal error (%d, %d)", wrapperhash.status_code,
                           wrapperfile.status_code, exc_info=True)
            return False

    def timer(self):
        t = time.time()
        while not self.halt:
            if time.time() - t > 1:
                self.events.callevent("timer.second", None)
                t = time.time()
            time.sleep(0.05)

    def console(self):
        while not self.halt:
            try:
                consoleinput = rawinput("")
            except Exception as e:
                print("[continue] variable 'consoleinput' in 'console()' did not evaluate \n%s" % e)
                continue

            if len(consoleinput) < 1:
                continue

            command = getargs(consoleinput[0:].split(" "), 0)

            if command in ("/halt", "halt"):
                self.server.stop("Halting server...", save=False)
                self.halt = True
                sys.exit()
            elif command in ("/stop", "stop"):
                self.server.stop("Stopping server...")
            elif command in ("/start", "start"):
                self.server.start()
            elif command == "/restart":
                self.server.restart("Server restarting, be right back!")
            elif command == "/reload":
                self.plugins.reloadplugins()
                if self.server.getservertype() != "vanilla":
                    self.log.info("Note: If you meant to reload the server's plugins instead of the Wrapper's "
                                  "plugins, try running 'reload' without any slash OR '/raw /reload'.")
            elif command in ("/update-wrapper", "update-wrapper"):
                self.checkforupdate(False)
            elif command in ("/plugins", "plugins"):
                self.listplugins()
            elif command in ("/mem", "/memory", "mem", "memory"):
                try:
                    self.log.info("Server Memory Usage: %d bytes", self.server.getmemoryusage())
                except UnsupportedOSException as e:
                    self.log.error(e)
                except Exception as ex:
                    self.log.exception("Something went wrong when trying to fetch memory usage! (%s)", ex)
            elif command in ("/raw", "raw"):
                try:
                    if len(getargsafter(consoleinput[1:].split(" "), 1)) > 0:
                        self.server.console(getargsafter(consoleinput[1:].split(" "), 1))
                    else:
                        self.log.info("Usage: /raw [command]")
                except InvalidServerStateError as e:
                    self.log.warning(e)
            elif command in ("/freeze", "freeze"):
                try:
                    self.server.freeze()
                except InvalidServerStateError as e:
                    self.log.warning(e)
                except UnsupportedOSException as ex:
                    self.log.error(ex)
                except Exception as exc:
                    self.log.exception("Something went wrong when trying to freeze the server! (%s)", exc)
            elif command in ("/unfreeze", "unfreeze"):
                try:
                    self.server.unfreeze()
                except InvalidServerStateError as e:
                    self.log.warning(e)
                except UnsupportedOSException as ex:
                    self.log.error(ex)
                except Exception as exc:
                    self.log.exception("Something went wrong when trying to unfreeze the server! (%s)", exc)
            elif command == "/version":
                readout("/version", self.getbuildstring())
            elif command == "help":
                readout("/help", "Get wrapper.py help.", separator=" (with a slash) - ")
                self.server.console(consoleinput)
            elif command == "/help":
                # This is the console help commands.  Below this in _registerwrappershelp is the in-game help
                readout("", "Get Minecraft help.", separator="help (with no slash) - ")
                readout("/reload", "Reload Wrapper.py plugins.")
                readout("/plugins", "Lists Wrapper.py plugins.")
                readout("/update-wrapper", "Checks for new Wrapper.py updates, and will install\n"
                                           "                  them automatically if one is available.")
                readout("/stop", "Stop the minecraft server without auto-restarting and without\n"
                                 "                  shuttingdown Wrapper.py.")
                readout("/start", "Start the minecraft server.")
                readout("/restart", "Restarts the minecraft server.")
                readout("/halt", "Shutdown Wrapper.py completely.")
                readout("/freeze", "Temporarily locks the server up until /unfreeze is executed\n"
                                   "                  (Only works on *NIX servers).")
                readout("/unfreeze", "Unlocks a frozen state server (Only works on *NIX servers).")
                readout("/mem", "Get memory usage of the server (Only works on *NIX servers).")
                readout("/raw [command]", "Send command to the Minecraft Server. Useful for Forge\n"
                                          "                  commands like '/fml confirm'.")
                readout("/version", self.getbuildstring())
            else:
                try:
                    self.server.console(consoleinput)
                except Exception as e:
                    print("[BREAK] Console input exception (nothing passed to server) \n%s" % e)
                    break
                continue

    def _registerwrappershelp(self):
        # All commands listed herein are accessible in-game
        # Also require player.isOp()
        self.api.registerHelp("Wrapper", "Internal Wrapper.py commands ", [
            ("/wrapper [update/memory/halt]",
             "If no subcommand is provided, it will show the Wrapper version.",
             None),
            ("/playerstats [all]",
             "Show the most active players. If no subcommand is provided, it'll show the top 10 players.",
             None),
            ("/plugins",
             "Show a list of the installed plugins",
             None),
            ("/reload",
             "Reload all plugins.",
             None),
            ("/permissions <groups/users/RESET>",
             "Command used to manage permission groups and users, add permission nodes, etc.",
             None),
            ("/ban <name> [reason..] [time <h/d>]",
             "Using a time creates a temp ban - (h)ours or (d)ays. Default is days(d)",
             "mc1.7.6"),  # Minimum server version for commands to appear (register default perm later in code)
            ("/ban-ip <address|name> [reason..] [time <h/d> (hours or days)",
             "Reason and time optional. Default unit is days",
             "mc1.7.6"),
            ("/pardon <name>",
             "pardon player 'name'. ",
             "mc1.7.6"),
            ("/banlist [players|ips|search] [args]",
             "search/display banlist",
             "mc1.7.6"),
            ("/pardon-ip <address>",
             "Pardon address",
             "mc1.7.6")
        ])
