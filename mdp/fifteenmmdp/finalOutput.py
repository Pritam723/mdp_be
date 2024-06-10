import os
from .models import AllMeterFiles,FinalOutputFile
from django.core.files import File
from django.conf import settings
from .supportingFunctions import *
import pandas as pd
import json
from datetime import time,timedelta,datetime
import math
from .finalOutputExcel import createFinalOutputExcel



# Added for Absolute Calculation
def getCorrespondingClosingIdx(tokens, t):
#     print(tokens)
    count = 1
    
    for token in tokens:
        if(token == '('):
            count = count + 1
        elif(token == ')'):
            count = count - 1
            if(count == 0): return t
        else:
            pass
    
        t = t + 1
    
    return t

# decideSpace(16,_part[i])

# Fixing the gaps between the headers
def headerInfoSpaceFix(_headerInfo,_spacingInfo):
    for i in range(len(_headerInfo[0])) :
        for j in range(len(_headerInfo)) :
            _headerInfo[j][i] = " " * (_spacingInfo[i] - len(_headerInfo[j][i].split('@')[0].rstrip())) + _headerInfo[j][i].split('@')[0].rstrip()
    return _headerInfo

def titleSpaceAdjust(_title,_spacingInfo) :
    _title = _title.lstrip()
    _title = _title.rstrip()
    lSpace = math.floor((sum(_spacingInfo) - len(_title))/2)
    returnTitle = " " * max(0, int(lSpace)) + _title
    return returnTitle

def removeBlank(_headerInfo,_equations) :
    indicesToRemove = []
    for i in range(len(_equations)) :
        isBlank = True
        for j in range(len(_headerInfo)) :
            # isBlank = (_headerInfo[j][i] == _equations[i] == '') and isBlank
            isBlank = (_headerInfo[j][i].strip() == _equations[i].strip() == '') and isBlank

        if(isBlank == True) :
            indicesToRemove.append(i)  

    #     print(indicesToRemove)
    for index in sorted(indicesToRemove, reverse=True):
        del _equations[index]
        for j in range(len(_headerInfo)) :
            del _headerInfo[j][index]
    #     print(_headerInfo)
    #     print(_equations)
    return _headerInfo,_equations

def removeBlankMvarConfig(_headerInfo,_equations) :
    indicesToRemove = []
    for i in range(len(_equations)) :
        if(_headerInfo[i].strip() == _equations[i].strip() == '') :
            indicesToRemove.append(i)  
            
    for index in sorted(indicesToRemove, reverse=True):
        del _equations[index]
        del _headerInfo[index]
  
    return _headerInfo,_equations

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

# def frequencyData() :
#     fr = "A list of 96 items" (as a string)
#     return fr.split()

def transposeSpaceadjusted(l1,eqs,si):
    print("Inside transpose space adjust")
    l2 = []
    # iterate over list l1 to the length of an item 
    for i in range(len(l1[0])):
        # print(i)
        row =[]
    #         print(l1)
        for itemIndex,item in enumerate(l1):
    #             print(i,itemIndex,item)
    #             print(item[i])
            # appending to new list with values and index positions
            # i contains index position and item contains values
            if(eqs[itemIndex].strip() == 'TIME' or eqs[itemIndex].strip() == 'DATE' or eqs[itemIndex].strip() == 'FREQ') :
                item[i] = " " * (si[itemIndex] - len(item[i])) + item[i]
                row.append(item[i])
            else :
                if(item[i][0] != '-') :
                    item[i] = '+' + item[i]
                item[i] = " " * (si[itemIndex] - len(item[i])) + item[i]
                row.append(item[i])
        l2.append(row)
    #     print(l2)
    print("Returning from transpose space adjust")

    return l2

def signSpaceAdjusted(_totalSummaryData,eqs,si) :
    # print(_totalSummaryData)
    # print(eqs)
    # print(si)
    _returnTotalSummary = []
    for itemIndex,item in enumerate(_totalSummaryData) :
        # print(str(itemIndex) + "hi " + eqs[itemIndex])
        if(eqs[itemIndex].strip() == 'TIME' or eqs[itemIndex].strip() == 'DATE' or eqs[itemIndex].strip() == 'FREQ') :
            # print(item + " inside if")

            item = " " * (si[itemIndex] - len(item)) + item
            _returnTotalSummary.append(item)
        else :
            # print(item + " inside else")

            if(item[0] != '-') :
                item = '+' + item
            item = " " * (si[itemIndex] - len(item)) + item
            _returnTotalSummary.append(item)
    return _returnTotalSummary

def dirJsonFinalOutput(nPath,_meterData,finalOutputDict):
    d = {'name': os.path.basename(nPath)}
    # d['size'] = str("{0:.2f}".format((os.stat(nPath).st_size / 1024)) + "KB")
    if os.path.isdir(nPath):
        d['type'] = "folder"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
        d['files'] = [dirJsonFinalOutput(os.path.join(nPath, x),_meterData,finalOutputDict) for x in os.listdir(nPath)]
    else:

        print(os.path.basename(nPath))
        d['id'] = finalOutputDict['lastIndex']
        finalOutputDict[finalOutputDict['lastIndex']] = os.path.relpath(nPath, 'fifteenmmdp/media')
        finalOutputDict['lastIndex'] = finalOutputDict['lastIndex'] + 1
        
        d['type'] = "file"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
       

    return d


def createFinalOutput(path,_meterData):
    print("Insside createFinalOutput")

    ct1 = datetime.now()    
    # meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    # relativeFilePathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)

    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    relativeFilePath = meterFileMainFolder+'/Final Output Files/'
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)

    # if not os.path.exists(meterFileMainFolder +'/Fictitious Meter MWH Files(Copy)'): 
    #     os.makedirs(meterFileMainFolder + '/Fictitious Meter MWH Files(Copy)')
    if not os.path.exists(meterFileMainFolder +'/Final Output Files'):
        os.makedirs(meterFileMainFolder + '/Final Output Files')

    ################################################### All RealMeters here. List of Real meters : #############################################

    # [{'Loc_Id': 'FK-01', 'Meter_No': 'ER-1649-A', 'ctr': '500', 'ptr': '3636.3636'} ,{'Loc_Id': 'FK-02', 'Meter_No': 'ER-1646-A', 'ctr': '500', 'ptr': '3636.3636'}]
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

    ################################################### Evalutate Function #################################################################

    def takeAbsolute(_fictMeterId,_mwhDate,valueToAppend) :
        print(type(valueToAppend))
        if(isinstance(valueToAppend, pd.core.series.Series)):
            print("Reached at takeAbsolute if. Need to take absolute of Series data")

            returnSeries = pd.Series([],dtype=object)
            seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ',_mwhDate] +  [str(e) for e in list(map(lambda x: abs(float(x)), valueToAppend[0].split()[3:]))]
            returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

            i = 1
            while i < 25 :
                seriesBody = [valueToAppend[i].split()[0]] +  [str(e) for e in list(map(lambda x: abs(float(x)), valueToAppend[i].split()[1:]))]
                print("Series body absolute is ")
                print(seriesBody)
                # seriesBody = ["0000"] + Rest of the calculated data
                # print(seriesBody)
                # seriesBody = spaceAdjustFictMeterBody(seriesBody)
                returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)
                
                i+=1

            return returnSeries

        if(isinstance(valueToAppend, float)):
            return abs(valueToAppend)

    def ffOperation(a,b,op) :  # Both operands are float
        if op == '+': return float(a) + float(b)
        if op == '-': return float(a) - float(b)
        if op == '*': return float(a) * float(b)
        if op == '/': 
            if(float(a) == float(0) or float(b) == float(0)) : return float(0)
            else : return float(a)/float(b)

    def ssOperation(_fictMeterId,_mwhDate,a,b,op) : # Both operands are PandasSeries
        #     print("Inside ssOperation")
        #     print(a)
        #     print(b)
        returnSeries = pd.Series([],dtype=object)
        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ',_mwhDate] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[0].split()[3:], b[0].split()[3:]))]
        #     print("sending")
        #     print(seriesHeader)

        #     seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)
        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[i].split()[1:], b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
        #         seriesBody = spaceAdjustFictMeterBody(seriesBody)
            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)
            
            i+=1

        return returnSeries

    def fsOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand float, second operand PandasSeries
        #     print("Inside fsOperation")

        returnSeries = pd.Series([],dtype=object)

        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ', _mwhDate] +  [str(e) for e in list(map(lambda y : ffOperation(a,y,op), b[0].split()[3:]))]
        #     seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)
        
        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [b[i].split()[0]] +  [str(e) for e in list(map(lambda y: ffOperation(a,y,op), b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
        #         seriesBody = spaceAdjustFictMeterBody(seriesBody)

            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    def sfOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand PandasSeries, second operand float
        
        returnSeries = pd.Series([],dtype=object)

        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ',_mwhDate] +  [str(e) for e in list(map(lambda x : ffOperation(x,b,op), a[0].split()[3:]))]
        #     seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)

        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x: ffOperation(x,b,op), a[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
        #         seriesBody = spaceAdjustFictMeterBody(seriesBody)

            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    # Function to perform arithmetic operations.

    def applyOp(_fictMeterId,_mwhDate,a, b, op):
        #     print("Inside applyOp")

        if(isinstance(a, pd.core.series.Series) and isinstance(b, float)) :
        #         print("1")
            return(sfOperation(_fictMeterId,_mwhDate,a,b,op))

        elif(isinstance(a, float) and isinstance(b, pd.core.series.Series)) :
        #         print("2")

            return(fsOperation(_fictMeterId,_mwhDate,a,b,op))

            
        elif(isinstance(a, float) and isinstance(b, float)) :
        #         print("3")

            return(ffOperation(a,b,op))
        
        elif(isinstance(a, pd.core.series.Series) and isinstance(b, pd.core.series.Series)) :
        #         print("4")

            return(ssOperation(_fictMeterId,_mwhDate,a,b,op))
        else :
        #         print("5")
            pass


    # Python3 program to evaluate a given expression where tokens are separated by space.

    # Function to find precedence
    # of operators.
    def precedence(op):
        
        if op == '+' or op == '-':
            return 1
        if op == '*' or op == '/':
            return 2
        return 0
 

    # Function that returns value of
    # expression after evaluation.
    def evaluate(_fictMeterId,_mwhDate,tokens):
        
        # stack to store integer values.
        values = []
        
        # stack to store operators.
        ops = []
        i = 0
        
        while i < len(tokens):
            
            # Current token is a whitespace,
            # skip it.
            if tokens[i] == ' ':
                i += 1
                continue
            
            # Current token is an opening 
            # brace, push it to 'ops'
            elif tokens[i] == '(':
                ops.append(tokens[i])
        #             print("Printing 1st : " +str(ops))
            # Current token is a number, push 
            # it to stack for numbers.


            elif tokens[i].isalpha() and tokens[i : i + 4].upper() == 'ABS(' :
                print("I got absolute")
                idx = getCorrespondingClosingIdx(tokens[i+4: ], i+4)

                #  We want to calculate the expression tokens[i+1 to idx - 1]

                newExp = tokens[i+4: idx]

                print(newExp)
                if(newExp[0] == '+' or newExp[0] == '-'):
                    newExp = '0' + newExp

                newExpValue = evaluate(_fictMeterId,_mwhDate,newExp)

                newExpValueAbsolute = takeAbsolute(_fictMeterId,_mwhDate,newExpValue)

                print(" Return value is ")
                print(newExpValueAbsolute)

                values.append(newExpValueAbsolute)

                # Finally we need to move i to idx + 1.
                i = idx # +1 will be done at last by default.



            # Current token is a meter ID, push 
            # it to stack for numbers.
            elif tokens[i].isalpha() and tokens[i : i + 4].upper() != 'ABS(':
                val = tokens[i : i+5].replace("_","-")
                # data = pd.read_csv('mySEMBASE/'+ _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)
                if(os.path.exists(realMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH')) :
                    data = pd.read_csv(realMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)  # May give FileNotFoundError
                else :
                    data = pd.read_csv(fictMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)
                # print(data)
                dfSeries = pd.DataFrame(data)
                df = dfSeries[0]
                values.append(df)
                
                i+=4              
                
            elif(tokens[i].isdigit() or tokens[i] == '.') :
                val = ""
                
                # There may be more than one
                # digits in the number.
                while (i < len(tokens) and (tokens[i].isdigit() or tokens[i] == '.')):             
                    val = val + tokens[i]
                    i += 1
                
                values.append(float(val))
        #             print(values) 
                # right now the i points to 
                # the character next to the digit,
                # since the for loop also increases 
                # the i, we would skip one 
                #  token position; we need to 
                # decrease the value of i by 1 to
                # correct the offset.
                i-=1
            
            # Closing brace encountered, 
            # solve entire brace.
            elif tokens[i] == ')':
            
                while len(ops) != 0 and ops[-1] != '(':
                
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
        #                 print(ops)

                    values.append(applyOp(_fictMeterId,_mwhDate,val1, val2, op))
                
                # pop opening brace.
                ops.pop()
        #             print(ops)
            # Current token is an operator.
            else:
            
                # While top of 'ops' has same or 
                # greater precedence to current 
                # token, which is an operator. 
                # Apply operator on top of 'ops' 
                # to top two elements in values stack.
                while (len(ops) != 0 and
                    precedence(ops[-1]) >=
                    precedence(tokens[i])):
                            
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
                    
                    values.append(applyOp(_fictMeterId,_mwhDate,val1, val2, op))
                
                # Push current token to 'ops'.
                ops.append(tokens[i])
            
            i += 1
        
        # Entire expression has been parsed 
        # at this point, apply remaining ops 
        # to remaining values.
        while len(ops) != 0:
            
            val2 = values.pop()
            val1 = values.pop()
            op = ops.pop()
                    
            values.append(applyOp(_fictMeterId,_mwhDate,val1, val2, op))
        
        # Top of 'values' contains result,
        # return it.
        return values[-1]


    ################################################### Performing main operation #######################################
    
    with open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/ConfigurationFile.xlsx', "rb") as f: # input the .xlsx
        data = pd.read_excel(f,sheet_name="Configuration",engine='openpyxl',header = None)
        f.close()
        
    df = pd.DataFrame(data)
    df = df.fillna('')
    # print(df)
    df.iloc[4][0].rstrip() == 'EQUATION :'
    # allConfigurations = [ {'Configuration Name' : 'AL1_MWH' , 'TITLE' : 'HVDC ALOPURDUAR AUX CONSUMPTION TRANSFORMER FLOW (in MWH)', 'HEADERLINE' : [] , 'EQUATION' : []} , {} , {}]

    dfLength = len(df)
    # print(df.iloc[0][1])
    allConfigurations = []
    i = 0
    while i < (len(df)) :
        currentConfig = {'Configuration Name' : '' , 'EXTENSION' : '' ,'TITLE' : '' ,'HEADERLINE' : [], 'EQUATION' : []}
        if(df.iloc[i][0].rstrip() == 'Configuration Name/Item/Extension') :

            currentConfig['Configuration Name'] = df.iloc[i][1]
            currentConfig['EXTENSION'] = df.iloc[i][3]

            currentConfig['TITLE'] = df.iloc[i+1][1]
            i = i+2
            j = i
            while df.iloc[j][0].rstrip() != 'EQUATION :' :
                currentConfig['HEADERLINE'].append(list(df.iloc[j][1:]))
                j = j+1
            i = j
            currentConfig['EQUATION'] = (list(df.iloc[i][1:]))
            allConfigurations.append(currentConfig)
        if(df.iloc[i][0].rstrip() == 'END') :
            i = i+1
            continue
        i = i+1

    # print((allConfigurations))
    # for item in (allConfigurations) :
    #     print((item['EQUATION']))
    #     print((item['HEADERLINE'][0]))
    rgnSummary = {'Date' : [] , 'NER_DRL' : [] , 'SR_DRL' : [] , 'WR_DRL' : [] , 'NR_DRL' : []}

    for configuration in (allConfigurations) :
        configName = configuration['Configuration Name']
        extension = configuration['EXTENSION']

        if(extension == 'RGN') :
            eqMapForRgnSumm = {'-(NE-91)' : 'NER_DRL' ,'-(SR-91)' : 'SR_DRL' ,'-(WR-91)' : 'WR_DRL' ,'-(NR-91)' : 'NR_DRL'  }

        title = configuration['TITLE']
        headerInfo,equations = removeBlank(configuration['HEADERLINE'],configuration['EQUATION'])
        #     print(headerInfo)
        spacingInfo = []
        for i in range(len(headerInfo[0])) :
        #     print(i)
            maxSpace = 0
            for j in range(len(headerInfo)) : # Will have 0,1 here
        #         print(len(headerInfo[j][i]))
                if(len(headerInfo[j][i].split('@')) > 1) :
                    maxSpaceLocal = max(len(headerInfo[j][i].split('@')[0].rstrip()) + 4, int(headerInfo[j][i].split('@')[-1]))
                else :
                    maxSpaceLocal = len(headerInfo[j][i].rstrip()) + 4

                if maxSpaceLocal > maxSpace : maxSpace = maxSpaceLocal
            if(equations[i].strip() == 'TIME' or equations[i].strip() == 'FREQ' or equations[i].strip() == 'DATE') :
                spacingInfo.append(maxSpace)
            else :
                spacingInfo.append(max(maxSpace,14))  ## Changed from 12 to 14

        print(spacingInfo)
        

        headerInfoSpacingFixed = headerInfoSpaceFix(headerInfo,spacingInfo)
    #     print(headerInfoSpacingFixed)
        
        for mwhDate in mwhDates :

            if(extension == 'RGN') :
                rgnSummary['Date'].append(mwhDate)


            if not os.path.exists(meterFileMainFolder + '/Final Output Files/'+ mwhDate + "/"):
                os.makedirs(meterFileMainFolder + '/Final Output Files/'+ mwhDate + "/")
            
            if os.path.exists(realMeterMWHPath + mwhDate + '/masterFrequency.MFD'):
                frData = pd.read_csv(realMeterMWHPath + mwhDate + '/masterFrequency.MFD' , header=None)
                freq = frData[0][1].split()
            else :
                freq = ['--']*96
            ##################################### Working with the outpt ###################################################################
            ################################## Header Fill #############################################################################

            configurationOutput = pd.Series([],dtype=object)
            configurationOutput = configurationOutput.append(pd.Series(' '), ignore_index=True)
            configurationOutput = configurationOutput.append(pd.Series('ENERGY ACCOUNTING USING SPECIAL ENERGY METER FOR ' + mwhDate), ignore_index=True)
            configurationOutput = configurationOutput.append(pd.Series('-'*sum(spacingInfo)), ignore_index=True)
            configurationOutput = configurationOutput.append(pd.Series(titleSpaceAdjust(title,spacingInfo)), ignore_index=True)
            for header in headerInfoSpacingFixed :
                configurationOutput = configurationOutput.append(pd.Series(''.join(header)), ignore_index=True)

            configurationOutput = configurationOutput.append(pd.Series('-'*sum(spacingInfo)), ignore_index=True)

            ################################## Header Done #############################################################################
            ################################## Body Fill ###############################################################################
            rowWiseData = [0]*len(equations)
            totalSummaryData = [0]*len(equations)

            for equationIndex, equation in enumerate(equations):
                #print((equationIndex, equation))

                if(equation.strip() == 'TIME' or equation.strip() == 'DATE' or equation.strip() == 'FREQ') :
                    if(equation.strip() == 'TIME') : 
                        rowWiseData[equationIndex] = timeSeries()
                        totalSummaryData[equationIndex] = 'TOTAL'
                    elif(equation.strip() == 'FREQ') : 
                        rowWiseData[equationIndex] = freq
                        totalSummaryData[equationIndex] = ''
                    else :
                        pass

                else : # i.e. it should be an meter equation
                    try :
                        equation = equation.replace(' ','')
                        equation = equation.replace(u'\xa0', u'') # Non breaking space.
                        equation = equation.replace('\t','')
                        equation = equation.replace('\n','')
                        # print('after trim')
                        # print(equation)
                        # print(len(equation))
                        
                        rawEqForRgnSumm = equation
                        
                        if(equation[0] == '+' or equation[0] == '-') :
                            equation = '0' + equation

                        equation = re.sub('([A-Z]{2})-([0-9]{2})', r'\1_\2', equation)

                        df = evaluate("XY-99",mwhDate,equation)
                        # print(df)
                        # Check if df is a series or float now. Act accordingly.
                        # If df is float, it implies that fictMeterId,mwhDate etc info never used. Only ffOperation() is called.

                        fullDayData = []
                        hour = 1
                        while(hour < 25) :
                            fullDayData = fullDayData + [f'{float(x) :.6f}' for x in df[hour].split()[1:]]
                            hour += 1
                        print("append fullDayData in rowWiseData")
                        # print(fullDayData)
                        rowWiseData[equationIndex] = fullDayData
                        totalSummaryData[equationIndex] = f'{sum([float(x) for x in fullDayData]) :.6f}'

                        if(extension == 'RGN') :
                            if(rawEqForRgnSumm == '-(NE-91)' or rawEqForRgnSumm == '-(SR-91)' or rawEqForRgnSumm == '-(WR-91)' or rawEqForRgnSumm == '-(NR-91)') :
                                rgnSummary[eqMapForRgnSumm[rawEqForRgnSumm]].append(totalSummaryData[equationIndex])
                        


                #        ************************** We must assign sign too ***************************
                    except FileNotFoundError as fnfe :
                        rowWiseData[equationIndex] = ['--']*96
                        totalSummaryData[equationIndex] = '--'
                    except :
                        print("Got error for "+configName)

            #         for p in (rowWiseData) :
            #             print(p)
            #         print(totalSummaryData)
            #         print("sending rowwise data")
            #         print(rowWiseData)
            colWiseData = transposeSpaceadjusted(rowWiseData,equations,spacingInfo)
            for colData in colWiseData :
                configurationOutput = configurationOutput.append(pd.Series("".join(colData)), ignore_index=True)

            ################################## Body Done #############################################################################
            ################################## Footer Fill ##########################################################################
            configurationOutput = configurationOutput.append(pd.Series('-'*sum(spacingInfo)), ignore_index=True)
            totalSummaryData = signSpaceAdjusted(totalSummaryData,equations,spacingInfo)
            configurationOutput = configurationOutput.append(pd.Series("".join(totalSummaryData)), ignore_index=True)
            #         g = [e for e in list(map(lambda x,y: " " * (y - len(x)) + x , totalSummaryData, spacingInfo))]
            configurationOutput = configurationOutput.append(pd.Series('-'*sum(spacingInfo)), ignore_index=True)

            ################################## Footer Done ##########################################################################
            ################################### Output ##############################################################################
            configurationOutput = configurationOutput.reset_index(drop=True)
            # configurationOutput.to_csv('mySEMBASE/MWH/'+ mwhDate.replace('-','') + "." + extension, header=False, index=None)
            configurationOutput.to_csv(meterFileMainFolder + '/Final Output Files/' + mwhDate + "/" + mwhDate.replace('-','') + "." + extension, header=False, index=None)
            print("Final Output created for " + extension + "For date " + mwhDate)

    print("Job Done")
    print("Creating RGN Summary")
    print(rgnSummary)

    # Uncomment next 2 lines.

    rgnSummaryDf = pd.DataFrame.from_dict(rgnSummary)

    rgnSummaryDf.to_excel(meterFileMainFolder + '/Final Output Files/RGN Summary.xlsx', sheet_name='RGN Summary')

    # with pd.ExcelWriter(meterFileMainFolder + '/Final Output Files/RGN Summary.xlsx', engine='openpyxl', mode='w') as writer:
        
    #     rgnSummaryDf.to_excel(writer,sheet_name='RGN Summary')
        
    #     writer.save()
    #     writer.close()

    

    print("Creating MVAR File")

    with open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/ConfigurationFile.xlsx', "rb") as f: # input the .xlsx
        data = pd.read_excel(f,sheet_name="ConfigurationMVAR",engine='openpyxl',header = None)
        f.close()

    df = pd.DataFrame(data)
    df = df.fillna('')
    # df
    # df.iloc[3][0].rstrip() == 'EQUATION'
    # df.iloc[3]
    # allConfigurations = [ {'Configuration Name' : 'AL1_MWH' , 'TITLE' : 'HVDC ALOPURDUAR AUX CONSUMPTION TRANSFORMER FLOW (in MWH)', 'HEADERLINE' : [] , 'EQUATION' : []} , {} , {}]

    dfLength = len(df)
    # print(df.iloc[0][1])
    allConfigurations = []
    i = 0
    while i < (len(df)) :
        currentConfig = {'Configuration Name' : '' , 'EXTENSION' : '' ,'TITLE' : '' ,'HEADERLINE' : [], 'EQUATION' : []}
        if(df.iloc[i][0].rstrip() == 'Configuration Name/Item/Extension') :

            currentConfig['Configuration Name'] = df.iloc[i][1]
            currentConfig['EXTENSION'] = df.iloc[i][3]

            currentConfig['TITLE'] = df.iloc[i+1][1]
            i = i+2
            currentConfig['HEADERLINE'] = list(df.iloc[i][1:])
            i = i+1
            currentConfig['EQUATION'] = (list(df.iloc[i][1:]))
            allConfigurations.append(currentConfig)
        if(df.iloc[i][0].rstrip() == 'END') :
            i = i+1
            continue
        i = i+1
        
    print(allConfigurations)

    for configuration in (allConfigurations) :
        tuples = []
        configName = configuration['Configuration Name']
        extension = configuration['EXTENSION']
        title = configuration['TITLE']
        headerInfo,equations = removeBlankMvarConfig(configuration['HEADERLINE'],configuration['EQUATION'])
        
        print(headerInfo,equations)
        
        for i in range(len(equations)) :
            if(headerInfo[i].strip() != 'DATE') :
                tuples.append((headerInfo[i],equations[i],equations[i] + 'H'))
                tuples.append((headerInfo[i],equations[i],equations[i] + 'L'))
        
        allDates = []
        allData = []  # Will be array of arrays. Datewise data in one list.
        
        for mwhDate in mwhDates :
            allDates.append(mwhDate)
            dataForThisDate = []
            for equation in equations:
                
                equation = equation.replace(' ','')
                equation = equation.replace(u'\xa0', u'') # Non breaking space.
                equation = equation.replace('\t','')
                equation = equation.replace('\n','')
                equation = equation.replace('(','')
                equation = equation.replace(')','')
                if(equation == 'DATE') :
                    continue
            ##################################### Working with the outpt ###################################################################

                if(os.path.exists(realMeterMWHPath + mwhDate + "/" + searchMeterNumber(equation) + '.MWH')) :
                    data = pd.read_csv(realMeterMWHPath + mwhDate + "/" + searchMeterNumber(equation) + '.MWH', header = None)
                    headerData = data[0][0].split()
                    reactiveHigh = headerData[4]
                    reactiveLow = headerData[5]
                    dataForThisDate.append(reactiveHigh)
                    dataForThisDate.append(reactiveLow)
                else :
                    dataForThisDate.append(None)
                    dataForThisDate.append(None)

            allData.append(dataForThisDate)
        allDates.append('TOTAL')


        allDataSumColWise = list()
        for j in range(0, len(allData[0])):
            tmp = 0
            for i in range(0, len(allData)):
                if(allData[i][j] is None):
                    continue
                tmp = tmp + float(allData[i][j])
            allDataSumColWise.append(tmp)
            
        allData.append(allDataSumColWise)



        col = pd.MultiIndex.from_tuples(tuples, names=('','', 'DATE'))

        df = pd.DataFrame(allData, index = allDates, columns=col)

        if not os.path.exists(meterFileMainFolder + '/Final Output Files/MVAR/'):
            os.makedirs(meterFileMainFolder + '/Final Output Files/MVAR/')

        df.to_excel(meterFileMainFolder + '/Final Output Files/MVAR/' + title + ".xlsx")





    if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 6)) :
        print("New filnalOutputFile creation executed")

        finalOutputDict = {'lastIndex' : 1}

        jsonOutput = dirJsonFinalOutput(os.path.splitext(relativeFilePath)[0],_meterData,finalOutputDict)
        print(json.dumps(jsonOutput))
        print(finalOutputDict)
        
        finalOutputFileObject = FinalOutputFile.objects.create(finalOutputDictionary = json.dumps(finalOutputDict),dirStructureFinalOutput=json.dumps(jsonOutput), meterFile = _meterData)
        finalOutputFileObject.save()

        AllMeterFiles.objects.filter(id = _meterData.id).update(status="FinalOutputCreated")
    

    createFinalOutputExcel(path)


    ct2 = datetime.now()
    print(str(ct2-ct1))
    print(ct1)
    print(ct2)