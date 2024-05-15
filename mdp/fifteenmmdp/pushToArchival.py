from .dbConnectorUtility import DBConnectorUtil
from datetime import datetime
import pandas as pd
from .getConfigID import *
import os
import re
from datetime import datetime
from .MeterUtil import MeterUtil
import pymongo
from django.conf import settings


def fixHeaderInfo(headerInfo, meterNumber) :
    if(len(headerInfo) == 6) :
        # So all data is fine.
        return headerInfo
    
    # To solve issue like ['TL-95', 'TAL_SOL_STBY01-01-18', '-35.9520', '1.6', '0.0']
    
    if(len(headerInfo[1]) > len(meterNumber)) : # So it is in 'TAL_SOL_STBY01-01-18' format.
        dateInfo = headerInfo[1].split(meterNumber)[1]
        # Now make headerInfo[1] = meterNumber
        headerInfo[1] = meterNumber
        headerInfo.insert(2, dateInfo)
        
    # To solve issue like ['FK-01', 'ER-9999-A', '01-01-18', '-35.9520', '-23395.2-130402.8']
    if(headerInfo[4].count('.') == 2) :
        x = headerInfo[4]

        lastIndexOfFirstNumber = x.find('.') + 1 # Because it will be in -23395.2-130402.8 format always.

        headerInfo[4] = x[ : lastIndexOfFirstNumber + 1]
        headerInfo.append(x[lastIndexOfFirstNumber + 1 : ])
        
    return headerInfo

def getDifferenceListOfDict(oldList, newList) :
    
    isDifferent = False
    
    deletedInNewList = []
    for i in oldList:
        if i not in newList:
            deletedInNewList.append(i)

    addedInNewList = []
    for i in newList:
        if i not in oldList:
            addedInNewList.append(i)
    
    if(len(deletedInNewList) + len(addedInNewList) > 0) : isDifferent = True
        
    return {'isDifferent' : isDifferent, 'Deleted' : deletedInNewList, 'Added' : addedInNewList}


def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

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

def removeExtraCharFromString(s) :
    s = s.replace('*', '')
    s = s.replace('z', '')
    s = s.replace('a', '')
    s = s.replace('r', '')
    s = s.replace(' ','')
    s = s.replace(u'\xa0', u'') # Non breaking space.
    s = s.replace('\t','')
    s = s.replace('\n','')
    return s

def isDate(value, delimeter = '-') :
    datePattern = re.compile(r'^[0-9]{2}' + delimeter + '[0-9]{2}' + delimeter + '[0-9]{2}$')
    result = re.match(datePattern, value)
    if(result is None) :
        return False                                             
    try:
        datetime.strptime(value, f"%d{delimeter}%m{delimeter}%y")
        return True
    except ValueError:
        return False
    
def isDateNoDelimeter(value, delimeter = '') :
    datePattern = re.compile(r'^[0-9]{2}' + delimeter + '[0-9]{2}' + delimeter + '[0-9]{2}$')
    result = re.match(datePattern, value)
    if(result is None) :
        return False                                             
    try:
        datetime.strptime(value, f"%d{delimeter}%m{delimeter}%y")
        return True
    except ValueError:
        return False
    
def sortDateStrings(stringDateList) :
    stringDateList.sort(key=lambda date: datetime.strptime(date, "%d-%m-%y"))
    return stringDateList
    
    
def sortDateNoDelimeterStrings(stringDateList) :
    stringDateList.sort(key=lambda date: datetime.strptime(date, "%d%m%y"))
    return stringDateList

def pushMeterDataToArchive(path, datesToConsider):
    # path = "meterFile" + str(941)
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    # meterFileMainFolder = path
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    configPath = f"{meterFileMainFolder}//NPC Files//Necessary Files Local Copy"


    meterUtilObj = MeterUtil(configPath)
    currentDateRealMeters = meterUtilObj.getAllRealMeters()
    currentDateFictMeters = meterUtilObj.getAllFictitiousMeters()
    currentDateFictConfigs = meterUtilObj.getAllFictitiousMeterEqutation()

    currentDateAllMeters = currentDateRealMeters + currentDateFictMeters


    # allDates = []
    corruptData = []


    #################### Setting up all the Database.Collection Connectors. ###################################

    # masterData_collectionObj = DBConnectorUtil(collection = 'masterData').getCollectionObject()

    # fictdatData_collectionObj = DBConnectorUtil(collection = 'fictdatData').getCollectionObject()
    # fictcfgData_collectionObj = DBConnectorUtil(collection = 'fictcfgData').getCollectionObject()

    datewiseConfig_collectionObj = DBConnectorUtil(collection = 'datewiseConfig').getCollectionObject()

    ############################################################################################################

    ############################## Bifurcating the dates yearwise ##############################################

    meterWeekFolders = list(filter(isDate, os.listdir(realMeterMWHPath))) # Can write fictMeterMWHPath too.
    selectedDatesToConsider = [dt["name"] for dt in datesToConsider]

    meterWeekFolders = list(set(meterWeekFolders) & set(selectedDatesToConsider))

    meterWeekFoldersDateObj = [datetime.strptime(dt,'%d-%m-%y') for dt in meterWeekFolders]

    meterWeekFoldersDateObj.sort()

    yearsToCover = {}
    for dt in meterWeekFoldersDateObj:
        if yearsToCover.get(dt.year) is None:
            yearsToCover[dt.year] = [dt]
        else:
            yearsToCover[dt.year].append(dt)

    ############################################################################################################

    ######################################### Running for a year ###############################################

    for yearToCover in yearsToCover:
        print(f"Working with {yearToCover}")
        
        # The meterData_collectionObj will be created dynamically based on the collectionName. It depends on the year.
        meterData_collectionObj = DBConnectorUtil(collection = f'meterData{yearToCover}').getCollectionObject()

        collection_indices = list(meterData_collectionObj.index_information())

        if 'queryByIDIndex' not in collection_indices:
            meterData_collectionObj.create_index([("meterID" , pymongo.ASCENDING),("date", pymongo.ASCENDING)],unique = True,name="queryByIDIndex")
        if 'queryByNameIndex' not in collection_indices:
            meterData_collectionObj.create_index([("meterNO" , pymongo.ASCENDING),("date", pymongo.ASCENDING)],name="queryByNameIndex")
        
        print(f"Dates for {yearToCover}")
        mwhDates = [dt.strftime("%d-%m-%y") for dt in yearsToCover[yearToCover]]
        print(mwhDates)
        
        ##################### Reading Single Week Data ##############################################################

        # For a week folder the 3 configurations are kept same. So, once we insert the data into MongoDB,
        # make sure to Insert configurations in datewiseConfig. Insert new configs only if there is a change
        # Otherwise use previous config ID for the date.

        # Let's do the check step by step. Below mentioned.

        #############################################################################################################
        
        # For a meterWeekFolder, the above configurations are same.
        # Run this to verify that configuration files are in correct readable format.

        # Now inside a meterWeekFolder we have data for the week. So, inside it
        # we will have All_Meter_MWH and Config File Folders.
        # From Config File We have taken the Configurations

        # Let's take the All_Meter_MWH data. It will have folders like 010118, 020118, 030118 etc.
        # Inside a folder we have data of that week.

        realMeterFolder = realMeterMWHPath
        fictMeterFolder = fictMeterMWHPath

        # mwhDatesFolder = f"{dataSource}//{meterWeekFolder}//All_Meter_MWH//Real_Meter_MWH"
        mwhDatesFolder = realMeterFolder # Can take fictMeterFolder too. We only want the dates.

        multipleDocumentToMongoDB = [] # For a Meter Week Folder it will store all the documents to be inserted.

        # allDates = allDates + mwhDates (Check Size is 365 or not)

        # Now check all the configs with previous & next date configs.
        # Now understand one thing. For a week the 3 configs are same. Also we assume that no data for this week is yet populated.
        # So, only pick one date of the week and take it's previous and next date. Check currentConfig with that of the previous and next.
        # And accordingly decide whether to add new config or use old ones only.
        # See, for every date we will have entry in datewiseConfig collection. However it will refer the 3 configs with IDs only. (WKR)
        # So, first decide what masterDataId, fictdatDataId, fictcfgDataID to use in the datewiseConfig of this date.

        # So, before looping through entire week (mwhDate), take the startDate = mwhDate[0] and decide the above 3 once and for all.


        startDate = mwhDates[0]
        endDate = mwhDates[-1]

        print("Calculating for the week : ")
        print(mwhDates)

        c1 = datetime.now()


        masterDataDocumentId = getMasterDataDocumentId(dateStr = startDate, configPath = configPath)
        fictdatDataDocumentId = getFictdatDataDocumentId(dateStr = startDate, configPath = configPath)
        fictcfgDataDocumentId = getFictcfgDataDocumentId(dateStr = startDate, configPath = configPath)

        # Now we are sure that we want to use these IDs only. It can be repeating IDs, no issue. So now Insert datewiseConfigurationLog
        # for each day. For each day the 3 IDs will be same. But the date will change as per mwhDate. It will not be startDate always.
        # But see, while Inserting meterDate we are actually Accumulating it for 7 days & then Inserting Many. We can do the same
        # for datewiseConfigurationLog too. Accumulate for 7 days & then finally Insert. Otherwise pushing for each day is also fine.
        # But doing in same manner will ensure Integrity. If something fails for a day in b/w week,
        # none of the meterData or datewiseConfigurationLog will prevail. Maximum of 7 days masterDataId, fictdatDataId, fictcfgDataID
        # will be inserted which is not an issue.

        weekwiseConfigurationLog = []
        print(masterDataDocumentId, fictdatDataDocumentId, fictcfgDataDocumentId)
            
        for mwhDate in mwhDates :
            mwhDateObj = datetime.strptime(mwhDate, "%d-%m-%y")

            ## Processing single day datewiseConfigurationLog.
            # # one document of meterDataArchival.datewiseConfig. Only Insert after we have successfully Inserted the 3 Configs.
            # # We need Object ID of those. See above, We have already done that for this week.

            datewiseConfigurationLog = {
            'date': mwhDateObj,
            'masterDataId': masterDataDocumentId,
            'fictdatDataId': fictdatDataDocumentId,
            'fictcfgDataID': fictcfgDataDocumentId,
            };

            # Don't Insert One at a time. Insert Weekly.
            ## datewiseConfigurationLogId = datewiseConfig_collectionObj.insert_one(datewiseConfigurationLog)

            weekwiseConfigurationLog.append(datewiseConfigurationLog)


            # Now for a date get all it's Real Meter Data and Fictitious Data.


            ##################### Getting All Real Meter Data. #########################

            for currentDateAllMeter in currentDateRealMeters :

                original_meter_no = currentDateAllMeter['Meter_No'] # All '-' and '_' chars are there.
                original_loc_Id = currentDateAllMeter['Loc_Id'] # All '-' and '_' chars are there.

                meter_no = currentDateAllMeter['Meter_No']
                loc_Id = currentDateAllMeter['Loc_Id']
                meter_no = meter_no
                loc_Id = loc_Id

                # print(meter_no, loc_Id)
                # dataPath = f"{mwhDatesFolder}\\{mwhDate}\\{meter_no}.MWH"
                dataPath = f"{realMeterFolder}\\{mwhDate}\\{meter_no}.MWH"

                ##################### Reading Single Day Data #########################

                #print(dataPath)
                if(os.path.exists(dataPath)) :

                    # print(f" Data available for {meter_no} of date {mwhDate}")

                    data = pd.read_csv(dataPath, header = None)  # May give FileNotFoundError
                    dfSeries = pd.DataFrame(data)
                    df = dfSeries[0]
                    headerInfo = df[0].split()

                    # Now headerInfo may have data like -23395.2-130402.8 for headerInfo[4] sometimes. So fix that.

                    headerInfo = fixHeaderInfo(headerInfo, original_meter_no)          

                    if(len(headerInfo) > 6) :
                        corruptData.append(f"Issue in Header Info for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        continue # Go process next Meter

                    fullDayData = []

                    for hourData in df[1:] :
                        fullDayData = fullDayData + hourData.split()[1:]

                    fullDayData = extraCharHandler(fullDayData)

                    fullDayData = [float(removeExtraCharFromString(x)) for x in fullDayData if isFloat(removeExtraCharFromString(x))]

                    if(len(fullDayData) != 96) :
                        # raise Exception(f"Full Day Data Not Available for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        corruptData.append(f"Full Day Data Not Available for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        continue # Go process next Meter

                    singleDocumentToMongoDB = { 'date' : mwhDateObj, 'meterID' : original_loc_Id, 'meterNO' : original_meter_no,'data' : fullDayData,'activeHigh' : float(headerInfo[3]),'reactiveHigh' : float(headerInfo[4]),'reactiveLow' : float(headerInfo[5])}

                    multipleDocumentToMongoDB.append(singleDocumentToMongoDB)

                    # print(f"file read successful for {meter_no} dated {mwhDate}")
                else :
                    print(f"no file for {meter_no} dated {mwhDate}")

                #print(fullDayData)
            #############################################################################


            ##################### Getting All Fictitious Meter Data. #########################

            for currentDateAllMeter in currentDateFictMeters :

                original_meter_no = currentDateAllMeter['Meter_No'] # All '-' and '_' chars are there.
                original_loc_Id = currentDateAllMeter['Loc_Id'] # All '-' and '_' chars are there.

                meter_no = currentDateAllMeter['Meter_No']
                loc_Id = currentDateAllMeter['Loc_Id']
                meter_no = meter_no
                loc_Id = loc_Id

                # print(meter_no, loc_Id)
                # dataPath = f"{mwhDatesFolder}\\{mwhDate}\\{meter_no}.MWH"
                dataPath = f"{fictMeterFolder}\\{mwhDate}\\{meter_no}.MWH"

                ##################### Reading Single Day Data #########################

                #print(dataPath)
                if(os.path.exists(dataPath)) :

                    # print(f" Data available for {meter_no} of date {mwhDate}")

                    data = pd.read_csv(dataPath, header = None)  # May give FileNotFoundError
                    dfSeries = pd.DataFrame(data)
                    df = dfSeries[0]
                    headerInfo = df[0].split()

                    # Now headerInfo may have data like -23395.2-130402.8 for headerInfo[4] sometimes. So fix that.

                    headerInfo = fixHeaderInfo(headerInfo, original_meter_no)          

                    if(len(headerInfo) > 6) :
                        corruptData.append(f"Issue in Header Info for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        continue # Go process next Meter

                    fullDayData = []

                    for hourData in df[1:] :
                        fullDayData = fullDayData + hourData.split()[1:]

                    fullDayData = extraCharHandler(fullDayData)

                    fullDayData = [float(removeExtraCharFromString(x)) for x in fullDayData if isFloat(removeExtraCharFromString(x))]

                    if(len(fullDayData) != 96) :
                        # raise Exception(f"Full Day Data Not Available for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        corruptData.append(f"Full Day Data Not Available for {meter_no} dated {mwhDate}. Data Source Might Be corrupt.")
                        continue # Go process next Meter

                    singleDocumentToMongoDB = { 'date' : mwhDateObj, 'meterID' : original_loc_Id, 'meterNO' : original_meter_no,'data' : fullDayData,'activeHigh' : float(headerInfo[3]),'reactiveHigh' : float(headerInfo[4]),'reactiveLow' : float(headerInfo[5])}

                    multipleDocumentToMongoDB.append(singleDocumentToMongoDB)

                    # print(f"file read successful for {meter_no} dated {mwhDate}")
                else :
                    print(f"no file for {meter_no} dated {mwhDate}")

                #print(fullDayData)
            #############################################################################




            # collectionObj = DBConnectorUtil(collection = "meterData2019").getCollectionObject() # Already Defined Above.

            # After full week data is ready, push it into DB.

        x = meterData_collectionObj.insert_many(multipleDocumentToMongoDB) # No need for x. We can see x.inserted_id

        x = datewiseConfig_collectionObj.insert_many(weekwiseConfigurationLog) # No need for x. We can see x.inserted_id
        # datewiseConfig_collectionObj.insert_many(weekwiseConfigurationLog)

        print(f'Data Inserted for week')
        c2 = datetime.now()
        print(c2-c1)
        

    ############################################################################################################