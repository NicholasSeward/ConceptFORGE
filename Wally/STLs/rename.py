import glob,os

files=glob.glob("*")
print files
for f in files:
    os.rename(f,f.replace(".ipt",""))
