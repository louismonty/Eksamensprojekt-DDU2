#libaries
import math
import random
import time 

#block size 
block_size = 800/21
cols = 20
rows = 20

#colors
gray=(150,150,150)
black = 0, 0, 0
green = 0,255,0
red = 255,0,0
blue = 0,0,250
pink = (255,105,180)
dark_gray= (66, 69, 68)

#time and path length accounting 
time_overall = 0
path_overall = 0 


#block objekt 
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

#finds neigbors  
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

#Euklid heuristic
def heuristic(ax,ay,bx,by):
    d = round(math.sqrt((ax-bx)**2+(ay-by)**2),2)
    return d

#10000 loops
r= 0
while(r<10000):
    #resets lists after run
    start_timer = time.time()
    open_set=[]
    closed_set=[]
    path=[]
    found_wall = []
    #a*loop bool
    stop = False

    #creates grid
    grid = [[d+1 for d in range(rows)] for i in range(cols)] 

    #makes the objekts
    for i in range(cols):
        for j in range(rows):
            grid[i][j] = block(i,j)
    #makes random walls          
    for i in range(cols):
        for j in range(rows):
            if int(random.uniform(0, 4)) == 1:
               grid[i][j].wall = True

    #creates start and random end
    start=grid[1][1]
    end=grid[int(random.uniform(1,cols))][int(random.uniform(1,cols))]
    end.wall=False
    start.wall=False
    start.path_len = 0

    open_set.append(start)

    fejl = False
    
    #uendeligt loop
    exit = False
    while exit == stop:

        if(not stop):
            lowest_index = 0
            #finds neighbors
            for i in range(cols):
                for j in range(rows):
                    grid[i][j].addneighbors(grid)
            end.f = 0
            #finds lowst scored
            if len(open_set)>0:
                for i in range(len(open_set)):
                    if(open_set[i].f<open_set[lowest_index].f):
                        lowest_index = i
                curent = open_set[lowest_index] 
                #if at end stops a* loop 
                if open_set[lowest_index]==end:
                    stop = True
                #removes current
                del open_set[lowest_index]
                closed_set.append(curent)
                if(not stop):
                    for i in range(len(curent.neighbors)):
                        if(curent.neighbors[i].wall == True):
                            found_wall.append( curent.neighbors[i])
                        elif(curent.neighbors[i] not in closed_set):
                            #uses manhatan heuristic
                            temp_g= man_heuristic(curent.neighbors[i].x,
                            curent.neighbors[i].y,start.x,start.y)
                        #for each steep makes g score longer
                        #    if(curent.previous):
                        #       temp_g = curent.previous.path_len+1
                        #    else:
                        #       temp_g = 1
                         
                            new_path=False
                            # if its cheked
                            if(curent.neighbors[i] in open_set):
                                if(temp_g < curent.neighbors[i].g):
                                    curent.neighbors[i].g = temp_g
                                    new_path = True
                            else:
                                curent.neighbors[i].g = temp_g
                                new_path = True
                                open_set.append(curent.neighbors[i])
                            #if new path is found 
                            if(new_path):
                                curent.neighbors[i].h = man_heuristic(
                                    curent.neighbors[i].x,
                                    curent.neighbors[i].y,end.x,end.y)
                                curent.neighbors[i].f = round((curent.neighbors[i].h*1) 
                                                            +curent.neighbors[i].g,2)
                                curent.neighbors[i].previous=curent
            else:
                #print(stop)
                stop = True
                fejl = True


        
    end_time = time.time()
    #only takes the ones that get to the end
    if(not fejl):
        time_overall += round(end_time-start_timer,2)
        path_overall += len(path)
        r+=1
    #status 
    if( (r%1000)==0):
        print(r)
#prints out the overall sum
print(r)
print(time_overall/r)
print(path_overall/r)