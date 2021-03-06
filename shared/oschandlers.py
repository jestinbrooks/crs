#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module that handles OSC messages.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""


__appname__ = "oschandlers.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import types

# installed modules
from OSC import OSCServer
#import pyglet

# local modules
from shared import config
from shared import debug

# local Classes

# Constants
OSCPORT = config.oscport
OSCHOST = config.oschost if config.oschost else "localhost"
OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
FREQ_REG_REPORT = config.freq_regular_reports

# init debugging
dbug = debug.Debug()

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is
# set to False
def handle_timeout(self):
    self.timed_out = True

class OSCHandler(object):

    """Set up OSC server and other handlers."""

    def __init__(self, field):
        self.m_field = field
        self.m_server = OSCServer( (OSCHOST, OSCPORT) )
        self.m_server.timeout = OSCTIMEOUT
        self.m_run = True

        self.m_xmin = 0
        self.m_ymin = 0
        self.m_xmax = 0
        self.m_ymax = 0

        self.eventfunc = {
            'ping': self.event_tracking_ping,
            'ack': self.event_tracking_ack,
            'start': self.event_tracking_start,
            'entry': self.event_tracking_entry,
            'exit': self.event_tracking_exit,
            'frame': self.event_tracking_frame,
            'stop': self.event_tracking_stop,
            'minx': self.event_tracking_set,
            'miny': self.event_tracking_set,
            'maxx': self.event_tracking_set,
            'maxy': self.event_tracking_set,
            'npeople': self.event_tracking_set,
            'groupdist': self.event_tracking_set,
            'ungroupdist': self.event_tracking_set,
            'fps': self.event_tracking_set,
            'update': self.event_tracking_update,
            'leg': self.event_tracking_leg,
            'body': self.event_tracking_body,
        }

        # add a method to an instance of the class
        self.m_server.handle_timeout = types.MethodType(handle_timeout, self.m_server)

        for i in self.eventfunc:
            self.m_server.addMsgHandler(OSCPATH[i], self.eventfunc[i])

        # this registers a 'default' handler (for unmatched messages), 
        # an /'error' handler, an '/info' handler.
        # And, if the client supports it, a '/subscribe' &
        # '/unsubscribe' handler
        self.m_server.addDefaultHandlers()
        self.m_server.addMsgHandler("default", self.default_handler)
        # TODO: Handle errors from OSCServer
        #self.m_server.addErrorHandlers()
        #self.m_server.addMsgHandler("error", self.default_handler)
        self.honey_im_home()

    def honey_im_home(self):
        """Broadcast a hello message to the network."""
        # TODO: Broadcast hello message
        return True

    def each_frame(self):
        # clear timed_out flag
        self.m_server.timed_out = False
        # handle all pending requests then return
        while not self.m_server.timed_out:
            self.m_server.handle_request()

    def user_callback(self, path, tags, args, source):
        # which user will be determined by path:
        # we just throw away all slashes and join together what's left
        user = ''.join(path.split("/"))
        # tags will contain 'fff'
        # args is a OSCMessage with data
        # source is where the message came from (in case you need to reply)
        if dbug.LEV & dbug.MSGS: print ("Now do something with", user,args[2],args[0],1-args[1]) 

    def quit_callback(self, path, tags, args, source):
        # don't do this at home (or it'll quit blender)
        self.m_run = False

    # Event handlers

    def default_handler(self, path, tags, args, source):
        if dbug.LEV & dbug.MORE: print "OSC:default_handler:No handler registered for ", path
        return None

    def event_tracking_ping(self, path, tags, args, source):
        if dbug.LEV & dbug.MSGS: print "OSC:event_ping:code",args[0]
        return None

    def event_tracking_ack(self, path, tags, args, source):
        if dbug.LEV & dbug.MSGS: print "OSC:event_ack:code",args[0]
        return None

    def event_tracking_start(self, path, tags, args, source):
        """Tracking system is starting.

        Sent before first /pf/update message for that target
        args:
            [ aparently no params now]
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        #samp = args[0]
        if dbug.LEV & dbug.MSGS: print "OSC:event_start"

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_set:",path,args,source
        if path == OSCPATH['minx']:
            self.m_xmin = int(100*args[0])
            if dbug.LEV & dbug.MSGS: print "OSC:event_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmin_field=(self.m_xmin,self.m_field.m_ymin_field))
        elif path == OSCPATH['miny']:
            self.m_ymin = int(100*args[0])
            if dbug.LEV & dbug.MSGS: print "OSC:event_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmin_field=(self.m_field.m_xmin_field,self.m_ymin))
        elif path == OSCPATH['maxx']:
            self.m_xmax = int(100*args[0])
            if dbug.LEV & dbug.MSGS: print "OSC:event_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmax_field=(self.m_xmax,self.m_field.m_ymax_field))
        elif path == OSCPATH['maxy']:
            self.m_ymax = int(100*args[0])
            if dbug.LEV & dbug.MSGS: print "OSC:event_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmax_field=(self.m_field.m_xmax_field,self.m_ymax))
        elif path == OSCPATH['npeople']:
            self.m_field.check_people_count(args[0])
            return
        elif path == OSCPATH['groupdist']:
            self.m_field.update(groupdist=args[0])
            return
        elif path == OSCPATH['ungroupdist']:
            self.m_field.update(ungroupdist=args[0])
            return
        elif path == OSCPATH['fps']:
            self.m_field.update(oscfps=args[0])
            return
        #if self.m_xmin and self.m_ymin and self.m_xmax and self.m_ymax:
            #print "set_scaling(",(self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            #self.m_field.set_scaling((self.m_xmin,self.m_ymin),(self.m_xmax,self.m_ymax))
            #self.m_field.updateScreen()
            

    def event_tracking_entry(self, path, tags, args, source):
        """Event when person enters field.

        Sent before first /pf/update message for that target
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since
            beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        #print "OSC:event_entry:",path,args,source
        #print "args:",args,args[0],args[1],args[2]
        samp = args[0]
        time = args[1]
        id = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_entry:cell:",id
        self.m_field.create_cell(id)

    def event_tracking_exit(self, path, tags, args, source):
        """Event when person exits field.

        args:
             samp - sample number
             t - time of sample (elapsed time in seconds since beginning of run)
             target - UID of target

        """
        #print "OSC:event_exit:",path,args,source
        samp = args[0]
        time = args[1]
        id = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_exit:cell:",id
        #print "BEFORE: cells:",self.m_field.m_cell_dict
        #print "BEFORE: conx:",self.m_field.m_connector_dict
        self.m_field.del_cell(id)
        #print "AFTER: cells:",self.m_field.m_cell_dict
        #print "AFTER: conx:",self.m_field.m_connector_dict

    def event_tracking_body(self, path, tags, args, source):
        """Information about people's movement within field.

        Update position of target.
        args:
            samp - sample number 
            target - UID of target
            x,y - position of person within field in m
            ex,ey - standard error of measurement (SEM) of position, in meters 
            spd, heading - estimate of speed of person in m/s, heading in degrees
            espd, eheading - SEM of spd, heading
            facing - direction person is facing in degees
            efacing - SEM of facing direction
            diam - estimated mean diameter of legs
            sigmadiam - estimated sigma (sqrt(variance)) of diameter
            sep - estimated mean separation of legs
            sigmasep - estimated sigma (sqrt(variance)) of sep
            leftness - measure of how likely leg 0 is the left leg
            visibility - number of frames since a fix was found for either leg
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = 0
        samp = args[0]
        id = args[1]
        x = int(100*args[2])       # comes in meters, convert to cm
        y = int(100*args[3])
        ex = int(100*args[4])
        ey = int(100*args[5])
        spd = int(100*args[6])
        heading = args[7]
        espd = int(100*args[8])
        eheading = args[9]
        facing = args[10]
        efacing = args[11]
        diam = int(100*args[12])
        sigmadiam = int(100*args[13])
        sep = int(100*args[14])
        sigmasep = int(100*args[15])
        leftness = args[16]
        vis = args[17]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_body:no id",id,"in registered id list"
        if samp%FREQ_REG_REPORT == 0:
            if dbug.LEV & dbug.MSGS: print "    OSC:event_body:id:",id,"pos:",(x,y)
        self.m_field.update_body(id, x, y, ex, ey, spd, espd, facing, efacing, 
                           diam, sigmadiam, sep, sigmasep, leftness, vis)

    def event_tracking_leg(self, path, tags, args, source):
        """Information about individual leg movement within field.

        Update position of leg.
        args:
            samp - sample number 
            id - UID of target
            leg - leg number (0..nlegs-1)
            nlegs - number of legs target is modeled with 
            x,y - position within field in m
            ex,ey - standard error of measurement (SEM) of position, in meters 
            spd, heading - estimate of speed of leg in m/s, heading in degrees
            espd, eheading - SEM of spd, heading
            visibility - number of frames since a positive fix
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = 0
        samp = args[0]
        id = args[1]
        leg = args[2]
        nlegs = args[3]
        x = int(100*args[4])       # comes in meters, convert to cm
        y = int(100*args[5])
        ex = int(100*args[6])
        ey = int(100*args[7])
        spd = int(100*args[8])
        heading = args[9]
        espd = int(100*args[10])
        eheading = args[11]
        vis = args[12]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_leg:no id",id,"in registered id list"
        if samp%FREQ_REG_REPORT == 0:
            if dbug.LEV & dbug.MSGS: print "    OSC:event_leg:id:",id,"leg:",leg,"pos:",(x,y)
        self.m_field.update_leg(id, leg, nlegs, x, y, ex, ey, spd, espd, 
                                   heading, eheading, vis)

    def event_tracking_update(self, path, tags, args, source):
        """Information about people's movement within field.

        Update position of target.
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            x,y - position within field in units - increasing in value towards right and down
            vx,vy - estimate of velocity in m/s
            major,minor - major/minor axis size in m
            groupid - id number of group
            groupsize - number of people in group
            channel - channel number assigned
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = 0
        samp = args[0]
        time = args[1]
        id = args[2]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_update:no id",id,"in registered id list"
        x = int(100*args[3])       # comes in meters, convert to cm
        y = int(100*args[4])
        vx = int(100*args[5])
        vy = int(100*args[6])
        major = int(100*args[7]/2)
        minor = int(100*args[8]/2)
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        #print "OSC:event_update:",path,args,source
        if samp%FREQ_REG_REPORT == 0:
            #print "OSC:event_update:",path,args,source
            if dbug.LEV & dbug.MSGS: print "    OSC:event_update:id:",id,"pos:",(x,y),"axis:",major
        #print "field.update_cell(",id,",",(x,y),",",major,")"
        self.m_field.update_cell(id,(x,y),major)
        #print "OSC:event_update: Done"

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            samp - sample number

        """
        #print "OSC:event_frame:",path,args,source
        samp = args[0]
        if samp%FREQ_REG_REPORT == 0:
            #print "OSC:event_update:",path,args,source
            if dbug.LEV & dbug.MSGS: print "    OSC:event_frame::",samp
        return None

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        if dbug.LEV & dbug.MSGS: print "OSC:event_stop:",path,args,source
        return None

if __name__ == "__main__":
        
    from myfield_class import MyField

    # initialize field
    field = MyField()
    #field.init_screen()

    osc = OSCHandler(field)

    keep_running = True
    while keep_running:

        #for window in pyglet.app.windows:
            #window.switch_to()
            #window.dispatch_events()
            #window.dispatch_event('on_draw')
            #window.flip()

        # do all the things
        #field.on_cycle()
        # call user script
        osc.each_frame()
        keep_running = osc.m_run and field.m_still_running

    osc.m_server.close()
