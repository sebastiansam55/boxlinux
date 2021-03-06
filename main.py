#!/usr/bin/env python
from xml.dom.minidom import parseString
import sys
import os
import json
import requests
from os.path import expanduser
import argparse
##user made
from helper import varprint, errprint, infoprint, foldercraft
import bitlyshortener as bitly
import googlshortener as googl
#BoxyLinux API-KEY
apikey = "l7c2il3sxmetf2ielkyxbvc2k4nqqkm4"
##doing it like this will enable crossplatform (windows) support
HOME = expanduser("~")

share = True

##need some way for this is be set from the file settings

##########################	Set to true for short URLS
bitly_enabled = False 	##	Set to false if you don't have an account
googl_enabled = False	##
##########################	or just don't want short urls

##Leave as blank until otherwise loaded or set
proxies = {"":"","":""}

global headers

#version number
ver = "0.1"
#change this whenever change folders
global rootdom
#global rootJSON

def main():
	#ArgumentParser setup
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-dl', metavar='filename', type=str, dest='dlFileName', help="Filename to download", action=dlAction)
	parser.add_argument('-dla', help="Download all files", action='store_true')
	parser.add_argument('-u', metavar='filename', type=str, dest='ulFileName', help="Filename to upload", action=ulAction)
	parser.add_argument('--setup', help="Setup for use", action='store_true')
	parser.add_argument('-lsh', help="List filenames for human view", action='store_true')
	parser.add_argument('-ls', help="Print filenames on Box to stdout", action='store_true')
	parser.add_argument('--interactive', help="Enter oldschool interactive mode", action='store_true')
	parser.add_argument('--http-proxy', metavar='PROXYIP', type=str, dest='http_proxy', help="HTTP proxy info", action=proxyAction)
	parser.add_argument('--https-proxy', metavar='PROXYIP', type=str, dest='https_proxy', help="HTTPS proxy info", action=proxyAction)
	parser.add_argument('--version', action='version', version='%(prog)s '+ver)
	args = parser.parse_args()
	print args.dla
	if args.interactive:
		interactive()
	elif args.lsh:
		init_settings()
		ls()
	elif args.ls:
		ls_stdout()
	elif args.setup:
		setup()
	elif args.dla:
		init_settings()
		download_all(get_all_file_id())
	
		
def interactive():
	global headers
	if not os.path.exists('~/.boxlinux'):
		print("Have you approved this app for use? [Y/n/Q]")
		yorn = raw_input()
		if yorn=='Y'or yorn=='y':			
			print("Loading Settings")
			load_settings()
			headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
		elif command_check(yorn):
			print("Quitting")
			return 0
		else:
			ticket = authenticate()
			print("Open this link in browser and confirm!")
			print("https://www.box.com/api/1.0/auth/"+ticket)
			raw_input("Press enter when approved")
			get_auth_token(ticket)		
	else:
		print("Loading Settings")
		load_settings()
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	global rootdom
	rootdom = parseString(get_folder_list(0))
	#global rootJSON
	#rootJSON = json.loads(get_folder_json(0))
	loop()
	return 0


class dlAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		init_settings()
		download_fileid(uni_get_name(values, "id", "file"))
		
class ulAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		init_settings()
		upload(os.getcwd()+values, values, 0)
		
class proxyAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		#have to load settings so the auth_token is available
		init_settings()
		proxies = {"http": values.http_proxy, "https": values.https_proxy}
		save_settings()

def setup():
	ticket = authenticate()
	print("Open this link in browser and confirm!")
	print("https://www.box.com/api/1.0/auth/"+ticket)
	raw_input("Press enter when approved")
	get_auth_token(ticket)	

def ls_stdout():
	init_settings()
	#get one list for folders and one for files
	folders = get_item_name_list("folder")
	files = get_item_name_list("file")
	#Not sure that this is the best way to do this; have to think about BASH usability
	for i in folders:
		sys.stdout.write(folders[i])
	for i in files:
		sys.stdout.write(folders[i])

def init_settings():
	load_settings()
	global headers
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	global rootdom
	rootdom = parseString(get_folder_list(0))
	
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
	print("\t13. Setup proxy")
	print("\t14. Get comments on file")
	print("\t15. Comment on file")
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
	elif command==13:
		setup_proxies()
	elif command==14:
		comments()
	elif command==15:
		mk_comment_choice()
	elif command==-1:
		test()
	else:
		loop()
	loop()

def authenticate():
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_ticket&api_key="+apikey, proxies=proxies)
	xml = r.content
	dom = parseString(xml)
	ticket = dom.getElementsByTagName('ticket')[0].toxml()
	ticket = ticket.replace('<ticket>', '').replace("</ticket>","")
	return ticket
	
def load_settings():
	f = open(os.getenv("HOME")+'/.boxlinux', 'r')
	global auth_token
	auth_token = json.loads(str(f.read()))
	auth_token = auth_token['auth_token']
	f.close()
	
def save_settings():
	## this becomes problem because it will overwrite the file getting rid of any bitly settings
	f = open(os.getenv("HOME")+'/.boxlinux', 'w')
	data = {"auth_token":auth_token, "proxies":proxies}
	f.write(json.dumps(data))
	f.close()
	
def get_auth_token(ticket):
	r = requests.get("https://www.box.com/api/1.0/rest?action=get_auth_token&api_key="+apikey+"&ticket="+ticket, proxies=proxies)
	xml = r.content
	dom = parseString(xml)
	global auth_token
	auth_token = dom.getElementsByTagName('auth_token')[0].toxml()
	auth_token = auth_token.replace('<auth_token>', '').replace("</auth_token>", "")
	save_settings()

def get_folder_list(folderid):
	url = build_url("folder", str(folderid)+".xml", None)
	r = requests.get(url=url, headers=headers, proxies=proxies)
	return r.content
	
def get_folder_json(folderid):
	url = build_url("folder", folderid, None)
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	r = requests.get(url=url, headers=headers, proxies=proxies)
	return json.loads(r.content)

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
			i+=1
			itemcnt+=1
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

def download(filenumber):
	fileid = str(get_file_id(filenumber))
	url = build_url("file", fileid, "content")
	r = requests.get(url=url, headers=headers, proxies=proxies)
	infoprint("Downloading...")
	filerecieved = r.content
	filename = uni_get_id(fileid, "name", "file")
	f = open(filename, 'w+')
	infoprint("Writing...")
	f.write(filerecieved)
	f.close()
	
def download_fileid(fileid):
	fileid=str(fileid)
	url = build_url("file", fileid, "content")
	print url
	r = requests.get(url=url, headers=headers, proxies=proxies)
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
		errprint("file might not exsist")
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

def command_check(command):
	command = str(command)
	if command=='Q' or command=='q':
		return True

def upload(filepath, filename, folderid):
	infoprint("Uploading...")
	url = build_url("file", "content", None)
	payload = {'filename1': filename, 'folder_id': folderid}
	try:
		data = {filename: open(filepath, 'r')}
	except:
		errprint("File selected is not a file or other error")
		return
	r = requests.post(url=url, data=payload, headers=headers, files=data, proxies=proxies)
	
	
def uploadchoices():
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

def deletefilechoice():
	print_file_list(-1, True)
	dlfile = raw_input("File to delete: ")
	if(in_list(dlfile, get_item_name_list("file"))):
		deletefile(uni_get_name(dlfile, "id", "file"))
	else:	
		fileid = get_file_id(dlfile)
		deletefile(fileid)
	update_dom(0)
	
	
def deletefile(fileid):
	try:
		sha1sum = get_sha1sum_remote(fileid)
		varprint("Sha1sum of file to be deleted: "+sha1sum)
		url = build_url("file", fileid, None)
		headers_ = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token, 'If-Match': sha1sum}
		r = requests.delete(url=url, headers=headers_, proxies=proxies)
		print(r.content)
	except:
		infoprint('Something bad happened when deleting file...')
	
def deletefolderchoice():
	print_folder_list(-1, True)
	dlfolder = raw_input("Folder to delete: ")
	if(in_list(dlfolder, get_item_name_list("folder"))):
		deletefolder(uni_get_name(dlfolder, "id", "folder"))
	else:
		folderid = get_folder_id(dlfolder)
		deletefolder(folderid)

def deletefolder(folderid):
	print("Deleting Folder with id "+folderid)
	url = build_url("folder", str(folderid)+"?recursive=true", None)
	#varprint(url)
	r = requests.delete(url=url, headers=headers, proxies=proxies)
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
			errprint("file might not exist")
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
	url = build_url(itemtype, None, None)
	payload = {'name': ''+foldername+'', 'parent': {'id': parent_folderid}}
	r = requests.post(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
	return r.content
	
def new_folder_choices():
	print("Current Folders:")
	print_folder_list(0, False)
	newfoldername = raw_input("Name for new folder:")
	parentfolder = raw_input("Parent Folder (0) for root")
	mk_new_folder(newfoldername, get_folder_id(parentfolder))
	update_dom(0)
	
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
	else:
		print("Read the readme for info on how to set this function up")
		
def get_item_url(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = build_url(itemtype, itemid, None)
		payload = {'shared_link': {'access': 'Open'}}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
		rtrnval = json.loads(r.content)
		return [rtrnval['shared_link']['url'], rtrnval['shared_link']['download_url']]
	elif itemtype=="file" or itemtype=="FILE":
		url = build_url(itemtype, itemid, None)
		payload = {'shared_link': {'access':'Open'}}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
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
	else:
		print("Read the readme for info on how to set this function up")
	

def rm_share_url_item(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = build_url(itemtype, itemid, None)
		payload = {'shared_link': None}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
		return r.content
	elif itemtype=="file" or itemtype=="FILE":
		url = build_url(itemtype, itemid, None)
		payload = {'shared_link': None}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
		return r.content
		
	
def rm_share_url_folder_choices():
	print_folder_list(-1, True)
	unsharethis = raw_input("Which folder to unshare?")
	if(in_list(unsharethis, get_item_name_list("folder"))):
		rm_share_url_item(uni_get_name(unsharethis, "id", "folder"), "FOLDER")
	else:
		rm_share_url_item(get_folder_id(unsharethis), "folder")
	
def rm_share_url_file_choices():
	print_file_list(0, True)
	unsharethis = raw_input("Which file to unshare?")
	if(in_list(unsharethis, get_item_name_list("file"))):
		rm_share_url_item(uni_get_name(unsharethis, "id", "file"), "FILE")
	else:
		rm_share_url_item(get_file_id(unsharethis), "FILE")
	##no need to update dom	
	
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
	
def rename_item(newname, itemid, itemtype):
	if(itemtype=="file" or itemtype=="FILE"):
		url = build_url(itemtype, itemid, None)
		payload = {'name': newname}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
		return r.content
	elif(itemtype=="folder" or itemtype=="FOLDER"):
		url = build_url(itemtype, itemid, None)
		payload = {'name': newname}
		r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
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
			varprint(fileid)
			download_fileid(fileid)
			k+=1
			
def setup_proxies():
	httpproxy = raw_input("What is the HTTP proxy?: ")
	httpsproxy = raw_input("What is the HTTPS proxy?: ")
	global proxies
	proxies = {"http": httpproxy, "https": httpsproxy,}
	save_settings()
	
def get_comments(fileid):
	## it appears that these come sorted in chronological order...
	url = build_url("file", fileid, "comments")
	r = requests.get(url=url, headers=headers)
	return json.loads(r.content)
	
def print_comments(comments):
	i=0
	for k in comments['entries']:
		print(comments['entries'][i]['created_by']['name']+" said: "+comments['entries'][i]['message'])
		i+=1

##do not include the s that should be in the URL this will add it
##as of now this doesn't do XML... will probably end up changing all the ones that still use XML
def build_url(itemtype, itemid, getthis):
	url = "https://api.box.com/2.0/"+str(itemtype)+"s/"
	if not itemid==None:
		url+=str(itemid)
		if not getthis==None:
			url+="/"+str(getthis)
	#varprint(url)
	return url

def comments():
	print_file_list(-1, False)
	get_comments_on = raw_input("Which file to get comments on?")
	if in_list(get_comments_on, get_item_name_list("file")):
		print_comments(get_comments(uni_get_name(get_comments_on, "id", "file")))
	else:
		print_comments(get_comments(get_file_id(get_comments_on)))
		
		
def mk_comment(fileid, comment):
	url = build_url("file", fileid, "comments")
	payload = {"message": comment}
	r = requests.post(url=url, data=json.dumps(payload), headers=headers, proxies=proxies)
	
def mk_comment_choice():
	print_file_list(-1, False)
	comment_on = raw_input("Which file to comment on?")
	comment = raw_input("Comment: ")
	if in_list(comment_on, get_item_name_list("file")):
		mk_comment(uni_get_name(comment_on, "id", "file"), comment)
	else:
		mk_comment(get_file_id(comment_on), comment)

def download_all(file_list):
	for i in file_list:
		download_fileid(file_list[i])

def get_info_item(itemid, itemtype):
	if itemtype=="folder" or itemtype=="FOLDER":
		url = "https://api.box.com/2.0/folders/"+str(itemid)+".xml"
		r = requests.get(url=url, headers=headers, proxies=proxies)
		return r.content
	elif itemtype=="file" or itemtype=="FILE":
		url = "https://api.box.com/2.0/files/"+str(itemid)+".xml"
		r = requests.get(url=url, headers=headers)
		return r.content
		
def ls():
	print_file_list(print_folder_list(-1, False), False)

def list_items_shared():
	print_file_list(print_folder_list(-1, True), False)

def test():
	print("DEBUG METHOD")


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