boxlinux
========

Bringing Box to the Linux desktop

[License] (http://www.gnu.org/licenses/gpl.html)

To use this tool (in it's current state) add it into your BIN, I recommend making a bin folder in your home dir and adding that to your $PATH. I'd also rename the *main.py* file to boxlinux, which is what it will eventually be.
Current Capabities:
	+Authentication (through BOX v1 API)
	+Interactive mode
	+Command line mode (great for scripting)
	+Upload (to root dir)
	+Download (from any folder)
		+Download all files in folder!
	+Listing all files in root dir and other dirs (on box)
	+Create shareable links for files
	+Saves settings to ~/.boxlinux (only setting atm is the auth token from BOX's API)
	
Planned Features:
	+ Automatic "Syncing"
	+ Sharable links for folders
		+ More sharable link options (expire time, permissions etc.)
	+ Box Version control (Need box pro account, not feature of free)
	+ Delete Folders
	+ Upload to other directories
	+ View Comments on File (maybe not sure if that would be useful yet)
	+ Update file info (rename files)
	+ Copy files on BOX (not sure why you would need to but it's in the API)
	+ Possible support for non-autheicated shared folder download?
	+ Anything else I can think of...





[Developers!] (http://i.imgur.com/Mnl5e.jpg)
======

I really have no idea about what should go here... I use the geany IDE if that makes any difference. 

[Box Documentation] (http://developer.box.com/docs/ "Documenation")

[README.md syntax] (http://daringfireball.net/projects/markdown/syntax)

[Requests documentation] (http://docs.python-requests.org/en/latest/api/)

I have choosen, because of my familarness with XML that all the responses from the BOX API should be requested in XML format, now that I've used JSON a bit, I might convert everything over sometime or other

(No longer used! Thank you requests!)

[PycURL documentation] (http://pycurl.sourceforge.net/doc/pycurl.html)

[libcURL documentation] (http://curl.haxx.se/libcurl/c/)
