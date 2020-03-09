
@echo off
set build_dir="build_env"


echo PIKAX BUILD
echo.
echo Build starting in current directory: %cd%
echo Using Build Directory: %build_dir%
echo.

REM check build directory does not exists
echo|set /p="Checking build directory ... "
if exist %build_dir% (
    start "" /wait cmd /c "echo Build directory %build_dir% exists, please remove the folder first!&echo(&pause"
    exit
)
echo done
echo.

call :run "Creating virtual environment ... " "virtualenv %build_dir%" 

call :run "Adding files to virtual environment ... " "for %%f in (py spec txt) do xcopy *.%%f %build_dir% && xcopy /r assets %build_dir%"

call :run "Activating virtual environment ... " "cd %build_dir%/Scripts && call activate.bat"

call :run "Installing required dependencies ... " "cd .. && pip install -r requirements.txt"

call :run "Building executable using pyinstaller ..." "pyinstaller main.spec"


:run
echo %~1
%~2
if ERROR_LEVEL 1 goto :fail
echo.
exit /b 0

:fail
echo.### Build Failed ###
goto :end

:success
echo.Build Successful
goto :end

:end
echo.Build finished
PAUSE