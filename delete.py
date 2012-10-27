#!/usr/bin/env/ python

def deletefilechoice():
	main.print_file_list(-1, True)
	rawinput = raw_input("File to delete: ")
	fileid = get_file_id(rawinput)
	deletefile(fileid)
	main.loop()
	
	
def deletefile(fileid):
	try:
		sha1sum = main.get_sha1sum_remote(fileid)
		helper.varprint("Sha1sum of file to be deleted: "+sha1sum)
		url = "https://api.box.com/2.0/files/"+fileid
		headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token, 'If-Match': sha1sum}
		r = requests.request("DELETE", url, None, None, headers)
		print(r.content)
	except:
		helper.infoprint('Something bad happened when deleting file...')
	
def deletefolderchoice():
	#instead of -1 should be zero because of the all files thing in all directories
	print_folder_list(0, True)
	rawinput = raw_input("Folder to delete: ")
	folderid = main.get_folder_id(rawinput)
	deletefolder(folderid)
	main.loop()

def deletefolder(folderid):
	print("Deleting Folder with id "+folderid)
	url = "https://api.box.com/2.0/folders/"+str(folderid)+"?recurive=true"
	headers = {'Authorization' : 'BoxAuth api_key='+apikey+'&auth_token='+auth_token,}
	payload = {'recursive': 'true'}
	r = requests.request("DELETE", url, None, None, headers)
	print(r.content)