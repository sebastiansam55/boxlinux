#!/usr/bin/env python

import boxlinux

box = boxlinux.boxlinux()
box.init_settings()
box.load_settings()
box.ls()
box.ls_stdout()
##making new folders
#and folder in folder
box.mk_new_folder("testfolder", 0)
tmpFolderId = box.uni_get_name("testfolder", "id", "folder")
box.mk_new_folder("testfolder", tmpFolderId)

##uploading testfile "settings" file atm
box.upload("/home/sam/.boxlinux", "testfile", 0)
box.upload_raw("BETTER WAY TO TEST", "testfile", 0)
tmpFileId = box.uni_get_name("testfile", "id", "file")
##uploading in folder besides root
box.upload("/home/sam/.boxlinux", "testfile", tmpFolderId)
#get sha1sum local
print(box.get_sha1sum_local("/home/sam/.boxlinux"))
#get sha1sum remote
print(box.get_sha1sum_remote(tmpFileId))
#mk share item urls for file and folder
box.get_item_url(tmpFileId, "file")
box.get_item_url(tmpFolderId, "folder")

# list shared items
##need to reimplement
#box.list_items_shared()

#remove those urls
box.rm_share_url_item(tmpFolderId, "folder")
box.rm_share_url_item(tmpFileId, "file")

#rename test items
box.rename_item("newFile", tmpFileId, "file")
box.rename_item("newFolder", tmpFolderId, "folder")

#make comments on test items
box.mk_comment(tmpFileId, "test_comment")

#get comments on test items
box.get_comments(tmpFileId)

#clean up files
box.rm_file(tmpFileId)
box.rm_folder(tmpFolderId)
