"""====================================================================================================================
Program:    exif.py
Version:    1.2.0
Py Ver:     2.7
Purpose:    This program is designed to extract the EXIF metadata from an image, and output the results either to a 
            user-specified text file, or to the console window.
Depends:    argparse
            os
            PIL
Comments:   Original program concept code was found on YouTube:
            Programmer: DrapsTV
            Source:     https://www.youtube.com/watch?v=hY4WuX_KqUQ&list=WL&index=22)

            GPSInfo (latitude / longitude extraction and conversion) exif program attribution:
            Programmer: Eran Sandler
            Source:     https://gist.github.com/erans/983821
            
            Original code has been updated for expanded functionality.
            
Use:        > exif.py path\img.jpg
            > exif.py path\img.jpg [-GPS]
            > exif.py path\img.jpg [-GPS] [-o path\output.txt]
            > exif.py path\img.jpg [-o path\output.txt]
      
Reference:  Metadata tables and key descriptions:
            General:    http://www.exiv2.org/tags.html
            GPS:        http://www.opanda.com/en/pe/help/gps.html#GPSSpeedRef
_______________________________________________________________________________________________________________________
UPDATE LOG:
Date        Programmer      Version     Update
18.11.14    DrapsTV         1.0.0       Written
20.12.15    J. Berendt      1.1.0       Minor coding updates.
                                        Added optional argument to find and export GPS data only.
                                        Added progess comments.
26.02.16    J. Berendt      1.2.0       Updated argparser.
                                        Added company / copyright / attribution information.
                                        Added check to ensure file exists before processing.
                                        Added error handling.
                                        Updated progess comments.
                                        Simplified code where applicable.
            E. Sandler via GitHub       Added E.Sandler's functions for latitude/longitude decimal degrees conversion.
===================================================================================================================="""

import  os.path
import  argparse
from    PIL             import  Image
from    PIL.ExifTags    import  TAGS
from    PIL.ExifTags    import  GPSTAGS

#----------------------------------------------------------------------------------------------------------------------------------------------------
#VARIABLE / CONSTANT DECLARATIONS
C_PROGNAME      = 'exif.py'
C_VERSION       = '1.2.0'
C_COMPANYNAME   = '73rd street development'
C_DESC          = 'program designed to extract exif data from image files'
C_COPYRIGHT     = '2016 | ' + C_COMPANYNAME
C_ATTRIB        = 'copyright only applies to this program as a whole.\n\t\tfeel free to fork or modify the code; just remember to attribute credit.'
C_LINE          = '------------------------------'

#GPSInfo DICTIONARY
dGPSsub = dict()


#----------------------------------------------------------------------------------------------------------------------------------------------------
#FUNCTION TO TEST IF IMAGE EXISTS
def ImageExists(imgName):
    #TEST IF FILE EXISTS
    if os.path.exists(imgName): return True

    
#----------------------------------------------------------------------------------------------------------------------------------------------------
#GPSInfo CONVERSION: FUNCTION RETURNS THE VALUE, IF THEY KEY EXISTS
def GetIfExist(data, key):
    if key in data: return data[key]


#----------------------------------------------------------------------------------------------------------------------------------------------------
#GPSInfo CONVERSION: FUNCTION CONVERTS GPS EXIF TO DECIMAL LAT/LON
def ConvertToDegrees(value):

    #DEGREES
    d0  = value[0][0]
    d1  = value[0][1]
    d   = float(d0) / float(d1)

    #MINUTES
    m0  = value[1][0]
    m1  = value[1][1]
    m   = float(m0) / float(m1)

    #SECONDS
    s0  = value[2][0]
    s1  = value[2][1]
    s   = float(s0) / float(s1)

    #RETURN CALCULATION
    return d + (m / 60.0) + (s / 3600.00)

   
#----------------------------------------------------------------------------------------------------------------------------------------------------
#GPSInfo CONVERSION: FUNCTION GETS THE LATITUDE AND LONGITUDE VALUES FROM GPSInfo DICTIONARY
def GetLatLon(dGPSInfo):

    #INITIALISE VARIABLES
    lat = None
    lon = None

    #if 'GPSInfo' in dEXIF_data:
    if 'GPSInfo' in dGPSInfo:
        #CREATE GPSINFO DICTIONARY
        dGPSInfosub = dGPSInfo['GPSInfo']
        
        #GET LAT / LON VALUES
        gps_lat     = GetIfExist(dGPSInfosub, 'GPSLatitude')
        gps_lon     = GetIfExist(dGPSInfosub, 'GPSLongitude')
        gps_lat_ref = GetIfExist(dGPSInfosub, 'GPSLatitudeRef')
        gps_lon_ref = GetIfExist(dGPSInfosub, 'GPSLongitudeRef')

        #TEST FOR ALL PARTS
        if gps_lat and gps_lon and gps_lat_ref and gps_lon_ref:
            #CONVERT TO DECIMAL
            lat = ConvertToDegrees(gps_lat)
            lon = ConvertToDegrees(gps_lon)

            #DETERMINE N/S/E/W
            if gps_lat_ref != 'N': lat = (0 - lat)
            if gps_lon_ref != 'E': lon = (0 - lon)

    #RETURN VALUE
    return lat, lon

#----------------------------------------------------------------------------------------------------------------------------------------------------
#FUNCTION TO GET METADATA FROM IMAGE FILE
def GetMetaData(imgName, gps, out):

    #INITIALISE VARIABLES
    bGPSReq     = False
    bGPSFound   = False
    dData       = dict()

    try:
        #OPEN IMAGE
        print 'REM: opening image: (%s)' % (imgName)
        imgFile = Image.open(imgName)

        #CALL THE EXIF METHOD
        print 'REM: searching for metadata.'
        imgInfo = imgFile._getexif()

        #TEST IF THE FILE CONTAINS DATA
        if imgInfo:
            #CONFIRM METADATA FOUND
            print 'REM: metadata found.'
            #TEST USER REQUEST FOR GPS ONLY
            if gps:
                #SET USER GPS REQUEST FLAG
                bGPSReq = True
                print 'REM: extracting GPS metadata only.'
            else:
                print 'REM: extracting metadata.'
            
            #ITERATE THROUGH METADATA
            for (key, value) in imgInfo.items():
                keyname = TAGS.get(key, key)

                #TEST IF GPS ONLY
                if gps:
                    #TEST FOR GPS TAG
                    if keyname == 'GPSInfo':
                        #FLAG GPS AS FOUND
                        bGPSFound = True
                        #SETUP DICTIONARY
                        dGPS = dict()
                        #ITERATE THROUGH GPSInfo SUBKEYS
                        for k in value:
                            #EXTRACT SUBKEYS
                            subkey = GPSTAGS.get(k)
                            #ADD SUBKEY / VALUE TO DICTIONARY
                            dGPS[subkey] = value[k]

                        #STORE SUBKEYS TO DICTIONARY FOR PROCESSING
                        dGPSsub[keyname] = dGPS

                        #SEND GPS DATA FOR DECIMAL PROCESSING > STORE TO DICTIONARY
                        dData[keyname] = GetLatLon(dGPSsub)
                        
                        #CATCH IF USED DOES NOT OUTPUT TO FILE
                        if not out:
                            print keyname, '\t', GetLatLon(dGPSsub)
                            
                else:
                    #STORE ALL KEYS AND VALUES TO DICTIONARY
                    dData[keyname] = value

                    #CATCH IF USER DOES NOT OUTPUT TO FILE
                    if not out:
                        #PRINT OUTPUT TO CONSOLE
                        print '%s\t%s' % (str(keyname), str(value))

            #OUTPUT RESULT(S) TO FILE
            if out:
                print 'REM: saving result(s) to file: (%s)' % (out)
                #OPEN OUTPUT FILE
                with open(out, 'w') as f:
                    #ITERATE THROUGH DICTIONARY
                    for (key, value) in dData.items():
                        #PRINT RESULT(S) TO FILE
                        f.write( str(key) + '\t' + str(value) + '\n' )
                                        
        else:
            #NOTIFY USER NO METADATA WAS FOUND
            print 'REM: no metadata was found in this image.'
        
        #PRINT COMPLETION
        print 'REM: processing complete.\n'
        
        #WAS GPS DATA FOUND?
        if bGPSReq == True and bGPSFound == False:
            #NOTIFY USER NO GPS METADATA FOUND (IF IT WAS REQUESTED)
            print 'REM: no GPS metadata found in this file.'

    #HANDLE EXCEPTION ERROR
    except Exception as e:
      #PRINT ERROR
      print 'ERROR:- %s' % (e)

            
#----------------------------------------------------------------------------------------------------------------------------------------------------
#MAIN PROGRAM
def Main():
    
    #SETUP ARGUMENT PARSER FOR CONSOLE
    parser = argparse.ArgumentParser(C_DESC)
    parser.add_argument('img',help='path and filename of image to process')
    parser.add_argument('-gps', '-GPS', nargs='?', const=True, help='find and output GPS information only (switch)')
    parser.add_argument('-o', '--output', help='path and filename of the results file')

    #EXTRACT ARGS FROM PARSER
    args = parser.parse_args()
    
    #TEST FOR IMAGE ARGUMENT
    if args.img:
    
        #PRINT COMPANY / COPYRIGHT INFORMATION
        print '\n\n', C_LINE
        print 'progam name:\t%s'    % C_PROGNAME
        print 'version:\t%s'        % C_VERSION
        print 'description:\t%s'    % C_DESC
        print 'copyright:\t%s'      % C_COPYRIGHT
        print 'attribution:\t%s'    % C_ATTRIB
        print C_LINE, '\n\n'
        
        #TEST IF FILE EXISTS
        if ImageExists(args.img):
            #SEND ARGUMENTS FOR EXTRACTION
            GetMetaData(args.img, args.gps, args.output)
        else:
            #PRINT ERROR MESSAGE
            print 'ERROR:- this file does not exist (%s)' % (args.img)
            #EXIT PROGRAM AFTER ERROR
            exit()
    
    else:
        #PRINT PARSER MESSAGE
        print parser.useage


#----------------------------------------------------------------------------------------------------------------------------------------------------
#RUN PROGRAM
if __name__ == '__main__':
    #RUN MAIN
    Main()