Usage
=====

Here is an example showing how to add a new user **test** and set the home directory::

    import pyFileZilla
    settings = pyFileZilla.ftpSettings('/path/to/filezilla/config.xml')
    # add a new user with user name "test" and password "1234" and enable the account
    user = settings.addUser('test')
    user.setPassword('1234')
    user.enabled = True
    # add a new permission for the user and make it the home directory
    home = user.addPermission('/absolute/path/to/folder')
    home.ishome = True
    # make sure the permission to write to the directory is False
    home.filewrite = False
    # open the FileZilla Server config file and save the changes
    configfile = file('/path/to/filezilla/config.xml', 'wb')
    settings.write(configfile)
    configfile.close()
