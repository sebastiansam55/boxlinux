#!/usr/bin/env python
#quick tester

import boxlinux

box = boxlinux.boxlinux()
box.__init__()

#box.upload_raw("Sam's file mofo", "testfile", 0)
#tmpFileId = box.uni_get_name("testfile", "id", "file")
#print tmpFileId

#box.get_sha1sum_remote(tmpFileId)
box.list_items_shared()