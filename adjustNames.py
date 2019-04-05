import glob,os,sys,time,json
from datetime import datetime
import PIL.ExifTags,PIL.Image
from subprocess import check_output
from datetime import timedelta

def getExif(img):
    exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
    exif['UserComment'] = ''
    return exif

fp = sys.argv[1]
if fp[-1] == '/' or fp[-1] == '\\':
    fp = fp[:-1]
fp = fp.replace("\\","/")

fl = []
if os.path.isdir(fp):
    fl = glob.glob(fp+"/*")
elif os.path.isdir(fp):
    fl = sys.argv[2:]
else:
    print 'not found : ' + fp

nfl = []
for file in fl:
    file = file.replace("\\","/")
    if '.jpg' == file[-4:].lower() or '.mp4' == file[-4:].lower() or '.mov' == file[-4:].lower():
        ext = file[-4:].lower()
        print file
        ctime = None
        print '\tSearching exif...'
        try:
            img = PIL.Image.open(file)
            md = getExif(img)
            img.close()
            ctime = md['DateTimeOriginal']
        except Exception as e:
            print "\tcould not get creation time from exif ", e
        if ctime != None:
            fs="%Y:%m:%d %H:%M:%S"
            ctime=time.mktime(time.strptime(ctime, fs))
        
        if ctime == None:
            print '\tSearching stream data...'
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json','-show_format', '-show_streams' ,file ]
 
            try:
    
                out = check_output(cmd)
                md = json.loads(out)
     
                ctime = md['streams'][0]['tags']['creation_time']
            except Exception as e:
                print "\tcould not get creation time from ffprobe ", e
        
            if ctime != None:
                ctime =ctime.split('.')[0]

                fs="%Y-%m-%dT%H:%M:%S"
                ctime=time.mktime(time.strptime(ctime, fs))
        print "\tctime:",ctime

        if ctime != None:
            
            date_time = datetime.fromtimestamp(ctime) 
            #time zone correction:
            date_timenew = date_time - timedelta(hours=0)
            
            d = date_timenew.strftime("%Y%m%d_%H%M%S")
            d1 = date_time.strftime("%Y-%m-%d_%H:%M:%S")
            d2 = date_timenew.strftime("%Y-%m-%d_%H:%M:%S")
            
            if os.path.isfile(fp+'/'+d + ext): 
                n = 0
                while os.path.isfile(fp+'/'+d + '_'+str(n)+ ext):
                    n+=1
                
                newfile =  d + '_'+str(n)+ ext
            else:
                newfile =  d +  ext
            if newfile != file:
                
                #print d1+ ' -> ' +d2 
                #print '\t'+newfile
                nfl.append(fp+'/'+newfile)
                #print '\t'+d1
           
                print '\tOriginal: ' +file +'\n\tNew:      '+ fp+'/'+newfile
                os.rename(file,fp+'/'+newfile)
            else:
                print '\tsame name'
nfl = sorted(nfl)
for f in nfl:
    print f