# JazzGA
A genetic algorithm sequence coded in python and max. The program uses OSC to communicate between the alogrithm(python) and the synthesizer(max). MIT's music21 was used for parsing the xml score into note objects, and the python package simpleOSC was used for basic open sound control setup. 

# Requirements
pyOSC installed
music21 installed
python 2.7 installed

# Directions 
(max side)
1. open max match
2. turn sound on. turn metronome on
3. set mod depth (around 50 is usually good for me)

(python side)
1.	Open terminal
2.	Type: ‘python JazzGA.py’
3.	To stop ‘ctr Z’.
4.	Type ‘ps’ to see the tasks running. You’ll see something that looks like “26110 ttys000    0:36.38 /Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Pyt..”
6.	Find the task number under the column PID, and type “kill #####” (For the above example it would be “kill 26110”)

# Demonstration 
https://www.youtube.com/watch?v=rl7xLumizio
