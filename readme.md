# Morrowind Dialog Explorer

Morrowind Dialog Explorer is a mod tool for the game
[The Elder Scrolls III: Morrowind](https://en.wikipedia.org/wiki/The_Elder_Scrolls_III:_Morrowind).
It allows you to search and explore Morrowind's dialog topics
and responses.

You can learn more about MWDE at
**[https://pineapplemachine.com/files/mwde](https://pineapplemachine.com/files/mwde)**.

## Setting up and using MWDE
To run MWDE, you'll need to have <a href="https://www.python.org/">Python</a>
installed on your computer.
MWDE is compatible with recent Python 2.x and Python 3.x
versions. That means it will be hard for you to
accidentally download a version of Python that doesn't
work with MWDE.
(If your computer runs OSX, then it probably
had Python already installed when you got it.)

- <a href="https://docs.python.org/3/using/windows.html">How to install Python on Windows</a></li>
- <a href="https://docs.python.org/3/using/mac.html">How to install Python on OSX</a></li>

Once Python is installed on your computer, you will need
to download Morrowind Dialog Explorer and unzip the
archive. (The download link is at the top of this page.)
You will need to set up MWDE by going into the extracted
folder and opening the file named "config.ini".
INI files are only a special kind of text file, so you
can edit it with Notepad or your choice of plain text
editor.

Inside "config.ini" is a lot of text to help you understand
how it works. The most important part is to enter the
paths to the Morrowind data files you want to load inside
the "load_file_paths" section.
Normally, this would be the paths to your Morrowind.esm,
Tribunal.esm, and Bloodmoon.esm files.

Once you've set up your file paths, you're ready to run
MWDE. Go back to the folder (the same one "config.ini" is in).
On Windows, double-click on "Morrowind Dialog Explorer.bat".
On OSX, open "Morrowind Dialog Explorer.app" instead.
A new console window will open and it will show something
like this.

```
C:\MWDE>"C:\MWDE\Morrowind Dialog Explorer.bat"

C:\MWDE\Morrowind Dialog Explorer>python src/dialog_explorer.py --config-path="./config.ini"
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Morrowind.esm"...
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Tribunal.esm"...
Loading "C:\Steam\steamapps\common\Morrowind\Data Files\Bloodmoon.esm"...
Finished loading 3 data files.

Morrowind Dialog Explorer v1.0 is ready.
query >
```

Now you're ready to start exploring!
You can type "help" into the console for a list of commands.
You can type "help &lt;command&gt;" to get help about how
to use a particular command.
