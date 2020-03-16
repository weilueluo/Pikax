
@echo off
set build_dir="build_debug"


echo PIKAX DEBUG BUILD
echo.
echo Build starting in current directory: %cd%
echo Using Build debug Directory: %build_dir%
echo.

call :run "Checking build directory ... " "if exist %build_dir% ( start """" /wait cmd /c ""echo Build directory %build_dir% exists, please remove the folder first!&echo(&pause"" exit)"

call :run "Creating virtual environment ... " "virtualenv %build_dir%"

call :run "Adding scripts files to virtual environment ... " "for %%%%f in (py spec txt) do xcopy *.%%%%f %build_dir%"

call :run "Adding assets files to virtual environment ... " "mkdir "%build_dir%/assets" && xcopy /s assets "%build_dir%/assets""

call :run "Activating virtual environment ... " "cd %build_dir%/Scripts && call activate.bat"

call :run "Installing required dependencies ... " "cd .. && pip install -r requirements.txt"

call :run "Building executable using pyinstaller ..." "pyinstaller debug.spec"

call :success

:run
echo %~1
%~2
if errorlevel 1 goto :fail
echo.
exit /b 0

:fail
echo.### Build Failed ###
goto :end

:success
echo.Build Successful
goto :end

:end
echo.Build Debug Finished in directory: %build_dir%
PAUSE
goto :eof