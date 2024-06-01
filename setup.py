from cx_Freeze import setup, Executable

# Reemplaza "script.py" con el nombre de tu script
executables = [Executable("gui.py", base="Win32GUI")]

setup(
    name="MyApp",
    version="0.1",
    description="My application!",
    executables=executables,
)