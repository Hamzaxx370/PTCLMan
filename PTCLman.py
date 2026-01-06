import sys
import struct
import os
from binary_reader import BinaryReader
import json


FilePath = sys.argv[1:]
def extract(FilePath):
    FILENAME = os.path.splitext(os.path.basename(FilePath))[0]
    INPUTDIR = os.path.dirname(FilePath)
    OUTPUTDIR = os.path.join(INPUTDIR,(FILENAME + ".unpack"))
    os.makedirs(OUTPUTDIR,exist_ok=True)
    OUTPUTPATH4 = os.path.join(OUTPUTDIR,f"{"manifest" + ".json"}")
    JSON = open(OUTPUTPATH4,"w")
    ptcl = open (FilePath,"rb")
    reader = BinaryReader(ptcl.read())
    writer = BinaryReader()
    reader.seek (48)
    ParticleTableOffset = reader.read_uint32()+48
    ParticleCount = reader.read_uint32()
    OMETableOffset = reader.read_uint32()+48
    OMECount = reader.read_uint32()
    TXBTableOffset = reader.read_uint32()+48
    TXBCount = reader.read_uint32()
    IDLIST=[]
    
    manifestdata={
        "Particle Count": ParticleCount,
        "OME Count": OMECount,
        "TXB Count": TXBCount,
        "Files": []
        
    }

    reader.seek (ParticleTableOffset)
    for p in range (ParticleCount):
        reader.seek((ParticleTableOffset) +(4*p))
        ParticleTableEntry = reader.read_uint32()+48
        reader.seek(ParticleTableEntry)
        ParticleHeader = reader.pos()
        PTCLNAME = reader.read_str(12)
        ParticleSize = reader.read_uint32()
        reader.seek(ParticleHeader+40)
        ID = reader.read_uint32()
        if ID!=0:
            IDLIST.append((ID,PTCLNAME))
            
        reader.seek(ParticleHeader)
        ParticleFile = reader.read_bytes(int(ParticleSize))
        OUTPUTPATH1 = os.path.join(OUTPUTDIR,f"{str(PTCLNAME)}.ptcl")
        manifestdata["Files"].append(os.path.basename(OUTPUTPATH1))
        with open (OUTPUTPATH1,"wb") as output1:
            output1.write (ParticleFile)
        
    reader.seek (OMETableOffset)
    for o in range (OMECount):
        reader.seek(OMETableOffset +(4*o))
        OMETableEntry = reader.read_uint32()+48
        reader.seek (OMETableEntry)
        OMEHeader = reader.pos()
        reader.seek (OMEHeader + 8)
        ODBPOffset = reader.read_uint32()
        ODBPSKIP = (ODBPOffset + 12)
        reader.seek (int(ODBPOffset) + int(OMETableEntry) + 12)
        ODBPsize = reader.read_uint32()
        OMESize = (int(ODBPOffset) + int(ODBPsize))
        reader.seek(OMEHeader)  
        OMEFile = reader.read_bytes(int(OMESize) + 12)
        OUTPUTPATH2 = os.path.join(OUTPUTDIR,f"{str(o) + ".OME"}")
        manifestdata["Files"].append(os.path.basename(OUTPUTPATH2))
        with open (OUTPUTPATH2,mode="wb") as output2:
            output2.write (OMEFile)
        
    reader.seek (TXBTableOffset)
    for t in range(TXBCount):
        reader.seek (TXBTableOffset + (t*4))
        TXBTableEntry = reader.read_uint32()+48
        reader.seek ((TXBTableEntry) + 8)
        TXBSize = reader.read_uint32() +64
        reader.seek (TXBTableEntry)
        TXBFile = reader.read_bytes (int(TXBSize))
        OUTPUTPATH3 = os.path.join(OUTPUTDIR,f"{str(t) + ".TXB"}")
        manifestdata["Files"].append(os.path.basename(OUTPUTPATH3))
        with open (OUTPUTPATH3,mode="wb")as output3:
            output3.write (TXBFile)
    
    
    json.dump(manifestdata,JSON,indent=4)
    
    ptcl.seek(TXBTableOffset + 4*TXBCount)
    endfile = ptcl.read()
    
    reader.seek(0)
    startfile = reader.read_bytes(48)
    
    OUTPUTPATH5 = os.path.join(OUTPUTDIR,"end.dat")
    OUTPUTPATH6 = os.path.join(OUTPUTDIR,"start.dat")
    
    end = open(OUTPUTPATH5,"wb")
    start = open(OUTPUTPATH6,"wb")
    end.write(endfile) 
    end.close()
    start.write(startfile)
    start.close()
    JSON.close()
    if len(IDLIST)!=0:
        OUTPUTPATH6 = os.path.join(OUTPUTDIR,"ID List.txt")
        txtfile = open(OUTPUTPATH6,"w")
        for txt in range(len(IDLIST)):
            txtfile.write('\n')
            txtfile.write(IDLIST[txt][1])
            txtfile.write(" : ")
            txtfile.write(str(IDLIST[txt][0]))
            txtfile.write('\n')
    
                
                
                
def repack(FilePath):
        
    if not os.path.exists(os.path.join(FilePath,"manifest.json")):
        print ("nah")
    else:
        MANIFEST = open(os.path.join(FilePath,"manifest.json"),"r")
        data = json.load(MANIFEST)
        pcount = data.get("Particle Count",0)
        ocount = data.get("OME Count",0)
        tcount = data.get("TXB Count",0)
        files = data.get("Files",[])
        
        ptclfiles = [name for name in files if name.endswith('.ptcl')]
        omefiles = [name for name in files if name.endswith('.OME')]
        txbfiles = [name for name in files if name.endswith('.TXB')]
        print(omefiles)
        
        Count = pcount+tcount+ocount
        tfcount =0
        ofcount =0
        pfcount =0
        TXBS = []
        OMES = []
        PTCLS = []
        endstart = []
        for txb in sorted(txbfiles,key=lambda x: int(x.split('.')[0])):
            
            txbdata = open(os.path.join(FilePath,txb),"rb")
            TXBS.append(txbdata.read())
            print(txb)
                
        for ome in sorted(omefiles,key=lambda x: int(x.split('.')[0])):
            
            ofcount+=1
            omedata = open(os.path.join(FilePath,ome),"rb")
            print(ome)
            OMES.append(omedata.read())
            
        for ptcl in ptclfiles:
            
                
            ptcldata = open(os.path.join(FilePath,ptcl),"rb")
            PTCLS.append(ptcldata.read())
            print(ptcl)
                
        
        end = open(os.path.join(FilePath,"end.dat"),"rb")
        enddata = end.read()
        
        start = open(os.path.join(FilePath,"start.dat"),"rb")
        startdata = start.read()
        
        endstart.append(startdata)
        endstart.append(enddata)
        
        writer = BinaryReader()
        writer.write_bytes(endstart[0])
        tableoffset = writer.pos()
        writer.pad(32)
        
        pPointers = []
        oPointers = []
        tPointers = []
        
        for wrte1 in range(len(PTCLS)):
            pPointers.append(writer.pos()-48)
            writer.write_bytes(PTCLS[wrte1])
        for wrte2 in range(len(OMES)):
            oPointers.append(writer.pos()-48)
            writer.write_bytes(OMES[wrte2])
        for wrte3 in range(len(TXBS)):
            tPointers.append(writer.pos()-48)
            writer.write_bytes(TXBS[wrte3])
        
        pTable = writer.pos()
        
        for p1 in range(len(PTCLS)):
            writer.write_uint32(pPointers[p1])
            
        oTable = writer.pos()
        for p2 in range(len(OMES)):
            writer.write_uint32(oPointers[p2])
            
        tTable = writer.pos()
        for p3 in range(len(TXBS)):
            writer.write_uint32(tPointers[p3])
            
        tablend = writer.pos()
        writer.write_bytes(endstart[1])
        
        writer.seek(tableoffset)
        writer.write_uint32(pTable-48)
        writer.write_uint32(len(PTCLS))
        writer.write_uint32(oTable-48)
        writer.write_uint32(len(OMES))
        writer.write_uint32(tTable-48)
        writer.write_uint32(len(TXBS))
        
        writer.seek(32)
        writer.write_uint32(tablend+4)
        writer.seek(20)
        writer.write_uint32(tablend-48)
        
        PTCLCONT = open(os.path.splitext(os.path.basename(FilePath))[0]+".dat","wb")
        
        PTCLCONT.write(writer.buffer())
        
        input("Enter to exit")
        
                
        
def main():
    FilePaths = sys.argv[1:]
    for FilePath in FilePaths:
        if os.path.isdir(FilePath):
            repack(FilePath)
        elif os.path.isfile(FilePath):
            extract(FilePath)

if __name__ == "__main__":
    main()
    