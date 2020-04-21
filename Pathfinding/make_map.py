import random

f = open("demofile3.csv", "a")

for i in range(20):
    for j in range(20):
        if int(random.uniform(0, 3)) == 1:
            f.write("x")
        else:
            f.write("o")
    f.write("\n")
    
    
f.close()