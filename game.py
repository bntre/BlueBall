
import sys
import pygame


#----------------------------------

def add(p0, p1):
    return (p0[0] + p1[0], p0[1] + p1[1])
def mult(p, k):
    return (p[0] * k, p[1] * k)
    

def split_text_to_cells(text, cell_width = 3):
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

def split_text_to_cell_map(text, cell_width = 3):
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


def create_image_areas(text, cell_width = 3):
    m = split_text_to_cell_map(text, cell_width)
    areas = {}
    for (name,(i,j)) in m.items():
        areas[name] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas



block_areas = create_image_areas("""
H0 H1 H2 H3
H4 H5 H6 H7
   W  F
L0 L1 L2 L3
L7 L4 L5 L6
B




R0 R1 R2 R3
""")

BLOCK_VISIBLE   = 1
BLOCK_SOLID     = 2
BLOCK_OPAQUE    = 4
BLOCK_BOX_BIT   = 8

BLOCK_BOX       = BLOCK_BOX_BIT | BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE

BLOCK_MAP = {    # block name letter => property bits
    "W": BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE,
    "F": BLOCK_VISIBLE,
    "L": BLOCK_VISIBLE | BLOCK_SOLID | BLOCK_OPAQUE,
}


LEVEL1 = """
W  W  W  W  W  W
W  F           W
W  L0          W
W        B     W
W        H0    W
W  W  W  W  W  W
"""

KEY_MOVES = {
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0, 1),
}

LASER_DIRS = [
    (1, 0), (0, -1), (-1, 0), (0, 1),   # >  ^  <  v
    (1, -1), (-1, -1), (-1, 1), (1, 1)  # /` `\ ,/ \,
]


class BlueBallGame:
    def __init__(self):
        self.windowSurface = pygame.display.get_surface()
        self.blocksSurface = pygame.image.load("blocks.png").convert()  # DOC: convert() to create a copy that will draw more quickly on the screen
        self.blocksSurface.set_colorkey(self.blocksSurface.get_at((0,0)))  # set transparency color from top-left corner

        self.load_level(LEVEL1)
    
    def load_level(self, blocksText):
        blocks = split_text_to_cells(blocksText)
        w, h = len(blocks[0]), len(blocks)

        self.levelSize = (w, h)
        self.levelBlocks = blocks
        self.levelSurface = pygame.surface.Surface((w*CELLSIZE, h*CELLSIZE))  # no scaling up, original pixel size

        self.heroPos = None
        self.boxes = []  # list of positions
        self.lazers = []
        self.level = []  # property bits for each cell
        for i in range(h):
            row = []
            for j in range(w):
                bits = 0  # 0 for space (default)
                name = blocks[i][j]
                if name:
                    letter = name[0]
                    if letter == "H":
                        self.heroPos = (j, i)
                    elif letter == "B":
                        self.boxes.append((j, i))
                        bits = BLOCK_BOX
                    else:
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
            if bits:
                if bits & BLOCK_BOX_BIT:
                    name = "B"
                else:
                    name = self.levelBlocks[i][j]
                self.draw_block((j,i), name)
        
        # hero
        self.draw_block(self.heroPos, "H0")
        
        # update window
        self.windowSurface.blit(pygame.transform.scale(self.levelSurface, (360, 360)), (0, 0))
        pygame.display.update()
    
    def run_loop(self):
        
        while True:
        
            # handle all events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN:
                    move = KEY_MOVES.get(e.key)
                    if move:
                        newPos = (x,y) = add(self.heroPos, move)
                        #print(move, newPos)
                        if self.is_in_level(newPos):
                            bits = self.level[y][x]
                            if bits & BLOCK_BOX_BIT:  # box. can we move it?
                                newPos2 = (x2,y2) = add(newPos, move)
                                if self.is_in_level(newPos2):
                                    bits2 = self.level[y2][x2]
                                    if not bits2 & BLOCK_SOLID:  # we can move it
                                        self.level[y ][x ] &= ~BLOCK_BOX
                                        self.level[y2][x2] |=  BLOCK_BOX
                                        self.heroPos = newPos
                                
                            elif not bits & BLOCK_SOLID:
                                self.heroPos = newPos

            self.redraw_level()


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