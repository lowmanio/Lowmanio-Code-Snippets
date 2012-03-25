import time
import os

file1 = "file1"
file2 = "file2"
file_tmp = "file0"
wait_period = 20 # seconds between creating 1st and 2nd files

def run_test(rename_delay, rename=True):
    """ Parameters:
    rename_delay - the amount of seconds delay between deleting/renaming 
    1st file and renaming 2nd file as the 1st file. 
    rename - True if you want to rename 1st file as a temp file, or False if 
    you want to delete the first file."""
    
    # remove old files
    if os.path.exists(file1):
        os.remove(file1)
    if os.path.exists(file_tmp):
        os.remove(file_tmp)
        
    print "\nRunning test\n============"
    
    # create the original file
    with open(file1, 'w') as file_1:
        file_1.write('First file')
    print "File '{}' created at {}".format(file1, os.path.getctime(file1))
        
    # wait
    print "Waiting {} seconds".format(wait_period)
    time.sleep(wait_period)

    # create second file
    with open(file2, 'w') as file_2:
        file_2.write('Second file')
    print "File '{}' created at {}".format(file2, os.path.getctime(file2))
    
    if rename:
        # rename first file to tmp file
        os.rename(file1, file_tmp)
        print "File '{}' renamed to '{}'".format(file1, file_tmp)
    else:
        # or delete the 1st file
        os.remove(file1)
        print "File '{}' deleted".format(file1)
        
    # wait
    print "Waiting {} seconds".format(rename_delay)
    time.sleep(rename_delay)
    
    # rename second file as first file 
    os.rename(file2, file1)
    print "File '{}' renamed to '{}'".format(file2, file1)

    if rename:
        print "File '{}' created at {}".format(file_tmp, os.path.getctime(file_tmp))
    print "File '{}' created at {}".format(file1, os.path.getctime(file1))
    
run_test(0, True)
run_test(14, True)
run_test(14.9, False)
run_test(15, False)