
###########################  Special Report is primarily made for LOSS Analysis only #####################################

# from django.test import TestCase

# Create your tests here.
from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
import numpy as np
from .analyseData import fetchData
from .componentWiseAnalysis import componentWiseMeterAnalysis

def successiveDifferencePercentage(lstInput) :
    toReturn = []
    for i in range(len(lstInput) - 1) :
        if((lstInput[i+1] is not None) and (lstInput[i] is not None)) :
            if(lstInput[i] == 0.0 and lstInput[i] != 0.0) :
                toReturn.append(9999.99)
            if(lstInput[i] == 0.0 and lstInput[i] == 0.0) :
                toReturn.append(0.00)
            else :
                toReturn.append(round( 100*(lstInput[i+1] - lstInput[i])/lstInput[i] , 2 ))
        else :
            toReturn.append(None)

    return toReturn

def successiveDifferencePercentageForLoss(lstInput) : # here difference is already divided by previous term.
    toReturn = []
    for i in range(len(lstInput) - 1) :
        if((lstInput[i+1] is not None) and (lstInput[i] is not None)) :
            toReturn.append(round((lstInput[i+1] - lstInput[i])*100 , 2))
        else :
            toReturn.append(None)

    return toReturn

def lossPercentage(_end2,_end1) :
    percentList = []
    for i in range(len(_end2)):
        if(_end2[i] is None or _end1[i] is None) :
            percentList.append(None)
        else :
            percentList.append((_end2[i] - _end1[i])/_end1[i])
    return percentList

def endDifference(_end2,_end1) :
    diffList = []
    for i in range(len(_end2)):
        if(_end2[i] is None or _end1[i] is None) :
            diffList.append(None)
        else :
            diffList.append(_end2[i] - _end1[i])
    return diffList

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

def specialReport1(path,meter_id,threshold):
    print("inside specialReports")

    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile/meterFile"+meter_id)
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)
    print(mwhDates)


    ############################################### All RealMeters here. List of fict meters : #############################################

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


    ############################################### All FictMeters here. List of fict meters : #############################################
    
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

    graphData = fetchData(meter_id,_end1="RN-95",_end2="RN-96",polarity="def",dataType="MWH Data")
    # return HttpResponse(json.dumps(graphData), content_type='application/json')
    _fullXAxisData = [datetime.strptime(x,"%d-%m-%y %H:%M") for x in graphData['xAxisData']]
    fullXAxisData = [datetime.strftime(x,"%Y-%m-%d %H:%M") for x in _fullXAxisData]
    percentLossList = lossPercentage(graphData['end2Data'],graphData['end1Data'])
    
    # successiveLossDifferenceList = list(np.diff(percentLossList))
    # successivePercentLossDifferenceList = [x * 100 for x in successiveLossDifferenceList]
    successivePercentLossDifferenceList = successiveDifferencePercentageForLoss(percentLossList)
    successivePercentGenerationDifferenceList = successiveDifferencePercentage(graphData['end1Data'])
    successivePercentDrawalDifferenceList = successiveDifferencePercentage(graphData['end2Data'])

    componentWiseGraphData1 = componentWiseMeterAnalysis("meterFile"+meter_id ,"RN-95")
    componentWiseGraphData2 = componentWiseMeterAnalysis("meterFile"+meter_id ,"RN-96")
    
    generationDataSuccessiveDiff = {}
    drawalDataSuccessiveDiff = {}

    for index,item in enumerate(componentWiseGraphData1) :
        generationDataSuccessiveDiff[item['name']] = successiveDifferencePercentage(item['y'])

    for index,item in enumerate(componentWiseGraphData2) :
        drawalDataSuccessiveDiff[item['name']] = successiveDifferencePercentage(item['y'])

    _hoverDataGenerationRed = {}
    _hoverDataDrawalRed = {}
    _hoverDataGenerationGreen = {}
    _hoverDataDrawalGreen = {}

    for key in generationDataSuccessiveDiff.keys():
        _hoverDataGenerationRed[key] = []
        _hoverDataGenerationGreen[key] = []

    for key in drawalDataSuccessiveDiff.keys():
        _hoverDataDrawalRed[key] = []
        _hoverDataDrawalGreen[key] = []


    redData = {'key' : 'red' , 'xVal' : [] , 'yVal' : [] ,'genVal' : [] , 'drwVal' : [], 'hoverDataGeneration' : _hoverDataGenerationRed , 'hoverDataDrawal' : _hoverDataDrawalRed}
    greenData = {'key': 'green' , 'xVal' : [] , 'yVal' : [],'genVal' : [] , 'drwVal' : [], 'hoverDataGeneration' : _hoverDataGenerationGreen , 'hoverDataDrawal' : _hoverDataDrawalGreen}

    for loopIndex,item in enumerate(successivePercentLossDifferenceList):
        if((item is not None) and (abs(item) >= threshold)) :
            redData['xVal'].append(fullXAxisData[loopIndex+1])
            redData['yVal'].append(item)
            redData['genVal'].append(successivePercentGenerationDifferenceList[loopIndex])
            redData['drwVal'].append(successivePercentDrawalDifferenceList[loopIndex])

            for key in generationDataSuccessiveDiff.keys() :
                redData['hoverDataGeneration'][key].append(generationDataSuccessiveDiff[key][loopIndex])
                        
            for key in drawalDataSuccessiveDiff.keys() :
                redData['hoverDataDrawal'][key].append(drawalDataSuccessiveDiff[key][loopIndex])

        else :
            print("in green")
            greenData['xVal'].append(fullXAxisData[loopIndex+1])
            greenData['yVal'].append(item)
            greenData['genVal'].append(successivePercentGenerationDifferenceList[loopIndex])
            greenData['drwVal'].append(successivePercentDrawalDifferenceList[loopIndex])

            for key in generationDataSuccessiveDiff.keys() :
                greenData['hoverDataGeneration'][key].append(generationDataSuccessiveDiff[key][loopIndex])

            for key in drawalDataSuccessiveDiff.keys() :
                greenData['hoverDataDrawal'][key].append(drawalDataSuccessiveDiff[key][loopIndex])


    dataToSend = [
        {
          'type': "scatter",
          'mode': "markers",
          'x': greenData['xVal'],
          'y': greenData['yVal'],
          'genVal' : greenData['genVal'],
          'drwVal' : greenData['drwVal'],
          'hoverDataGeneration' : greenData['hoverDataGeneration'],
          'hoverDataDrawal' : greenData['hoverDataDrawal'],
          'marker': { 'color' : "green" },
          'name': "|dL/dt| < " + str(threshold),
        },
        {
          'type': "scatter",
          'mode': "markers",
          'x': redData['xVal'],
          'y': redData['yVal'],
          'genVal' : redData['genVal'],
          'drwVal' : redData['drwVal'],
          'hoverDataGeneration' : redData['hoverDataGeneration'],
          'hoverDataDrawal' : redData['hoverDataDrawal'],
          'marker': { 'color' : "red" },
          'name': "|dL/dt| >= " + str(threshold),
        },
      ]

    # return {'graphData' : graphData ,'componentWiseGraphData1' : componentWiseGraphData1, 'componentWiseGraphData2' : componentWiseGraphData2}
    # return {'generationDataSuccessiveDiff' : generationDataSuccessiveDiff , 'drawalDataSuccessiveDiff' : drawalDataSuccessiveDiff }
    return {'dataToSend' : dataToSend}