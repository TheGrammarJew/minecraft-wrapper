# -*- coding: utf-8 -*-

# Copyright (C) 2016, 2017 - BenBaptist and Wrapper.py developer(s).
# https://github.com/benbaptist/minecraft-wrapper
# This program is distributed under the terms of the GNU
# General Public License, version 3 or later.

import time
import threading
import random
import datetime
import logging

from core.storage import Storage

try:
    from flask import Flask
except ImportError:
    Flask = False

if Flask:
    from flask import g, redirect, url_for, render_template, request, make_response, Response, Markup
    from flask_socketio import send, emit, join_room, leave_room


class Web(object):

    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.config = wrapper.config  # Remember if you need to save use 'wrapper.configManager.save()' not config.save
        self.log = logging.getLogger('Web')
        self.check_password = self.wrapper.cipher.check_pw()

        if not Flask:
            self.config["Web"]["web-enabled"] = False
            self.wrapper.configManager.save()
            self.log.critical("You don't have the 'flask/flask_socketio' dashboard dependencies installed "
                              "on your system. You can now restart, but Web mode is disabled.")
            self.wrapper.haltsig.halt = True

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = "".join([chr(random.randrange(48, 90)) for i in range(32)])  # LOL
        self.socketio = SocketIO(self.app)

        # Flask filters
        def strftime(f):
            return datetime.datetime.fromtimestamp(int(f)).strftime('%Y-%m-%d @ %I:%M%p')
            
        self.app.jinja_env.filters["strftime"] = strftime

        # Register handlers
        self.add_decorators()

        self.data_storage = Storage("dash")
        if "keys" not in self.data_storage.Data:
            self.data_storage.Data["keys"] = []

        self.loginAttempts = 0
        self.last_attempt = 0
        self.disableLogins = 0

        # Start thread for running server
        t = threading.Thread(target=self.run, args=())
        t.daemon = True
        t.start()

    def __del__(self):
        self.data_storage.close()

    # Authorization methods
    def check_login(self, password):
        if time.time() - self.disableLogins < 60:
            return False  # Threshold for logins
        if self.check_password(password, self.config["Web"]["web-password"]):
            return True
        self.loginAttempts += 1
        if self.loginAttempts > 10 and time.time() - self.last_attempt < 60:
            self.disableLogins = time.time()
            self.log.warning("Disabled login attempts for one minute")
        self.last_attempt = time.time()

    def make_key(self, rememberme):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@-_"
        a = "".join([random.choice(chars) for _i in range(64)])

        self.data_storage.Data["keys"].append([a, time.time(), rememberme])
        return a

    def validate_key(self):
        if "__wrapper_cookie" not in request.cookie:
            return False

        key = request.cookie["__wrapper_cookie"]
        for i in self.data_storage.Data["keys"]:
            expiretime = 7884000  # Three weeks old
            if len(i) > 2:
                if not i[2]:
                    expiretime = 21600
            # Validate key and ensure it's under the expiretime
            if i[0] == key and time.time() - i[1] < expiretime:
                self.loginAttempts = 0
                return True
        return False

    def remove_key(self, key):
        for i, v in enumerate(self.data_storage.Data["keys"]):
            if v[0] == key:
                del self.data_storage.Data["keys"][i]

    # Dectorators and misc.
    def add_decorators(self):
        @self.app.before_request
        def handle():
            print("I'm a freakin' sandwich dude!")

        @self.app.route("/")
        def index():
            return render_template("dashboard.html")

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            badpass = False
            if request.method == "POST":
                password = request.form["password"]
                rememberme = "remember" in request.form

                if self.check_login(password):
                    key = self.make_key(rememberme)
                    return redirect("/")
                    # self.log.warning("%s logged in to web mode (remember me: %s)", request.addr, rememberme)
                else:
                    badpass = True

            return render_template("login.html", badPass=badpass)

        @self.socketio.on('connect')
        def handle_connect():
            pass

        @self.socketio.on('disconnect')
        def handle_disconnect():
            pass

    def run(self, halt):
        while not self.wrapper.haltsig.halt:
            self.socketio.run(self.app, host=self.config["Web"]["web-bind"],
                          port=self.config["Web"]["web-port"])

        self.data_storage.close()
