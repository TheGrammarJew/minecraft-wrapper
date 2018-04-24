# -*- coding: utf-8 -*-

***Wrapper Events***

    Each Wrapper event, once registered, will call back the passed function
    when the event occurs.  The call back function must reference the correct
    return payload.
    
    When a plugin calls an event which can be aborted, it is important that
    your code not delay in completing.  The proxy packet processing is on
    hold while your code decides what to do with the event.  If you take too 
    long, the client could be disconnected!  This is an aggregate time of
    all the plugins that call this event.
    
    :sample Plugin snippet:
    
        .. code:: python

            class Main:
                def __init__(self, api, log):
                    self.api = api
                    
            def onEnable(self):
                self.api.registerEvent("player.login", _player_login_callback)
            
            def _player_login_callback(self, payload):
                playername = payload["playername"]
                player_object = self.api.getPlayer(playername)
                self.api.minecraft.broadcast("%s joined the server!" % playername)
                player_object.message("Welcome to the server, %s" % playername)
                
        ..


**< Group 'core/mcserver.py' >**

:Event: "player.login"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description:
        When player logs into the java MC server.

    :Payload:
        :"player": player object (if object available -could be False if not)
        :"playername": user name of player (string)

    :Can be aborted/modified: No

    :Comments:
        All events in the core/mcserver.py group are collected
        from the console output, do not require proxy mode, and
        therefore, also, cannot be aborted.

:Event: "player.logout"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description:
        When player logs out of the java MC server.

    :Payload:
        :"player": player object (if object available -could be False if not)
        :"playername": user name of player (string)

    :Can be aborted/modified: No - but This will pause long enough for you to deal with the playerobject.

    :Comments:
        All events in the core/mcserver.py group are collected
        from the console output, do not require proxy mode, and
        therefore, also, cannot be aborted.

:Event: "server.stopped"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.stopped

    :Payload:
        :"reason": reason}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.starting"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.starting

    :Payload:
        :"reason": reason}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.started"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.started

    :Payload:
        :"reason": reason}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.stopping"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.stopping

    :Payload:
        :"reason": reason}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.state"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.state

    :Payload:
        :"state": state
        :"reason": reason}
         abortable=False

    :Can be aborted/modified: 


:Event: "player.message"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description:
        Player chat scrubbed from the console.

    :Payload:
        :"player": playerobject (self.__str__ represents as player.username)
        :"message": <str> type - what the player said in chat. ('hello everyone')
        :"original": The original line of text from the console ('<mcplayer> hello everyone`)

    :Can be aborted/modified: No

    :Comments:
        This event is triggered by console chat which has already been sent.
        This event returns the player object. if used in a string context,
        ("%s") it's repr (self.__str__) is self.username (no need to do
        str(player) or player.username in plugin code).

:Event: "player.action"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: player.action

    :Payload:
        :"player": self.getplayer(name)
        :"action": message}
         abortable=False

    :Can be aborted/modified: 


:Event: "player.achievement"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: player.achievement

    :Payload:
        :"player": name
        :"achievement": achievement}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.say"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.say

    :Payload:
        :"player": name
        :"message": message
        :"original": original}
         abortable=False

    :Can be aborted/modified: 


:Event: "player.death"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: player.death

    :Payload:
        :"player": self.getplayer(name)
        :"death": getargsafter(line_words
         1)}
         abortable=False

    :Can be aborted/modified: 


:Event: "server.lagged"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description: server.lagged

    :Payload:
        :"ticks": get_int(skipping_ticks)}
         abortable=False

    :Can be aborted/modified: 


:Event: "player.teleport"

    :Module: mcserver.py *(core/mcserver.py)*

    :Description:
        When player teleports.

    :Payload:
        :"player": player object

    :Can be aborted/modified: No

    :Comments:
        driven from console message "Teleported ___ to ....".

**< Group 'wrapper' >**

:Event: "timer.second"

    :Module: wrapper.py *(core/wrapper.py)*

    :Description:
        a timer that is called each second.  Do
          not rely on these events to happen 'on-time'!  They
          can be delayed based on their position the queue, as
          well as the total number of timer.second events being
          called.

    :Payload:
         None
         abortable=False

    :Can be aborted/modified: No


:Event: "timer.tick"

    :Module: wrapper.py *(core/wrapper.py)*

    :Description:
        a timer that is called each 1/20th
          of a second, like a minecraft tick.

    :Payload:
         None
         abortable=False

    :Can be aborted/modified: No

    :Comments:
        Use of this timer is deprecated and is turned off
          by default in the wrapper.config.json file.  the final
          wrapper version 1.0 final will not support this timer. Its
          use in wrapper has always been a bad idea. Starting with
          wrapper 1.0.9 RC 12, this timer will be somewhat buggy,
          running two or more ticks behind.

**< Group 'core/irc.py' >**

:Event: "irc.join"

    :Module: irc.py *(core/irc.py)*

    :Description: irc.join

    :Payload:
        :"nick": nick
        :"channel": channel}
         abortable=False

    :Can be aborted/modified: 


:Event: "irc.part"

    :Module: irc.py *(core/irc.py)*

    :Description: irc.part

    :Payload:
        :"nick": nick
        :"channel": channel}
         abortable=False

    :Can be aborted/modified: 


:Event: "irc.quit"

    :Module: irc.py *(core/irc.py)*

    :Description: irc.quit

    :Payload:
        :"nick": nick
        :"message": message
        :"channel": None}
         abortable=False

    :Can be aborted/modified: 


:Event: "irc.action"

    :Module: irc.py *(core/irc.py)*

    :Description: irc.action

    :Payload:
        :"nick": nick
        :"channel": channel
        :"action": getargsafter(message.split(" ")
         1)[:-1]}
         abortable=False

    :Can be aborted/modified: 


:Event: "irc.message"

    :Module: irc.py *(core/irc.py)*

    :Description: irc.message

    :Payload:
        :"nick": nick
        :"channel": channel
        :"message": message}
         abortable=False

    :Can be aborted/modified: 


**< Group 'Proxy' >**

:Event: "player.preLogin"

    :Module: clientconnection.py *(client/clientconnection.py)*

    :Description:
        Called before client logs on.  This event marks the
        birth of the player object in wrapper (when in proxy mode)

    :Payload:
        :"playername": self.username,
        :"player": Player object will be created by the event code
        :"online_uuid": online UUID,
        :"server_uuid": UUID on local server (offline),
        :"ip": the user/client IP on the internet.
        :"secure_connection": Proxy's online mode

    :Can be aborted/modified: Yes, return False to disconnect the client.

    :Comments:
        - If aborted, the client is disconnnected with message
        "Login denied by a Plugin."
        - Event occurs after proxy ban code runs right after a
        successful handshake with Proxy.

:Event: "player.rawMessage"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        Raw message from client to server.
        Contains the "/", if present.

    :Payload:
        :"player": player object
        :"playername": player's name
        :"message": the chat message string.

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False. Can be modified before
        passing to server.  'chatmsg' accepts both raw string
        or a dictionary payload containing ["message"] item.

:Event: "player.dig"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        When a player attempts to dig.  This event
        only supports starting and finishing a dig.

    :Payload:
        :"playername": player's name
        :"player": player object
        :"position": x, y, z block position
        :"action": begin_break or end_break (string)
        :"face": 0-5 (bottom, top, north, south, west, east)

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False. Note that the client
        may still believe the block is broken (or being broken).
        If you intend to abort the dig, it should be done at
        "begin_break". Sending a false bedrock to the client's
        digging position will help prevent the client from
        sending "end_break"

:Event: "player.interact"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        Called when the client is eating food,
        pulling back bows, using buckets, etc.

    :Payload:
        :"playername": player's name
        :"player": player object
        :"position":  the PLAYERS position - x, y, z, pitch, yaw
        :"action": "finish_using"  or "use_item"
        :"hand": 0 = main hand, 1 = off hand (shield).
        :"origin": Debugging information on where event was parsed.
         Either 'pktSB.PLAYER_DIGGING' or 'pktSB.USE_ITEM'

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False. Note that the client
        may still believe the action happened, but the server
        will act as though the event did not happen.  This
        could be confusing to a player.  If the event is aborted,
        consider some feedback to the client (a message, fake
        particles, etc.)

:Event: "player.place"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        Called when the client places an item

    :Payload:
        :"playername": player's name
        :"player": player object
        :"position":  the clicked position, corrected for 'face' (i.e.,
         the adjoining block position)
        :"clickposition": The position of the block that was actually
         clicked
        :"item": The item player is holding (item['id'] = -1 if no item)
        :"hand": hand in use (0 or 1)

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False. Note that the client
        may still believe the action happened, but the server
        will act as though the event did not happen.  This
        could be confusing to a player.  If the event is aborted,
        consider some feedback to the client (a message, fake
        block, etc.)

:Event: "player.createSign"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        When a player creates a sign and finishes editing it

    :Payload:
        :"player": player object
        :"playername": player's name
        :"position": position of sign
        :"line1": l1
        :"line2": l2
        :"line3": l3
        :"line4": l4

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False.
        Any of the four line arguments can be changed by
        returning a dictionary payload containing the lines
        you want replaced:
        
        `return {"line2": "You can't write", "line3": "that!"}`

:Event: "player.slotClick"

    :Module: parse_sb.py *(client/parse_sb.py)*

    :Description:
        When a player clicks a window slot

    :Payload:
        :"player": Player object
        :"playername": the player's name
        :"wid": window id ... always 0 for inventory
        :"slot": slot number
        :"button": mouse / key button
        :"action": unique action id - incrementing counter
        :"mode": varint:mode - see the wiki?
        :"clicked": item data

    :Can be aborted/modified: Yes

    :Comments:
        Can be aborted by returning False. Aborting is not recommended
        since that is how wrapper keeps tabs on inventory.

:Event: "player.chatbox"

    :Module: parse_cb.py *(server/parse_cb.py)*

    :Description:
        Chat message sent from the server to the client.

    :Payload:
        :"playername": client username
        :"player": player object
        :"json": json or string data

    :Can be aborted/modified: Yes

    :Comments:
        - The message will not reach the client if the event is returned False.
        - If json chat (dict) or text is returned, that value will be sent
        to the client instead.

:Event: "player.usebed"

    :Module: parse_cb.py *(server/parse_cb.py)*

    :Description:
        Sent when server sends client to bedmode.

    :Payload:
        :"playername": client username
        :"player": player object
        :"position": position of bed

    :Can be aborted/modified: No - The server thinks the client is in bed already.


:Event: "player.spawned"

    :Module: parse_cb.py *(server/parse_cb.py)*

    :Description:
        Sent when server advises the client of the Spawn position.

    :Payload:
        :"playername": client username
        :"player": player object
        :"position": Spawn's position

    :Can be aborted/modified: No - Notification only.

    :Comments:
        Sent by the server after login to specify the coordinates of the spawn point (the point at which players spawn at, and which the compass points to). It can be sent at any time to update the point compasses point at.

:Event: "entity.unmount"

    :Module: parse_cb.py *(server/parse_cb.py)*

    :Description:
        Sent when player attaches to entity.

    :Payload:
        :"playername": client username
        :"player": player object
        :"vehicle_id": EID of vehicle or MOB
        :"leash": leash True/False

    :Can be aborted/modified: No - Notification only.

    :Comments:
        Only works if entity controls are enabled.  Entity controls
        add significant load to wrapper's packet parsing and is off by default.

:Event: "entity.mount"

    :Module: parse_cb.py *(server/parse_cb.py)*

    :Description:
        Sent when player detaches/unmounts entity.

    :Payload:
        :"playername": client username
        :"player": player object
        :"vehicle_id": EID of vehicle or MOB
        :"leash": leash True/False

    :Can be aborted/modified: No - Notification only.

    :Comments:
        Only works if entity controls are enabled.  Entity controls
        add significant load to wrapper's packet parsing and is off by default.

**< Group 'Backups' >**

:Event: "wrapper.backupDelete"

    :Module: backups.py *(core/backups.py)*

    :Description:
        Called upon deletion of a backup file.

    :Payload:
        :"file": filename

    :Can be aborted/modified: Yes, return False to abort.


:Event: "wrapper.backupFailure"

    :Module: backups.py *(core/backups.py)*

    :Description:
        Indicates failure of backup.

    :Payload:
        :"reasonCode": an integer 1-4
        :"reasonText": a string description of the failure.

    :Can be aborted/modified: No - informatinal only

    :Comments:
        Reasoncode and text provide more detail about specific problem.
        1 - Tar not installed.
        2 - Backup file does not exist after the tar operation.
        3 - Specified file does not exist.
        4 - backups.json is corrupted
        5 - unable to create backup directory

:Event: "wrapper.backupBegin"

    :Module: backups.py *(core/backups.py)*

    :Description:
        Indicates a backup is being initiated.

    :Payload:
        :"file": Name of backup file.

    :Can be aborted/modified: Yes, return False to abort.

    :Comments:
        A console warning will be issued if a plugin cancels the backup.

:Event: "wrapper.backupEnd"

    :Module: backups.py *(core/backups.py)*

    :Description:
        Indicates a backup is complete.

    :Payload:
        :"file": Name of backup file.
        :"status": Status code from TAR
        :"summary": string summary of operation

    :Can be aborted/modified: No - informational only


**< Group 'core/wrapper.py' >**

:Event: "server.consoleMessage"

    :Module: wrapper.py *(core/wrapper.py)*

    :Description:
        a line of Console output.

    :Payload:
        :"message": <str> type - The line of buffered output.

    :Can be aborted/modified: No

    :Comments:
        This event is triggered by console output which has already been sent.

