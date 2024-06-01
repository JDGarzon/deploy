from cx_Freeze import setup, Executable

# Reemplaza "script.py" con el nombre de tu script
executables = [Executable("script.py", base="Win32GUI", icon="path/to/icon.ico")]

setup(
    name="MyApp",
    version="0.1",
    description="My application!",
    executables=executables,
)