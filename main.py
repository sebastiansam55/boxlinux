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
global folderid
folderid = str(0)




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
	print("	0. Go To Download options")
	print("\t1. Change Directory")
	print("\t2. Upload File")
	print("\t3. Delete File")
	print("\t4. Delete Folder")
	print("\t5. Make URL for file")
	print("\t6. Test Method")
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
	request = urllib2.Request("https://api.box.com/2.0/folders/"+folderid+".xml", None, headers)
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
	rawinput = int(raw_input("Select a file to download: "))
	if command_check(rawinput):
		return
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
	#this will be replaced with a file write method deally
	filename = get_file_name(filenumber)
	f = open(filename, 'w+')
	print("Writing")
	f.write(filerecieved)
	f.close()

def get_file_name(filenumber):
	dom = parseString(rootxml)
	nameofitem = dom.getElementsByTagName('file')[filenumber].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
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
	folderid_ = dom.getElementsByTagName('folder')[int(folderlistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	return folderid_
		
	
def errprint(printthis):	
	print("[ERROR] "+printthis)
	
def varprint(printthis):
	print("[VARCHECK] "+str(printthis))
	
def cdchoices():
	global folderid
	global rootxml
	print_folder_list(0)
	#have to convert to int after becuase int() throws error when not actually int
	rawinput = raw_input("Which folder to cd to?")
	if command_check(rawinput):
		return
	folderid = get_folder_id(int(rawinput))
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
		
def upload():
	print "Upload method placeholder"
	
def uploadchoices():
	print "Uploadchoices method placeholder"
		
def test():
	print_file_list(-1)
	getfileurl(0)
	
	
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
		
		
##all of the delete methods need SHA1SUM's of the file that they are deleting! ARGGGGG
##the sha1sum is given in the <etag> in the xml folder listing
def deletefilechoice():
	print "deletefilechoice place holder"
	
def deletefile():
	print "Deletefile place holder"
	
def deletefolderchoice():
	print "deletefolderchoice place holder"
	
def deletefolder():
	print "deletefolder placeholder"
	
def fileurlchoices():
	print("fileurlchoices placeholder")
	#the -1 is so that the list starts with 0
	#done for consistency more than anything else
	print_file_list(-1)
	rawinput = raw_input("Which file to get URL for? (give the number)")
	fileid = get_file_id(rawinput)
	getfileurl(fileid)

##right now this returns 400 bad request error code
##BUT I KNOW I'M CLOSE!
##it might have to do with the httplib and the https
##it def has to do with the Content Lenght thingy
def getfileurl(fileid):
	fileid = str(fileid)
	headers = {'Content-length' : '0', 'Content-Type' : 'application/json', 'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,} #'shared_link' : {'access' : 'Open'},}
	data = {'shared_link' : {'access' : 'Open'}}
	data = urllib.urlencode(data)
	conn = httplib.HTTPSConnection('api.box.com')
	conn.request('PUT', '/2.0/files/'+fileid, data, headers)
	##.read() turns it from object to text
	response = conn.getresponse().read()
	print response
		
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
