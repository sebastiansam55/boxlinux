#!/usr/bin/env python
##Right now this was written/run/tested with python 2.7
##I know that one of the major changes there is between 2.7 and later ones is that print is a function
##feel free to submit any patches if you are so possessed :)

##I am also very inconsistent i sometimes do get_file_name or downloadchoices or deleteFile i don't have a preference if someone wants to do all that work ;)

#For communicating with the BOX APIs
import urllib2
#have to use something else to do PUT's and DELETE's
import httplib
#for encoding (not sure if necessary)
import urllib
#AARGG XML!
from xml.dom.minidom import parseString
#I don't think that this is necessary atm
import sys
#for checking for file exsistance
import os
#for the response from the BOX APIS
import json
#for hashing files for delete and download checking
import sha
#should convert all internet communication to pycurl
import pycurl
#used to read from pycurl (saw in tut on sourceforge)
import StringIO
#used for tempfiles...
import tempfile

#hopefully the solution to all my problems
import requests##helper methods!
import helper


#do globals have to be declared outside of methods?
global xmlfolderlist
#this is gonna get confusing!
global itemlist
itemlist = []
#BoxyLinux API-KEY
global apikey
apikey = "l7c2il3sxmetf2ielkyxbvc2k4nqqkm4"
#global xml for procesing ie the root folder xml info
global rootxml
#change this whenever change folders
#whenever this is updated the rootxml needs to be too!
global glo_folderid
glo_folderid = str(0)




#Should rearrange MAIN loop 
#maybe have option to look for system arguments and send it one way or the other?
def main():
	if int(len(sys.argv))==1:
		if not firstrun():
			print("Have you approved this app for use? [Y/n]")
			yorn = raw_input()
			if yorn=='Y'or yorn=='y':			
				print("Loading Settings")
				load_settings()
			else:
				authenticate()
				print("Open this link in browser and confirm!")
				print("https://www.box.com/api/1.0/auth/"+ticket)
				raw_input("Press enter when approved")
				get_auth_token()
			
		else:
			print("Loading settings")
			load_settings()	
		loop()
		return 0
	else:
		shellhelper()
		
		
def loop():
	global rootxml
	rootxml = get_folder_list()
	print("	0. Download")
	print("\t1. Change Directory")
	print("\t2. Upload File")
	print("\t3. Delete File")
	print("\t4. Delete Folder")
	print("\t5. Make URL for file")
	print("\t6. Upload File")
	print("\t7. Test Method")
	#rawinput should be int
	#int() is a lifesaver!
	rawinput = raw_input("What would you like to do?")
	if command_check(rawinput):
		return
	rawinput = int(rawinput)
	if rawinput==0:
		downloadchoices()
	elif rawinput==1:
		cdchoices()
	elif rawinput==2:
		uploadchoices()
	elif rawinput==3:
		deletefilechoice()
	elif rawinput==4:
		deletefolderchoice()
	elif rawinput==5:
		fileurlchoices()		
	elif rawinput==6:
		uploadchoices()
	elif rawinput==7:
		test()
	else:
		loop()
		

#not actually ~authenticating~ more like preping to authenticate	
def authenticate():
	response = urllib2.urlopen("https://www.box.com/api/1.0/rest?action=get_ticket&api_key="+apikey)
	xml = response.read()
	dom = parseString(xml)
	global ticket
	ticket = dom.getElementsByTagName('ticket')[0].toxml()
	#gets rid of the XML tags!
	ticket = ticket.replace('<ticket>', '').replace("</ticket>","")
	return ticket
	
def save_ticket():
	#the ~/ DOES NOT WORK, should substutie something else like a $USER
	f = open('/home/sam/.boxlinux', 'w')
	f.write(ticket)
	f.close()
	
def save_settings(setting):
	#the ~/ DOES NOT WORK, should substutie something else like a $USER
	f = open('/home/sam/.boxlinux', 'a')
	f.write(setting)
	f.close()
	
def load_settings():
	#the ~/ DOES NOT WORK, should substutie something else like a $USER
	f = open('/home/sam/.boxlinux', 'r')
	global auth_token
	auth_token = f.readline()
	
def save_auth_token():
	#the ~/ DOES NOT WORK, should substutie something else like a $USER
	f = open('/home/sam/.boxlinux', 'w')
	f.write(auth_token)
	f.close()	
	
	
def firstrun():
	return os.path.exists('~/.boxlinux')
	
	
def get_auth_token():
	response = urllib2.urlopen("https://www.box.com/api/1.0/rest?action=get_auth_token&api_key="+apikey+"&ticket="+ticket)
	xml = response.read()
	dom = parseString(xml)	
	global auth_token
	auth_token = dom.getElementsByTagName('auth_token')[0].toxml()
	#get rid of those nasty XML tags!
	auth_token = auth_token.replace('<auth_token>', '').replace("</auth_token>", "")
	save_auth_token()

##this causes so many headaches... it's not just a folder list...
def get_folder_list():
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	#root folder of the BOX account is refered to as "0" 
	#appending .xml to the end of requests will make the API return XML!
	request = urllib2.Request("https://api.box.com/2.0/folders/"+glo_folderid+".xml", None, headers)
	response = urllib2.urlopen(request)
	global xmlfolderlist
	xmlfolderlist = response.read()
	return xmlfolderlist
	
	
	#where path will usually be ~/Box
	#should also have ability to read option from file
def foldercraft(path):
	#I *think* that this will check for both exsisteance of file and folder?
	if not os.path_exists(path):
		#this might be the right way?
		os.mkdirs(path)
	else:
		print ""
		
		
def print_folder_list(itemcnt):
	itemcnt = int(itemcnt)
	#this will be BIG method!
	#how will this work as a daemon??
	xml = get_folder_list()
	dom = parseString(xml)
	#number of items in the folder
	#should this be in it's own method?
	#the two .replace-s should be in their own method!
	noofitems = dom.getElementsByTagName('total-count')[0].toxml().replace('<total-count>', '').replace('</total-count>', '')
	i=0
	bol = True
	#maybe but in another method and then have a while true with return?
	print "FOLDERS:"
	while bol:
		#folder 0 is root in the XML
		try:
			nameoffolder = dom.getElementsByTagName('folder')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
			fileid = dom.getElementsByTagName('folder')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			i+=1
			print `itemcnt`+" "+nameoffolder + " ("+fileid+")"
			itemcnt = itemcnt+1
		except:
			bol = False	
			print "End of Folders!"
	return itemcnt

def print_file_list(itemcnt):
	itemcnt = int(itemcnt)
	dom = parseString(rootxml)		
	print "############################"
	print "FILES: "
	bol = True
	i=0
	while bol:
		try:
			nameofitem = dom.getElementsByTagName('file')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
			fileid = dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			i+=1
			itemcnt = itemcnt+1
			print `itemcnt`+" "+nameofitem+" ("+fileid+")"
		except:
			print "End of Items!"
			bol=False
	
def downloadchoices():
	#itemcnt = print_folder_list(itemcnt)-1
	print_file_list(-1)
	#have to convert to int after command_check in case it's a char or string
	print("Select 'all' to download all of the files listed")
	rawinput = raw_input("Select a file to download: ")
	if command_check(rawinput):
		return
	elif str(rawinput)=="all" or str(rawinput)=="ALL":
		fileids = get_all_file_id()
		download_all(fileids)
	else:
		download(int(rawinput))
	##return to main loop?
	loop()
	
##the /content!
def download(filenumber):
	#BOX API reference refers to /content?version=numberhere i have no idea where that number comes from
	#I assume that it has to do with the way that BOX does multiple versions of the file
	#I have no idea if it is necessary tho
	#no need to append the .xml, nothing but the file will be returned here
	#remember the comma at the end!
	fileid = ""
	fileid = str(get_file_id(filenumber))
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	request = urllib2.Request("https://api.box.com/2.0/files/"+fileid+"/content", None, headers)
	response = urllib2.urlopen(request)
	filerecieved = response.read()
	#this will be replaced with a file write method idealy
	filename = get_file_name(fileid)
	f = open(filename, 'w+')
	print("Writing")
	f.write(filerecieved)
	f.close()
	
def download_fileid(fileid):
	fileid=str(fileid)
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	url = "https://api.box.com/2.0/files/"+fileid+"/content"
	r = requests.request("GET", url, None, headers)
	filedata = r.content
	filename = get_file_name(str(fileid))
	f = open(filename, 'w')
	f.write(filedata)
	f.close()

def get_file_name(fileid):
	dom = parseString(rootxml)
	i=0
	while i<=len(dom.getElementsByTagName('file')):
		try:
			if dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>','').replace('</id>','')==fileid:
				nameofitem = dom.getElementsByTagName('file')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
				return nameofitem
			else:
				i=i+1
		except:
			return
	#nameofitem = dom.getElementsByTagName('file')[filenumber].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
	return nameofitem
	
def get_file_id(filelistno):
	dom = parseString(rootxml)
	varprint(filelistno)
	try:
		fileid = dom.getElementsByTagName('file')[int(filelistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	except:
		errprint("file might not exsist")
	varprint(fileid)
	return fileid
	
def get_folder_id(folderlistno):
	dom = parseString(rootxml)
	#under score because of the global var w/ same name
	glo_folderid_ = dom.getElementsByTagName('folder')[int(folderlistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	return glo_folderid_
			
def cdchoices():
	global glo_folderid
	global rootxml
	print_folder_list(0)
	#have to convert to int after becuase int() throws error when not actually int
	rawinput = raw_input("Which folder to cd to?")
	if command_check(rawinput):
		return
	glo_folderid = get_folder_id(int(rawinput))
	rootxml = get_folder_list()
	itemcnt = print_folder_list(0)
	##should be removed after testing ?? (below i mean)
	print_file_list(int(itemcnt))
	##return to main loop?
	loop()
	
#right now this works because there is only quit command
#if it's going to be command line like there should be something different; don't know quite what yet	
def command_check(rawinput):
	rawinput = str(rawinput)
	if rawinput=='Q' or rawinput=='q':
		return True
		
		
	
#i know that there are whole modules dedicated to this kind of stuff
#i just think that this for the moment might be a bit faster than learning them
def shellhelper():
	#as of right now the best I can do is offer only access to the root
	#should write something that will get the folders and files into an xml file...
	#it could then do some matching to match file names with fileids'
	#some globals will also have to be set/reset... rootxml auth_token etc.
	load_settings() #this will load auth_token
	global rootxml
	rootxml = get_folder_list() ##make the rootxml...
	command = str(sys.argv[1])
	#listed in order of usage (suspected usage at least)
	if command=='-h':
		print "usage boxlinux [option] At this stage only one command at a time will work...."
		print "-h\t\t :will display this help message"
		print "-V\t\t :will display the Version Number"
		print "-u <filename>\t :will upload the specified file to the root dir (unless other wise specified)"
		print "-d <filename>\t :Download the filename... according to the number listed in ls (see below)"
		#print "\t this has to be the first set of commands in the list"
		#print "\t like boxlinux -d <filename>  and not boxlinux -V -d <filename>"
		print "ls\t\t :will display the files and folders in the root dir (unless other wise specified)"
	elif command=='-V':
		print 'Version 0.0.0.1'
	elif command=='ls':
		print_file_list(print_folder_list(0))
	elif command=='-u':
		upload()
	elif command=='-d':
		#right now the method wants a file number according to the number of items and files listed...
		#this will end up being a real headache
		download(sys.argv[2])
	else:
		loop()
		
		
	
def fileurlchoices():
	#the -1 is so that the list starts with 0
	#done for consistency more than anything else
	print_file_list(-1)
	rawinput = raw_input("Which file to get URL for? (give the number)")
	fileid = get_file_id(rawinput)
	getfileurl(fileid)

#this can later be modified to make more complex links with more complex thingys
def getfileurl(fileid):
	fileid = str(fileid)
	url = "https://api.box.com/2.0/files/"+fileid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'shared_link': {'access': 'Open'}}
	r = requests.request("PUT", url, None, json.dumps(payload), headers)
	print r.content
	print json.dumps(payload)	

#says here that the sha1sum is optional for upload!
##IT WORKS!!!!
def upload(filepath, filename, folderid):
	print "Uploading..."
	url = "https://api.box.com/2.0/files/content"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'filename1': filename, 'folder_id': folderid}
	data = {filename: open(filepath, 'r')}
	r = requests.request("POST", url, None, payload, headers, None, data)
	print r.content
	
	
def uploadchoices():
#lists files in folder of place where command was invoked
	print "Choose file to upload"
	filelist = get_local_files()
	i = 0
	for filename in filelist:
		print str(i)+" "+filename
		i=i+1

def deletefilechoice():
	print "deletefilechoice place holder"
	print_file_list()
	
def deletefile():
	print "Deletefile place holder"
	
def deletefolderchoice():
	print "deletefolderchoice place holder"
	
def deletefolder():
	print "deletefolder placeholder"

def get_all_file_id():
	dom = parseString(rootxml)
	cnt = int(dom.getElementsByTagName('total-count')[0].toxml().replace('<total-count>', '').replace('</total-count>', ''))
	varprint(cnt)
	fileid={}
	i=0
	while i<=cnt:
		try:
			fileid[i] = dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			i=i+1
		except:
			errprint("file might not exsist")
			i=cnt+5
	varprint(fileid)
	varprint(fileid[0])
	return fileid





########################################################################
############################WORKING METHODS#############################

def get_sha1sum(filepath):
	f = open(filepath, 'r')
	string = f.read()
	#must be string or buffer not file
	sha1sum = sha.new(string)
	return sha1sum.hexdigest()
	
def get_local_files():
	return os.listdir(os.getcwd())
	
def download_all(file_list):
	for i in file_list:
		varprint(file_list[i])
		download_fileid(file_list[i])



########################################################################
#######################HELPER METHODS###################################

def errprint(printthis):	
	print("[ERROR] "+printthis)
	
def varprint(printthis):
	print("[VARCHECK] "+str(printthis))
	return
	
def test():
	download_all(get_all_file_id())
	
	
def progress(download_t, download_d, upload_t, upload_d):
	print "Total to download", download_t
	print "Total downloaded", download_d
	print "Total to upload", upload_t
	print "Total uploaded", upload_d
	
	
########################################################################
	
##########!!!!!!!!!!!!!!!!!!!!
#don't put anything below this; python will stop loading stuff once it gets to this!
if __name__ == '__main__':
	main()


		
		
	
"""
    BoxLinux; Bringing Box services to the Linux desktop
    Copyright (C) 2012  Sam Sebastian

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""



"""
Dependincies:
python-requests



"""
