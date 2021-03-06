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

# local modules
from shared import config
from shared import debug

# local classes
from dataelement_class import Cell,Connector

# constants
LOGFILE = config.logfile
GROUP_DIST = config.group_distance
UNGROUP_DIST = config.ungroup_distance
OSC_FPS = config.osc_framerate
XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field

# init debugging
dbug = debug.Debug()

# TODO: Delete anything here that is specific to visualsys
class Field(object):
    """An object representing the field.  

    Here are the things we store:
        m_still_running: a flag for exiting the main loop
        m_our_cell_count: the running we count of how many cells we have
        m_reported_cell_count: what the tracking system reports
        m_cell_dict: list of cells we have
        m_connector_dict: list of connectors we have
        m_suspect_cells: list of cells we suspect are dead
        m_suspect_conx: list of connectors we suspect are dead

    
    """

    cellClass = Cell
    connectorClass = Connector

    def __init__(self):
        self.m_still_running = True
        self.m_our_cell_count = 0
        self.m_reported_cell_count = 0
        # we could use a list here which would make certain things easier, but
        # we need to do deletions and references pretty regularly.
        # TODO: Consider making these dict into lists
        self.m_cell_dict = {}
        self.m_connector_dict = {}
        # a hash of counts of missing connectors, indexed by id
        self.m_suspect_conxs = {}
        # a hash of counts of missing cells, indexed by id
        self.m_suspect_cells = {}
        #self.allpaths = []
        self.set_scaling((XMIN_FIELD,YMIN_FIELD),(XMAX_FIELD,YMAX_FIELD))
        self.m_xmin_field = XMIN_FIELD
        self.m_ymin_field = YMIN_FIELD
        self.m_xmax_field = XMAX_FIELD
        self.m_ymax_field = YMAX_FIELD
        self.m_groupdist = GROUP_DIST
        self.m_ungroupdist = UNGROUP_DIST
        self.m_oscfps = OSC_FPS

    def update(self, groupdist=None, ungroupdist=None, oscfps=None):
        if groupdist is not None:
            self.m_groupdist = groupdist
        if ungroupdist is not None:
            self.m_ungroupdist = ungroupdist
        if oscfps is not None:
            self.m_oscfps = oscfps

    # Screen Stuff
    #def init_screen(self):
    # moved to subclass

    # Scaling
    def set_scaling(self,pmin_field=None,pmax_field=None):
        """Set up scaling in the field.

        A word about graphics scaling:
         * The vision tracking system (our input data) measures in meters.

         So we will keep eveything internally in centemeters (so we can use ints
         instead of floats), and then convert it to the approriate units before 
         ...but we will probably be changing this to meter floats

         """

        if pmin_field is not None:
            self.m_xmin_field = pmin_field[0]
            self.m_ymin_field = pmin_field[1]
        if pmax_field is not None:
            self.m_xmax_field = pmax_field[0]
            self.m_ymax_field = pmax_field[1]
        if dbug.LEV & dbug.MORE: print "Field dims:", (self.m_xmin_field,
                self.m_ymin_field), (self.m_xmax_field, self.m_ymax_field)

    # Everything
    #def renderAll(self):
    # moved to subclass
    #def drawAll(self):
    # moved to subclass

    # Guides

    #def drawGuides(self):
    # moved to subclass

    def check_for_missing_cell(self, id):
        """Check for missing or suspect cell, handle it.

        Possibilities:
            * Cell does not exist:
                create it, remove from suspect list, update it, increment count
            * Cell exists, but is on the suspect list
                remove from suspect list, increment count
            * Cell exists in master list and is not suspect:
                update its info; count unchanged
        """
        # if cell does not exist:
        if not id in self.m_cell_dict:
            # create it and increment count
            self.create_cell(id)
            # remove from suspect list
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            if dbug.LEV & dbug.FIELD: print "Field:update_cell:Cell",id,\
                        "was lost and has been recreated"
        # if cell exists, but is on suspect list
        elif id in self.m_suspect_cells:
            # remove from suspect list
            del self.m_suspect_cells[id]
            # increment count
            self.m_our_cell_count += 1
            if dbug.LEV & dbug.FIELD: print "Field:update_cell:Cell",id,\
                        "was suspected lost but is now above suspicion"

    # Legs and Body

    def update_body(self, id, x=None, y=None, ex=None, ey=None, 
                 spd=None, espd=None, facing=None, efacing=None, 
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        # first we make sure the cell exists and is not suspect
        self.check_for_missing_cell(id)
        # update body info
        self.m_cell_dict[id].update_body(x, y, ex, ey, spd, espd, facing, efacing, 
                           diam, sigmadiam, sep, sigmasep, leftness, vis)

    def update_leg(self, id, leg, nlegs=None, x=None, y=None, 
                 ex=None, ey=None, spd=None, espd=None, 
                 heading=None, eheading=None, vis=None):
        """ Update leg information.  """ 
        # first we make sure the cell exists and is not suspect
        self.check_for_missing_cell(id)
        # update leg info
        self.m_cell_dict[id].update_leg(leg, nlegs, x, y, ex, ey, spd, espd, 
                                   heading, eheading, vis)

    # Cells

    def create_cell(self, id):
        """Create a cell.  """
        # create cell - note we pass self since we want a back reference to
        # field instance
        # If it already exists, don't create it
        if not id in self.m_cell_dict:
            cell = self.cellClass(self, id)
            # add to the cell list
            self.m_cell_dict[id] = cell
            self.m_our_cell_count += 1
            if dbug.LEV & dbug.FIELD: print "Field:create_cell:count:",self.m_our_cell_count
        # but if it already exists
        else:
            # let's make sure it is no longer suspect
            if id in self.m_suspect_cells:
                if dbug.LEV & dbug.FIELD: print "Field:create_cell:Cell",id,"was suspected lost but is now above suspicion"
                del self.m_suspect_cells[id]

    def update_cell(self, id, p=None, r=None, effects=None, color=None):
        """ Update a cells information."""
        self.check_for_missing_cell(id)
        # update cell's info
        self.m_cell_dict[id].update(p, r, effects, color)

    def is_cell_good_to_go(self, id):
        """Test if cell is good to be rendered.
        Returns True if cell is on master list and not suspect.
        """
        if not id in self.m_cell_dict:
            return False
        if id in self.m_suspect_cells:
            return False
        if self.m_cell_dict[id].m_location is None:
            return False
        return True

    def del_cell(self, id):
        """Delete a cell.
        We used to delete all of it's connections, now we just delete it and
        let the connector sort it out. This allows us to defer connector
        deletion -- instead we keep a cound of suspicious connectors. That way, 
        if the cells reappear, we can reconnect them without losing their
        connectors.
        """
        #cell = self.m_cell_dict[id]
        # delete all cell's connectors from master list of connectors
        #for conxid in cell.m_connector_dict:
        #    if conxid in self.m_connector_dict:
        #        del self.m_connector_dict[conxid]
        # have cell disconnect all of its connections and refs
        # Note: connector checks if cell still exists before rendering
        if id in self.m_cell_dict:
            #cell.cell_disconnect()
            # delete from the cell master list of cells
            if dbug.LEV & dbug.FIELD: print "Field:del_cell:deleting",id
            del self.m_cell_dict[id]
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            else:
                self.m_our_cell_count -= 1
            if dbug.LEV & dbug.FIELD: print "Field:del_cell:count:",self.m_our_cell_count

    def check_people_count(self,reported_count):
        self.m_reported_cell_count = reported_count
        our_count = self.m_our_cell_count
        if dbug.LEV & dbug.FIELD: print "Field:check_people_count:count:",our_count,"- Reported:",self.m_reported_cell_count
        if reported_count != our_count:
            if dbug.LEV & dbug.FIELD: print "Field:check_people_count:Count mismatch"
            self.hide_all_cells()
            self.m_out_cell_count = 0

    def hide_cell(self, id):
        """Hide a cell.
        We don't delete cells unless we have to.
        Instead we add them to a suspect list (actually a count of how
        suspicous they are)
        """
        self.m_suspect_cells[id] = 1
        self.m_our_cell_count -= 1
        if dbug.LEV & dbug.FIELD: print "Field:hide_cell:count:",self.m_our_cell_count

    def hide_all_cells(self):
        if dbug.LEV & dbug.FIELD: print "Field:hide_all_cells"
        for id in self.m_cell_dict:
            self.hide_cell(id)
        self.m_our_cell_count = 0


    #def renderCell(self,cell):
    # moved to subclass
    #def renderAllCells(self):
    # moved to subclass
    #def drawCell(self,cell):
    # moved to subclass
    #def drawAllCells(self):
    # moved to subclass

    # Connectors

    def create_connector(self, id, cell0, cell1):
        # create connector - note we pass self since we want a back reference
        # to field instance
        # NOTE: Connector class takes care of storing the cells as well as
        # telling each of the two cells that they now have a connector
        connector = self.connectorClass(self, id, cell0, cell1)
        # add to the connector list
        self.m_connector_dict[id] = connector

    def del_connector(self,conxid):
        if conxid in self.m_connector_dict:
            # make sure the cells that this connector is attached to, delete
            # refs to it
            self.m_connector_dict[id].conx_disconnect_thyself()
            # delete from the connector list
            del self.m_connector_dict[conxid]

    #def renderConnector(self,connector):
    # moved to subclass
    #def renderAllConnectors(self):
    # moved to subclass
    #def drawConnector(self,connector):
    # moved to subclass
    #def draw_all_connectors(self):
    # moved to subclass

    # Distances - TODO: temporary -- this info will come from the conduction subsys

    def dist_sqd(self,cell0,cell1):
        return ((cell0.m_location[0]-cell1.m_location[0])**2 + 
                (cell0.m_location[1]-cell1.m_location[1])**2)

    def calc_distances(self):
        self.distance = {}
        for id0,c0 in self.m_cell_dict.iteritems():
            for id1,c1 in self.m_cell_dict.iteritems():
                conxid = str(id0)+'.'+str(id1)
                conxid_ = str(id1)+'.'+str(id0)
                if c0 != c1 and not (conxid in self.distance):
                #if c0 != c1 and not (conxid in self.m_cell_dict) and \
                        #not (conxid_ in self.m_cell_dict):
                    dist = self.dist_sqd(c0,c1)
                    #print "Calculating distance",conxid,"dist:",dist
                    self.distance[conxid] = dist
                    self.distance[conxid_] = dist
                    #self.distance[str(c1.m_id)+'.'+str(c0.m_id)] = dist
                    if dist < GROUP_DIST:
                        self.create_connector(conxid,c0,c1)

    # Paths
    # all moved to subclass
    #def make_path_grid(self):
    #def reset_path_grid(self):
    #def path_score_cells(self):
    #def path_find_connectors(self):
    #def find_path(self, connector):
    #def print_grid(self):

    # Scaling conversions
    # all moved to subclass
    #def _convert(self,obj,scale,min1,min2):
    #def scale2out(self,n):
    #def scale2path(self,n):
    #def path2scale(self,n):
    #def _rescale_pts(self,obj,scale,orig_pmin,new_pmin):
    #def rescale_pt2out(self,p):
    #def rescale_num2out(self,n):


