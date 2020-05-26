# raspi-pygame-countdown
Launch Countdown Timer (version configured for SpaceX DM2 #LaunchAmerica)

![Example Countdown](/countdown-example_la.png)Format: ![#LaunchAmerica Countdown]

Super early release of this code.. and.. I'm a bit busy on other launch prep activities to be able to devote a lot of time beyond this release.  I built this entirely for my own use - as part of a [Launch Watch Party for the SpaceX DM2](https://www.spaceforhumanity.org/demo-2-launch-party) mission that I am helping produce.  


I'm running this on my own trusty image with Raspbian Stretch-LITE(!!!).  I run this as a console application - not using any GUI. 

Just clone the repo and give it a try I guess.  Good Luck!!

Dependancies:  Python 2 / Pygame maybe some other stuff too.  Hope it installs easy for you! 

**Fonts**

Run the install-fonts.sh bash script (just copies fonts over to /usr/share/fonts/truetype/)

    sudo chmod +X install-fonts.sh
    sudo ./install-fonts.sh

**I install Pygame like this:**

    sudo apt-get -y install python-pygame

**Run it thus:**

    sudo python countdown.py

Just play around.  

Good luck!!!



