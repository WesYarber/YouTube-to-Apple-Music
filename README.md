# YouTube-to-Apple-Music
This is a simple tool for downloading YouTube video audio, setting metadata, and moving the tracks automatically into your Apple Music library.

<div align="center">
<img src="https://github.com/WesYarber/YouTube-to-Apple-Music/blob/master/example%20images/playlist%20download.png" width="600">
</div>

If you click "Download Video", it will download all video to your current directory, or if you select a different directory, it will download them to that.

Clicking "Download Audio" will, by default, download the audio file into your Apple Music library, but if you select a directory using the folder button,
it will instead just download the file to that directory.

If you paste in a link to a youtube playlist (the link will contain the word "playlist" in it), the script will get each video in the playlist and download them
all in your chosen format. This is great if you have a playlist of music you like to listen to on YouTube and want to save it to your Apple Music library for
offline listening.

This is a pretty simple program, and is my first time playing around with a python based GUI. Please feel free to contribute with forks or pull requests if you
have the ability and desire to contribute! This is a tool I have wanted for a long time but know it has a lot of room for improvement.

If you are on Mac, you should be able to run the YT2AM-MacOS executable. You could also istall the required python libraries and run it as a python script.
For Windows or Linux, you will need to install the python libraries and run it that way. You will then need to figure out how to move the files to Apple Music
on your OS. I have not done this since I have no need for that functionality myself. 

It is also possible that this could work with Spotify, but I haven't looked into that any. If you feel inclined, feel free to add that functionality!
