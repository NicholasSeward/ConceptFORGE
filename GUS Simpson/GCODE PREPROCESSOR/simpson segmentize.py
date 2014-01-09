#THIS IS A ConceptFORGE PRODUCT.
#GPL LICENSE

#EXPERIMENTAL.  THIS CODE NEEDS IMPROVEMENT.

#ALL LENGTHS ARE IN mm

#A LIST OF MACHINE POSITIONS WHERE PAPER CAN
#BARELY SLIDE BETWEEN THE BED AND THE EXTRUDER.
#THIS NEEDS TO COVER THE AREA YOU WANT TO PRINT.
#THE MORE THE BETTER.
#EXPECT THE MACHINE TO NEED TO BE RECALIBRATED OFTEN AS
#THE SYSTEM GETS WORKED IN.
POINTS=[(183.6,100,100),
        (100,184.1,100),
        (100,100,182.7),
        (133.4,133.4,133.4),
        (207.5,75,75),
        (75,207.9,75),
        (75,75,206.7),
        (146.2,146.2,100),
        (100,145.7,145.7),
        (145.6,100,145.6)]

#DISTANCE FROM SHOULDER SCREW TO SHOULDER SCREW
SIZE=250.0

#APPROXIMATE Z DISTANCE FROM SHOULDER ARM ATTACHMENT
#TO HUB ARM ATTACHMENT
BED_Z=70

#APPROXIMATE MAX ACTUATED LENGTH OF ARM
MAX_ARM_LENGTH=300

#HOW SMALL SHOULD THE LINE SEGMENTS BE BROKEN DOWN TO.
#SMALL=BETTER QUALITY
#LARGE=SMALLER FILE/FASTER
SEGMENT_SIZE=1.0


from scipy.optimize import leastsq
import numpy.linalg
import math, random, copy, sys

if len(sys.argv)<3:
    f=file(raw_input("Input File: "))
    f2=file(raw_input("Output File: "),"w")
else:
    f=file(sys.argv[1])
    f2=file(sys.argv[2])

DEFAULT_VALUES=[BED_Z,BED_Z,BED_Z,MAX_ARM_LENGTH,MAX_ARM_LENGTH,MAX_ARM_LENGTH]

SHOULDER_Z1,SHOULDER_Z2,SHOULDER_Z3,MAX_LENGTH_1,MAX_LENGTH_2,MAX_LENGTH_3=DEFAULT_VALUES

#GET COORDINATES USING TRILATERATION
def getxyz(r1,r2,r3):
    d=SIZE*1.0
    i=SIZE/2.0
    j=SIZE*math.sqrt(3)/2.0
    x=(r1*r1-r2*r2+d*d)/(2*d)
    y=(r1*r1-r3*r3-x*x+(x-i)**2+j*j)/(2*j)
    z=math.sqrt(r1*r1-x*x-y*y)
    return x,y,z

#GET VALUES FOR EACH POINT TO SEE HOW CLOSE TO THE PLANE IT IS
def equations(p):
    SHOULDER_Z1,SHOULDER_Z2,SHOULDER_Z3,MAX_LENGTH_1,MAX_LENGTH_2,MAX_LENGTH_3=p
    m=[]
    for i in range(len(POINTS)):
        R1,R2,R3=MAX_LENGTH_1-POINTS[i][0],MAX_LENGTH_2-POINTS[i][1],MAX_LENGTH_3-POINTS[i][2]
        X,Y,Z=getxyz(R1,R2,R3)
        d=SIZE*1.0
        i=SIZE/2.0
        j=SIZE*math.sqrt(3)/2.0
        q=[[0,0,SHOULDER_Z1,1],
           [d,0,SHOULDER_Z2,1],
           [i,j,SHOULDER_Z3,1],
           [X,Y,Z,1]]
        det=numpy.linalg.det(q)
        m.append(det**2)
    return m

#GET OPTIMAL VALUES
SHOULDER_Z1,SHOULDER_Z2,SHOULDER_Z3,MAX_LENGTH_1,MAX_LENGTH_2,MAX_LENGTH_3=leastsq(equations, DEFAULT_VALUES)[0]



x1=-SIZE/2.0
y1=-SIZE*math.sqrt(3)/2.0/3.0
z1=-SHOULDER_Z1
x2=+SIZE/2.0
y2=-SIZE*math.sqrt(3)/2.0/3.0
z2=-SHOULDER_Z2
x3=0
y3=2*SIZE*math.sqrt(3)/2.0/3.0
z3=-SHOULDER_Z3
x0,y0,z0=getxyz(MAX_LENGTH_1,MAX_LENGTH_2,MAX_LENGTH_3)
coord={"X":x0+x1,"Y":y0+y1,"Z":z0+z1, "E":0, "F":0}


def getABC(position1):
    if "X" not in position1:
        return position1
    position=copy.deepcopy(position1)
    d=distance(coord,position)
    xs,ys,zs=coord["X"],coord["Y"],coord["Z"]
    x,y,z,f=position["X"],position["Y"],position["Z"],position["F"]
    a1=MAX_LENGTH_1-math.sqrt((xs-x1)**2+(ys-y1)**2+(zs-z1)**2)
    b1=MAX_LENGTH_2-math.sqrt((xs-x2)**2+(ys-y2)**2+(zs-z2)**2)
    c1=MAX_LENGTH_3-math.sqrt((xs-x3)**2+(ys-y3)**2+(zs-z3)**2)
    a2=MAX_LENGTH_1-math.sqrt((x-x1)**2+(y-y1)**2+(z-z1)**2)
    b2=MAX_LENGTH_2-math.sqrt((x-x2)**2+(y-y2)**2+(z-z2)**2)
    c2=MAX_LENGTH_3-math.sqrt((x-x3)**2+(y-y3)**2+(z-z3)**2)
    virtual_d=math.sqrt((a1-a2)**2+(b1-b2)**2+(c1-c2)**2)
    fnew=f
    if d!=0:
        fnew=f*virtual_d/d
    position['X']=a2
    position['Y']=b2
    position['Z']=c2
    position['F']=fnew
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

program=[]
move_count=0
for line in f:
    line=line.upper()
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
        segments=segmentize(coord,stuff,SEGMENT_SIZE)
        program+=segments
    for c in coord:
        if c in stuff:
            coord[c]=stuff[c]
f2.write("G92 X0 Y0 Z0 E0\nG1 X-1000 Y-1000 Z-1000\nG28\n")
for line in program:
    abcline=getABC(line)
    for letter in prefixes:
        if letter in abcline and letter in commands:
            f2.write(letter+str(abcline[letter])+" ")
        elif letter in abcline:
            f2.write(letter+str(round(abcline[letter],3))+" ")
    f2.write("\n")


f2.close()
print "done"

