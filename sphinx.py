#!/usr/bin/env python3.4

#Pocket Sphinx Installer

import os
import tarfile

def main():
    if os.getuid() != 0:
        print("This needs to be ran as root")
        return False
        
    download = [
        "http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/US%20English%20Generic%20Acoustic%20Model/cmusphinx-en-us-5.2.tar.gz/download",
        "http://sourceforge.net/projects/cmusphinx/files/sphinxbase/5prealpha/sphinxbase-5prealpha.tar.gz/download",
        "http://sourceforge.net/projects/cmusphinx/files/pocketsphinx/5prealpha/pocketsphinx-5prealpha.tar.gz/download"
    ]
    
    print("Only Ubuntu or systems with apt-get automatically install dependencies.")
    print("You can manually install \"bison autoconf libtool automake python-dev swig python-pocketsphinx pocketsphinx-hmm-wsj1 pocketsphinx-lm-wsj\"")
    input("Press enter to continue")
    
    os.system("mkdir /tmp/Lir_Downloads")
    
    for f in download:
        if not os.path.exists("/tmp/Lir_Downloads/"+f.split("/")[-2].replace(".tar.gz","")):
            print("Downloading",f)
            os.system("wget "+f+" -O /tmp/Lir_Downloads/"+f.split("/")[-2])
            with tarfile.open("/tmp/Lir_Downloads/"+f.split("/")[-2],"r:gz") as tar:
                tar.extractall("/tmp/Lir_Downloads/"+f.split("/")[-2].replace(".tar.gz",""))
        
    #install sphinxbase
    os.system("mkdir /tmp/Lir_Downloads/recordings")
    os.system("cp arctic20.transcription /tmp/Lir_Downloads/recordings")
    os.system("cp arctic20.fileids /tmp/Lir_Downloads/recordings")
    os.chdir("/tmp/Lir_Downloads/sphinxbase-5prealpha/sphinxbase-5prealpha")
    #TODO install for multiple OSs
    if input("Install dependcies using apt-get?").lower() == "y":
        os.system("sudo apt-get install bison autoconf libtool automake python-dev swig python-pocketsphinx pocketsphinx-hmm-wsj1 pocketsphinx-lm-wsj -f")
    os.system("./autogen.sh")
    os.system("make")
    os.system("make install")
    os.chdir("../../pocketsphinx-5prealpha/pocketsphinx-5prealpha/")
    os.system("./autogen.sh")
    os.system("make")
    os.system("make install")
    os.chdir("../../")
    
    #os.chdir("recordings")
    #
    #sen = []
    #with open("arctic20.transcription",'r') as f:
    #    data = f.read()
    #    data = data.split(" </s>")
    #    for d in data:
    #        print(d)
    #        try:
    #            d = d.split("<s> ")[1]
    #        except:
    #            pass
    #        sen.append(d)
    #sen = sen[:-1]
    #print(sen)
    
    #record samples to improve voice model
    #def command(x): 
    #    if x < 10:
    #        return "rec -r 16000 -q -b 16 -c 1 arctic_000"+str(x)+".wav 2>/dev/null"
    #    else:
    #        return "rec -r 16000 -q -b 16 -c 1 arctic_00"+str(x)+".wav 2>/dev/null"
    #print("Press <Control>+C after reading each sentence.")
    #for i in range(1,21):
    #    print(sen[i-1])
    #    os.system(command(i))
        
    #TODO Run commands to adapt model
    
    
if __name__ == "__main__":
    main()
