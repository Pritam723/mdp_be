from .supportingFunctions import *
from django.conf import settings
import pandas as pd
from datetime import datetime,timedelta
from .models import AllMeterFiles,DateFilteredFile
from .allMeterDetails import getRealMeterFullData

def preValidate(df) :
    print("Inside preValidate")
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
            validateWeekHeader = weekHeaderCheckDate(weekHeaderData)
            if(not validateWeekHeader['status']) : errorList.append(str(validateWeekHeader['message']) + str(errorLine+1))
                
            weekStartDate_object = datetime.strptime(weekHeaderData[5], "%d-%m-%y")
            weekEndDate_object = datetime.strptime(weekHeaderData[10], "%d-%m-%y")
            
            print("For weekheader"+str(weekListIndex)+" : "+str(informationDict[weekListIndex]))
            # For weekheader0 : [1, 8, 15, 22, 29, 36, 43, 50, 54]
            
            meterNames = [df[x].split()[0] for x in informationDict[weekListIndex][:-1]]  # Must be unique
            meterDates = [datetime.strptime(df[x].split()[4], "%d-%m-%y") for x in informationDict[weekListIndex][:-1]] # Must be consequtive in the range of weekStartDate_object to weekEndDate_object
            
            # if(not (isMeterNameUnique(meterNames) and isMeterDateConsecutive(meterDates,weekStartDate_object,weekEndDate_object))) :

            if(not (isMeterNameUnique(meterNames))) :
                print("I am error at "+ str(weekListIndex))
                errorList.append("Different meter names/non-consecutive dates inside same WEEK Header :{{ " + str(df[weekListIndex]) + " }}. Line number : " + str(errorLine+1))
                continue
                
            #       No need to chcek this. DateFilter or File Overwrite will handle the issue.        
            #         if(meterNames[0] in meterNamesList) :
            #             errorList.append("Same meter name already exists. Line number : " + str(errorLine+1))
            #             continue
            
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
                
                validateMeterHeader = meterHeaderCheckDate(meterHeaderData)
                if(not validateMeterHeader['status']) : errorList.append(str(validateMeterHeader['message'])+str(errorLine+1))

                errorLine = informationDict[weekListIndex][k+1]
                validateMeterHeader = meterHeaderCheckDate(meterHeaderDataNext)
                if(not validateMeterHeader['status']) : errorList.append(str(validateMeterHeader['message'])+str(errorLine+1))            
                
                print("Changing meter header")

            print("Changing Week header")
        print("-----------------------------------------------------------------")

    except Exception as e :
        errorList.append("Unhandled generic issue : " + str(e) + ". Line no : " + str(errorLine+1))
            
    finally:
        print(len(errorList))
        return errorList
        #     print(set(allMeterNumbers) - set(meterNamesList)) # For these meters we do not have any data
        #     print(set(meterNamesList) - set(allMeterNumbers)) # These meter names are not defined in master.dat
        # for err in errorList :
        #     print(err)
        # if(len(errorList) == 0) :
        #     print("Proceed")
        #     return errorList
        # else :
        #     print("Stop")        
        #     return errorList


def dateFilterMergedFile(path,_meterData) :
    
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path) #Later "Merged File" path is added

    if not os.path.exists(meterFileMainFolder +'/DateFiltered File(Copy)'):
        os.makedirs(meterFileMainFolder + '/DateFiltered File(Copy)')
    if not os.path.exists(meterFileMainFolder +'/DateFiltered File'):
        os.makedirs(meterFileMainFolder + '/DateFiltered File')
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
            
    data = pd.read_csv(meterFileMainFolder+'/Merged File/MergedFile.npc', header = None)
    dfSeries = pd.DataFrame(data)
    df = dfSeries[0]
    print(df)

    validateError = preValidate(df = df)
    print("Returned from preValidate")

    nrxFormatNew = ['', 'Locations from where Data Not Received', '']
    nrxFormatNewBody = []
    
    nonAvailabilityInDateRange = []  # In case meter data not available in specified daterange.
    notDefinedMeters = []

    if(len(validateError) != 0) :
        return validateError
    else :
        userStartDate_str =  _meterData.startDate.strftime("%d-%m-%y")
        userEndDate_str =  _meterData.endDate.strftime("%d-%m-%y")   # Taken from input/meterFile. Do +1 for endDate.
        print(userStartDate_str)
        print(userEndDate_str)
        userStartDate_object = datetime.strptime(userStartDate_str, "%d-%m-%y")
        userEndDate_object = datetime.strptime(userEndDate_str, "%d-%m-%y")

        weekList = []
        meterHeaderList = []
        meterNamesList = []

        for i in range(len(df)-1) :
            rowList = df[i].split()
            rowList = extraCharHandler(rowList) # there can be extra char coz when validated we just ignored them. Didn't remove them.
            if(rowList[0] == "WEEK") : weekList.append(i) # Rest already validated.
            if(isMeterNumberPattern(rowList[0])) : meterHeaderList.append(i)
        weekList.append(len(df)-1) #EOF index must be added

        # print(weekList)

        print("*************************************")


        # print(meterHeaderList)

        informationDict = getDfInfo(weekList,meterHeaderList)
        print(informationDict)


        dateFixedDf = pd.Series([],dtype=object)

        for weekListIndex in weekList[:-1] :  # Will not take the EOFs index
            weekHeaderDataRaw = df[weekListIndex] # "WEEK FROM 0000 HRS OF 07-12-20 TO 1033 HRS OF 14-12-20"
            weekHeaderData = weekHeaderDataRaw.split()
            weekHeaderData = extraCharHandler(weekHeaderData)
        #      ********** should handle extra char, coz in validation we didn't edit them **************
            weekStartDate_object = datetime.strptime(weekHeaderData[5], "%d-%m-%y")
            weekEndDate_object = datetime.strptime(weekHeaderData[10], "%d-%m-%y")
            
            meterNames = [df[x].split()[0] for x in informationDict[weekListIndex][:-1]]  # Must be unique. Uniqueness already checked.
            meterNamesList.append(meterNames[0])
            nonAvailableForDates = []
            # If weekHeaderDate is completely out of user desired range, just skip the entire Header.
            if(weekStartDate_object > userEndDate_object or weekEndDate_object < userStartDate_object) :
                delta = userEndDate_object - userStartDate_object
                for i in range(delta.days+1):
                    day = userStartDate_object + timedelta(days=i)
                    nonAvailableForDates.append(datetime.strftime(day, "%d-%m-%y"))  
                
                nonAvailabilityInDateRange.append("Meter number : "+meterNames[0]+ " : "+ (",".join(nonAvailableForDates)))

                ### Code for new NRX Format ###

                realMeterFullData = getRealMeterFullData(path,meterNames[0])
    
                if(realMeterFullData is None) :
                    stringToAppend = f"{'NA   '}       {meterNames[0]}   {'NA  '}      {'NA       '}   {'NA'}" # Space Adjusted.
                    nrxFormatNew.append(stringToAppend)
                else :
                    stringToAppend = f"{realMeterFullData['Loc_Id']}       {meterNames[0]}   {realMeterFullData['ctr'] + ' ' * (4-len(realMeterFullData['ctr']))}      {realMeterFullData['ptr'] + ' ' * (9-len(realMeterFullData['ctr']))}   {realMeterFullData['POI'].lstrip()}"
                    nrxFormatNewBody.append({'Loc_Id' : realMeterFullData['Loc_Id'], 'msg' : stringToAppend})

                ### Code for new NRX Format Ends ###

                continue

            else :
                if(weekStartDate_object <= userStartDate_object): # i.e. we have more data left side.
                    weekStartDate_object = userStartDate_object
                    weekHeaderData[5] = datetime.strftime(userStartDate_object,"%d-%m-%y")
                    
                else : # i.e. we have less data left side.
                    
                    delta = weekStartDate_object - userStartDate_object       # as timedelta

                    for i in range(delta.days):
                        day = userStartDate_object + timedelta(days=i)
                        nonAvailableForDates.append(datetime.strftime(day, "%d-%m-%y"))            
                    
                if(weekEndDate_object >= userEndDate_object): # we have more data right side.
                    weekEndDate_object = userEndDate_object
                    weekHeaderData[7] = '2345'
                    weekHeaderData[10] = datetime.strftime(userEndDate_object,"%d-%m-%y")
                    
                else : # i.e. we have less data right side.

                    delta = userEndDate_object - weekEndDate_object       # as timedelta

                    for i in range(1,delta.days+1):
                        day = weekEndDate_object + timedelta(days=i)
                        nonAvailableForDates.append(datetime.strftime(day, "%d-%m-%y"))
                    
            # print(weekHeaderData)
            
            dateFixedDf = dateFixedDf.append(pd.Series(" ".join(weekHeaderData)), ignore_index=True)
            
            if(len(nonAvailableForDates) != 0) :
                nonAvailabilityInDateRange.append("Meter number : "+meterNames[0]+ " : "+ (",".join(nonAvailableForDates)))
                ### Code for new NRX Format ###

                realMeterFullData = getRealMeterFullData(path,meterNames[0])

                if(realMeterFullData is None) :
                    stringToAppend = f"{'NA   '}       {meterNames[0]}   {'NA  '}      {'NA       '}   {'NA'}" # Space Adjusted.
                    nrxFormatNew.append(stringToAppend)
                else :
                    stringToAppend = f"{realMeterFullData['Loc_Id']}       {meterNames[0]}   {realMeterFullData['ctr'] + ' ' * (4-len(realMeterFullData['ctr']))}      {realMeterFullData['ptr'] + ' ' * (9-len(realMeterFullData['ctr']))}   {realMeterFullData['POI'].lstrip()}"
                    nrxFormatNewBody.append({'Loc_Id' : realMeterFullData['Loc_Id'], 'msg' : stringToAppend})

                ### Code for new NRX Format Ends ###

            print("For weekheader"+str(weekListIndex)+" : "+str(informationDict[weekListIndex]))
            
            for k in range(len(informationDict[weekListIndex])-1):
                meterHeaderDataRaw = df[informationDict[weekListIndex][k]] # "NP-5851-A    97845.9    35371.6    00136.0    07-12-20"
                meterHeaderData = meterHeaderDataRaw.split()
                meterHeaderData = extraCharHandler(meterHeaderData)
            #      ********** should handle extra char, coz in validation we didn't edit them **************

                meterHeaderDate_object = datetime.strptime(meterHeaderData[4], "%d-%m-%y")

                if(not (meterHeaderDate_object >= weekStartDate_object and meterHeaderDate_object <= weekEndDate_object)):
                    continue
                
            #         print(meterHeaderData)
                
                dateFixedDf = dateFixedDf.append(pd.Series(meterHeaderDataRaw), ignore_index=True)

                meterMainDataRaw = df[informationDict[weekListIndex][k]+1:informationDict[weekListIndex][k+1]]
                # print(meterMainDataRaw)

                dateFixedDf = dateFixedDf.append(pd.Series(meterMainDataRaw), ignore_index=True)

                print("Changing meter header")
            print("Changing Week header")
        print("-----------------------------------------------------------------")
        print("----------Forgot to add EOF at the end--------------")

        dateFixedDf = dateFixedDf.append(pd.Series(["EOF"]), ignore_index=True)
        dateFixedDf = dateFixedDf.reset_index(drop=True)
        print(dateFixedDf)

        dateFixedDf.to_csv(meterFileMainFolder+'/DateFiltered File(Copy)/DateFilteredFile.npc', header=False, index=None)
        dateFixedDf.to_csv(meterFileMainFolder+'/DateFiltered File/DateFilteredFile.npc', header=False, index=None)

        if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 2)) :
            print("New DateFilteredFileId added")
            local_file = open(meterFileMainFolder+'/DateFiltered File(Copy)/DateFilteredFile.npc',"rb")
            dateFilteredFileObject = DateFilteredFile.objects.create(fileName = 'DateFilteredFile.npc', filePath = os.path.join("meterFile",path,"DateFiltered File/DateFilteredFile.npc"), meterFile = _meterData)
            dateFilteredFileObject.dateFilteredFile.save("DateFilteredFile.npc",  File(local_file))
            dateFilteredFileObject.save()
            local_file.close()
            AllMeterFiles.objects.filter(id = _meterData.id).update(status="DateFiltered")
        

        print(nonAvailabilityInDateRange)
        print("-----------------------------------------------------------------")

        print(set(allMeterNumbers) - set(meterNamesList)) # For these meters we do not have any data
        metersWithNoData = list(set(allMeterNumbers) - set(meterNamesList))  # These meters are defined in master.dat

        for meterWithNoData in metersWithNoData :
            nonAvailableForDates = []
            delta = userEndDate_object - userStartDate_object
            for i in range(delta.days+1):
                day = userStartDate_object + timedelta(days=i)
                nonAvailableForDates.append(datetime.strftime(day, "%d-%m-%y"))  
                
            nonAvailabilityInDateRange.append("Meter number : "+ meterWithNoData + " : "+ (",".join(nonAvailableForDates)))
            ### Code for new NRX Format ###

            realMeterFullData = getRealMeterFullData(path,meterWithNoData)

            if(realMeterFullData is None) :
                stringToAppend = f"{'NA   '}       {meterWithNoData}   {'NA  '}      {'NA       '}   {'NA'}" # Space Adjusted.
                nrxFormatNew.append(stringToAppend)
            else :
                stringToAppend = f"{realMeterFullData['Loc_Id']}       {meterWithNoData}   {realMeterFullData['ctr'] + ' ' * (4-len(realMeterFullData['ctr']))}      {realMeterFullData['ptr'] + ' ' * (9-len(realMeterFullData['ptr']))}   {realMeterFullData['POI'].lstrip()}"
                nrxFormatNewBody.append({'Loc_Id' : realMeterFullData['Loc_Id'], 'msg' : stringToAppend})

            ### Code for new NRX Format Ends ###
                
                
        print("-----------------------------------------------------------------")

        # print(set(meterNamesList) - set(allMeterNumbers)) # These meter names are not defined in master.dat
        notDefinedMeters = list(set(meterNamesList) - set(allMeterNumbers))

        nrxFiledDf = pd.Series([],dtype=object)
        if(len(nonAvailabilityInDateRange)) :
            nrxFiledDf = nrxFiledDf.append(pd.Series(["Data not available for the following " + str(len(nonAvailabilityInDateRange)) + " Meter(s) : "]), ignore_index=True)
            nrxFiledDf = nrxFiledDf.append(pd.Series([" "]), ignore_index=True)

            for item in nonAvailabilityInDateRange :
                nrxFiledDf = nrxFiledDf.append(pd.Series([item]), ignore_index=True)
            nrxFiledDf = nrxFiledDf.reset_index(drop=True)

            # Before adding footer, add the body. But we want the body to be sorted in alphabetical order in the basis of Loc_Id

            nrxFormatNewBody_Sorted = sorted(nrxFormatNewBody, key=lambda x: x['Loc_Id'])

            for item in nrxFormatNewBody_Sorted:
                nrxFormatNew.append(item['msg'])

            nrxFormatNew.append('')
            nrxFormatNew.append(f'NO OF LOCATIONS - DATA NOT RECEIVED - {str(len(nonAvailabilityInDateRange))}')
            nrxFormatNew.append('')

            with open(meterFileMainFolder + '/DateFiltered File/NEW_NRX_File.NRX', 'w') as f:
                for line in nrxFormatNew:
                    f.write(f"{line}\n")

        nrxFiledDf = nrxFiledDf.append(pd.Series([" "]), ignore_index=True)

        if(len(notDefinedMeters)) :

            nrxFiledDf = nrxFiledDf.append(pd.Series(["Following " + str(len(notDefinedMeters)) + " Meter(s) are not defined in master.dat file : "]), ignore_index=True)
            nrxFiledDf = nrxFiledDf.append(pd.Series([" "]), ignore_index=True)

            for item in notDefinedMeters :
                nrxFiledDf = nrxFiledDf.append(pd.Series([item]), ignore_index=True)
            nrxFiledDf = nrxFiledDf.reset_index(drop=True)

        if(len(nrxFiledDf)):
            nrxFiledDf.to_csv(meterFileMainFolder + '/DateFiltered File/NRXFile.NRX', header=False, index=None)

        return validateError
