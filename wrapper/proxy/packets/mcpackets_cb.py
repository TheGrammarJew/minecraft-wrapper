# -*- coding: utf-8 -*-

# Copyright (C) 2016, 2017 - BenBaptist and Wrapper.py developer(s).
# https://github.com/benbaptist/minecraft-wrapper
# This program is distributed under the terms of the GNU
# General Public License, version 3 or later.

from __future__ import print_function
from proxy.utils.constants import *

"""
Ways to reference packets by names and not hard-coded numbers.

This attempts to follow the wiki as much as possible.

the ServerBound and ClientBound classes take an integer protocol argument
to determine the packet values.

Protocol constants are named as follows:
    first two digits are major version, third digit in minor version.
    example: PROTOCOL_1_8_9 means - version 1.8.9.
    Explanatory text (pre, start, etc) may be last.

set something False/unimplemented using 0xEE

"""


class Packets(object):
    def __init__(self, protocol):
        # not supporting 1.9 and 1.12 snapshots due to high instability/changes
        if protocol in UNSUPPORTED:
            print("Protocol version not supported:", protocol)
            raise ValueError

        # Login, Status, and Ping packets
        # -------------------------------
        self.LOGIN_DISCONNECT = 0x00
        self.LOGIN_ENCR_REQUEST = 0x01
        self.LOGIN_SUCCESS = 0x02
        self.LOGIN_SET_COMPRESSION = 0X03

        # the json data represented as a string
        self.PING_JSON_RESPONSE = 0x00
        # PONG sent in response to Client PING
        self.PING_PONG = 0x01

        # play mode packets
        # -------------------------------
        # Base set 1.7 - 1.8.9 - The packet numbers were the same,
        # although parsing differed amongst versions
        self.KEEP_ALIVE = [0x00, [INT]]
        self.JOIN_GAME = [0x01, [INT, UBYTE, BYTE, UBYTE, UBYTE, STRING]]
        self.CHAT_MESSAGE = [0x02, [STRING, NULL]]
        self.TIME_UPDATE = 0x03
        self.ENTITY_EQUIPMENT = 0x04
        self.SPAWN_POSITION = 0x05
        self.UPDATE_HEALTH = 0x06
        self.RESPAWN = 0x07

        self.PLAYER_POSLOOK = [0x08, [DOUBLE, DOUBLE, DOUBLE, FLOAT, FLOAT, BOOL]]
        if protocol > PROTOCOL_1_7_9:
            self.PLAYER_POSLOOK[PARSER] = [DOUBLE, DOUBLE, DOUBLE, FLOAT, FLOAT,
                                           BYTE]
        self.HELD_ITEM_CHANGE = 0x09
        self.USE_BED = 0x0a
        self.ANIMATION = 0x0b
        self.SPAWN_PLAYER = 0x0c
        self.COLLECT_ITEM = 0x0d
        self.SPAWN_OBJECT = 0x0e
        self.SPAWN_MOB = 0x0f
        self.SPAWN_PAINTING = 0x10
        self.SPAWN_EXPERIENCE_ORB = 0x11
        self.ENTITY_VELOCITY = 0x12
        self.DESTROY_ENTITIES = 0x13
        self.ENTITY = 0x14
        self.ENTITY_RELATIVE_MOVE = 0x15
        self.ENTITY_LOOK = 0x16
        self.ENTITY_LOOK_AND_RELATIVE_MOVE = 0x17
        self.ENTITY_TELEPORT = 0x18
        self.ENTITY_HEAD_LOOK = 0x19
        self.ENTITY_STATUS = 0x1a
        self.ATTACH_ENTITY = 0x1b
        # [VARINT, METADATA]  This one and NBT things are broke in 1.7
        self.ENTITY_METADATA = [0x1c, [VARINT, RAW]]
        self.ENTITY_EFFECT = 0x1d
        self.REMOVE_ENTITY_EFFECT = 0x1e
        self.SET_EXPERIENCE = 0x1f
        self.ENTITY_PROPERTIES = 0x20
        self.CHUNK_DATA = 0x21
        self.MULTI_BLOCK_CHANGE = 0x22
        self.BLOCK_CHANGE = 0x23
        self.BLOCK_ACTION = 0x24
        self.BLOCK_BREAK_ANIMATION = 0x25
        self.MAP_CHUNK_BULK = 0x26
        self.EXPLOSION = 0x27
        self.EFFECT = 0x28
        self.SOUND_EFFECT = 0x29
        self.PARTICLE = 0x2a
        self.CHANGE_GAME_STATE = 0x2b
        self.SPAWN_GLOBAL_ENTITY = 0x2c
        self.OPEN_WINDOW = [0x2d, [UBYTE, UBYTE, STRING, UBYTE]]
        self.CLOSE_WINDOW = 0x2e
        self.SET_SLOT = [0x2f, [BYTE, SHORT, SLOT_NO_NBT]]
        self.WINDOW_ITEMS = 0x30
        self.WINDOW_PROPERTY = 0x31
        self.CONFIRM_TRANSACTION = 0x32
        self.UPDATE_SIGN = 0x33
        self.MAP = 0x34
        self.UPDATE_BLOCK_ENTITY = 0x35
        self.OPEN_SIGN_EDITOR = 0x36
        self.STATISTICS = 0x37
        self.PLAYER_LIST_ITEM = 0x38
        self.PLAYER_ABILITIES = 0x39
        self.TAB_COMPLETE = 0x3a
        self.SCOREBOARD_OBJECTIVE = 0x3b
        self.UPDATE_SCORE = 0x3c
        self.DISPLAY_SCOREBOARD = 0x3d
        self.TEAMS = 0x3e
        self.PLUGIN_MESSAGE = 0x3F
        self.DISCONNECT = 0x40
        # protocol 4-5 ends at 0x40
        # self.PACKET_THAT_EXISTS_IN_OTHER_PROTOCOLS_BUT_NOT_THIS_ONE = 0xee

        # new to 1.8 (protocol 47)
        self.SERVER_DIFFICULTY = 0xee
        self.COMBAT_EVENT = 0xee
        self.CAMERA = 0xee
        self.WORLD_BORDER = 0xee
        self.TITLE = 0xee
        self.BROKEN_SET_COMPRESSION_REMOVED1_9 = 0xee
        self.PLAYER_LIST_HEADER_AND_FOOTER = 0xee
        self.RESOURCE_PACK_SEND = 0xee
        self.UPDATE_ENTITY_NBT = 0xee

        # NEW to 1.9
        # ALL VERSIONS handle chunk unloading DIFFERENTLY - CAVEAT EMPTOR!
        self.UNLOAD_CHUNK = 0xee
        self.NAMED_SOUND_EFFECT = 0xee
        self.BOSS_BAR = 0xee
        self.SET_COOLDOWN = 0xee
        self.VEHICLE_MOVE = 0xee
        self.SET_PASSENGERS = 0xee

        # NEW to 1.12
        self.UNLOCK_RECIPES = 0xee
        self.SELECT_ADVANCEMENT_TAB = 0xee
        self.ADVANCEMENTS = 0xee

        # 1.8 changes
        if protocol >= PROTOCOL_1_8START:
            self.SERVER_DIFFICULTY = 0x41
            self.COMBAT_EVENT = 0x42
            self.CAMERA = 0x43
            self.WORLD_BORDER = 0x44
            self.TITLE = 0x45
            self.BROKEN_SET_COMPRESSION_REMOVED1_9 = 0x46
            self.PLAYER_LIST_HEADER_AND_FOOTER = 0x47
            self.RESOURCE_PACK_SEND = 0x48
            self.UPDATE_ENTITY_NBT = 0x49

            # Parsing changes
            self.KEEP_ALIVE[PARSER] = [VARINT]
            self.CHAT_MESSAGE[PARSER] = [JSON, BYTE]
            self.OPEN_WINDOW[PARSER] = [UBYTE, STRING, JSON, UBYTE]
            self.SET_SLOT[PARSER] = [BYTE, SHORT, SLOT]
            self.ENTITY_METADATA[PARSER] = [VARINT, METADATA]

        # 1.9 changes
        if protocol >= PROTOCOL_1_9REL1:
            self.SPAWN_OBJECT = 0x00
            self.SPAWN_EXPERIENCE_ORB = 0x01
            self.SPAWN_GLOBAL_ENTITY = 0x02
            self.SPAWN_MOB = 0x03
            self.SPAWN_PAINTING = 0x04
            self.SPAWN_PLAYER = 0x05
            self.ANIMATION = 0x06
            self.STATISTICS = 0x07
            self.BLOCK_BREAK_ANIMATION = 0x08
            self.UPDATE_BLOCK_ENTITY = 0x09
            self.BLOCK_ACTION = 0x0a
            self.BLOCK_CHANGE = 0x0b
            self.BOSS_BAR = 0x0c  # TODO NEW
            self.SERVER_DIFFICULTY = 0x0d
            self.TAB_COMPLETE = 0x0e
            self.CHAT_MESSAGE[PKT] = 0x0f
            self.MULTI_BLOCK_CHANGE = 0x10
            self.CONFIRM_TRANSACTION = 0x11
            self.CLOSE_WINDOW = 0x12
            self.OPEN_WINDOW[PKT] = 0x13
            self.WINDOW_ITEMS = 0x14
            self.WINDOW_PROPERTY = 0x15
            self.SET_SLOT[PKT] = 0x16
            self.SET_COOLDOWN = 0x17  # TODO NEW
            self.PLUGIN_MESSAGE = 0x18
            self.NAMED_SOUND_EFFECT = 0x19  # TODO NEW
            self.DISCONNECT = 0x1a
            self.ENTITY_STATUS = 0x1b
            self.EXPLOSION = 0x1c
            # ALL VERSIONS handle chunk unloading DIFFERENTLY - CAVEAT EMPTOR!
            self.UNLOAD_CHUNK = 0x1d  # TODO NEW
            self.CHANGE_GAME_STATE = 0x1e
            self.KEEP_ALIVE[PKT] = 0x1f
            self.CHUNK_DATA = 0x20
            self.EFFECT = 0x21
            self.PARTICLE = 0x22
            self.JOIN_GAME[PKT] = 0x23
            self.MAP = 0x24
            self.ENTITY_RELATIVE_MOVE = 0x25
            self.ENTITY_LOOK_AND_RELATIVE_MOVE = 0x26
            self.ENTITY_LOOK = 0x27
            self.ENTITY = 0x28
            self.VEHICLE_MOVE = 0x29  # TODO NEW
            self.OPEN_SIGN_EDITOR = 0x2a
            self.PLAYER_ABILITIES = 0x2b
            self.COMBAT_EVENT = 0x2c
            self.PLAYER_LIST_ITEM = 0x2d
            self.PLAYER_POSLOOK = [0x2e, [DOUBLE, DOUBLE, DOUBLE, FLOAT, FLOAT,
                                          BYTE, VARINT]]

            self.USE_BED = 0x2f
            self.DESTROY_ENTITIES = 0x30
            self.REMOVE_ENTITY_EFFECT = 0x31
            self.RESOURCE_PACK_SEND = 0x32
            self.RESPAWN = 0x33
            self.ENTITY_HEAD_LOOK = 0x34
            self.WORLD_BORDER = 0x35
            self.CAMERA = 0x36
            self.HELD_ITEM_CHANGE = 0x37
            self.DISPLAY_SCOREBOARD = 0x38
            self.ENTITY_METADATA = [0x39, [VARINT, METADATA_1_9]]
            self.ATTACH_ENTITY = 0x3a
            self.ENTITY_VELOCITY = 0x3b
            self.ENTITY_EQUIPMENT = 0x3c
            self.SET_EXPERIENCE = 0x3d
            self.UPDATE_HEALTH = 0x3e
            self.SCOREBOARD_OBJECTIVE = 0x3f
            self.SET_PASSENGERS = 0x40  # TODO NEW
            self.TEAMS = 0x41
            self.UPDATE_SCORE = 0x42
            self.SPAWN_POSITION = 0x43
            self.TIME_UPDATE = 0x44
            self.TITLE = 0x45  # did not change
            self.UPDATE_SIGN = 0x46
            self.SOUND_EFFECT = 0x47
            self.PLAYER_LIST_HEADER_AND_FOOTER = 0x48
            self.COLLECT_ITEM = 0x49
            self.ENTITY_TELEPORT = 0x4a
            self.ENTITY_PROPERTIES = 0x4b
            self.ENTITY_EFFECT = 0x4c

            # removed
            self.UPDATE_ENTITY_NBT = 0xee
            self.MAP_CHUNK_BULK = 0xee
            self.BROKEN_SET_COMPRESSION_REMOVED1_9 = 0xee

            # parsing changes
            self.JOIN_GAME[PARSER] = [INT, UBYTE, INT, UBYTE, UBYTE, STRING]

        # 1.9.4 - 1.11 changes
        # http://wiki.vg/index.php?title=Protocol&oldid=7819#Entity_Properties
        # still good packet numbers through protocol 315
        if protocol > PROTOCOL_1_9_4:
            # removed
            self.UPDATE_SIGN = 0xee

            # -renumbered because of UPDATE_SIGN removal
            self.SOUND_EFFECT = 0x46
            self.PLAYER_LIST_HEADER_AND_FOOTER = 0x47
            self.COLLECT_ITEM = 0x48
            self.ENTITY_TELEPORT = 0x49
            self.ENTITY_PROPERTIES = 0x4a
            self.ENTITY_EFFECT = 0x4b

        # 1.12 changes
        if protocol > PROTOCOL_1_12START:
            # snapshots raise ValueError, so this is really >= PROTOCOL_1_12
            
            # re-ordered:
            self.ENTITY = 0x25
            self.ENTITY_RELATIVE_MOVE = 0x26
            self.ENTITY_LOOK_AND_RELATIVE_MOVE = 0x27
            self.ENTITY_LOOK = 0x28

            # new
            self.UNLOCK_RECIPES = 0x30  # TODO New
            
            # order bumped +1
            self.DESTROY_ENTITIES = 0x31
            self.REMOVE_ENTITY_EFFECT = 0x32
            self.RESOURCE_PACK_SEND = 0x33
            self.RESPAWN = 0x34
            self.ENTITY_HEAD_LOOK = 0x35
            
            # new
            self.SELECT_ADVANCEMENT_TAB = 0x36
            
            # order bumped +2
            self.WORLD_BORDER = 0x37
            self.CAMERA = 0x38
            self.HELD_ITEM_CHANGE = 0x39
            self.DISPLAY_SCOREBOARD = 0x3a
            self.ENTITY_METADATA[PKT] = 0x3b
            self.ATTACH_ENTITY = 0x3c
            self.ENTITY_VELOCITY = 0x3d
            self.ENTITY_EQUIPMENT = 0x3e
            self.SET_EXPERIENCE = 0x3f
            self.UPDATE_HEALTH = 0x40
            self.SCOREBOARD_OBJECTIVE = 0x41
            self.SET_PASSENGERS = 0x42  # TODO NEW
            self.TEAMS = 0x43
            self.UPDATE_SCORE = 0x44
            self.SPAWN_POSITION = 0x45
            self.TIME_UPDATE = 0x46
            self.TITLE = 0x47  # did not change
            self.SOUND_EFFECT = 0x48
            self.PLAYER_LIST_HEADER_AND_FOOTER = 0x49
            self.COLLECT_ITEM = 0x4a
            self.ENTITY_TELEPORT = 0x4b

            # new
            self.ADVANCEMENTS = 0x4c

            # order bumped +3
            self.ENTITY_PROPERTIES = 0x4d
            self.ENTITY_EFFECT = 0x4e

        # 1.12.1 CHANGES AGAIN! (to 340)
        if protocol >= PROTOCOL_1_12_1START:
            self.CRAFT_RECIPE_RESPONSE = 0x2b
            self.PLAYER_ABILITIES = 0x2c
            self.COMBAT_EVENT = 0x2d
            self.PLAYER_LIST_ITEM = 0x2e
            self.PLAYER_POSLOOK[PKT] = 0x2f
            self.USE_BED = 0x30
            self.UNLOCK_RECIPES = 0x31
            self.DESTROY_ENTITIES = 0x32
            self.REMOVE_ENTITY_EFFECT = 0x33
            self.RESOURCE_PACK_SEND = 0x34
            self.RESPAWN = 0x35
            self.ENTITY_HEAD_LOOK = 0x36
            self.SELECT_ADVANCEMENT_TAB = 0x37
            self.WORLD_BORDER = 0x38
            self.CAMERA = 0x39
            self.HELD_ITEM_CHANGE = 0x3a
            self.DISPLAY_SCOREBOARD = 0x3b
            self.ENTITY_METADATA[PKT] = 0x3c
            self.ATTACH_ENTITY = 0x3d
            self.ENTITY_VELOCITY = 0x3e
            self.ENTITY_EQUIPMENT = 0x3f
            self.SET_EXPERIENCE = 0x40
            self.UPDATE_HEALTH = 0x41
            self.SCOREBOARD_OBJECTIVE = 0x42
            self.SET_PASSENGERS = 0x43
            self.TEAMS = 0x44
            self.UPDATE_SCORE = 0x45
            self.SPAWN_POSITION = 0x46
            self.TIME_UPDATE = 0x47
            self.TITLE = 0x48
            self.SOUND_EFFECT = 0x49
            self.PLAYER_LIST_HEADER_AND_FOOTER = 0x4a
            self.COLLECT_ITEM = 0x4b
            self.ENTITY_TELEPORT = 0x4c
            self.ADVANCEMENTS = 0x4d
            self.ENTITY_PROPERTIES = 0x4e
            self.ENTITY_EFFECT = 0x4f

        # 1.12.2 CHANGES (340)
        if protocol >= PROTOCOL_1_12_1START:
            self.CRAFT_RECIPE_RESPONSE = 0x2b

            # Parsing changes
            self.KEEP_ALIVE[PARSER] = [LONG]

            # Things that may need addressed:
            # -Open sign editor
            # -Ping values has new info
            # -Display scoreboard has new info for team play
