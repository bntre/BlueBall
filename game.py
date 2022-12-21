
import sys
import pygame


def run_loop():
    
    windowSurface = pygame.display.get_surface()
    levelSurface = pygame.surface.Surface((36, 36))

    imagesSurface = pygame.image.load("images.png").convert()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        levelSurface.fill('black')
        for i in range(4):
            levelSurface.blit(imagesSurface, dest = (i * 9, 0), area = (9,18,9,9))
        
        windowSurface.blit(pygame.transform.scale(levelSurface, (360, 360)), (0, 0))
        
        pygame.display.update()


def main():
    #pygame.init()
    
    pygame.display.init()
    pygame.display.set_mode((800, 600), flags = pygame.RESIZABLE, depth = 32)
    pygame.display.set_caption('Blue Ball')
    
    run_loop()
    
    pygame.quit()


main()