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

filePath = sys.argv[1]
print('file path passed to script:\n%s\n' % (filePath))
filename = os.path.basename(filePath)


if os.path.isfile(filePath):
    if re.search(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', filename):

        zutilOutput = subprocess.check_output('%s adler32 %s' % (path_to_zutil, filePath)).decode(sys.stdout.encoding).strip()
        print('zutil output:\n%s\n' % (zutilOutput))

        filenamePrepend = re.sub(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', r'\1', filename)
        filenameAppend = re.sub(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', r'\4', filename)
        checksumNew = re.sub(r'.*(\()(0x)([a-fA-F0-9]{8})(\))', r'\3', zutilOutput).upper()
        filePathNew = os.path.dirname(filePath) + '\\' + filenamePrepend + '0x' + checksumNew + filenameAppend

        os.rename(filePath, filePathNew)

        if os.path.isfile(filePathNew) and os.path.getsize(filePathNew) > 0:
            print('new file path:\n%s\n' % (filePathNew))
            print ('\n\n\n/============================================\\\n|                                            |\n|                                            |\n|------- FILE RENAMED SUCCESSFULLY!!! -------|\n|                                            |\n|                                            |\n\\============================================/\n\n')
        time.sleep(1)

    else:
        print('\nERROR: please select proper file containing checksum in its name\n')
        time.sleep(3)
else:
    print('\nERROR: please select existing file\n')
    time.sleep(3)

sys.exit()
