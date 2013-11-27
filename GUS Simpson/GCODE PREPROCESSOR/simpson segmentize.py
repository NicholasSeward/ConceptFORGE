import math,copy

size=250.0 #distance from shoulder swivel to shoulder swivel
maxl=300.0 #max effective distance of an arm
offset=73 #adjust up or down to roughly zero before you zero for good.




f=file(raw_input("Input File: "))
x1=-size/2.0
y1=-size*math.sqrt(3)/2.0/3.0
z1=-offset
x2=+size/2.0
y2=-size*math.sqrt(3)/2.0/3.0
z2=-offset
x3=0
y3=2*size*math.sqrt(3)/2.0/3.0
z3=-offset
coord={"X":0,"Y":0,"Z":0, "E":0, "F":0}


def getABC(position1):
    if "X" not in position1:
        return position1
    position=copy.deepcopy(position1)
    d=distance(coord,position)
    xs,ys,zs=coord["X"],coord["Y"],coord["Z"]
    x,y,z,f=position["X"],position["Y"],position["Z"],position["F"]
    a1=maxl-math.sqrt((xs-x1)**2+(ys-y1)**2+(zs-z1)**2)
    b1=maxl-math.sqrt((xs-x2)**2+(ys-y2)**2+(zs-z2)**2)
    c1=maxl-math.sqrt((xs-x3)**2+(ys-y3)**2+(zs-z3)**2)
    a2=maxl-math.sqrt((x-x1)**2+(y-y1)**2+(z-z1)**2)
    b2=maxl-math.sqrt((x-x2)**2+(y-y2)**2+(z-z2)**2)
    c2=maxl-math.sqrt((x-x3)**2+(y-y3)**2+(z-z3)**2)
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
        segments=segmentize(coord,stuff,3)
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


f2.close()
print "done"

