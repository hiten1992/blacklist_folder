# Note 		: 	This python script is used to download the blacklist websites
#		 		tar file. Then untar that file. Further copy the "domains" file
#		 		data from their respective subfolders to a new location.
#
# Author	:	Hiten Aggarwal
# Date		:	14-May-2021
################################################################################

import os
import time
import sys
import re
import hashlib


# This is the Path where the tar file will be extracted
path  = '/tmp'

dirName = path + '/blacklists/'

# This is the new path where the domains.txt files will created under their subfolders
newPath = '/var/unbound/blacklist/'

# This is the path from where we will read the domains file of the subfolders present in it
custom_blacklist_folder='/var/unbound/custom_blacklist/'

# This is the path where all the data from all the domains.txt files will be stored read from "custom_blacklist_folder" path
blacklistConf='/var/unbound/conf.d/blacklist.conf'

#print(blacklistConf)

os.getcwd()
#print(os.getcwd())
os.chdir(path)
#print(os.getcwd())

#check blacklists.tar.gz exists or not remove if exist
if os.path.exists(path+'/blacklists.tar.gz'):
    os.system('rm -rf '+ path + '/blacklists.tar.gz')

if os.path.exists(path+'/blacklists'):
    #print("111")
    os.system('rm -rf '+ path + '/blacklists')

if os.path.exists(newPath):
    #print("222")
    os.system('sudo rm -rf '+ newPath + '*')
    
if os.path.exists(blacklistConf):
    #print("333")
    os.system('rm '+ blacklistConf)

#download blacklist tar from ftp
#os.system('wget ftp://ftp.univ-tlse1.fr/pub/reseau/cache/squidguard_contrib/blacklists.tar.gz')
os.system('wget http://54.82.96.79/blacklists.tar.gz')

#extract tar into tmp blacklist dir
os.system('tar xzf blacklists.tar.gz')

#'v' is to display the output of untar process
os.system('tar xvzf blacklists.tar.gz')

def remove_duplicates():
    output_file_path = '/var/unbound/conf.d/blacklist_temp.conf'
    
    completed_lines_hash = set()
    
    output_file = open(output_file_path, "w")
    
    print("\nRemoving duplicate domains. Please wait..") 
    
    for line in open(blacklistConf, "r"):
    	hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
    	if hashValue not in completed_lines_hash:
    		output_file.write(line)
    		completed_lines_hash.add(hashValue)
    output_file.close()
    
    os.system('rm /var/unbound/conf.d/blacklist.conf')
    os.system('mv /var/unbound/conf.d/blacklist_temp.conf' + ' ' + '/var/unbound/conf.d/blacklist.conf')
    print("\nDone.\n")

def create_blacklist_Conf():
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    
    blacklist_file = open(blacklistConf, 'a+')
    
    blacklist_file.write("server:\n")
    
    # decalring the regex pattern for IP addresses
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    
    print("\nCreating blacklist.conf file. Please wait...")
    
    for file in os.listdir(custom_blacklist_folder):
        d = os.path.join(custom_blacklist_folder, file)
        if os.path.isdir(d):
           
            # This prints the subfolders with full path
            #print(d)
            
		    # This line prints only subfolder names
            #print(file)
		    
            for (dirpath, dirnames, filenames) in os.walk(d):
                listOfFiles += [os.path.join(dirpath, file) for file in filenames]
                for elem in filenames:
                    if elem == "domains.txt":
                        filePath=d + '/' + elem
                        #print(filePath)
                        with open(filePath) as fh:
                           string = fh.readlines()
                           
                        # extracting the IP addresses
                        for line in string:
                            line = line.rstrip()
                            result = pattern.search(line)
                            if result == None:
                                # ~ print(line)
                                # ~ time.sleep(1)
                                ModifiedData= line + '\n'
                                blacklist_file.write(ModifiedData)
    blacklist_file.close()
    print("\nDone.\n")

def main():
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    
    # decalring the regex pattern for IP addresses
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    
    print("\nProcessing blacklist folders. Please wait...")
    
    for file1 in os.listdir(dirName):
        d = os.path.join(dirName, file1)
        if os.path.isdir(d):
           
           # This prints the subfolders with full path
           #print("directory : ",d)
           #print("\n")
           # This line prints only subfolder names
           #print("subfolders : ")
           #print(file1)
           #print("\n")
		   
           createFolder='mkdir '+ newPath + file1
           
           # print(createFolder)
           os.system(createFolder)
           
           #print("\n")
           #print("file name 1 : ")
           #print(file1);
           
           for (dirpath, dirnames, filenames) in os.walk(d):
               listOfFiles += [os.path.join(dirpath, file2) for file2 in filenames]
               for elem in filenames:
                   #print("\n")
                   #print("elem : ")
                   #print(elem)
                   #print("\n")
                   #print("File name 2 : ")
                   #print(file1)
                   
                   filePath=d + '/' + elem
                   WriteFilePath=newPath + file1 + '/' + elem + '.txt'
                   #print("\n")
                   #print("file name 3 : ")
                   #print(file2)
                   #print("\n")
                   #print("\nWrite path")
                   #print(WriteFilePath)
                   #print("\n")
                   if elem == "domains":
                       domain_file = open(WriteFilePath, 'a')
                       
                       with open(filePath) as fh:
                          string = fh.readlines()
                      
                       # extracting the IP addresses
                       for line in string:
                           line = line.rstrip()
                           result = pattern.search(line)
                           if result == None:
                               #print(line)
                               #time.sleep(0.01)
                               ModifiedData="local-zone:" + ' ' + line + ' ' + "always_nxdomain" + '\n'
                               domain_file.write(ModifiedData)
                               
                               #time.sleep(1)
                       
                       domain_file.close()
    
    print("\nProcessing of blacklist folders is completed.")
    
    create_blacklist_Conf()
    remove_duplicates()
    
if __name__ == '__main__':
    main()
