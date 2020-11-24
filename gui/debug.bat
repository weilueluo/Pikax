
@echo off
set build_dir="build_debug"


echo PIKAX DEBUG BUILD
echo.
echo Build starting in current directory: %cd%
echo Using Build debug Directory: %build_dir%
echo.

echo Checking build directory ...
if exist %build_dir% (
    echo Build directory: %build_dir% already exists
    goto :fail
)

echo Creating virtual environment ...
virtualenv %build_dir%

echo Adding scripts files to virtual environment ...
for %%f in (py spec txt) do xcopy *.%%f %build_dir%
if errorlevel 1 goto :fail

echo Adding assets files to virtual environment ...
mkdir "%build_dir%/assets" && xcopy /s assets "%build_dir%/assets"
if errorlevel 1 goto :fail

echo Activating virtual environment ...
cd %build_dir%/Scripts && call activate.bat
if errorlevel 1 goto :fail

echo Installing required dependencies ...
cd .. && pip install -r requirements.txt
if errorlevel 1 goto :fail

echo Building executable using pyinstaller ...
pyinstaller debug.spec
if errorlevel 1 goto :fail

call :success

:fail
echo.### Build DEBUG Failed ###
goto :end

:success
echo.Build Successful
goto :end

:end
echo.Build Debug Finished in directory: %build_dir%
PAUSE
exit