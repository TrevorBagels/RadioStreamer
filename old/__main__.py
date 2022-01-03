'''import time, vlc


#url = "https://broadcastify.cdnstream1.com/32048"
url = "https://us4.internet-radio.com/proxy/wsjf?mp=/stream;"

vlc_instance = vlc.Instance("--input-repeat=1", "--fullscreen")

player = vlc_instance.media_player_new()
media = vlc_instance.media_new(url)
player.set_media(media)
player2 = vlc_instance.media_player_new()
media2 = vlc_instance.media_new(url)
player2.set_media(media2)

player.play()
print("..1")
time.sleep(5)
print("..2")
player2.play()
time.sleep(5)'''

from . import main

m = main.Main()