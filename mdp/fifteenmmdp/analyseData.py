# from django.test import TestCase

# Create your tests here.
from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
import numpy as np


def endDifference(_end2,_end1) :
    diffList = []
    for i in range(len(_end2)):
        if(_end2[i] is None or _end1[i] is None) :
            diffList.append(None)
        else :
            diffList.append(_end2[i] - _end1[i])
    return diffList

def endDifferencePercentage(_end2,_end1) :
    percentList = []
    for i in range(len(_end2)):
        if(_end2[i] is None or _end1[i] is None) :
            percentList.append(None)
        elif(float(_end1[i]) == 0.0) :
            percentList.append(0)
        else :
            percentList.append((_end2[i] - _end1[i])*100/_end1[i])
    return percentList

def timeSeries() :
    _timeSeries = []
    ts = datetime.strptime('00:00', '%H:%M')
    # ts= time(00,00)
    while(True) :
        newTime = time(ts.hour,ts.minute)
        if(newTime >= time(23,45)) :
            break
        _timeSeries.append(newTime.strftime('%H:%M'))
        ts += timedelta(minutes=15)

    _timeSeries.append('23:45')
    return(_timeSeries)

def fetchData(meter_id,_end1,_end2,polarity,dataType) :
    # End1 = 'ER-02' 
    # End2 = 'BI-02'
    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile/meterFile"+meter_id)
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)
    print(mwhDates)


    ################################################### All RealMeters here. List of fict meters : #############################################

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
        return "FileNotFound"

    def searchMeterId(Meter_No) : # Any meter real or fictitious. Returns meter Loc_Id.
        meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
        fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Fict_Meter_No'] == Meter_No]
        if(len(meterDetails) != 0) : return meterDetails[0]['Loc_Id']
        if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Loc_Id']
        # return None
        return "Loc_Id not found"

    ##############################################################################################################################################

    # print(searchMeterNumber('ER-02'))
    # print(searchMeterNumber('BI-02'))

    end1 = searchMeterNumber(_end1)
    end2 = searchMeterNumber(_end2)
    print(end1)
    print(end2)

    xAxisData = []
    end1Data = []
    end2Data = []

    for mwhDate in mwhDates :
        
        timeArray = timeSeries()
        fullDayTimeStamp = [mwhDate + "  " + tStamp for tStamp in timeArray]

        if(dataType == "MWH Data"):
            xAxisData = xAxisData + fullDayTimeStamp
        else:
            xAxisData.append(datetime.strptime(mwhDate, "%d-%m-%y").strftime("%d-%b-%Y"))

        try :
            # dataEnd1 = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end1 + '.MWH' ,header = None)

            if(os.path.exists(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end1 + '.MWH')) :
                dataEnd1 = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end1 + '.MWH', header = None)  # May give FileNotFoundError
            else :
                dataEnd1 = pd.read_csv(meterFileMainFolder+'/Fictitious Meter MWH Files/' + mwhDate +'/' + end1 + '.MWH', header = None)

            dfSeriesEnd1 = pd.DataFrame(dataEnd1)
            dfEnd1 = dfSeriesEnd1[0]
            # dfEnd1

            headerData = dfEnd1[0].split()[1:]

            headerDataDict = {
                'Date' : headerData[1],
                'Active Data' : float(headerData[2]),
                'Reactive High' : float(headerData[3]),
                'Reactive Low' : float(headerData[4]),
            }

            # Now depending on whether the dataType is MWH Data/Active/Reactive High/Reactive Low, the prepared data will be different.

            if(dataType == "MWH Data"):
                for i in range(1, len(dfEnd1)) :
                    oneHourDataEnd1 = [changeToFloat(x) for x in dfEnd1[i].split()[1:]]
                    end1Data = end1Data + oneHourDataEnd1
            else:
                end1Data.append(headerDataDict[dataType])

        except FileNotFoundError as e:
            print(e)

            if(dataType == "MWH Data"):
                end1Data = end1Data + [None]*96
            else:
                end1Data.append(None)

        try :    
            multiplier = 1
            if(polarity == 'opp') :
                multiplier = -1

            # dataEnd2 = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end2 + '.MWH' ,header = None )
            if(os.path.exists(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end2 + '.MWH')) :
                dataEnd2 = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end2 + '.MWH', header = None)  # May give FileNotFoundError
            else :
                dataEnd2 = pd.read_csv(meterFileMainFolder+'/Fictitious Meter MWH Files/' + mwhDate +'/' + end2 + '.MWH', header = None)

            dfSeriesEnd2 = pd.DataFrame(dataEnd2)
            dfEnd2 = dfSeriesEnd2[0]
            # dfEnd2

            headerData = dfEnd2[0].split()[1:]


            headerDataDict = {
                'Date' : headerData[1],
                'Active Data' : float(headerData[2]),
                'Reactive High' : float(headerData[3]),
                'Reactive Low' : float(headerData[4]),
            }

            # Now depending on whether the dataType is MWH Data/Active/Reactive High/Reactive Low, the prepared data will be different.

            if(dataType == "MWH Data"):
                for i in range(1, len(dfEnd2)) :
                    oneHourDataEnd2 = [multiplier*changeToFloat(x) for x in dfEnd2[i].split()[1:]]
                    end2Data = end2Data + oneHourDataEnd2
            else:
                end2Data.append(multiplier * headerDataDict[dataType])
                
        except FileNotFoundError :
            if(dataType == "MWH Data"):
                end2Data = end2Data + [None]*96
            else:
                end2Data.append(None)

    # print(end1Data)
    print(len(end1Data))
    # print(end2Data)
    print(len(end2Data))
    # print(xAxisData)

    graphData = {'end1Data' : end1Data ,'end2Data' : end2Data , 'xAxisData' : xAxisData , 'diff' : endDifference(end2Data,end1Data), 'diffPercentage' : endDifferencePercentage(end2Data,end1Data)}

    
    return graphData