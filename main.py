#!/usr/bin/env python
##Right now this was written/run/tested with python 2.7
##every once in a while i'll run it with python 3 to see if they are still both working
##last time I did it was (10/21/2012)
##another things to do it to take all of the times I've used rawinput as a variable and put more sensible names

##I am also very inconsistent i sometimes do get_file_name or downloadchoices or deleteFile i don't have a preference if someone wants to do all that work ;)

#<3 XML!
from xml.dom.minidom import parseString
#This is used for the command line version of the program
#this is what I'm using atm instead of something like optparse
import sys
#for checking for file exsistance
#also creating folders
import os
#for the response from the BOX APIS
import json
#for hashing files for delete and download checking, also deleting files
import hashlib
#hopefully the solution to all my problems
#this is literally the best module that I have ever used
import requests

##helper methods!
import helper


#do globals have to be declared outside of methods?
global xmlfolderlist
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
			print("Have you approved this app for use? [Y/n/Q]")
			yorn = raw_input()
			if yorn=='Y'or yorn=='y':			
				print("Loading Settings")
				load_settings()
			elif yorn=='q' or yorn=='Q':
				print("Quitting")
				return 0
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
	print("\t5. Make URL for File")
	print("\t6. Make URL for Folder")
	print("\t7. Remove URL for File")
	print("\t8. Remove URL for Folder")
	print("\t9. Make a new Folder")
	print("\t10. Rename a File")
	print("\t11. Rename a Folder")
	print("\t12. List Files in Current Dir") 
	print("\t-1. Test Method")
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
		folder_url_choices()
	elif rawinput==7:
		rm_share_url_file_choices()
	elif rawinput==8:
		rm_share_url_folder_choices()		
	elif rawinput==9:
		new_folder_choices()
	elif rawinput==10:
		rename_file_choices()
	elif rawinput==11:
		rename_folder_choices()
	elif rawinput==12:
		ls()
	elif rawinput==-1:
		test()
	else:
		loop()
		

#not actually ~authenticating~ more like preping to authenticate	
def authenticate():
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_ticket&api_key="+apikey)
	xml = r.content
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
	f.close()
	
def save_auth_token():
	#the ~/ DOES NOT WORK, should substutie something else like a $USER
	f = open('/home/sam/.boxlinux', 'w')
	f.write(auth_token)
	f.close()
	
	
def get_auth_token():
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_auth_token&api_key="+apikey+"&ticket="+ticket)
	xml = r.content
	dom = parseString(xml)	
	global auth_token
	auth_token = dom.getElementsByTagName('auth_token')[0].toxml()
	#get rid of those nasty XML tags!
	auth_token = auth_token.replace('<auth_token>', '').replace("</auth_token>", "")
	save_auth_token()


def get_folder_list():
	url = "https://api.box.com/2.0/folders/"+glo_folderid+".xml"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	#root folder of the BOX account is refered to as "0" 
	#appending .xml to the end of requests will make the API return XML!
	r = requests.request("GET", url, None, None, headers)
	global xmlfolderlist
	xmlfolderlist = r.content
	return r.content
	
	
	#where path will usually be ~/Box
	#should also have ability to read option from file
def foldercraft(path):
	#I *think* that this will check for both exsisteance of file and folder?
	if not os.path.exists(path):
		#this might be the right way?
		os.makedirs(path)
	else:
		print("Folder already exists")
		
		
def print_folder_list(itemcnt):
	itemcnt = int(itemcnt)
	#this will be BIG method!
	#how will this work as a daemon??
	dom = parseString(get_folder_list())
	#number of items in the folder
	#should this be in it's own method?
	#the two .replace-s should be in their own method!
	i=0
	bol = True
	sharebool = False
	#maybe but in another method and then have a while true with return?
	print("FOLDERS:")
	while bol:
		#folder 0 is root in the XML
		try:
			nameoffolder = dom.getElementsByTagName('folder')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
			folderid = dom.getElementsByTagName('folder')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			dom_of_folder = parseString(get_info_folder(folderid))
			try:
				dom_of_folder.getElementsByTagName('shared-link')[0]
				sharebool = True
			except:
				sharebool = False
			i=i+1
			print(str(itemcnt)+" "+nameoffolder +" Shared: "+str(sharebool)+" ("+folderid+")")
			itemcnt = itemcnt+1
		except:
			bol = False	
			print("End of Folders! On the "+str(itemcnt))
	return itemcnt

def print_file_list(itemcnt):
	itemcnt = int(itemcnt)
	dom = parseString(rootxml)		
	print("############################")
	print("FILES: ")
	sharebool = False
	bol = True
	i=0
	while bol:
		try:
			nameofitem = dom.getElementsByTagName('file')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')		
			fileid = dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			dom_of_file = parseString(get_info_file(fileid))
			try:
				dom_of_file.getElementsByTagName('shared-link')[0]
				sharebool = True
			except:
				sharebool = False
			i=i+1
			itemcnt = itemcnt+1
			print(str(itemcnt)+" "+nameofitem+" Shared: "+str(sharebool)+" ("+fileid+")")
		except:
			print("End of Items! On the "+str(itemcnt))
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
	url = "https://api.box.com/2.0/files/"+fileid+"/content"
	r = requests.request("GET", url, None, headers)
	filerecieved = r.content
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
	folderid = dom.getElementsByTagName('folder')[int(folderlistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	return folderid
			
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
		print("usage boxlinux [option] At this stage only one command at a time will work....")
		print("-h\t\t :will display this help message")
		print("-V\t\t :will display the Version Number")
		print("-u <filename>\t :will upload the specified file to the root dir (unless other wise specified)")
		print("-d <filename>\t :Download the filename... according to the number listed in ls (see below)")
		print("ls\t\t :will display the files and folders in the root dir (unless other wise specified)")
		print("-da Will download all the files in the root directory (not yet recursive)")
		print("-mkfolders Makes folders based on Box folders")
	elif command=='-V':
		print('Version 0.0.0.1')
	elif command=='ls':
		print_file_list(print_folder_list(0))
	elif command=='-u':
		upload(sys.argv[2])
	elif command=='-d':
		#this is broken right now?
		download(sys.argv[2])
	elif command=='-da':
		download_all(get_all_file_id())
	elif command=='-mkfolders':
		try:
			#xml = get_folder_list()
			dom = parseString(rootxml)
			icnt=1
			for i in dom.getElementsByTagName('folder'):
				foldername = dom.getElementsByTagName('folder')[icnt].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
				foldercraft("./"+foldername)
				icnt = icnt+1
		except:
			errprint("You might be okay...")
	else:
		loop()
		
		
	
def fileurlchoices():
	#the -1 is so that the list starts with 0
	#done for consistency more than anything else
	print_file_list(-1)
	rawinput = raw_input("Which file to get URL for? (give the number)")
	fileid = get_file_id(rawinput)
	urls = get_file_url(fileid)
	print("Download link: "+urls[0])
	print("Direct Download link: "+urls[1])
	#return to main loop?
	loop()

#this can later be modified to make more complex links with more complex thingys
#needs to be changed so it returns the parsed out link...
def get_file_url(fileid):
	fileid = str(fileid)
	url = "https://api.box.com/2.0/files/"+fileid+".xml"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = "<shared_link><access>Open</access></shared_link>"
	r = requests.request("PUT", url, None, parseString(payload).toxml(), headers)
	#url and download-url
	dom = parseString(r.content)
	return [dom.getElementsByTagName('url')[0].toxml().replace('<url>', '').replace('</url>', ''), dom.getElementsByTagName('download-url')[0].toxml().replace('<download-url>', '').replace('</download-url>', '')]

#says here that the sha1sum is optional for upload!
##IT WORKS!!!!
def upload(filepath, filename, folderid):
	print("Uploading...")
	url = "https://api.box.com/2.0/files/content"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'filename1': filename, 'folder_id': folderid}
	data = {filename: open(filepath, 'r')}
	r = requests.request("POST", url, None, payload, headers, None, data)
	print(r.content)
	
	
def uploadchoices():
#lists files in folder of place where command was invoked
	print("Choose file to upload")
	filelist = get_local_files()
	i = 0
	files = ['']
	for filename in filelist:
		print(str(i)+" "+filename)
		files.append(filename)
		i=i+1
	rawinput = raw_input("What file do you want to upload?")
	upload(os.getcwd()+"/"+files[int(rawinput)+1], files[int(rawinput)], 0)
	loop()

def deletefilechoice():
	print_file_list(-1)
	rawinput = raw_input("File to delete: ")
	fileid = get_file_id(rawinput)
	deletefile(fileid)
	loop()
	
	
def deletefile(fileid):
	sha1sum = get_sha1sum_remote(fileid)
	url = "https://api.box.com/2.0/files/"+fileid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'If-Match': sha1sum}
	r = requests.request("DELETE", url, None, payload, headers)
	print(r.content)
	
	
def deletefolderchoice():
	#instead of -1 should be zero because of the all files thing in all directories
	print_folder_list(0)
	rawinput = raw_input("Folder to delete: ")
	folderid = get_folder_id(rawinput)
	deletefolder(folderid)
	loop()
	
	#it wants the recursive as a addition onto the url... easy enough
def deletefolder(folderid):
	print("Deleting Folder with id "+folderid)
	url = "https://api.box.com/2.0/folders/"+str(folderid)+"?recurive=true"
	varprint(url)
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'recursive': 'true'}
	r = requests.request("DELETE", url, None, None, headers)
	print(r.content)

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

def get_sha1sum_remote(fileid):
	#slight modification of get_file_name or what ever it was 
	dom = parseString(rootxml)
	i=0
	while i<=len(dom.getElementsByTagName('file')):
		try:
			if dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>','').replace('</id>','')==fileid:
				sha1sum = dom.getElementsByTagName('file')[i].getElementsByTagName('etag')[0].toxml().replace('<etag>', '').replace('</etag>', '')
				return sha1sum
			else:
				i=i+1
		except:
			return
			
			
			
def mk_new_folder(foldername, parent_folderid):
	#where folderid is the folder that the new folder is going to be created in ?
	url = "https://api.box.com/2.0/folders/"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'name': ''+foldername+'', 'parent': {'id': '0'}}
	varprint(payload)
	r = requests.request("POST", url, None, json.dumps(payload), headers)
	return r.content
	
def new_folder_choices():
	print("Current Folders:")
	print_folder_list(0)
	newfoldername = raw_input("Name for new folder:")
	parentfolder = raw_input("Parent Folder (0) for root")
	mk_new_folder(newfoldername, get_folder_id(parentfolder))
	loop()
	
def folder_url_choices():
	print_folder_list(0)
	folderid = raw_input("Folder to make new link for: ")
	urls = get_folder_url(get_folder_id(folderid))
	print("Download URL: "+urls[0])
	print("Direct(?) Download URL: "+urls[1]+ " (Pro account might be required)" )
	loop()
	
## this will return url plus list of all files in the folder
## there's a download-url too (i thought that that was only for premium or pro i'm not sure which one it is)
## it will give you a 404 sorta error when you visit the download-url link...
def get_folder_url(folderid):
	url = "https://api.box.com/2.0/folders/"+folderid+".xml"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = "<shared_link><access>Open</access></shared_link>"
	r = requests.request("PUT", url, None, parseString(payload).toxml(), headers)
	dom = parseString(r.content)
	return [dom.getElementsByTagName('url')[0].toxml().replace('<url>', '').replace('</url>', ''), dom.getElementsByTagName('download-url')[0].toxml().replace('<download-url>','').replace('</download-url>','')]
	
	
#you have to send null value for the 'shared_link'!
def rm_share_url_folder(folderid):
	url = "https://api.box.com/2.0/folders/"+folderid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'shared_link': None}
	r = requests.request("PUT", url, None, json.dumps(payload), headers)
	return r.content
	
def rm_share_url_folder_choices():
	print_folder_list(0)
	rawinput = raw_input("Which folder to unshare?")
	rm_share_url_folder(get_folder_id(rawinput))
	loop()
	
def rm_share_url_file_choices():
	print_file_list(0)
	rawinput = raw_input("Which file to unshare?")
	rm_share_url_file(get_file_id(rawinput))
	loop()
	
def rm_share_url_file(fileid):
	url = "https://api.box.com/2.0/files/"+fileid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'shared_link': None}
	r = requests.request("PUT", url, None, json.dumps(payload), headers)
	return r.content
	
	
def get_folder_name(fileid):
	dom = parseString(rootxml)
	i=0
	while i<=len(dom.getElementsByTagName('folder')):
		try:
			if dom.getElementsByTagName('folder')[i].getElementsByTagName('id')[0].toxml().replace('<id>','').replace('</id>','')==fileid:
				nameofitem = dom.getElementsByTagName('folder')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
				return nameofitem
			else:
				i=i+1
		except:
			return
	return nameofitem
	
def rename_file_choices():
	print_file_list(-1)
	filenumber = raw_input("What file to rename? (integer designation): ")
	fileid = get_file_id(filenumber)
	print("Renaming: "+get_file_name(fileid)+" Press Q to stop")
	filename = raw_input("New name for file: ")
	if filename=='q' or filename=='Q':
		return
	rename_file(filename, fileid)	
	loop()
	
def rename_file(newname, fileid):
	url = "https://api.box.com/2.0/files/"+fileid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'name': newname}
	r = requests.request("PUT", url, None, json.dumps(payload), headers)
	return r.content
	
def rename_folder_choices():
	print_folder_list(0)
	foldernumber = raw_input("What folder to rename? (integer designation): ")
	folderid = get_folder_id(foldernumber)
	print("Renaming: "+get_folder_name(folderid)+" Press Q to stop")
	foldername = raw_input("New name for folder: ")
	if foldername=='q' or foldername=='Q':
		return
	rename_folder(foldername, folderid)	
	loop()
	
def rename_folder(newname, folderid):
	url = "https://api.box.com/2.0/folders/"+folderid
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'name': newname}
	r = requests.request("PUT", url, None, json.dumps(payload), headers)
	return r.content




########################################################################
############################WORKING METHODS#############################
#See description of helper methods
#exactly the same except these are mostly mission critical
	
def download_all(file_list):
	for i in file_list:
		varprint(file_list[i])
		download_fileid(file_list[i])
		
def get_info_folder(folderid):
	url = "https://api.box.com/2.0/folders/"+str(folderid)+".xml"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	r = requests.request("GET", url, None, None, headers)
	return r.content
	
def get_info_file(fileid):
	url = "https://api.box.com/2.0/files/"+str(fileid)+".xml"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	r = requests.request("GET", url, None, None, headers)
	return r.content
	
def ls():
	print_file_list(print_folder_list(0))
	loop()
	
	
##this is for when I go back and take out the parsing the prints that slows it down
##will make it some config option
def list_items_shared():
	print_file_list(print_folder_list(0))
	loop()
	
def firstrun():
	return os.path.exists('~/.boxlinux')



########################################################################
#######################HELPER METHODS###################################
#these are generally small methods that work as they and I have no
#reason to change or update

def test():
	print_folder_list(0)
	get_info_folder(445859823)

def errprint(printthis):	
	print("[ERROR] "+printthis)
	
def varprint(printthis):
	print("[VARCHECK] "+str(printthis))
	return
	
def get_sha1sum_local(filepath):
	f = open(filepath, 'r')
	string = f.read()
	#must be string or buffer not file
	sha1sum = hashlib.sha1()
	sha1sum.update(string)
	return sha1sum.hexdigest()
	
def get_local_files():
	return os.listdir(os.getcwd())
	
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
	in the ubuntu repos it only installs the version for 2.7
	looking for fix for python3.2 now...
python2.7 (duh!)
"""
