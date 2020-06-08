#!/usr/bin/python

#-----------------------------------------------------------------
# author:   dawid.koszewski@nokia.com
# date:     2019.10.28
# update:   2019.11.21
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

import os
import re
import stat
import sys
import time

try:
    import zlib
except (ImportError, Exception) as e:
    print("\n%s\n" % e)


PYTHON_MAJOR = sys.version_info[0]
PYTHON_MINOR = sys.version_info[1]
PYTHON_PATCH = sys.version_info[2]

def printDetectedAndSupportedPythonVersion():
    if((PYTHON_MAJOR == 2 and PYTHON_MINOR == 6 and PYTHON_PATCH >= 6)
    or (PYTHON_MAJOR == 2 and PYTHON_MINOR == 7 and PYTHON_PATCH >= 4)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 4 and PYTHON_PATCH >= 5)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 5 and PYTHON_PATCH >= 2)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR >= 6)):
        print("\ndetected python version: %d.%d.%d [SUPPORTED]" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    else:
        print("\ndetected python version: %d.%d.%d [NOT TESTED]\n(it is highly recommended to upgrade to 2.6.6, 2.7.4, 3.4.5, 3.5.2 or any newer)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))


def getUnit(variable):
    units = ['kB', 'MB', 'GB', 'TB']
    variableUnit = ' B'
    for unit in units:
        if variable > 1000:
            variable /= 1024
            variableUnit = unit
        else:
            break
    return variable, variableUnit


def printProgress(copied, fileSize, speedCurrent = 1048576.0, speedAverage = 1048576.0):
    percent = (copied / fileSize) * 100
    if percent > 100.0:
        percent = 100.0
    dataLeft = (fileSize - copied) #Bytes
    timeLeftSeconds = (dataLeft / speedAverage) #Seconds

    timeLeftHours = timeLeftSeconds / 3600
    timeLeftSeconds = timeLeftSeconds % 3600
    timeLeftMinutes = timeLeftSeconds / 60
    timeLeftSeconds = timeLeftSeconds % 60

    #padding = len(str(int(fileSize)))
    copied, copiedUnit = getUnit(copied)
    fileSize, fileSizeUnit = getUnit(fileSize)
    speedCurrent, speedCurrentUnit = getUnit(speedCurrent)

    symbolDone = '='
    symbolLeft = '-'
    sizeTotal = 20
    sizeDone = int((percent / 100) * sizeTotal)
    sizeLeft = sizeTotal - sizeDone
    progressBar = '[' + sizeDone*symbolDone + sizeLeft*symbolLeft + ']'
    sys.stdout.write('\r%3d%% %s [%3.1d%s/%3.1d%s]  [%6.2f%s/s] %3.1dh%2.2dm%2.2ds' % (percent, progressBar, copied, copiedUnit, fileSize, fileSizeUnit, speedCurrent, speedCurrentUnit, timeLeftHours, timeLeftMinutes, timeLeftSeconds))
    sys.stdout.flush()


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
        try:
            f = open(pathToFile, 'rb')
            checksum = 1
            print("calculating checksum...")

            fileSize = 1
            try:
                fileSize = os.stat(pathToFile).st_size
            except (OSError, IOError, Exception) as e:
                print("\nGetting file info ERROR: %s" % (e))
            if fileSize <= 0:
                fileSize = 1
            timeStarted = time.time()
            data_step = 131072
            dataMark = 0
            time_step = 1.0
            timeMark = time.time()
            timeMarkData = 0
            timeNow = 0
            timeNowData = 0
            speedCurrent = 1048576.0
            speedAverage = 1048576.0

            try:
                while 1:
                    buffer = f.read(128*1024)
                    if not buffer:
                        break
                    checksum = zlib.adler32(buffer, checksum)

                    timeNow = time.time()
                    timeNowData += len(buffer)
                #update Current Speed
                    if timeNow >= (timeMark + time_step):
                        timeDiff = timeNow - timeMark
                        if timeDiff == 0:
                            timeDiff = 0.1
                        dataDiff = timeNowData - timeMarkData
                        timeMark = timeNow
                        timeMarkData = timeNowData
                        speedCurrent = (dataDiff / timeDiff) #Bytes per second
                #update Average Speed and print progress
                    if timeNowData >= (dataMark + data_step):
                        timeDiff = timeNow - timeStarted
                        if timeDiff == 0:
                            timeDiff = 0.1
                        dataMark = timeNowData
                        speedAverage = (timeNowData / timeDiff) #Bytes per second
                #print progress
                        printProgress(timeNowData, fileSize, speedCurrent, speedAverage)
                printProgress(timeNowData, fileSize, speedCurrent, speedAverage)
                print()

                f.close()
                checksum = checksum & 0xffffffff
                fileNamePrepend = re.sub(fileMatcher, r'\1', pathToFile)
                fileNameAppend = re.sub(fileMatcher, r'\4', pathToFile)
                #checksumFormatted = '0x' + (hex(checksum)[2:].zfill(8)).upper() #in python 2.7.14 it appends letter L
                checksumHex = "%x" % checksum
                checksumFormatted = '0x' + ((checksumHex.zfill(8)).upper())
                fileNameNew = fileNamePrepend + checksumFormatted + fileNameAppend
            except (OSError, IOError) as e:
                print("\nCalculate checksum ERROR: %s - %s" % (e.filename, e.strerror))
            finally:
                f.close()

        except (Exception) as e:
            print ("\nCalculate checksum ERROR: %s" % (e))
    else:
        print('\nERROR: Could not find file to calculate checksum\n')
    return fileNameNew


def renameFile(pathToFile, pathToFileNew):
    try:
        print('renaming to:\n%s\n' % (pathToFileNew))
        os.rename(pathToFile, pathToFileNew)
        if not os.path.isfile(pathToFileNew) or not os.path.getsize(pathToFileNew) > 0:
            print("Something went wrong. File not renamed correctly")
    except OSError as e:
        print("File rename ERROR: %s - %s.\n" % (e.filename, e.strerror))


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
        else:
            print('\nERROR: please select existing file\n')
    else:
        print("\nPath to file was not passed as first argument\n")
    time.sleep(1)
    sys.exit()
    return "" #just in case


def main():
    printDetectedAndSupportedPythonVersion()

    fileMatcher = r'(.*)(0x)([a-fA-F0-9]{1,8})(.*)'
    pathToFile = handleParameterPassedToScript(fileMatcher)
    fileNameNew = getChecksum(pathToFile, fileMatcher)
    renameFile(pathToFile, os.path.join(os.path.dirname(pathToFile), fileNameNew))



if __name__ == '__main__':
    main()
    time.sleep(2)
    sys.exit()
