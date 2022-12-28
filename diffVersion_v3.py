import os
import time
import argparse
import csv

from filecmp import dircmp
from time import strftime
from time import gmtime
from datetime import datetime, timezone, timedelta
from difflib import Differ

DIFF_LOGS = 'diff_logs/'

COLUMN_FILE_TYPE = 'File Type'
COLUMN_PATH = 'Path'
COLUMN_RK_FILENAME = 'Remark File Name'
COLUMN_RK_FILESIZE = 'Remark File Size'
COLUMN_RK_FILECONTENT = 'Remark File Content'
COLUMN_REALLINK = 'Real Link'
COLUMN_REALLINK_IN = 'Real Link in'

FILE_BROKEN_LINK = 'Broken Link'
FILE_FOLDER = 'Folder'
FILE_FILE = 'File'

STR_SAME = 'same'
STR_DIFF = 'diff'

def check_type(fPath):
    print("check_type path: " + fPath)
    fType = FILE_BROKEN_LINK
    if os.path.isdir(fPath):
        fType = FILE_FOLDER
    
    if os.path.isfile(fPath):
        fType = FILE_FILE

    return fType

def result_diff_files(dcmp, fPath, ver1, ver2, writer):
    for name in dcmp.diff_files:
        print("diff_file: %s, found in %s and %s" % (name, dcmp.left, dcmp.right))
        if os.stat(dcmp.left+'/'+name).st_size == os.stat(dcmp.right+'/'+name).st_size:
            fSize = STR_SAME
        else:
            fSize = STR_DIFF

        fType = check_type(dcmp.left+'/'+name)

        if fType is FILE_FILE:
            logFileName = str(dcmp.right[len(fPath):]+'/'+name).replace('/', '>')
            logFile = os.path.join(DIFF_LOGS, logFileName+'.log')

            with open(dcmp.left+'/'+name, 'rb') as file1, open(dcmp.right+'/'+name, 'rb') as file2, open(logFile, 'w') as f:
                content1 = file1.read()
                content2 = file2.read()

                if content1 == content2:
                    fContent = STR_SAME
                else:
                    fContent = STR_DIFF

            with open(dcmp.left+'/'+name, 'rb') as file1, open(dcmp.right+'/'+name, 'rb') as file2, open(logFile, 'w') as f:
                differ = Differ()

                for line in differ.compare(file1.readlines(), file2.readlines()):
                    f.writelines(line)

                f.close

            realLinkinver1 = os.path.realpath(dcmp.left+'/'+name)
            realLinkinver2 = os.path.realpath(dcmp.right+'/'+name)

            if realLinkinver1 == realLinkinver2:
                realLink = STR_SAME
            else:
                realLink = STR_DIFF
        else:
            fContent = ''
            realLink = ''
            realLinkinver1 = ''
            realLinkinver2 = ''

        writer.writerow([fType, dcmp.left[len(fPath)+len(ver2):], name, name, STR_SAME, fSize, fContent, realLink, realLinkinver1, realLinkinver2])

    for name in dcmp.left_only:
        print("ver1 only: %s, found in %s" % (name, dcmp.left))

        fType = check_type(dcmp.left+'/'+name)

        if fType is FILE_FILE:
            realLink = STR_DIFF
            realLinkinver1 = os.path.realpath(dcmp.left+'/'+name)
        else:
            realLink = ''
            realLinkinver1 = ''
        
        fContent = ''
        realLinkinver2 = ''

        writer.writerow([fType, dcmp.left[len(fPath)+len(ver1):], name, '', STR_DIFF, STR_DIFF, fContent, realLink, realLinkinver1, realLinkinver2])

    for name in dcmp.right_only:
        print("ver2 only: %s, found in %s" % (name, dcmp.right))

        fType = check_type(dcmp.right+'/'+name)

        if fType is FILE_FILE:
            realLink = STR_DIFF
            realLinkinver2 = os.path.realpath(dcmp.right+'/'+name)
        else:
            realLink = ''
            realLinkinver2 = ''
        
        fContent = ''
        realLinkinver1 = ''

        writer.writerow([fType, dcmp.right[len(fPath)+len(ver2):], '', name, STR_DIFF, STR_DIFF, fContent, realLink, realLinkinver1, realLinkinver2])
    
    for sub_dcmp in dcmp.subdirs.values():
        result_diff_files(sub_dcmp, fPath, ver1, ver2, writer)

def parse_diff_folders(dcmp, fPath, folder, ver1, ver2):
    tz = timezone(timedelta(hours=+8))
    dateObject = datetime.now(tz).strftime("%Y-%m-%d")
    csvFileName = 'result_' + folder + '_' + dateObject + '_' + ver1 + '_' + ver2 +'.csv'
    with open(csvFileName, 'w', newline='') as csvfile:
        startTime = time.time()
        writer = csv.writer(csvfile)
        writer.writerow([COLUMN_FILE_TYPE, COLUMN_PATH, ver1, ver2, COLUMN_RK_FILENAME, COLUMN_RK_FILESIZE, COLUMN_RK_FILECONTENT, COLUMN_REALLINK, COLUMN_REALLINK_IN+' '+ ver1, COLUMN_REALLINK_IN+' '+ver2])
        result_diff_files(dcmp, fPath, ver1, ver2, writer)

        print("Time taken for diff:", strftime("%H:%M:%S", gmtime(time.time() - startTime)))

#Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument('--path', type=str, default="")
parser.add_argument('--folder', type=str, default="")
parser.add_argument('--ver1', type=str, default="")
parser.add_argument('--ver2', type=str, default="")

args = parser.parse_args()

fPath = args.path
folder = args.folder
ver1 = args.ver1
ver2 = args.ver2

print("Diff version: %s and %s" % (ver1, ver2))
print("=======================================================")

dcmp = dircmp(fPath+ver1, fPath+ver2) 
parse_diff_folders(dcmp, fPath, folder, ver1, ver2) 