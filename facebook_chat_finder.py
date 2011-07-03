import os
import re
import shutil
import csv
from datetime import datetime

# change this to where the temporary internet files are kept
temp_internet_files_loc = r"c:\Users\Sarah\AppData\Local\Microsoft\Windows\Temporary Internet Files"

# regular expressions to make facebook chat files
facebook_reg = re.compile(r'\Ap\_(\d)+(\S)*\.(txt|htm)\Z')
message_ref = re.compile(r'\Afor \(\;\;\)\;{"t":"msg","c":"\S+","s":\d+,"ms":\[\{"msg":\{"text":"(.*?)","time":(\d+),"clientTime":(\d+),"msgID":"(\d+)"\},"from":(\d+),"to":(\d+),"from_name":"(.*?)","from_first_name":"(\S+)","type":"msg","fl":\S+,"to_name":"(.*?)","to_first_name":"(\S+)"\}\]\}\Z')

total_found = 0
results = None

def check_format(file):
	"""
		Opens the file given and checks it matches the Facebook chat regular expression. 
		If so, returns the Facebook chat fields.
	"""
	with open(file, 'r') as f:
		line = f.read()
		result = message_ref.match(line)
		if result is not None:	
			message, time, clientTime, msgID, from_, to, from_name, from_first_name, \
			to_name, to_first_name = result.group(1,2,3,4,5,6,7,8,9,10)
			return message, time, clientTime, from_, to, from_name, to_name

		else:
			return None
			

if __name__ == "__main__":

	# get the full path of the folder results will be stored in
	dest = raw_input("\nPath of folder to write results to: ")
	
	if os.path.exists(dest):
		# open a CSV file and write Facebook chat headers
		results = csv.writer(open(os.path.join(dest, 'facebook_chat_messages.csv'), 'wb'), 
								delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		results.writerow(['UTC Time', 'UTC Formatted Time', 'Users Time', 'Users Formatted Time', 
						  'From FB ID', 'From Name', 'To FB ID', 'To Name', 'Message Sent'])

		# walk through the temporary internet files folder and look at each file
		for root, dirs, files in os.walk(temp_internet_files_loc):
			for file in files:
				# if it matches the facebook file name format:
				if facebook_reg.match(file):
					src = os.path.join(root, file)
					msg_tuple = check_format(src) # check the file is a facebook chat file
					if msg_tuple is not None:
						# format date/times correctly
						client_time = datetime.fromtimestamp(float(msg_tuple[2])/1000.00).strftime("%d/%m/%Y %H:%M:%S")
						time = datetime.fromtimestamp(float(msg_tuple[1])/1000.00).strftime("%d/%m/%Y %H:%M:%S")
						# write a row to the CSV file
						results.writerow([float(msg_tuple[2])/1000.00, time, float(msg_tuple[2])/1000.00, 
							client_time, msg_tuple[3], msg_tuple[5], msg_tuple[4], msg_tuple[6], msg_tuple[0]])
						dst = os.path.join(dest, file)
						# copy the original Facebook file to results folder
						shutil.copy(src, dst)
						total_found = total_found + 1
					
		print "\nTotal facebook chat messages found: %s\n" % total_found
		print r"Messages found and a summary CSV file added to: %s" % dest

	else:
		print "\nInvalid folder! Exiting."