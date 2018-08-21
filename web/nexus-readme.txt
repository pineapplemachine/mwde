Morrowind Dialog Explorer
=========================

Morrowind Dialog Explorer is a mod tool which allows you to search and explore
Morrowind's dialog topics and responses.

You can learn more about MWDE at https://pineapplemachine.com/files/mwde
MWDE is open source on GitHub at https://github.com/pineapplemachine/mwde

Setting up and using MWDE
=========================

To run MWDE, you'll need to have Python installed on your computer. MWDE is
compatible with recent Python 2.x and Python 3.x versions. That means it will
be hard for you to accidentally download a version of Python that doesn't work
with MWDE. (If your computer runs OSX, then it probably had Python already
installed when you got it.)

How to install Python on Windows:
https://docs.python.org/3/using/windows.html

How to install Python on OSX:
https://docs.python.org/3/using/mac.html

Once Python is installed on your computer, you will need to download
Morrowind Dialog Explorer and unzip the archive. You will need to set up MWDE
by going into the extracted folder and opening the file named "config.ini".
INI files are only a special kind of text file, so you can edit it with Notepad
or your choice of plain text editor.

Inside "config.ini" is a lot of text to help you understand how it works. The
most important part is to enter the paths to the Morrowind data files you want
to load inside the "load_file_paths" section. Normally, this would be the paths
to your Morrowind.esm, Tribunal.esm, and Bloodmoon.esm files.

Once you've set up your file paths, you're ready to run MWDE. Go back to the
folder. (The same one "config.ini" is in.) On Windows, double-click on
"Morrowind Dialog Explorer.bat". On OSX, open "Morrowind Dialog Explorer.app"
instead. A new console window will open and it will show something like this.

(Linux users should open a command line, navigate to the unzipped MWDE
directory, and run "python src/dialog_explorer.py".)

---

C:\MWDE>"C:\MWDE\Morrowind Dialog Explorer.bat"

C:\MWDE\Morrowind Dialog Explorer>python src/dialog_explorer.py --config-path="./config.ini"
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Morrowind.esm"...
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Tribunal.esm"...
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Bloodmoon.esm"...
Finished loading 3 data files.

Morrowind Dialog Explorer v1.0 is ready.
query >

---

Now you're ready to start exploring!

You can type "help" into the console for a list of commands. You can type
"help <command>" to get help about how to use a particular command.
