#improrts 
import pygame
import math
import random

#initilising screen
pygame.init()
size = width, height = 1000, 800
screen = pygame.display.set_mode(size)

#block set
block_size = 800/21
cols = 20
rows = 20

#open csv file
f = open("demofile3.csv", "r")

gray = (150,150,150)
black = 0, 0, 0
green = 0,255 ,0
red = 255,0,0
blue = 0,0,250
pink = (255,105,180)
dark_gray= (66, 69, 68)

open_set=[]
closed_set=[]
path=[]
found_wall = []

stop = False

sysfont = pygame.font.get_default_font()

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

    def draw_box(self,color):
        pygame.draw.rect(screen, color, pygame.Rect(self.x*(block_size+1), self.y*(block_size+1), block_size, block_size))
    
    def addneighbors(self,grid):
        if (self.y<cols-1):
            self.neighbors.append(grid[self.x][self.y+1])
        if (self.y>0):
            self.neighbors.append(grid[self.x][self.y-1])
        if (self.x<cols-1):
            self.neighbors.append(grid[self.x+1][self.y])
        if (self.x>0):
            self.neighbors.append(grid[self.x-1][self.y])
       
         

def man_heuristic(ax,ay,bx,by):
    d = round(abs(ax-bx)+abs(ay-by))
    return d

def heuristic(ax,ay,bx,by):
    d = round(math.sqrt((ax-bx)**2+(ay-by)**2),2)
    return d

grid = [[d+1 for d in range(rows)] for i in range(cols)] 

for i in range(cols):
    for j in range(rows):
        grid[i][j] = block(i,j)
        
#for i in range(cols):
#    for j in range(rows):
#        if int(random.uniform(0, 4)) == 1:
#            grid[i][j].wall = True
#            print(grid[i][j].x,grid[i][j].y)
x = -1           
for wal in f:
    x+=1
    y=-1
    wall = wal.split(" ")
    for k in wal:
        if k == "x":
            grid[y][x].wall = True
            y+=1
        elif k == "o":
            y+=1

start=grid[1][1]
#end=grid[int(random.uniform(11,cols))][int(random.uniform(11,cols))]
end = grid[19][19]
end.wall=False
start.wall=False
start.path_len = 0

open_set.append(start)

exit = False
while exit == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    screen.fill(black)

    if(not stop):
        lowest_index = 0
        for i in range(cols):
            for j in range(rows):
                grid[i][j].addneighbors(grid)
        end.f = 0
        if len(open_set)>0:
            for i in range(len(open_set)):
                if(open_set[i].f<open_set[lowest_index].f):
                    lowest_index = i
            curent = open_set[lowest_index] 
            if open_set[lowest_index]==end:
                stop = True
            del open_set[lowest_index]
            closed_set.append(curent)
            if(not stop):
                for i in range(len(curent.neighbors)):
                    if(curent.neighbors[i].wall == True):
                        found_wall.append( curent.neighbors[i])
                    elif(curent.neighbors[i] not in closed_set):
                        #temp_g= man_heuristic(curent.neighbors[i].x,
                        #curent.neighbors[i].y,start.x,start.y)
                        if(curent.previous):
                            temp_g = curent.previous.path_len+1
                        else:
                            temp_g = 1
                        new_path=False
                        if(curent.neighbors[i] in open_set):
                            if(temp_g < curent.neighbors[i].g):
                                curent.neighbors[i].g = temp_g
                                new_path = True
                        else:
                            curent.neighbors[i].g = temp_g
                            new_path = True
                            open_set.append(curent.neighbors[i])
                        if(new_path):
                            curent.neighbors[i].h = heuristic(
                                curent.neighbors[i].x,
                                curent.neighbors[i].y,end.x,end.y)
                            curent.neighbors[i].f = round((curent.neighbors[i].h*1) +curent.neighbors[i].g,2)
                            curent.neighbors[i].previous=curent


    #g current til start h current til slut 
    for i in range(cols):
        for j in range(rows):
            grid[i][j].draw_box(gray)
            

    for i in range(len(closed_set)):
        closed_set[i].draw_box(red)
        

    for i in range(len(open_set)):
        open_set[i].draw_box(green)
        
    if(not stop):
        path = []
        temp = curent
        path.append(temp)
        while(temp.previous):
            path.append(temp.previous)
            temp = temp.previous
        curent.path_len = len(path)


    for i in path:
        i.draw_box(blue)

    for i in found_wall:
        i.draw_box(dark_gray)

    end.draw_box(blue)
    
    for i in range(len(closed_set)):  
        font = pygame.font.SysFont(sysfont, 30)
        img = font.render(str(abs(closed_set[i].f)), True, pink)
        screen.blit(img, (closed_set[i].x*(block_size)+closed_set[i].x,closed_set[i].y*block_size+closed_set[i].y))
        
    for i in range(len(open_set)):  
        font = pygame.font.SysFont(sysfont, 30)
        img = font.render(str(round(open_set[i].f,0)), True, pink)
        screen.blit(img, (open_set[i].x*(block_size)+open_set[i].x,open_set[i].y*block_size+open_set[i].y))

    font = pygame.font.SysFont(sysfont, 30)
    img = font.render("lenght of path "+str(len(path)), True, pink)
    screen.blit(img, (800,0))

    pygame.display.flip()