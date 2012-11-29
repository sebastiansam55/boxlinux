boxlinux
========

Bringing Box to the Linux desktop

[License] (http://www.gnu.org/licenses/gpl.html)

## Current Capabities:

* Selection of folders and files based off of filenames 
	
* Command line mode (great for scripting)
	
* Upload (see below on how to UL to different DIRs)
	
* Download (from any folder (using the cd command))
	
	* Download all files in folder!
	
* Listing all files in root dir and other dirs (on Box)
	
* Create shareable links for files

	* Will also return bit.ly shortened links for files (if enabled)
	
	* Returns "direct" links but they will only work if the account is *PRO*
	
* Saves settings to ~/.boxlinux (Saved as JSON data)

* Delete Folders

* Removal of share links (files and folders)

* Rename Files and Folders

* Option to shorten the share URLs either by: ***

	* Unauthenticated googl
	
	* Legacy bitly authentication
	
* Display all comments on files. ***

* Comment on Files  ***

* Upload to other directories (Dependant on --dir being before -u)

* Added syncing!! (use 'boxlinux --sync'!)

***: Still in the code just no longer supported via command line interaction.
	
## Planned Features:

* Automatic "Syncing"
	
* More sharable link options (expire time, permissions etc.)
	
* Box Version control (Need box pro account, not feature of free)

* View Files shared with you
	
* Copy files on BOX (not sure why you would need to but it's in the API)

* Sharing of Files with other Box users...
	
* Possible support for non-autheicated shared folder download?
	
* Anything else I can think of...

## How to Use

First to run this you'll need `python` (Ubuntu package names are used here) installed, and you'll also need the requests python module installed (`python-requests`). 

You can install these by running `sudo apt-get install python python-requests` although python should already be installed on Ubuntu installations. 
The python matter shouldn't matter all that much; I developed and tested it with `python2.7` but I'm not entirely sure about python3 because installing python-requests did not install
 it for python 3, only for 2.

After downloading, make the file (boxlinux) executable by running `chmod +x boxlinux`, after changing to appropriate directory of course.

Next run `boxlinux --setup` and it will give you a link that you open in a browser, and login to you [Box.com](http://box.com) account.

After that it will ask you for the directory in which you want to save your files, right now it is limited to anywhere in your home directory; `/home/sam/BOX` or `/home/sam/downloads/dir`
would be acceptable but `/usr/bin` would not. 

The next command you should run is `boxlinux --sync` which will download all of the files in your box.com account and store them in the directory you just chose. Some of the other commands
of note are `-dl`, `-dla`, `-u`, `-ls`, `-lsh` and `--dir`.

`-dl` and `-dla` download files based off of where you tell them too with --dir, if the --dir argument is not supplied, or is supplied after the `-dl` or `-dla` arguments the command will execute in the Box.com root directory.

`-u` takes one argument, the name of the file that you want to upload; the file should be in the same directory that you are executing the command in. (Does work with --dir)

`-ls` and `-lsh` `-ls` will write out the Folder names to stdout, part of hopefully making this better to write scripts with. `-lsh` will write out the folder and file names in "human" readable format (neither are --dir compatiable, YET!) 





[Developers!] (http://i.imgur.com/Mnl5e.jpg)
----------

I really have no idea about what should go here... I use the geany IDE if that makes any difference. 

[Box Documentation] (http://developer.box.com/docs/ "Documenation")

This documentation is aboslutely atrocious (in my opinion) I mean it looks nice, but the only examples that they give are in cURL, and not everyone knows what *every single option* on cURL is for.

[README.md syntax] (http://daringfireball.net/projects/markdown/syntax)

[Requests documentation] (http://docs.python-requests.org/en/latest/api/)

[Bit.ly URL shortening Service] (http://dev.bitly.com/api.html)

[Bit.ly API Key] (http://bitly.com/a/your_api_key)

After gettings used to XML I'm going to change what I did in XML to use JSON.