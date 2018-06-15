import sys
from cx_Freeze import setup, Executable
import os


os.environ['TCL_LIBRARY'] = r"D:\Users\Andres\Python36\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"D:\Users\Andres\Python36\tcl\tk8.6"

setup(
    name = "vistacabeceras",
    version = "1",
    description = ".",
    options = {"build_exe": {"packages":[],"include_files": ["tcl86t.dll", "tk86t.dll"]}},
    executables = [Executable("Informes_trafico_interfaz.py")])
