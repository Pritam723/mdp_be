import os
from .models import AllMeterFiles,FinalOutputFile
from django.core.files import File
from django.conf import settings
from .supportingFunctions import *
import pandas as pd
import json
from datetime import time,timedelta,datetime

# For now it only returns meter number, however, we can take any data of any meter with help of this function.
def getAllMeterDetails(path, Loc_Id) :

    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)

    ################################################### All RealMeters here. List of Real meters : #############################################

    # [{'Loc_Id': 'FK-01', 'Meter_No': 'ER-1649-A', 'ctr': '500', 'ptr': '3636.3636'} ,{'Loc_Id': 'FK-02', 'Meter_No': 'ER-1646-A', 'ctr': '500', 'ptr': '3636.3636'}]
    realMeterInfo = []
    masterData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/master.dat', "r")
    masterDataList = masterData.readlines()
    masterData.close()
    for elem in masterDataList :
        if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
            # print(elem.split())
            realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3] })

    # print(realMeterInfo)

    def getMeterInfoById(Loc_Id) :
        
        meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]  
        
        if(len(meterDetails) < 1) :
            print(Loc_Id + " not found in master.dat")
            return None
        else :
            return(meterDetails[0])
        
            
            
    def getMeterInfoByNo(Meter_No) :
        
        meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
        
        if(len(meterDetails) < 1) :
            return None
        else :
            return(meterDetails[0])
    
    ################################################### All FictMeters here. List of fict meters : #############################################
    
    # [{'Loc_Id': 'FK-91', 'Fict_Meter_No': 'FKK-TOT-LN'} ,{'Loc_Id': 'FK-93', 'Fict_Meter_No': 'FKK-TOT-CL'}]
    fictMeterInfo = []
    fictInfoData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FICTMTRS.dat', "r")
    
    fictInfoDataList = fictInfoData.readlines()
    fictInfoData.close()
    for elem in fictInfoDataList :
        if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
            # print(elem.split())
            fictMeterInfo.append({"Loc_Id" : elem.split()[0] , "Fict_Meter_No" : elem.split()[1] })


    def getFictMeterInfoById(Loc_Id) :

        fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Loc_Id'] == Loc_Id]
                
        if(len(fictMeterDetails) < 1) :
            print(Loc_Id + " not found in FICTMTRS.dat")
            return None
        else :
            return(fictMeterDetails[0])

    ################################################### Search any meter here. #################################################################
    
    def searchMeterNumber(Loc_Id) : # Any meter real or fictitious. Returns meter number.
        meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]
        fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Loc_Id'] == Loc_Id]
        if(len(meterDetails) != 0) : return meterDetails[0]['Meter_No']
        if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Fict_Meter_No']
        return "Meter_No not found"

    def searchMeterId(Meter_No) : # Any meter real or fictitious. Returns meter Loc_Id.
        meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
        fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Fict_Meter_No'] == Meter_No]
        if(len(meterDetails) != 0) : return meterDetails[0]['Loc_Id']
        if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Loc_Id']
        # return None
        return "Loc_Id not found"

    #############################################################################################################################################


    return searchMeterNumber(Loc_Id)



def getRealMeterFullData(path, Meter_No) :

    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)

    ################################################### All RealMeters here. List of Real meters : #############################################

    # [{'Loc_Id': 'FK-01', 'Meter_No': 'ER-1649-A', 'ctr': '500', 'ptr': '3636.3636'} ,{'Loc_Id': 'FK-02', 'Meter_No': 'ER-1646-A', 'ctr': '500', 'ptr': '3636.3636'}]
    realMeterInfo = []
    masterData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/master.dat', "r")
    masterDataList = masterData.readlines()
    masterData.close()
    for elem in masterDataList :
        if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
            # print(elem.split())
            realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3], "POI" : " ".join(elem.split()[4:]) })

    # print(realMeterInfo)

    def getMeterInfoById(Loc_Id) :

        meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]  

        if(len(meterDetails) < 1) :
            print(Loc_Id + " not found in master.dat")
            return None
        else :
            return(meterDetails[0])



    def getMeterInfoByNo(Meter_No) :

        meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]

        if(len(meterDetails) < 1) :
            return None
        else :
            return(meterDetails[0])


    return getMeterInfoByNo(Meter_No)


    ################################################### All RealMeters here. List of Real meters : #############################################