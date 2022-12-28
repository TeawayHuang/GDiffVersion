import argparse
import csv
from filecmp import dircmp

def result_diff_files(dcmp, ver1, ver2, writer):
    for name in dcmp.diff_files:
        print("diff_file: %s, found in %s and %s" % (name, dcmp.left,
            dcmp.right))
        writer.writerow([name, 'diff', dcmp.left + ' and ' +dcmp.right])

    for name in dcmp.left_only:
        print("ver1 only: %s, found in %s" % (name, dcmp.left))
        writer.writerow([name, ver1, dcmp.left])

    for name in dcmp.right_only:
        print("ver2 only: %s, found in %s" % (name, dcmp.right))
        writer.writerow([name, ver2, dcmp.right])
    
    for sub_dcmp in dcmp.subdirs.values():
        result_diff_files(sub_dcmp, ver1, ver2, writer)

def parse_diff_folders(dcmp, ver1, ver2):
    with open('result.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(['name', 'diff or existed only', 'path'])
        result_diff_files(dcmp, ver1, ver2, writer)

#Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument('--ver1', type=str, default="")
parser.add_argument('--ver2', type=str, default="")

args = parser.parse_args()

ver1 = args.ver1
ver2 = args.ver2

print("Diff version: %s and %s" % (ver1, ver2))
print("=======================================================")

dcmp = dircmp(ver1, ver2) 
parse_diff_folders(dcmp, ver1, ver2) 