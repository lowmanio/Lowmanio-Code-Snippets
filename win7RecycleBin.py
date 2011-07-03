#################################
#								#
#	Win7RecycleBin.py			#
#	(c) Sarah Lowman 2011		#
#								#
#################################

from datetime import datetime
import os
import csv

# change this if you have a different recycle bin location. In this folder
# should be a folder for each user SID on the machine with their recycled
# files.
recycle_folder = r'C:\$RECYCLE.BIN' 

def convert_little_endian(num_bytes, f):
	""" num_bytes is the number of bytes to read 
	from the open file f that are in little endian format. 
	Returns the result as a decimal number. """
	
	bytes = []
	for i in xrange(0,num_bytes):
		bytes.append(f.read(1).encode("hex"))
	bytes.reverse()
	return int("".join([hex for hex in bytes]),16)

def get_deleted_metadata(file_name, record):
	""" Populates 'record' with deleted file info from a file 
	named 'file_name' """
	
	try:
		with open(file_name,"rb") as f:
			# first 8 bytes is a header
			header = f.read(8)
			
			# next 8 bytes in the file size in bytes - little endian
			record['File Size (bytes)'] = convert_little_endian(8, f)
			
			# next 8 bytes is date deleted in Windows timestamp - little
			# endian ( seconds since Jan 1st 1601)
			date_convert = convert_little_endian(8, f)
			diff_epoch = 116444736000000000L 
			epoch = (date_convert - diff_epoch)/10000000
			record['Date deleted'] = datetime.utcfromtimestamp(epoch)
			
			# rest of the bytes is the original path
			final_path = ""
			file_path = f.read(1) 
			while file_path != "":
				if int(file_path.encode("hex"),16) != 0:
					final_path = final_path + file_path
				file_path = f.read(1) 
			record['Original path'] = final_path
	except IOError, e:
		pass

def get_recycled_files(files_in_folder, recycled_files,type='file'):
	""" Given the list of files 'files_in_folder', populates the dict
	'recycled_files' with an entry for each deleted file. The Key is the 
	unique string Win7 gives to deleted files, and Value is a tuple of
	the name of the file with the deleted file metadata and a dictionary of 
	the metadata """
	
	for file in files_in_folder:
		if file.startswith('$R'):
			unique_string = file[2:].split('.')[0]
			recycled_files[unique_string] = ('$I'+file[2:], {'Type':type})
	
def convert_to_csv(recycle_info, user):
	""" Converts the dictionary of all the deleted file data 'recycle_info'
	for the user 'user' into a CSV file """
	
	csv_writer = csv.writer(open(user+'_recycle_bin.csv','wb'))
	csv_writer.writerow(['Type','Original Path','Size (bytes)','Date Deleted (UTC)','Location of deleted file'])
	for recycled in recycle_info:
		csv_writer.writerow([recycle_info[recycled][1]['Type'],
							recycle_info[recycled][1]['Original path'],
							recycle_info[recycled][1]['File Size (bytes)'],
							recycle_info[recycled][1]['Date deleted'].strftime("%d-%m-%Y %H:%M:%S"),
							os.path.join(recycle_folder,user,recycle_info[recycled][0])])
	
users = os.walk(recycle_folder).next()[1]	# get the User SIDs

# for each user, make a CSV file with all the deleted file information in it
for user_recycle_bin in users:
	recycled_files = {}	
	user_recycle_dir = os.path.join(recycle_folder, user_recycle_bin)
	try:
		_, recycled_folders, files_in_folder = os.walk(user_recycle_dir).next()
	except Exception:
		continue
	
	get_recycled_files(files_in_folder, recycled_files)
	get_recycled_files(recycled_folders, recycled_files, type='folder')

	for file, (name, info) in recycled_files.iteritems():
		get_deleted_metadata(os.path.join(user_recycle_dir, name), info)
		
	convert_to_csv(recycled_files,user_recycle_bin)

