#!/usr/bin/env python
from xml.dom.minidom import parseString
import sys
import os
import json
import requests
from os.path import expanduser
import requests.auth
##user made
import helper
import delete
import bitlyshortener as bitly
import googlshortener as googl
#BoxyLinux API-KEY
apikey = "l7c2il3sxmetf2ielkyxbvc2k4nqqkm4"
##doing it like this will enable crossplatform (windows) support
HOME = expanduser("~")

share = False
shareurl = '&auth_token=YOURAUTH_TOKENHERE'

##need some way for this is be set from the file settings

##########################	Set to true for short URLS
bitly_enabled = False 	##	Set to false if you don't have an account
##########################	or just don't want short urls


#change this whenever change folders
global rootdom

def main():
	if int(len(sys.argv))==1:
		if not os.path.exists('~/.boxlinux'):
			print("Have you approved this app for use? [Y/n/Q]")
			yorn = raw_input()
			if yorn=='Y'or yorn=='y':			
				print("Loading Settings")
				load_settings()
			elif yorn=='q' or yorn=='Q':
				print("Quitting")
				return 0
			else:
				ticket = authenticate()
				print("Open this link in browser and confirm!")
				print("https://www.box.com/api/1.0/auth/"+ticket)
				raw_input("Press enter when approved")
				get_auth_token(ticket)
			
		else:
			print("Loading settings")
			load_settings()
		global rootdom
		rootdom = parseString(get_folder_list(0))	
		loop()
		return 0
	else:
		shellhelper()
		
		
def loop():
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
	command = raw_input("What would you like to do?")
	if command_check(command):
		return
	command = int(command)
	if command==0:
		download_choices()
	elif command==1:
		cdchoices()
	elif command==2:
		uploadchoices()
	elif command==3:
		deletefilechoice()
	elif command==4:
		deletefolderchoice()
	elif command==5:
		fileurlchoices()		
	elif command==6:
		folder_url_choices()
	elif command==7:
		rm_share_url_file_choices()
	elif command==8:
		rm_share_url_folder_choices()		
	elif command==9:
		new_folder_choices()
	elif command==10:
		rename_file_choices()
	elif command==11:
		rename_folder_choices()
	elif command==12:
		ls()
	elif command==-1:
		test()
	else:
		loop()

def authenticate():
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_ticket&api_key="+apikey)
	xml = r.content
	dom = parseString(xml)
	ticket = dom.getElementsByTagName('ticket')[0].toxml()
	ticket = ticket.replace('<ticket>', '').replace("</ticket>","")
	return ticket
	
def load_settings():
	f = open(os.getenv("HOME")+'/.boxlinux', 'r')
	global auth_token
	auth_token = str(f.readline())
	if(bitly_enabled):
		f.readline()
		f.readline()
		
	f.close()
	
def save_auth_token():
	f = open(os.getenv("HOME")+'/.boxlinux', 'w')
	f.write(auth_token)
	f.close()
	
	
def get_auth_token(ticket):
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_auth_token&api_key="+apikey+"&ticket="+ticket)
	xml = r.content
	dom = parseString(xml)	
	global auth_token
	auth_token = dom.getElementsByTagName('auth_token')[0].toxml()
	auth_token = auth_token.replace('<auth_token>', '').replace("</auth_token>", "")
	save_auth_token()


def get_folder_list(folderid):
	url = "https://api.box.com/2.0/folders/"+str(folderid)+".xml"
	r = requests.get(url, headers={'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,})
	return r.content
		
		
def print_folder_list(itemcnt, showshare):
	itemcnt = int(itemcnt)
	dom = rootdom
	i=0
	bol = True
	sharebool = False
	print("FOLDERS:")
	while bol:
		try:
			nameoffolder = dom.getElementsByTagName('folder')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
			folderid = dom.getElementsByTagName('folder')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			if showshare==True:
				dom_of_folder = parseString(get_info_item(folderid, "folder"))
				try:
					dom_of_folder.getElementsByTagName('shared-link')[0]
					sharebool = True
				except:
					sharebool = False
			i=i+1
			itemcnt = itemcnt+1
			if showshare==True:
				print(str(itemcnt)+" "+nameoffolder +" Shared: "+str(sharebool)+" ("+folderid+")")
			else:
				print(str(itemcnt)+" "+nameoffolder+" ("+folderid+")")

		except:
			bol = False	
			print("End of Folders! On the "+str(itemcnt))
	return itemcnt

def print_file_list(itemcnt, showshare):
	itemcnt = int(itemcnt)
	dom = rootdom	
	print("############################")
	print("FILES: ")
	sharebool = False
	bol = True
	i=0
	while bol:
		try:
			nameofitem = dom.getElementsByTagName('file')[i].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')		
			fileid = dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			if showshare==True:
				dom_of_file = parseString(get_info_item(fileid, "FILE"))
				try:
					dom_of_file.getElementsByTagName('shared-link')[0]
					sharebool = True
				except:
					sharebool = False
			i=i+1
			itemcnt = itemcnt+1
			if showshare==True:
				print(str(itemcnt)+" "+nameofitem+" Shared: "+str(sharebool)+" ("+fileid+")")
			else:
				print(str(itemcnt)+" "+nameofitem+" ("+fileid+")")
		except:
			print("End of Items! On the "+str(itemcnt))
			bol=False
	
def download_choices():
	print_file_list(-1, False)
	print("Select 'all' to download all of the files listed")
	dlchoice = raw_input("Select a file to download: ")
	if command_check(dlchoice):
		return
	elif str(dlchoice)=="all" or str(dlchoice)=="ALL":
		fileids = get_all_file_id()
		download_all(fileids)
	elif in_list(str(dlchoice), get_item_name_list("file")):
		download_fileid(file_id_from_name(dlchoice))
	else:
		download(int(dlchoice))
	loop()

def download(filenumber):
	fileid = str(get_file_id(filenumber))
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	url = "https://api.box.com/2.0/files/"+fileid+"/content"
	r = requests.request("GET", url, None, headers)
	helper.infoprint("Downloading...")
	filerecieved = r.content
	#this will be replaced with a file write method idealy
	filename = uni_get_id(fileid, "name", "file")
	f = open(filename, 'w+')
	helper.infoprint("Writing...")
	f.write(filerecieved)
	f.close()
	
def download_fileid(fileid):
	fileid=str(fileid)
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	url = "https://api.box.com/2.0/files/"+fileid+"/content"
	r = requests.request("GET", url, None, headers)
	filedata = r.content
	filename = uni_get_id(fileid, "name", "file")
	f = open(filename, 'w')
	f.write(filedata)
	f.close()
	
def get_file_id(filelistno):
	dom = rootdom
	try:
		fileid = dom.getElementsByTagName('file')[int(filelistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	except:
		helper.errprint("file might not exsist")
	return fileid
	
def file_id_from_name(filename):
	dom = rootdom
	for files in dom.getElementsByTagName('file'):
		testervar = files.getElementsByTagName('name')[0].toxml().replace('<name>','').replace('</name>','')
		if testervar==filename:
			return files.getElementsByTagName('id')[0].toxml().replace('<id>','').replace('</id>','')
	
def get_folder_id(folderlistno):
	dom = rootdom
	folderid = dom.getElementsByTagName('folder')[int(folderlistno)].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
	return folderid
			
def cdchoices():
	global rootdom
	print_folder_list(-1, False)
	cdto = raw_input("Which folder to cd to?")
	if command_check(cdto):
		return
	elif in_list(cdto, get_item_name_list("folder")):
		rootdom = parseString(get_folder_list(uni_get_name(str(cdto), "id", "folder")))
	else:
		rootdom = parseString(get_folder_list(get_folder_id(int(cdto))))
	itemcnt = print_folder_list(0, False)
	print_file_list(int(itemcnt), False)
	loop()
		
def command_check(command):
	command = str(command)
	if command=='Q' or command=='q':
		return True
		
#TODO: Convert this to prebuilt module like optparse
def shellhelper():
	#as of right now the best I can do is offer only access to the root
	#should write something that will get the folders and files into an xml file...
	#it could then do some matching to match file names with fileids'
	#some globals will also have to be set/reset... rootxml auth_token etc.
	load_settings() #this will load auth_token
	global rootdom
	rootdom = parseString(get_folder_list(0))
	command = str(sys.argv[1])
	#listed in order of usage (suspected usage at least)
	if command=='-h' or command=='--help':
		print("usage boxlinux [option] At this stage only one command at a time will work....")
		print("-h\t\t :will display this help message")
		print("-V\t\t :will display the Version Number")
		print("-u <filename>\t :will upload the specified file to the root dir (unless other wise specified)")
		print("-d <filename>\t :Download the filename... according to the number listed in ls (see below)")
		print("ls\t\t :will display the files and folders in the root dir (unless other wise specified)")
		print("-da Will download all the files in the root directory (not yet recursive)")
		print("-mkfolders Makes folders based on Box folders")
		##GET TO WORK ON THIS LATER
		print("-rm <filename>\t :will delete file on Box.com with same name and sha1sum")
	elif command=='-V' or command=='-version':
		print('Version 0.0.0.1')
	elif command=='ls':
		ls()
	elif command=='-u' or command=='--upload':
		upload(os.getcwd()+"/"+sys.argv[2], sys.argv[2], 0)
	elif command=='-d':
		download(sys.argv[2])
	elif command=='-da':
		download_all(get_all_file_id())
	elif command=='-mkfolders':
		try:
			dom = rootdom
			icnt=1
			for i in dom.getElementsByTagName('folder'):
				foldername = dom.getElementsByTagName('folder')[icnt].getElementsByTagName('name')[0].toxml().replace('<name>', '').replace('</name>', '')
				helper.foldercraft("./"+foldername)
				icnt = icnt+1
		except:
			helper.errprint("You might be okay...")
	else:
		return
		
		
def upload(filepath, filename, folderid):
	helper.infoprint("Uploading...")
	url = "https://api.box.com/2.0/files/content"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'filename1': filename, 'folder_id': folderid}
	try:
		data = {filename: open(filepath, 'r')}
	except:
		helper.errprint("File selected is not a file or other error")
		return
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
	ulchoice = raw_input("What file do you want to upload?")
	print_folder_list(-1, True)
	uldir = raw_input("What folder to upload to?")
	if(in_list(ulchoice, get_local_files()) and in_list(uldir, get_item_name_list("folder"))):
		upload(os.getcwd()+"/"+str(ulchoice), str(ulchoice), int(uni_get_name(uldir, "id", "folder")))
	elif(in_list(uldir, get_item_name_list("folder"))):
		upload(os.getcwd()+"/"+files[int(ulchoice)+1], files[int(ulchoice)], int(uni_get_name(uldir, "id", "folder")))
	elif(in_list(ulchoice, get_local_files())):
		upload(os.getcwd()+"/"+str(ulchoice) , str(ulchoice), get_folder_id(uldir))
	else:
		upload(os.getcwd()+"/"+files[int(ulchoice)+1], files[int(ulchoice)], 0)
	update_dom(0)
	loop()

def deletefilechoice():
	print_file_list(-1, True)
	dlfile = raw_input("File to delete: ")
	if(in_list(dlfile, get_item_name_list("file"))):
		deletefile(uni_get_name(dlfile, "id", "file"))
	else:	
		fileid = get_file_id(dlfile)
		deletefile(fileid)
	update_dom(0)
	loop()
	
	
def deletefile(fileid):
	try:
		sha1sum = get_sha1sum_remote(fileid)
		helper.varprint("Sha1sum of file to be deleted: "+sha1sum)
		url = "https://api.box.com/2.0/files/"+fileid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token, 'If-Match': sha1sum}
		r = requests.request("DELETE", url, None, None, headers)
		print(r.content)
	except:
		helper.infoprint('Something bad happened when deleting file...')
	
def deletefolderchoice():
	print_folder_list(-1, True)
	dlfolder = raw_input("Folder to delete: ")
	if(in_list(dlfolder, get_item_name_list("folder"))):
		deletefolder(uni_get_name(dlfolder, "id", "folder"))
	else:
		folderid = get_folder_id(dlfolder)
		deletefolder(folderid)
	loop()
	
	#it wants the recursive as a addition onto the url... easy enough
def deletefolder(folderid):
	print("Deleting Folder with id "+folderid)
	url = "https://api.box.com/2.0/folders/"+str(folderid)+"?recurive=true"
	#varprint(url)
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	r = requests.request("DELETE", url, None, None, headers)
	print(r.content)

def get_all_file_id():
	dom = rootdom
	cnt = int(dom.getElementsByTagName('total-count')[0].toxml().replace('<total-count>', '').replace('</total-count>', ''))
	fileid={}
	i=0
	while i<=cnt:
		try:
			fileid[i] = dom.getElementsByTagName('file')[i].getElementsByTagName('id')[0].toxml().replace('<id>', '').replace('</id>', '')
			i=i+1
		except:
			helper.errprint("file might not exsist")
			i=cnt+5
	return fileid

def get_sha1sum_remote(fileid):
	#slight modification of get_file_name or what ever it was 
	dom = rootdom
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
	r = requests.request("POST", url, None, json.dumps(payload), headers)
	return r.content
	
def new_folder_choices():
	print("Current Folders:")
	print_folder_list(0, False)
	newfoldername = raw_input("Name for new folder:")
	parentfolder = raw_input("Parent Folder (0) for root")
	mk_new_folder(newfoldername, get_folder_id(parentfolder))
	update_dom(0)
	loop()
	
def folder_url_choices():
	if(share):
		print_folder_list(-1, True)
		folderid = raw_input("Folder to make new link for: ")
		if(in_list(folderid, get_item_name_list("folder"))):
			urls = get_item_url(uni_get_name(folderid, "id", "folder"))
		else:
			urls = get_item_url(get_folder_id(folderid), "folder")
		print("Download URL: "+urls[0])
		if(googl_enabled):
			print("\t"+googl.shorten_url(urls[0]))
		elif(bitly_enabled):
			print("\t"+bitly.shorten_url(urls[0]))
		print("Direct(?) Download URL: "+urls[1]+ " (Pro account might be required)" )
		if(googl_enabled):
			print("\t"+googl.shorten_url(urls[1]))
		elif(bitly_enabled):
			print("\t"+bitly.shorten_url(urls[1]))
		loop()
	else:
		print("Read the readme for info on how to set this function up")
		
def get_item_url(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = "https://api.box.com/2.0/folders/"+itemid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+shareurl,}
		payload = {'shared_link': {'access': 'Open'}}
		r = requests.request("PUT", url, None, json.dumps(payload), headers)
		print r.content
		rtrnval = json.loads(r.content)
		return [rtrnval['shared_link']['url'], rtrnval['shared_link']['download_url']]
	elif itemtype=="file" or itemtype=="FILE":
		url = "https://api.box.com/2.0/files/"+itemid
		headers = {'content-type': 'application/json', 'Authorization': 'BoxAuth api_key='+apikey+shareurl}
		payload = {'shared_link': {'access':'Open'}}
		r = requests.put(url, data=json.dumps(payload), headers=headers)
		print r.content
		rtrnval = json.loads(r.content)
		return [rtrnval['shared_link']['url'],rtrnval['shared_link']['download_url']]




def fileurlchoices():
	if(share):
		print_file_list(-1, True)
		fileurl = raw_input("Which file to get URL for? (give the number)")
		if(in_list(fileurl, get_item_name_list("file"))):
			urls = get_item_url(uni_get_name(fileurl, "id", "file"), "file")
		else:
			urls = get_item_url(get_file_id(fileurl), "file")
		print("Download link: "+urls[0])
		if(googl_enabled):
			print("\t"+googl.shorten_url(urls[0]))
		elif(bitly_enabled):
			print("\t"+bitly.shorten_url(urls[0]))
		print("Direct Download link: "+urls[1])
		if(googl_enabled):
			print("\t"+googl.shorten_url(urls[1]))
		elif(bitly_enabled):
			print("\t"+bitly.shorten_url(urls[1]))
		loop()
	else:
		print("Read the readme for info on how to set this function up")
	

def rm_share_url_item(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = "https://api.box.com/2.0/folders/"+itemid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		payload = {'shared_link': None}
		r = requests.request("PUT", url, None, json.dumps(payload), headers)
		return r.content
	elif itemtype=="file" or itemtype=="FILE":
		#url = "https://api.box.com/2.0/files/"+itemid
		url = "http://httpbin.org/put"
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		payload = {'shared_link': None}
		r = requests.request("PUT", url, None, json.dumps(payload), headers)
		print r.content
		return r.content
		
	
def rm_share_url_folder_choices():
	print_folder_list(-1, True)
	unsharethis = raw_input("Which folder to unshare?")
	if(in_list(unsharethis, get_item_name_list("folder"))):
		rm_share_url_item(uni_get_name(unsharethis, "id", "folder"), "FOLDER")
	else:
		rm_share_url_item(get_folder_id(unsharethis), "folder")
	loop()
	
def rm_share_url_file_choices():
	print_file_list(0, True)
	unsharethis = raw_input("Which file to unshare?")
	if(in_list(unsharethis, get_item_name_list("file"))):
		rm_share_url_item(uni_get_name(unsharethis, "id", "file"), "FILE")
	else:
		rm_share_url_item(get_file_id(unsharethis), "FILE")
	##no need to update dom
	loop()	
	
def rename_file_choices():
	print_file_list(-1, True)
	filenumber = raw_input("What file to rename? (integer designation): ")
	fileid = get_file_id(filenumber)
	print("Renaming: "+uni_get_id(fileid, "name", "file")+" Press Q to stop")
	filename = raw_input("New name for file: ")
	if filename=='q' or filename=='Q':
		return
	rename_item(filename, fileid, "file")
	update_dom(0)	
	loop()
	
def rename_item(newname, itemid, itemtype):
	if(itemtype=="file" or itemtype=="FILE"):
		url = "https://api.box.com/2.0/files/"+itemid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		payload = {'name': newname}
		r = requests.request("PUT", url, None, json.dumps(payload), headers)
		return r.content
	elif(itemtype=="folder" or itemtype=="FOLDER"):
		url = "https://api.box.com/2.0/folders/"+itemid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		payload = {'name': newname}
		r = requests.request("PUT", url, None, json.dumps(payload), headers)
		return r.content
	
def rename_folder_choices():
	print_folder_list(-1, True)
	foldernumber = raw_input("What folder to rename? (integer designation): ")
	folderid = get_folder_id(foldernumber)
	print("Renaming: "+uni_get_id(folderid, "name", "folder")+" Press Q to stop")
	foldername = raw_input("New name for folder: ")
	if foldername=='q' or foldername=='Q':
		return
	rename_item(foldername, folderid, "folder")	
	update_dom(0)
	loop()

def get_item_name_list(itemtype):
	dom = rootdom
	i=0
	itemnames={}
	for itemname in dom.getElementsByTagName(itemtype):
		itemnames[i] = dom.getElementsByTagName(itemtype)[i].getElementsByTagName('name')[0].toxml().replace('<name>','').replace('</name>','')
		i+=1
	return itemnames

def filename_choices(filenamelist):
	i=0
	for filename in filenamelist:
		print(filenamelist[i])
		i+=1
		
def in_list(choice, filenamelist):
	i=0
	for filename in filenamelist:
		if(filenamelist[i]==choice):
			return True
		else:
			i+=1
	return False

			
			
def uni_get_id(itemid, getthis, itemtype):
	dom = rootdom
	i=0
	while i<=len(dom.getElementsByTagName(itemtype)):
		try:
			if dom.getElementsByTagName(itemtype)[i].getElementsByTagName('id')[0].toxml().replace('<id>','').replace('</id>','')==itemid:
				iteminfo = dom.getElementsByTagName(itemtype)[i].getElementsByTagName(getthis)[0].toxml().replace('<'+getthis+'>', '').replace('</'+getthis+'>', '')
				return iteminfo
			else:
				i=i+1
		except:
			return
	return iteminfo	
	
def uni_get_name(itemname, getthis, itemtype):
	dom = rootdom
	i=0
	while i<=len(dom.getElementsByTagName(itemtype)):
		try:
			if dom.getElementsByTagName(itemtype)[i].getElementsByTagName('name')[0].toxml().replace('<name>','').replace('</name>','')==itemname:
				iteminfo = dom.getElementsByTagName(itemtype)[i].getElementsByTagName(getthis)[0].toxml().replace('<'+getthis+'>','').replace('</'+getthis+'>','')
				return iteminfo
			else:
				i=i+1
		except:
			return
	return iteminfo
	
def update_dom(folderid):
	global rootdom
	rootdom = parseString(get_folder_list(folderid))
	
def sync():
	global rootdom
	folderlist = get_item_name_list("folder")
	for i in folderlist:
		rootdom = parseString(get_folder_list(uni_get_name(folderlist[i], "id", "folder")))
		k=0
		for j in rootdom.getElementsByTagName("file"):
			fileid = rootdom.getElementsByTagName("file")[k].getElementsByTagName("id")[0].toxml().replace('<id>','').replace('</id>','')
			helper.varprint(fileid)
			download_fileid(fileid)
			k+=1

########################################################################
############################WORKING METHODS#############################	
def download_all(file_list):
	for i in file_list:
		download_fileid(file_list[i])

def get_info_item(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = "https://api.box.com/2.0/folders/"+str(itemid)+".xml"
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		r = requests.request("GET", url, None, None, headers)
		return r.content
	elif itemtype=="file" or itemtype=="FILE":
		url = "https://api.box.com/2.0/files/"+str(itemid)+".xml"
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		r = requests.request("GET", url, None, None, headers)
		return r.content
		
def ls():
	print_file_list(print_folder_list(-1, False), False)
	loop()

def list_items_shared():
	print_file_list(print_folder_list(0, True), False)
	loop()

########################################################################
#######################HELPER METHODS###################################
def test():
    #get_folder_list(0);
	print_folder_list(-1, False)


def get_local_files():
	return os.listdir(os.getcwd())	
########################################################################
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
