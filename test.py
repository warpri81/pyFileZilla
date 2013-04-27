import os
import unittest

import pyFileZilla


CONFIG_FILE_NAME = "temp.xml"
FILEZILLA_SERVER_XML = r"""<?xml version="1.0"?><FileZillaServer><Settings></Settings><Groups></Groups><Users></Users></FileZillaServer>"""


class TestAddingData(unittest.TestCase):
    def testAddUser(self):
        settings = pyFileZilla.ftpSettings(CONFIG_FILE_NAME, None)
        user = settings.addUser('test')
        self.assertIsInstance(user, pyFileZilla.ftpUser)
        self.assertRaises(pyFileZilla.UserExistsError, settings.addUser, 'TEST')

    def testAddGroup(self):
        settings = pyFileZilla.ftpSettings(CONFIG_FILE_NAME, None)
        group = settings.addGroup('test')
        self.assertIsInstance(group, pyFileZilla.ftpGroup)
        self.assertRaises(pyFileZilla.GroupExistsError, settings.addGroup, 'TEST')

    
if __name__ == '__main__':
    config_file = file(CONFIG_FILE_NAME, 'wb')
    config_file.write(FILEZILLA_SERVER_XML)
    config_file.close()
    unittest.main()
    os.remove(CONFIG_FILE_NAME)
