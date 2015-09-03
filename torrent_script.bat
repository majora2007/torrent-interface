@echo off
title Torrent-Interface's torrent-file script
rem Parameter usage: fromdir tortitle torlbl kind name info_hash
rem corresponds to uTorrents flags: %D %N %L %K %F %I
set "handledlog=logs/handled_torrents.log"
>> "%handledlog%" echo *********************************************
>> "%handledlog%" echo Run on %date% at %time%


set NLM=^


set NL=^^^%NLM%%NLM%^%NLM%%NLM%

set "fromdir=%~1"
set "tortitle=%~2"
set "torlbl=%~3"
set "kind=%~4"
set "name=%~5"
set "hash=%~6"

rem Un-comment the below two lines for debugging input parameters
rem >> "%handledlog%" ECHO The %~nx0 script args are...
rem for %%I IN (%*) DO >> "%handledlog%" ECHO %%I

>> "%handledlog%" echo Handling torrent "%tortitle%"

>> "%handledlog%" echo %NL%Torrent Information: %NL%Directory: "%fromdir%"%NL%Title: "%name%"%NL%Label: "%torlbl%"%NL%Kind: "%kind%"%NL%Name: "%name%"%NL%Hash: "%hash%"%NL%


pythonw.exe torrent_script.py --title "%tortitle%" --label "%torlbl%" --dir "%fromdir%" --kind "%kind%" --name "%name%" --info_hash "%hash"
rem pause
