import os
import hashlib
from subprocess import call
import xml.dom.minidom


RELOAD_COMMAND_ARGS = '/reload-config'

YESNO_VALUES = {
    False: '0',
    True: '1',
    None: '2',
}
YESNO_OPTIONS = {
    '0': False,
    '1': True,
    '2': None,
}

SPEED_DEFAULT = '0'
SPEED_UNLIMITED = '1'
SPEED_CONSTANT = '2'
SPEED_RULES = '3'


class ftpElement(object):
    def __init__(self, **kwargs):
        if kwargs.get('element'):
            self.element = kwargs['element']
            self.document = self.element.ownerDocument
            self.loadElement()
        elif kwargs.get('document') and kwargs.get('tagName'):
            self.document = kwargs['document']
            self.createElement(**kwargs)
        else:
            raise Exception('no element or document provided')

    def createElement(self, **kwargs):
        self.element = self.document.createElement(kwargs['tagName'])
        if kwargs.get('value') != None:
            self.element.appendChild(self.document.createTextNode(str(kwargs['value'])))

    def loadElement(self): pass


class ftpNamedElement(ftpElement):
    def __init__(self, **kwargs):
        ftpElement.__init__(self, **kwargs)

    def createElement(self, **kwargs):
        ftpElement.createElement(self, **kwargs)
        if kwargs.get('name'):
            self.name = kwargs['name']

    @property
    def name(self):
        return self.element.getAttribute('Name')
    @name.setter
    def name(self, value):
        self.element.setAttribute('Name', str(value))


class ftpOptionElement(ftpNamedElement):
    def __init__(self, **kwargs):
        ftpNamedElement.__init__(self, tagName='Option', **kwargs)

    @property
    def value(self):
        return self.element.firstChild.nodeValue if self.element.firstChild and self.element.firstChild.data else None
    @value.setter
    def value(self, value):
        if self.element.firstChild:
            self.element.removeChild(self.element.firstChild)
        self.element.appendChild(self.document.createTextNode(str(value)))


class ftpSettingElement(ftpNamedElement):
    def __init__(self, **kwargs):
        self.options = {}
        ftpNamedElement.__init__(self, **kwargs)

    def loadElement(self):
        for element in self.element.childNodes:
            try:
                if element.tagName == 'Option':
                    option = ftpOptionElement(element=element)
                    self.options[option.name] = option
            except AttributeError: pass

    def getOption(self, name):
        return self.options[name].value if self.options.has_key(name) else None
    def getYesNoOption(self, name):
        return YESNO_OPTIONS[self.getOption(name)]

    def setOption(self, name, value):
        if self.options.has_key(name):
            self.options[name].value = value
        else:
            self._addOption(name, value)
    def setYesNoOption(self, name, value):
        self.setOption(name, YESNO_VALUES[value])

    def _addOption(self, name, value=''):
        if name in self.options.keys(): raise Exception('option %s already exists' % name)
        option = ftpOptionElement(document=self.document, name=name, value=value)
        self.element.appendChild(option.element)
        self.options[option.name] = option
        return option


class ftpPermission(ftpSettingElement):
    def __init__(self, **kwargs):
        ftpSettingElement.__init__(self, tagName='Permission', **kwargs)
        self._loadAliases()

    def createElement(self, **kwargs):
        ftpElement.createElement(self, **kwargs)
        if kwargs.get('directory'):
            self.directory = kwargs['directory']
        self.setYesNoOption('FileRead', True)
        self.setYesNoOption('FileWrite', True)
        self.setYesNoOption('FileDelete', False)
        self.setYesNoOption('FileAppend', False)
        self.setYesNoOption('DirCreate', False)
        self.setYesNoOption('DirDelete', False)
        self.setYesNoOption('DirList', True)
        self.setYesNoOption('DirSubdirs', True)
        self.setYesNoOption('IsHome', True)
        self.setYesNoOption('AutoCreate', False)

    def addAlias(self, alias):
        if alias in self.aliases: raise Exception('alias \'%s\' already exists' % alias)
        aliasElement = self.document.createElement('Alias')
        aliasElement.appendChild(self.document.createTextNode(alias))
        self.aliasesElement.appendChild(aliasElement)
        self.aliases.append(alias)

    @property
    def directory(self):
        return self.element.getAttribute('Dir')
    @directory.setter
    def directory(self, value):
        self.element.setAttribute('Dir', str(value))

    @property
    def ishome(self):
        return self.getYesNoOption('IsHome')
    @ishome.setter
    def ishome(self, value):
        self.setYesNoOption('IsHome', value)

    @property
    def fileread(self):
        return self.getYesNoOption('FileRead')
    @fileread.setter
    def fileread(self, value):
        self.setYesNoOption('FileRead', value)

    @property
    def filewrite(self):
        return self.getYesNoOption('FileWrite')
    @filewrite.setter
    def filewrite(self, value):
        self.setYesNoOption('FileWrite', value)

    @property
    def filedelete(self):
        return self.getYesNoOption('FileDelete')
    @filedelete.setter
    def filedelete(self, value):
        self.setYesNoOption('FileDelete', value)

    @property
    def fileappend(self):
        return self.getYesNoOption('FileAppend')
    @fileappend.setter
    def fileappend(self, value):
        self.setYesNoOption('FileAppend', value)

    @property
    def dircreate(self):
        return self.getYesNoOption('DirCreate')
    @dircreate.setter
    def dircreate(self, value):
        self.setYesNoOption('DirCreate', value)

    @property
    def dirdelete(self):
        return self.getYesNoOption('DirDelete')
    @dirdelete.setter
    def dirdelete(self, value):
        self.setYesNoOption('DirDelete', value)

    def _loadAliases(self):
        try:
            self.aliasesElement = self.element.getElementsByTagName('Aliases')[0]
        except IndexError:
            self.aliasesElement = self.document.createElement('Aliases')
            self.element.appendChild(self.aliasesElement)
        self.aliases = []
        for aliasElement in self.aliasesElement.getElementsByTagName('Alias'):
            self.aliases.append(aliasElement.firstChild.data)


class ftpSpeedLimit(object):
    def __init__(self, element):
        self.element = element

    @property
    def dltype(self):
        return self.element.getAttribute('DlType')
    @dltype.setter
    def dltype(self, value):
        self.element.setAttribute('DlType', str(value))

    @property
    def dllimit(self):
        return self.element.getAttribute('DlLimit')
    @dllimit.setter
    def dllimit(self, value):
        self.element.setAttribute('DlLimit', str(value))

    @property
    def dlbypass(self):
        return self.element.getAttribute('ServerDlLimitBypass')
    @dlbypass.setter
    def dlbypass(self, value):
        self.element.setAttribute('ServerDlLimitBypass', str(value))

    @property
    def ultype(self):
        return self.element.getAttribute('UlType')
    @ultype.setter
    def ultype(self, value):
        self.element.setAttribute('UlType', str(value))

    @property
    def ullimit(self):
        return self.element.getAttribute('UlLimit')
    @ullimit.setter
    def ullimit(self, value):
        self.element.setAttribute('UlLimit', str(value))

    @property
    def ulbypass(self):
        return self.element.getAttribute('ServerUlLimitBypass')
    @ulbypass.setter
    def ulbypass(self, value):
        self.element.setAttribute('ServerUlLimitBypass', str(value))


class ftpSecurityBase(ftpSettingElement):
    def __init__(self, **kwargs):
        ftpSettingElement.__init__(self, **kwargs)
        self._loadPermissions()
        self._loadSpeedLimit()

    def createElement(self, **kwargs):
        ftpSettingElement.createElement(self, **kwargs)
        self.setYesNoOption('Bypass server userlimit', None if kwargs.get('default') else False)
        self.setYesNoOption('Enabled', None)
        self.setOption('Comments', '')
        self.setYesNoOption('ForceSsl', None if kwargs.get('default') else False)

    def addPermission(self, directory):
        if directory in self.permissions.keys(): raise Exception('permission for \'%s\' already exists' % directory)
        permission = ftpPermission(document=self.document, directory=directory)
        self.permissionsElement.appendChild(permission.element)
        self.permissions[permission.directory] = permission
        return permission

    def clearPermissions(self):
        for permissionNode in self.permissionsElement.getElementsByTagName('Permission'):
            self.permissionsElement.removeChild(permissionNode)
        self.permissions = {}

    @property
    def enabled(self):
        return self.getYesNoOption('Enabled')
    @enabled.setter
    def enabled(self, value):
        self.setYesNoOption('Enabled', value)

    @property
    def comments(self):
        comments = self.getOption('Comments')
        return comments if comments else ''
    @comments.setter
    def comments(self, value):
        self.setOption('Comments', value)

    def _loadPermissions(self):
        try:
            self.permissionsElement = self.element.getElementsByTagName('Permissions')[0]
        except IndexError:
            self.permissionsElement = self.document.createElement('Permissions')
            self.element.appendChild(self.permissionsElement)
        self.permissions = {}
        for permissionElement in self.permissionsElement.getElementsByTagName('Permission'):
            permission = ftpPermission(element=permissionElement)
            self.permissions[permission.directory] = permission

    def _loadSpeedLimit(self):
        try:
            speedLimitElement = self.element.getElementsByTagName('SpeedLimits')[0]
        except IndexError:
            speedLimitElement = self.document.createElement('SpeedLimits')
            self.element.appendChild(speedLimitElement)
        self.speedLimit = ftpSpeedLimit(speedLimitElement)


class ftpGroup(ftpSecurityBase):
    def __init__(self, **kwargs):
        ftpSecurityBase.__init__(self, tagName='Group', **kwargs)


class ftpUser(ftpSecurityBase):
    def __init__(self, **kwargs):
        ftpSecurityBase.__init__(self, tagName='User', **kwargs)

    def createElement(self, **kwargs):
        ftpSecurityBase.createElement(self, default=True, **kwargs)

    def setPassword(self, password):
        self.setOption('Pass', hashlib.md5(password).hexdigest() if password else '')

    @property
    def group(self):
        return self.getOption('Group')
    @group.setter
    def group(self, value):
        self.setOption('Group', value)


class ftpSettings:
    def __init__(self, config_path, exe_path):
        self.config_path = config_path
        self.exe_path = exe_path
        self.load()

    def load(self):
        fp = open(self.config_path, 'rb')
        self.document = xml.dom.minidom.parseString(fp.read())
        fp.close()
        self.element = self.document.documentElement
        self._loadGroups()
        self._loadUsers()

    def apply(self):
        fp = open(self.config_path, 'wb')
        fp.write(self.document.toxml())
        fp.close()
        call([self.exe_path, RELOAD_COMMAND_ARGS])
        
    def addGroup(self, name):
        if name.lower() in self.groups.keys(): raise GroupExistsError(name)
        group = ftpGroup(document=self.document, name=name)
        self.groupsElement.appendChild(group.element)
        self.groups[group.name.lower()] = group
        return group
        
    def addUser(self, name):
        if name.lower() in self.users.keys(): raise UserExistsError(name)
        user = ftpUser(document=self.document, name=name)
        self.usersElement.appendChild(user.element)
        self.users[user.name.lower()] = user
        return user

    def removeGroup(self, name):
        group = self.groups[name.lower()]
        self.groupsElement.removeChild(group.element)
        del self.groups[name.lower()]

    def removeUser(self, name):
        user = self.users[name.lower()]
        self.usersElement.removeChild(user.element)
        del self.users[name.lower()]

    def _loadGroups(self):
        try:
            self.groupsElement = self.element.getElementsByTagName('Groups')[0]
        except IndexError:
            self.groupsElement = self.document.createElement('Groups')
            self.element.appendChild(self.groupsElement)
        self.groups = {}
        for groupElement in self.groupsElement.getElementsByTagName('Group'):
            group = ftpGroup(element=groupElement)
            self.groups[group.name.lower()] = group

    def _loadUsers(self):
        try:
            self.usersElement = self.element.getElementsByTagName('Users')[0]
        except IndexError:
            self.usersElement = self.document.createElement('Users')
            self.element.appendChild(self.usersElement)
        self.users = {}
        for userElement in self.usersElement.getElementsByTagName('User'):
            user = ftpUser(element=userElement)
            self.users[user.name.lower()] = user

class UserExistsError(Exception):
    def __init__(self, user_name):
        Exception.__init__(self, 'User already exists: %s' % user_name)
        self.user_name = user_name

class GroupExistsError(Exception):
    def __init__(self, group_name):
        Exception.__init__(self, 'Group already exists: %s' % group_name)
        self.group_name = group_name