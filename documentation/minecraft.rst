
**< class Minecraft(object) >**

    .. code:: python

        def __init__(self, wrapper)

    ..

    This class contains functions related to in-game features
    directly. These methods are accessed using 'self.api.minecraft'

    
-  banIp(self, ipaddress, reason="by wrapper api.", source="minecraft.api", expires=False)

        Ban an ip address using the wrapper proxy system. Messages
        generated by process can be directed to a particular player's
        client or to the Console (default). Ban will fail if it is not
        a valid ip4 address.

        :args:

                :ipaddress: IP address to ban
                :reason: Optional text reason
                :source: Source (author/op) of ban.
                :expires: Optional expiration in time.time() format.

        :returns: String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  banName(self, playername, reason="by wrapper api.", source="minecraft.api", expires=False)

        Ban a player using the wrapper proxy system.  Will attempt to
        poll or read cache for name. If no valid name is found, does a
        name-only ban with offline-hashed uuid

        :args:

                :playername: Player's name... specify the mojangUuid for online
                 ban and offlineUuid for offline bans.

                :reason: Optional text reason.

                :source: Source (author/op) of ban.

                :expires: Optional expiration in time.time() format.
                 Expirations only work when wrapper handles the login
                 (proxy mode).. and only for online bans.

        :returns: String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  banUUID(self, playeruuid, reason="by wrapper api.", source="minecraft.api", expires=False)

        Ban a player using the wrapper proxy system.

        :args:

                :playeruuid: Player's uuid... specify the mojangUuid
                 for online ban and offlineUuid for offline bans.

                :reason: Optional text reason.

                :source: Source (author/op) of ban.

                :expires: Optional expiration in time.time() format.
                 Expirations only work when wrapper handles the login
                 (proxy mode).. and only for online bans.

        :returns: String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  broadcast(self, message="", irc=False)

        Broadcasts the specified message to all clients connected.
        message can be a JSON chat object, or a string with formatting
        codes using the & as a prefix. Setting irc=True will also
        broadcast the specified message on IRC channels that Wrapper.py
        is connected to. Formatting might not work properly.

        :Args:
            :message:  The message
            :irc: Also broadcast to IRC if set to True.

        :returns:  Nothing

        
-  changeServerProps(self, config_item, new_value, reload_server=False)

        *New feature starting in version 1.0*

        Edits the server.properties file

        :Args:
            :item: item, like "online-mode"

            :new_value: applicable value

            :reload_server: True to restart the server.

        Items are changed in the config, but a server restart is required to
         make the changes persist.

        
-  configWrapper(self, section, config_item, new_value, reload_file=False)

        *New feature starting in version 0.8.12*

        Edits the Wrapper.Properties.json file

        :Args:
            :section:

            :config_item:

            :new_value:

            :reload_file: True to reload the config

        :returns: True or False, indicating Success or Failure

        
-  console(self, string)

        Run a command in the Minecraft server's console.

        :arg string: Full command text(without slash)

        :returns: Nothing

        
-  deOp(self, name_to_deop, playerObj=None,)

        De-ops player 'name_to_deop'.  If he is a super-op, the
        name is removed from superops.txt also.  Case sensitive!

        :Requires: Running server instance.

        :Args:
            :playerObj: This is the player that receives the command's
             output.  Setting 'None' uses the console operator (and
             permissions!). This player object must have OP level 10
             permission.
            :name_to_deop: The player to de-op.  Must match what is
             in superops.txt to remove superOP perms, but may deop
             the server ops.json file without case-sensitivity.

        :returns: True if success, a text message on failure.

        
-  getAllPlayers(self)

        Returns a dict containing the uuids and associated
        login data of all players ever connected to the server.

        
-  getEntityControl(self)

        Returns the server's entity controls context.  Will be None if
        the server is not up.

        Supported variables and methods:

        :These variables affect entity processing:
            :Property: Config Location

            :self.entityControl:
             config["Entities"]["enable-entity-controls"]

            :self.entityProcessorFrequency:
             config["Entities"]["entity-update-frequency"]

            :self.thiningFrequency:
             config["Entities"]["thinning-frequency"]

            :self.startThinningThreshshold:
             config["Entities"]["thinning-activation-threshhold"]

        :See api.entity for more about these methods:

                def killEntityByEID(self, eid, dropitems=False, count=1)

                def existsEntityByEID(self, eid)

                def getEntityInfo(self, eid)

                def countEntitiesInPlayer(self, playername)

                def countActiveEntities(self)

                def getEntityByEID(self, eid)


        
-  getGameRules(self)

        Get the server gamerules.

        :returns: a dictionary of the gamerules.

        
-  getLevelInfo(self, worldname=False)

        Get the world level.dat.

        :arg worldname:
            optional world name.  If not
            specified, Wrapper looks up the server worldname.

        :returns: Return an NBT object of the world's level.dat.

        
-  getOfflineUUID(self, name)


        :arg name: gets UUID object based on "OfflinePlayer:<name>"

        :returns: a MCUUID object based on the name

        
-  getPlayer(self, username="")

        Returns the player object of the specified logged-in player.
        Will raise an exception if the player is not logged in.

        This includes players who are transferred to another server. If
        you need to test whether a player is on this server; test if
        player.client and player.client.local == True

        :arg username: playername

        :returns: The Player Class object for "playername".

        
-  getPlayers(self)

        Returns a list of the currently connected players.

        
-  getServer(self)

        Returns the server context.  Use at own risk - items
        in server are generally private or subject to change (you are
        working with an undefined API!)... what works in this wrapper
        version may not work in the next.

        :returns: The server context that this wrapper is running.

        
-  getServerPackets(self, packetset="CB")

        Get the current proxy packet set.  Packet use will also
        require the following import at the begining of your
        plugin:
        .. code:: python

        from proxy.utils.constants import *
        # this line is needed to access constants for packet sending/parsing.

        ..

        :packets are also available from the player.api:
            player.cbpkt
            player.sbpkt

        :Args:
           :packetset: type(string)= "CB" or "SB". Argument is optional.
            If not specified, the client-bound packetset is returned.  If
            packetset is actually anything except "CB", the server-bound
            set is returned.

        :returns: The desired packet set.

       
-  getServerPath(self)

        Gets the server's path.

        
-  getSpawnPoint(self)

        Get the spawn point of the current world.

        :returns: Returns the spawn point of the current world.

        
-  getTime(self)

        Gets the world time in ticks.  This is total ticks since
        the server started! modulus the value by 24000 to get the time.

        :returns: Returns the time of the world in ticks.

        
-  getTimeofDay(self, dttmformat=0)

        get the "virtual" world time of day on the server.

        :arg dttmformat: 0 = ticks, 1 = Military, (else = civilian AM/PM).

            :ticks: are useful for timebased- events (like spawing
             your own mobs at night, etc).
            :Miliary/civilian: is useful for player displays.

        :returns: The appropriately formatted time string

        
-  getUuidCache(self)

        Gets the wrapper uuid cache.  This is as far as the API goes.
        The format of the cache's contents are undefined by this API.

        
-  getWorld(self)

        Get the world context

        :returns: Returns the world context of 'api.world, class World'
         for the running server instance

        
-  getWorldName(self)

        Returns the world's name.  If worldname does not exist (server
         not started), it returns `None`.  If a server was stopped and a
         new server instance not started, it will return the old world name.

        
-  getplayerby_eid(self, eid)

        Returns the player object of the specified logged-in player.
        Will raise an exception if the player is not logged in.

        :arg eid: EID of the player

        :returns: The Player Class object for the specified EID.
         If the EID is not a player or is not found, returns False
        
-  giveStatusEffect(self, player, effect, duration=30, amplifier=30)

        Gives the specified status effect to the specified target.

        :Args: (self explanatory? -see official Minecraft Wiki)

            :player: A player name or any valid string target
             selector (@p/e/a) with arguments ([r=...], etc)
            :effect:
            :duration:
            :amplifier:

        :returns: Nothing; runs in console

        
-  isIpBanned(self, ipaddress)

        Check if a ipaddress is banned.  Using this method also
        refreshes any expired bans and unbans them.

        :arg ipaddress: Check if an ipaddress is banned

        :returns: True or False (banned or not banned).
         If there is no proxy instance, nothing is returned.

        
-  isServerStarted(self)

        Return a boolean indicating if the server is
        fully booted or not.
        
-  isUUIDBanned(self, uuid)

        Check if a uuid is banned.  Using this method also refreshes
        any expired bans and unbans them.

        :arg uuid: Check if the UUID of the user is banned

        :returns: True or False (banned or not banned)
         If there is no proxy instance, None is returned.

        
-  lookupUUID(self, uuid)

        Returns a dictionary of {"uuid: the-uuid-of-the-player,
        "name": playername}. legacy function from the old 0.7.7 API.

        lookupbyUUID() is a better and more direct way to get the
        name from a uuid.

        :arg uuid:  player uuid

        :returns: a dictionary of two items, {"uuid: <player-uuid>,
         "name": <playername>}

        
-  lookupbyName(self, name)

        Returns the UUID from the specified username.
        If the player has never logged in before and isn't in the
        user cache, it will poll Mojang's API.  The function will
        return False if the name is invalid.

        :arg name:  player name

        :returns: a UUID object (wrapper type MCUUID)

        Remember to use the MCUUID.string to get a string when
         using this for string purposes (json keys)!

        
-  lookupbyUUID(self, uuid)

        Returns the username from the specified UUID.
        If the player has never logged in before and isn't in the user
        cache, it will poll Mojang's API.  The function will return
        False if the UUID is invalid.

        :arg uuid: string uuid with dashes

        :returns: username

        
-  makeOp(self, nametoOP, argslist, playerObj=None)

        Ops player 'nametoOP'.  Case sensitivity and other
        bahaviors of the command vary with server status and
        the arguments to 'argslist'

        :nametoOP: Name of player to OP.

        :playerObj: This is the player that receives the command's
         output.  Setting 'None' uses the console operator (and
         permissions!). This player object must have OP level 10
         permission.

        :Valid args for argslist:
            :-s: make player superop.txt entry.  Player will still
             not be superOP unless given appropriate level.
            :-o: use offline name and uuid.  This option only
             works if the server is not running!  Otherwise,
             the server uses its' default (depending on server
             mode).
            :-l: Flag for next argument to be a number
             corresponding to the desired level.  If the server is
             running, this argument only superops.txt is updated.
             if server is not running, the json.ops is also
             updated (to a maximum level of 4).
            :<number>: A number corresponding to the desired
             '-l' level.  These are two separate arguments and
             this number must be the next argument after -l in
             the list.

        :Notes:
            - Json.ops controls minecraft server permissions.
              This command CAN alter json.ops if the server is
              not running.
            - superops.txt controls wrapper commands, INCLUDING
              proxy ban commands.

        :returns: Nothing.  All output is directed to playerObj.

        
-  message(self, destination="", jsonmessage="")

        Used to message some specific target.

        :Args:
            :destination: playername or target
             selector '@a', 'suresttexas00' etc
            :jsonmessage: strict json chat message

        :returns: Nothing; succeeds or fails with no programmatic indication.

        
-  pardonIp(self, ipaddress)

        Pardon an IP.

        :arg ipaddress: a valid IPV4 address to pardon.

        :returns:  String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  pardonName(self, playername)

        Pardon a player.

        :arg playername:  Name to pardon.

        :returns: String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  pardonUUID(self, playeruuid)

        Pardon a player by UUID.

        :arg playeruuid:  UUID to pardon

        :returns: String describing the operation's outcome.
         If there is no proxy instance, nothing is returned.

        
-  refreshOpsList(self)

        OPs list is read from disk at startup.  Use this method
        to refresh the in-memory list from disk.

        
-  setBlock(self, x, y, z, tilename, datavalue=0, oldblockhandling="replace", datatag=None)

        Sets a block at the specified coordinates with the specific
        details. Will fail if the chunk is not loaded.

        :Args:  See the minecraft command wiki for these setblock arguments:

                :x:
                :y:
                :z:
                :tilename:
                :datavalue:
                :datatag:
                :oldblockhandling:

        :returns: Nothing.

        
-  setLocalName(self, MojangUUID, desired_name, kick=True)

        Set the local name on the server.  Understand that this
        may cause a vanilla server UUID change and loss of player
        data from the old name's offline uuid.

        
-  summonEntity(self, entity, x=0, y=0, z=0, datatag=None)

        Summons an entity at the specified coordinates with the
        specified data tag.

        :Args:

                :entity: string entity name type (capitalized correctly!)
                :x: coords
                :y:
                :z:
                :datatag: strict json text datatag


        :returns: Nothing - console executes command.

        
-  teleportAllEntities(self, entity, x, y, z)

        Teleports all of the specific entity type to the specified coordinates.

        :Args:
                :entity: string entity name type (capitalized correctly!)
                :x: coords
                :y:
                :z:

        :returns: Nothing - console executes command.

        