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

import ConfigParser
import pygame
import pygame.gfxdraw
from pygtest import pyscreen
import time
import datetime
import os 

print "Current Working Directory", os.getcwd()
print "Script Absolute Path", os.path.dirname(os.path.realpath(__file__))

pys = pyscreen() 
pygame.mouse.set_visible(False)

class banner :
      ASPECTRATIO = float( pygame.display.Info().current_w ) / float(pygame.display.Info().current_h)
      
      def __init__(self, filename ) :
          self.filename = filename
          self.surface = pygame.Surface(pys.screen.get_size())
          self.image = pygame.image.load( filename ) # assuming python script / directory is as expected.  May need to check this
          
          #Scale photo to the screen surface
          photoRect = self.image.get_rect()
          if photoRect[2] / photoRect[3] >= banner.ASPECTRATIO :
             scalePhoto = float( pygame.display.Info().current_w ) / photoRect[2] * 0.9
          else :
               scalePhoto = float( pygame.display.Info().current_h ) / photoRect[3] * 0.9
               
          self.image = pygame.transform.smoothscale( self.image, ( int (photoRect[2] *scalePhoto ), int(photoRect[3]*scalePhoto)) )
          photoRect = self.image.get_rect()
          print "Scaled: ", scalePhoto, "New size: ", photoRect
                   
          topPhotoR = 50 #int((pygame.display.Info().current_h - photoRect[3])/2)
          topPhotoL = int((pygame.display.Info().current_w - photoRect[2])/2)
          photoRect[1]=topPhotoR # topPhoto
          photoRect[0]=topPhotoL # topPhoto
          
          print "Photo Rect: ", photoRect
          self.surface.blit(self.image, photoRect)
          
class countdown :
      
      # Pygame display needs to be initialized first
      print "SCREEN WIDTH:", pygame.display.Info().current_w
      SCALE = pygame.display.Info().current_w/1920.0 # used to remap the positions to account for display differences to 1920x1080
      TARGET_TIME = datetime.datetime(2020, 5, 27, 20, 33) # Time is in UTC!!!!
      TIMERFONT = [ "dsdigital", 340, True, (255,255,0) ] # fontname, size, bold, color = yellow
      LEGENDFONT = ( "coolvetica", 136, False, (0,255,0) ) # fontname, size, bold, color = green
      # These positions represent the top / center position of the days/hrs/mins/sec based upon 1920x1080 screen
      TIMER_LINE = 600
      LEGEND_LINE = 880 
      TIMER_X = [ 420 , 750, 1120, 1490 ] 
      TIMER_Y = [ TIMER_LINE, TIMER_LINE, TIMER_LINE, TIMER_LINE ] 
      
      LEGEND_X = [ 420, 750, 1120, 1490 ] 
      LEGEND_Y = [ LEGEND_LINE, LEGEND_LINE, LEGEND_LINE, LEGEND_LINE ]
      DEBUG = False
      
      def __init__(self, targettime = TARGET_TIME, \
                         timerfont = TIMERFONT, \
                         legendfont = LEGENDFONT, \
                         timerx = TIMER_X, \
                         timery = TIMER_Y, \
                         legendx = LEGEND_X, \
                         legendy = LEGEND_Y ) :
          
          if self.DEBUG :
             print "COUNTDOWN:"
             print " targettime:", targettime
             print " timerfont:", timerfont
             print " legendfont:", legendfont
             print " timerx:", timerx
             print " timery:", timery
             print " legendx:", legendx
             print " legendy:", legendy
             print " SCALE:", self.SCALE, countdown.SCALE
                         
          self.target_time = targettime 
          self.timer_font = pygame.font.SysFont(timerfont[0], int(timerfont[1]*countdown.SCALE) , bold=timerfont[2])
          self.legend_font = pygame.font.SysFont(legendfont[0], int(legendfont[1]*countdown.SCALE) , bold=legendfont[2])          
          self.legend_color = legendfont[3]
          self.timer_color = timerfont[3]
          self.timer_x = [ int(timerx[0]*countdown.SCALE), int(timerx[1]*countdown.SCALE),int(timerx[2]*countdown.SCALE), int(timerx[3]*countdown.SCALE) ]          
          self.timer_y = [ int(timery[0]*countdown.SCALE), int(timery[1]*countdown.SCALE),int(timery[2]*countdown.SCALE), int(timery[3]*countdown.SCALE) ]  
          self.legend_x = [ int(legendx[0]*countdown.SCALE), int(legendx[1]*countdown.SCALE),int(legendx[2]*countdown.SCALE), int(legendx[3]*countdown.SCALE) ]
          self.legend_y = [ int(legendy[0]*countdown.SCALE), int(legendy[1]*countdown.SCALE),int(legendy[2]*countdown.SCALE), int(legendy[3]*countdown.SCALE) ] 
          if self.DEBUG :                  
             print "TIMER_X", self.timer_x
             print "TIMER_Y", self.timer_y
             print "LEGEND_X", self.legend_x
             print "LEGEND_X", self.legend_y
          
      def display(self) :
          
          time_until = self.target_time - datetime.datetime.utcnow()
          tdays = time_until.days
          thrs  = time_until.seconds // 3600 % 3600 # (remainder or hours) 60m x 60s per hour
          tmin  = time_until.seconds // 60 % 60 # (remainder of minutes)
          tsec  = time_until.seconds % 60 #(remainder of seconds)
          text=" %2d  %02d %02d %02d" % (time_until.days,thrs,tmin,tsec)
          #txt = font.render(text , 1, (255,255,0) )
          
          self.center( tdays, self.timer_font, self.timer_x[0], self.timer_y[0], self.timer_color)
          self.center( thrs, self.timer_font, self.timer_x[1], self.timer_y[1], self.timer_color)
          self.center( tmin, self.timer_font, self.timer_x[2], self.timer_y[2], self.timer_color)
          self.center( tsec, self.timer_font, self.timer_x[3], self.timer_y[3], self.timer_color)
          
          if tdays > 1 :
             dtxt = "DAYS" 
          else :
             dtxt = "DAY"
          self.center( dtxt, self.legend_font, self.legend_x[0], self.legend_y[0], self.legend_color)
          
          if thrs > 1 :
             htxt = "HOURS" 
          else :
             htxt = "HOUR"
          self.center( htxt, self.legend_font, self.legend_x[1], self.legend_y[1], self.legend_color)
          
          if tmin > 1 :
             mtxt = "MINUTES" 
          else :
             mtxt = "MINUTE"
          self.center( mtxt, self.legend_font, self.legend_x[2], self.legend_y[2], self.legend_color)
          
          if tsec > 1 :
             stxt = "SECONDS" 
          else :
             stxt = "SECOND"
          self.center( stxt, self.legend_font, self.legend_x[3], self.legend_y[3], self.legend_color)       
      
      def center(self, text, font, x,y, clr ) :
          if self.DEBUG :   
             print "Center:",text, x,y,clr
          txt = font.render(str(text) , 1, clr )
          tw = txt.get_width()
          topL = x - int(tw/2)
          pys.screen.blit(txt, (topL,y) )
          
def loadconfig(op) :
    #not using this yet 
    options = ConfigParser.ConfigParser(allow_no_value=True)
    options.read( "countdown.conf" )
    
    op.banners = options.items('banners')
    op.year = int(options.get('options','year',0))
    op.month = int(options.get('options','month',0))
    op.day = int(options.get('options','day',0))
    op.second = int(options.get('options','second',0))  
    op.banner_switch = int(options.get('options','banner_switch',0)) 
       


banners = []
banners.append( banner( "la-logo.png" ) )
banners.append( banner( "la_bob_doug.png" ) )
#banners.append( banner( "la_banner_za.jpg" ) )

print "banners:", len(banners)

#Display the first banner image 
pys.screen.blit(banners[0].surface,(0,0))
pygame.display.update()
banner_switched = datetime.datetime.utcnow()
banner_interval = 30 # 60 seconds
current_banner = 0
        
if False :
   # just some code that will display all systemfonts.   
   all_fonts = pygame.font.get_fonts()
   print all_fonts
    
   for fontname in all_fonts : 
       print fontname
       font = pygame.font.SysFont(fontname, size , bold=True)
       text = font.render(fontname , 1, (255,255,0) )
       pys.screen.blit(text, (50,line*80) )
       pygame.display.update()
       time.sleep(1)
       line+=1


d = datetime.datetime(2020, 5, 27, 20, 33)  # UTC time of launch.  This is the default in the countdown class 
print d.year, d.month, d.day, d.hour, d.second


# Initialize the countdown object.  This uses the defaults for #LaunchAmerica
countdown = countdown()

while datetime.datetime.utcnow() < countdown.target_time :
                       
      pys.screen.fill((0,0,0))
      pys.screen.blit(banners[current_banner].surface,(0,0))

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

# should probably do something special when countdown finishes.  Just break out as needed.   
while True:     
      time.sleep(1)
