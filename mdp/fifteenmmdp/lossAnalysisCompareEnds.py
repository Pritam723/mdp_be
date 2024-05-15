from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
import numpy as np


def percentageViolation(p1, p2, percentageDiff) :
    p1 = abs(p1)
    p2 = abs(p2)
    
    if(float(p1) == float(0)) :
        diff = 'Infinite'
    else :    
        diff = abs((p2-p1)/p1)*100
    
    if(diff == 'Infinite') : 
        return {'status' : True, 'diff' : 'Infinite'}
    elif(diff >= abs(float(percentageDiff))) :
        return {'status' : True, 'diff' : round(diff, 2)}
    else :
        return {'status' : False, 'diff' : round(diff, 2)}

def mwhViolation(p1, p2, mwhDiff) :
    p1 = abs(p1)
    p2 = abs(p2)
    
    diff = abs(p1-p2)
    
    if(diff >= abs(float(mwhDiff))) :
        return {'status' : True, 'diff' : round(diff, 2)}
    else :
        return {'status' : False, 'diff' : round(diff,2)}
    

def findViolations(df1, df2, fromTime, toTime, parameter, percentageDiff, mwhDiff, violationCountOnly = True) :
    print(fromTime, toTime, parameter, percentageDiff, mwhDiff)
    
    fromHr, fromMin = fromTime.split(":")
    toHr, toMin = toTime.split(":")
    
    fromHr = int(fromHr)
    fromMin = int(fromMin)
    toHr = int(toHr)
    toMin = int(toMin)

    startBlock = fromHr * 4 + fromMin//15
    endBlock = toHr * 4 + toMin//15

    print("This is start & end block")
    print(startBlock, endBlock)

    end1_fullDayData = []
    end2_fullDayData = []

    i = fromHr + 1
    while(i < toHr + 2) :
        if(i == fromHr + 1) :
            end1_fullDayData = end1_fullDayData + df1[i].split()[fromMin//15 + 1 : ]
            end2_fullDayData = end2_fullDayData + df2[i].split()[fromMin//15 + 1 : ]

        elif(i == toHr + 1) :
            end1_fullDayData = end1_fullDayData + df1[i].split()[1 : toMin//15 + 2]
            end2_fullDayData = end2_fullDayData + df2[i].split()[1 : toMin//15 + 2]

        else :
            end1_fullDayData = end1_fullDayData + df1[i].split()[1 : ]
            end2_fullDayData = end2_fullDayData + df2[i].split()[1 : ]

        i = i + 1

    violationCount = 0
    violationInfo = []
    
    block = startBlock
    while(block <= endBlock) :
        currentTS = str(block//4).zfill(2) + ":" + str(block%4 * 15).zfill(2)
        # print(currentTS)
        p1 = float(end1_fullDayData[block - startBlock])
        p2 = float(end2_fullDayData[block - startBlock])
        block = block + 1
        p_violation = percentageViolation(p1, p2, percentageDiff)
        m_violation = mwhViolation(p1, p2, mwhDiff)

        if(parameter == "Percentage") :
            if(p_violation['status']) :
                violationCount = violationCount + 1
                violationInfo.append(f"Percentage Difference at {currentTS} is {p_violation['diff']}%. END1 value is {p1}, END2 value is {p2}.")
        elif(parameter == "MWH") :
            if(m_violation['status']) :
                violationCount = violationCount + 1
                violationInfo.append(f"MWH Difference at {currentTS} is {m_violation['diff']} MWH. END1 value is {p1}, END2 value is {p2}.")
        elif(parameter == "Percentage & MWH") :
            if(p_violation['status'] and m_violation['status']) :
                violationCount = violationCount + 1
                violationInfo.append(f"Percentage Difference at {currentTS} is {p_violation['diff']}%. MWH Difference at {currentTS} is {m_violation['diff']} MWH. END1 value is {p1}, END2 value is {p2}.")
        else :
            if(p_violation['status'] or m_violation['status']) :
                violationCount = violationCount + 1
                violationInfo.append(f"Percentage Difference at {currentTS} is {p_violation['diff']}%. MWH Difference at {currentTS} is {m_violation['diff']} MWH. END1 value is {p1}, END2 value is {p2}.")
    if(violationCountOnly) :
        return violationCount, []
    else :
        return violationCount,violationInfo


def getLineDetails(voltageLevel, path) :

    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile", path)

    voltage_levels = [33,66,132,220,400,765]

    voltagewise_linedetails = {}

    for voltage_level in voltage_levels :
        voltagewise_linedetails[voltage_level] = []

    xl = pd.ExcelFile(meterFileMainFolder + "/NPC Files/Necessary Files Local Copy/GraphConfiguration.xlsx")

    sheets = xl.sheet_names

    for sheet in sheets :
        data = xl.parse(sheet)

        if 'Voltage' not in list(data.keys()) :
            continue
        else :
            # print("Let's Work")


            for index, row in data.iterrows():
                # print(row['Feeder Name'], row['Voltage'])
                if(row['Voltage'] in voltage_levels) :
                    feederDetails = {'Feeder Name' : row['Feeder Name'], 'End1' : row['End1'], 'End2' : row['End2'] }
                    voltagewise_linedetails[row['Voltage']].append(feederDetails)

    return voltagewise_linedetails[int(voltageLevel)] 

def singleDayViolations(dateObject, end1, end2, fromTime, toTime, violations,parameter,percentageDiff,mwhDiff, path, violationCountOnly = True) :    
    # print(dateObject)
    
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'

    ################################################### All RealMeters here. List of fict meters : #############################################

    realMeterInfo = []
    masterData = open(meterFileMainFolder + '/NPC Files/Necessary Files Local Copy/master.dat', "r")
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
            # print(Loc_Id + " not found in master.dat")
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
    fictInfoData = open(meterFileMainFolder + '/NPC Files/Necessary Files Local Copy/FICTMTRS.dat', "r")

    fictInfoDataList = fictInfoData.readlines()
    fictInfoData.close()
    for elem in fictInfoDataList :
        if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
            # print(elem.split())
            fictMeterInfo.append({"Loc_Id" : elem.split()[0] , "Fict_Meter_No" : elem.split()[1] })


    def getFictMeterInfoById(Loc_Id) :

        fictMeterDetails =  [meter for meter in fictMeterInfo if meter['Loc_Id'] == Loc_Id]

        if(len(fictMeterDetails) < 1) :
            # print(Loc_Id + " not found in FICTMTRS.dat")
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

    dataNonAvailability = False
    violationCount = 0
    
    dateStr = dateObject.strftime("%d-%m-%y")
    
    try :
        if(getMeterInfoById(end1) is not None) :
            end1_data = pd.read_csv(realMeterMWHPath + dateStr + "/" + searchMeterNumber(end1) + '.MWH', header = None)
        else :
            end1_data = pd.read_csv(fictMeterMWHPath + dateStr + "/" + searchMeterNumber(end1) + '.MWH', header = None)
        
        dfSeriesEnd1 = pd.DataFrame(end1_data)
        df1 = dfSeriesEnd1[0]
        
        
        if(getMeterInfoById(end2) is not None) :
            end2_data = pd.read_csv(realMeterMWHPath + dateStr + "/" + searchMeterNumber(end2) + '.MWH', header = None)
            
        else :
            end2_data = pd.read_csv(fictMeterMWHPath + dateStr + "/" + searchMeterNumber(end2) + '.MWH', header = None)
        
        dfSeriesEnd2 = pd.DataFrame(end2_data)
        df2 = dfSeriesEnd2[0]
        
        # print(df1, df2)
        
        violationCount, violationInfo = findViolations(df1, df2, fromTime, toTime, parameter, percentageDiff, mwhDiff, violationCountOnly = violationCountOnly)
        
        if(violationCount > 0) :
            violations.append({'key' : dateStr, 'label' : f'{dateStr} : There is/are {violationCount} violation(s) on this date (From {fromTime} to {toTime})', 'violationInfo' : violationInfo})
        
    except FileNotFoundError :
        dataNonAvailability = True
        # violations.append({'key' : dateStr, 'label' : f'{dateStr} : Data of atleast one End is not available for this date', 'violationInfo' : []})

    # print(dataNonAvailability)


def lossAnalysisCompareEnds(request, path):
    

    voltageLevel = request.POST['voltageLevel']
    parameter = request.POST['parameter']
    percentageDiff = request.POST['percentageDiff']
    mwhDiff = request.POST['mwhDiff']
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    # Dates are in String Format. For 12th June 2023 we have 06/12/2023 00:00:00
    
    # voltageLevel = '33'
    # parameter = 'Percentage'
    # percentageDiff = '2.00'
    # mwhDiff = '0.2'
    # startDate = '06/12/2023 00:00:00'
    # endDate = '06/18/2023 23:45:00'

    startDateObject = datetime.strptime(startDate, '%m/%d/%Y %H:%M:%S')
    endDateObject = datetime.strptime(endDate, '%m/%d/%Y %H:%M:%S')
    
    # print(startDateObject, endDateObject)
    lineDetails = getLineDetails(voltageLevel, path)
    # print(lineDetails)
    
    lineWiseViolationDetails = []
    
    for line in lineDetails :
        feederName = line['Feeder Name']
        end1 = line['End1']
        end2 = line['End2']
        
        if(isNaN(end1)) :
            end1 = "Meter Not Specified"
        if(isNaN(end2)) :
            end2 = "Meter Not Specified"
        
        violations = []

        if(startDateObject.date() == endDateObject.date()) :
            print("Start date end date same")
            fromTime = datetime.strftime(startDateObject, "%H:%M")
            toTime = datetime.strftime(endDateObject, "%H:%M")
            singleDayViolations(startDateObject.date(), end1, end2, fromTime, toTime, violations,parameter,percentageDiff,mwhDiff, path)

        else :
            for day in range((endDateObject - startDateObject).days + 1) :
                dateObj = startDateObject+timedelta(days=day)
                print(dateObj)

                if(dateObj.date() == startDateObject.date()) :
                    print("This is start date")
                    fromTime = datetime.strftime(startDateObject, "%H:%M")
                    singleDayViolations(dateObj.date(), end1, end2, fromTime, '23:45', violations,parameter,percentageDiff,mwhDiff, path)

                elif(dateObj.date() == endDateObject.date()) :
                    print("This is end date")
                    toTime = datetime.strftime(endDateObject, "%H:%M")
                    singleDayViolations(dateObj.date(), end1, end2, '00:00', toTime, violations,parameter,percentageDiff,mwhDiff, path)

                else :
                    print("Date in between")
                    singleDayViolations(dateObj.date(), end1, end2, '00:00', '23:45', violations,parameter,percentageDiff,mwhDiff, path)

        # print(violations)
        if(len(violations) > 0) :
            violations.append({'key' : f"{feederName} Download Button", 'voltageLevel' : voltageLevel,'end1' : end1, 'end2' : end2, 'startDate' : startDate, 'endDate' : endDate, 'parameter' : parameter,'percentageDiff' : percentageDiff, 'mwhDiff' : mwhDiff,  'label' : f'Download violation details', 'type' : 'download'})
            lineWiseViolationDetails.append({'key' : feederName, 'label' : f'{feederName}({end1} vs {end2})', 'children' : violations})

    return(lineWiseViolationDetails)