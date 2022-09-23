import pygame

import sys
import time
import math

world = [ #y,x
    [2,2,1,2,1,2,1,1],
    [2,0,0,0,0,0,0,1],
    [1,0,2,0,1,0,0,2],
    [2,0,0,0,2,0,0,1],
    [1,0,0,0,1,0,0,2],
    [1,1,2,1,1,0,0,1],
    [1,0,0,0,0,0,0,2],
    [1,1,2,1,2,1,2,2]
]

colors = [(128, 128, 128),
        (140, 140, 140)]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

class Sprite():
    def __init__(self, position, size, filename):
        self.position = position
        self.size = size
        self.height = size[1]
        self.width = size[0]
        self.image = pygame.image.load(filename).convert_alpha()

class Player():
    def __init__(self):
        self.position = [5, 1]
        self.viewangle = 0 #0 to 360
        self.fov = 80
        self.rays = 180
        self.draw_distance = 8
        self.line_resolution = 25
        
        self.speed = 0.02
        
        self.hp = 10
        self.ammo_max = 30
        self.ammo = 25
        
    def move(self, world, keys):
        dx = 0
        dy = 0
    
        if keys[pygame.K_LSHIFT]: #sprinting
            speed = self.speed * 2
        else:
            speed = self.speed
    
        if keys[pygame.K_w]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle)) * speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle)) * speed
        if keys[pygame.K_s]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 180)) * speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 180)) * speed
        if keys[pygame.K_a]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 270)) * speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 270)) * speed
        if keys[pygame.K_d]:
            dx = self.position[0] + math.sin(math.radians(self.viewangle + 90)) * speed
            dy = self.position[1] + math.cos(math.radians(self.viewangle + 90)) * speed
            
        if world[round(dy)][round(dx)] == 0:
            self.position = [dx, dy]
        elif world[round(dy)][round(self.position[0])] == 0:
            self.position[1] = dy
        elif world[round(self.position[1])][round(dx)] == 0:
            self.position[0] = dx
    
    def raycast(self, world, surface, colors, sprites):
        w = surface.get_width()
        h = surface.get_height()
    
        boxwidth = w/self.rays + 1
        angle = self.fov/self.rays
        
        zbuffer = []
        for i in range(self.rays + 1):
            #generate ray angle vectors
            x = math.sin(math.radians(self.viewangle - (self.fov / 2) + (i * angle)))
            y = math.cos(math.radians(self.viewangle - (self.fov / 2) + (i * angle)))
            
            #cast rays
            for j in range(1,self.draw_distance * self.line_resolution):
                yindex = self.position[1] + (j/self.line_resolution * y)
                xindex = self.position[0] + (j/self.line_resolution * x)
                
                if (0 <= round(yindex) < len(world) and 0 <= round(xindex) < len(world[0])):
                    tile = world[round(yindex)][round(xindex)]
                    if (tile > 0):
                        scale = 1/(distance(self.position, (xindex,yindex)) * math.cos(math.radians((i * angle) - self.fov/2))) #fisheye correction
                        boxheight = h * scale
                        
                        color = colors[tile - 1]
                        
                        zbuffer.append((pygame.Rect((i*w)/self.rays, (h-boxheight)//2, boxwidth, boxheight), color, distance(self.position, (xindex,yindex)), 'rect'))
                        break
                else:
                    break #abandon ray if it lies out of bounds
            
        #place sprites in zbuffer
        for sprite in sprites:
            spriteangle = math.degrees(math.atan2(sprite.position[1] - self.position[1],sprite.position[0] - self.position[0]))
            viewlocation = (spriteangle + self.viewangle - 90 + self.fov/2) % 360
            screenlocation = w - viewlocation * (w/self.fov)
            dist = distance(self.position, sprite.position)
            scale = 1/dist
            if scale > 10:
                scale = 10
            
            zbuffer.append((sprite.image, 
                (int(sprite.width * scale), int(sprite.height * scale)), 
                dist, 'image',
                (screenlocation - (sprite.width * (scale)//2), (h - (sprite.height * scale) + ((h - sprite.height - 2*sprite.position[2]) * scale))//2)))
            
        zbuffer.sort(key = lambda x: x[2], reverse = True) #sort by distance
        for rect in zbuffer:
            if rect[3] == 'rect':
                pygame.draw.rect(surface, rect[1], rect[0])
            elif rect[3] == 'image':
                surface.blit(pygame.transform.scale(rect[0], rect[1]), rect[4])
    
def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Raycaster")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    consolas = pygame.font.SysFont("Consolas", 14)
    
    player = Player()
    sprites = []
    sprites.append(Sprite([1,1,0], (120, 250), "Assets/zombie.png"))

    hearts = pygame.image.load("Assets/hearts.png").convert_alpha()
    heart = pygame.image.load("Assets/heart_center.png").convert_alpha()
    
    ammo = pygame.image.load("Assets/ammo_single.png").convert_alpha()
    bullet = pygame.image.load("Assets/bullet.png").convert_alpha()
    
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
        player.move(world, keys)
        player.raycast(world, screen, colors, sprites)
        
        sprites[0].position[0] += 0.01
        
        frames = consolas.render("{} fps".format(round(fps,1)),True,(255,255,255))
        angle = consolas.render("angle = {}".format(player.viewangle % 360),True,(255,255,255))
        pos = consolas.render("position = {}".format(player.position),True,(255,255,255))
        screen.blit(frames, (5, 5))
        screen.blit(angle, (5, 20))
        screen.blit(pos, (5, 35))
        
        #draw health/ammo
        screen.blit(hearts, (470, 5))
        for i in range(player.hp):
            screen.blit(heart, (616 - (i*16), 7))
        
        for i in range(player.ammo_max):
            screen.blit(ammo, (614 - ((i%10)*16), 25 + 20 * (i // 10)))
        
        for i in range(player.ammo):
            screen.blit(bullet, (614 - ((i%10)*16), 25 + 20 * (i // 10)))
        
        #draw crosshair
        chsize = 7
        centerx = screen.get_width()//2
        centery = screen.get_height()//2
        pygame.draw.line(screen, (255, 255, 255), (centerx - chsize, centery), (centerx + chsize, centery), 1)
        pygame.draw.line(screen, (255, 255, 255), (centerx, centery - chsize), (centerx, centery + chsize), 1)
        
        #game code end here
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        clock.tick(60)
        fps = int(1/(time.time() - startloop + 0.000001))
    

if __name__ == "__main__":
    main(sys.argv)