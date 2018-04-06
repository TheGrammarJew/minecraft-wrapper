# -*- coding: utf-8 -*-

# Copyright (C) 2016, 2017 - BenBaptist and Wrapper.py developer(s).
# https://github.com/benbaptist/minecraft-wrapper
# This program is distributed under the terms of the GNU
# General Public License, version 3 or later.

# Mincraft version constants
# use these constants decide how a packet should be parsed.

# Still in development at versions 201-210(6/14/16)

# def Wrapper.py Constants:
# """
PROTOCOL_MAX = 4000

PROTOCOL_PRE_RELEASE = 368

PROTOCOL_1_12_2END = 340
PROTOCOL_1_12_2 = 340
PROTOCOL_1_12_2START = 339

PROTOCOL_1_12_1END = 338
PROTOCOL_1_12_1 = 336
PROTOCOL_1_12_1START = 336

PROTOCOL_1_12END = 335
PROTOCOL_1_12 = 334
PROTOCOL_1_12START = 332

# Between 317-332, the protocol is highly unstable again.
PROTOCOL_1_11END = 317
PROTOCOL_1_11 = 314

# Missing 211-300
PROTOCOL_1_10END = 210
PROTOCOL_1_10 = 205

# Missing 111-200
# post- 1.9.3 "pre" releases (1.9.3 pre-2 -)
PROTOCOL_1_9_4 = 110

# PAGE: http://wiki.vg/index.php?title=Protocol&oldid=7817
# post- 1.9 "pre" releases (1.9.2 - 1.9.3 pre-1)
PROTOCOL_1_9_3PRE3 = 109

# PAGE: http://wiki.vg/index.php?title=Protocol&oldid=7617
# post- 1.9 "pre" releases (1.9.1 pre-3 through 1.9.1)
PROTOCOL_1_9_1PRE = 108
# first stable 1.9 release
PROTOCOL_1_9REL1 = 107

# Between 49-106, the protocol is incredibly unstable.
# Packet numbers changed almost weekly.  using a version in this range
# is not supported

# start of 1.9 snapshots
PROTOCOL_1_9START = 48

# PAGE: http://wiki.vg/index.php?title=Protocol&oldid=7368
# 1.8.9
PROTOCOL_1_8END = 47
# 1.8 snapshots start- #
PROTOCOL_1_8START = 6

# PAGE: http://wiki.vg/index.php?title=Protocol&oldid=6003
# 1.7.6 - 1.7.10
PROTOCOL_1_7_9 = 5

# PAGE: http://wiki.vg/index.php?title=Protocol&oldid=5486
# 1.7.1-pre to 1.7.5
PROTOCOL_1_7 = 4

# coallate unsupprted protocols
UNSUPPORTED = list(range(6, 43, 1))
UNSUPPORTED = UNSUPPORTED + list(range(PROTOCOL_1_9START, PROTOCOL_1_9REL1, 1))
UNSUPPORTED = UNSUPPORTED + list(range(111, 201, 1))
UNSUPPORTED = UNSUPPORTED + list(range(211, 301, 1))
UNSUPPORTED = UNSUPPORTED + list(range(PROTOCOL_1_11END, PROTOCOL_1_12START, 1))
UNSUPPORTED = UNSUPPORTED + list(range(341, 367, 1))

"""Minecraft version 1.6.4 and older used a protocol versioning
scheme separate from the current one. Accordingly, an old protocol
version number may ambiguously refer to an one of those old versions
and from the list above.  Do not run a 1.6.4 server with proxy mode."""

# parser constants
PKT = 0
PARSER = 1

# Data constants
# ------------------------------------------------

STRING = 0
JSON = 1
UBYTE = 2
BYTE = 3
INT = 4
SHORT = 5
USHORT = 6
LONG = 7
DOUBLE = 8
FLOAT = 9
BOOL = 10
VARINT = 11
BYTEARRAY = 12
BYTEARRAY_SHORT = 13
POSITION = 14

# gets full slot info, including NBT data.
SLOT = 15

# This fellow is a bit of a hack that allows getting the
# basic slot data where the NBT part may be buggy or
#  you are not sure you are correctly parsing the NBT
# data (like in older pre-1.8 minecrafts).
SLOT_NO_NBT = 18

UUID = 16

# this is the old pre-1.9 metadata parsing.
METADATA = 17
# It is radically different in 1.9+ now (through 11.2 atm)
METADATA_1_9 = 19

# upgrade for something that always existed:
# this actually processes a VARINT and then the number of STRING.
#       read returns: list of strings.
#       send: accepts a list of strings.
STRING_ARRAY = 20

# Both of these just read or send the rest of the packet in its raw bytes form.
REST = 90
RAW = 90

# allows the insertion of padding into argument lists.
# Any field with this designation is just silently skipped.
NULL = 100

# server state definitions
# Constants used in client and server connections

# Handshake is the default mode of a server awaiting packets from a
# client.  Client will send a handshake (a 0x00 packet WITH payload)
# asking for STATUS or LOGIN mode.  This mode is n/a to
# serverconnection.py, which starts in LOGIN mode
HANDSHAKE = 0
OFFLINE = 0  # an alias of Handshake.

# Not used by serverconnection.py. clientconnection.py handles
# PING/MOTD functions  Status mode will await either a ping (0x01)
# containing a unique long int and will respond with same integer...
#  OR if it receives a 0x00 packet (with no payload), that signals
# server (client.py) to send the MOTD json response packet.  The
# ping will follow the 0x00 request for json response.  The ping
# will set wrapper/server back to HANDSHAKE mode (to await
# the next handshake).
MOTD = 1
STATUS = 1

LOGIN = 2  # login state
PLAY = 3  # play state
LOBBY = 4  # lobby state (remote server)
IDLE = 5  # no parsing at all; just keeping client suspended
