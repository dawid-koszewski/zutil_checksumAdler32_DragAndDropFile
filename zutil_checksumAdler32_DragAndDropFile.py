#!/usr/bin/python

#-----------------------------------------------------------------
# author:   dawid.koszewski@nokia.com
# date:     2019.10.28
# update:   2019.11.06
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# HOW TO RUN SCRIPT in windows environment
#-----------------------------------------------------------------
#
# You can add this script as Total Commander button (to simply select file and then click button)
#
# 1. Click Configuration -> Buttor Bar
# 2. Button bar: -> Add
# 3. As Command: python and path to this script (for example: python C:\zutil_checksumFilePassedAsArgument.py)
# 4. As Parameters: %P%N
# 5. Click OK and you will see new button (you can also select new icon)
# 6. Now simply select file containing checksum and then click on newly created button to rename file with new checksum
#
#-----------------------------------------------------------------


import sys
import re
import os
import time
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


def getChecksum(pathToFile, fileMatcher):
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

        fileNamePrepend = re.sub(fileMatcher, r'\1', pathToFile)
        fileNameAppend = re.sub(fileMatcher, r'\4', pathToFile)
        checksumNew = re.sub(fileMatcher, r'\3', hex(checksum)).upper()
        fileNameNew = fileNamePrepend + '0x' + checksumNew + fileNameAppend
    else:
        print('\nERROR: Could not find file to calculate checksum\n')
    return fileNameNew


def renameFile(pathToFile, pathToFileNew):
    try:
        os.rename(pathToFile, pathToFileNew)
    except OSError as e:
        print("File rename ERROR: %s - %s.\n" % (e.filename, e.strerror))

    if os.path.isfile(pathToFileNew) and os.path.getsize(pathToFileNew) > 0:
        print('\nrenamed to:\n%s\n\n' % (pathToFileNew))
        print('\n/============================================\\\n|                                            |\n|                                            |\n|------- FILE RENAMED SUCCESSFULLY!!! -------|\n|                                            |\n|                                            |\n\\============================================/\n\n')
    else:
        print("Something went wrong. File not renamed correctly")


def handleParameterPassedToScript(fileMatcher):
    if len(sys.argv) > 1:
        pathToFile = sys.argv[1]
        print('\nfile passed to script:\n%s' % (pathToFile))
        print('modified: %s\n' % (getLastModificationTimeAsString(pathToFile)))
        if os.path.isfile(pathToFile):
            if re.search(fileMatcher, os.path.basename(pathToFile)):
                return pathToFile
            else:
                print('\nERROR: please select proper file containing checksum in its name\n')
                time.sleep(1)
                sys.exit()
        else:
            print('\nERROR: please select existing file\n')
    else:
        print("\nPath to file was not passed as first argument\n")
    time.sleep(1)
    sys.exit()
    return ""


def main():
    fileMatcher = r'(.*)(0x)([a-fA-F0-9]{8})(.*)'
    pathToFile = handleParameterPassedToScript(fileMatcher)
    fileNameNew = getChecksum(pathToFile, fileMatcher)
    renameFile(pathToFile, os.path.join(os.path.dirname(pathToFile), fileNameNew))



if __name__ == '__main__':
    main()
    time.sleep(2)
    sys.exit()
