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

def deleteWeeklyData(path, datesToConsider):
    # path = "meterFile" + str(941)
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    # meterFileMainFolder = path
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    # fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'


    #################### Setting up all the Database.Collection Connectors. ###################################

    # masterData_collectionObj = DBConnectorUtil(collection = 'masterData').getCollectionObject()

    # fictdatData_collectionObj = DBConnectorUtil(collection = 'fictdatData').getCollectionObject()
    # fictcfgData_collectionObj = DBConnectorUtil(collection = 'fictcfgData').getCollectionObject()

    datewiseConfig_collectionObj = DBConnectorUtil(collection = 'datewiseConfig').getCollectionObject()

    ############################################################################################################

    ############################## Bifurcating the dates yearwise ##############################################

    meterWeekFolders = list(filter(isDate, os.listdir(realMeterMWHPath))) # Can write fictMeterMWHPath too.
    selectedDatesToConsider = [dt["name"] for dt in datesToConsider]
    # print("Printing 2 dates")
    # print(meterWeekFolders)
    # print(selectedDatesToConsider)
    # print("Done 2 dates")

    meterWeekFolders = list(set(meterWeekFolders) & set(selectedDatesToConsider))
    # print(meterWeekFolders)

    meterWeekFoldersDateObj = [datetime.strptime(dt,'%d-%m-%y') for dt in meterWeekFolders]

    meterWeekFoldersDateObj.sort()

    # print(meterWeekFoldersDateObj)


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
        print(f"Dates for {yearToCover}")
        mwhDates = [dt.strftime("%d-%m-%y") for dt in yearsToCover[yearToCover]]
        print(mwhDates)
        startDate = mwhDates[0]
        endDate = mwhDates[-1]
        
        startDateObj = datetime.strptime(startDate, '%d-%m-%y')
        endDateObj = datetime.strptime(endDate, '%d-%m-%y')
        
        deletedConfig = datewiseConfig_collectionObj.delete_many({'date' : {"$gte" : startDateObj, "$lte" : endDateObj}})
        print(f"{deletedConfig.deleted_count} no. of configuration data deleted")
        deletedMeterData = meterData_collectionObj.delete_many({'date' : {"$gte" : startDateObj, "$lte" : endDateObj}})
        print(f"{deletedMeterData.deleted_count} no. of meter data deleted")
        