#!/usr/bin/python

#-----------------------------------------------------------------
# author:   dawid.koszewski@nokia.com
# date:     2019.10.28
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# set absolute path to your zutil or pass it as second parameter to this script
#-----------------------------------------------------------------
path_to_zutil = 'C:\zutil\zutil.exe'


import sys
import re
import os
import time
import subprocess


if len(sys.argv) == 3:
    path_to_zutil = sys.argv[2]

filename = sys.argv[1]

print('filename passed to script:\n%s\n' % (filename))
time.sleep(1)

if re.search('SRM-rfsw-image-install_z-uber-', filename):
    filenamePrepend = 'SRM-rfsw-image-install_z-uber-0x'
    filenameAppend = '.tar'

    output = subprocess.check_output('%s adler32 %s' % (path_to_zutil, filename)).decode(sys.stdout.encoding).strip()
    print('zutil output:\n%s\n' % (output))

    checksum = re.sub(r'.*(\()(0x)([a-fA-F0-9]{8})(\))', r'\3', output).upper()
    #print('calculated checksum: %s\n' % (checksum))
    time.sleep(1)

    filenameNew = os.path.dirname(filename) + '\\' + filenamePrepend + checksum + filenameAppend

    if os.path.isfile(filename) :
        os.rename(filename, filenameNew)
    else:
        print('failed to rename file')

    if os.path.isfile(filenameNew) and os.path.getsize(filenameNew) > 0:
        print('new filename:\n%s\n' % (filenameNew))
        time.sleep(1)
        print ('\n\n\n/============================================\\\n|                                            |\n|                                            |\n|------- FILE RENAMED SUCCESSFULLY!!! -------|\n|                                            |\n|                                            |\n\\============================================/\n\n')
    time.sleep(3)

else:
    print('\nERROR: select proper SRM image file\n')
    time.sleep(3)
    sys.exit()
