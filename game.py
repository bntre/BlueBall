
import sys, re
import pygame


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
#                 [  dir  ;        letter          ]             [\  /  |  -]
#                 [                                ]             [   RAYS   ]
#                 [        block name bits         ][                 property bits                  ]
#                 # used for drawing static objects;
#                 # 0 for boxes - BIT_BOX used instead;


BIT_VISIBLE     = 1
BIT_SOLID       = 1<<1
BIT_OPAQUE      = 1<<2
BIT_FINISH      = 1<<3  # to mark finish cell (it stays "invisible")
BIT_BOX         = 1<<4
BIT_DYNAMIC     = 1<<5  # dynamic object
BIT_RAY0        = 1<<8  # shift 0..3 for  --  |  /  \
BITS_RAYS       = (BIT_RAY0 << 0) | (BIT_RAY0 << 1) | (BIT_RAY0 << 2) | (BIT_RAY0 << 3)

BITS_WALL      = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
#BITS_FINISH    = BIT_VISIBLE | BIT_NEEDS_BG
#BITS_FINISH    = BIT_VISIBLE
BITS_ICE       = BIT_VISIBLE | BIT_SOLID
BITS_LASER     = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE
BITS_ICELASER  = BIT_VISIBLE | BIT_SOLID
BITS_BOX       = BIT_VISIBLE | BIT_SOLID | BIT_OPAQUE | BIT_BOX

PROPERTY_BITS_MAP = {    # block name letter => property bits
    "W": BITS_WALL,
    #"F": BITS_FINISH,
    "I": BITS_ICE,
    "L": BITS_LASER,
    "J": BITS_ICELASER,
    "B": BITS_BOX,
    "A": BITS_WALL,         # Arrow (dynamic blocks)
}

BLOCK_NAME_SHIFT = 16
BLOCK_NAME_MASK = (0x7FF) << BLOCK_NAME_SHIFT  # 3 bits for direction, 8 bits for a letter

CELLSIZE = 9


def block_name_to_pair(name):
    return name[0], int(name[1:] or "0")
def block_pair_to_bits(letter, direction):
    bits  = ord(letter) <<      BLOCK_NAME_SHIFT
    bits |=   direction << (8 + BLOCK_NAME_SHIFT)
    return bits


def create_image_areas(text, cell_width = 4):
    """Result map: block name bits => image area"""
    m = split_text_to_cell_map(text, cell_width)
    areas = {}
    for (name,(i,j)) in m.items():
        nameBits = block_pair_to_bits(*block_name_to_pair(name))
        areas[nameBits] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas

# block name bits => area
BLOCK_AREAS = create_image_areas("""
H0  H1  H2  H3
H4  H5  H6  H7
S   W   F   I
L0  L2  L1  L3
L6  L5  L7  L4
B           
A7  A5  A4  A6
A2  A0  A1  A3
J2  J1  J3  J0
J6  J5  J7  J4
R1  R0  R2  R3
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
W   W   W   W   W   W   W   W   W   W   W
W   F       H           i               W
W                                       W
L0          J3                  B       W
W                                       W
W       I                               L1
W                       j               W
W   B   B                   B           W
W                                       W
W                                       W
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

] # end of LEVELS

LEVEL_TO_START = "temp"
LEVEL_TO_START = 4


KEY_STEPS = {
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0, 1),
}

LASER_DIRS = [
    ( 1, 0), (-1, 0),   #  >  <     0  1   >>1  0 --
    ( 0,-1), ( 0, 1),   #  ^  v     2  3        1  |
    ( 1,-1), (-1, 1),   #  /` ./    4  5        2  /
    (-1,-1), ( 1, 1),   #  `\  \,   6  7        3  \
]



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
        self.direction = direction  # 0..7  see LASER_DIRS
        self.staticPos = staticPos  # (x, y) or None for dynamic
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
        
        cells = [[None]*w for _ in range(h)]  # [i][j] => (letter, direction) or None
        aliases = {}                          # cell alias => (i,j)
        
        for (i,row) in enumerate(cellsText):
         for (j,cellText) in enumerate(row):
            if cellText:
                (letter, d, alias) = re.match(r'^([A-Z]?)([0-9]?)([a-z]?)$', cellText).groups()
                if letter:
                    cells[i][j] = (letter, int(d or "0"))
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
        
        self.animations = []  # list of Animation objects
        self.currentFrameDynamics = []  # used to process all current frame dynamic animations at once

        # Fill level cell integers
        self.level = [[0]*w for _ in range(h)]  # cell integer values
        for (i,row) in enumerate(mapCells):
         for (j,blockPair) in enumerate(row):
            if blockPair:
                letter, direction = blockPair
                cell = 0
                if letter == "H":           # Hero
                    self.heroPos = (j, i)
                else:
                    if letter == "F":       # Finish: special case - draw by BIT_FINISH
                        self.finishPos = (j, i)
                        cell |= BIT_FINISH
                    elif letter == "B":     # Box: special case - draw by BIT_BOX
                        self.boxes.append((j, i))
                        cell |= BIT_BOX
                    elif letter in "LJ":    # Laser or Ice laser
                        lazer = Lazer(direction, (j, i))
                        self.lazers.append(lazer)
                    if cell == 0:  # no special bits were set - means regular static object - add block name bits for drawing
                        cell |= block_pair_to_bits(letter, direction)
                    cell |= PROPERTY_BITS_MAP.get(letter, 0)
                self.level[i][j] = cell

        # Start dynamic animations
        for (poses, blocks, delay) in dynamics:
            self.start_dynamic_animation(poses, blocks, delay)
        
        self.recalculateLazerRays = True  # set if we need to update the scene - recalculate lazer rays
        self.redrawScene = True
        self.canPlay = True  # False on dying
    
    def start_dynamic_animation(self, keyPoses, blocks, delay):
        print(keyPoses, blocks) #!!!
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
            (letter, direction) = block_name_to_pair(blockName)
            d = self.start_dynamic_block(
                block_pair_to_bits(letter, direction),
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
    
    def draw_block(self, pos, letter = None, direction = 0, nameBits = None):
        if nameBits is None: 
            nameBits = block_pair_to_bits(letter, direction)
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

            # Draw by block name (e.g. L1,..)
            nameBits = cell & BLOCK_NAME_MASK
            if nameBits:
                self.draw_block((j,i), nameBits = nameBits)
        
        # hero
        self.draw_block(self.heroPos, "H", self.heroState)
        
        # dynamic objects
        for a in self.animations:
            if a.name == "dyn":
                pos = a.poses[a.posIndex]
                self.draw_block(pos, nameBits = a.nameBits)

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
        w, h = self.levelSize
        
        # Update lazers (corresponding cell bits: BITS_RAYS)
        for i in range(h):
         for j in range(w):
            self.level[i][j] &= ~BITS_RAYS;
        for lazer in self.lazers:
            ray = lazer.direction >> 1  # 0..3: - | / \
            step = LASER_DIRS[lazer.direction]
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
            self.start_new_level_animation()  # reload same level
            a.ended = True

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
            propertyBits | BIT_DYNAMIC, 
            poses, delay
        )
        self.animations.append(d)
        return d
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
            self.level[y][x] |= d.propertyBits
        #
        self.currentFrameDynamics = []
        self.recalculateLazerRays = True
        self.redrawScene = True


    def handle_hero_step(self, step):
        """step is e.g. (-1,0)"""
        newPos = (x,y) = add(self.heroPos, step)
        #print(step, newPos)
        if not self.in_level(newPos): return
        bits = self.level[y][x]

        if not bits & BIT_SOLID:
            self.heroPos = newPos
            self.recalculateLazerRays = True
            self.redrawScene = True
        
        if bits & BIT_BOX:  # box. can we move it?
            newPos2 = (x2,y2) = add(newPos, step)
            if self.in_level(newPos2):
                bits2 = self.level[y2][x2]
                if not bits2 & BIT_SOLID:  # we can move it
                    self.level[y ][x ] &= ~BITS_BOX  #!!! remove bits by global mask (not only BOX)
                    self.level[y2][x2] |=  BITS_BOX
                    self.heroPos = newPos
                    self.recalculateLazerRays = True
                    self.redrawScene = True
                    self.start_pushing_box_animation()
    
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
                        step = KEY_STEPS.get(e.key)  # e.g. (-1,0)
                        if step:
                            self.handle_hero_step(step)

            # Process all animations (remove ended ones)
            self.process_animations()  # animation procs called here

            self.process_current_frame_dynamics()

            if self.canPlay:
                x, y = self.heroPos
                if self.level[y][x] & BITS_RAYS:
                    print("=== GAME OVER ===")
                    self.canPlay = False
                    self.stop_pushing_box_animation() # if any
                    self.start_dying_animation()
                
                if self.heroPos == self.finishPos:
                    print("=== YOU WIN ===")
                    self.canPlay = False
                    self.levelIndex += 1
                    self.stop_pushing_box_animation() # if any
                    self.start_new_level_animation()

            if self.recalculateLazerRays:
                self.recalculate_lazer_rays()
                self.recalculateLazerRays = False
            
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