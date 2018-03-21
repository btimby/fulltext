rem ==========================================================================
rem Shortcuts for various tasks, emulating UNIX "make" on Windows.
rem ==========================================================================

set HOME=%USERPROFILE%
set PYTHON=C:\Python36\python.exe

%PYTHON% fulltext\data\winmake.py %1 %2 %3 %4 %5 %6
