
**< class Backups(object) >**

    .. code:: python

        def __init__(self, wrapper)

    ..

    These methods are accessed using 'self.api.backups'

    .. code:: python

        <yourobject> = self.api.backups
        <yourobject>.<backups_method>

    ..

    This class wraps the wrapper.backups functions.  Wrapper starts
    core.backups.py class Backups (as .backups).  This API
    class manipulates the backups instance within core.wrapper

    
-  adjustBackupInterval(self, desired_interval)

        Adjust the backup interval for automatic backups.

        :arg desired_interval: interval in seconds for regular backups

        :returns:

        
-  adjustBackupsKept(self, desired_number)

        Adjust the number of backups kept.

        :arg desired_number: number of desired backups

        :returns:

        
-  backupInProgress(self)

        Query the state of automatic backups.  This and `backupIsIdle` are
        just the same function phrased in opposite manner.

        :returns:  True if a backup is in progress.  Otherwise, if a backup
         is not running, returns False

        
-  backupIsIdle(self)

        Query the state of automatic backups, asking a boolean representing
        whether the backups are currently idle.

        :returns:  True if a backup is idle and not running.  Otherwise, if
         a backup is running, returns False

        
-  disableBackups(self)

        Allow plugin to temporarily shut off backups (only during
        this wrapper session).

        :returns: None

        
-  enableBackups(self)

        Allow plugin to re-enable disabled backups or enable backups
        during this wrapper session.

        :returns: False if tar is not installed, otherwise, nothing.

        
-  performBackup(self)

        Perform an immediate backup

        :returns: check console for messages (or wrapper backup Events)

        
-  pruneBackups(self)

        prune backups according to wrapper properties settings.

        :returns: Output to console and logs

        
-  verifyTarInstalled(self)

        checks for tar on users system.

        :returns: True if installed, False if not (along with error logs
         and console messages).

        