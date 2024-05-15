from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
import numpy as np



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

def frequencyGraphData(path) :

    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)
    print(mwhDates)

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


    # Reading Master Frequency Info
    masterFreqMeter = {"Loc_Id" : '' , "Meter_No" : '' , "ctr" : 0 , "ptr" : 0 }
    masterFreqData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FRQMASTR.dat', "r")
    masterFreqDataList = masterFreqData.readlines()
    masterFreqData.close()

    for elem in masterFreqDataList :
        if(len(elem) > 1) :
            # print(elem.split())
            if(elem.split()[0] == 'LOC_ID') :
                masterFreqMeter['Loc_Id'] = elem.split()[1]
            if(elem.split()[0] == 'METER_NO') :
                masterFreqMeter['Meter_No'] = elem.split()[1]
            if(elem.split()[0] == 'CT_RATIO') :
                masterFreqMeter['ctr'] = elem.split()[1]
            if(elem.split()[0] == 'PT_RATIO') :
                masterFreqMeter['ptr'] = elem.split()[1]
                
                
    print(masterFreqMeter)
    # Done Reading Master Frequency Info

    # Reading Frequency Graph Info
    meterNumbersFreqGraph = []
    freqGraphData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FrequencyGraph.dat', "r")
    freqGraphDataList = freqGraphData.readlines()
    freqGraphData.close()
    for elem in freqGraphDataList :
        if(len(elem) > 1 and elem[0] != '#' and elem.strip() != 'LOC_ID') :
            if(getMeterInfoById(elem.strip()) is not None) :
                meterNumbersFreqGraph.append(getMeterInfoById(elem.strip())['Meter_No'])
                
    print("Printing frequency graph info...")
    meterNumbersFreqGraph.append(masterFreqMeter['Meter_No'])
    print(meterNumbersFreqGraph)

    # Done Frequency Graph Info
    allMeterFrequencyData = []

    for meterName in meterNumbersFreqGraph :
        fullWeekFreqData = {'x' : [] , 'y' : [] , 'type': "line" , 'name' : meterName}

        print(meterName)
        if(meterName == masterFreqMeter['Meter_No']) :
            fullWeekFreqData['name'] = meterName + " (Master Frequency) "
            for mwhDate in mwhDates  :
                timeArray = timeSeries()
                fullDayTimeStamp = [mwhDate + "  " + tStamp for tStamp in timeArray]
                fullWeekFreqData['x'] = fullWeekFreqData['x'] + fullDayTimeStamp
                if os.path.exists(realMeterMWHPath + mwhDate + '/masterFrequency.MFD'):
                    frData = pd.read_csv(realMeterMWHPath + mwhDate + '/masterFrequency.MFD' , header=None)
                    freq = [(49.5 + float(x)/100) for x in frData[0][1].split()]
                else :
                    freq = [None]*96

                fullWeekFreqData['y'] = fullWeekFreqData['y'] + freq
        else :
            for mwhDate in mwhDates  :
                timeArray = timeSeries()
                fullDayTimeStamp = [mwhDate + "  " + tStamp for tStamp in timeArray]
                fullWeekFreqData['x'] = fullWeekFreqData['x'] + fullDayTimeStamp
                if os.path.exists(realMeterMWHPath + mwhDate + '/'+ meterName +'.FD'):
                    frData = pd.read_csv(realMeterMWHPath + mwhDate + '/' + meterName +'.FD' , header=None)
                    freq = [(49.5 + float(x)/100) for x in frData[0][1].split()]
                else :
                    freq = [None]*96
                
                fullWeekFreqData['y'] = fullWeekFreqData['y'] + freq
        
        allMeterFrequencyData.append(fullWeekFreqData)
    
    return {'dataToSend' : allMeterFrequencyData}