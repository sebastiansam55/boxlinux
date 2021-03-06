#!/usr/bin/env python
import curses
import json
from main import load_settings, get_folder_json, upload
import os


def get_input(prompt, length):
	screen.addstr(size[0]-1,0, prompt)
	input = screen.getstr(size[0]-1, length+1)
	return input

def commands(input):
	if input=="q" or input=="Q":
		curses.endwin()
	elif input=="?":
		screen.clear()
		screen.border(0)
		screen.addstr(1,1, "This is a full listing of the commands available:")
		screen.addstr(2,1, "?\tDisplay this help message")
		screen.addstr(3,1, "download (d) \tDownload File")
		screen.addstr(4,1, "ls\t\tList files.")
		screen.addstr(5,1, "clear\t\tClear the Screen.")
		screen.addstr(6,1, "upload (u)\t Upload File")
	elif input=="ls" or input=="LS":
		screen.clear()
		screen.border(0)
		print_folder_list()
	elif input=="clear" or input=="CLEAR":
		screen.clear()
		screen.border(0)
	elif input=="u" or input=="upload":
		screen.clear()
		screen.border(0)
		filelist = os.listdir(os.getcwd())
		pos = 4
		screen.addstr(3, 1, "Some of these are Folders")		
		for filename in filelist:
			screen.addstr(pos,1, str(filename))
			pos+=1
		prompt = "File to upload: "
		input = get_input(prompt, len(prompt))
		upload(os.getcwd()+"/"+input, input, 0)

def print_folder_list():
	i=0
	pos = 3
	fil = True
	screen.addstr(2,0, "Folders: ")
	while i<len(folder_list['item_collection']['entries']):
		screen.addstr(pos,1, str(folder_list['item_collection']['entries'][i]['name']))
		i+=1
		pos+=1
		if fil and folder_list['item_collection']['entries'][i]['type']=="file":
			screen.addstr(pos, 0, "Files ")
			pos+=1
			screen.addstr(pos,1, str(folder_list['item_collection']['entries'][i]['name']))
			pos+=1
			i+=1
			fil = False

load_settings()
folder_list = get_folder_json(0)
version="v0.0.0.1"
run=True
screen = curses.initscr()
screen.clear()
screen.border(0)
size = screen.getmaxyx()

screen.addstr(0,0, "BoxLinux "+version)
screen.addstr(1,1, "Number of Lines: "+str(screen.getmaxyx()))
#print_folder_list()
prompt = "Choose a Command (? for help):"
while True:
	screen.addstr(0,0, "BoxLinux "+version)
	command = get_input(prompt, len(prompt))
	commands(command)
	screen.refresh()
