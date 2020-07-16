#-------------------------------------------------------------------------
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Liam Kennedy
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#-------------------------------------------------------------------------
#
# In case it isn't obvious this is a work in progress - and this represents
# a very early release. 
#
# This code works on my own raspbian image (based on Stretch-Lite) 
# Basic package requirement is pygame - but there are probably others too
# To install the fonts you will need to run install-fonts.sh
# those two fonts come from dafont.com
#  
# Updated for UAE HOPE PROBE MARS countdown

import ConfigParser
import pygame
import pygame.gfxdraw
from pygtest import pyscreen
import time
import datetime
import os 

import sys, signal, subprocess 

def signal_handler(signal, frame):
  print 'Signal: {}'.format(signal)
  time.sleep(1)
  pygame.quit()
  sys.exit(0) 
  
pys = pyscreen() 
pygame.mouse.set_visible(False)

from countdown import countdown, banner

# makes it possible to kill the process even if it is started at boot in /etc/init.d/* file
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

banners = []
banners.append( banner( pygame, pys, "M2020-Launch-Red-Circle-Logo-Black-Text-Side-Stacked-white-lrg.png" ) )

print "banners:", len(banners)

#Display the first banner image 
#pys.screen.blit(banners[0].surface,(0,0))
#pygame.display.update()
banner_switched = datetime.datetime.utcnow()
banner_interval = 10 # 60 seconds
current_banner = 0
        
# Initialize the countdown object.  This uses the defaults for #LaunchAmerica

TARGET_NAME = "Launch of MARS 2020 PERSEVERANCE - 7:50AM ET JUL 30 2020"
print TARGET_NAME
      
TARGET_TIME = datetime.datetime(2020, 7, 30, 11, 50) # Time is in UTC!!!!
#TARGET_TIME = datetime.datetime(2020, 5, 30, 19, 20) # Time is in UTC!!!!
TIMERFONT = [ "dsdigital", 130, True, (255,255,0) ] # fontname, size, bold, color = yellow
LEGENDFONT = ( "coolvetica", 60, False, (0,255,0) ) # fontname, size, bold, color = green
NAMEFONT = ( "arial", 40, False, (255,255,0) )
# These positions represent the top / center position of the days/hrs/mins/sec based upon 1920x1080 screen
TIMER_LINE = 800
LEGEND_LINE = 916 
TIMER_X = [ 420 , 750, 1120, 1490 ] 
TIMER_Y = [ TIMER_LINE, TIMER_LINE, TIMER_LINE, TIMER_LINE ] 

LEGEND_X = [ 420, 750, 1120, 1490 ] 
LEGEND_Y = [ LEGEND_LINE, LEGEND_LINE, LEGEND_LINE, LEGEND_LINE ]
      
countdown = countdown(   pys, \
                         targettime = TARGET_TIME, \
                         targetname = TARGET_NAME, \
                         timerfont = TIMERFONT, \
                         legendfont = LEGENDFONT, \
                         namefont = NAMEFONT, \
                         timerx = TIMER_X, \
                         timery = TIMER_Y, \
                         legendx = LEGEND_X, \
                         legendy = LEGEND_Y, \
                         displayname = True )
                         

while True : #datetime.datetime.utcnow() < countdown.target_time :
                       
      pys.screen.fill((0,0,0))
      pys.screen.blit(banners[current_banner].surface,(0,0))

      countdown.checkKey() # check for any keys pressed on attached USB Keyboard
      
      countdown.display()

      pygame.display.update()
      time.sleep(0.1)
      
      elapsed = datetime.datetime.utcnow() - banner_switched
      
      if elapsed.total_seconds() > banner_interval :
         current_banner +=1 
         if current_banner > len(banners) -1 :
            current_banner = 0
         print "switching to banner:",banners[current_banner].filename   
         banner_switched = datetime.datetime.utcnow()
    
time.sleep(20)
