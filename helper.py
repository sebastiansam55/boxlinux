#!/usr/bin/env python
##helper methods !
#on second thought I question the helpfulness of splitting all the files up like this


def errprint(printthis):	
	print("[ERROR] "+printthis)
	
def varprint(printthis):
	print("[VARCHECK] "+str(printthis))
	
def infoprint(printthis):
	print("[INFO] "+str(printthis))
	
	
def ls():
	main.print_file_list(print_folder_list(-1, False), False)
	main.loop()

def list_items_shared():
	main.print_file_list(print_folder_list(0, True), False)
	main.loop()
	
def foldercraft(path):
	if not os.path.exists(path):
		os.makedirs(path)
	else:
		print("Folder already exists")