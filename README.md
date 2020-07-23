# MentalMath

This project allows users to create an account and then, at the home screen, they will be able
to find a match. If there is no other player found within 5 seconds, it will match them against a server AI. Otherwise, it is PvP.

The "matches" are a matter of answering simple mental math problems. Users have to answer them for the ai or other user in the game. 

Every user has a profile page, which gives some stats on how they performed.

There is also a leaderboard page that shows all of the users with the user with the highest amount of points at the top and the user with the lowest at the bottom.

## views.py
All of the view functions for rendering pages

## routing.py
Sets up the routes for the sockets to run on

## consumers.py
The consumer objects that get created to act as a socket connection on the server side

## templates/MentalMathWebsite
This folder contains all of the html webpages that get loaded

## static/MentalMathWebsite
This folder contains the css file that gets loaded.

## settings.py
The settings file used by Django, which I had to change to make it work for sockets

## requirements.txt
The python modules I had installed on my computer to gurantee yours runs the same way as mine.


## Technical Details
The match functionality was done using sockets. Everything else was done using Django, bootsrap, and javascript. There was some multithreading used to achieve better performance.

## Justification Of Project
This project should meet the required difficulty condition since it uses most of what was covered in the course along with what I would consider a more advanced topic - sockets. It took a good amount of effort to get the sockets working properly - things like multithreading I had to use to get things to work on top of asyncio. 

The project also looks fairly clean (visually), which I think adds to why it should count.

