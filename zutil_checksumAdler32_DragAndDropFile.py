#!/usr/bin/python

#-----------------------------------------------------------------
# author:   dawid.koszewski.01@gmail.com
# date:     2019.10.28
# update:   2019.12.16
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# HOW TO RUN SCRIPT in windows environment
#-----------------------------------------------------------------
#
# You can simply drag and drop file onto this script...
#
# Or you can add this script as Total Commander button (to simply select a file you want to rename and then click on a button)
#
# 1. Click Configuration -> Buttor Bar
# 2. Button bar: -> Add
# 3. As Command: "python" and "path to this script" (for example: python C:\zutil_checksumAdler32_DragAndDropFile.py)
# 4. As Parameters: %P%N
# 5. Click OK and you will see new button (you can also select new icon)
# 6. Now simply select file containing checksum and then click on newly created button to rename file with newly calculated checksum
#
#-----------------------------------------------------------------

import os
import re
import stat
import sys
import time
#import zlib    #imported below in try except block

#-------------------------------------------------------------------------------


#===============================================================================
# python version global variables
#===============================================================================

PYTHON_MAJOR = sys.version_info[0]
PYTHON_MINOR = sys.version_info[1]
PYTHON_PATCH = sys.version_info[2]

def printDetectedAndSupportedPythonVersion():
    if((PYTHON_MAJOR == 2 and PYTHON_MINOR == 6 and PYTHON_PATCH >= 6)
    or (PYTHON_MAJOR == 2 and PYTHON_MINOR == 7 and PYTHON_PATCH >= 4)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 3 and PYTHON_PATCH >= 5)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 4 and PYTHON_PATCH >= 5)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 5 and PYTHON_PATCH >= 2)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR >= 6)):
        print("\ndetected python version: %d.%d.%d [SUPPORTED]\n(tested in 2.6.6, 2.7.4, 3.3.5, 3.8.0)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    elif (PYTHON_MAJOR >= 4):
        print("\ndetected python version: %d.%d.%d [PROBABLY SUPPORTED]\n(tested in 2.6.6, 2.7.4, 3.3.5, 3.8.0)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    else:
        print("\ndetected python version: %d.%d.%d [NOT TESTED]\n(it is highly recommended to upgrade to 2.6.6, 2.7.4, 3.3.5, 3.8.0 or any newer)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    print("please do not hesitate to contact: dawid.koszewski@nokia.com\n\n")

printDetectedAndSupportedPythonVersion()

#-------------------------------------------------------------------------------


#===============================================================================
# python implementation of zlib.adler32 library
#===============================================================================

def adler32(buffer, checksum): #probably the Fastest pure Python Adler32 in the West (FPAW)
    sum2 = (checksum >> 16) & 0xffff;
    adler = checksum & 0xffff;

    # step = 256 #256 max for adler-=65521 version (256*255+1 = 65281 so adler modulo can be skipped)
    # i = 0
    buffer = bytearray(buffer)
    for byte in buffer:
        adler += byte
        sum2 += adler
        # i += 1
        # if i>= step:
            # # if adler >= 65521:
                # # adler -= 65521
            # adler %= 65521
            # sum2 %= 65521
            # i = 0
    # # if adler >= 65521:
        # # adler -= 65521
    adler %= 65521
    sum2 %= 65521

    return (sum2 << 16) | adler


def adler32_naive(buffer, checksum):
    sum2 = (checksum >> 16) & 0xffff;
    adler = checksum & 0xffff;
    buffer = bytearray(buffer)
    for byte in buffer:
        adler = (adler + byte) % 65521
        sum2 = (sum2 + adler) % 65521
    return (sum2 << 16) | adler


adler32_function = adler32

try:
    import zlib
    adler32_function = zlib.adler32
except (ImportError, Exception) as e:
    print("\nWARNING: %s\nscript will use python implementation of adler32 algorithm..." % e)
    adler32_function = adler32

#-------------------------------------------------------------------------------


#===============================================================================
# utility functions
#===============================================================================

def pressEnterToExit():
#1.
    # try:
        # raw_input("\nPress Enter to exit...\n") #python2 only
    # except (SyntaxError, Exception) as e:
        # input("\nPress Enter to exit...\n") #python3 only
#2.
    try:
        input("\nPress Enter to exit...\n") #python3 only
    except (SyntaxError, Exception) as e:
        pass
    time.sleep(1)
    sys.exit()


def pressCtrlCOrEnterToContinue():
#1.
    # try:
        # raw_input("\nPress Enter to continue...\n") #python2 only
    # except (SyntaxError, Exception) as e:
        # input("\nPress Enter to continue...\n") #python3 only
#2.
    try:
        input("\nPress CTRL+C to ABORT NOW or Press Enter to continue...\n")  #python3 only
    except (SyntaxError, Exception) as e:
        pass
    time.sleep(1)


def renameFile(pathToFileOld, pathToFileNew):
    try:
        os.rename(pathToFileOld, pathToFileNew)
    except (OSError) as e:
        print("\nFile rename ERROR: renameFile(e1) %s - %s" % (e.filename, e.strerror))
        pressEnterToExit()
    except (Exception) as e:
        print("\nFile rename ERROR: renameFile(e2) %s" % (e))
        pressEnterToExit()


def getLastModificationTime(pathToFile):
    secondsSinceEpoch = 0
    try:
        secondsSinceEpoch = os.path.getmtime(pathToFile)
    except (OSError) as e:
        print("\nGetting file info ERROR: getLastModificationTime(e) %s - %s" % (e.filename, e.strerror))
    return secondsSinceEpoch


def getLastModificationTimeAsString(pathToFile):
    return time.ctime(getLastModificationTime(pathToFile))


def getFileSize(pathToFile):
    fileSize = 1
    try:
        fileSize = os.stat(pathToFile).st_size
    except (OSError, IOError, Exception) as e:
        print("\nGetting file info ERROR: getFileSize(e) %s" % (e))
    if fileSize <= 0:
        fileSize = 1
    return fileSize


def checkIfSymlinkAndGetRelativePath(pathToFile):
    if os.path.islink(pathToFile):
        pathtoDir = os.path.dirname(pathToFile)
        pathInSymlink = os.readlink(pathToFile)
        pathToFile = os.path.normpath(os.path.join(pathtoDir, pathInSymlink))
#### OR simply:
        #pathToFile = os.path.realpath(pathToFile)

        if not os.path.isfile(pathToFile):
            print("file that is being pointed to by symlink does not exist anymore: %s" % pathFromSymlink)
    return pathToFile

#-------------------------------------------------------------------------------


#===============================================================================
# functions to print progress bar
#===============================================================================

def getUnit(variable):
    try:
        units = ['kB', 'MB', 'GB', 'TB'] #Decimal Prefixes - The SI standard http://wolfprojects.altervista.org/articles/binary-and-decimal-prefixes/
        variableUnit = ' B'
        for unit in units:
            if variable >= 1000:
                variable /= 1000
                variableUnit = unit
            else:
                break
        #which translates to:
        # i = 0
        # while variable >= 1000 and i < len(units):
            # variable /= 1000
            # variableUnit = units[i] #"damn I miss array[i++] style syntax" - Dawid Koszewski, AD 2019
            # i += 1
    except (Exception) as e:
        print("\nProgress bar ERROR: getUnit(e) %s" % (e))
    return variable, variableUnit


def printProgressBar(copied, fileSize, speedCurrent = 1000000.0, speedAverage = 1000000.0):
    try:
        percent = (copied / (fileSize * 1.0)) # multiplication by 1.0 needed for python 2
        if percent > 1.0:
            percent = 1.0
        dataLeft = (fileSize - copied) #Bytes
        timeLeftSeconds = (dataLeft / speedAverage) #Seconds
        timeLeftHours = (timeLeftSeconds / 3600)
        timeLeftSeconds = (timeLeftSeconds % 3600)
        timeLeftMinutes = (timeLeftSeconds / 60)
        timeLeftSeconds = (timeLeftSeconds % 60)

        #padding = len(str(int(fileSize)))
        copied, copiedUnit = getUnit(copied)
        fileSize, fileSizeUnit = getUnit(fileSize)
        speedCurrent, speedCurrentUnit = getUnit(speedCurrent)

        symbolDone = '='
        symbolLeft = '-'
        sizeTotal = 20
        sizeDone = int(percent * sizeTotal)

        sizeLeft = sizeTotal - sizeDone
        progressBar = '[' + sizeDone*symbolDone + sizeLeft*symbolLeft + ']'
        sys.stdout.write('\r%3d%% %s [%3.1d%s/%3.1d%s]  [%6.2f%s/s] %3.1dh%2.2dm%2.2ds' % (percent*100, progressBar, copied, copiedUnit, fileSize, fileSizeUnit, speedCurrent, speedCurrentUnit, timeLeftHours, timeLeftMinutes, timeLeftSeconds))
        sys.stdout.flush()
        #time.sleep(0.05) #### DELETE AFTER DEVELOPMENT ##########################################################################################################
    except (Exception) as e:
        print("\nProgress bar ERROR: printProgressBar(e) %s" % (e))


def handleProgressBarWithinLoop(vars, buffer, fileSize):
    try:
    #------------------------------------------
    # less readable and probably slower version
    #------------------------------------------
        # vars['timeNow'] = time.time()
        # vars['timeNowData'] += len(buffer)
    # #update Current Speed
        # if vars['timeNow'] >= (vars['timeMark'] + vars['time_step']):
            # vars['timeDiff'] = vars['timeNow'] - vars['timeMark']
            # if vars['timeDiff'] == 0:
                # vars['timeDiff'] = 0.1
            # vars['dataDiff'] = vars['timeNowData'] - vars['timeMarkData']
            # vars['timeMark'] = vars['timeNow']
            # vars['timeMarkData'] = vars['timeNowData']
            # vars['speedCurrent'] = (vars['dataDiff'] / vars['timeDiff']) #Bytes per second
    # #update Average Speed and print progress
        # if vars['timeNowData'] >= (vars['dataMark'] + vars['data_step']):
            # vars['timeDiff'] = vars['timeNow'] - vars['timeStarted']
            # if vars['timeDiff'] == 0:
                # vars['timeDiff'] = 0.1
            # vars['dataMark'] = vars['timeNowData']
            # vars['speedAverage'] = (vars['timeNowData'] / vars['timeDiff']) #Bytes per second
    # except (Exception) as e:
        # print("\nProgress bar ERROR: handleProgressBarWithinLoop(e) %s" % (e))
    # #print progress
    # printProgressBar(vars['timeNowData'], fileSize, vars['speedCurrent'], vars['speedAverage'])


    #------------------------------------------
    # more readable and probably faster version
    #------------------------------------------

    #----------------------------
    # get values from list
    #----------------------------
        timeStarted     = vars[0]
        data_step       = vars[1]
        dataMark        = vars[2]
        time_step       = vars[3]
        timeMark        = vars[4]
        timeMarkData    = vars[5]
        timeNow         = vars[6]
        timeNowData     = vars[7]
        speedCurrent    = vars[8]
        speedAverage    = vars[9]
    #----------------------------

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

    #----------------------------
    # update list
    #----------------------------
        vars[2] = dataMark
        vars[4] = timeMark
        vars[5] = timeMarkData
        vars[6] = timeNow
        vars[7] = timeNowData
        vars[8] = speedCurrent
        vars[9] = speedAverage
    #----------------------------

    except (Exception) as e:
        print("\nProgress bar ERROR: handleProgressBarWithinLoop(e) %s" % (e))
    #print progress
    printProgressBar(timeNowData, fileSize, speedCurrent, speedAverage)


def initProgressBarVariables():
    try:
        # progressBarVars = {}

        # progressBarVars['timeStarted'] = time.time()
        # progressBarVars['data_step'] = 131072
        # progressBarVars['dataMark'] = 0

        # progressBarVars['time_step'] = 1.0
        # progressBarVars['timeMark'] = time.time()
        # progressBarVars['timeMarkData'] = 0
        # progressBarVars['timeNow'] = 0.0
        # progressBarVars['timeNowData'] = 0
        # progressBarVars['speedCurrent'] = 1048576.0
        # progressBarVars['speedAverage'] = 1048576.0

        progressBarVars = [1.0] * 10

        timeStarted = time.time()
        data_step = 256*1024
        dataMark = 0

        time_step = 1.0
        timeMark = time.time()
        timeMarkData = 0
        timeNow = 0.0
        timeNowData = 0
        speedCurrent = 1000*1000.0
        speedAverage = 1000*1000.0

        progressBarVars[0] = timeStarted
        progressBarVars[1] = data_step
        progressBarVars[2] = dataMark
        progressBarVars[3] = time_step
        progressBarVars[4] = timeMark
        progressBarVars[5] = timeMarkData
        progressBarVars[6] = timeNow
        progressBarVars[7] = timeNowData
        progressBarVars[8] = speedCurrent
        progressBarVars[9] = speedAverage

    except (Exception) as e:
        print("\nProgress bar ERROR: initProgressBarVariables(e) %s" % (e))
    return progressBarVars

#-------------------------------------------------------------------------------


#===============================================================================
# functions to calculate checksum and get new file name
#===============================================================================

def getNewChecksumFileName(fileName, fileMatcher, checksumAsHex):
    fileNameNew = ""
    fileNamePrepend = fileMatcher.sub(r'\1', fileName)
    fileNameAppend = fileMatcher.sub(r'\3', fileName)
    checksumAsHexUpper = checksumAsHex.upper()
    fileNameNew = fileNamePrepend + checksumAsHexUpper + fileNameAppend
    return fileNameNew


def getChecksumAsHex(checksum):
    #checksumFormatted = '0x' + hex(checksum)[2:] #in python 2.7.14 it appends letter L
    checksumHex = "%x" % checksum
    return checksumHex.zfill(8)


def getChecksum(pathToFile):
    checksum = 1 #initialize with 1
    if os.path.isfile(pathToFile):
        try:
            f = open(pathToFile, 'rb')
            #print("calculating checksum...")
            fileSize = getFileSize(pathToFile)

            try:
                progressBarVars = initProgressBarVariables()

                while 1:
                    buffer = f.read(1024*1024) #default 64*1024 for linux (SLOW), 1024*1024 for windows (FAST also on linux)
                    if not buffer:
                        break
                    checksum = adler32_function(buffer, checksum)

                    handleProgressBarWithinLoop(progressBarVars, buffer, fileSize)
                printProgressBar(progressBarVars[7], fileSize, progressBarVars[8], progressBarVars[9])
                print()

                f.close()
                checksum = checksum & 0xffffffff
            except (OSError, IOError) as e:
                print("\nCalculate checksum ERROR: getChecksum(e1) %s - %s" % (e.filename, e.strerror))
            finally:
                f.close()
        except (Exception) as e:
            print ("\nCalculate checksum ERROR: getChecksum(e2) %s" % (e))
    else:
        print('\nERROR: getChecksum(e3) Could not find file to calculate checksum')
    return checksum

#-------------------------------------------------------------------------------


#===============================================================================
# function to get path to file passed to this script as first parameter
#===============================================================================

def getPathToFileNew(pathToFile, fileName, fileMatcher, checksumAsHex):
    pathToFileNew = ""
    checksumOld = fileMatcher.sub(r'\2', fileName)
    index = fileName.find(checksumOld)
    padding = ' ' * index
    fileNameNew = getNewChecksumFileName(fileName, fileMatcher, checksumAsHex)
    #print("\nCurrent checksum has been matched as [ %s ]" % (matchStrictResult.group(2)))
    print("\n%s   [ OLD ]" % (fileName))
    print("%s   [ NEW ]" % (fileNameNew))
    print("%s^^^^^^^^" % (padding))
    print("Do you want to rename this part of file to new checksum?\n")
    pressCtrlCOrEnterToContinue()
    pathToFileNew = os.path.join(os.path.dirname(pathToFile), fileNameNew)
    return pathToFileNew


def handleParameterPassedToScript(fileMatcherChecksumStrict, fileMatcherChecksumRelaxed):
    if len(sys.argv) > 1:
        pathToFile = sys.argv[1]
        pathToFileNew = ""
        print('file passed to script:\n%s' % (pathToFile))
        pathToFile = checkIfSymlinkAndGetRelativePath(pathToFile)

        if os.path.isfile(pathToFile):
            print('modified: %s\n' % (getLastModificationTimeAsString(pathToFile)))
            checksum = getChecksum(pathToFile)
            checksumAsHex = getChecksumAsHex(checksum)
            print("adler32 checksum: %d (0x%s)\n" % (checksum, checksumAsHex))
            fileName = os.path.basename(pathToFile)

            matchStrictResult = fileMatcherChecksumStrict.search(fileName)
            if matchStrictResult:
                pathToFileNew = getPathToFileNew(pathToFile, fileName, fileMatcherChecksumStrict, checksumAsHex)
            else:
                matchRelaxedResult = fileMatcherChecksumRelaxed.search(fileName)
                if matchRelaxedResult:
                    pathToFileNew = getPathToFileNew(pathToFile, fileName, fileMatcherChecksumRelaxed, checksumAsHex)
                else:
                    print('\nERROR: If you want to rename file - please select a file containing checksum in its name\n')
                    pressEnterToExit()
        else:
            print('\nERROR: please select existing file\n')
            pressEnterToExit()
    else:
        print("\nPlease pass a path to file as first parameter to this script...\nYou can do this by simply drag and drop a file directly onto this script \"*.py\" file\n")
        pressEnterToExit()
    return pathToFile, pathToFileNew

#-------------------------------------------------------------------------------


#===============================================================================
# === MAIN FUNCTION ===
#===============================================================================

def main():

    fileMatcherChecksumStrict = re.compile(r'(.*0x)([a-fA-F0-9]{8})(.*)')
    fileMatcherChecksumRelaxed = re.compile(r'(.*)([a-fA-F0-9]{8})(.*)')

    pathToFile, pathToFileNew = handleParameterPassedToScript(fileMatcherChecksumStrict, fileMatcherChecksumRelaxed)
    renameFile(pathToFile, pathToFileNew)
    if not os.path.isfile(pathToFileNew) or not os.path.getsize(pathToFileNew) > 0:
        print("Something went wrong. File not renamed correctly")
    else:
        print('%s file renamed to:\n%s\n\n' % (pathToFile, pathToFileNew))


if __name__ == '__main__':
    main()
    pressEnterToExit()
