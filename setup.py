import sys
from cx_Freeze import setup, Executable

base = None
#base = "Win32GUI"

build_exe_options = {"include_files": ['assets', 'freesansbold.ttf', 'default', 'rooms.txt', 'users.txt', 'sleekxmpp']}

setup(  name = "pyStratego",
            version = "0.1",
            description = "Multiplayer Online Ultimate Stratego",
            author = "Andrew Francis",
            author_email= "agf33@cornell.edu",
            options = {"build_exe": build_exe_options},
            executables = [Executable("main.py", base=base)])