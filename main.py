import pygame

import sys
import time
import math

world = [ #y,x
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,0,1],
    [1,0,1,0,1,0,0,1],
    [1,0,0,0,1,0,0,1],
    [1,1,1,1,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1]
]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

class Player():
    def __init__(self):
        self.position = [5, 1]
        self.viewangle = 0 #0 to 360
        self.fov = 70
        self.rays = 90
        self.draw_distance = 8
        self.line_resolution = 20
        
        self.speed = 0.02
        
    def move(self, keys):
        dx = 0
        dy = 0
    
        if keys[pygame.K_w]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle)) * self.speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle)) * self.speed
        if keys[pygame.K_s]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 180)) * self.speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 180)) * self.speed
        if keys[pygame.K_a]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 270)) * self.speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 270)) * self.speed
        if keys[pygame.K_d]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 90)) * self.speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 90)) * self.speed
            
        if world[round(dy)][round(dx)] == 0:
            self.position = [dx, dy]
        elif world[round(dy)][round(self.position[0])] == 0:
            self.position[1] = dy
        elif world[round(self.position[1])][round(dx)] == 0:
            self.position[0] = dx
            
    def raycast(self, world, surface):
        boxwidth = surface.get_width()/self.rays + 1
        angle = self.fov/self.rays
        
        for i in range(self.rays + 1):
            #generate ray angle vectors
            x = math.sin(math.radians(self.viewangle - (self.fov / 2) + (i * angle)))
            y = math.cos(math.radians(self.viewangle - (self.fov / 2) + (i * angle)))
            
            #cast rays
            for j in range(1,self.draw_distance * self.line_resolution):
                yindex = self.position[1] + (j/self.line_resolution * y)
                xindex = self.position[0] + (j/self.line_resolution * x)
                
                if (0 <= round(yindex) < len(world) and 0 <= round(xindex) < len(world[0])):
                    if (world[round(yindex)][round(xindex)] == 1):
                        boxheight = surface.get_height() * (1/distance(self.position, (xindex,yindex)))
                        pygame.draw.rect(surface, (128,128,128), 
                        pygame.Rect((i*surface.get_width())/self.rays, (surface.get_height()-boxheight)//2, boxwidth, boxheight))
                        break
                else:
                    break #abandon ray if it lies out of bounds
    
def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Raycaster")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    consolas = pygame.font.SysFont("Consolas", 14)
    
    player = Player()
    
    run = True
    locked = True
    fps = 0
    mouse_speed = 2
    clock = pygame.time.Clock()
    while run:
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    locked = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
            if event.type == pygame.MOUSEBUTTONDOWN:
                locked = True
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
        
        if locked:
            pygame.mouse.set_pos(screen.get_width()//2,screen.get_height()//2)
            m = pygame.mouse.get_rel()
            if m[0] != 0 and abs(m[0]) < 300: #if the mouse moved, move camera
                player.viewangle += math.radians(m[0] * mouse_speed)
        
        #game code start here
        screen.fill((0,128,255))
        pygame.draw.rect(screen, (128,100,0), pygame.Rect(0, screen.get_height()//2,
                            screen.get_width(), screen.get_height()//2))
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        player.raycast(world, screen)
        
        frames = consolas.render("{} fps".format(round(fps,1)),True,(255,255,255))
        angle = consolas.render("angle = {}".format(player.viewangle % 360),True,(255,255,255))
        pos = consolas.render("position = {}".format(player.position),True,(255,255,255))
        screen.blit(frames, (5, 5))
        screen.blit(angle, (5, 20))
        screen.blit(pos, (5, 35))
        
        #game code end here
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        clock.tick(240)
        fps = int(1/(time.time() - startloop + 0.000001))
    

if __name__ == "__main__":
    main(sys.argv)