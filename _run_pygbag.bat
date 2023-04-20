

set DEST=blueball1
@rem  It will be also the name of .apk file


rd /Q /S %DEST%
mkdir %DEST%


xcopy main.py %DEST%\
xcopy levels.py %DEST%\
xcopy blocks.png %DEST%\
xcopy sound\*.ogg %DEST%\sound\


python -m pygbag --app_name BlueBall --package com.torec.blueball --title "Blue Ball" --icon "favicon.png" %DEST%
