import math, struct, glob

class facet:
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
    def __getitem__(self,i):
        if i==0:
            return self.p1
        elif i==1:
            return self.p2
        elif i==2:
            return self.p3
        else:
            raise IndexError
    def __len__(self):
        return 3
    def get_normal(self):
        (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=self
        ux,uy,uz=x2-x1,y2-y1,z2-z1
        vx,vy,vz=x3-x1,y3-y1,z3-z1
        x,y,z=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
        l=math.sqrt(x*x+y*y+z*z)
        x,y,z=x/l,y/l,z/l
        return (x,y,z)
    def angle(self):
        x,y,z=self.get_normal()
        return 90-math.degrees(math.acos(z))
    def midPoints(self):
        (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=self
        return ((x1+x2)/2,(y1+y2)/2,(z1+z2)/2),((x3+x2)/2,(y3+y2)/2,(z3+z2)/2),((x1+x3)/2,(y1+y3)/2,(z1+z3)/2)
    def get_maxl(self):
        (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=self
        l1=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
        l2=math.sqrt((x1-x3)**2+(y1-y3)**2+(z1-z3)**2)
        l3=math.sqrt((x3-x2)**2+(y3-y2)**2+(z3-z2)**2)
        return max(l1,l2,l3)
    def transform(self,func):
        self.p1=func(self.p1)
        self.p2=func(self.p2)
        self.p3=func(self.p3)
    def projectedArea(self):
        (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=self
        a=math.sqrt((x1-x2)**2+(y1-y2)**2)
        b=math.sqrt((x3-x2)**2+(y3-y2)**2)
        c=math.sqrt((x1-x3)**2+(y1-y3)**2)
        s=.5*(a+b+c)
        return math.sqrt(s*(s-a)*(s-b)*(s-c))

class solid:
    def __init__(self,filename):
        f=file(filename)
        text=f.read()
        self.facets=[]
        if "vertex" in text and "outer loop" in text and "facet normal" in text:
            
            text_facets=text.split("facet normal")[1:]
            for text_facet in text_facets:
                points=text_facet.split()[6:-2]
                p1=[float(x) for x in points[0:3]]
                p2=[float(x) for x in points[4:7]]
                p3=[float(x) for x in points[8:11]]
                self.facets.append(facet(p1,p2,p3))
        else:
            f.close()
            f=file(filename,"rb")
            f.read(80)
            n=struct.unpack("I",f.read(4))[0]
            for i in xrange(n):
                facetdata=f.read(50)
                try:
                    data=struct.unpack("12f1H",facetdata)
                    normal=data[0:3]
                    v1=data[3:6]
                    v2=data[6:9]
                    v3=data[9:12]
                    self.facets.append(facet(v1,v2,v3))
                except:
                    print "ERROR REPORT"
                    print [ord(c) for c in facetdata]
                    print "facet number:",i
                    print "facet count:", n
                    

    def getBounds(self):
        p1=list(self.facets[0][0])
        p2=list(self.facets[0][0])
        for f in self.facets:
            for v in f:
                for i in range(3):
                    if v[i]<p1[i]:
                        p1[i]=v[i]
                    if v[i]>p2[i]:
                        p2[i]=v[i]
        return p1,p2

    def printRating(self,minAngle=-60):
        (x,y,minz),p2=self.getBounds()
        c=0
        base=0
        for f in self.facets:
            (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=f
            if abs(minz-z1)<.1 and abs(minz-z2)<.1 and abs(minz-z3)<.1:
                base+=f.projectedArea()
            elif f.angle()<minAngle:
                c+=f.projectedArea()*abs(minz-z1)
        return c,base

    def getSize(self):
        p1,p2=self.getBounds()
        x1,y1,z1=p1
        x2,y2,z2=p2
        return x2-x1,y2-y1,z2-z1
    

    def sub_divide(self,d=1):
        nfacets=[]
        again=False
        l=0
        for f in self.facets:
            p1,p2,p3=f
            if f.get_maxl()<d:
                nfacets.append(f)
            else:
                if l<f.get_maxl():
                    l=f.get_maxl()
                again=True
                p12,p23,p31=f.midPoints()
                nfacets.append(facet(p1,p12,p31))
                nfacets.append(facet(p2,p23,p12))
                nfacets.append(facet(p3,p31,p23))
                nfacets.append(facet(p12,p23,p31))
        self.facets=nfacets
        if again:
            self.sub_divide(d)

    def transform(self,func):
        for f in self.facets:
            f.transform(func)

    def rotX(self):
        for f in self.facets:
            f.transform(lambda (x,y,z): (x,z,-y))
            
    def rotY(self):
        for f in self.facets:
            f.transform(lambda (x,y,z): (z,y,-x))

    def zero(self):
        (x1,y1,z1),p2=self.getBounds()
        for f in self.facets:
            f.transform(lambda (x,y,z): (x-x1,y-y1,z-z1))

    def save(self,filename,ascii=False):
        self.zero()
        if ascii:
            output="solid "+filename.split(".")[0]+"\n"
            for face in self.facets:
                nx,ny,nz=face.get_normal()
                (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=face
                output+="  facet normal "+str(nx)+" "+str(ny)+" "+str(nz)+"\n"
                output+="    outer loop\n"
                output+="      vertex "+str(x1)+" "+str(y1)+" "+str(z1)+"\n"
                output+="      vertex "+str(x2)+" "+str(y2)+" "+str(z2)+"\n"
                output+="      vertex "+str(x3)+" "+str(y3)+" "+str(z3)+"\n"
                output+="    endloop\n"
                output+="  endfacet\n"
            f=file(filename,"w")
            f.write(output)
            f.close()
        else:
            f=file(filename,"wb")
            f.write(("STLB "+filename).ljust(80))
            f.write(struct.pack("I",len(self.facets)))
            for face in self.facets:
                nx,ny,nz=face.get_normal()
                (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=face
                f.write(struct.pack("12f1H",nx,ny,nz,x1,y1,z1,x2,y2,z2,x3,y3,z3,0))
            f.close



def getBestOrientation(s):
    best_cost,best_base=s.printRating()
    for i in range(4):
        cost,base=s.printRating()
        if base>0 and cost<best_cost:
            best_cost=cost
            best_base=base
        if base>best_base and cost==best_cost:
            best_base=base
        s.rotX()
    for i in range(4):
        cost,base=s.printRating()
        if base>0 and cost<best_cost:
            best_cost=cost
            best_base=base
        if base>best_base and cost==best_cost:
            best_base=base
        s.rotY()
    for i in range(4):
        cost,base=s.printRating()
        if cost==best_cost and base==best_base:
            return s
        s.rotX()
    for i in range(4):
        cost,base=s.printRating()
        if cost==best_cost and base==best_base:
            return s
        s.rotY()
    

solids=glob.glob("*.stl")
for sname in solids:
    if sname[:4]!="mod_":
        print "Processing:",sname
        s=solid(sname)
        getBestOrientation(s)
        s.save(sname)

