Set Sound = CreateObject("WMPlayer.OCX.7")
if WScript.Arguments.Count = 0 then
  WScript.Echo "Missing parameters"
else
  Sound.URL = "cache\" & WScript.Arguments(0) & ".mp3"
  Sound.Controls.play
  do while Sound.currentmedia.duration = 0
  wscript.sleep 100
  loop
  wscript.sleep (int(Sound.currentmedia.duration)+1)*1000
end if 
