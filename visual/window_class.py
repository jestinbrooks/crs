#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Header template file.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "header.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules
import pyglet
from pyglet.window import key

# local modules
from shared import config

# local classes
from shared import debug

# constants
LOGFILE = config.logfile

DEF_ORIENT = config.default_orient
DEF_BKGDCOLOR = config.default_bkgdcolor

# init debugging
dbug = debug.Debug()

class Window(pyglet.window.Window):

    def __init__(self,field,width,height):
        # initialize pyglet 
        #(xmax_screen,ymax_screen) = self.screenMax()
        #self.m_screen = pyglet.window.Window(width=xmax_screen,height=ymax_screen)
        self.m_field = field
        if dbug.LEV & dbug.PYG: print "Window:init"
        #super(Window, self).__init__(width, height, *args)
        super(Window, self).__init__(width, height,resizable=True,visible=False)

        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        # ... perform some additional initialisation
        pyglet.gl.glClearColor(*DEF_BKGDCOLOR)
        self.clear()

    def resize(self,width,height):
        self.set_size(width, height)
        self.m_field.m_xmax_screen = width
        self.m_field.m_ymax_screen = height

    def on_close(self, width, height):
        self.m_field.m_still_running = False
        if dbug.LEV & dbug.PYG: print "Window:on_close:exiting"
        self.close()
        #super(Window, self).on_close()

    def on_resize(self, width, height):
        self.m_field.set_scaling(pmin_screen=(0,0),pmax_screen=(width,height))
        if dbug.LEV & dbug.PYG: print "Window:on_resize:width=",width,"height=",height
        super(Window, self).on_resize(width, height)

    def on_draw(self):
        #self.calc_distances()
        #self.reset_path_grid()
        #self.path_score_cells()
        #self.path_find_connectors()
        self.clear()
        self.m_field.render_all()
        self.m_field.draw_all()
        #print "draw loop in",(time.clock() - start)*1000,"ms"

    def on_key_press(self, symbol, modifiers):
        MOVEME = 25
        if symbol == pyglet.window.key.SPACE:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:SPACE"
            self.clear()
            self.m_field.render_all()
            return
        elif symbol == pyglet.window.key.LEFT:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:LEFT"
            rx = -MOVEME
            ry = 0
        elif symbol == pyglet.window.key.RIGHT:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:RIGHT"
            rx = MOVEME
            ry = 0
        elif symbol == pyglet.window.key.UP:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:UP"
            rx = 0
            ry = MOVEME
        elif symbol == pyglet.window.key.DOWN:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:DOWN"
            rx = 0
            ry = -MOVEME
        elif symbol == pyglet.window.key.ESCAPE:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:ESCAPE:exiting"
            self.m_field.m_still_running = False
            self.dispatch_event('on_close')
        else:
            if dbug.LEV & dbug.PYG: print "Window:KeyPress:unhandled"
            return
        # move cell

