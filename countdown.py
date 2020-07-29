#-------------------------------------------------------------------------
# 
# The MIT License (MIT)
#
# Copyright (c) 2020 Liam Kennedy : 7/15/2020
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
# EXTENSIVE RE_WORK IN THIS VERSION (7/15/2020)
# You may have noticed I really wasn't making proper use of this file 
# as a class file you would import in to your own projects.  BAD PROGRAMMER!! 
# 
# This version is now reworked to properly support this as a real class library
# Although you can still run this file from the command line (sudo python countdown.py)
# you will find other examples which import these classes and adjust them as needed
# e.g. mars_small.py, mars_large.py 
#      hope_small.py, hope_larger.py
#
# NEW FEATURES:
#     Keyboard commands (attach a USB keyboard - or my favorite - an MX3 remote
#       You can now adjust the countdown timer on the fly
#       you may ask WHY??
#   
#     In my use case I also stream the live launch video from NASA and others. 
#     They have their own launch clock displayed at times.  
#     Due to ordinary "internet delays" those timers can be out (by 30 seconds or more)
#     Although not "technically" accurate in "REAL TIME" it causes confusion when 
#     running a Zoom watch party if my countdown timer is different than the launch stream
#     So... you can now adjust on the fly
#
#     PRESS:   
#        Cursor RIGHT = add 1 second
#        Cursor LEFT  = subtract 1 second
#        Cursor UP    = add 5 seconds
#        Cursor DOWN  = subtract 5 seconds
#        PGUP         = add 30 seconds
#        PGDN         = subtract 30 seconds  
#        ZERO (0)     = RESET to real time
#        RETURN       = RESET to real time 

import ConfigParser
import pygame
import pygame.gfxdraw
from pygtest import pyscreen
import time
import datetime
import os 

import sys, signal, subprocess 
import json,urllib2

def signal_handler(signal, frame):
  print 'Signal: {}'.format(signal)
  time.sleep(1)
  pygame.quit()
  sys.exit(0) 

# this needs to be initialized up here - even in the class file - otherwise that aspectratio and the scale can't get calculated if the
# class file is executed from the command line.   
# maybe I should pass those FROM the class init call
# This still seems to work OK... so I'll leave it like this for now.  

pys = pyscreen() 
pygame.mouse.set_visible(False)
     
class banner :
      ASPECTRATIO = float( pygame.display.Info().current_w ) / float(pygame.display.Info().current_h)
      SCRIPTPATH = os.path.dirname(os.path.realpath(__file__)) # allows running from boot
      def __init__(self, pygame, pys, filename ) :
          
          self.filename = filename
          self.surface = pygame.Surface(pys.screen.get_size())
          self.image = pygame.image.load( self.SCRIPTPATH+"/"+filename ) # assuming python script / directory is as expected.  May need to check this
          scaleFix = 1.05 
          
          #Scale photo to the screen surface
          photoRect = self.image.get_rect()
          if photoRect[2] / photoRect[3] >= banner.ASPECTRATIO :
             print "Scale Type 1",
             scalePhoto = float( pygame.display.Info().current_w ) / photoRect[2] * 0.9
             
          else :
               print "Scale Type 2", 
               scalePhoto = float( pygame.display.Info().current_h ) / photoRect[3] * 0.9
               
          self.image = pygame.transform.smoothscale( self.image, ( int (photoRect[2] *scalePhoto*scaleFix ), int(photoRect[3]*scalePhoto)) )
          photoRect = self.image.get_rect()
          print "Scaled: ", scalePhoto, "New size: ", photoRect
                   
          topPhotoR = 50 #int((pygame.display.Info().current_h - photoRect[3])/2)
          topPhotoL = int((pygame.display.Info().current_w - photoRect[2])/2)
          photoRect[1]=topPhotoR # topPhoto
          photoRect[0]=topPhotoL # topPhoto
          #photoRect[2]=photoRect[2]+topPhotoR 
          #photoRect[3]=photoRect[3]+topPhotoL
          
          print "Photo Rect: ", photoRect
          self.surface.blit(self.image, (topPhotoL,topPhotoR))
          
class countdown :
      
      SCRIPTPATH = os.path.dirname(os.path.realpath(__file__)) # allows running from boot
      
      # Pygame display needs to be initialized first
      print "SCREEN WIDTH:", pygame.display.Info().current_w
      SCALE = pygame.display.Info().current_w/1920.0 # used to remap the positions to account for display differences to 1920x1080
      #TARGET_NAME = "Docking of the Capsule Endeavour to the ISS - 10:29AM ET MAY 31 2020"
      TARGET_NAME = "Launch of Mars 2020 Perseverance"
      DISPLAY_NAME = False
      TARGET_TIME = datetime.datetime(2020, 7, 30, 11, 50) # Time is in UTC!!!!
      TIMERFONT = [ "dsdigital", 340, True, (255,255,0) ] # fontname, size, bold, color = yellow
      LEGENDFONT = ( "coolvetica", 136, False, (0,255,0) ) # fontname, size, bold, color = green
      NAMEFONT = ( "arial", 40, False, (255,255,0) )
      # These positions represent the top / center position of the days/hrs/mins/sec based upon 1920x1080 screen
      TIMER_LINE = 600
      LEGEND_LINE = 880 
      TIMER_X = [ 420 , 750, 1120, 1490 ] 
      TIMER_Y = [ TIMER_LINE, TIMER_LINE, TIMER_LINE, TIMER_LINE ] 
      
      LEGEND_X = [ 420, 750, 1120, 1490 ] 
      LEGEND_Y = [ LEGEND_LINE, LEGEND_LINE, LEGEND_LINE, LEGEND_LINE ]
      DEBUG = False
      
      def __init__(self, pys, \
                         targettime = TARGET_TIME, \
                         targetname = TARGET_NAME, \
                         timerfont = TIMERFONT, \
                         legendfont = LEGENDFONT, \
                         namefont = NAMEFONT, \
                         timerx = TIMER_X, \
                         timery = TIMER_Y, \
                         legendx = LEGEND_X, \
                         legendy = LEGEND_Y, \
                         displayname = DISPLAY_NAME, \
                         cd_JSON = None ) :
          
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
          
          self.pys = pys # this is the initialized pygame screen surface.              
          self.target_time = targettime
          self.target_time_original = targettime
          self.target_name = targetname 
          self.timer_font = pygame.font.SysFont(timerfont[0], int(timerfont[1]*countdown.SCALE) , bold=timerfont[2])
          self.legend_font = pygame.font.SysFont(legendfont[0], int(legendfont[1]*countdown.SCALE) , bold=legendfont[2])
          self.name_font = pygame.font.SysFont(namefont[0], int(namefont[1]*countdown.SCALE) , bold=namefont[2])          
          self.legend_color = legendfont[3]
          self.timer_color = timerfont[3]
          
          self.name_color = namefont[3]
          self.timer_x = [ int(timerx[0]*countdown.SCALE), int(timerx[1]*countdown.SCALE),int(timerx[2]*countdown.SCALE), int(timerx[3]*countdown.SCALE) ]          
          self.timer_y = [ int(timery[0]*countdown.SCALE), int(timery[1]*countdown.SCALE),int(timery[2]*countdown.SCALE), int(timery[3]*countdown.SCALE) ]  
          self.legend_x = [ int(legendx[0]*countdown.SCALE), int(legendx[1]*countdown.SCALE),int(legendx[2]*countdown.SCALE), int(legendx[3]*countdown.SCALE) ]
          self.legend_y = [ int(legendy[0]*countdown.SCALE), int(legendy[1]*countdown.SCALE),int(legendy[2]*countdown.SCALE), int(legendy[3]*countdown.SCALE) ] 
          # calc position of the countdown NAME text
          # NOTE:  I am probably nuts to tie this to the line position of the legend.  I'll leave this for now though.   
          self.name_x = int( (1920.0 / 2.0) * countdown.SCALE)
          tw,th = self.legend_font.size("SAMPLE")
          self.name_y = int( self.legend_y[0]+th + 1*countdown.SCALE )
          self.displayname = displayname
          self.fullscreenvideo = False
          
          # get the target time from a web source rather than the date/time in the code (allows for target to be adjusted e.g. with a launch delay)
          if cd_JSON :
             self.countdownJSON = cd_JSON
             self.getCountdownTime() 
 
          self.videos = [] # array of videos - files need to be in /videos folder
          
          if self.DEBUG :                  
             print "TIMER_X", self.timer_x
             print "TIMER_Y", self.timer_y
             print "LEGEND_X", self.legend_x
             print "LEGEND_X", self.legend_y
          
      def display(self) :
          
          if self.target_time > datetime.datetime.utcnow() :
             # In regular countdown mode 
             time_until = self.target_time - datetime.datetime.utcnow()
          else  : 
             # After countdown expires - it becomes a COUNT UP... or MET... or Mission Elapsed Time.
             # Might want to have some additional indication of this.  Maybe different color for numbers - or some other flag.       
             time_until = datetime.datetime.utcnow() - self.target_time
              
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
          
          # Display Target Countdown Name
          if self.displayname :
             self.center( self.target_name, self.name_font, self.name_x, self.name_y, self.name_color)
                 
      
      def center(self, text, font, x,y, clr ) :
          if self.DEBUG :   
             print "Center:",text, x,y,clr
          txt = font.render(str(text) , 1, clr )
          tw = txt.get_width()
          topL = x - int(tw/2)
          self.pys.screen.blit(txt, (topL,y) )
          
      def addTime( self, a_secs ) :
          print "Adding", a_secs, "seconds"
          self.target_time = self.target_time + datetime.timedelta( 0, a_secs )
          
      def playVideo( self, id ) :
          playing = False
          try : 
              if self.vproc.poll() == None :
                 print "Video still playing"
                 playing = True  
          except Exception, Err:
                 print "WARNING Video Playing Check Error", repr(Err)
              
          if not playing :
             try :
                 print "Play Video", self.videos[id]
                 if self.fullscreenvideo :
                    cmd = ["omxplayer",countdown.SCRIPTPATH +"/videos/" + self.videos[id] ,"-o","local"]
                 else :
                      cmd = ["omxplayer",countdown.SCRIPTPATH +"/videos/" + self.videos[id] ,"-o","local","--win",'240 0 1680 810']
                      
                 print cmd
                 # preexec_fn=os.setsid - check below - this allows us to kill the process tree called by this Popen.  
                 self.vproc = subprocess.Popen(cmd, shell=False, preexec_fn=os.setsid)
             except Exception, Err: 
                    print "VIDEO ERROR", repr(Err)
                 
      def killVideo( self ) :
          #self.vproc.kill() #####  THIS DOES NOT WORK!!
          # https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
          try :
              os.killpg(os.getpgid(self.vproc.pid), signal.SIGTERM)  # Send the signal to all the process groups
              print "Video killed"
          except Exception, Err:
                 print "Video Kill ERROR", repr(Err)
                          

      def getCountdownTime( self ) :
          print "Checking counddown time at:", self.countdownJSON
          #'http://issabove.pythonanywhere.com/static/'
          
              
          try :
              raw = urllib2.urlopen(self.countdownJSON).read()
              data=json.loads(raw)
              ye= int(data['year'])
              mo= int(data['month'])
              da= int(data['day'])
              hr= int(data['hour'])
              mi= int(data['minute'])
              se= int(data['second'])
              new_name = data['name']
              
              tt = datetime.datetime(ye,mo,da,hr,mi,se)
              
              tt_adjust = self.target_time - self.target_time_original  # have we added (or subtracted) any time from the countdown time (to adjust for streaming lag)
              
              print "Target Time  CURRENT:", self.target_time
              print "            ORIGINAL:", self.target_time_original
              print "          ADJUSTMENT:", tt_adjust
              print "                 NEW:", tt
              print "                NAME:", new_name
              
              self.target_time_original = tt
              self.target_time = tt + tt_adjust
              print "        ADJUSTED NEW:", self.target_time                    
              
              self.target_time_original = tt
              self.target_time = tt + tt_adjust 
              
              self.target_name = new_name 
               
          except Exception, E :
              print "PythonAnywhere Error: " + str(E) 
          
      def checkKey( self ) :
          keyOffCounter = 0
          keyRebootCounter = 0
          keyHealthCounter = 0
          keyVideoCounter = 0
          keyLastPressedTime = datetime.datetime.now()-datetime.timedelta(minutes=1)
          keyLastPressed = None 
          events = pygame.event.get()
          for event in events:
              if self.DEBUG :
                 print "event:", event
              if event.type == pygame.KEYDOWN:
                 elapsedKeyPress = datetime.datetime.now() - keyLastPressedTime
                 if keyOffCounter > 0 and ( event.key != pygame.K_o or elapsedKeyPress.total_seconds() ) > 3 :
                    keyOffCounter = 0
                 if keyRebootCounter > 0 and ( event.key != pygame.K_r or elapsedKeyPress.total_seconds() ) > 3 :
                    keyRebootCounter = 0  
                 if keyHealthCounter > 0 and ( event.key != pygame.K_0 or elapsedKeyPress.total_seconds() ) > 3 :
                    keyHealthCounter = 0  
                 if keyVideoCounter > 0 and ( elapsedKeyPress.total_seconds() ) > 8 :
                    keyVideoCounter = 0 
                    
                 if event.key == pygame.K_o:                            
                    keyOffCounter+=1
                    print "Pressed 'o'", keyOffCounter," times"
                    keyRebootCounter = 0
                    keyHealthCounter = 0
                    if keyOffCounter ==3 :
                       print "Power Off" 
                       #powerOff()
                 elif event.key == pygame.K_r:
                    keyRebootCounter+=1
                    print "Pressed 'r'", keyRebootCounter," times"
                    keyOffCounter = 0
                    keyHealthCounter = 0
                    if keyRebootCounter ==3 :
                       print "REBOOT"
                       #rebootNow()                               
                 elif event.key == pygame.K_PAGEUP:
                    self.addTime( 30 )
                    #streamOn()
                    
                 elif event.key == pygame.K_PAGEDOWN:
                    self.addTime( -30 )
                    #streamOff()
                 
                 elif event.key == pygame.K_h : #was k_0
                    keyHealthCounter+=1
                    print "Pressed '0'", keyHealthCounter," times"
                    keyOffCounter = 0 
                    keyRebootCounter = 0 
                    if keyHealthCounter == 2:
                       print "Show Health" 
                       #showHealth()
                 elif event.key == pygame.K_1:
                     print 'KEY PRESSED: 1'
                     self.playVideo(0)
                     
                 elif event.key == pygame.K_2:
                     print 'KEY PRESSED: 2'
                     self.playVideo(1)
                     
                 elif event.key == pygame.K_3:
                     print 'KEY PRESSED: 3'
                     self.playVideo(2)
                     
                 elif event.key == pygame.K_4:
                     print 'KEY PRESSED: 4'
                     self.playVideo(3)
                     
                 elif event.key == pygame.K_5:
                     print 'KEY PRESSED: 5'
                     self.playVideo(4)
                     
                 elif event.key == pygame.K_6:
                     print 'KEY PRESSED: 6'
                     self.playVideo(5)
                     
                 elif event.key == pygame.K_7:
                     print 'KEY PRESSED: 7'
                     self.playVideo(6)
                     
                 elif event.key == pygame.K_RIGHT:
                    #print ''
                    self.addTime( 1 )
                 
                 elif event.key == pygame.K_LEFT:
                    #print 'KEY PRESSED: LEFT'
                    self.addTime( -1 )
                    
                 elif event.key == pygame.K_UP:
                    #print 'KEY PRESSED: UP'
                    self.addTime( 5 )
                    
                 elif event.key == pygame.K_DOWN:
                    #print 'KEY PRESSED: DOWN'
                    self.addTime( -5 )
                                       
                 elif event.key == pygame.K_RETURN or event.key == pygame.K_0 :
                    print 'RESET target to ', self.target_time_original
                    self.target_time = self.target_time_original
                 
                 elif event.key == pygame.K_F2:
                      self.killVideo()
                      
                 elif event.key == pygame.K_BACKSPACE:
                      print "BACKSPACE: Get Updated Countdown Target" 
                      self.getCountdownTime()       
                  
          
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
       
if __name__ == '__main__':  

   pys = pyscreen() 
   pygame.mouse.set_visible(False)
   
   # makes it possible to kill the process even if it is started at boot in /etc/init.d/* file
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT, signal_handler)

   #pre = "images/launchamerica/"
   pre = "images/mars2020/"
   banners = []
   banners.append( banner( pygame, pys, pre+"M2020-Launch-Red-Circle-Logo-Black-Text-Side-Stacked-white-lrg.png" ) )
   banners.append( banner( pygame, pys, pre+"MARS-2020-BANNER.png" ) )
   banners.append( banner( pygame, pys, pre+"MARS-2020-BANNER-2.png" ) )
   #banners.append( banner( pygame, pys, pre+"la-logo.png" ) )
   #banners.append( banner( pygame, pys, pre+"la_bob_doug.png" ) )
   #banners.append( banner( pygame, pys, pre+"la_banner_za.jpg" ) )
   
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
   
   
   d = datetime.datetime(2020, 7, 30, 11, 50)  # UTC time of launch.  This is the default in the countdown class
   print d 
   print d.year, d.month, d.day, d.hour, d.second
   
   
   # Initialize the countdown object.  This uses the defaults for #LaunchAmerica
   countdown = countdown( pys )
   
   # Now runs loop all the time... and becomes a count UP timer after target reaches
   while True: # datetime.datetime.utcnow() < countdown.target_time :
                          
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
            #print "switching to banner:",banners[current_banner].filename   
            banner_switched = datetime.datetime.utcnow()
   
