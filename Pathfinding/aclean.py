#imports 
import pygame
import math
import random

#init screen
pygame.init()
size = width, height = 1000, 800
screen = pygame.display.set_mode(size)

#block and gridsystem
block_size = 800/21
cols = 20
rows = 20

#collors 
gray = (150,150,150)
black = 0, 0, 0
green = 0,255 ,0
red = 255,0,0
blue = 0,0,250
pink = (255,105,180)
dark_gray= (66, 69, 68)

#lists 
open_set=[]
closed_set=[]
path=[]
found_wall = []

#loop bool
stop = False

#font
sysfont = pygame.font.get_default_font()

#block class
class block():
    def __init__(self,i,j):
        self.x = i
        self.y = j
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.previous = None
        self.wall = False
        self.path_len = 0

#draws box 
    def draw_box(self,color):
        pygame.draw.rect(screen, color, pygame.Rect(self.x*(block_size+1), self.y*(block_size+1), block_size, block_size))
  
#finds neighbors  
    def addneighbors(self,grid):
        if (self.y<cols-1):
            self.neighbors.append(grid[self.x][self.y+1])
        if (self.y>0):
            self.neighbors.append(grid[self.x][self.y-1])
        if (self.x<cols-1):
            self.neighbors.append(grid[self.x+1][self.y])
        if (self.x>0):
            self.neighbors.append(grid[self.x-1][self.y])
       
         
#Manhatan heuristic 
def man_heuristic(ax,ay,bx,by):
    d = round(abs(ax-bx)+abs(ay-by))
    return d

#Euklid 
def heuristic(ax,ay,bx,by):
    d = round(math.sqrt((ax-bx)**2+(ay-by)**2),2)
    return d

#makes grid 
grid = [[d+1 for d in range(rows)] for i in range(cols)] 

#objekt constructing 
for i in range(cols):
    for j in range(rows):
        grid[i][j] = block(i,j)
        
#makes walls         
for i in range(cols):
    for j in range(rows):
        if int(random.uniform(0, 4)) == 1:
            grid[i][j].wall = True
            print(grid[i][j].x,grid[i][j].y)

#start and end 
start=grid[1][1]
end=grid[int(random.uniform(11,cols))][int(random.uniform(11,cols))]
end.wall=False
start.wall=False
start.path_len = 0

#start in openset
open_set.append(start)

#starts gameloop 
exit = False
while exit == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    screen.fill(black)

#a* loop
    if(not stop):
        lowest_index = 0
        #finds neighbors 
        for i in range(cols):
            for j in range(rows):
                grid[i][j].addneighbors(grid)
        end.f = 0
        #finds lowest scored 
        if len(open_set)>0:
            for i in range(len(open_set)):
                if(open_set[i].f<open_set[lowest_index].f):
                    lowest_index = i
            curent = open_set[lowest_index] 
            #if at end stop a* loop
            if open_set[lowest_index]==end:
                stop = True
            #removes current from openset and moves it to closed_set
            del open_set[lowest_index]
            closed_set.append(curent)
            if(not stop):
                #finds walls 
                for i in range(len(curent.neighbors)):
                    if(curent.neighbors[i].wall == True):
                        found_wall.append( curent.neighbors[i])
                    elif(curent.neighbors[i] not in closed_set):
                        #Manhatan heuristic 
                        temp_g= man_heuristic(curent.neighbors[i].x,
                        curent.neighbors[i].y,start.x,start.y)
                        #for each steep makes g score longer 
                        #if(curent.previous):
                        #    temp_g = curent.previous.path_len+1
                        #else:
                        #    temp_g = 1
                        new_path=False
                        #if its cheked
                        if(curent.neighbors[i] in open_set):
                            if(temp_g < curent.neighbors[i].g):
                                curent.neighbors[i].g = temp_g
                                new_path = True
                        else:
                            curent.neighbors[i].g = temp_g
                            new_path = True
                            open_set.append(curent.neighbors[i])
                        #if new path found 
                        if(new_path):
                            curent.neighbors[i].h = heuristic(
                                curent.neighbors[i].x,
                                curent.neighbors[i].y,end.x,end.y)
                            curent.neighbors[i].f = round((curent.neighbors[i].h*1.5) 
                                                          +curent.neighbors[i].g,2)
                            curent.neighbors[i].previous=curent


    #draws box
    for i in range(cols):
        for j in range(rows):
            grid[i][j].draw_box(gray)
            
    #draws closed_set red
    for i in range(len(closed_set)):
        closed_set[i].draw_box(red)
        
    #draws open_set green
    for i in range(len(open_set)):
        open_set[i].draw_box(green)
     
    #finds path   
    if(not stop):
        path = []
        temp = curent
        path.append(temp)
        while(temp.previous):
            path.append(temp.previous)
            temp = temp.previous
        curent.path_len = len(path)

    #draws path blue
    for i in path:
        i.draw_box(blue)

    #draws walls dark_gray
    for i in found_wall:
        i.draw_box(dark_gray)

    #draws end blue
    end.draw_box(blue)
    
    #draws score
    for i in range(len(closed_set)):  
        font = pygame.font.SysFont(sysfont, 30)
        img = font.render(str(abs(closed_set[i].f)), True, pink)
        screen.blit(img, (closed_set[i].x*(block_size+1),closed_set[i].y*block_size+20))
    #draws score    
    for i in range(len(open_set)):  
        font = pygame.font.SysFont(sysfont, 30)
        img = font.render(str(round(open_set[i].f,0)), True, pink)
        screen.blit(img, (open_set[i].x*(block_size+1),open_set[i].y*block_size+20))
    #draws path lengt
    font = pygame.font.SysFont(sysfont, 30)
    img = font.render("lenght of path "+str(len(path)), True, pink)
    screen.blit(img, (800,0))

    #updates display 
    pygame.display.flip()