from pathlib import Path
import pandas as pd
import os
from django.conf import settings
from .models import AllMeterFiles,ValidatedFile
from .supportingFunctions import *
from datetime import datetime,timedelta


def validateFile(path,_meterData) :

    print("i am in validateFile " + path)
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path) #Later "DateFiltered File" path is added

    # if not os.path.exists(meterFileMainFolder +'/Validated File(Copy)'):   # Not required. Because file is taken from "DateFiltered File" Folder.
    #     os.makedirs(meterFileMainFolder + '/Validated File(Copy)')
    if not os.path.exists(meterFileMainFolder +'/Validated File'):
        os.makedirs(meterFileMainFolder + '/Validated File')

    # All RealMeters here

    realMeterInfo = []
    allMeterNumbers = []
    masterData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/master.dat', "r")
    masterDataList = masterData.readlines()
    masterData.close()
    for elem in masterDataList :
        if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
    #         print(elem.split())
            allMeterNumbers.append(elem.split()[1])
            realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3] })

    # print(realMeterInfo)
    # print(allMeterNumbers)
   
    data = pd.read_csv(meterFileMainFolder+'/DateFiltered File/DateFilteredFile.npc', header = None)
    dfSeries = pd.DataFrame(data)
    df = dfSeries[0]
    print(df)

    errorLine = 0
    errorList = []
    # eofCheckFlag = 0

    if(df[len(df)-1] != "EOF") :
        errorList.append("Structural error. No EOF.")
    #     return(False)    





    weekList = []
    meterHeaderList = []
    meterNamesList = []

    try :
        
        for i in range(len(df)-1) : # So EOF should not come at all.
            errorLine = i
            rowList = df[i].split()
            rowListNext = df[i+1].split()

            rowList = extraCharHandler(rowList)
            rowListNext = extraCharHandler(rowListNext)

            if(rowList[0] in checkTimeStamp or isMeterNumberPattern(rowList[0]) or rowList[0] == "WEEK" or rowList[0] == "EOF") :

                if(rowList[0] == "WEEK"):
                    if(isMeterNumberPattern(rowListNext[0])) : weekList.append(i)
                    else : errorList.append("1.Structural Error. Line :"+str(errorLine+1)+","+str(errorLine+2))

                if(isMeterNumberPattern(rowList[0])):
                    if(rowListNext[0] in checkTimeStamp) : meterHeaderList.append(i)
                    else : errorList.append("2.Structural Error. Line :"+str(errorLine+1)+","+str(errorLine+2))


                if(rowList[0] == "EOF") : 

                    errorList.append("Structural error. Unexpected EOF. Line number : " + str(errorLine+1))


            else :
                errorList.append("Error at line : "+str(errorLine+1)+" length is "+str(len(rowList[0]))+ ". >> "+str(" ".join(rowList)))

        weekList.append(len(df)-1) #EOF index must be added
        
            
        informationDict = getDfInfo(weekList,meterHeaderList)
    #     print(informationDict)

        
    #     ###############################################################################################################


        for weekListIndex in weekList[:-1] :  # Will not take the EOF's index
            errorLine = weekListIndex
            weekHeaderDataRaw = df[weekListIndex] # "WEEK FROM 0000 HRS OF 07-12-20 TO 1033 HRS OF 14-12-20"
            weekHeaderData = weekHeaderDataRaw.split()
            weekHeaderData = extraCharHandler(weekHeaderData)
            validateWeekHeader = weekHeaderCheck(weekHeaderData)
            if(not validateWeekHeader['status']) : errorList.append(str(validateWeekHeader['message']) + str(errorLine+1))
                
            weekStartDate_object = datetime.strptime(weekHeaderData[5], "%d-%m-%y")
            weekEndDate_object = datetime.strptime(weekHeaderData[10], "%d-%m-%y")
            
            print("For weekheader"+str(weekListIndex)+" : "+str(informationDict[weekListIndex]))
            # For weekheader0 : [1, 8, 15, 22, 29, 36, 43, 50, 54]
            
            meterNames = [df[x].split()[0] for x in informationDict[weekListIndex][:-1]]  # Must be unique
            meterDates = [datetime.strptime(df[x].split()[4], "%d-%m-%y") for x in informationDict[weekListIndex][:-1]] # Must be consequtive in the range of weekStartDate_object to weekEndDate_object

            if(not (isMeterNameUnique(meterNames) and isMeterDateConsecutive(meterDates,weekStartDate_object,weekEndDate_object))) :
                print("I am error at "+ str(weekListIndex))
                errorList.append("Different meter names/non-consecutive dates inside same WEEK Header :{{ " + str(df[weekListIndex]) + " }}. Line number : " + str(errorLine+1))
                continue
            
            # if(meterNames[0] in meterNamesList) :
            #     errorList.append("Same meter name already exists. Line number : " + str(errorLine+1))
            #     continue
            
            meterNamesList.append(meterNames[0])
            
            for k in range(len(informationDict[weekListIndex])-2): 
                # Will run for [1,21,31,not 41,not 54] i.e. 2 times less. 
                # Coz no need to check the last chuck
                
                errorLine = informationDict[weekListIndex][k]

                meterHeaderDataRaw = df[informationDict[weekListIndex][k]] # "NP-5851-A    97845.9    35371.6    00136.0    07-12-20"
                meterHeaderDataNextRaw = df[informationDict[weekListIndex][k+1]]
                meterHeaderData = meterHeaderDataRaw.split() 
                meterHeaderDataNext = meterHeaderDataNextRaw.split() 
                meterHeaderData = extraCharHandler(meterHeaderData)
                meterHeaderDataNext = extraCharHandler(meterHeaderDataNext)
                
                validateMeterHeader = meterHeaderCheck(meterHeaderData)
                if(not validateMeterHeader['status']) : errorList.append(str(validateMeterHeader['message'])+str(errorLine+1))

                for line in range(informationDict[weekListIndex][k]+1,informationDict[weekListIndex][k+1]):
                    
                    errorLine = line

                    meterMainDataRaw = df[line]
                    meterMainData = meterMainDataRaw.split()
                    meterMainData = extraCharHandler(meterMainData)
                    validateMeterData = mainMeterDataCheck(meterMainData)  
                    # This need to be modified. Because now just skip the last chuck
                    # And for each chuck we must ensure full data availability.
                    if(not validateMeterData['status']) : errorList.append(str(validateMeterData['message'])+str(errorLine+1))
                
                errorLine = informationDict[weekListIndex][k+1]
                validateMeterHeader = meterHeaderCheck(meterHeaderDataNext)
                if(not validateMeterHeader['status']) : errorList.append(str(validateMeterHeader['message'])+str(errorLine+1))            
                
                print("Changing meter header")

            print("Changing Week header")
        print("-----------------------------------------------------------------")

    except Exception as e :
        errorList.append("Unhandled generic issue : " + str(e) + ". Line no : " + str(errorLine+1))

    finally:
        # print(set(allMeterNumbers) - set(meterNamesList)) # For these meters we do not have any data
        # print(set(meterNamesList) - set(allMeterNumbers)) # These meter names are not defined in master.dat
        # for err in errorList :
        #     print(err)
        # if(len(errorList) == 0) :
        #     print("Proceed")
        # else :
        #     print("Stop")
        if(len(errorList) != 0) :
            return errorList
        else :
            # dateFixedDf.to_csv(meterFileMainFolder+'/DateFiltered File(Copy)/DateFilteredFile.npc', header=False, index=None)
            # dateFixedDf.to_csv(meterFileMainFolder+'/DateFiltered File/DateFilteredFile.npc', header=False, index=None)

            if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 3)) :
                print("New validatedFileId added")
                local_file = open(meterFileMainFolder+'/DateFiltered File/DateFilteredFile.npc',"rb") # Latest DateFiltered File will be picked from this folder.
                validatedFileObject = ValidatedFile.objects.create(fileName = 'ValidatedFile.npc', filePath = os.path.join("meterFile",path,"Validated File/ValidatedFile.npc"), meterFile = _meterData)
                validatedFileObject.validatedFile.save("ValidatedFile.npc",  File(local_file))
                validatedFileObject.save()
                local_file.close()
                AllMeterFiles.objects.filter(id = _meterData.id).update(status="Verified")
            else : # That is ValidatedFile Object for this meter already exists.
                
                validatedFileObjects = list(filter(lambda validatedFile: (validatedFile.validatedFileMeterId() == str(_meterData.id)),ValidatedFile.objects.all()))
                print(validatedFileObjects)
                print(len(validatedFileObjects))
                validatedFileObject = validatedFileObjects[0]
                local_file = open(meterFileMainFolder+'/DateFiltered File/DateFilteredFile.npc',"rb") # Latest DateFiltered File will be picked from this folder.
                validatedFileObject.validatedFile.save("ValidatedFile.npc",  File(local_file))
                validatedFileObject.save()

            return errorList