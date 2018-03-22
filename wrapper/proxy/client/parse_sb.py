# -*- coding: utf-8 -*-

# Copyright (C) 2016, 2017 - BenBaptist and Wrapper.py developer(s).
# https://github.com/benbaptist/minecraft-wrapper
# This program is distributed under the terms of the GNU
# General Public License, version 3 or later.

from proxy.utils.constants import *


# noinspection PyMethodMayBeStatic
class ParseSB(object):
    """
    ParseSB parses server bound packets that are coming from the client.
    """
    def __init__(self, client, packet):
        self.client = client
        self.proxy = client.proxy
        self.log = client.log
        self.packet = packet
        self.pktSB = self.client.pktSB

        self.command_prefix = self.proxy.srv_data.command_prefix
        self.command_prefix_non_standard = self.command_prefix != "/"
        self.command_prefix_len = len(self.command_prefix)

    def parse_play_player_poslook(self):  # player position and look
        """decided to use this one solely for tracking the client position"""

        # DOUBLE, DOUBLE, DOUBLE, DOUBLE, FLOAT, FLOAT, BOOL - 1.7 - 1.7.10
        # ("double:x|double:feety|double:heady|double:z|float:yaw|float:pitch|bool:on_ground")

        # DOUBLE, DOUBLE, DOUBLE, FLOAT, FLOAT, BOOL - 1.8 and up
        # ("double:x|double:feety|double:z|float:yaw|float:pitch|bool:on_ground")

        data = self.packet.readpkt(self.pktSB.PLAYER_POSLOOK[PARSER])
        if self.client.clientversion > PROTOCOL_1_8START:
            self.client.position = (data[0], data[1], data[2])
            self.client.head = (data[3], data[4])
        else:
            self.client.position = (data[0], data[1], data[3])
            self.client.head = (data[4], data[5])
        return True

    def parse_play_chat_message(self):
        data = self.packet.readpkt([STRING])
        if data is None:
            return False

        # Get the packet chat message contents
        chatmsg = data[0]

        payload = self.proxy.eventhandler.callevent("player.rawMessage", {
            "playername": self.client.username,
            "message": chatmsg
        })
        """ eventdoc
            <group> Proxy <group>

            <description> Raw message from client to server.
            Contains the "/", if present.
            <description>

            <abortable> Yes <abortable>

            <comments>
            Can be aborted by returning False. Can be modified before
            passing to server.  'chatmsg' accepts both raw string
            or a dictionary payload containing ["message"] item.
            <comments>
            <payload>
            "player": player's name
            "message": the chat message string.
            <payload>

        """
        # This part allows the player plugin event "player.rawMessage" to...
        if payload is False:
            return False  # ..reject the packet (by returning False)

        # This is here for compatibility.  older plugins
        #  may attempt to send a string back
        if type(payload) == str:  # or, if it can return a substitute payload
            chatmsg = payload

        # Newer plugins return a modified version of the original
        # payload (i.e., a dictionary).

        # or, if it can return a substitute payload
        if type(payload) == dict and "message" in payload:
            chatmsg = payload["message"]

        # determine if this is a command. act appropriately
        if chatmsg[0:self.command_prefix_len] == self.command_prefix:
            # it IS a command of some kind
            if self.proxy.eventhandler.callevent(
                    "player.runCommand", {
                        "playername": self.client.username,
                        "command": chatmsg.split(" ")[0][1:].lower(),
                        "args": chatmsg.split(" ")[1:]}):

                # wrapper processed this command.. it goes no further
                """ eventdoc
                    <group> Proxy <group>

                    <description> When a player runs a command. Do not use
                    for registering commands.
                    <description>

                    <abortable> Yes. Registered commands ARE already aborted since they do not get passed to the server.
                    <abortable>

                    <comments>
                    Called AFTER player.rawMessage event (if rawMessage
                    does not reject it).  However, rawMessage could have
                    modified it before this point.
                    
                    The best use of this event is a quick way to prevent a client from 
                    passing certain commands or command arguments to the server.
                    rawMessage is better if you need something else (parsing or
                    filtering chat, for example).
                    <comments>

                    <payload>
                    "player": playerobject()
                    "command": slash command (or whatever is set in wrapper's
                    config as the command cursor).
                    "args": the remaining words/args
                    <payload>

                """
                return False

        if chatmsg[0] == "/" and self.command_prefix_non_standard:
            # strip leading slash if using a non-slash command  prefix
            chatmsg = chatmsg[1:]

        # NOW we can send it (possibly modded) on to server...
        self.client.chat_to_server(chatmsg)
        return False  # and cancel this original packet

    def parse_play_player_position(self):
        if self.client.clientversion < PROTOCOL_1_8START:
            data = self.packet.readpkt([DOUBLE, DOUBLE, DOUBLE, DOUBLE, BOOL])
            # ("double:x|double:y|double:yhead|double:z|bool:on_ground")
        elif self.client.clientversion >= PROTOCOL_1_8START:
            data = self.packet.readpkt([DOUBLE, DOUBLE, NULL, DOUBLE, BOOL])
            # ("double:x|double:y|double:z|bool:on_ground")
        else:
            data = [0, 0, 0, 0]
        # skip 1.7.10 and lower protocol yhead args
        self.client.position = (data[0], data[1], data[3])
        return True

    def parse_play_player_look(self):
        data = self.packet.readpkt([FLOAT, FLOAT, BOOL])
        # ("float:yaw|float:pitch|bool:on_ground")
        self.client.head = (data[0], data[1])
        return True

    def parse_play_player_digging(self):
        if self.client.clientversion < PROTOCOL_1_7:
            data = None
            position = data
        elif PROTOCOL_1_7 <= self.client.clientversion < PROTOCOL_1_8START:
            data = self.packet.readpkt([BYTE, INT, UBYTE, INT, BYTE])
            # "byte:status|int:x|ubyte:y|int:z|byte:face")
            position = (data[1], data[2], data[3])
        else:
            data = self.packet.readpkt([BYTE, POSITION, NULL, NULL, BYTE])
            # "byte:status|position:position|byte:face")
            position = data[1]

        if data is None:
            return True

        # finished digging
        if data[0] == 2:
            if not self.proxy.eventhandler.callevent("player.dig", {
                "playername": self.client.username,
                "position": position,
                "action": "end_break",
                "face": data[4]
            }):
                return False  # stop packet if  player.dig returns False
            """ eventdoc
                        <group> Proxy <group>

                        <description> When a player attempts to dig.  This event
                        only supports starting and finishing a dig.
                        <description>

                        <abortable> Yes <abortable>

                        <comments>
                        Can be aborted by returning False. Note that the client
                        may still believe the block is broken (or being broken).
                        If you intend to abort the dig, it should be done at
                        "begin_break". Sending a false bedrock to the client's 
                        digging position will help prevent the client from 
                        sending "end_break"
                        
                        <comments>

                        <payload>
                        "playername": playername (not the player object!)
                        "position": x, y, z block position
                        "action": begin_break or end_break (string)
                        "face": 0-5 (bottom, top, north, south, west, east)
                        <payload>

                    """
        # started digging
        if data[0] == 0:
            if self.client.gamemode != 1:
                if not self.proxy.eventhandler.callevent("player.dig", {
                    "playername": self.client.username,
                    "position": position,
                    "action": "begin_break",
                    "face": data[4]
                }):
                    return False
            else:
                if not self.proxy.eventhandler.callevent("player.dig", {
                    "playername": self.client.username,
                    "position": position,
                    "action": "end_break",
                    "face": data[4]
                }):
                    return False
        if data[0] == 5 and position == (0, 0, 0):
                playerpos = self.client.position
                if not self.proxy.eventhandler.callevent("player.interact", {
                    "playername": self.client.username,
                    "position": playerpos,
                    "action": "finish_using",
                    "origin": "pktSB.PLAYER_DIGGING"
                }):
                    return False
                """ eventdoc
                    <group> Proxy <group>

                    <description> Called when the client is eating food, 
                    pulling back bows, using buckets, etc.
                    <description>

                    <abortable> Yes <abortable>

                    <comments>
                    Can be aborted by returning False. Note that the client
                    may still believe the action happened, but the server
                    will act as though the event did not happen.  This 
                    could be confusing to a player.  If the event is aborted, 
                    consider some feedback to the client (a message, fake 
                    particles, etc.)
                    <comments>

                    <payload>
                    "playername": playername (not the player object!)
                    "position":  the PLAYERS position - x, y, z, pitch, yaw
                    "action": "finish_using"  or "use_item"
                    "origin": Debugging information on where event was parsed.
                    <payload>

                """
        return True

    def parse_play_player_block_placement(self):
        player = self.client.username
        hand = 0  # main hand
        helditem = self.client.inventory[36 + self.client.slot]

        if self.client.clientversion < PROTOCOL_1_7:
            data = None
            position = data

        elif PROTOCOL_1_7 <= self.client.clientversion < PROTOCOL_1_8START:
            data = self.packet.readpkt(
                [INT, UBYTE, INT, BYTE, SLOT_NO_NBT, REST])
            # "int:x|ubyte:y|int:z|byte:face|slot:item")
            #  REST includes cursor positions x-y-z
            position = (data[0], data[1], data[2])

            # just FYI, notchian servers have been ignoring this field ("item")
            # for a long time, using server inventory instead.
            helditem = data[4]  # "item" - SLOT

        elif PROTOCOL_1_8START <= self.client.clientversion < PROTOCOL_1_9REL1:
            data = self.packet.readpkt(
                [POSITION, NULL, NULL, BYTE, SLOT, REST])
            # "position:Location|byte:face|slot:item|byte:CurPosX|
            #     byte:CurPosY|byte:CurPosZ")
            # helditem = data["item"]  -available in packet, but server
            # ignores it (we should too)!
            # starting with 1.8, the server maintains inventory also.
            position = data[0]

        else:  # self.clientversion >= PROTOCOL_1_9REL1:
            data = self.packet.readpkt(
                [POSITION, NULL, NULL, VARINT, VARINT, BYTE, BYTE, BYTE])
            # "position:Location|varint:face|varint:hand|byte:CurPosX|
            #     byte:CurPosY|byte:CurPosZ")
            hand = data[4]  # used to be the spot occupied by "slot"
            position = data[0]

        # Face and Position exist in all version protocols at this point
        clickposition = position
        face = data[3]

        if face == 0:  # Compensate for block placement coordinates
            position = (position[0], position[1] - 1, position[2])
        elif face == 1:
            position = (position[0], position[1] + 1, position[2])
        elif face == 2:
            position = (position[0], position[1], position[2] - 1)
        elif face == 3:
            position = (position[0], position[1], position[2] + 1)
        elif face == 4:
            position = (position[0] - 1, position[1], position[2])
        elif face == 5:
            position = (position[0] + 1, position[1], position[2])

        if helditem is None:
            # if no item, treat as interaction (according to wrappers
            # inventory :(, return False  )
            if not self.proxy.eventhandler.callevent("player.interact", {
                "playername": player,
                "position": position,
                "action": "useitem",
                "origin": "pktSB.PLAYER_BLOCK_PLACEMENT"
            }):
                self.log.debug("player helditem was None. (playerblockplacement-SB)")
                return False

        # block placement event
        self.client.lastplacecoords = position
        # position is where new block goes
        # clickposition is the block actually clicked
        if not self.proxy.eventhandler.callevent(
                "player.place",
                {"playername": player, "position": position,
                 "clickposition": clickposition,
                 "hand": hand, "item": helditem}):
            """ eventdoc
                <group> Proxy <group>

                <description> Called when the client places an item
                <description>

                <abortable> Yes <abortable>

                <comments>
                Can be aborted by returning False. Note that the client
                may still believe the action happened, but the server
                will act as though the event did not happen.  This 
                could be confusing to a player.  If the event is aborted, 
                consider some feedback to the client (a message, fake 
                block, etc.)
                <comments>

                <payload>
                "playername": playername (not the player object!)
                "position":  the PLAYERS position - x, y, z, pitch, yaw
                "action": "finish_using"  or "use_item"
                "origin": Debugging information on where event was parsed.
                <payload>

            """
            return False
        return True

    def parse_play_use_item(self):  # no 1.8 or prior packet
        data = self.packet.readpkt([REST])
        # "rest:pack")
        position = self.client.lastplacecoords
        if "pack" in data:
            if data[0] == '\x00':
                if not self.proxy.eventhandler.callevent("player.interact", {
                    "playername": self.client.username,
                    "position": position,
                    "action": "useitem",
                    "origin": "pktSB.USE_ITEM"
                }):
                    return False
        return True

    def parse_play_held_item_change(self):
        slot = self.packet.readpkt([SHORT])
        # "short:short")  # ["short"]
        if 9 > slot[0] > -1:
            self.client.slot = slot[0]
        else:
            self.log.debug("held item change returned False (SB)")
            return False
        return True

    def parse_play_player_update_sign(self):
        if self.client.clientversion < PROTOCOL_1_8START:
            data = self.packet.readpkt(
                [INT, SHORT, INT, STRING, STRING, STRING, STRING])
            # "int:x|short:y|int:z|string:line1|string:line2|string:line3|
            #   string:line4")
            position = (data[0], data[1], data[2])
            pre_18 = True
        else:
            data = self.packet.readpkt(
                [POSITION, NULL, NULL, STRING, STRING, STRING, STRING])
            # "position:position|string:line1|string:line2|string:line3|
            #   string:line4")
            position = data[0]
            pre_18 = False

        l1 = data[3]
        l2 = data[4]
        l3 = data[5]
        l4 = data[6]
        payload = self.proxy.eventhandler.callevent("player.createSign", {
            "playername": self.client.username,
            "position": position,
            "line1": l1,
            "line2": l2,
            "line3": l3,
            "line4": l4
        })

        # plugin can reject sign entirely
        if not payload:
            return False

        # send back edits
        if type(payload) == dict:
            if "line1" in payload:
                l1 = payload["line1"]
            if "line2" in payload:
                l2 = payload["line2"]
            if "line3" in payload:
                l3 = payload["line3"]
            if "line4" in payload:
                l4 = payload["line4"]
        """ eventdoc
            <group> Proxy <group>

            <description> When a player creates a sign and finishes editing it
            <description>

            <abortable> Yes <abortable>

            <comments>
            Can be aborted by returning False.
            Any of the four line arguments can be changed by
            returning a dictionary payload containing the lines 
            you want replaced:    
            
            `return {"line2": "You can't write", "line3": "that!"}`
            <comments>

            <payload>
            "player": player name
            "position": position of sign
            "line1": l1
            "line2": l2
            "line3": l3
            "line4": l4
            <payload>

        """
        self.client.editsign(position, l1, l2, l3, l4, pre_18)
        return False

    def parse_play_client_settings(self):  # read Client Settings
        """ This is read for later sending to servers we connect to """
        self.client.clientSettings = self.packet.readpkt([RAW])[0]
        self.client.clientSettingsSent = True
        # the packet is not stopped, sooo...
        return True

    def parse_play_click_window(self):  # click window
        if self.client.clientversion < PROTOCOL_1_8START:
            data = self.packet.readpkt(
                [BYTE, SHORT, BYTE, SHORT, BYTE, SLOT_NO_NBT])
            # ("byte:wid|short:slot|byte:button|short:action|byte:mode|
            #   slot:clicked")
        elif PROTOCOL_1_8START < self.client.clientversion < PROTOCOL_1_9START:
            data = self.packet.readpkt(
                [UBYTE, SHORT, BYTE, SHORT, BYTE, SLOT])
            # ("ubyte:wid|short:slot|byte:button|short:action|byte:mode|
            #   slot:clicked")
        elif PROTOCOL_1_9START <= self.client.clientversion < PROTOCOL_MAX:
            data = self.packet.readpkt(
                [UBYTE, SHORT, BYTE, SHORT, VARINT, SLOT])
            # ("ubyte:wid|short:slot|byte:button|short:action|varint:mode|
            #   slot:clicked")
        else:
            data = [False, 0, 0, 0, 0, 0, 0]

        datadict = {
            "playername": self.client.username,
            "wid": data[0],  # window id ... always 0 for inventory
            "slot": data[1],  # slot number
            "button": data[2],  # mouse / key button
            "action": data[3],  # unique action id - incrementing counter
            "mode": data[4],
            "clicked": data[5]  # item data
        }

        if not self.proxy.eventhandler.callevent("player.slotClick", datadict):
            return False
        """ eventdoc
            <group> Proxy <group>

            <description> When a player clicks a window slot
            <description>

            <abortable> Yes <abortable>

            <comments>
            Can be aborted by returning False. Aborting is not recommended
            since that is how wrapper keeps tabs on inventory.
            <comments>

            <payload>
            "player": Players name (not the object!)
            "wid": window id ... always 0 for inventory
            "slot": slot number
            "button": mouse / key button
            "action": unique action id - incrementing counter
            "mode": varint:mode - see the wiki?
            "clicked": item data
            <payload>

        """
        # for inventory control, the most straightforward way to update
        # wrapper's inventory is to use the data from each click.  The
        # server will make other updates and corrections via SET_SLOT

        # yes, this probably breaks for double clicks that send the item
        # to who-can-guess what slot. We can fix that in a future update...
        # this gets us 98% fixed (versus 50% before) another source of
        # breakage is if lagging causes server to deny the changes.  Our
        # code does not check if the server accepted these changes with
        # a CONFIRM_TRANSACTION.

        # window 0 (inventory) and right or left click
        if data[0] == 0 and data[2] in (0, 1):
            # player first clicks on an empty slot - mark empty.
            if self.client.lastitem is None and data[5] is None:
                self.client.inventory[data[1]] = None

            # player first clicks on a slot where there IS some data..
            if self.client.lastitem is None:
                # having clicked on it puts the slot into NONE
                # status (since it can now be moved).
                # So we set the current slot to empty/none
                self.client.inventory[data[1]] = None
                # ..and we cache the new slot data to see where it goes
                self.client.lastitem = data[5]
                return True

            # up to this point, there was not previous item
            if self.client.lastitem is not None and data[5] is None:
                # now we have a previous item to process

                # that previous item now goes into the new slot.
                self.client.inventory[data[1]] = self.client.lastitem
                # since the slot was empty, there is no newer item to cache.
                self.client.lastitem = None
                return True

            if self.client.lastitem is not None and data[5] is not None:
                # our last item now occupies the space clicked and the new
                # item becomes the cached item.

                # set the cached item into the clicked slot.
                self.client.inventory[data[1]] = self.client.lastitem
                # put the item that was in the clicked slot into the cache now.
                self.client.lastitem = data[5]
                return True
        return True

    def parse_play_spectate(self):
        # Spectate - convert packet to local server UUID

        # "Teleports the player to the given entity. The player must be in
        # spectator mode. The Notchian client only uses this to teleport to
        # players, but it appears to accept any type of entity. The entity
        # does not need to be in the same dimension as the player; if
        # necessary, the player will be respawned in the right world."

        """ Inter-dimensional player-to-player TP ! """  # TODO !

        # solves the uncertainty of dealing with what gets returned.
        data = self.packet.readpkt([UUID, NULL])

        # ("uuid:target_player")
        for client in self.proxy.clients:
            if data[0] == client.uuid:
                self.client.server_connection.packet.sendpkt(
                    self.client.pktSB.SPECTATE,
                    [UUID],
                    [client.serveruuid])
                self.log.debug("spectate returned False (SB)")
                return False
        return True
