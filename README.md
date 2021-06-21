# Synthesia2Midi
 A program that takes a synthesia video and converts the song in it into a midi file.

## Reason for the program
Synthesia videos are a very common way to share piano songs on the internet, especially on YouTube. 

I commonly used these videos to learn how to play songs, since the videos show what notes are being played when and for how long. However, the uploaders of the videos often lock the sheet music behind a paywall. Considering the fact that all the information on how to play the song is available in the video, I knew that it would be possible to write a program to convert the video into sheet music. This program does not do that exactly, however it converts the video into a midi file, which one could then convert into sheet music using popular programs such as MuseScore.

Another reason for this program to get data for machine learning models. Midi files are easier to use as data for machine learning than mp4 files.

## How to use
There are currently two ways to use this program, the "full converter" or the "partial converter". 

The full converter takes in all the parameters that the program will need up front. This requires the user to already know all the parameters. The use-case for this is when the user already knows all the values they want inputted and does not want to be prompted for more while the program is running.

The partial converter takes in as many parameters up front as the user wishes to give, then prompts for more parameters while the program is running if it needs them. It can accomplish anything and everything that the full converter can and is the recommended way to use this program. If needed, it will show frames of the image for the user to know what values they should enter in for parameters.

## The parameters
* video name: the name to give the video, csv, and midi files
* video url: the url of the synthesia video
* tag: used by PyTube to specify which video to download
* first note: the letter name of the first white note on the keyboard (must be capital)
* first white note col: the column/x-coordinate of the center of the first white note
* tenth white note col: the column/x-coordinate of the center of the tenth white note
* read height: the height in the frame at which to read a row to find out what note is being played in that frame (make sure that the read height row is unobstructed)
* left hand color: the RGB values of the left hand notes
* right hand color: the RGB values of the right hand notes
* background color: the RGB values of the background
* minimum note width: the minimum number of pixels wide something must be to be considered a note
* video dir path: the path to a directory in which to store the downloaded YouTube video
* frame dir path: the path to a directory in which to store the frames of the video
* array dir path: the path to a directory in which to save an intermediate representation of the song
* csv dir path: the path to a directory in which to save the csv files that will be converted to midi files
* midi dir path: the path to a directory in which to save the final midi files

## Notes to the user
* All colors must be specified in RGB and as a list, such as `[200, 100, 50].`
* All directories will be created if they do not already exist.
* The converter function must be called in an `if __name__ == "__main__"` block.
* It is highly recommended for the user to run `main.py` from the terminal as some parts of the program do not appear properly if run with the IDE's run button.
