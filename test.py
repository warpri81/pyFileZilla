import os
from StringIO import StringIO
import xml.dom.minidom
import unittest

import pyFileZilla


class TestSanity(unittest.TestCase):
    def testWrite(self):
        settings = pyFileZilla.ftpSettings()
        output = StringIO()
        settings.write(output)
        xmldoc = xml.dom.minidom.parseString(output.getvalue())
        self.assertEqual(xmldoc.documentElement.tagName, "FileZillaServer")


class TestAddingData(unittest.TestCase):
    def testAddUser(self):
        settings = pyFileZilla.ftpSettings()
        user = settings.addUser('test')
        self.assertIsInstance(user, pyFileZilla.ftpUser)
        self.assertRaises(pyFileZilla.UserExistsError, settings.addUser, 'TEST')

    def testAddGroup(self):
        settings = pyFileZilla.ftpSettings()
        group = settings.addGroup('test')
        self.assertIsInstance(group, pyFileZilla.ftpGroup)
        self.assertRaises(pyFileZilla.GroupExistsError, settings.addGroup, 'TEST')

    
if __name__ == '__main__':
    unittest.main()
    os.remove(CONFIG_FILE_NAME)
