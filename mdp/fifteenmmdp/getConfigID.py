from .dbConnectorUtility import DBConnectorUtil
from datetime import datetime
from .MeterUtil import MeterUtil

def getDifferenceDicts(oldDict, newDict) :
    
    isDifferent = False
    
    deletedInNewDict = {key:oldDict.get(key) for key in oldDict if oldDict.get(key) != newDict.get(key)}

    addedInNewDict = {key:newDict.get(key) for key in newDict if newDict.get(key) != oldDict.get(key)}
    
    if(len(deletedInNewDict) + len(addedInNewDict) > 0) : isDifferent = True
        
    return {'isDifferent' : isDifferent, 'Deleted' : deletedInNewDict, 'Added' : addedInNewDict}

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


def getMasterDataDocumentId(dateStr, configPath) :
    
    
    #################### Setting up all the Database.Collection Connectors. ###################################

    masterData_collectionObj = DBConnectorUtil(collection = 'masterData').getCollectionObject()

    # fictdatData_collectionObj = DBConnectorUtil(collection = 'fictdatData').getCollectionObject()
    # fictcfgData_collectionObj = DBConnectorUtil(collection = 'fictcfgData').getCollectionObject()

    datewiseConfig_collectionObj = DBConnectorUtil(collection = 'datewiseConfig').getCollectionObject()

    ############################################################################################################

    
    # dateStr = '14-03-23'
    # configPath = "//10.3.100.24//Meter-Data//Meter Archive//2018 C/JAN'18//070118//Config File"
    
    # For this weekFolder read the ConfigFiles & Read the Current Date Configurations.
    meterUtilObj = MeterUtil(configPath)
    currentDateRealMeters = meterUtilObj.getAllRealMeters()
    ##################################################################################
    
    # Now we will read the previous and nextDate Configurations
    
    # dateObj = datetime.strptime(dateStr, "%d%m%y") # For old Data Format
    dateObj = datetime.strptime(dateStr, "%d-%m-%y") # For new Data Format


    previousConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$lt' : dateObj} }).sort([("date", -1)]).limit(1))
    nextConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$gt' : dateObj} }).sort([("date", 1)]).limit(1))
    
    isPreviousDifferent = True
    isNextDifferent = True

    previousDateMasterData = {'realMeters' : []}
    nextDateMasterData = {'realMeters' : []}
    
    if(len(previousConfig) != 0) : # So, there is atleast one Config Available of Some Previous Date
        # previousConfig[0]['masterDataId']
        # previousConfig can be empty [] if this is first date.
        previousDateMasterData = masterData_collectionObj.find_one({'_id' : previousConfig[0]['masterDataId']})
        isPreviousDifferent = getDifferenceListOfDict(previousDateMasterData['realMeters'], currentDateRealMeters)['isDifferent']

    if(len(nextConfig) != 0) : # So, there is atleast one Config Available of Some Next Date
        # nextConfig[0]['masterDataId']
        # nextConfig can be empty [] if this is last date.
        nextDateMasterData = masterData_collectionObj.find_one({'_id' : nextConfig[0]['masterDataId']})
        isNextDifferent = getDifferenceListOfDict(nextDateMasterData['realMeters'], currentDateRealMeters)['isDifferent']


    # Now we have got final value of isPreviousDifferent and isNextDifferent. Now decide what to do.

    masterDataDocumentId = None

    if(isPreviousDifferent == False) :
        # We should use this previous day's masterData ID for this day also.
        masterDataDocumentId = previousDateMasterData['_id']

    elif(isNextDifferent == False) :
        # If it is different from previous data, check with next day's masterData.
        # We should use this next day's masterData ID for this day also.
        masterDataDocumentId = nextDateMasterData['_id']
    else :
        # So, if both are true, we should add a fresh masterData Document.
        
        # print("Adding Fresh Master Data")
        
        masterDataDocument = {
            'realMeters' : currentDateRealMeters
        }

        masterDataDocumentInsertedObj = masterData_collectionObj.insert_one(masterDataDocument)

        masterDataDocumentId = masterDataDocumentInsertedObj.inserted_id
        
        # Also in this case we should Add New Real Meter IDs in allTimeRealMeterIDs list.
        addedInNewList = getDifferenceListOfDict(previousDateMasterData['realMeters'], currentDateRealMeters)['Added']
                
        allTimeRealMeterIDs_collectionObj = DBConnectorUtil(collection = 'allTimeRealMeterIDs').getCollectionObject()
        
        # print(addedInNewList)

        for item in addedInNewList :
            meterID = item['Loc_Id']

            document = allTimeRealMeterIDs_collectionObj.find_one({'name' : meterID})

            if(document is None) :
                # Insert a new document.
                allTimeRealMeterIDs_collectionObj.insert_one({'name' : meterID, 'code' : meterID})
                # print("Document inserted")
            
    # Now once the masterDataDocumentId is fixed. We can go ahead to use it in other Document as reference.
    return masterDataDocumentId


def getFictdatDataDocumentId(dateStr, configPath) :
    
    
    #################### Setting up all the Database.Collection Connectors. ###################################

    # masterData_collectionObj = DBConnectorUtil(collection = 'masterData').getCollectionObject()

    fictdatData_collectionObj = DBConnectorUtil(collection = 'fictdatData').getCollectionObject()
    
    # fictcfgData_collectionObj = DBConnectorUtil(collection = 'fictcfgData').getCollectionObject()

    datewiseConfig_collectionObj = DBConnectorUtil(collection = 'datewiseConfig').getCollectionObject()

    ############################################################################################################

    
    # dateStr = '14-03-23'
    # configPath = "//10.3.100.24//Meter-Data//Meter Archive//2018 C/JAN'18//070118//Config File"
    
    # For this weekFolder read the ConfigFiles & Read the Current Date Configurations.
    meterUtilObj = MeterUtil(configPath)
    currentDateFictMeters = meterUtilObj.getAllFictitiousMeters()

    ##################################################################################
    
    # Now we will read the previous and nextDate Configurations
    
    # dateObj = datetime.strptime(dateStr, "%d%m%y") # For old Data Format
    dateObj = datetime.strptime(dateStr, "%d-%m-%y") # For new Data Format

    previousConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$lt' : dateObj} }).sort([("date", -1)]).limit(1))
    nextConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$gt' : dateObj} }).sort([("date", 1)]).limit(1))
    
    isPreviousDifferent = True
    isNextDifferent = True

    previousDateFictData = {'fictMeters' : []}
    nextDateFictData = {'fictMeters' : []}
    
    if(len(previousConfig) != 0) : # So, there is atleast one Config Available of Some Previous Date
        # previousConfig[0]['fictdatDataId']
        # previousConfig can be empty [] if this is first date.
        # print("Fine here")
        previousDateFictData = fictdatData_collectionObj.find_one({'_id' : previousConfig[0]['fictdatDataId']})
        isPreviousDifferent = getDifferenceListOfDict(previousDateFictData['fictMeters'], currentDateFictMeters)['isDifferent']
        
        # print(previousDateFictData['fictMeters'])
        # print(currentDateFictMeters)
        
        # print(getDifferenceListOfDict(previousDateFictData['fictMeters'], currentDateFictMeters))
        
    if(len(nextConfig) != 0) : # So, there is atleast one Config Available of Some Next Date
        # nextConfig[0]['fictdatDataId']
        # nextConfig can be empty [] if this is last date.
        nextDateFictData = fictdatData_collectionObj.find_one({'_id' : nextConfig[0]['fictdatDataId']})
        isNextDifferent = getDifferenceListOfDict(nextDateFictData['fictMeters'], currentDateFictMeters)['isDifferent']


    # Now we have got final value of isPreviousDifferent and isNextDifferent. Now decide what to do.

    fictdatDataDocumentId = None

    if(isPreviousDifferent == False) :
        # We should use this previous day's fictdatData ID for this day also.
        fictdatDataDocumentId = previousDateFictData['_id']

    elif(isNextDifferent == False) :
        # If it is different from previous data, check with next day's fictdatData.
        # We should use this next day's fictdatData ID for this day also.
        fictdatDataDocumentId = nextDateFictData['_id']
    else :
        # So, if both are true, we should add a fresh fictdatData Document.
        
        # print("Adding Fresh Fictdat Data")

        
        fictdatDataDocument = {
            'fictMeters' : currentDateFictMeters
        }

        fictdatDataDocumentInsertedObj = fictdatData_collectionObj.insert_one(fictdatDataDocument)

        fictdatDataDocumentId = fictdatDataDocumentInsertedObj.inserted_id
        
        # Also in this case we should Add New Fict Meter IDs in allTimeFictMeterIDs list.
        addedInNewList = getDifferenceListOfDict(previousDateFictData['fictMeters'], currentDateFictMeters)['Added']
        
        allTimeFictMeterIDs_collectionObj = DBConnectorUtil(collection = 'allTimeFictMeterIDs').getCollectionObject()

        # print(addedInNewList)
        
        for item in addedInNewList :
            meterID = item['Loc_Id']

            document = allTimeFictMeterIDs_collectionObj.find_one({'name' : meterID})

            if(document is None) :
                # Insert a new document.
                allTimeFictMeterIDs_collectionObj.insert_one({'name' : meterID, 'code' : meterID})
                # print("Document inserted")

    # Now once the fictdatDataDocumentId is fixed. We can go ahead to use it in other Document as reference.
    return fictdatDataDocumentId


def getFictcfgDataDocumentId(dateStr, configPath) :
    
    
    #################### Setting up all the Database.Collection Connectors. ###################################

    # masterData_collectionObj = DBConnectorUtil(collection = 'masterData').getCollectionObject()

    # fictdatData_collectionObj = DBConnectorUtil(collection = 'fictdatData').getCollectionObject()
    
    fictcfgData_collectionObj = DBConnectorUtil(collection = 'fictcfgData').getCollectionObject()

    datewiseConfig_collectionObj = DBConnectorUtil(collection = 'datewiseConfig').getCollectionObject()

    ############################################################################################################

    
    # dateStr = '14-03-23'
    # configPath = "//10.3.100.24//Meter-Data//Meter Archive//2018 C/JAN'18//070118//Config File"
    
    # For this weekFolder read the ConfigFiles & Read the Current Date Configurations.
    meterUtilObj = MeterUtil(configPath)

    currentDateFictConfigs = meterUtilObj.getAllFictitiousMeterEqutation()
    ##################################################################################
    
    # Now we will read the previous and nextDate Configurations
    
    # dateObj = datetime.strptime(dateStr, "%d%m%y") # For old Data Format
    dateObj = datetime.strptime(dateStr, "%d-%m-%y") # For new Data Format

    previousConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$lt' : dateObj} }).sort([("date", -1)]).limit(1))
    nextConfig = list(datewiseConfig_collectionObj.find({ 'date' : {'$gt' : dateObj} }).sort([("date", 1)]).limit(1))
    
    isPreviousDifferent = True
    isNextDifferent = True

    if(len(previousConfig) != 0) : # So, there is atleast one Config Available of Some Previous Date
        # previousConfig[0]['fictcfgDataID']
        # previousConfig can be empty [] if this is first date.
        previousDateFictcfgData = fictcfgData_collectionObj.find_one({'_id' : previousConfig[0]['fictcfgDataID']})
        isPreviousDifferent = getDifferenceDicts(previousDateFictcfgData['fictCFGs'], currentDateFictConfigs)['isDifferent']

    if(len(nextConfig) != 0) : # So, there is atleast one Config Available of Some Next Date
        # nextConfig[0]['fictcfgDataID']
        # nextConfig can be empty [] if this is last date.
        nextDateFictcfgData = fictcfgData_collectionObj.find_one({'_id' : nextConfig[0]['fictcfgDataID']})
        isNextDifferent = getDifferenceDicts(nextDateFictcfgData['fictCFGs'], currentDateFictConfigs)['isDifferent']


    # Now we have got final value of isPreviousDifferent and isNextDifferent. Now decide what to do.

    fictcfgDataDocumentId = None

    if(isPreviousDifferent == False) :
        # We should use this previous day's fictcfgData ID for this day also.
        fictcfgDataDocumentId = previousDateFictcfgData['_id']

    elif(isNextDifferent == False) :
        # If it is different from previous data, check with next day's fictcfgData.
        # We should use this next day's fictcfgData ID for this day also.
        fictcfgDataDocumentId = nextDateFictcfgData['_id']
    else :
        # So, if both are true, we should add a fresh fictcfgData Document.
        fictcfgDataDocument = {
            'fictCFGs' : currentDateFictConfigs
        }

        fictcfgDataDocumentInsertedObj = fictcfgData_collectionObj.insert_one(fictcfgDataDocument)

        fictcfgDataDocumentId = fictcfgDataDocumentInsertedObj.inserted_id

    # Now once the fictcfgDataDocumentId is fixed. We can go ahead to use it in other Document as reference.
    return fictcfgDataDocumentId