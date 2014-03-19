import math,copy,turtle,sys

try:
    import numpy
except:
    print "Download numpy."
    raw_input("PRESS ENTER TO EXIT PROGRAM")
    sys.exit()

try:
    import scipy.optimize
    import scipy.interpolate 
    
except:
    print "Download scipy."
    raw_input("PRESS ENTER TO EXIT PROGRAM")
    sys.exit()

#How many mm does the machine think is one rotation of the x or y axis?
mm_rotation=400    

#various machine coordinate sets where the effector barely touches the bed
touch_points=[(820,720,149.90),(820,1370,150.5),(1370,820,151),(1200,1200,150.9),(1350,3600,151.40)] 

#CALIBRATION DATA FOR THE BED HEIGHT
z_machine_actual=[(1,0.08),(2,0.84),(3,1.76),(4,2.68),
                  (5,3.62),(6,4.52),(7,5.45),(8,6.35),
                  (9,7.21),(10,8.13),(11,9.11),(12,10.03),
                  (13,11.05),(14,12.11),(15,13.19),(16,14.3),
                  (17,15.42),(18,16.51),(19,17.61),(20,18.71),
                  (21,19.74),(22,20.72),(23,21.65),(24,22.57),
                  (25,23.5),(26,24.44),(27,25.41),(28,26.39),
                  (29,27.41),(30,28.45),(31,29.51),(32,30.61),
                  (33,31.69),(34,32.77),(35,33.87),(36,34.94),
                  (37,36.01),(38,37.01),(39,37.97),(40,38.97),
                  (41,39.89),(42,40.85),(43,41.81),(44,42.79),
                  (45,43.84),(46,44.88),(47,45.96),(48,47.02),
                  (49,48.11),(50,49.24),(51,50.34),(52,51.42),
                  (53,52.48),(54,53.5),(55,54.5),(56,55.48),
                  (57,56.47),(58,57.43),(59,58.41),(60,59.43),
                  (61,60.48),(62,61.52),(63,62.57),(64,63.65),
                  (65,64.75),(66,65.83),(67,66.94),(68,68.01),
                  (69,69.09),(70,70.13),(71,71.15),(72,72.14),
                  (73,73.1),(74,74.07),(75,75.08),(76,76.08),
                  (77,77.13),(78,78.14),(79,79.19),(80,80.25),
                  (81,81.32),(82,82.38),(83,83.44),(84,84.51),
                  (85,85.58),(86,86.66),(87,87.62),(88,88.6),
                  (89,89.54),(90,90.5),(91,91.47),(92,92.45),
                  (93,93.47),(94,94.5),(95,95.55),(96,96.6),
                  (97,97.62),(98,98.65),(99,99.72),(100,100.76),
                  (101,101.83),(102,102.86),(103,103.85),(104,104.85),
                  (105,105.81),(106,106.8),(107,107.72),(108,108.68),
                  (109,109.7),(110,110.7),(111,111.71),(112,112.73),
                  (113,113.75),(114,114.76),(115,115.8),(116,116.84),
                  (117,117.87),(118,118.88),(119,119.87),(120,120.85),
                  (121,121.74),(122,122.73),(123,123.63),(124,124.54),
                  (125,125.49),(126,126.46),(127,127.42),(128,128.4),
                  (129,129.39),(130,130.39),(131,131.4),(132,132.32),
                  (133,133.42),(134,134.44),(135,135.42),(136,136.4),
                  (137,137.37),(138,138.29),(139,139.2),(140,140.1),
                  (141,141.05),(142,141.97),(143,142.95),(144,143.89),
                  (145,144.87),(146,145.85),(147,146.86),(148,147.85),
                  (149,148.87),(150,149.86),(151,150.86),(152,151.87),
                  (153,152.84),(154,153.77),(155,154.68),(156,155.57)]

#the z height where the bed arms are at 90 degrees
square_z=76.97

#LENGTH OF ARMS
l=150

#DISTANCE BETWEEN SHOULDERS
L=250

#DISTANCE FROM BED ARM ATTACHMENT TO THE CENTER OF THE BED IN THE Y DIRECTION
y_offset=37.5

#Using "G1 X? Y?" to find the machine coordinates that make the arms colinear
straight_forearms=996 


machine_z=numpy.array([i for i,j in z_machine_actual])
actual_z=numpy.array([j for i,j in z_machine_actual])
square_z=float(square_z)
l=float(l)
L=float(L)
y_offset=float(y_offset)
straight_forearms=float(straight_forearms)
mm_rotation=float(mm_rotation)
mechanical_advantage=(straight_forearms/(mm_rotation/2)*math.pi+math.asin(1-L/2.0/l)+math.asin(L/4.0/l))/(math.pi-math.acos(1-L/2.0/l))




def interpolate2(v,leftLookup=True):
    try:
        x=machine_z
        y=actual_z
        if leftLookup:
            f = scipy.interpolate.interp1d(x, y)#, kind='cubic')
        else:
            f = scipy.interpolate.interp1d(y,x)
        return float(f(v))
    except:
        return 0

    """total_weight=0
    new_v=0
    table.sort()
    for m,a in table:
        if not leftLookup:
            m,a=a,m
        if m!=v:
            weight=1.0/(m-v)**2
        else:
            weight=100.0
        new_v+=weight*a
        total_weight+=weight
    return new_v/total_weight"""
#print interpolate2(0)



def machine2reference((x,y,z)):
    zprime=interpolate2(z)
    def func((i,j)):
        (x2,y2,z2)=reference2machine((i,j,0))
        return (x-x2)**2+(y-y2)**2
    xprime,yprime=scipy.optimize.fmin(func,(100,-100), xtol=0.000001, ftol=0.000001,disp=False)
    return xprime,yprime,zprime
    
def reference2machine((x,y,z)):
    try:
        zprime=interpolate2(z,False)
        initial_angle=math.acos(L/(4*l))
        left_leg=math.sqrt(x*x+y*y)
        right_leg=math.sqrt((L-x)*(L-x)+y*y)
        left_elbow=math.acos((left_leg*left_leg-2*l*l)/(-2*l*l))
        right_elbow=math.acos((right_leg*right_leg-2*l*l)/(-2*l*l))
        left_small_angle=(math.pi-left_elbow)/2
        right_small_angle=(math.pi-right_elbow)/2
        left_virtual=math.atan(-y/x)
        right_virtual=math.atan(-y/(L-x))
        left_drive=left_small_angle+left_virtual-initial_angle
        right_drive=right_small_angle+right_virtual-initial_angle
        left_stepper=-left_drive+(math.pi-left_elbow)*mechanical_advantage
        right_stepper=-right_drive+(math.pi-right_elbow)*mechanical_advantage
        return left_stepper*mm_rotation/2/math.pi,right_stepper*mm_rotation/2/math.pi,zprime
    except:
        return 0,0,0

def refPlane():
    ref_points=[(machine2reference(p)) for p in touch_points]
    #print ref_points
    def func((a,b,c,d)):
        v=0
        for x,y,z in ref_points:
            v+=(a*x+b*y+c*z+d)**2
        return v
    a,b,c,d=scipy.optimize.fmin(func,(1,1,1,1),disp=False)
    return a,b,c,d

print "Finding bed level from touch points.  This may take a while."
ap,bp,cp,dp=refPlane()
#print ap,bp,cp,dp

#print machine2reference((1000,1000,100))
#print reference2machine((125,125,100))
def actual2reference((x,y,z)):
    bed_angle=math.asin((z-interpolate2(square_z))/l)
    leg_offset=l*math.cos(bed_angle)
    yprime=y+y_offset-leg_offset
    xprime=x+L/2
    zero_z=(-dp-ap*xprime-bp*yprime)/cp
    #print xprime,yprime,zero_z
    zprime=zero_z-z
    return xprime,yprime,zprime
#print actual2reference((0,0,0))

def reference2actual((x,y,z)):
    pass

def transform(x,y,z):
    return reference2machine(actual2reference((x,y,z)))
#print transform(0,0,0)

def testcode(x,y,z):
    a,b,c=transform(x,y,z)
    #print transform(x,y,z)
    return "G1 X"+str(a)+" Y"+str(b)+" Z"+str(c)+" F9000"
#print testcode(0,0,0)

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
#print testcode(0,0,0)


def distance(start, end):
    try:
        x1,y1,z1=start['X'],start['Y'],start['Z']
        x2,y2,z2=end['X'],end['Y'],end['Z']
        return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    except:
        return 0
#print testcode(0,0,0)


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
for i in range(len(program)):
    line=program[i]
    if i%100==0:
        print str(i*100.0/len(program))+"%"
    abcline=getABC(line)
    for letter in prefixes:
        if letter in abcline and letter in commands:
            f2.write(letter+str(abcline[letter])+" ")
        elif letter in abcline:
            f2.write(letter+str(round(abcline[letter],3))+" ")
    f2.write("\n")



f2.close()
print "done"



