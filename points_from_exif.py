#!/usr/bin/python3

import os
import subprocess
import shlex
import sys
import getopt
import datetime
import re
from timeit import default_timer as timer

def getGPSData( filename ):
    command = "exiftool -s -s -s -gpsposition " + shlex.quote(filename)
    result = subprocess.getoutput( command )
    data = ""

    if result :
        exp = re.compile( r'\d+ deg \d+\' \d+\.\d+\" [NS], \d+ deg \d+\' \d+\.\d+\" [EW]' )

        if exp.match( result ):
            data = [x.strip() for x in result.split(',')]
        else:
            print( result )

    return data

def splitGPSString( gpsString ):
    result = [x.strip('deg\'"') for x in gpsString.split()]
    return list( filter(None, result) )

def dmsToDecimal( degrees, minutes, seconds, direction ):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'W' or direction == 'S':
        dd *= -1

    return dd;

def countFiles( path, filter ):
    fileCount = 0

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(filter.lower()) or file.endswith(filter.upper()):
                fileCount += 1
                print( "Counting Files: {0}  ".format(fileCount), end='\r', flush=True )

    return fileCount


if __name__ == "__main__":

    args = sys.argv[1:]

    sourceDir = "/home/pictures/"
    fileFilter = ".cr2"
    outputFile = "gpsdata.txt"
    appendToFile = False

    if args:
        opts, args = getopt.getopt(args,"d:af:o:h",["directory=","append","filter=","outfile=","help"])

        for cmd,param in opts:
            if cmd == "-d" or cmd == "--directory":
                sourceDir = param
            elif cmd == "-a" or cmd == "--append":
                appendToFile = True
            elif cmd == "-f" or cmd == "--filter":
                fileFilter = param
            elif cmd == "-o" or cmd == "--outfile":
                outputFile = param
            elif cmd == "-h" or cmd == "--help":
                print( "-d --directory  Source Verzeichnis\n-f --filter     Dateifilter\n-o --outfile    Ausgabedatei\n" )
                sys.exit()

    print( "==================================" )
    print( " Wopfi's GPS Extractor")    
    print( "==================================" )
    print( "" )
    print( "Directory: {}".format(sourceDir) )
    print( "Filter: {}".format(fileFilter) )
    print( "Output File: {}".format(outputFile) )
    print( "Output Mode: {}".format("append" if appendToFile else "overwrite") )
    print( "" )

    if appendToFile:
        textFile = open(outputFile, 'a')
    else:
        textFile = open(outputFile, 'w')

    if textFile:

        textFile.write( "filename,longitude,latitude,longitude_dec,latitude_dec\n" )

        maxFiles = countFiles( sourceDir, fileFilter )
        fileCount = 0
        gpsFiles = 0
        startTime = timer()

        for subdir, dirs, files in os.walk(sourceDir):
            for file in files:
                name,ext = os.path.splitext( file )

                if (ext == fileFilter.lower()) or (ext == fileFilter.upper()) and (name[0] != "."):
                    fileCount += 1
                    #print( os.path.join(subdir, file) )
                    gps = getGPSData( os.path.join(subdir, file) )

                    if gps != "":
                        #print( "{}, {}".format( gps[0], gps[1] ) )
                        gpsDMS = splitGPSString( gps[0] )
                        #print( gpsDMS )
                        gpsDD = []
                        gpsDD.append( dmsToDecimal( gpsDMS[0], gpsDMS[1], gpsDMS[2], gpsDMS[3] ) )
                        gpsDMS = splitGPSString( gps[1] )
                        #print( gpsDMS )
                        gpsDD.append( dmsToDecimal( gpsDMS[0], gpsDMS[1], gpsDMS[2], gpsDMS[3] ) )
                        #print( "{}, {}".format( gpsDD[0], gpsDD[1] ) )
                        gpsFiles += 1
                        textFile.write( "{},{},{},{},{}\n".format(os.path.join(subdir, file),gps[1],gps[0],gpsDD[1],gpsDD[0] ) )

                    timeLeft = ( timer() - startTime ) / fileCount * ( maxFiles - fileCount )
                    m, s = divmod(timeLeft, 60)
                    h, m = divmod(m, 60)
                    timeRemain = "{0:0>2.0f}:{1:0>2.0f}:{2:0>2.0f}".format(h,m,s)

                    print( "{0}/{1}/{2} {3:.1f}% {4}  ".format(fileCount,gpsFiles,maxFiles,fileCount/maxFiles*100,timeRemain), end='\r', flush=True )

    textFile.close();
    print( "\n" );
    print( "Finished\n" )
