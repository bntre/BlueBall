
import sys
import pygame

CELLSIZE = 9


def split_text_to_cells(text, cell_width = 3):
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
    arr = split_text_to_cells(text, cell_width)
    m = {}
    for (i,a) in enumerate(arr):
     for (j,cell) in enumerate(a):
        if cell:
            m[cell] = (i,j)
    return m



def create_image_areas(text, cell_width = 3):
    m = split_text_to_cell_map(text, cell_width)
    areas = {}
    for (name,(i,j)) in m.items():
        areas[name] = (j*CELLSIZE, i*CELLSIZE, CELLSIZE, CELLSIZE)
    return areas



image_areas = create_image_areas("""
H0 H1 H2 H3
H4 H5 H6 H7
   W  F
L0 L1 L2 L3

B
""")

level = split_text_to_cells("""
W  W  W  W  W  W
W  F           W
W  L0          W
W        B     W
W        H0    W
W  W  W  W  W  W
""")



def run_loop():
    
    windowSurface = pygame.display.get_surface()
    levelSurface = pygame.surface.Surface((6*CELLSIZE, 6*CELLSIZE))

    imagesSurface = pygame.image.load("images.png").convert()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        levelSurface.fill('black')
        
        for (i,a) in enumerate(level):
         for (j,name) in enumerate(a):
            if name:
                a = image_areas[name]
                levelSurface.blit(imagesSurface, dest = (j*CELLSIZE, i*CELLSIZE), area = a)
        
        windowSurface.blit(pygame.transform.scale(levelSurface, (360, 360)), (0, 0))
        
        pygame.display.update()



def test():
    print(image_regions)


def main():
    #test(); return
    
    pygame.display.init()
    pygame.display.set_mode((800, 600), flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption('Blue Ball')
    
    run_loop()
    
    pygame.quit()



main()