
import re
import pygame
from collections import defaultdict


#----------------------------------

def add(p0, p1):
    return (p0[0] + p1[0], p0[1] + p1[1])
def sub(p0, p1):
    return (p0[0] - p1[0], p0[1] - p1[1])
def mult(p, k):
    return (p[0] * k, p[1] * k)


def split_text_to_cells(text, cell_width = 4):
    "multiline text -> [[cell]]"
    arr = []
    text = text.replace('\r\n', '\n')
    for line in text.strip('\n').split('\n'):
        a = []
        while line:
            cell = line[:cell_width]
            line = line[cell_width:]
            a.append(cell.strip())
        arr.append(a)
    return arr

def split_text_to_cell_map(text, cell_width = 4):
    "multiline text -> { cell => (i,j) }"
    arr = split_text_to_cells(text, cell_width)
    m = {}
    for (i,a) in enumerate(arr):
     for (j,cell) in enumerate(a):
        if cell:
            m[cell] = (i,j)
    return m

#----------------------------------
#  
# [31 30 29 28 27 26 25 24][23 22 21 20 19 18 17 16][15 14 13 12 11 10  9  8][ 7  6  5  4  3  2  1  0]
#        [ color ;   dir  ;        letter          ]             [\  /  |  -]
#        [                                         ]             [   RAYS   ]
#        [            block name bits              ][                 property bits                  ]
#        # used for drawing static objects;
#        # 0 for boxes - BIT_BOX used instead;


BIT_VISIBLE          = 1     #!!! needed?
BIT_SOLID            = 1<<1
BIT_OPAQUE           = 1<<2
BIT_FINISH           = 1<<3  # to mark finish cell (it stays "invisible")
BIT_BOX              = 1<<4
BIT_BOX_BROKEN       = 1<<5
BIT_TELEPORT         = 1<<6
BIT_TELEPORT_SECOND  = 1<<7  # 0|1 - to easy find the second teleport
#BIT_DYNAMIC          = 1<<7  # dynamic object    !!! needed?
BIT_RAY0             = 1<<8  # shift 0..3 for  --  |  /  \
BITS_RAYS            = (BIT_RAY0 << 0) | (BIT_RAY0 << 1) | (BIT_RAY0 << 2) | (BIT_RAY0 << 3)

BITS_WALL       = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
#BITS_FINISH     = BIT_VISIBLE | BIT_NEEDS_BG
#BITS_FINISH     = BIT_VISIBLE
BITS_ICE        = BIT_VISIBLE | BIT_SOLID
BITS_LASER      = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_ICELASER   = BIT_VISIBLE | BIT_SOLID
BITS_BOX        = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_BOX
#BITS_BOX_BROKEN = BIT_VISIBLE |                          BIT_BOX_BROKEN
BITS_TELEPORT   = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_TELEPORT

PROPERTY_BITS_MAP = {    # block name letter => property bits
    "W": BITS_WALL,
    #"F": BITS_FINISH,
    "I": BITS_ICE,
    "L": BITS_LASER,
    "J": BITS_ICELASER,
    "B": BITS_BOX,
    "A": BITS_WALL,         # Arrow (dynamic blocks)
    "T": BITS_TELEPORT,
}

BLOCK_NAME_SHIFT        = 16
BLOCK_NAME_SHIFT_DIR    = 16 + 8
BLOCK_NAME_SHIFT_COLOR  = 16 + 8 + 3
BLOCK_NAME_MASK         = 0x3FFF << BLOCK_NAME_SHIFT  # 3 bits for color, 3 bits for direction, 8 bits for a letter
BLOCK_NAME_MASK2        =  0x7FF << BLOCK_NAME_SHIFT  #                   3 bits for direction, 8 bits for a letter

CELLSIZE = 9  # in pixels

def block_name_to_tuple(name):
    return name[0], int(name[1:] or "0"), 0
def block_tuple_to_bits(letter, direction, color):
    nameBits  = ord(letter) << BLOCK_NAME_SHIFT
    nameBits |=   direction << BLOCK_NAME_SHIFT_DIR
    nameBits |=       color << BLOCK_NAME_SHIFT_COLOR
    return nameBits
def get_bits_dir(bits):
    return (bits >> BLOCK_NAME_SHIFT_DIR) & 0x7
def get_bits_color(bits):
    return (bits >> BLOCK_NAME_SHIFT_COLOR) & 0x7


def create_image_areas(text, cell_width = 4):
    """Result map: block name bits => image area"""
    m = split_text_to_cell_map(text, cell_width)
    areas = {}
    for (name,(i,j)) in m.items():
        nameBits = block_tuple_to_bits(*block_name_to_tuple(name))
        areas[nameBits] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas

# block name bits => area
BLOCK_AREAS = create_image_areas("""
H0  H1  H2  H3                  
H4  H5  H6  H7                  
S   W   F   I               T0  
L0  L2  L1  L3              T1  
L6  L5  L7  L4              T3  
B0  B1                      T2  
A7  A5  A4  A6                  
A2  A0  A1  A3                  
J2  J1  J3  J0                  
J6  J5  J7  J4                  
R1  R0  R2  R3  C1  C2  C3      
""")


LEVELS = [
{   'name': 1, 
    'map': """
W   W   W   W   W   W
W   F               W
W   L0              W
W           B       W
W           H0      W
W   W   W   W   W   W
""" },

{   'name': "temp", 
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W   W
W   F                   i       T12             W
W                                               W
L0          J3                  B               W
W                                               W
W       I                                       L1
W                       j                       W
W   B   B                   B                   W
W                   T02                         W
W           W   H                               W
W                                               W
W               B                               W
W                   T01         T11 B           W
W                                               W
W                                               W
W                                               W
""",
    'dynamics': [
        ("ij", "A7", 500)
    ]
},

{   'name': 2, 
    'map': """
W   W   W   W   W           F
W   W   L0                  W
W   W       W   B           L1
L0                  W       W
W   W       W       W       W
W   W   B   W       W       W
    H0                  B    
W   W   W   W   W           W
""" },

{   'name': 3, 
    'map': """
L7              H                       
            B                           
            W                           
        B               L5              
            B                           
    B                                   
                                        
                            W           
                                    L1  
L4                  F                   
""" },

{   'name': 4,
    'map': """
W   W   W   W   W   W   W   W   W   W   W   W
W   a                                   b   W
W                                           W
W   W                               W   W   W
W   F                               W   H   W
W                                           W
W                                           W
W   W   W   W   W   W   W   W   W   W   W   W
""",
    'dynamics': [
        ("ab", "L3", 500)
    ]
},

{   'name': 5,
    'map': """
W   W   W   W   W   W   W   W   W   W   W
W   F           a                   L1  W
W                           c           W
W   L0                                  W
W                                       W
W   L0                                  W
W                                       W
W                                       W
W   L0          b                   W   W
W                           d       H   W
W   W   W   W   W   W   W   W   W   W   W
""",
    'dynamics': [
        ("ab", "L2", 500),
        ("cd", "L3", 500),
    ]
},

{   'name': 6,
    'map': """
W   W   W   F   W   W
L0      a           W
L0                  W
L0                  W
L0                  W
L0                  W
L0                  W
L0      b           W
L0                  W
W   W   W   W   H   W
""",
    'dynamics': [
        ("ab", "A5/A6", 500),
    ]
},


] # end of LEVELS

LEVEL_TO_START = 5
LEVEL_TO_START = "temp"


DIRECTIONS = [
    ( 1, 0), (-1, 0),   #  >  <     0  1   >>1  0 --
    ( 0,-1), ( 0, 1),   #  ^  v     2  3        1  |
    ( 1,-1), (-1, 1),   #  /` ./    4  5        2  /
    (-1,-1), ( 1, 1),   #  `\  \,   6  7        3  \
]

KEY_DIRECTIONS = {  # key => index of DIRECTIONS
    pygame.K_RIGHT:  0,
    pygame.K_LEFT:   1,
    pygame.K_UP:     2,
    pygame.K_DOWN:   3,
}



class Animation:
    def __init__(self, name, time, proc):
        self.name = name  # used e.g. for stopping an animation by name
        self.time = time  # ticks
        self.proc = proc  # Animation -> void
        self.ended = False  # flag used to delete the animation

class DynamicAnimation(Animation):
    def __init__(self, name, time, proc, nameBits, propertyBits, poses, delay):
        super().__init__(name, time, proc)
        self.nameBits       = nameBits  # for drawing
        self.propertyBits   = propertyBits  # for putting to cells
        self.poses          = poses
        self.posIndex       = -1        # waiting for first frame
        self.delay          = delay     # ticks between frames

class Lazer:
    def __init__(self, direction, staticPos = None, dynamic = None):
        self.direction = direction  # 0..7  index of DIRECTIONS
        self.staticPos = staticPos  # (x,y) or None for dynamic
        self.dynamic   = dynamic    # DynamicAnimation for dynamic or None for static


class BlueBallGame:

    def __init__(self):
        self.windowSurface = pygame.display.get_surface()
        self.blocksSurface = pygame.image.load("blocks.png").convert()  # DOC: convert() to create a copy that will draw more quickly on the screen
        self.blocksSurface.set_colorkey(self.blocksSurface.get_at((0,0)))  # set transparency color from top-left corner

        self.levelIndex = 0  # first by default
        for (i,level) in enumerate(LEVELS):
            if level["name"] == LEVEL_TO_START:
                self.levelIndex = i
        self.reloadLevel = False  # used to trigger level reloading (including animations) out of process_animations call
        self.load_level()
    
    
    def parse_level(self, levelDict):
        cellsText = split_text_to_cells(levelDict['map'])
        w, h = len(cellsText[0]), len(cellsText)
        
        cells = [[None]*w for _ in range(h)]  # [i][j] => (letter, direction, color) or None
        aliases = {}                          # cell alias => (i,j)
        
        for (i,row) in enumerate(cellsText):
         for (j,cellText) in enumerate(row):
            if cellText:
                (letter, direction, color, alias) = re.match(r'^([A-Z]?)([0-9]?)([0-9]?)([a-z]?)$', cellText).groups()
                if letter:
                    cells[i][j] = (letter, int(direction or "0"), int(color or "0"))
                if alias:
                    aliases[alias] = (j,i)
        
        dynamics = []  # [([poses], [[block names]], delay)]
        for (cellAliases, blockNames, delay) in levelDict.get('dynamics', ()):
            dynamics.append((
                tuple(aliases[a] for a in cellAliases),
                [re.findall(r'[A-Z][0-9]?', r) for r in blockNames.split("/")],
                delay
            ))
        
        return ((w, h), cells, dynamics)
    
    def load_level(self):
        if self.levelIndex == len(LEVELS): raise "CONGRATULATIONS!"
    
        (w, h), mapCells, dynamics = self.parse_level(LEVELS[self.levelIndex])
        
        self.levelSize = (w, h)
        self.levelSurface = pygame.surface.Surface((w*CELLSIZE, h*CELLSIZE))  # no scaling up, original pixel size
        self.ticks = pygame.time.get_ticks()  # current time in ms (already needed for starting animations)

        self.finishPos = None
        self.heroPos = None
        self.heroState = 0  # index of skin
        self.boxes = []  # list of positions
        self.lazers = []  # list of Lazer objects
        self.lazersOn = True  # we turn them off when hero reach the finish
        self.teleports = defaultdict(list)  # teleport color => [(x,y), (x,y)] - both teleport poses
        
        self.animations = []  # list of Animation objects
        self.currentFrameDynamics = []  # used to process all current frame dynamic animations at once

        # Fill level cell integers
        self.level = [[0]*w for _ in range(h)]  # cell integer values
        for (i,row) in enumerate(mapCells):
         for (j,blockValues) in enumerate(row):
            if blockValues:
                letter, direction, color = blockValues
                cell = 0
                addNameBits = True
                if letter == "H":           # Hero
                    self.heroPos = (j, i)
                else:
                    if letter == "F":       # Finish: special case - draw by BIT_FINISH
                        self.finishPos = (j, i)
                        cell |= BIT_FINISH
                        addNameBits = False
                    elif letter == "B":     # Box: special case - draw by BIT_BOX
                        self.boxes.append((j, i))
                        cell |= BIT_BOX
                        addNameBits = False
                    elif letter in "LJ":    # Laser or Ice laser
                        lazer = Lazer(direction, (j, i))
                        self.lazers.append(lazer)
                    elif letter == "T":     # Teleport
                        ts = self.teleports[color]
                        if ts: cell |= BIT_TELEPORT_SECOND  # 1 for the second teleport of this color
                        ts.append((j, i))
                    if addNameBits:  # no special bits were set - means regular static object - add block name bits for drawing
                        cell |= block_tuple_to_bits(letter, direction, color)
                    cell |= PROPERTY_BITS_MAP.get(letter, 0)
                self.level[i][j] = cell

        # Start dynamic animations
        for (poses, blocks, delay) in dynamics:
            self.start_dynamic_animation(poses, blocks, delay)
        
        self.recalculateLazerRays = True  # recalculate lazer ray bits
        self.redrawScene = True
        self.canPlay = True  # False on level ending (when just waiting for final animations end)
    
    def start_dynamic_animation(self, keyPoses, blocks, delay):
        poses = []  # collect all poses (from key poses)
        pc = len(keyPoses)
        for i in range(pc):
            (x0,y0), (x1,y1) = keyPoses[i], keyPoses[(i+1)%pc]
            if y0 == y1:  # horizontal
                poses += [(x,y0) for x in range(x0, x1, x0 < x1 and 1 or -1)]
            elif x0 == x1:  # vertical
                poses += [(x0,y) for y in range(y0, y1, y0 < y1 and 1 or -1)]
            else:
                raise "invalid dynamic"
        # Now start dynamic for each block in 2d array
        for (i,row) in enumerate(blocks):
         for (j,blockName) in enumerate(row):
            (letter, direction, color) = block_name_to_tuple(blockName)
            d = self.start_dynamic_block(
                block_tuple_to_bits(letter, direction, color),
                PROPERTY_BITS_MAP[letter],
                [add(p, (j,i)) for p in poses], 
                delay
            )
            if letter in "LJ":
                lazer = Lazer(direction, dynamic = d)
                self.lazers.append(lazer)

    
    def in_level(self, pos):
        x, y = pos
        w, h = self.levelSize
        return 0 <= x < w and 0 <= y < h
    
    def draw_block(self, pos, letter, direction = 0, color = 0):
        nameBits = block_tuple_to_bits(letter, direction, color)
        self.draw_block_by_bits(pos, nameBits)
        
    def draw_block_by_bits(self, pos, nameBits):
        # draw background color if needed
        color = get_bits_color(nameBits)
        if color:
            self.draw_block(pos, "C", direction = color)  # we use direction for color index here
            nameBits = nameBits & BLOCK_NAME_MASK2  # remove color bits
        # draw the block (dir and letter bits only)
        area = BLOCK_AREAS.get(nameBits)
        if area:
            self.levelSurface.blit(
                self.blocksSurface, 
                dest = mult(pos, CELLSIZE), 
                area = area
            )
    
    def redraw_scene(self):
        self.levelSurface.fill('black')
        
        # Layer 1
        for (i,a) in enumerate(self.level):
         for (j,cell) in enumerate(a):
         
            # Draw specials by property bits
            if not cell & BIT_VISIBLE:
                self.draw_block((j,i), "S")     # just space
            if cell & BIT_FINISH:
                self.draw_block((j,i), "F")     # Finish is like a space
            if cell & BIT_BOX_BROKEN:
                self.draw_block((j,i), "B", 1)  # Broken box is like a space

            # Draw by block name (e.g. L1,..)
            nameBits = cell & BLOCK_NAME_MASK
            if nameBits:
                self.draw_block_by_bits((j,i), nameBits)
        
        # hero
        if self.heroState < 8:  #!!! 8 for hidden
            self.draw_block(self.heroPos, "H", self.heroState)
        
        # dynamic objects
        for a in self.animations:
            if a.name == "dyn":
                pos = a.poses[a.posIndex]
                self.draw_block_by_bits(pos, a.nameBits)

        # Layer 2
        for (i,a) in enumerate(self.level):
         for (j,cell) in enumerate(a):
            for ray in range(4):                # Rays
                if cell & (BIT_RAY0 << ray):
                    self.draw_block((j,i), "R", ray)
            if cell & BIT_BOX:                  # Box
                self.draw_block((j,i), "B")
        
        # update window
        w, h = self.levelSize
        w2, h2 = self.windowSurface.get_size()
        k = int(min(w2/w, h2/h))
        self.windowSurface.fill('black')
        self.windowSurface.blit(pygame.transform.scale(self.levelSurface, (w*k, h*k)), (0, 0))
        pygame.display.update()


    def recalculate_lazer_rays(self):
        # Update lazer ray bits (mask: BITS_RAYS)
        w, h = self.levelSize
        for i in range(h):
         for j in range(w):
            self.level[i][j] &= ~BITS_RAYS;
        if self.lazersOn:
            for lazer in self.lazers:
                ray = lazer.direction >> 1  # 0..3: - | / \
                step = DIRECTIONS[lazer.direction]
                pos = lazer.staticPos or lazer.dynamic.poses[lazer.dynamic.posIndex]
                while True:
                    pos = (x,y) = add(pos, step)
                    if not self.in_level(pos): break
                    if self.level[y][x] & BIT_OPAQUE: break
                    self.level[y][x] |= BIT_RAY0 << ray;
    
    # Animations
    def process_animations(self):
        # call proc-s
        for a in self.animations:
            if not a.ended:
                if self.ticks >= a.time:
                    a.proc(a)
        # remove ended
        self.animations = list(filter(
            lambda a: not a.ended,
            self.animations
        ))
    def stop_animation(self, name):
        for a in self.animations:
            if a.name == name:
                a.ended = True
    def add_animation(self, name, delay, proc):
        a = Animation(name, self.ticks + delay, proc)
        self.animations.append(a)

    # pushing a box animation
    def start_pushing_box_animation(self):
        self.heroState = 1  # face for pushing a box
        self.stop_animation("pushingBox")
        self.add_animation("pushingBox", 500, self.proc_pushing_box_animation)
        self.redrawScene = True
    def proc_pushing_box_animation(self, a):
        self.heroState = 0
        self.redrawScene = True
        a.ended = True
    def stop_pushing_box_animation(self):
        self.stop_animation("pushingBox")
    
    # dying animation
    def start_dying_animation(self):
        self.heroState = 2  # begin to die
        self.add_animation("dying", 100, self.proc_dying_animation)
        self.redrawScene = True
    def proc_dying_animation(self, a):
        if self.heroState < 8:
            self.heroState += 1
            self.redrawScene = True
            a.time += 100  # request next frame
        else:
            a.ended = True
            self.start_new_level_animation()  # reload same level

    # starting new level (1 sec pause)
    def start_new_level_animation(self):
        self.add_animation("newLevel", 1000, self.proc_new_level_animation)
    def proc_new_level_animation(self, a):
        self.reloadLevel = True
        a.ended = True

    # dynamics
    def start_dynamic_block(self, nameBits, propertyBits, poses, delay):
        d = DynamicAnimation(
            "dyn", self.ticks, self.proc_dynamic_block, 
            nameBits,
            #propertyBits | BIT_DYNAMIC, 
            propertyBits,
            poses, delay
        )
        self.animations.append(d)
        return d
    def stop_dynamic_blocks(self):
        self.stop_animation("dyn")
    def proc_dynamic_block(self, d):
        self.currentFrameDynamics.append(d)  # we process all current frame dynamics at once
        d.time += d.delay
    def process_current_frame_dynamics(self):
        if not self.currentFrameDynamics: return
        # remove from previous cell
        for d in self.currentFrameDynamics:
            if d.posIndex == -1: continue
            (x,y) = d.poses[d.posIndex]
            self.level[y][x] &= ~d.propertyBits
        # put to next cell
        for d in self.currentFrameDynamics:
            d.posIndex += 1
            d.posIndex %= len(d.poses)
            (x,y) = d.poses[d.posIndex]
            
            # check a box here
            if self.level[y][x] & BIT_BOX:
                self.level[y][x] &= ~BITS_BOX
                self.level[y][x] |=  BIT_BOX_BROKEN  # single bit only
            
            # check the hero is here
            if self.canPlay and self.heroPos == (x,y):
                self.end_playing(False)
            
            self.level[y][x] |= d.propertyBits
            
        #
        self.currentFrameDynamics = []
        self.recalculateLazerRays = True
        self.redrawScene = True

    
    def get_next_cell(self, pos, dirIndex, allowTeleport = True):
        newPos = (x,y) = add(pos, DIRECTIONS[dirIndex])
        if not self.in_level(newPos): return (None,None,None)
        bits = self.level[y][x]
        
        if allowTeleport:
            while bits & BIT_TELEPORT:  # there may be few steps like    -> [0 ]     [ 0][O ]     [ O] ->
                d = get_bits_dir(bits)
                c = get_bits_color(bits)
                if d == dirIndex:  # can enter the teleport
                    i = (bits & BIT_TELEPORT_SECOND) and 1 or 0
                    (xT,yT) = self.teleports[c][i ^ 1]  # pos of other teleport
                    bitsT = self.level[yT][xT]
                    dirIndex = get_bits_dir(bitsT) ^ 1  # step out
                    newPos = (x,y) = add((xT,yT), DIRECTIONS[dirIndex])
                    if not self.in_level(newPos): return (None,None,None)
                    bits = self.level[y][x]
        
        return (newPos, bits, dirIndex)


    def handle_hero_step(self, dirIndex):
        
        newPos, bits, dirIndex = self.get_next_cell(self.heroPos, dirIndex)
        if newPos is None: return
        
        if not bits & BIT_SOLID:
            self.heroPos = newPos
            #self.recalculateLazerRays = True
            self.redrawScene = True
        
        elif bits & BIT_BOX:  # box. can we move it?
            newPos2, bits2, dirIndex2 = self.get_next_cell(newPos, dirIndex)
            if newPos2 is None: return
            
            if not bits2 & BIT_SOLID:  # we can move it
                (x, y ) = newPos
                (x2,y2) = newPos2
                self.level[y ][x ] &= ~BITS_BOX  #!!! remove bits by global mask (not only BOX)
                self.level[y2][x2] |=  BITS_BOX
                self.heroPos = newPos
                self.recalculateLazerRays = True
                self.redrawScene = True
                self.start_pushing_box_animation()
        
    
    def end_playing(self, win):
        if not self.canPlay: return  # already ended
        self.canPlay = False  # player can't play, but wait for some animations end
        #self.stop_dynamic_blocks()
        if win:
            print("=== YOU WIN ===")
            self.lazersOn = False  # turn lazers off (otherwise lazer may reach the winning hero)
            self.recalculateLazerRays = True
            self.redrawScene = True
            #
            self.levelIndex += 1  #!!! use some self.switchLevel instead
            self.stop_pushing_box_animation() # if any
            self.start_new_level_animation()
        else:
            print("=== YOU LOSE ===")
            self.stop_pushing_box_animation() # if any
            self.start_dying_animation()
    
    def run_loop(self):
        
        while True:
            
            if self.reloadLevel:
                self.reloadLevel = False
                self.load_level()
            
            self.ticks = pygame.time.get_ticks()  # in ms

            # handle all events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                # window size?
                elif e.type == pygame.KEYDOWN:
                    if self.canPlay:
                        dirIndex = KEY_DIRECTIONS.get(e.key, -1)  # 0..3
                        if dirIndex != -1:
                            self.handle_hero_step(dirIndex)

            # Process all animations (remove ended ones)
            self.process_animations()  # animation procs called here

            self.process_current_frame_dynamics()

            if self.recalculateLazerRays:
                self.recalculate_lazer_rays()
                self.recalculateLazerRays = False
            
            if self.canPlay:
                x, y = self.heroPos
                if self.level[y][x] & BITS_RAYS:
                    self.end_playing(False)
                elif self.heroPos == self.finishPos:
                    self.end_playing(True)

            if self.redrawScene:
                self.redraw_scene()
                self.redrawScene = False


def test():
    print(image_regions)


def main():
    #test(); return
    
    pygame.init()

    pygame.display.set_mode((800, 600), flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption('Blue Ball')
    
    game = BlueBallGame()
    game.run_loop()
    
    pygame.quit()



main()
