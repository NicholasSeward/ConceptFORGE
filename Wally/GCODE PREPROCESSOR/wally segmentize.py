import math,copy,turtle

front_z=152.0
back_z=151.5
square_z=75 #the z height where the bed arms are at 90 degrees
l=150
L=250
d=200 #print diameter
y_offset=37.5
mechanical_advantage=9.5



front_z=float(front_z)
back_z=float(back_z)
square_z=float(square_z)
l=float(l)
L=float(L)
d=float(d)
y_offset=float(y_offset)
mechanical_advantage=float(mechanical_advantage)
def testcode(x,y,z):
    a,b,c=transform(x,y,z)
    return "G1 X"+str(a)+" Y"+str(b)+" Z"+str(c)+" F9000"

"""def transform(x,y,z):
    initial_angle=math.acos(L/2/l/2)
    bed_angle=math.asin((z-square_z)/l)
    leg_offset=l*math.cos(bed_angle)
    ypri20me=+y-y_offset-leg_offset
    #print yprime
    xprime=x+L/2
    topz=((d/2-y)/d)*front_z+(1-(d/2-y)/d)*back_z
    bed_tilt=math.atan2(-back_z+front_z,d)
    yprime-=z*math.sin(bed_tilt)
    zprime=topz-z*math.cos(bed_tilt)
    a=math.sqrt(xprime**2+yprime**2)
    b=math.sqrt(xprime**2+yprime**2+L**2-2*xprime*L)
    c=math.acos((2*l**2-a**2)/2/l/l)
    dp=math.acos((2*l**2-b**2)/2/l/l)
    e=math.atan(-yprime/xprime)
    f=math.atan(-yprime/(L-xprime))
    g=e+(math.pi-c)/2-initial_angle
    h=f+(math.pi-dp)/2-initial_angle
    stepper1=c*mechanical_advantage+g
    stepper2=dp*mechanical_advantage+h
    return stepper1,stepper2,zprime"""

def transform(x,y,z):
    initial_angle=math.acos(L/(4*l))#
    bed_angle=math.asin((z-square_z)/l)#
    leg_offset=l*math.cos(bed_angle)
    yprime=y+y_offset-leg_offset
    xprime=x+L/2
    topz=((d/2-y)/d)*front_z+(1-(d/2-y)/d)*back_z
    bed_tilt=math.atan2(-back_z+front_z,d)
    yprime-=z*math.sin(bed_tilt)
    zprime=topz-z*math.cos(bed_tilt)
    left_leg=math.sqrt(xprime*xprime+yprime*yprime)
    right_leg=math.sqrt((L-xprime)*(L-xprime)+yprime*yprime)
    left_elbow=math.acos((left_leg*left_leg-2*l*l)/(-2*l*l))
    right_elbow=math.acos((right_leg*right_leg-2*l*l)/(-2*l*l))
    left_small_angle=(math.pi-left_elbow)/2
    right_small_angle=(math.pi-right_elbow)/2
    left_virtual=math.atan(-yprime/xprime)
    right_virtual=math.atan(-yprime/(L-xprime))
    left_drive=left_small_angle+left_virtual-initial_angle
    right_drive=right_small_angle+right_virtual-initial_angle
    left_stepper=-left_drive+(math.pi-left_elbow)*mechanical_advantage
    right_stepper=-right_drive+(math.pi-right_elbow)*mechanical_advantage
    #print "left_angle: "+str(left_drive)+" left_elbow: "+str(math.pi-left_elbow)
    #print "right_angle: "+str(left_drive)+" right_elbow: "+str(math.pi-right_elbow)
    return left_stepper*200/math.pi,right_stepper*200/math.pi,zprime

def getABC(position1):
    global coord
    if "X" not in position1:
        return position1
    position=copy.deepcopy(position1)
    d=distance(coord,position)
    f=position["F"]
    a1,b1,c1=transform(coord["X"],coord["Y"],coord["Z"])
    a2,b2,c2=transform(position["X"],position["Y"],position["Z"])                                                     
    virtual_d=math.sqrt((a1-a2)**2+(b1-b2)**2+(c1-c2)**2)
    fnew=f*1.0
    if d!=0:
        fnew=f*virtual_d/d

    position['X']=a2
    position['Y']=b2
    position['Z']=c2
    position['F']=fnew
    coord=position1
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
        if c in end and c in start and c in "XYZE":
            middle[c]=(i*end[c]+(n-i)*start[c])/float(n)
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
            
    
print testcode(0,0,0)
f=file(raw_input("Input File: "))
coord={"X":0,"Y":0,"Z":0, "E":0, "F":0}
prefixes="MGXYZESF"
commands="MG"
f2=file(raw_input("Output File: "),"w")
f2.write("G92 X0 Y0 Z0 E0\n")
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



f2.close()
print "done"



