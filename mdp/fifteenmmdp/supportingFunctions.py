import os
from django.core.files import File
import re
from datetime import datetime,timedelta
# import plotly.graph_objects as go
# import numpy as np

###################################################  Global Variables #######################################################################
checkTimeStamp = ['00','04','08','12','16','20']
statusCodes =  ['Uploaded' , 'Extracted' , 'Merged' , 'DateFiltered','Verified', 'MWHCreated', 'FictCreated' , 'FinalOutputCreated' ]

#############################################################################################################################################

def sortDateStrings(stringDateList) :
    stringDateList.sort(key=lambda date: datetime.strptime(date, "%d-%m-%y"))
    return stringDateList

###################################################  Global Functions #######################################################################

def extraCharHandler(value) :
    # Handles '*' , 'a' , 'z' , 'r' extra characters.
    while '*' in value:   
        value.remove('*')
    while 'z' in value:   
        value.remove('z')
    while 'a' in value:   
        value.remove('a')
    while 'r' in value:   
        value.remove('r')
    return value
    
def initialCharHandler(value) :
    # Handles 'aa' , 'rr' initials.
    if(value[0] == 'a' and value[1] == 'a') :
        value = value[2:]
        return value
    elif(value[0] == 'r' and value[1] == 'r') :
        value = value[2:]
        return value
    else :
        return value
    
def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def isNaN(num):
    return num != num

def changeToFloat(x) :
    if(isFloat(x)) :
        return float(x)
    else :
        return None

def isTwoDigitFloat(value):
    value = initialCharHandler(value)
    twoDigitFloatPattern = re.compile(r'^[0-9]{2}$')
    result = re.match(twoDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isSixDigitFloat(value):
    value = initialCharHandler(value)
    sixDigitFloatPattern = re.compile(r'^[+-][0-9]{2}\.[0-9]{2}$')
    result = re.match(sixDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False

def isSevenDigitFloat(value):
    value = initialCharHandler(value)
    sevenDigitFloatPattern = re.compile(r'^[0-9]{5}\.[0-9]$')
    result = re.match(sevenDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isSevenEightDigitFloat(value):
    value = initialCharHandler(value)
    sevenEightDigitFloatPattern = re.compile(r'^[+-]?[0-9]{4}\.[0-9]{2}$')
    result = re.match(sevenEightDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isDate(value) :
    datePattern = re.compile(r'^[0-9]{2}-[0-9]{2}-[0-9]{2}$')
    result = re.match(datePattern, value)
    if(result is None) :
        return False                                             
    try:
        datetime.strptime(value, "%d-%m-%y")
        return True
    except ValueError:
        return False


def isTime(value) :
    import time
    timePattern = re.compile(r'^[0-2][0-9][0-5][0-9]$')
    result = re.match(timePattern, value)
    if(result is None) :
        return False                                             
    try:
        time.strptime(value, '%H%M')
        return True
    except ValueError:
        return False
                                          
def isMeterNumberPattern(value) :
    meterNumberPattern = re.compile(r'^[A-Z]{2}-[0-9]{4}-[A-Z]$')
    result = re.match(meterNumberPattern, value)
    if result:
        return True
    else:
        return False
    
def isMeterIdPattern(value) :
    meterIdPattern = re.compile(r'^[A-Z]{2}-[0-9]{2}$')
    result = re.match(meterIdPattern, value)
    if result:
        return True
    else:
        return False

def isMeterNameUnique(nameList) :
    
    return(len(set(nameList)) == 1)

def isMeterDateConsecutive(dateList,startObj,endObj) :
    
    # if(dateList[0] != startObj or dateList[-1] != endObj) :
    #     return False

    for day in range((endObj-startObj).days+1) :
        if(dateList[day] != startObj+timedelta(days=day)) :
            return False

    return True

def getDfInfo(_weekList,_meterHeaderList) :
    informationDict = {}
    meterHeaderIndex = 0
    for weekHeaderIndex in range(len(_weekList)-1):
        informationDict[_weekList[weekHeaderIndex]] = []  # Makes a dictionary index with weekHeaderIndex
        while meterHeaderIndex < len(_meterHeaderList) and _weekList[weekHeaderIndex] < _meterHeaderList[meterHeaderIndex] < _weekList[weekHeaderIndex + 1]:
            informationDict[_weekList[weekHeaderIndex]].append(_meterHeaderList[meterHeaderIndex])
            meterHeaderIndex+=1
        informationDict[_weekList[weekHeaderIndex]].append(_weekList[weekHeaderIndex+1])
    return(informationDict)


#############################################################################################################################################


###################################################  Specific Functions #######################################################################

# ************************************************ Helps Extract *******************************************************
# No function yet

# ************************************************ Helps DateFilter *******************************************************

def meterHeaderCheckDate(rowList) :
    
    if(len(rowList) != 5) :

        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}

    if(not isDate(rowList[4])) :

        return {"message" : "Date format mismatch : "+ str(rowList[4]) +". Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

def weekHeaderCheckDate(rowList) :
    
    if(len(rowList) != 11) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}

    if(not isTime(rowList[2])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[2]) +". Line number : ", "status" : False}
    if(not isTime(rowList[7])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[7]) +". Line number : ", "status" : False}
    if(not isDate(rowList[5])) :
        return {"message" : "Date format mismatch : "+ str(rowList[5]) +". Line number : ", "status" : False}
    if(not isDate(rowList[10])) :
        return {"message" : "Date format mismatch : "+ str(rowList[10]) +". Line number : ", "status" : False}
    
     # If I reach here, I am pretty sure that both the dates are in correct format.
    if(datetime.strptime(rowList[10], "%d-%m-%y") < datetime.strptime(rowList[5], "%d-%m-%y")) :  
        return {"message" : "Date format mismatch. End date smaller than start date. Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

# ************************************************ Helps Validate *******************************************************
def mainMeterDataCheck(rowList) :

    #  len(rowList) must be odd, if timestamp not = '20'

    if(rowList[0] == '20') :
        if(not (len(rowList) >= 33)) :
            return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : " , "status" : False }
        
        for rowListIndex in range(1,len(rowList)-1) :
            if(rowListIndex % 2 == 1) :
                if(not isTwoDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in frequency data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
            else :
                if(not isSixDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in active energy data : "+ str(rowList[rowListIndex]) +". Line number : " , "status" : False }
                
        return {"message" : "All checked." , "status" : True}

    else :
        if(not (len(rowList) == 33)) :
            return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
        for rowListIndex in range(1,len(rowList)) :
            if(rowListIndex % 2 == 1) :
                if(not isTwoDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in frequency data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
            else :
                if(not isSixDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in active energy data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
        
        return {"message" : "All checked." , "status" : True}

def meterHeaderCheck(rowList) :
    
    if(len(rowList) != 5) :

        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not (isMeterNumberPattern(rowList[0]) and isSevenDigitFloat(rowList[1]) and isSevenDigitFloat(rowList[2]) and isSevenDigitFloat(rowList[3]))) : 

        return {"message" : "Non-uniformity in Meter no./ Active energy/ Reactive high/Reactive low. Line number : ", "status" : False}
    if(not isDate(rowList[4])) :

        return {"message" : "Date format mismatch : "+ str(rowList[4]) +". Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}
   
def weekHeaderCheck(rowList) :
    
    if(len(rowList) != 11) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not (rowList[0]=='WEEK' and rowList[1]=='FROM' and rowList[3]=='HRS' and rowList[4]=='OF' and rowList[6]=='TO'and rowList[8]=='HRS'and rowList[9]=='OF')) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not isTime(rowList[2])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[2]) +". Line number : ", "status" : False}
    if(not isTime(rowList[7])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[7]) +". Line number : ", "status" : False}
    if(not isDate(rowList[5])) :
        return {"message" : "Date format mismatch : "+ str(rowList[5]) +". Line number : ", "status" : False}
    if(not isDate(rowList[10])) :
        return {"message" : "Date format mismatch : "+ str(rowList[10]) +". Line number : ", "status" : False}
     # If I reach here, I am pretty sure that both the dates are in correct format.
    if(datetime.strptime(rowList[10], "%d-%m-%y") < datetime.strptime(rowList[5], "%d-%m-%y")) :  # <= changed to <
        return {"message" : "Date format mismatch. End date smaller than start date. Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

# ************************************************ Helps Real Meter MWH Creation *****************************************

# ************************************************ Helps Fictitious Meter MWH Creation *****************************************

def decideSpace(spaceValue,stringToCheck) :
    spaceOffset = max(spaceValue,len(stringToCheck)+1)
    return spaceOffset - len(stringToCheck)

#############################################################################################################################################

################################################### All RealMeters here. List of fict meters : #############################################

# def getAnyMeter() : 
#     # [{'Loc_Id': 'FK-01', 'Meter_No': 'ER-1649-A', 'ctr': '500', 'ptr': '3636.3636'} ,{'Loc_Id': 'FK-02', 'Meter_No': 'ER-1646-A', 'ctr': '500', 'ptr': '3636.3636'}]
#     realMeterInfo = []
#     masterData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/master.dat', "r")
#     masterDataList = masterData.readlines()
#     masterData.close()
#     for elem in masterDataList :
#         if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
#             # print(elem.split())
#             realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3] })

#     # print(realMeterInfo)

#     def getMeterInfoById(Loc_Id) :
        
#         meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]  
        
#         if(len(meterDetails) < 1) :
#             print(Loc_Id + " not found in master.dat")
#             return None
#         else :
#             return(meterDetails[0])
        
            
            
#     def getMeterInfoByNo(Meter_No) :
        
#         meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
        
#         if(len(meterDetails) < 1) :
#             return None
#         else :
#             return(meterDetails[0])

#     ################################################### All FictMeters here. List of fict meters : #############################################

#     # [{'Loc_Id': 'FK-91', 'Fict_Meter_No': 'FKK-TOT-LN'} ,{'Loc_Id': 'FK-93', 'Fict_Meter_No': 'FKK-TOT-CL'}]
#     fictMeterInfo = []
#     fictInfoData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FICTMTRS.dat', "r")

#     fictInfoDataList = fictInfoData.readlines()
#     fictInfoData.close()
#     for elem in fictInfoDataList :
#         if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
#             # print(elem.split())
#             fictMeterInfo.append({"Loc_Id" : elem.split()[0] , "Fict_Meter_No" : elem.split()[1] })


#     def getFictMeterInfoById(Loc_Id) :

#         fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Loc_Id'] == Loc_Id]
                
#         if(len(fictMeterDetails) < 1) :
#             print(Loc_Id + " not found in FICTMTRS.dat")
#             return None
#         else :
#             return(fictMeterDetails[0])

#     ################################################### Search any meter here. #################################################################

#     def searchMeterNumber(Loc_Id) : # Any meter real or fictitious. Returns meter number.
#         meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]
#         fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Loc_Id'] == Loc_Id]
#         if(len(meterDetails) != 0) : return meterDetails[0]['Meter_No']
#         if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Fict_Meter_No']
#         return "FileNotFound"

#     def searchMeterId(Meter_No) : # Any meter real or fictitious. Returns meter Loc_Id.
#         meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
#         fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Fict_Meter_No'] == Meter_No]
#         if(len(meterDetails) != 0) : return meterDetails[0]['Loc_Id']
#         if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Loc_Id']
#         # return None
#         return "Loc_Id not found"