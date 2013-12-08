import math,copy

"""PARAMETERS"""
shoulder_offset=37.5
hub_offset=50
arm_length=200
screw_spacing=300
screw_angles=[150,270,30]
start_positions=[253.25,253.25,253.25] #G92 X253.75 Y253.75 Z253.75

delta_radius=screw_spacing/3.0*math.sqrt(3)
screw_positions=[(delta_radius*math.cos(math.pi*screw_angles[i]/180.0),delta_radius*math.sin(math.pi*screw_angles[i]/180.0)) for i in range(3)]

coord={"X":0,"Y":0,"Z":0, "E":0, "F":1200}

f=file(raw_input("Input File: "))

def transform_raw(x,y,z):
    thetas=[(((+.5-math.atan2(y-screw_positions[i][1],x-screw_positions[i][0])/2/math.pi+screw_angles[i]/360.0)+.5)%1-.5)*25.4 for i in range(3)]
    ds=[math.sqrt((x-screw_positions[i][0])**2+(y-screw_positions[i][1])**2) for i in range(3)]
    try:
        return [z+thetas[i]+math.sqrt(arm_length**2-(ds[i]-hub_offset-shoulder_offset)**2) for i in range(3)]
    except:
        print x,y,z
def transform(x,y,z):
    A,B,C=transform_raw(0,0,0)
    a,b,c=transform_raw(x,y,z)
    return a-A,b-B,c-C
#print "G1","X"+str(x-X),"Y"+str(y-Y),"Z"+str(z-Z)
print transform(0,0,0)
def getABC(position1):
    if "X" not in position1:
        return position1
    position=copy.deepcopy(position1)
    d=distance(coord,position)
    xs,ys,zs=coord["X"],coord["Y"],coord["Z"]
    x,y,z,f=position["X"],position["Y"],position["Z"],position["F"]
    a1,b1,c1=transform(xs,ys,zs)
    a2,b2,c2=transform(x,y,z)
    virtual_d=math.sqrt((a1-a2)**2+(b1-b2)**2+(c1-c2)**2)
    fnew=f
    if d!=0:
        fnew=f*virtual_d/d
    position['X']=a2
    position['Y']=b2
    position['Z']=c2
    position['F']=fnew*2
    return position




def distance(start, end):
    try:
        x1,y1,z1=start['X'],start['Y'],start['Z']
        x2,y2,z2=end['X'],end['Y'],end['Z']
        return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    except:
        return 0

def interpolate(start, end, i, n):
    x1,y1,z1,e1=start['X'],start['Y'],start['Z'],start['E']
    x2,y2,z2,e2=end['X'],end['Y'],end['Z'],end['E']
    middle={}
    for c in end:
        if c in end and c in start and c!="F":
            middle[c]=(i*end[c]+(n-i)*start[c])/n
        else:
            middle[c]=end[c]
    return middle

def segmentize(start,end,maxLength):
    l=distance(start,end)
    if l<=maxLength:
        return [end]
    else:
        output=[]
        n=int(math.ceil(l/maxLength))
        for i in range(1,n+1):
            output.append(interpolate(start,end,i,n))
        return output
            
    



prefixes="MGXYZESF"
commands="MG"
f2=file(raw_input("Output File: "),"w")
f2.write("G92 X"+str(start_positions[0])+" Y"+str(start_positions[1])+" Z"+str(start_positions[2])+"\n")
program=[]
move_count=0
for line in f:
    line=line.strip()
    chunks=line.split(";")[0].split(" ")
    stuff={}
    for chunk in chunks:
        if len(chunk)>1:
            stuff[chunk[0]]=chunk[1:]
            try:
                stuff[chunk[0]]=int(stuff[chunk[0]])
            except:
                try:
                    stuff[chunk[0]]=float(stuff[chunk[0]])
                except:
                    pass
        if "X" in stuff or "Y" in stuff or "Z" in stuff:
            move_count+=1
            for c in coord:
                if c not in stuff:
                    stuff[c]=coord[c]           
    if move_count<=3 and len(stuff)>0:
        program+=[stuff]
    elif len(stuff)>0:
        segments=segmentize(coord,stuff,1)
        program+=segments
    for c in coord:
        if c in stuff:
            coord[c]=stuff[c]

for line in program:
    abcline=getABC(line)
    for letter in prefixes:
        if letter in abcline and letter in commands:
            f2.write(letter+str(abcline[letter])+" ")
        elif letter in abcline:
            f2.write(letter+str(round(abcline[letter],3))+" ")
    f2.write("\n")
f2.write("G1 X"+str(start_positions[0])+" Y"+str(start_positions[1])+" Z"+str(start_positions[2])+"\n")


f2.close()
print "done"

