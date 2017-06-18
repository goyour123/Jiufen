import sys
from cx_Freeze import setup, Executable
import matplotlib, numpy
import os

os.environ['TCL_LIBRARY'] = r'C:\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Anaconda3\tcl\tk8.6'

base = 'Console'
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'excludes': ['gtk', 'PyQt5', 'Tkinter'],
        'includes': ['numpy.core._methods', 'numpy.lib.format', 'idna.idnadata']
    }
}

executables = [
    Executable('Jiufen.py', base=base)
]

setup(name='Jiufen',
      version='1.0',
      description='Gold price analyzer',
      executables=executables,
      options=options
      )
