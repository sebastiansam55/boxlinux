boxlinux
========

Bringing Box to the Linux desktop

[License] (http://www.gnu.org/licenses/gpl.html)

To use this tool (in it's current state) add it into your BIN, I recommend making a bin folder in your home dir and adding that to your $PATH. I'd also rename the *main.py* file to boxlinux, which is what it will eventually be.
Right now this is only officially supported for python 2.7 (developed and tested) but it should be mostly compatible with python 3 and newer versions.
The only problem that I have run into with trying to run it is that python3.2 (on ubuntu 12.04) does not install python-requests to the python3.2 libs or whatever.

## Current Capabities:

* Selection of folders and files based off of filenames 

	* Most, I have yet to finish all of them.

* Authentication (through BOX v1 API)

* Interactive mode
	
* Command line mode (great for scripting) --*Not Completed*
	
* Upload (to root dir)
	
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

* Option to shorten the share URLs either by:

	* Unauthenticated googl
	
	* Legacy bitly authentication
	
* Display all comments on files.

* Comment on Files
	
## Planned Features:

* Automatic "Syncing"
	
* More sharable link options (expire time, permissions etc.)
	
* Box Version control (Need box pro account, not feature of free)
	
* Upload to other directories (Needs to be tested)

* View Files shared with you
	
* Copy files on BOX (not sure why you would need to but it's in the API)

* Sharing of Files with other Box users...
	
* Possible support for non-autheicated shared folder download?
	
* Anything else I can think of...





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