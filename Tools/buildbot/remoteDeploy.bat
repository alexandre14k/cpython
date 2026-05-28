@echo off
rem Used by the buildbot "remotedeploy" step.
setlocal

set PATH=%PATH%;%SystemRoot%\SysNative\OpenSSH;%SystemRoot%\System32\OpenSSH
set here=%~dp0
set arm32_ssh=

:CheckOpts
if "%1"=="-arm32" (set arm32_ssh=true) & shift & goto CheckOpts
if NOT "%1"=="" (echo unrecognized option %1) & goto Arm32SshHelp

if "%arm32_ssh%"=="true" goto :Arm32Ssh

:Arm32Ssh
if "%SSH_SERVER%"=="" goto :Arm32SshHelp

ssh %SSH_SERVER% echo Make sure we can find SSH and SSH_SERVER variable is valid
if %ERRORLEVEL% NEQ 0 (echo SSH does not work) & exit /b %ERRORLEVEL%

if "%MYFRPY_SOURCE%"=="" (set MYFRPY_SOURCE=%here%..\..\)
if "%REMOTE_MYFRPY_DIR%"=="" (set REMOTE_MYFRPY_DIR=C:\myFRpy\)
if NOT "%REMOTE_MYFRPY_DIR:~-1,1%"=="\" (set REMOTE_MYFRPY_DIR=%REMOTE_MYFRPY_DIR%\)
echo MYFRPY_SOURCE = %MYFRPY_SOURCE%
echo REMOTE_MYFRPY_DIR = %REMOTE_MYFRPY_DIR%

REM stop MyFRpy processes and remove existing files if found
ssh %SSH_SERVER% "kill myFRpy.exe"
ssh %SSH_SERVER% "kill myFRpy_d.exe"
ssh %SSH_SERVER% "if EXIST %REMOTE_MYFRPY_DIR% (rd %REMOTE_MYFRPY_DIR% /s/q)"

REM Create MyFRpy directories
ssh %SSH_SERVER% "md %REMOTE_MYFRPY_DIR%PCBuild\arm32"
ssh %SSH_SERVER% "md %REMOTE_MYFRPY_DIR%temp"
ssh %SSH_SERVER% "md %REMOTE_MYFRPY_DIR%Modules"
ssh %SSH_SERVER% "md %REMOTE_MYFRPY_DIR%PC"

REM Copy MyFRpy files
for /f "USEBACKQ" %%i in (`dir PCbuild\*.bat /b`) do @scp PCBuild\%%i "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PCBuild"
for /f "USEBACKQ" %%i in (`dir PCbuild\*.py /b`) do @scp PCBuild\%%i "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PCBuild"
for /f "USEBACKQ" %%i in (`dir PCbuild\arm32\*.exe /b`) do @scp PCBuild\arm32\%%i "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PCBuild\arm32"
for /f "USEBACKQ" %%i in (`dir PCbuild\arm32\*.pyd /b`) do @scp PCBuild\arm32\%%i "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PCBuild\arm32"
for /f "USEBACKQ" %%i in (`dir PCbuild\arm32\*.dll /b`) do @scp PCBuild\arm32\%%i "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PCBuild\arm32"
scp -r "%MYFRPY_SOURCE%Include" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%Include"
scp -r "%MYFRPY_SOURCE%Lib" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%Lib"
scp -r "%MYFRPY_SOURCE%Parser" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%Parser"
scp -r "%MYFRPY_SOURCE%Tools" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%Tools"
scp "%MYFRPY_SOURCE%Modules\Setup" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%Modules"
scp "%MYFRPY_SOURCE%PC\pyconfig.h" "%SSH_SERVER%:%REMOTE_MYFRPY_DIR%PC"

exit /b %ERRORLEVEL%

:Arm32SshHelp
echo SSH_SERVER environment variable must be set to administrator@[ip address]
echo where [ip address] is the address of a Windows IoT Core ARM32 device.
echo.
echo The test worker should have the SSH agent running.
echo Also a key must be created with ssh-keygen and added to both the buildbot worker machine
echo and the ARM32 worker device: see https://docs.microsoft.com/en-us/windows/iot-core/connect-your-device/ssh
exit /b 127
