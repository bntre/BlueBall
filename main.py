"""
Blue Ball
pygame

Control keys:
    Arrows, WASD - move
    End, L - restart the level
    Home, R - restart the game
    Page Down/Up, J/K - switch the level for practice

These sources: https://github.com/bntre/BlueBall
Playable:      https://bntr.itch.io/blueball
"""


import re, random
from   collections import defaultdict
import asyncio
import pygame

from   levels import LEVELS

LEVELS = LEVELS[1:]         # delete temp level
LEVEL_ID_TO_START = 0       # "temp" level for debugging
LEVEL_ID_TO_START = "3.5"   # play custom level
LEVEL_ID_TO_START = "1.1"   # normal start

USE_SOUNDS = True

#-----------------------------------------------------
# Utils

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


#-----------------------------------------------------
# Level cell integer bits
#  
# [31 30 29 28 27 26 25 24][23 22 21 20 19 18 17 16][15 14 13 12 11 10  9  8][ 7  6  5  4  3  2  1  0]
# [  index 2  ;  index 1  ;        letter          ][\  /  |  -]
# [ e.g color ;  e.g. dir ;                        ][   RAYS   ]
# [               block name bits                  ][                 property bits                  ]
#      # used for drawing static objects;
#      # 0 for boxes - BIT_BOX used instead;

#-----------------------------------------------------
# Property bits

BIT_VISIBLE         = 1     #!!! needed?
BIT_SOLID           = 1<<1  # solid for hero, lazers, boxes
BIT_OPAQUE          = 1<<2
BIT_START           = 1<<3  # start or respawn cell (it stays "invisible")
BIT_FINISH          = 1<<4  # to mark finish cell   (it stays "invisible")
BIT_BOX             = 1<<5
BIT_BOX_BROKEN      = 1<<6
BIT_TELEPORT        = 1<<7
BIT_TELEPORT_SECOND = 1<<8  # to easy find the second teleport
BIT_BUTTON          = 1<<9
BIT_DAMAGE          = 1<<10 # a damaging block (e.g. spike)
BIT_DOUBLE_WALL     = 1<<11 # a wall the double can go through  
BIT_RAY0            = 1<<12 # shift 0..3 for  --  |  /  \
BITS_RAYS           = (BIT_RAY0 << 0) | (BIT_RAY0 << 1) | (BIT_RAY0 << 2) | (BIT_RAY0 << 3)

BITS_WALL           = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_GLASS          = BIT_VISIBLE | BIT_SOLID
BITS_LASER          = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_GLASSLASER     = BIT_VISIBLE | BIT_SOLID
BITS_BOX            = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_BOX
BITS_TELEPORT       = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_TELEPORT
BITS_SPIKE          = BIT_VISIBLE                          | BIT_DAMAGE
BITS_DOUBLE_WALL    = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_DOUBLE_WALL

PROPERTY_BITS_MAP = {    # block name letter => property bits
    "W": BITS_WALL,
    "G": BITS_GLASS,
    "L": BITS_LASER,
    "J": BITS_GLASSLASER,
    "B": BITS_BOX,
    "A": BITS_WALL,         # Arrow (dynamic blocks)
    "T": BITS_TELEPORT,
    "S": BITS_SPIKE,
    "V": BITS_DOUBLE_WALL
}

#-----------------------------------------------------
# Name bits

BLOCK_NAME_SHIFT        = 16
BLOCK_NAME_MASK         = 0xFFFF << BLOCK_NAME_SHIFT
BLOCK_NAME_MASK_INDEX1  = 0x0F00 << BLOCK_NAME_SHIFT
BLOCK_NAME_MASK_INDEX2  = 0xF000 << BLOCK_NAME_SHIFT

def block_name_to_tuple(name):
    name += "00"  # add default zeros
    return name[0], int(name[1], 16), int(name[2], 16)
def block_tuple_to_bits(letter, index1, index2):
    nameBits  = ord(letter) <<  BLOCK_NAME_SHIFT
    nameBits |=      index1 << (BLOCK_NAME_SHIFT + 8)
    nameBits |=      index2 << (BLOCK_NAME_SHIFT + 8+4)
    return nameBits
def get_bits_letter(bits):
    return chr((bits >> BLOCK_NAME_SHIFT) & 0xFF)
def get_bits_index1(bits):
    return     (bits >> (BLOCK_NAME_SHIFT + 8)) & 0xF
def get_bits_index2(bits):
    return     (bits >> (BLOCK_NAME_SHIFT + 8+4)) & 0xF
def name_bits_to_tuple(bits):
    return (get_bits_letter(bits), 
            get_bits_index1(bits),
            get_bits_index2(bits))

#-----------------------------------------------------
# Block image map

CELLSIZE = 9  # in pixels

def create_image_areas(text, cell_width = 4):
    """Result map: block name bits => image area (for blitting)"""
    arr = split_text_to_cells(text, cell_width)
    m = {}  # { cell text => (i,j) }
    for (i,a) in enumerate(arr):
     for (j,cell) in enumerate(a):
        if cell:
            m[cell] = (i,j)
    areas = {}  # block name bits => image area
    for (name,(i,j)) in m.items():
        nameBits = block_tuple_to_bits(*block_name_to_tuple(name))
        areas[nameBits] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas

# block name bits => area
BLOCK_AREAS = create_image_areas("""
H0  H1  H2  H3  D0  D1  D2  D3  V       
H4  H5  H6  H7  D4  D5  D6  D7          
-   W   F   G   S30 S31 S33 S15 S14 S13 
L0  L2  L1  L3  S00 S32 S34 S25 S12 S11 
L6  L5  L7  L4  S01 S02 S35 S24 S22 S10 
B0  B1  *   A8  S03 S04 S05 S23 S21 S20 
A7  A5  A4  A6  T0  T1  T3  T2  
A2  A0  A1  A3  C0  C1  C2  C3  
J2  J1  J3  J0  C4  C5  C6  C7  
J6  J5  J7  J4  C8  C9  CA  CB  
R1  R0  R2  R3  P   E0  E1
""")

#-----------------------------------------------------

DIRECTIONS = [
    ( 1, 0), (-1, 0),   #  >  <     0  1   >>1  0 --
    ( 0,-1), ( 0, 1),   #  ^  v     2  3        1  |
    ( 1,-1), (-1, 1),   #  /` ./    4  5        2  /
    (-1,-1), ( 1, 1),   #  `\  \,   6  7        3  \
]

KEY_TO_DIRECTION = {  # key => index of DIRECTIONS
    pygame.K_RIGHT:  0,
    pygame.K_LEFT:   1,
    pygame.K_UP:     2,
    pygame.K_DOWN:   3,
    pygame.K_d:      0,
    pygame.K_a:      1,
    pygame.K_w:      2,
    pygame.K_s:      3,
}

ANY_KEY = tuple(KEY_TO_DIRECTION.keys()) + (  # used e.g. to finish level intro
    pygame.K_PAGEDOWN, pygame.K_PAGEUP, pygame.K_HOME, pygame.K_END,
    pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_KP_ENTER,
    pygame.K_r, pygame.K_j, pygame.K_k, pygame.K_l,
)


#-----------------------------------------------------

class Animation:
    def __init__(self, args):
        self.name       = args.get('name', "")  # used e.g. for stopping an animation by name
        self.time       = args.get('time', -1)  # time to action (to call the proc); -1 for paused
        self.proc       = args['proc']          # Animation -> void
        self.ended      = False                 # flag used to delete the animation
        self.flags      = 0                     # additional flags


ANIMATION_DYNAMIC       = 1
ANIMATION_PERMANENT     = 1 << 1
ANIMATION_BUTTON        = 1 << 2


class DynamicAnimation(Animation):
    def __init__(self, args):
        super().__init__(args)
        self.flags         |= ANIMATION_DYNAMIC
        self.nameBits       = args['nameBits']              # used for drawing
        self.propertyBits   = args['propertyBits']          # put into level cells (for lazer calculation etc)
        self.currentPos     = None                          # current pos, None until set into level cell

class PermanentDynamicAnimation(DynamicAnimation):
    def __init__(self, args):
        super().__init__(args)
        self.flags         |= ANIMATION_PERMANENT
        self.delay          = args['delay']                 # ms between frames
        self.phase          = args['phase']                 # phase of first frame delay
        self.poses          = args['poses']                 # single pos for 'by direction'
        self.direction      = args.get('direction', None)   # None when moving by poses list
        self.posIndex       = 0                             # always 0 for 'by direction'

class ButtonDynamicAnimation(DynamicAnimation):
    def __init__(self, args):
        super().__init__(args)
        self.flags         |= ANIMATION_BUTTON
        self.delay          = args['delay']                 # ms between frames
        self.buttonPos      = args['buttonPos']
        self.poses          = args['poses']                 # single pos for 'by direction'
        self.posIndex       = 0                             #
        self.pushed = False

class Lazer:
    def __init__(self, direction, staticPos = None, dynamic = None):
        self.direction = direction  # 0..7  index of DIRECTIONS
        self.staticPos = staticPos  # (x,y) or None for dynamic
        self.dynamic   = dynamic    # DynamicAnimation for dynamic or None for static



class BlueBallGame:

    def __init__(self):
        self.windowSurface  = pygame.display.get_surface()
        self.blocksSurface  = pygame.image.load("blocks.png").convert()  # DOC: convert() to create a copy that will draw more quickly on the screen
        self.blocksSurface.set_colorkey(self.blocksSurface.get_at((0,0)))  # set transparency color from top-left corner
        self.updateWindow = True
        
        if USE_SOUNDS:
            def load_sound(name):
                s = pygame.mixer.Sound("sound/" + name)
                s.set_volume(0.1)
                return s
            self.soundStart      = load_sound("Pickup_02.ogg")
            self.soundWin        = load_sound("Jingle_Win_00.ogg")
            self.soundDead       = load_sound("Hero_Death_00.ogg")
            self.soundBox        = load_sound("Hit_03.ogg")
            self.soundTeleport   = load_sound("Pickup_03.ogg")
            self.soundButton1    = load_sound("Menu_Navigate_00.ogg")
            self.soundButton0    = load_sound("Menu_Navigate_03.ogg")
            self.soundFireworks  = load_sound("Jingle_Achievement_01.ogg")
        
        self.windowSize     = self.windowSurface.get_size()
        
        # header
        self.update_header_font()
        self.textSurfaces   = [None] * 3
        self.timerCacheTime  = -1  # currently shown times values (to avoid redrawing); see update_timer_text
        self.timerCacheColor = -1  # 0 - normal, 1 - win, 2 - dead, -1 - force update        

        self.currentTime    = pygame.time.get_ticks()  # updated in main loop

        self.practiceMode   = False
        self.fireworks      = False  # set when all levels won - show fireworks on next scene switch
        self.deathCount     = 0
        self.fullPlayTime   = 0  # time spent on all levels; shown on fireworks

        self.triggerSwitchScene = False  # used to trigger scene switching in main loop
        self.reset_scene()
        
        self.levelIndex     = 0  # first by default
        for (i,levelDict) in enumerate(LEVELS):
            if levelDict.get('id') == LEVEL_ID_TO_START:
                self.levelIndex = i
                break
        
        self.levelPhase     = -1  # 0 - intro, 1 - play, 2 - outro, -1 - not a level scene
        self.levelPlayTime  = 0   # set on starting level outro (e.g. diyng for respawn) and on level reset
        self.levelStartTime = -1  # set on ending level intro; used for running the timer
        
        self.resetLevel = True
        self.load_level()

    def update_header_font(self):
        (w, h) = self.windowSize
        self.headerHeight = min(w, h) // 25
        self.headerFont = pygame.font.SysFont('Consolas', self.headerHeight * 10//10)
        
    def update_header_texts(self):
        self.update_level_name_text()
        self.update_timer_text()
        self.update_deaths_text()
    
    def reset_scene(self):
        # reset scene specific stuff
        self.animations             = []    # list of Animation objects
        self.currentFrameDynamics   = []    # used to process all current frame dynamic animations at once        
    
    def parse_level(self, levelDict):
        cellsText = split_text_to_cells(levelDict['map'])
        w, h = len(cellsText[0]), len(cellsText)
        
        cells = [[None]*w for _ in range(h)]  # [i][j] => (letter, index1, index2) or None
        aliasToPos = {}                       # cell alias => (i,j)
        
        cellRe = re.compile(r'^([A-Z\*]?)([0-9A-F]?)([0-9A-F]?)([a-z]?)$')
        for (i,row) in enumerate(cellsText):
         for (j,cellText) in enumerate(row):
            if cellText:
                (letter, index1, index2, alias) = cellRe.match(cellText).groups()
                if letter:
                    cells[i][j] = (letter, int(index1 or "0", 16), int(index2 or "0", 16))
                if alias:
                    aliasToPos[alias] = (j,i)
        
        dynamics = []  # list of ([block poses], optional direction, [[block names]], (stepDelay, optional stepPhase))
        locationsRe = re.compile(r'^([a-z]+)([0-3]?)$')
        for dynConf in levelDict.get('dynamics', ()):
            (locations, blockNames, *delays) = dynConf
            (aliases, direction) = locationsRe.match(locations).groups()
            dynamics.append((
                tuple(aliasToPos[a] for a in aliases),
                int(direction) if direction else None,
                [re.findall(r'[ A-Z][0-9]*', r) for r in blockNames.split("/")],  # 2D list of block names
                delays
            ))
        
        buttons = []  # list of (button pos, [block poses], [[block names]], stepDelay)
        for butConf in levelDict.get('buttons', ()):
            (buttonAlias, aliases, blockNames, stepDelay) = butConf
            buttons.append((
                aliasToPos[buttonAlias],
                tuple(aliasToPos[a] for a in aliases),
                [re.findall(r'[ A-Z][0-9]*', r) for r in blockNames.split("/")],  # 2D list of block names
                stepDelay
            ))
        
        return ((w, h), cells, dynamics, buttons)
    
    def load_level(self):
    
        if self.resetLevel:
            self.resetLevel = False
            self.spawnIndex      = 0
            self.levelPlayTime   = 0
    
        (w, h), mapCells, dynamics, buttons = self.parse_level(LEVELS[self.levelIndex])
        
        self.levelSize      = (w, h)
        self.sceneSurface   = pygame.surface.Surface((w*CELLSIZE, h*CELLSIZE))  # no scaling up, original pixel size
                
        self.spawnPoses     = [None]      # start and respawn poses
        self.finishPos      = None
        self.heroPoses      = [None]      # first one for hero, others for doubles
        self.heroState      = 0           # index of hero skin (0 for normal, others for dying)
        self.boxes          = []          # list of positions
        self.lazers         = []          # list of Lazer objects
        self.lazersOn       = True        # we turn them off when hero reach the finish
        self.teleports      = defaultdict(list)  # teleport color => [(x,y), (x,y)] - both teleport poses
        
        # Fill level cell integers
        self.level = [[0]*w for _ in range(h)]  # cell integer values
        for (i,row) in enumerate(mapCells):
         for (j,blockValues) in enumerate(row):
            if blockValues:
                letter, index1, index2 = blockValues
                cell = 0
                addNameBits = True      # False for cells drawn by property bits
                if letter in "H*":      # Hero start or respawn pos
                    if letter == "H":
                        spawnIndex = 0
                        self.spawnPoses[0] = (j, i)
                    elif letter == "*":
                        spawnIndex = len(self.spawnPoses)
                        self.spawnPoses.append((j, i))
                    if spawnIndex == self.spawnIndex:  # (re)spawn here
                        self.heroPoses[0] = (j, i)
                    cell |= BIT_START
                    addNameBits = False
                elif letter == "D":     # A Double
                    self.heroPoses.append((j, i))
                    addNameBits = False
                elif letter == "F":     # Finish: special case - draw by BIT_FINISH
                    self.finishPos = (j, i)
                    cell |= BIT_FINISH
                    addNameBits = False
                elif letter == "B":     # Box: special case - draw by BIT_BOX
                    self.boxes.append((j, i))
                    cell |= BIT_BOX
                    addNameBits = False
                elif letter in "LJ":    # Laser or Glass laser
                    lazer = Lazer(direction = index1, staticPos = (j, i))
                    self.lazers.append(lazer)
                elif letter == "T":     # Teleport
                    ts = self.teleports[index2]
                    if ts: cell |= BIT_TELEPORT_SECOND  # 1 for the second teleport of this color
                    ts.append((j, i))
                elif letter == "P":     # (Push) Button - draw by BIT_BUTTON
                    cell |= BIT_BUTTON
                    addNameBits = False
                if addNameBits:  # no special bits were set - means regular static object - add block name bits for drawing
                    cell |= block_tuple_to_bits(letter, index1, index2)
                cell |= PROPERTY_BITS_MAP.get(letter, 0)
                self.level[i][j] = cell

        # Some validation
        if not self.heroPoses[0]:   raise Exception("No start pos found")
        if not self.finishPos:      raise Exception("No finish pos found")

        # Start permanent dynamic animations
        for (keyPoses, direction, blocks, delays) in dynamics:
            self.create_permanent_dynamic(keyPoses, direction, blocks, *delays)

        # Create (prepare) button animations
        for (buttonPos, keyPoses, blocks, stepDelay) in buttons:
            self.create_button_dynamic(buttonPos, keyPoses, blocks, stepDelay)

        self.levelUpdated   = True  # recalculate lazer ray bits etc
        self.redrawLevel    = True
        
        self.update_header_texts()
        
        self.levelPhase = 0  # intro
                
        if USE_SOUNDS:
            pygame.mixer.Sound.stop(self.soundStart)
            pygame.mixer.Sound.play(self.soundStart)
        
        
    def create_permanent_dynamic(self, keyPoses, direction, blocks, stepDelay, stepPhase = 0):
        """Start a PermanentDynamicAnimation for each block of this dynamic"""
        keyCount = len(keyPoses)
        if direction is not None:  # moving by direction
            if keyCount != 1: raise "invalid dynamic by direction"
            poses = [keyPoses[0]]
        else:                       # moving by key poses
            if keyCount < 2: raise "invalid dynamic by key positions"
            poses = []  # collect full cycle of poses (from key poses): p0 -> p1 -> p2 -> .. -> p0
            for i in range(keyCount):
                (x0,y0), (x1,y1) = keyPoses[i], keyPoses[(i+1)%keyCount]
                if y0 == y1:  # horizontal
                    poses += [(x,y0) for x in range(x0, x1, x0 < x1 and 1 or -1)]
                elif x0 == x1:  # vertical
                    poses += [(x0,y) for y in range(y0, y1, y0 < y1 and 1 or -1)]
                else:
                    raise "invalid dynamic key positions"
        # Now start a dynamic for each block in 2d array
        posRow = poses[0]  # used for 'by direction' case only
        for (i,row) in enumerate(blocks):
            posCell = posRow
            for (j,blockName) in enumerate(row):
                if blockName != " ":
                    (letter, i1, i2) = block_name_to_tuple(blockName)
                    if direction is not None:
                        blockPoses = [posCell]
                    else:
                        blockPoses = [add(p, (j,i)) for p in poses]
                    dyn = PermanentDynamicAnimation({
                        'time':         -1,  # pause when intro mode
                        'proc':         self.proc_dynamic,
                        'nameBits':     block_tuple_to_bits(letter, i1, i2),
                        'propertyBits': PROPERTY_BITS_MAP[letter],
                        'delay':        stepDelay,
                        'phase':        stepPhase,
                        'poses':        blockPoses,
                        'direction':    direction
                    })
                    self.animations.append(dyn)
                    
                    # Set the block into cell (!!! no moving or damaging allowed here)
                    (x,y) = dyn.currentPos = dyn.poses[0]
                    self.level[y][x] |= dyn.propertyBits
                    
                    # Also create a dynamic lazer
                    if letter in "LJ":  # lazer or glass lazer
                        lazer = Lazer(direction = i1, dynamic = dyn)
                        self.lazers.append(lazer)
                
                posCell, _, _, _ = self.get_next_cell(posCell, 0)  # allow to go through teleports
            posRow, _, _, _ = self.get_next_cell(posRow, 3)  # allow to go through teleports

    def create_button_dynamic(self, buttonPos, keyPoses, blocks, stepDelay):
        poses = []   # collect the path of poses (from key poses): p0 -> p1 -> .. -> pN
        keyCount = len(keyPoses)
        for i in range(keyCount-1):
            (x0,y0), (x1,y1) = keyPoses[i], keyPoses[i+1]
            if y0 == y1:  # horizontal
                poses += [(x,y0) for x in range(x0, x1, x0 < x1 and 1 or -1)]
            elif x0 == x1:  # vertical
                poses += [(x0,y) for y in range(y0, y1, y0 < y1 and 1 or -1)]
            else:
                raise "invalid button dynamic key positions"
        poses += [keyPoses[-1]]
        # Now start a button dynamic for each block in 2d array
        for (i,row) in enumerate(blocks):
            for (j,blockName) in enumerate(row):
                if blockName != " ":
                    (letter, i1, i2) = block_name_to_tuple(blockName)
                    dyn = ButtonDynamicAnimation({
                        'time':         -1,  # paused until button pushed
                        'proc':         self.proc_dynamic,
                        'nameBits':     block_tuple_to_bits(letter, i1, i2),
                        'propertyBits': PROPERTY_BITS_MAP[letter],
                        'delay':        stepDelay,
                        'buttonPos':    buttonPos,
                        'poses':        [add(p, (j,i)) for p in poses]
                    })
                    self.animations.append(dyn)
                    
                    # Set the block into first cell
                    (x,y) = dyn.currentPos = dyn.poses[0]
                    self.level[y][x] |= dyn.propertyBits
                    
                    # Also create a dynamic lazer
                    if letter in "LJ":  # lazer or glass lazer
                        lazer = Lazer(direction = i1, dynamic = dyn)
                        self.lazers.append(lazer)
    
    def in_level(self, pos):
        x, y = pos
        w, h = self.levelSize
        return 0 <= x < w and 0 <= y < h
    
    def draw_block(self, pos, letter, index1 = 0, index2 = 0):
        nameBits = block_tuple_to_bits(letter, index1, index2)
        self.draw_block_by_bits(pos, nameBits)
    def draw_block_by_bits(self, pos, nameBits):
        # draw background color if needed
        letter = get_bits_letter(nameBits)
        if letter in "T":
            color = get_bits_index2(nameBits)          # using index2 as background color
            self.draw_block(pos, "C", index1 = color)  # draw color block by color index
            nameBits &= ~BLOCK_NAME_MASK_INDEX2        # remove color bit
        # draw the block (dir and letter bits only)
        area = BLOCK_AREAS.get(nameBits)
        if area:
            self.sceneSurface.blit(
                self.blocksSurface, 
                dest = mult(pos, CELLSIZE), 
                area = area
            )
    
    def redraw_level(self):
        self.sceneSurface.fill('black')
        
        # Layer 1
        for (i,a) in enumerate(self.level):
         for (j,cell) in enumerate(a):
            # Draw background
            #!!! Always? it needed for Finish, Broken box, Spike,.. Use some BIT_NEED_BG instead of BIT_VISIBLE...
            self.draw_block((j,i), "-")

            # Draw specials by property bits
            if cell & BIT_START:
                self.draw_block((j,i), "*")     # Start is like a space
            if cell & BIT_FINISH:
                self.draw_block((j,i), "F")     # Finish is like a space
            if cell & BIT_BOX_BROKEN:
                self.draw_block((j,i), "B", 1)  # Broken box is like a space
            if cell & BIT_BUTTON:
                self.draw_block((j,i), "P")     # (Push) Button

            # Draw by block name (e.g. L1,..)
            nameBits = cell & BLOCK_NAME_MASK
            if nameBits:
                self.draw_block_by_bits((j,i), nameBits)
        
        # hero
        if self.heroState < 8:  #!!! 8 for hidden
            self.draw_block(self.heroPoses[0], "H", self.heroState)
            for doublePos in self.heroPoses[1:]:
                if doublePos != self.heroPoses[0]:  #!!! annihilation?
                    self.draw_block(doublePos, "D", self.heroState)
        
        # dynamic objects
        for a in self.animations:
            if a.flags & ANIMATION_DYNAMIC:  # DynamicAnimation object (permanent or button)
                self.draw_block_by_bits(a.currentPos, a.nameBits)

        # Layer 2
        for (i,a) in enumerate(self.level):
         for (j,cell) in enumerate(a):
            for ray in range(4):                # Rays
                if cell & (BIT_RAY0 << ray):
                    self.draw_block((j,i), "R", ray)
            if cell & BIT_BOX:                  # Box
                self.draw_block((j,i), "B")
        
    def update_window(self):        
        self.windowSurface.fill('black')
        
        self.blit_header_texts()
        
        w, h = self.sceneSurface.get_size()
        W, H = self.windowSize
        hh   = self.headerHeight
        H -= hh
        #k = min(W // w, H // h)
        k = min(W / w, H / h)  # allow to stretch
        w *= k
        h *= k
        l = (W - w) // 2
        t = (H - h) // 2
        self.windowSurface.blit(pygame.transform.scale(self.sceneSurface, (w, h)), (l, hh + t))
        
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
                pos = lazer.staticPos or lazer.dynamic.currentPos
                while True:
                    pos = (x,y) = add(pos, step)
                    if not self.in_level(pos): break
                    if self.level[y][x] & BIT_OPAQUE: break
                    self.level[y][x] |= BIT_RAY0 << ray;
    
    
    def check_hero_position(self):
        # Hero or double dies
        for (x,y) in self.heroPoses:
            if self.level[y][x] & (BITS_RAYS | BIT_DAMAGE):
                self.end_playing(win = False)

        # Hero reaches the finish
        heroPos = self.heroPoses[0]
        if heroPos == self.finishPos:
            self.end_playing(win = True)

        # Hero reaches a spawn point
        elif heroPos in self.spawnPoses:
            self.spawnIndex = self.spawnPoses.index(heroPos)  # save new pos to respawn
    
    # Animations
    def process_animations(self):
        # call proc-s
        for a in self.animations:
            if not a.ended and a.time != -1:
                if self.currentTime >= a.time:
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
        a = Animation({ 
            'name': name, 
            'time': self.currentTime + delay, 
            'proc': proc
        })
        self.animations.append(a)

    # pushing a box animation
    def start_pushing_box_animation(self):
        self.heroState = 1  # face for pushing a box
        self.stop_animation("pushingBox")
        self.add_animation("pushingBox", 500, self.proc_pushing_box_animation)
        self.redrawLevel = True
    def proc_pushing_box_animation(self, a):
        self.heroState = 0
        self.redrawLevel = True
        a.ended = True
    def stop_pushing_box_animation(self):
        self.stop_animation("pushingBox")
    
    # dying animation
    def start_dying_animation(self):
        self.heroState = 2  # begin to die
        self.add_animation("dying", 100, self.proc_dying_animation)
        self.redrawLevel = True
    def proc_dying_animation(self, a):
        if self.heroState < 8:
            self.heroState += 1
            self.redrawLevel = True
            a.time += 100  # request next frame
        else:
            a.ended = True
            self.start_level_end_animation(delay = 1000)  # reload same level

    # ending level (jusr a pause)  !!! use some lambda for such easy case
    def start_level_end_animation(self, delay):
        self.add_animation("levelEnd", delay, self.proc_level_end_animation)
    def proc_level_end_animation(self, a):
        a.ended = True
        self.triggerSwitchScene = True

    # permanent and button dynamics
    def start_permanent_dynamics(self):
        for d in self.animations:
            if d.flags & ANIMATION_PERMANENT:
                d.time = self.currentTime + d.delay - d.phase  # remove the phase from first frame delay
    
    def update_button_states(self):
        for b in self.animations:
            if b.flags & ANIMATION_BUTTON:
                (x,y) = b.buttonPos
                pushed = (self.level[y][x] & BIT_BOX) or (b.buttonPos in self.heroPoses)
                if b.pushed != pushed:
                    b.pushed = pushed
                    if b.time == -1:  # unpause, request the frame - we will check the moving later
                        b.time = self.currentTime + b.delay
                    if USE_SOUNDS:
                        pygame.mixer.Sound.play(b.pushed and self.soundButton1 or self.soundButton0)
    
    def proc_dynamic(self, dyn):
        self.currentFrameDynamics.append(dyn)  # we process all current frame dynamics at once in process_current_frame_dynamics()
    
    def process_current_frame_dynamics(self):
        if not self.currentFrameDynamics: return
        
        # remove from previous cell
        for d in self.currentFrameDynamics:
            (x,y) = d.currentPos
            if d.flags & ANIMATION_PERMANENT:
                self.level[y][x] &= ~d.propertyBits
            elif d.flags & ANIMATION_BUTTON:
                if d.time == -1: continue
                pause = False
                if d.pushed:
                    pause = d.posIndex == len(d.poses) - 1
                else:
                    pause = d.posIndex == 0
                if pause:
                    d.time = -1
                    continue
                self.level[y][x] &= ~d.propertyBits
        
        # put to next cell
        for d in self.currentFrameDynamics:
            if d.flags & ANIMATION_PERMANENT:
                dirIndex = None
                if d.direction is None:     # move by poses
                    prevPos = d.currentPos
                    d.posIndex += 1
                    d.posIndex %= len(d.poses)
                    d.currentPos = d.poses[d.posIndex]
                    step = sub(d.currentPos, prevPos)
                    dirIndex = DIRECTIONS.index(step)
                else:                       # move by direction
                    d.currentPos, dirIndex, _, _ = self.get_next_cell(d.currentPos, d.direction)
                self.put_dynamic_to_next_cell(d, dirIndex)
                d.time += d.delay  # permanently request next frame
            elif d.flags & ANIMATION_BUTTON:
                if d.time == -1: continue
                prevPos = d.currentPos
                d.posIndex += d.pushed and 1 or -1
                d.currentPos = d.poses[d.posIndex]
                step = sub(d.currentPos, prevPos)
                dirIndex = DIRECTIONS.index(step)
                self.put_dynamic_to_next_cell(d, dirIndex)
                d.time += d.delay  # request also new frame
        
        self.currentFrameDynamics = []
        self.levelUpdated = True
        self.redrawLevel = True
        
    def put_dynamic_to_next_cell(self, dyn, dirIndex):
        """dyn.currentPos is already set"""
        if dyn.propertyBits & BIT_DAMAGE:
            # check a box here
            (x,y) = dyn.currentPos
            if self.level[y][x] & BIT_BOX:
                self.level[y][x] &= ~BITS_BOX        # erase the box
                self.level[y][x] |=  BIT_BOX_BROKEN  # single bit only
            # check the hero is here
            elif self.levelPhase == 1 and (x,y) in self.heroPoses:
                self.end_playing(win = False)
        else:
            # collect items to move (player, boxes,..)
            items = []  # list of tuples (position, [indices]) where index -1 for box or hero indices 0,1.. (annihilated)
            move = False  # move (if space behind) or crash (the first item, if no space)
            p = dyn.currentPos
            d = dirIndex
            while p:
                (x,y) = p
                bits = self.level[y][x]
                if self.levelPhase == 1 and p in self.heroPoses:  # a hero
                    items.append((p, [i for (i,h) in enumerate(self.heroPoses) if h == p]))
                elif bits & BIT_BOX:  # a box
                    items.append((p, [-1]))
                else: # no more heroes nor boxes
                    if items: 
                        # move (if space) or crash (if solid)
                        move = not bits & BIT_SOLID or \
                                   bits & BIT_DOUBLE_WALL and all(i >= 1 for i in items[-1][1])  # allow to move the doubles into the "double wall"
                        if move: items.append((p, []))  # add also the last cell (space) to move to
                    break
                p, d, _, _ = self.get_next_cell(p, d)
            # move (or crash) the items if any
            if items:
                if move:
                    for (c0,c1) in reversed(list(zip(items, items[1:]))):
                        (x0,y0),indices = c0
                        (x1,y1),_       = c1
                        damaged = self.level[y1][x1] & BIT_DAMAGE
                        for i in indices:
                            if i == -1:  # move a box
                                self.level[y0][x0] &= ~BITS_BOX
                                self.level[y1][x1] |= damaged and BIT_BOX_BROKEN or BITS_BOX
                            elif i >= 0:  # move a hero
                                self.heroPoses[i] = (x1,y1)  # damage bit will be checked later
                else:  # no space to move - crash the first item
                    (x,y),indices = items[0]
                    i = indices[0]  # first index is enough to check
                    if i == -1:  # a box
                        self.level[y][x] &= ~BITS_BOX
                        self.level[y][x] |=  BIT_BOX_BROKEN
                    elif i >= 0:
                        if self.levelPhase == 1:
                            self.end_playing(win = False)
        (x,y) = dyn.currentPos
        self.level[y][x] |= dyn.propertyBits


    def get_next_cell(self, pos, dirIndex, allowTeleport = True):
        newPos = (x,y) = add(pos, DIRECTIONS[dirIndex])
        if not self.in_level(newPos): return (None,None,None,False)
        bits = self.level[y][x]
        teleported = False
        
        if allowTeleport:
            while bits & BIT_TELEPORT:  # there may be few steps like    -> [0 ]     [ 0][O ]     [ O] ->
                d = get_bits_index1(bits)  # direction
                c = get_bits_index2(bits)  # color
                if d == dirIndex:  # can enter the teleport
                    i = (bits & BIT_TELEPORT_SECOND) and 1 or 0
                    (xT,yT) = self.teleports[c][i ^ 1]  # pos of other teleport
                    bitsT = self.level[yT][xT]
                    dirIndex = get_bits_index1(bitsT) ^ 1  # step out
                    newPos = (x,y) = add((xT,yT), DIRECTIONS[dirIndex])
                    if not self.in_level(newPos): return (None,None,None,False)
                    bits = self.level[y][x]
                    teleported = True
                else:
                    break  # can't enter - just like a solid block
        
        return (newPos, dirIndex, bits, teleported)


    def handle_hero_step(self, dirIndex_):
        
        for i in range(len(self.heroPoses)):
            dirIndex = dirIndex_
            moved = False
        
            newPos, dirIndex, bits, teleported = self.get_next_cell(self.heroPoses[i], dirIndex)
            if newPos:
                
                if not bits & BIT_SOLID or \
                       bits & BIT_DOUBLE_WALL and i >= 1:  # allow the double to step into the "double wall"
                    self.heroPoses[i] = newPos
                    self.levelUpdated = True  # button may be pushed
                    self.redrawLevel = True
                    moved = True
                    
                    if USE_SOUNDS:
                        if teleported:
                            pygame.mixer.Sound.play(self.soundTeleport)
                
                elif bits & BIT_BOX:  # box. can we move it?
                    newPos2, dirIndex2, bits2, _ = self.get_next_cell(newPos, dirIndex)
                    if newPos2 is None: continue
                    
                    if not bits2 & BIT_SOLID:  # we can move the box
                        #!!! bug: if here is a double that can't move!
                        (x, y ) = newPos
                        (x2,y2) = newPos2
                        self.level[y ][x ] &= ~BITS_BOX
                        self.level[y2][x2] |=  BITS_BOX
                        self.heroPoses[i] = newPos
                        self.levelUpdated = True
                        self.redrawLevel = True
                        self.start_pushing_box_animation()
                        moved = True
                        
                        if USE_SOUNDS:
                            pygame.mixer.Sound.play(self.soundBox)
                            if teleported:
                                pygame.mixer.Sound.play(self.soundTeleport)
            
            if not moved and i == 0:  # forbid moving doubles if hero can't
                return
        
    
    def end_playing(self, win):
        if self.levelPhase == 2: return  # already ended
        self.levelPhase = 2  # player can't play, but wait for some animations end
        self.levelPlayTime = self.currentTime - self.levelStartTime
        if win:
            #print("=== YOU WIN ===")
            self.lazersOn = False  # turn lazers off (otherwise lazer may reach the winning hero)
            self.levelUpdated = True
            self.redrawLevel = True
            #
            self.stop_pushing_box_animation() # if any
            
            self.fullPlayTime += self.levelPlayTime
            
            self.levelIndex += 1
            self.levelIndex %= len(LEVELS)
            self.resetLevel = True
            
            # last level won? - fireworks!
            if self.levelIndex == 0 and not self.practiceMode:
            #if self.levelIndex == 0:
            #if True:
                self.fireworks = True
                self.levelPlayTime = self.fullPlayTime  # full time will be shown as stopped timer
            
            self.start_level_end_animation(delay = 3000)
            
            if USE_SOUNDS:
                pygame.mixer.Sound.play(self.soundWin)
            
        else:
            #print("=== YOU LOSE ===")
            self.stop_pushing_box_animation() # if any
            self.start_dying_animation()
            #
            self.deathCount += 1
            self.update_deaths_text()
            
            if USE_SOUNDS:
                pygame.mixer.Sound.play(self.soundDead)
    
    # header text surfaces
    def update_level_name_text(self):
        if self.fireworks:
            text = "Congratulations!"
        else:
            levelDict = LEVELS[self.levelIndex]
            levelId   = levelDict.get('id', 0)
            levelName = levelDict.get('name', "unnamed")
            text = "%s. %s" % (levelId, levelName)
            if self.practiceMode:
                text += " (practice)"
        self.textSurfaces[0] = self.headerFont.render(text, True, 0x7F7F7Fff)
    def update_deaths_text(self):
        self.textSurfaces[1] = self.headerFont.render("D: %d" % self.deathCount, True, 0x7F7F7Fff)
    def update_timer_text(self):
        run, col = False, 0
        if self.levelPhase == 0:    # intro
            run, col = False, 0     #   0 - gray, 1 - green (win), 2 - red (lose)
        elif self.levelPhase == 1:  # play
            run, col = True, 0      #   gray
        elif self.levelPhase == 2:  # outro
            run, col = False, self.resetLevel and 1 or 2
        elif self.fireworks:        # fireworks
            run, col = False, 1     #   green
        #
        if run:
            time = (self.currentTime - self.levelStartTime) // 100
        else:
            time = self.levelPlayTime // 100
        # 
        if self.timerCacheTime == time and self.timerCacheColor == col:  # nothing changed
            return False
        else:
            self.timerCacheTime  = time
            self.timerCacheColor = col
            timerText = "%d:%02d.%01d" % (time // 600, time // 10 % 60, time % 10)
            self.textSurfaces[2] = self.headerFont.render(timerText, True, (0x7F7F7Fff, 0x7FFF7Fff, 0xFF7F7Fff)[col])
            return True
    def blit_header_texts(self):
        space = self.headerHeight // 8
        shiftLeft  = 0
        shiftRight = 0
        shiftLeft  = self.blit_text(self.windowSurface, self.textSurfaces[0], shiftLeft  + space)  # level name
        shiftRight = self.blit_text(self.windowSurface, self.textSurfaces[2], shiftRight - space)  # timer
        shiftRight = self.blit_text(self.windowSurface, self.textSurfaces[1], shiftRight - space*10)  # deaths
    
    def blit_text(self, destSurface, textSurface, shift):
        destWidth   = destSurface.get_size()[0]
        sourceWidth = textSurface.get_size()[0]
        if shift >= 0:  # left side
            destSurface.blit(textSurface, (shift, 0))
            return shift + sourceWidth
        else:           # right side
            shift -= sourceWidth
            destSurface.blit(textSurface, (destWidth + shift, 0))
            return shift
    
    def start_fireworks_scene(self):
        self.levelPhase = -1
        self.sceneSurface = pygame.surface.Surface((100, 100))  
        self.sceneSurface.fill('black')
        self.update_header_texts()
        self.add_animation("outro", 20, self.proc_fireworks)
        if USE_SOUNDS:
            pygame.mixer.Sound.play(self.soundFireworks, loops = 2)  # play 3 times
    def stop_fireworks_scene(self):
        self.stop_animation("outro")
    def proc_fireworks(self, a):
        a.time += 20
        i = random.randrange(len(BLOCK_AREAS))
        area = tuple(BLOCK_AREAS.values())[i]
        w, h = self.sceneSurface.get_size()
        dest = random.randrange(-CELLSIZE, w), random.randrange(-CELLSIZE, h)
        self.sceneSurface.blit(
            self.blocksSurface, 
            dest = dest, 
            area = area
        )
        self.updateWindow = True
    
    def switch_level(self, firstLevel = False, shiftLevel = 0):
        if firstLevel:
            self.practiceMode = False
            self.fullPlayTime = 0
            self.deathCount = 0
            self.levelIndex = 0
        elif shiftLevel != 0:
            self.practiceMode = True
            self.levelIndex += len(LEVELS) + shiftLevel
            self.levelIndex %= len(LEVELS)
        self.resetLevel = True
        self.triggerSwitchScene = True
    
    def get_click_direction(self, pos):
        cx, cy = pos
        w, h = self.windowSize
        x = cx - w // 2
        y = cy - h // 2
        if abs(x) > abs(y):
            return x < 0 and 1 or 0
        else:
            return y < 0 and 2 or 3
    
    async def run_loop(self):
        
        while True:
            
            self.currentTime = pygame.time.get_ticks()  # in ms
            
            if self.triggerSwitchScene:
                self.triggerSwitchScene = False
                self.reset_scene()
                if self.fireworks:      # final scene: fireworks
                    self.start_fireworks_scene()
                else:                   # level scene
                    self.load_level()
            
            self.updateWindow |= self.update_timer_text()

            # handle all events
            for e in pygame.event.get():
                buttonPushed = False
                dirIndex = -1
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.VIDEORESIZE:
                    self.windowSize = e.size
                    self.update_header_font()
                    self.update_header_texts()
                    self.updateWindow = True
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    buttonPushed = True
                    dirIndex = self.get_click_direction(e.pos)  # => 0..3
                elif e.type == pygame.KEYDOWN:
                    buttonPushed = e.key in ANY_KEY
                    dirIndex = KEY_TO_DIRECTION.get(e.key, -1)  # => 0..3
                    # switching level
                    if buttonPushed:
                        if self.fireworks:  # allow to exit fireworks scene
                            self.fireworks = False
                            self.stop_fireworks_scene()
                            self.switch_level(firstLevel = True)
                        elif e.key in (pygame.K_r, pygame.K_HOME):      # reset game
                            self.switch_level(firstLevel = True)
                        elif e.key in (pygame.K_l, pygame.K_END):       # reset level
                            self.switch_level(shiftLevel = 0)
                        elif e.key in (pygame.K_j, pygame.K_PAGEDOWN):  # next level
                            self.switch_level(shiftLevel = 1)
                        elif e.key in (pygame.K_k, pygame.K_PAGEUP):    # previous level
                            self.switch_level(shiftLevel = -1)
                        if self.triggerSwitchScene:
                            continue  # skip other handling
                if buttonPushed:
                    if self.levelPhase == 0:  # key pressed - end level intro (start animations and timer)
                        self.levelPhase = 1
                        self.levelStartTime = self.currentTime - self.levelPlayTime
                        self.start_permanent_dynamics()
                    if self.levelPhase == 1:
                        if dirIndex != -1:  # Hero step
                            self.handle_hero_step(dirIndex)

            if self.triggerSwitchScene:
                continue  # skip other handling

            if self.levelUpdated:
                self.update_button_states()

            # Process all animations (remove ended ones)
            self.process_animations()  # animation procs called here
            self.process_current_frame_dynamics()

            if self.levelUpdated:
                self.recalculate_lazer_rays()
                #self.update_button_states()  # here update them again: after animations ?
                self.levelUpdated = False
            
            if self.levelPhase == 1:
                self.check_hero_position()

            if self.redrawLevel:
                self.redrawLevel = False
                self.redraw_level()
                self.updateWindow = True
                
            if self.updateWindow:
                self.updateWindow = False
                self.update_window()
            
            await asyncio.sleep(0)


async def main():
    pygame.init()
    
    windowSize = (800, 800)
    pygame.display.set_mode(windowSize, flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption("Blue Ball")

    game = BlueBallGame()
    await game.run_loop()
    
    pygame.quit()


asyncio.run(main())
