#!/usr/bin/python

#-----------------------------------------------------------------
# author:   dawid.koszewski@nokia.com
# date:     2019.10.28
#-----------------------------------------------------------------

import sys
import re
import os
import time
import subprocess
import zlib


def getLastModificationTime(pathToFile):
    secondsSinceEpoch = 0
    try:
        secondsSinceEpoch = os.path.getmtime(pathToFile)
    except OSError as e:
        print("Getting file info ERROR: %s - %s.\n" % (e.filename, e.strerror))
    return secondsSinceEpoch


def getLastModificationTimeAsString(pathToFile):
    return time.ctime(getLastModificationTime(pathToFile))


def getChecksum(pathToFile):
    fileNameNew = ""
    if os.path.isfile(pathToFile):
        f = open(pathToFile, 'rb')
        checksum = 1
        buffer = f.read(1024)
        while buffer: #len(buffer) > 0:
            checksum = zlib.adler32(buffer, checksum)
            buffer = f.read(1024)
        f.close()

        checksum = checksum & 0xffffffff
        #print("%d %s" % (checksum, (hex(checksum))))

        fileNamePrepend = re.sub(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', r'\1', pathToFile)
        fileNameAppend = re.sub(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', r'\4', pathToFile)
        checksumNew = re.sub(r'.*(0x)([a-fA-F0-9]{8}).*', r'\2', hex(checksum)).upper()
        fileNameNew = fileNamePrepend + '0x' + checksumNew + fileNameAppend
    else:
        print('\nERROR: Could not find new stratix image file to calculate checksum\n')
    return fileNameNew


def renameFile(pathToFile, pathToFileNew):
    try:
        os.rename(pathToFile, pathToFileNew)
    except OSError as e:
        print("File rename ERROR: %s - %s.\n" % (e.filename, e.strerror))

    if os.path.isfile(pathToFileNew) and os.path.getsize(pathToFileNew) > 0:
        print('\n\n\n === new Stratix file ===\n\n%s\n' % (pathToFileNew))
        print(' --- file last modified: %s ---\n' % (getLastModificationTimeAsString(pathToFileNew)))
        print('\n/============================================\\\n|                                            |\n|                                            |\n|------- FILE CREATED SUCCESSFULLY!!! -------|\n|                                            |\n|                                            |\n\\============================================/\n\n')
    else:
        print("Something went wrong. New Stratix file not generated correctly")


def main():
    pathToFile = sys.argv[1]
    print('file path passed to script:\n%s\n' % (pathToFile))
    if os.path.isfile(pathToFile):
        fileName = os.path.basename(pathToFile)
        pathToDir = os.path.dirname(pathToFile)
        if re.search(r'(.*)(0x)([a-fA-F0-9]{8})(.*)', fileName):
            fileNameNew = getChecksum(pathToFile)
            renameFile(pathToFile, os.path.join(pathToDir, fileNameNew))
        else:
            print('\nERROR: please select proper file containing checksum in its name\n')
            time.sleep(3)
    else:
        print('\nERROR: please select existing file\n')
        time.sleep(3)


if __name__ == '__main__':
    main()
    time.sleep(3)
    sys.exit()
