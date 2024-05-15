
import re
import os
from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
from shutil import copyfile
from pathlib import Path

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

def componentWiseMeterAnalysis(path ,meterEndToAnalyse):
    print("inside componentWiseMeterAnalysis")
    
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
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

    ################################################### Get all the equations of Fictitious Meters #############################################

    # 'fictMeterDict' stores equation data. 
    # fictMeterDict['(BM-99)'] gives      -(BI-09)*0.97899. trim spaces later. \n trimmed


    fctCFG = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FICTMTRS.CFG', "r")
    fList = fctCFG.readlines()
    # print(len(fList[len(fList)-2]))
    # print((fList[len(fList)-2])[:3])

    fctCFG.close()
    startIndex = 1
    # print(fList)

    fictMeterDict = {}

    fictMeterIdIndex = []
    for elemIndex in range(len(fList)) :
        if(fList[elemIndex].split()[0].isdigit() and int(fList[elemIndex].split()[0]) == startIndex) :
            fictMeterIdIndex.append(elemIndex)
            startIndex += 1
    if(fList[len(fList)-2][:3] == "END") :
        fictMeterIdIndex.append(len(fList)-2)  # Must append END index too
    else :
        print("Error")
        
    for i in range(len(fictMeterIdIndex)-1) :
    #     print("i value " + str(fictMeterIdIndex[i]))
        fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] = ""

        for j in range(fictMeterIdIndex[i]+1,fictMeterIdIndex[i+1]) :
            fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] = fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] + (fList[j].replace('\n',''))

    # print(fictMeterDict['(BM-99)'])
    # print(len(fictMeterDict))

    #################################################### Component Seperate Function ####################################################################

    if(getMeterInfoById(meterEndToAnalyse) is not None) :  # So it is a real meter
        meterEquation = meterEndToAnalyse
    else : # Fict Meter
        meterEquation = fictMeterDict['('+ meterEndToAnalyse +')']

    meterEquation = meterEquation.replace(' ','')
    meterEquation = meterEquation.replace(u'\xa0', u'') # Non breaking space.
    meterEquation = meterEquation.replace('\t','')
    meterEquation = meterEquation.replace('\n','')

    meterIdPattern = re.compile(r'[A-Z]{2}-[0-9]{2}')
    components = re.findall(meterIdPattern, meterEquation)
    print(len(components))


    ################################################### Dynamic plotting #################################################################

    # print(searchMeterNumber('ER-02'))
    dynamicGraphData = []

    for index,component in enumerate(components) :
        print(component)
        if(index == 0 or index == 1) :
            componentData = {'x' : [] , 'y' : [] , 'stackgroup' : 'one' , 'name' : component}
        else :
            componentData = {'x' : [] , 'y' : [] , 'stackgroup' : 'one', 'visible': "legendonly" , 'name' : component}

        end = searchMeterNumber(component)

        xAxisData = []
        endData = []
        for mwhDate in mwhDates :
            
            timeArray = timeSeries()
            fullDayTimeStamp = [mwhDate + "  " + tStamp for tStamp in timeArray]
            xAxisData = xAxisData + fullDayTimeStamp



            try :
                # dataEnd = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end + '.MWH' ,header = None)

                if(os.path.exists(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end + '.MWH')) :
                    dataEnd = pd.read_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate +'/' + end + '.MWH', header = None)  # May give FileNotFoundError
                else :
                    dataEnd = pd.read_csv(meterFileMainFolder+'/Fictitious Meter MWH Files/' + mwhDate +'/' + end + '.MWH', header = None)

                dfSeriesEnd = pd.DataFrame(dataEnd)
                dfEnd = dfSeriesEnd[0]
                # dfEnd
                for i in range(1, len(dfEnd)) :
                    oneHourDataEnd = [changeToFloat(x) for x in dfEnd[i].split()[1:]]
                    endData = endData + oneHourDataEnd
            except FileNotFoundError :
                endData = endData + [None]*96
        
        componentData['x'] = xAxisData
        componentData['y'] = endData

        dynamicGraphData.append(componentData)
    # #####################################################################################
 
################################################################################################
    return dynamicGraphData