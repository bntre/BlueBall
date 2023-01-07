
import sys
import pygame


#----------------------------------

def add(p0, p1):
    return (p0[0] + p1[0], p0[1] + p1[1])
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

CELLSIZE = 9


def create_image_areas(text, cell_width = 4):
    m = split_text_to_cell_map(text, cell_width)
    areas = {}
    for (name,(i,j)) in m.items():
        areas[name] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas



block_areas = create_image_areas("""
H0  H1  H2  H3
H4  H5  H6  H7
S   W   F   I
L0  L2  L1  L3
L6  L5  L7  L4
B           
            
            
J2  J1  J3  J0
J6  J5  J7  J4
R1  R0  R2  R3
""")

BLOCK_VISIBLE   = 1
BLOCK_SOLID     = 1<<1
BLOCK_OPAQUE    = 1<<2
BLOCK_NEEDS_BG  = 1<<3  # has transparency and needs background
BLOCK_BOX_BIT   = 1<<4
CELL_RAY        = 1<<5  # shift 0..3 for  --  |  /  \
CELL_RAYS       = (CELL_RAY << 0) | (CELL_RAY << 1) | (CELL_RAY << 2) | (CELL_RAY << 3)

BLOCK_WALL      = BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE
BLOCK_FINISH    = BLOCK_VISIBLE | BLOCK_NEEDS_BG
BLOCK_ICE       = BLOCK_VISIBLE | BLOCK_SOLID
BLOCK_LASER     = BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE
BLOCK_ICELASER  = BLOCK_VISIBLE | BLOCK_SOLID
BLOCK_BOX       = BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE | BLOCK_BOX_BIT


BLOCK_MAP = {    # block name letter => property bits
    "W": BLOCK_WALL,
    "F": BLOCK_FINISH,
    "I": BLOCK_ICE,
    "L": BLOCK_LASER,
    "J": BLOCK_ICELASER,
    "B": BLOCK_BOX,
}


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
W   F                                   W
W                                       W
L0          J3                  B       W
W                                       W
W       I                               L1
W                                       W
W   B   B                   B           W
W                                       W
W   H0                                  W
""" },

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
]

LEVEL_TO_START = 1


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



class BlueBallGame:

    def __init__(self):
        self.windowSurface = pygame.display.get_surface()
        self.blocksSurface = pygame.image.load("blocks.png").convert()  # DOC: convert() to create a copy that will draw more quickly on the screen
        self.blocksSurface.set_colorkey(self.blocksSurface.get_at((0,0)))  # set transparency color from top-left corner

        self.levelIndex = 0  # first by default
        for (i,l) in enumerate(LEVELS):
            if l["name"] == LEVEL_TO_START:
                self.levelIndex = i
        self.load_level()
    
    def load_level(self):
        blocksText = LEVELS[self.levelIndex]["map"]
        blocks = split_text_to_cells(blocksText)
        w, h = len(blocks[0]), len(blocks)

        self.levelSize = (w, h)
        self.levelBlocks = blocks  # block map loaded from block text
        self.levelSurface = pygame.surface.Surface((w*CELLSIZE, h*CELLSIZE))  # no scaling up, original pixel size

        self.level = []  # property bits for each cell
        self.boxes = []  # list of positions
        self.lazers = []  # list of (pos, direction)
        self.heroPos = None
        self.finishPos = None
        
        for i in range(h):
            row = []
            for j in range(w):
                bits = 0  # 0 for space (default)
                name = blocks[i][j]
                if name:
                    letter = name[0]
                    if letter == "H":       # Hero
                        self.heroPos = (j, i)
                    elif letter == "F":     # Finish
                        self.finishPos = (j, i)
                    elif letter == "B":     # Box
                        self.boxes.append((j, i))
                    elif letter in "LJ":    # Laser or Ice laser
                        d = int(name[1])     # direction
                        self.lazers.append(((j, i), d))
                    bits = BLOCK_MAP.get(letter, 0)
                row.append(bits)
            self.level.append(row)
    
    def is_in_level(self, pos):
        x, y = pos
        w, h = self.levelSize
        return 0 <= x < w and 0 <= y < h
    
    def draw_block(self, pos, blockName):
        area = block_areas.get(blockName)
        if not area: return
        x, y = pos
        self.levelSurface.blit(
            self.blocksSurface, 
            dest = (pos[0]*CELLSIZE, pos[1]*CELLSIZE), 
            area = area
        )
    
    def redraw_level(self):
        self.levelSurface.fill('black')
        
        # level
        for (i,a) in enumerate(self.level):
         for (j,bits) in enumerate(a):
            if not bits & BLOCK_VISIBLE:
                self.draw_block((j,i), "S")         # just space
            else:
                if bits & BLOCK_NEEDS_BG:           # draw background for some blocks
                    self.draw_block((j,i), "S")
                
                if bits & BLOCK_BOX_BIT:            # Box
                    self.draw_block((j,i), "B")
                #elif not bits & BLOCK_VISIBLE:     # Space (background)
                else:
                    name = self.levelBlocks[i][j]   #  get block name from level block map
                    self.draw_block((j,i), name)
            for ray in range(4):                # Rays
                if bits & (CELL_RAY << ray):
                    self.draw_block((j,i), "R%d" % ray)
        
        # hero
        self.draw_block(self.heroPos, "H0")
        
        # update window
        w, h = self.levelSize
        w2, h2 = self.windowSurface.get_size()
        k = int(min(w2/w, h2/h))
        self.windowSurface.fill('black')
        self.windowSurface.blit(pygame.transform.scale(self.levelSurface, (w*k, h*k)), (0, 0))
        pygame.display.update()
    
    def update_lazers(self):
        w, h = self.levelSize
        
        for i in range(h):
         for j in range(w):
            self.level[i][j] &= ~CELL_RAYS;
        
        for (pos0,d) in self.lazers:
            ray = d>>1  # 0..3
            step = LASER_DIRS[d]
            pos = pos0
            while True:
                pos = (x,y) = add(pos, step)
                if not self.is_in_level(pos): break
                if self.level[y][x] & BLOCK_OPAQUE: break
                self.level[y][x] |= CELL_RAY << ray;

    
    def run_loop(self):
        
        while True:
            
            updateLazers = False
            
            # handle all events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN:
                    step = KEY_STEPS.get(e.key)  # e.g. (-1,0)
                    if step:
                        wasMoved = self.try_to_step(step)
                        if wasMoved:
                            updateLazers = True
            
            updateLazers = True  # always?
            if updateLazers:
                self.update_lazers();
            
            self.redraw_level()

            x, y = self.heroPos
            if self.level[y][x] & CELL_RAYS:
                print("=== GAME OVER ===")
                self.load_level()
                #return
            
            if self.heroPos == self.finishPos:
                print("=== I WIN ===")
                self.levelIndex += 1
                self.load_level()
                #return


    def try_to_step(self, step):
        "move is e.g. (-1,0)"
        newPos = (x,y) = add(self.heroPos, step)
        #print(step, newPos)
        if self.is_in_level(newPos):
            bits = self.level[y][x]
            if bits & BLOCK_BOX_BIT:  # box. can we move it?
                newPos2 = (x2,y2) = add(newPos, step)
                if self.is_in_level(newPos2):
                    bits2 = self.level[y2][x2]
                    if not bits2 & BLOCK_SOLID:  # we can move it
                        self.level[y ][x ] &= ~BLOCK_BOX
                        self.level[y2][x2] |=  BLOCK_BOX
                        self.heroPos = newPos
                        return True
            elif not bits & BLOCK_SOLID:
                self.heroPos = newPos
                return True
        return False
    


def test():
    print(image_regions)


def main():
    #test(); return
    
    pygame.display.init()
    pygame.display.set_mode((800, 600), flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption('Blue Ball')
    
    game = BlueBallGame()
    game.run_loop()
    
    pygame.quit()



main()