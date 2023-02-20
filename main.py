
import re
import pygame
from collections import defaultdict

from levels import LEVELS

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
# [  index 2  ;  index 1  ;        letter          ][\  /  |  -]
# [ e.g color ;  e.g. dir ;                        ][   RAYS   ]
# [               block name bits                  ][                 property bits                  ]
#      # used for drawing static objects;
#      # 0 for boxes - BIT_BOX used instead;


BIT_VISIBLE          = 1     #!!! needed?
BIT_SOLID            = 1<<1
BIT_OPAQUE           = 1<<2
BIT_START            = 1<<3  # start or respawn cell (it stays "invisible")
BIT_FINISH           = 1<<4  # to mark finish cell   (it stays "invisible")
BIT_BOX              = 1<<5
BIT_BOX_BROKEN       = 1<<6
BIT_TELEPORT         = 1<<7
BIT_TELEPORT_SECOND  = 1<<8  # to easy find the second teleport
BIT_DAMAGE           = 1<<9  # a damaging block (e.g. spike)
BIT_RAY0             = 1<<12 # shift 0..3 for  --  |  /  \
BITS_RAYS            = (BIT_RAY0 << 0) | (BIT_RAY0 << 1) | (BIT_RAY0 << 2) | (BIT_RAY0 << 3)

BITS_WALL       = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_GLASS      = BIT_VISIBLE | BIT_SOLID
BITS_LASER      = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_GLASSLASER = BIT_VISIBLE | BIT_SOLID
BITS_BOX        = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_BOX
BITS_TELEPORT   = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_TELEPORT
BITS_SPIKE      = BIT_VISIBLE                          | BIT_DAMAGE

PROPERTY_BITS_MAP = {    # block name letter => property bits
    "W": BITS_WALL,
    "G": BITS_GLASS,
    "L": BITS_LASER,
    "J": BITS_GLASSLASER,
    "B": BITS_BOX,
    "A": BITS_WALL,         # Arrow (dynamic blocks)
    "T": BITS_TELEPORT,
    "S": BITS_SPIKE,
}

BLOCK_NAME_SHIFT        = 16
BLOCK_NAME_MASK         = 0xFFFF << BLOCK_NAME_SHIFT
BLOCK_NAME_MASK_INDEX1  = 0x0F00 << BLOCK_NAME_SHIFT
BLOCK_NAME_MASK_INDEX2  = 0xF000 << BLOCK_NAME_SHIFT

def block_name_to_tuple(name):
    name += "00"
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


CELLSIZE = 9  # in pixels

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
H0  H1  H2  H3  D0  D1  D2  D3          
H4  H5  H6  H7  D4  D5  D6  D7          
-   W   F   G   S30 S31 S33 S15 S14 S13 
L0  L2  L1  L3  S00 S32 S34 S25 S12 S11 
L6  L5  L7  L4  S01 S02 S35 S24 S22 S10 
B0  B1  *       S03 S04 S05 S23 S21 S20 
A7  A5  A4  A6  T0  T1  T3  T2  
A2  A0  A1  A3  C0  C1  C2  C3  
J2  J1  J3  J0  C4  C5  C6  C7  
J6  J5  J7  J4  C8  C9  CA  CB  
R1  R0  R2  R3                  
""")

LEVEL_TO_START = "temp"
LEVEL_TO_START = 1

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
        self.time = time  # time to action
        self.proc = proc  # Animation -> void
        self.ended = False  # flag used to delete the animation

class DynamicAnimation(Animation):
    def __init__(self, name, time, proc, nameBits, propertyBits, delay, poses, direction = None):
        super().__init__(name, time, proc)
        self.nameBits       = nameBits      # used for drawing
        self.propertyBits   = propertyBits  # put into level cells (for lazer calculation etc)
        self.delay          = delay         # ms between frames
        self.currentPos     = None          # current pos, None before first frame
        #
        self.poses          = poses         # single pos for 'by direction'
        self.posIndex       = -1            # -1 for 'by direction' or when not started
        self.direction      = direction     # None when moving by poses list

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
        
        self.windowSize = self.windowSurface.get_size()
        self.handle_window_resize()

        self.levelIndex = 0  # first by default
        for (i,level) in enumerate(LEVELS):
            if level["name"] == LEVEL_TO_START:
                self.levelIndex = i
        
        self.deathCount = 0
        
        self.startIndex = 0  # index of start position to respawn
        self.switchLevel = False  # switching to next level (resetting self.startIndex)
        self.reloadLevel = False  # used to trigger level reloading (including animations) out of process_animations call
        self.load_level()
    
    def handle_window_resize(self):
        (w, h) = self.windowSize
        # header
        self.headerHeight = min(w, h) // 25
        self.headerFont = pygame.font.SysFont('Consolas', self.headerHeight * 10//10)
        
    
    def parse_level(self, levelDict):
        cellsText = split_text_to_cells(levelDict['map'])
        w, h = len(cellsText[0]), len(cellsText)
        
        cells = [[None]*w for _ in range(h)]  # [i][j] => (letter, index1, index2) or None
        aliases = {}                          # cell alias => (i,j)
        
        cellRe = re.compile(r'^([A-Z\*]?)([0-9A-F]?)([0-9A-F]?)([a-z]?)$')
        for (i,row) in enumerate(cellsText):
         for (j,cellText) in enumerate(row):
            if cellText:
                (letter, index1, index2, alias) = cellRe.match(cellText).groups()
                if letter:
                    cells[i][j] = (letter, int(index1 or "0", 16), int(index2 or "0", 16))
                if alias:
                    aliases[alias] = (j,i)
        
        dynamics = []  # [([poses], direction, [[block names]], (stepDelay, optional stepPhase))]
        locationsRe = re.compile(r'^([a-z]+)([0-3]?)$')
        for dynConf in levelDict.get('dynamics', ()):
            (locations, blockNames, *delays) = dynConf
            (aa, d) = locationsRe.match(locations).groups()
            dynamics.append((
                tuple(aliases[a] for a in aa),  # key poses
                int(d) if d else None,          # direction
                [re.findall(r'[A-Z][0-9]?', r) for r in blockNames.split("/")],  # 2D list of block names
                delays
            ))
        
        return ((w, h), cells, dynamics)
    
    def load_level(self):
        if self.switchLevel:
            self.levelIndex += 1
            self.startIndex  = 0
            self.switchLevel = False
    
        if self.levelIndex == len(LEVELS): raise "CONGRATULATIONS!"
    
        (w, h), mapCells, dynamics = self.parse_level(LEVELS[self.levelIndex])
        
        self.levelSize      = (w, h)
        self.levelSurface   = pygame.surface.Surface((w*CELLSIZE, h*CELLSIZE))  # no scaling up, original pixel size
        self.ticks          = pygame.time.get_ticks()  # current time in ms (already needed for starting animations)

        self.startPoses     = [None]      # start and respawn poses
        self.finishPos      = None
        self.heroPoses      = [None]      # first one for hero, others for doubles
        self.heroState      = 0           # index of hero skin (0 for normal, others for dying)
        self.boxes          = []          # list of positions
        self.lazers         = []          # list of Lazer objects
        self.lazersOn       = True        # we turn them off when hero reach the finish
        self.teleports      = defaultdict(list)  # teleport color => [(x,y), (x,y)] - both teleport poses
        
        self.animations     = []        # list of Animation objects
        self.currentFrameDynamics = []  # used to process all current frame dynamic animations at once

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
                        pointIndex = 0
                        self.startPoses[0] = (j, i)
                    else:
                        pointIndex = len(self.startPoses)
                        self.startPoses.append((j, i))
                    if pointIndex == self.startIndex:
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
                if addNameBits:  # no special bits were set - means regular static object - add block name bits for drawing
                    cell |= block_tuple_to_bits(letter, index1, index2)
                cell |= PROPERTY_BITS_MAP.get(letter, 0)
                self.level[i][j] = cell

        # Some validation
        if not self.heroPoses[0]:   raise Exception("No start pos found")
        if not self.finishPos:      raise Exception("No finish pos found")

        # Start dynamic animations
        for (poses, direction, blocks, delays) in dynamics:
            self.start_dynamic_animation(poses, direction, blocks, *delays)
        
        self.recalculateLazerRays = True  # recalculate lazer ray bits
        self.redrawScene = True
        self.canPlay = True  # False on level ending (when just waiting for final animations end)
    
    def start_dynamic_animation(self, keyPoses, direction, blocks, stepDelay, stepPhase = 0):
        poses = []   # collect all poses (from key poses)
        pc = len(keyPoses)
        if pc == 1:  # moving by direction
            if direction is None: raise "invalid dynamic by direction"
            poses.append(keyPoses[0])
        else:        # moving by key poses
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
            (letter, i1, i2) = block_name_to_tuple(blockName)
            d = self.start_dynamic_block(
                block_tuple_to_bits(letter, i1, i2),
                PROPERTY_BITS_MAP[letter],
                stepDelay, stepPhase,
                [add(p, (j,i)) for p in poses], direction
            )
            if letter in "LJ":  # lazer or glass lazer
                lazer = Lazer(direction = i1, dynamic = d)
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
            if a.name == "dyn":
                self.draw_block_by_bits(a.currentPos, a.nameBits)

        # Layer 2
        for (i,a) in enumerate(self.level):
         for (j,cell) in enumerate(a):
            for ray in range(4):                # Rays
                if cell & (BIT_RAY0 << ray):
                    self.draw_block((j,i), "R", ray)
            if cell & BIT_BOX:                  # Box
                self.draw_block((j,i), "B")
        
        # update window
        self.windowSurface.fill('black')
        W, H = self.windowSize
        
        # header
        hh = self.headerHeight
        textSurface = self.headerFont.render("Text Text Text", True, 0x7F7F7Fff)
        self.windowSurface.blit(textSurface, (hh // 8, 0))
        textSurface = self.headerFont.render("Text Text Text", True, 0x7F7F7Fff)
        
        
        # blit the level
        w, h = self.levelSize
        k = min(W // w, (H - hh) // h)
        self.windowSurface.blit(pygame.transform.scale(self.levelSurface, (w*k, h*k)), (0, hh))
        
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
    def start_dynamic_block(self, nameBits, propertyBits, stepDelay, stepPhase, poses, direction):
        d = DynamicAnimation(
            "dyn",
            self.ticks - stepPhase,  # substract a 'stepPhase' from the first animation step delay
            self.proc_dynamic_block,
            nameBits,
            propertyBits,
            stepDelay,
            poses, direction
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
            if d.currentPos is None: continue  # not yet started
            (x,y) = d.currentPos
            self.level[y][x] &= ~d.propertyBits
        # put to next cell
        for d in self.currentFrameDynamics:
            dirIndex = None
            if d.direction is None:     # move by poses
                prevPos = d.poses[d.posIndex]
                d.posIndex += 1
                d.posIndex %= len(d.poses)
                d.currentPos = d.poses[d.posIndex]
                step = sub(d.currentPos, prevPos)
                dirIndex = DIRECTIONS.index(step)
            else:                       # move by direction
                if d.currentPos is None:
                    d.currentPos = d.poses[0]
                    dirIndex = d.direction
                else:
                    d.currentPos, dirIndex, _ = self.get_next_cell(d.currentPos, d.direction)
            self.put_dynamic_to_next_cell(d, dirIndex)
        #
        self.currentFrameDynamics = []
        self.recalculateLazerRays = True
        self.redrawScene = True
    def put_dynamic_to_next_cell(self, dyn, dirIndex):
        if dyn.propertyBits & BIT_DAMAGE:
            # check a box here
            (x,y) = dyn.currentPos
            if self.level[y][x] & BIT_BOX:
                self.level[y][x] &= ~BITS_BOX        # erase the box
                self.level[y][x] |=  BIT_BOX_BROKEN  # single bit only
            # check the hero is here
            elif self.canPlay and (x,y) in self.heroPoses:
                self.end_playing(win = False)
        else:
            # collect items to move (player, boxes,..)
            items = []  # list of tuples (position, [indices]) where index -1 for box or hero index 0,1..
            move = False  # move (if space behind) or crash (the first item, if no space)
            p = dyn.currentPos
            d = dirIndex
            while p:
                (x,y) = p
                bits = self.level[y][x]
                if self.canPlay and p in self.heroPoses:
                    items.append((p, [i for (i,h) in enumerate(self.heroPoses) if h == p]))
                elif bits & BIT_BOX:
                    items.append((p, [-1]))
                else:
                    move = not (bits & BIT_SOLID)  # move (if space) or crash (if solid)
                    if move and items: items.append((p, []))  # add also the last cell (space) to move to
                    break
                p, d, _ = self.get_next_cell(p, d)
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
                        if self.canPlay:
                            self.end_playing(win = False)
        (x,y) = dyn.currentPos
        self.level[y][x] |= dyn.propertyBits

    
    def get_next_cell(self, pos, dirIndex, allowTeleport = True):
        newPos = (x,y) = add(pos, DIRECTIONS[dirIndex])
        if not self.in_level(newPos): return (None,None,None)
        bits = self.level[y][x]
        
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
                    if not self.in_level(newPos): return (None,None,None)
                    bits = self.level[y][x]
                else:
                    break  # can't enter - just like a solid block
        
        return (newPos, dirIndex, bits)


    def handle_hero_step(self, dirIndex):
        
        for i in range(len(self.heroPoses)):
        
            newPos, dirIndex, bits = self.get_next_cell(self.heroPoses[i], dirIndex)
            if newPos is None: continue
            
            if not bits & BIT_SOLID:
                self.heroPoses[i] = newPos
                #self.recalculateLazerRays = True
                self.redrawScene = True
            
            elif bits & BIT_BOX:  # box. can we move it?
                newPos2, dirIndex2, bits2 = self.get_next_cell(newPos, dirIndex)
                if newPos2 is None: continue
                
                if not bits2 & BIT_SOLID:  # we can move it
                    (x, y ) = newPos
                    (x2,y2) = newPos2
                    self.level[y ][x ] &= ~BITS_BOX  #!!! remove bits by global mask (not only BOX)
                    self.level[y2][x2] |=  BITS_BOX
                    self.heroPoses[i] = newPos
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
            self.switchLevel = True
            #self.levelIndex += 1  #!!! use some self.switchLevel instead
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
                elif e.type == pygame.VIDEORESIZE:
                    self.windowSize = e.size
                    self.handle_window_resize()
                    self.redrawScene = True  #!!! update the window only needed
                elif e.type == pygame.KEYDOWN:
                    if self.canPlay:
                        dirIndex = KEY_DIRECTIONS.get(e.key, -1)  # => 0..3
                        if dirIndex != -1:
                            self.handle_hero_step(dirIndex)

            # Process all animations (remove ended ones)
            self.process_animations()  # animation procs called here
            self.process_current_frame_dynamics()

            if self.recalculateLazerRays:
                self.recalculate_lazer_rays()
                self.recalculateLazerRays = False
            
            if self.canPlay:
                for (x,y) in self.heroPoses:
                    if self.level[y][x] & (BITS_RAYS | BIT_DAMAGE):
                        self.end_playing(win = False)
                heroPos = self.heroPoses[0]
                if heroPos == self.finishPos:
                    self.end_playing(win = True)
                elif heroPos in self.startPoses:
                    self.startIndex = self.startPoses.index(heroPos)  # save pos to respawn

            if self.redrawScene:
                self.redraw_scene()
                self.redrawScene = False



def test():
    print(image_regions)


def main():
    #test(); return
    
    pygame.init()
    print(pygame.version)

    pygame.display.set_mode((800, 600), flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption('Blue Ball')
    
    game = BlueBallGame()
    game.run_loop()
    
    pygame.quit()



main()
