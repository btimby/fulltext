@echo off

rem ==========================================================================
rem Shortcuts for various tasks, emulating UNIX "make" on Windows.
rem ==========================================================================


IF "%PYTHON%"=="" (
    IF EXIST C:\Python35-64 SET PYTHON=C:\Python35-64\python.exe
)

rem Needed to locate the .pypirc file and upload exes on PYPI.
set HOME=%USERPROFILE%

%PYTHON% fulltext\data\winmake.py %1 %2 %3 %4 %5 %6
