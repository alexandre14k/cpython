@rem Recreate some myFRpy charmap codecs from the Windows function
@rem MultiByteToWideChar.

@cd /d %~dp0
@mkdir build
@rem Arabic DOS code page
c:\myFRpy30\myFRpy genwincodec.py 720 > build/cp720.py
