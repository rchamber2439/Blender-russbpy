REM
REM blender.bat - Launch Blender against a Python file
REM
REM The command below uses the default Blender install path on Windows.
REM
set PYTHONPATH="c:\program files\blender foundation\blender\2.76\python;%~p0"
"c:\program files\blender foundation\blender\blender-app.exe" -P %1 %2 %3 %4 %5 %6 %7 %8 %9
