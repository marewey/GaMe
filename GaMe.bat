@echo off
set log=nul
set version=1.2
mkdir cache\scores 2>nul
mkdir data 2>nul
set cd_=%cd%
set args=%*
set url=markspi.ddns.me
echo.Initializing...

SetLocal EnableDelayedExpansion Enableextensions
For /F %%a In ('Copy /Z "%~dpf0" Nul') Do Set "CR=%%a"
::========== MAKE SCREEN BIGGER ==========::
set "cmd.con=HKCU\Console\%%SystemRoot%%_system32_cmd.exe /v"
set "ram=!tmp!\WRAM.tmp"
del "%tmp%\_$xy.bat">nul 2>&1
if [%1]==[ok] goto :init
Reg export HKCU\Console Backup.reg>nul
Reg delete HKCU\Console\%%SystemRoot%%_system32_cmd.exe /f>nul
for %%a in (
"FaceName /t REG_SZ /d "Terminal" /f"
"FontFamily /t REG_DWORD /d 48 /f"
"FontSize /t REG_DWORD /d 2610612 /f"
"FontWeight /t REG_DWORD /d 900 /f"
"ScreenBufferSize /t REG_DWORD /d 13107280 /f"
"CursorSize /t REG_DWORD /d 1 /f"
) do (
set "param=%%a"
set "param=!param:~1!"
set "param=%cmd.con% !param:~0,-1!"
Reg Add !param! >nul
)
start /high cmd /q /k "%~0" ok %arg%
for %%a in (
"FaceName /f"
"FontFamily /f"
"FontSize /f"
"FontWeight /f"
"CursorSize /f"
) do (
set "param=%%a"
set "param=!param:~1!"
set "param=%cmd.con% !param:~0,-1!"
Reg Delete !param! >nul
)
del Backup.reg 2>nul
exit
::===============================================::
:init
call :load
goto :init
:load
title GaMe
call :codepage
call :makeBG
call :script.music silent
set toffset=3
set rate=300
set out=0
set pd=5
set rows=9
set view=18
set mem=80
set difficulty=2
set color_on=1
set mute=0
set music=1
::min of 5 for speed
set speed=10
call :net.check
if "%connection%"=="1" call :gam.update
ping localhost -n 2 >nul
:play
copy nul .stop >nul 2>nul
::if "%color_on%"=="-1" set color_on=0
call :gam.conf.load
call :gam.format
if "%color_on%"=="1" bin\bg.exe Locate 0 0&bin\bg.exe print 8 "%test_%"
if "%sel%"=="" set sel=1
bin\bg.exe Cursor 0
call :gam.music 1
goto :gam.menu
:start
::Setup start values
set gems=0
set special=0
set lives=3
set level=0
set score=0
set ymin=0
set gemSeed=209
set /a damage=0
set boomSeed=1
set heartSeed=101
set xmax=%rows%
set ymax=%view%
set /a x=%xmax%/2
set x_=%x% %% 2
if not "%x_%"=="0" set /a x=%x%+1
set y=2
set /a start=0
set /a end=%start%+%mem%
copy nul .stop >nul 2>nul
del .pause 2>nul
del .stop 2>nul
::LOADING BAR
for /l %%t in (0,2,%xwin%) do set /a tmpside=!tmpside!+1
set /a tmpside=!tmpside!-8
set /a tmpheight=!ywin!-3
bin\bg.exe fcprint !tmpheight! !tmpside! F "Loading Game..."
set /a tmpheight=!tmpheight!+1
if "%color_on%"=="1" (
	set /a xwin_tmp=!xwin!-2
	for /l %%a in (1,1,!xwin_tmp!) do (
		set /a sleep_=%%a + !random! %% 150
		bin\bg.exe fcprint !tmpheight! %%a F "Û"
		bin\bg.exe sleep !sleep_!
		if "%%a"=="4" call :script.ic silent
		if "%%a"=="10" call :script.music silent
	)
)
set tmpside=
call :gam.load
start /min bin\inputcontroller.bat
call :gam.music 0
bin\bg.exe Locate 0 0
bin\bg.exe print 8 "%test_%"
set refresh_top=1
call :gam.refresh.icons
title GaMe
set tptC=0
set tss=%time%
:a
call :gam.input
call :gam.usr
call :gam.draw
call :gam.action
goto :a
:gam.input
set last_input=%input%
::Get input from keyboad/mouse
bin\getinput.exe
set input=%errorlevel%
goto :eof
:gam.usr
::Move User along the map
::Take input and process
set x%x%-y%y%= 
set /a y=%y%+1
if "%input%"=="293" set /a x=%x%-1
if "%input%"=="295" set /a x=%x%+1
if "%input%"=="32" call :gam.boom
if "%input%"=="13" call :gam.boom
if "%input%"=="27" call :gam.music -1&set pausetimestart=%time%&call :gam.pause&title GaMe&set refresh_top=1&call :gam.music 1
set lpos=%pos%
set pos=!x%x%-y%y%!
if not "%lpos%"==" " if not "%lpos%"=="." if not "%lpos%"=="%char_gem%" if not "%lives%"=="10" if not "%special%"=="5" call :gam.refresh.icons
set x%x%-y%y%=%char_down%
if "%input%"=="3" set lives=0&set x%x%-y%y%=X
if "%input%"=="113" set lives=0&set x%x%-y%y%=X
set /a x_win_pos=%xside%+%x%
set y_view=%y%
goto :eof
:gam.draw
::Write active part of map to screen from memory
if "%color_on%"=="0" (
	bin\bg.exe Locate 0 0
	echo.%test%%bs_%%hearts% %boom%
	for /l %%y in (%ymin%,1,%ymax%) do (
		for /l %%x in (1,1,%xmax%) do (
			set line%%y=!line%%y!!x%%x-y%%y!
		)
		set /p "=%side%º!line%%y!º%side%" <NUL
		set line%%y=
	)
	::Write score and level
	set /p "=%test%%bs_%" <NUL
	set /p "=SCORE: %score%  LVL: %level% GEMS: %gems%" <NUL
)

if "%color_on%"=="1" (
	set /a ywin_tmp=%ywin%-2
	if "!refresh_top!"=="1" bin\bg.exe Locate 0 0
	if "!refresh_top!"=="1" bin\bg.exe print 8 "%test%"
	if "!refresh_top!"=="1" bin\bg.exe Locate 0 0
	if "!refresh_top!"=="1" bin\bg.exe print 4 "%hearts% " D "%boom%"
	if "!refresh_top!"=="1" set refresh_top=0
	bin\bg.exe Locate 1 0
	set color_stack=
	for /l %%y in (%ymin%,1,%ymax%) do (
		for /l %%x in (1,1,%xmax%) do (
			if "!x%%x-y%%y!"=="%char_heart%" set line%%y=!line%%y!" 4 "%char_heart%" F "
			if "!x%%x-y%%y!"=="%char_gem%" set line%%y=!line%%y!" A "%char_gem%" F "
			if "!x%%x-y%%y!"=="%char_sun%" set line%%y=!line%%y!" D "%char_sun%" F "
			if %lives% gtr 0 if "%pos%"=="%char_gem%" if "!x%%x-y%%y!"=="%char_down%" set line%%y=!line%%y!" A6 "%char_down%" F "
			if %lives% gtr 0 if "%pos%"=="%char_heart%" if "!x%%x-y%%y!"=="%char_down%" set line%%y=!line%%y!" 46 "%char_down%" F "
			if %lives% gtr 0 if "%pos%"=="%char_sun%" if "!x%%x-y%%y!"=="%char_down%" set line%%y=!line%%y!" D6 "%char_down%" F "
			if %lives% gtr 0 if not "%pos%"=="%char_sun%" if not "%pos%"=="%char_heart%" if not "%pos%"=="%char_gem%" if "!x%%x-y%%y!"=="%char_down%" set line%%y=!line%%y!" 6 "%char_down%" F "
			if %lives% leq 0 if "!x%%x-y%%y!"=="X" set line%%y=!line%%y!" C4 "X" F "
			if not "!x%%x-y%%y!"=="%char_heart%" if not "!x%%x-y%%y!"=="%char_gem%" if not "!x%%x-y%%y!"=="%char_sun%" if not "!x%%x-y%%y!"=="%char_down%" if not "!x%%x-y%%y!"=="X" set line%%y=!line%%y!!x%%x-y%%y!
		)
		set color_stack=!color_stack! 8 "%side%" F "º!line%%y!º" 8 "%side%"
		set line%%y=
	)
	bin\bg.exe print !color_stack!
	::Write score and level
	bin\bg.exe Locate !ywin_tmp! 0
	bin\bg.exe print F "SCORE:%score% LVL:%level% " A "%char_gem%" F ":%gems%"
	
)
::Erase last row from memory
set /a ly=%ymin%-1
for /l %%x in (1,1,%xmax%) do (
	set x%%x-y%ly%=
)
goto :eof
:gam.refresh.icons
::Convert lives into hearts
set hearts=
for /l %%a in (1,1,!lives!) do (
	set hearts=%char_heart%!hearts!
)
set boom=
for /l %%a in (1,1,!special!) do (
	set boom=%char_sun%!boom!
)
set refresh_top=1
goto :eof
:gam.action
::Move map down
set /a ymin=%ymin%+1
set /a ymax=%ymax%+1
::Add points
set /a score=%score%+1
::Detect if at the end of map in memory
if "%end%"=="%ymax%" call :gam.add
::If touching gems/hearts/suns add stuff
if "%pos%"=="%char_gem%" call :gam.add.gem&goto :eof
if "%pos%"=="%char_heart%" call :gam.add.heart&goto :eof
if "%pos%"=="%char_sun%" call :gam.add.boom&goto :eof
::If touching anything else, lose a life.
if not "%pos%"==" " if not "%pos%"=="." call :gam.damage
if %lives% leq 0 set /a ymin=!ymin!-1&set /a ymax=!ymax!-1&goto :gam.gameover
goto :eof
:gam.add.heart
if not "%lives%"=="10" set /a lives=%lives%+1&call :gam.refresh.icons&if "%mute%"=="0" start /b "" bin\bg.exe play cache\heart.wav
goto :eof
:gam.add.gem
set /a score=%score%+(5*%difficulty%)+5
set /a gems=%gems%+1
if "%mute%"=="0" start /b "" bin\bg.exe play cache\gem.wav
goto :eof
:gam.add.boom
set /a boom_tot=%boom_tot%+1
if not "%special%"=="5" set /a special=%special%+1&call :gam.refresh.icons&if "%mute%"=="0" start /b "" bin\bg.exe play cache\boom.wav
goto :eof
:gam.damage
set /a damage=%damage%+1
if "%mute%"=="0" start /b "" bin\bg.exe play cache\damage.wav
::@0 SHIELD: -3
if "%special%"=="0" set /a lives=%lives%-3
::@1 SHIELD: -2
if "%special%"=="1" set /a lives=%lives%-2
::@2 SHIELD: 1/2 of -1 + 1/2 of -2
if "%special%"=="2" set /a rand=%random% %% 2
if "%special%"=="2" if not "!rand!"=="0" set /a lives=%lives%-2
if "%special%"=="2" if "!rand!"=="0" set /a lives=%lives%-1
::@3 SHIELD: 1/4 of -1 + 3/4 of -2
if "%special%"=="3" set /a rand=%random% %% 4
if "%special%"=="3" if not "!rand!"=="0" set /a lives=%lives%-2
if "%special%"=="3" if "!rand!"=="0" set /a lives=%lives%-1
::@4 SHIELD: 1/4 of -2 + 3/4 of -1
if "%special%"=="4" set /a rand=%random% %% 4
if "%special%"=="4" if "!rand!"=="0" set /a lives=%lives%-2
if "%special%"=="4" if not "!rand!"=="0" set /a lives=%lives%-1
::@5 SHIELD: 1/8 of -1 + 1/8 of no effect (keep shield)
if "%special%"=="5" set /a rand=%random% %% 8
if "%special%"=="5" if "!rand!"=="0" set /a lives=%lives%-1
if "%special%"=="5" if "!rand!"=="7" goto :eof
::subract 1 SHIELD
if %special% gtr 0 set /a special=%special%-1
call :gam.refresh.icons
goto :eof
:gam.boom
call :gam.refresh.icons
if "%special%"=="0" goto :eof
set /a special=%special%-1
set /a nx=%x%+3
set /a ny=%y%+4
set /a lx=%x%-3
for /l %%y in (%y%,1,%ny%) do (
	for /l %%x in (%lx%,1,%nx%) do (
		if not "!x%%x-y%%y!"==" " if not "!x%%x-y%%y!"=="%char_gem%" if not "!x%%x-y%%y!"=="%char_heart%" if not "!x%%x-y%%y!"=="%char_sun%" set x%%x-y%%y=.
	)
)
goto :eof
:gam.add
::Move the borders of map memory down and generate/load it
set /a start=%mem%+%start%
set /a end=%mem%+%end%
call :gam.load
goto :eof

:: ========== INIT/FINISH ========== ::

:gam.menu
title GaMe - Menu
set name=
if "%color_on%"=="1" bin\bg.exe Locate 0 0&bin\bg.exe print 8 "%test_%"
:gam.menu0
::The Main Menu
if "%color_on%"=="0" for /l %%s in (1,1,8) do set sel%%s= 
if "%color_on%"=="1" for /l %%s in (1,1,8) do set sel%%s=" 7 " 
if "%color_on%"=="0" set sel%sel%=^^^>
if "%color_on%"=="1" set sel%sel%=^>
if "%color_on%"=="0" (
	cls
	echo.%test%
	echo... Gems and Meteors
	echo.%test%
	echo... %sel1% Start GaM
	echo... %sel2% Scores
	echo... %sel3% Controls
	echo... %sel4% Goals
	echo... %sel5% Color On: %color_on% [C]
	echo... %sel6% Muted: %mute% [M]
	echo... %sel7% Difficulty: %difficulty%
	echo... %sel8% Quit
	echo.%test%
)
if "%color_on%"=="1" (
	for /l %%t in (0,2,%xwin%) do set /a tmpside=!tmpside!+1
	set /a tmpside=!tmpside!-9
	bin\bg.exe Locate 3 !tmpside!&bin\bg.exe print A "Gems" 7 " and " F "Meteors\n"
	bin\bg.exe Locate 5 !tmpside!&bin\bg.exe print 8F "%sel1% Start GaM     \n"
	bin\bg.exe Locate 6 !tmpside!&bin\bg.exe print 8F "%sel2% Scores        \n"
	bin\bg.exe Locate 7 !tmpside!&bin\bg.exe print 8F "%sel3% Controls      \n"
	bin\bg.exe Locate 8 !tmpside!&bin\bg.exe print 8F "%sel4% Goals         \n"
	bin\bg.exe Locate 9 !tmpside!&bin\bg.exe print 8F "%sel5% Color On: %color_on%   \n"
	bin\bg.exe Locate 10 !tmpside!&bin\bg.exe print 8F "%sel6% Muted: %mute%      \n"
	bin\bg.exe Locate 11 !tmpside!&bin\bg.exe print 8F "%sel7% Difficulty: %difficulty% \n"
	bin\bg.exe Locate 12 !tmpside!&bin\bg.exe print 8F "%sel8% Quit          \n"
)
set tmpside=
call :gam.input
if "%input%"=="294" set /a sel=%sel%-1
if "%input%"=="296" set /a sel=%sel%+1
if "%sel%"=="0" set sel=8
if "%sel%"=="9" set sel=1
if "%input%"=="3" call :gam.music -1&del .stop&exit
if "%input%"=="113" call :gam.music -1&del .stop&exit
if not "%input%"=="13" goto :gam.menu0
if "%sel%"=="1" goto :start
if "%sel%"=="2" goto :gam.download
if "%sel%"=="3" call :gam.controls&goto :gam.menu
if "%sel%"=="4" call :gam.goals&goto :gam.menu
if "%sel%"=="5" if "%color_on%"=="1" set color_on=-1
if "%sel%"=="5" if "%color_on%"=="0" set color_on=1
if "%sel%"=="6" if "%mute%"=="1" set mute=-1
if "%sel%"=="6" if "%mute%"=="0" set mute=1
if "%sel%"=="7" set /a difficulty=%difficulty%+1
if "%sel%"=="8" call :gam.music -1&del .stop&exit
if "%difficulty%"=="5" set difficulty=1
if "%sel%"=="5" if "%color_on%"=="-1" set color_on=0&call :gam.conf.save
if "%sel%"=="5" if "%color_on%"=="1" call :gam.conf.save&bin\bg.exe Locate 0 0&bin\bg.exe print 8 "%test_%"
if "%sel%"=="6" if "%mute%"=="-1" set mute=0&call :gam.conf.save
if "%sel%"=="6" if "%mute%"=="1" call :gam.conf.save
if "%sel%"=="7" call :gam.music -1&call :gam.format&call :gam.conf.save
if "%sel%"=="7" if "%color_on%"=="1" bin\bg.exe Locate 0 0&bin\bg.exe print 8 "%test_%"
goto :gam.menu0
:gam.goals
cls
bin\bg.exe locate 0 5
echo.GOALS:
echo.
echo.  Avoid all Meteors
echo.  %char_gem% : +10 points %char_gem%
echo.  %char_heart% : +1 life %char_heart%
echo.  %char_sun% : +1 SHIELD %char_sun%
echo.
echo.  Holding %char_sun% will lower damage 
echo.
echo.  Score Calculation:
echo.   SCORE
echo.   BONUS [{LVL*2}*{DIFF*2}]
echo.   BONUS [{DMG*2}*{DIFF*2}]
echo.   ________________________
echo.   TOTAL
pause >nul
goto :eof
:gam.controls
cls
if "%color_on%"=="1" bin\bg.exe print 8 "%test_%"
bin\bg.exe locate 0 0
echo.    CONTROLS:    
echo.%test%
echo.    LEFT -- Go Left       
echo.    RIGHT - Go Right      
echo.    SPACE - Use SHIELD    
echo.    ESC --- Pause         
echo.    Q/^^^C -- Quit/Die      
echo.%test%
pause >nul
goto :eof
:gam.load
::Add level for each map loaded
set /a level=%level%+1
set /a level_=%level_%+1
if "%level_%"=="10" set /a prb=%prb%+1&set level_=0
if "%level:~-2%"=="00" set prb_=%prb%&set prb=-1&set heartSeed=180&set gemSeed=500&set boomSeed=64
if "%level:~-2%"=="01" set prb=%prb_%&set heartSeed=101&set gemSeed=209&set boomSeed=1
if "%level:~-2%"=="50" set prb_=%prb%&set prb=-1&set heartSeed=120&set gemSeed=300&set boomSeed=32
if "%level:~-2%"=="51" set prb=%prb_%&set heartSeed=101&set gemSeed=209&set boomSeed=1
::Generate probabilities
for /l %%p in (0,1,9) do (
	set /a prb%%p=%%p*100+!prb!
)
::Generate Map based off probabilities and output to map file
for /l %%y in (%start%,1,%end%) do (
	for /l %%x in (1,1,%xmax%) do (
		set /a num=!random! %% 1000
		set char= 
		if !num! geq 0 if !num! leq %boomSeed% set char=%char_sun%
		if !num! geq 100 if !num! leq %heartSeed% set char=%char_heart%
		if !num! geq 200 if !num! leq %gemSeed% set char=%char_gem%
		if !num! geq 50 if !num! leq %prb0% set char=Þ
		if !num! geq 150 if !num! leq %prb1% set char=@
		if !num! geq 250 if !num! leq %prb2% set char=#
		if !num! geq 300 if !num! leq %prb3% set char=Û
		if !num! geq 400 if !num! leq %prb4% set char=²
		if !num! geq 500 if !num! leq %prb5% set char=Ý
		if !num! geq 600 if !num! leq %prb6% set char=°
		if !num! geq 700 if !num! leq %prb7% set char=±
		if !num! geq 800 if !num! leq %prb8% set char=ß
		if !num! geq 900 if !num! leq %prb9% set char=Ü
		set x%%x-y%%y=!char!
	)
)
::Clear a starting path (+5) if first map
set /a ly=%y%-1
set /a ny=%y%+5
for /l %%y in (%ly%,1,%ny%) do (
	if "%level%"=="1" if not "!x%x%-y%%y!"==" " set x%x%-y%%y= 
)
goto :eof
:gam.format
echo.
::Choose game settings based off difficulty
if "%difficulty%"=="1" set rows=13&set view=19&set rate=145&set prb=5&set mem=50&set pd=4
if "%difficulty%"=="2" set rows=11&set view=17&set rate=140&set prb=7&set mem=60&set pd=5
if "%difficulty%"=="3" set rows=9&set view=15&set rate=135&set prb=10&set mem=80&set pd=6
if "%difficulty%"=="4" set rows=6&set view=13&set rate=130&set prb=12&set mem=95&set pd=8
if "%difficulty%"=="0" set rows=15&set view=20&set rate=200&set prb=8&set mem=65&set pd=5
::set /a icrate=1
::Generate the numbers on window and screen
set xmax=%rows%
set ymax=%view%
set /a pad=%pd%+(%xmax%/2)
set /a xwin=%xmax%+2+(%pad%*2)
set /a ywin=%ymax%+4
set side=&set spc=&set spc_=&set bs=&set bs_=&set test=&set test_=&set xside=0
::Generate display shortcuts
for /l %%x in (1,1,%xwin%) do (
	set bs_=!bs_!
	set spc_= !spc_!
	set test=.!test!
)
for /l %%y in (1,1,%ywin%) do (
	set bs=!bs_!!bs!
	set spc=!spc_!!spc!
	set test_=!test_!!test!
)
for /l %%x in (1,1,%pad%) do (
	set side=.!side!
	set /a xside=!xside!+1
)
mode con cols=%xwin% lines=%ywin%
mode con rate=%rate%
call :script.ic silent
goto :eof
:gam.update
::Update program if version changed
set /p "=Downloading missing assets... " <NUL
if not exist "bin\getinput.exe" set /p "=getinput.exe " <NUL&bin\wget.exe -O bin\getinput.exe http://%url%/game/getinput.exe 2>nul
if not exist "bin\bg.exe" set /p "=bg.exe " <NUL&bin\wget.exe -O bin\bg.exe http://%url%/game/bg.exe 2>nul
if not exist "cache\music.mp3" set /p "=music.mp3 " <NUL&bin\wget.exe -O cache\music.mp3 http://%url%/game/sounds/music.mp3 2>nul
if not exist "cache\boom.wav" set /p "=boom.wav " <NUL&bin\wget.exe -O cache\boom.wav http://%url%/game/sounds/boom.wav 2>nul
if not exist "cache\damage.wav" set /p "=damage.wav " <NUL&bin\wget.exe -O cache\damage.wav http://%url%/game/sounds/damage.wav 2>nul
if not exist "cache\gem.wav" set /p "=gem.wav " <NUL&bin\wget.exe -O cache\gem.wav http://%url%/game/sounds/gem.wav 2>nul
if not exist "cache\heart.wav" set /p "=heart.wav " <NUL&bin\wget.exe -O cache\heart.wav http://%url%/game/sounds/heart.wav 2>nul
echo.
set /p "=Checking for updates... " <NUL
bin\wget.exe -O data\version http://%url%/game/version 2>nul
title 
for /f %%v in ('type data\version') do (
	if not "%version%"=="%%v" echo.Downloading Update...&bin\wget.exe -O GaM_.bat http://%url%/game/game.bat 2>nul
	if "%version%"=="%%v" echo.No Updates found.&goto :eof
)
echo.Press any key to install update.
pause >nul
move GaM_.bat GaMe.bat 2>nul >nul
::::::::::::::::
::::::::::::::::
::::::::::::::::
::::::::::::::::
::::::::::::::::
title 
start GaMe.bat
exit
:gam.conf.load
::Load settings File to memory
if not exist "data\settings" call :gam.conf.save
for /f "tokens=1-2 delims==" %%a in ('type data\settings') do set %%a=%%b
goto :eof
:gam.conf.save
::Load settings File to memory
call :gam.music -1
>data\settings echo.mem=%mem%
>>data\settings echo.difficulty=%difficulty%
>>data\settings echo.mute=%mute%
>>data\settings echo.color_on=%color_on%
>>data\settings echo.speed=%speed%
>>data\settings echo.music=%music%
call :gam.music 1
goto :eof
:gam.music
if "%1"=="-1" (
	taskkill /fi "windowtitle eq GaM - Music" >nul 2>nul&&taskkill /fi "imagename eq cscript" >nul 2>nul
)
if "%1"=="0" (
	taskkill /f /fi "imagename eq cscript.exe" >nul 2>nul
)
if "%1"=="1" (
	if "%mute%"=="0" if "%music%"=="1" start /min "" bin\music.bat
)
goto :eof
:gam.pause
title GaMe (Paused)
::Cover the window in dots
copy nul .pause >nul 2>nul
for /l %%t in (0,4,%ywin%) do set /a tmp=!tmp!+1
for /l %%t in (4,4,%ywin%) do set /a tmpp=!tmpp!+1
for /l %%t in (0,4,%xwin%) do set /a tmpside=!tmpside!+1
for /l %%t in (0,8,%xwin%) do set tmpspc=!tmpspc! 
set /a tmp_=%ywin%-2
set /a tmp_2=%ywin%-3
bin\bg.exe Locate 0 0
if "%color_on%"=="0" for /l %%a in (0,1,%tmp_%) do echo.%test%
if "%color_on%"=="1" for /l %%a in (0,1,%tmp_%) do bin\bg.exe print 8 "%test%"
bin\bg.exe Locate 0 0
echo.%hearts% %boom% 
bin\bg.exe Locate %tmpp% %tmpside%
echo.%tmpspc% GAME %tmpspc%
bin\bg.exe Locate %tmp% %tmpside%
echo.%tmpspc%PAUSED%tmpspc%
bin\bg.exe Locate !tmp_2! 0
set /p "=MUTED:%mute% COLOR:%color_on% DIFF:%difficulty% MEM:%mem%" <NUL
bin\bg.exe Locate !tmp_! 0
set /p "=SCORE:%score% LVL:%level% %char_gem%:%gems% " <NUL
bin\getinput.exe
set input=%errorlevel%
if "%input%"=="4" cls&call :gam.dev
set tmp=
set tmp_=
set tmpp=
set tmpside=
set tmpspc=
if "%input%"=="3" set lives=0&call :gam.pause.timefix&del .pause 2>nul&goto :eof
if "%input%"=="113" set lives=0&call :gam.pause.timefix&del .pause 2>nul&goto :eof
if "%input%"=="27" call :gam.pause.timefix&del .pause 2>nul&goto :eof
if "%input%"=="99" if "%color_on%"=="1" set color_on=-1
if "%input%"=="99" if "%color_on%"=="0" set color_on=1&call :gam.conf.save
if "%input%"=="99" if "%color_on%"=="-1" set color_on=0&call :gam.conf.save
if "%input%"=="109" if "%mute%"=="1" set mute=-1
if "%input%"=="109" if "%mute%"=="0" set mute=1&call :gam.conf.save
if "%input%"=="109" if "%mute%"=="-1" set mute=0&call :gam.conf.save
call :gam.refresh.icons
::m for mute 109
::c for color 99

goto :gam.pause
:gam.pause.timefix
set pausetimeend=%time%
if "%pausetimestart:~0,1%"==" " set pausetimestart=0%pausetimestart:~1%
if "%pausetimeend:~0,1%"==" " set pausetimeend=0%pausetimeend:~1%
set /a pausetimeendC=(1%pausetimeend:~0,2%-100)*360000 + (1%pausetimeend:~3,2%-100)*6000 + (1%pausetimeend:~6,2%-100)*100 + (1%pausetimeend:~9,2%-100)
set /a pausetimestartC=(1%pausetimestart:~0,2%-100)*360000 + (1%pausetimestart:~3,2%-100)*6000 + (1%pausetimestart:~6,2%-100)*100 + (1%pausetimestart:~9,2%-100)
set /a pausetimeC=%pausetimeendC%-%pausetimestartC%
set /a tptC=%tptC%+%pausetimeC%
goto :eof

:gam.dev
bin\bg.exe Cursor 1
set /p cmd=CMD: 
%cmd%
pause >nul
bin\bg.exe Cursor 0
goto :eof

:gam.gameover
title GaMe - Gameover
::Display last frame
set hearts=YOU DIED
set refresh_top=1
set x%x%-y%y%=X
call :gam.draw
call :gam.music -1
ping localhost -n 3 >nul
::Stop the input controller
copy nul .stop >nul
set letternum=1
set letter1=_
set letter2=_
set letter3=_
::Generate final scores/info
call :ttt
set /a bonus=(%level%*2)*(%difficulty%*2)+(%difficulty%*2)*(%damage%*2)
set /a bonus=%bonus%+%ttt:~0,-2%
set /a fs=%score%+%bonus%
SetLocal EnableDelayedExpansion Enableextensions
For /F %%a In ('Copy /Z "%~dpf0" Nul') Do Set "CR=%%a"
:gam.name
title GaMe - Gameover (%letter1%%letter2%%letter3%)
cls
::Display scores/info
echo.%test%
echo.... GAME OVER
echo.%test%
echo.... Score: %score%
echo.... Level: %level%
echo.... Difficulty: %difficulty%
echo.... Total Damage: %damage%
echo.... GEMS: %gems%
if not "%tttH%"=="00" echo.... Time: %tttH%:%tttM%:%tttS%.%tttQ%
if "%tttH%"=="00" echo.... Time: %tttM%:%tttS%.%tttQ%
echo.%test%
echo.... Bonus: %bonus%
echo.%test%
echo.... Final Score: %fs%
echo.%test%
echo.Please Enter your initials:
echo.%letter1% %letter2% %letter3%
set "Key="
For /F "Delims=" %%K In ('Xcopy /W "%~f0" "%~f0" 2^>Nul') Do (
	If Not Defined Key (
		Set "Key=%%K"
		set "key=!Key:~-1!"
	)
)

If /i "!Key!" Equ "!CR!" (
  if "%letternum%"=="4" goto gam.upload
  goto gam.name
)
If /i "!Key!" Equ "" (
  if not "%letternum%"=="1" set /a letternum=%letternum% - 1
  set letter!letternum!=_
  goto gam.name
)
If /i "!Key!" Equ "	" (
  goto :gam.download
)
if "%letternum%"=="4" goto gam.name
set letter%letternum%=%key%
set /a letternum=%letternum% + 1
goto gam.name
:upload.missing
echo.Uploading previous scores...
for /f "tokens=1-9 delims=;" %%a in ('type cache\offline.scores') do bin\wget --spider "http://%url%/game/score.php?name=%%a&fs=%%b&score=%%c&bonus=%%d&level=%%e&difficulty=%%f&gems=%%g&ttt=%%h&damage=%%i" 2>%log%
title 
del cache\offline.scores 2>nul
goto :eof
:gam.upload
echo.%bs%%test%%bs%Uploading Score...
call :net.check
set name=%letter1%%letter2%%letter3%
set score_=%score%
if "%score_:~0,-1%"=="" set score_=0%score%
if "%connection%"=="0" echo.No Internet Connection. Could not upload score.&>>cache\offline.scores echo.%name%;%fs%;%score%;%bonus%;%level%;%difficulty%;%gems%;%tttH%:%tttM%:%tttS%.%tttQ%;%damage%&ping localhost -n 3 >nul&call :gam.score&goto :eof
echo.Uploading Score...
bin\wget --spider "http://%url%/game/score.php?name=%name%&fs=%fs%&score=%score%&bonus=%bonus%&level=%level%&difficulty=%difficulty%&gems=%gems%&ttt=%tttH%:%tttM%:%tttS%.%tttQ%" 2>%log%
title 
:gam.download
if exist "cache\offline.scores" call :upload.missing
::Get scores from server.
echo.Downloading Scores...
if "%connection%"=="1" bin\wget.exe -O data\scores.data http://%url%/game/scores.data 2>nul
title 
::Order scores
echo.y | del cache\scores\* 2>nul >nul
for /f "tokens=1-9 delims=;" %%a in ('type data\scores.data') do (
	set sc=000000000%%b
	set sc_=!sc:~-8!
	>>cache\scores\!sc_! echo.%%a;%%b;%%c;%%d;%%e;%%f;%%g;%%h;%%i
)
:gam.score
set diff_bak=%difficulty%
set difficulty=1
call :gam.format
set difficulty=%diff_bak%
::Display scores
title GaMe - Scores
cls
echo.   HIGH SCORES:
echo.# Name: SCORE [DIFF:LVL][TIME]
echo.%test%
if not "%name%"=="" echo.%name%: %fs% [%difficulty%:%level%][%tttH%:%tttM%:%tttS%.%tttQ%]
if not "%name%"=="" echo.%test%
set count=0
echo.y | del scores 2>nul >nul
for /f %%s in ('dir /b /o:-n cache\scores\*') do (
	::type cache\scores\%%s >>data\scores
	if not "!count!"=="15" (
		set /a count=!count!+1
		for /f "tokens=1-9 delims=;" %%a in ('type cache\scores\%%s') do echo.!count!. %%a: %%b [%%f:%%e][%%h]
	)
)
echo.%test%
call :gam.input
if "%input%"=="3" goto :gam.menu
if "%input%"=="113" goto :gam.menu
if "%input%"=="13" goto :gam.menu
goto :gam.score
:script.music
if not "%1"=="silent" echo.Making Music Script...
( echo Set Sound = CreateObject^("WMPlayer.OCX.7"^)
  echo if WScript.Arguments.Count = 0 then
  echo   WScript.Echo "Missing parameters"
  echo else
  echo   Sound.URL = "cache\" ^& WScript.Arguments^(0^) ^& ".mp3"
  echo   Sound.Controls.play
  echo   do while Sound.currentmedia.duration = 0
  echo   wscript.sleep 100
  echo   loop
  echo   wscript.sleep ^(int^(Sound.currentmedia.duration^)+1^)*1000
  echo end if )>bin\music.vbs
>bin\music.bat echo.@echo off
>>bin\music.bat echo.title GaM - Music
>>bin\music.bat echo.:a
>>bin\music.bat echo.cscript /nologo bin\music.vbs music
>>bin\music.bat echo.goto a
goto :eof
:script.ic
if not "%1"=="silent" echo.Making Input Controller Script...
::Create program: Force the input without keypress.
>bin\inputcontroller.bat echo.title INPUTCONTROLLER
>>bin\inputcontroller.bat echo.:a
>>bin\inputcontroller.bat echo.if exist ".stop" del .stop^&exit
>>bin\inputcontroller.bat echo.if exist ".pause" ping localhost -n 2 ^>nul^&goto a
>>bin\inputcontroller.bat echo.taskkill /F /fi "imagename eq GetInput.exe"
::>>bin\inputcontroller.bat echo.bin\bg.exe sleep %icrate%
>>bin\inputcontroller.bat echo.ping localhost -n 1 -l 1
::Use Difficulty to calculate how much to sleep
for /l %%z in (0,%difficulty%,%speed%) do (
	>>bin\inputcontroller.bat echo.ping localhost -n 1 -l %%z
	if not "%1"=="silent" echo.Delay %%z
)
::>>bin\inputcontroller.bat echo.^>^>.log echo.%%time%%
>>bin\inputcontroller.bat echo.goto :a
goto :eof
:codepage
set /p "=Assigning Symbols... " <NUL
:: Set the console to codepage 65001 (UTF-8).
for /f "tokens=2 delims=:" %%a in ('chcp.com') do set "CONSOLE_CODEPAGE=%%a"
set "CONSOLE_CODEPAGE=%CONSOLE_CODEPAGE: =%"
chcp.com 65001 >nul
set "char_gem=â™¦"
set /p "=%char_gem% " <NUL
set "char_down=â–¼"
set /p "=%char_down% " <NUL
set "char_heart=â™¥"
set /p "=%char_heart% " <NUL
set "char_sun=â˜¼"
set /p "=%char_sun% " <NUL
chcp.com %CONSOLE_CODEPAGE% >nul
:: /\ Restore the previous console codepage.
echo.
goto :eof
:makeBG
goto :eof
Del /f /q /a bg.exe bg.ex_ >nul 2>&1
For %%b In (
"4D534346000000008F080000000000002C000000000000000301010001000000000000"
"00430000000100030FBC160000000000000000924178B6200062672E65786500CCC3D9"
"BC4408BC165B80808D0110C26B00003302563400006F006EBBF6D6B6D75BEF9235D8D6"
"66BD12D938CBACCDAB84FF016A6D993B75ED45495E81BDDBCDB5EEEE77CF6D6B1564B8"
"C6351DA1C50A225A44068C48164BB6F641256448EC830659225108906862E5E61E18F2"
"C71C39AB80B800008DCC80191900CF83AF7BB98FC50BE09B082C4B0613F0408899DDE6"
"281B48B796616EDC2D6FD96A666BC77B6BB49296ED573B9B9649674A532E8A26412520"
"1C3449164812F8111088D89F002000002300404340046DB7ACDB71254204E08C3921C8"
"C7F03FFF07EBFF3E142EDFD0076D1676A2B274DD4180E07E2F4BFFEA056CBE3310FD8F"
"F0955193871FC78BA947203F3CA184724F4922C6994CA33A64F1511F98227EFC869BE2"
"E6A58F8C4E10843030BB100F232E87D320A9E3C0D27D1E1ABA3CB9E42E46DA3F6883B6"
"DAF336F97F676162B283EB8BBB217AEF223F12AE447BCF1102B4EE83AF62415940798C"
"A8AA92DAE38C3E7715F74CFB5608942AD1F544EFA7F5016B8F39BB64355D41C087B4FD"
"D6AF5C923970677990E34CD55E937AFAF452421A8A7592B325C77B605D185742FF4896"
"F741F6B0F1ECD95AAF661200DC9CF424AA09ADD1E672E976B82D1E6B942F516C96AF50"
"CDC0971E37C884EDCDACDB5713B64D3F68F353E31B53F1B100331DA224E6B3AFE956BC"
"3E92EC0CCE6CE4F4ABB2D3756CD395F99E1E8E21BC97DCEFB79D9FEEFB7801619759D7"
"83857A1021DC6FA117E8313B5F014C761AAC7865AFD1F471B920FBCC9B841E9FA15E18"
"5A4B3BDBE897AD4C6BC9AA268A5D26080BE99173FA02C6D7B2284A4FDD2953E0BDB8D6"
"B2B931D785C667B02E3652BB3AF61CCE68881F7A00E18CE0BDA7F306CCA5CE05798F17"
"6637E92ECB8E8DB0DD2B316C9015E5CA9E4F3F5CD59ADBD00BED7C477044C399780978"
"1E2B0391B6AA3C345B7F9F7539A97325D8A0A94B3D8101C772A83CA12E9B44ADA19151"
"AD32D746E53362A119D6A47C6778369300AE0778D28D0FC64B27C606D85FD9C581DD02"
"52ED87943F0DA56DAB3F7EBB191F83F775F143AB0FF15F677EAF1A47A7DE436865FE9F"
"CD156AB385379692EE1EBE33B0B45FDEB3BBD02F67A95FDCDA9CC99EC1CBB888F1BF0C"
"0E9998C48327AF50FC20173C78A8F7AADD6430C578FEE649B8A1038338DC59F70C5E9B"
"6ED8FB863FA0A9EE2E1BC4D5DD5A60CB89A381090DA2F0C97B836EF42F11B279979CD8"
"EED9DA87B4E8FD158CBE80DF1556305F865D6D333EB1A1E9B38F71DCA7D6148866DCE3"
"4A4557B3BE618D2E9E9F04BE575EEF298B104F38C754EE8B4B24AFD11F4EFC4F0B134E"
"C90E2379E306C582B5BCFE7652B86880F8526621F0AEB11AAC4C977C3643666AD05873"
"E538C3EE399819ED27005C41992DD42AD1CCECEE4936592839343760627059B8A23AAB"
"7736CC3C016B0DDBDBC57C8E7DEA8F2C03F5B669CE38E84951810C3F19D32CCF798BEC"
"AF980B6DE783C87B60243FBAA7652577B907BB35CA8A8A5A47BC93BA56D8B7BBD5ECCB"
"EC39BEAF2B05099CB4EC2583B2FBF792D1DFFE2B1BFFB22358C89A1A8DA1AF17AC4BD7"
"9F3587AD9E6FEDBA2F84673B940AC182FD37B0EAAD8676EFDA758CF5E8F3B019B6CB43"
"DF42E56A8693B4078B4942E4004C171EE4AD5C9D42ED5876709C25360BDF5B9BD18C5F"
"D683E71777348E4955EA3F2F2D9C7E3B7B39879DFC607BB0D15801845FC13327B775FA"
"FF1EFFD171C1E480DCE71D1FE285DD41D3AF72FC134373A0C6190B9F71B6BE281AF4F6"
"C0DACADB77B7BE39EC8076172E58BA77656D1B6A3F6E75AA8295F53BF8F006A554CEAD"
"BEE6B7D0BF86B7505D8449B810D772FCCC176F3D06FD342C688EE6B3D22FDA13435C58"
"0E0D6B00EF6677ADE8BBFCFDDEDF5E6F541F42ACE71CF5E6A58EA5D98E6E53928DCDFF"
"807C16CB1EEAE17616E3C69678B9C79F0913F2BF21C9E39CE2525EFA1DAC920CF7FB42"
"5FCB5284E50990D17A002C2E97F025E2B3CFAC2A6C84E971BAA02EE54B7C092CB197D0"
"255209D5C466FB8AA5A2A0ACBE43C493117D28FF957120BF9E9BF4A64DAEF70B3AB6B6"
"61F003383DA4FDFBFF05C343C5595BA7797FC394B49CEEC438DDACECAC5D19085F9AE4"
"5BDBB88E6225ED9F3550FC630A50D4F9B975765A301BCFD9D35074467686742667A6E9"
"8CCDCCDA19F499FA0C2C4638336E675E6176F0B54B6D8AE19CCC8BDFBDA23BB0590F66"
"8DD438B3D361CF3A86160C3273C51FF4C9C59D5C088B8864C3CFD0773B35E1C37B2830"
"FE680D47B000010608A249BC83F02D6E028E96C4FF222A6894502EA0B904E6343E7721"
"62BD59A0EBB668AD0F9A1D667E0057A8B807CF0DFD947A75736BF833A5A03E0F701950"
"FC41F50F991560FB813961B7B3A52583E50C82714891A1400FE05FC2CCFE572A19849C"
"8562114849A4C847AA48C6C89163A3286568932AEAC852BAC612644856C17C5C3A5E55"
"3D1C17AA42FD79A284323DDDA8A75409F52A322635223712E0A6A24975528E91D9D792"
"3CB609854988BF80AAF954F685E9994E744A4584F93B260448C2C6C67BCFD134DBA9A1"
"F82E3695A3D560762ABA7888C6E6F06461505407AAA64ED1AB93F4A4CAA45294789149"
"77D33492D129EDD4782A11A2D6237A4775DC78CE10F1319E4C127A5C965AA4A66B48CA"
"4B75CDEE5D28624E554788796C15C5119B7CACBDDB7E3CB7D6492342771DB362453438"
"D468A7103377641122B672C41B8B3F795121EAE8689316BB0D9DD844C288D564FD799F"
"BA9579A58AC8DB21A9FD46A18889D971144718D0B8EE6F67A1358D7FA0AB18A66579D8"
"05FDBCD822D7735F2F77D6288399332F2F47B06E186D438EC8FFB4ACEDFBBBD45BEBEB"
"DD20EBCFD14806EDB9B02CE17283E887D187E387E40EA83B701F51882A6003057E17C8"
"1C30F8030120017445D020C7242306471E817AA2622C897450D47F8DD0447F23AD8824"
"70BFB4A1647B2A1C20E02BF4292973DBA35BB540DF"
) Do >>bg.exe (Echo For b=1 To len^(%%b^) Step 2
Echo WScript.StdOut.Write Chr^(CByte^("&H"^&Mid^(%%b,b,2^)^)^) : Next)
Cscript /b /e:vbs bg.exe > bg.ex_
Expand -r bg.ex_ >nul
Del bg.ex_ >nul 2>&1
move bg.exe bin\bg.exe >nul
Goto :Eof
:net.check
set /p "=Checking Connection... " <NUL
ping %url% -n 1 >nul
if "%errorlevel%"=="1" set connection=0
if "%errorlevel%"=="0" set connection=1
copy nul sig >nul
if "%connection%"=="0" echo.[408] OFFLINE&goto :eof
if "%connection%"=="1" bin\wget -q http://%url%/game/sig -O sig&title 
for /f %%z in ('type sig') do set sig=%%z
if "%sig%"=="GaMe" set connection=1
if not "%sig%"=="GaMe" set connection=0
if "%sig%"=="" set connection=-1
del sig 2>nul
if "%connection%"=="1" echo.[200] ONLINE
if "%connection%"=="0" echo.[404] NOT FOUND
if "%connection%"=="-1" echo.[400] BAD REQUEST
goto :eof
:ttt
set ttt=0
set tse=%time%
if "%tss:~0,1%"==" " set tss=0%tss:~1%
if "%tse:~0,1%"==" " set tse=0%tse:~1%
set /a tssC=(1%tss:~0,2%-100)*360000 + (1%tss:~3,2%-100)*6000 + (1%tss:~6,2%-100)*100 + (1%tss:~9,2%-100)
set /a tseC=(1%tse:~0,2%-100)*360000 + (1%tse:~3,2%-100)*6000 + (1%tse:~6,2%-100)*100 + (1%tse:~9,2%-100)
set /a ttt=%tseC%-%tssC%-%tptC%
::set /a ttt=%ttt%-%toffset%
if "%tseC%" lss "%tssC%" set /a ttt=%tss%-%tse%
set /A tttH=%ttt% / 360000
set /A tttM=(%ttt% - %tttH%*360000) / 6000
set /A tttS=(%ttt% - %tttH%*360000 - %tttM%*6000) / 100
set /A tttQ=(%ttt% - %tttH%*360000 - %tttM%*6000 - %tttS%*100)
if %tttH% leq 9 set tttH=0%ttth%
if %tttM% leq 9 set tttM=0%tttm%
if %tttS% leq 9 set tttS=0%ttts%
if %tttQ% leq 9 set tttQ=0%tttQ%
::set /a timescore=60000-%ttt%
::if "%timescore:~0,1%"=="-" set timescore=0
goto :eof