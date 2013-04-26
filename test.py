import sys
import os

import pyFileZilla

def print_usage():
    print "Usage: %s [FileZilla path]" % (sys.argv[0])


def test_groups(settings):
    print "Testing groups"
    print "=============="
    try:
        groups = settings.groups
    except Exception, err:
        print "Could not load groups: %s" % err


if __name__ == '__main__':
    print "Testing pyFileZilla version %s" % pyFileZilla.VERSION
    print "==============================="
    if (len(sys.argv) != 2):
        print_usage()
        sys.exit(1)
    filezilla_path = sys.argv[1]
    if not os.path.isdir(filezilla_path):
        print "Could not find FileZilla path: %s" % filezilla_path
        print_usage()
        sys.exit(1)
    try:
        settings = pyFileZilla.ftpSettings(os.path.join(filezilla_path, 'FileZilla Server.xml'), os.path.join(filezilla_path, 'FileZilla server.exe'))
        print "ftpSettings loaded"
        print "=================="
        test_groups(settings)
    except Exception, err:
        print "Could not load ftpSettings object %s" % err
        sys.exit(2)
