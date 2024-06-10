
import re
import os
from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
from shutil import copyfile
from pathlib import Path
from .models import *
import json




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

def headerForMWHData(headerData):
    actDiff = f'{float(headerData[3]) :.4f}'

    reactiveHighDiff = f'{float(headerData[4]) :.1f}'

    reactiveLowDiff = f'{float(headerData[5]) :.1f}'

    # Adjusting the spaces
    _mwhHeaderData = [headerData[0]," "+headerData[1]," "*3 + headerData[2]," "*decideSpace(14,actDiff) + actDiff," "*decideSpace(11,reactiveHighDiff) + reactiveHighDiff," "*decideSpace(9,reactiveLowDiff) + reactiveLowDiff]
    return(''.join(_mwhHeaderData))

def spaceAdjustmentRealMeterRow(_part) :  # Adjusts one row of real meter
    spaceAdjustedPart = []
    for i in range(len(_part)) :
        if(i == 0) :
            spaceAdjustedPart.append(_part[i])
        elif(i == 1) :
            spaceAdjustedPart.append(" "*decideSpace(16,_part[i]) + _part[i])
        else :
            spaceAdjustedPart.append(" "*decideSpace(18,_part[i]) + _part[i])
    return spaceAdjustedPart

def spaceAdjustFictMeterHeader(_seriesHeader) :
    #     print("_seriesHeader")

    #     print(_seriesHeader)
    
    #     _seriesHeader[1] = " "+ _seriesHeader[1] + " "*(12-len(_seriesHeader[1]))
    # Issue is if metername is > 12 chars then there will be overlap. Also in case of = 12, metername and date can't be split()
    # So add a check
    # if(len(_seriesHeader[1]) >= 12) :
    #     _seriesHeader[1] = " " + _seriesHeader[1] + " "
    # else :
    #     _seriesHeader[1] = " " + _seriesHeader[1] + " "*(12-len(_seriesHeader[1]))
        
    _seriesHeader[1] = " " + _seriesHeader[1] + " " * decideSpace(12,_seriesHeader[1])

    _seriesHeader[3] = f'{float(_seriesHeader[3]) :.4f}'
    # _seriesHeader[3] = " "*(14-len(_seriesHeader[3])) + _seriesHeader[3]
    _seriesHeader[3] = " "*decideSpace(14,_seriesHeader[3]) + _seriesHeader[3]
   
    _seriesHeader[4] = f'{float(_seriesHeader[4]) :.1f}'
    # _seriesHeader[4] = " "*(11-len(_seriesHeader[4])) + _seriesHeader[4]
    _seriesHeader[4] = " "*decideSpace(11,_seriesHeader[4]) + _seriesHeader[4]

    _seriesHeader[5] = f'{float(_seriesHeader[5]) :.1f}'
    # _seriesHeader[5] = " "*(9-len(_seriesHeader[5])) + _seriesHeader[5]
    _seriesHeader[5] = " "*decideSpace(9,_seriesHeader[5]) + _seriesHeader[5]

    #     print("returning")
    #     print(_seriesHeader)

    return "".join(_seriesHeader)

def spaceAdjustFictMeterBody(_seriesBody) :
    _seriesBody[1] = f'{float(_seriesBody[1]) :.6f}'
    # _seriesBody[1] = " "*(16-len(_seriesBody[1])) + _seriesBody[1]
    _seriesBody[1] = " "*decideSpace(16,_seriesBody[1]) + _seriesBody[1]
    
    _seriesBody[2] = f'{float(_seriesBody[2]) :.6f}'
    # _seriesBody[2] = " "*(18-len(_seriesBody[2])) + _seriesBody[2]
    _seriesBody[2] = " "*decideSpace(18,_seriesBody[2]) + _seriesBody[2]
    
    _seriesBody[3] = f'{float(_seriesBody[3]) :.6f}'
    # _seriesBody[3] = " "*(18-len(_seriesBody[3])) + _seriesBody[3]
    _seriesBody[3] = " "*decideSpace(18,_seriesBody[3]) + _seriesBody[3]
    
    _seriesBody[4] = f'{float(_seriesBody[4]) :.6f}'
    # _seriesBody[4] = " "*(18-len(_seriesBody[4])) + _seriesBody[4]
    _seriesBody[4] = " "*decideSpace(18,_seriesBody[4]) + _seriesBody[4]

    #     print("returning")

    #     print(_seriesBody)
    return "".join(_seriesBody)

def spaceAdjustmentFictMeter(_df) :
    _df[0] = spaceAdjustFictMeterHeader(_df[0].split())
    i = 1
    while i < 25 :
        _df[i] = spaceAdjustFictMeterBody(_df[i].split())
        i+=1
    return _df

def dirJsonRealMeterMWH(nPath,_meterData,mwhDict):
    d = {'name': os.path.basename(nPath)}
    # d['size'] = str("{0:.2f}".format((os.stat(nPath).st_size / 1024)) + "KB")
    if os.path.isdir(nPath):
        d['type'] = "folder"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
        d['files'] = [dirJsonRealMeterMWH(os.path.join(nPath, x),_meterData,mwhDict) for x in os.listdir(nPath)]
    else:
        print(os.path.basename(nPath))
        d['id'] = mwhDict['lastIndex']
        mwhDict[mwhDict['lastIndex']] = os.path.relpath(nPath, 'fifteenmmdp/media')
        mwhDict['lastIndex'] = mwhDict['lastIndex'] + 1
        
        d['type'] = "file"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')

    return d

def dirJsonFictMeterMWH(nPath,_meterData,fictMwhDict):
    d = {'name': os.path.basename(nPath)}
    # d['size'] = str("{0:.2f}".format((os.stat(nPath).st_size / 1024)) + "KB")
    if os.path.isdir(nPath):
        d['type'] = "folder"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
        d['files'] = [dirJsonFictMeterMWH(os.path.join(nPath, x),_meterData,fictMwhDict) for x in os.listdir(nPath)]
    else:
        # if(os.path.splitext(nPath)[1].lower() != '.log') :

        print(os.path.basename(nPath))
        d['id'] = fictMwhDict['lastIndex']
        fictMwhDict[fictMwhDict['lastIndex']] = os.path.relpath(nPath, 'fifteenmmdp/media')
        fictMwhDict['lastIndex'] = fictMwhDict['lastIndex'] + 1
        
        d['type'] = "file"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
      

    return d

def changeMeterEndDataWithEquation(path,startDate,endDate,meterEndToReplace,equationToReplaceWith) :


    # startDate =  "12/07/2020 14:00:00"
    # endDate = "12/13/2020 20:45:00"
    # meterEndToReplace = "ER-02"
    # equationToReplaceWith = "2*(BI-02)"

    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    fictMeterMWHPathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    realMeterMWHPathCopy = meterFileMainFolder+'/Real Meter MWH Files(Copy)/'
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

    ################################################ Evaluate Function ###########################################################################
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

        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ', _mwhDate] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[0].split()[3:], b[0].split()[3:]))]
        #     print("sending")
        #     print(seriesHeader)

        #     seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)
        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[i].split()[1:], b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)
            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    def fsOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand float, second operand PandasSeries
        #     print("Inside fsOperation")

        returnSeries = pd.Series([],dtype=object)

        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ', _mwhDate] +  [str(e) for e in list(map(lambda y : ffOperation(a,y,op), b[0].split()[3:]))]
        # seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)

        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [b[i].split()[0]] +  [str(e) for e in list(map(lambda y: ffOperation(a,y,op), b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)

            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    def sfOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand PandasSeries, second operand float

        returnSeries = pd.Series([],dtype=object)

        seriesHeader = [_fictMeterId, 'ZZZ-ZZZ-ZZZ', _mwhDate] +  [str(e) for e in list(map(lambda x : ffOperation(x,b,op), a[0].split()[3:]))]
        # seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)

        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x: ffOperation(x,b,op), a[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)

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
    # Function to find precedence of operators.
    def precedence(op):

        if op == '+' or op == '-':
            return 1
        if op == '*' or op == '/':
            return 2
        return 0


    # Function that returns value of expression after evaluation.
    def evaluate(_fictMeterId,_mwhDate,tokens):
        
        print("Evaluating expression for " + tokens)
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

            # Current token is a meter ID, push 
            # it to stack for numbers.

            elif tokens[i].isalpha() and tokens[i : i + 4].upper() == 'ABS(' :
                print("I got absolute")
                idx = getCorrespondingClosingIdx(tokens[i+4: ], i+4)

                #  We want to calculate the expression tokens[i+1 to idx - 1]
                print("Closing Index is " + str(idx))

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
                # print(values) 
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


    def scalarToSeries(floatValue,customHeader = ["No header"]) : # Replace header with desired value.
        scalarDf = pd.Series([],dtype=object)
        scalarDf = scalarDf.append(pd.Series(''.join(customHeader)), ignore_index=True)
        for timeStamp in range(24) :
            rowPart = [str((timeStamp)*100).zfill(4)] + [f'{(float(x)) :.6f}' for x in [str(floatValue)]*4]
            scalarDf = scalarDf.append(pd.Series(' '.join((rowPart))), ignore_index=True)
            scalarDf = scalarDf.reset_index(drop=True)
        return scalarDf

    ######################################## Space adjustments real mater ############################################################################


    def decideSpace(spaceValue,stringToCheck) :
        spaceOffset = max(spaceValue,len(stringToCheck)+1)
        return spaceOffset - len(stringToCheck)


    def generateMwhHeader(_meterHeaderData,_nextMeterHeaderData,_meterId,_meterName,_ctr,_ptr,_headerDate) :
        # We have [NP-5851-A,    97845.9,    35371.6,    00136.0,    07-12-20] and for 08-12-20

        actDiff = f'{((float(_nextMeterHeaderData[1]) - float(_meterHeaderData[1]))*_ctr*_ptr)/1000000 :.4f}'

        reactiveHighDiff = f'{((float(_nextMeterHeaderData[2]) - float(_meterHeaderData[2]))*_ctr*_ptr)/1000000 :.1f}'

        reactiveLowDiff = f'{((float(_nextMeterHeaderData[3]) - float(_meterHeaderData[3]))*_ctr*_ptr)/1000000 :.1f}'

        # Adjusting the spaces
        _mwhHeaderData = [_meterId," "+_meterName," "*3 + _headerDate," "*decideSpace(14,actDiff) + actDiff," "*decideSpace(11,reactiveHighDiff) + reactiveHighDiff," "*decideSpace(9,reactiveLowDiff) + reactiveLowDiff]
        return(_mwhHeaderData)



    ######################################## Space adjustments Fict mater ############################################################################

    def spaceAdjustFictMeterHeader(_seriesHeader) :
            
        _seriesHeader[1] = " " + _seriesHeader[1] + " " * decideSpace(12,_seriesHeader[1])

        _seriesHeader[3] = f'{float(_seriesHeader[3]) :.4f}'
        _seriesHeader[3] = " "*decideSpace(14,_seriesHeader[3]) + _seriesHeader[3]
    
        _seriesHeader[4] = f'{float(_seriesHeader[4]) :.1f}'
        _seriesHeader[4] = " "*decideSpace(11,_seriesHeader[4]) + _seriesHeader[4]

        _seriesHeader[5] = f'{float(_seriesHeader[5]) :.1f}'
        _seriesHeader[5] = " "*decideSpace(9,_seriesHeader[5]) + _seriesHeader[5]

        return "".join(_seriesHeader)

    def spaceAdjustFictMeterBody(_seriesBody) :
        _seriesBody[1] = f'{float(_seriesBody[1]) :.6f}'
        # _seriesBody[1] = " "*(16-len(_seriesBody[1])) + _seriesBody[1]
        _seriesBody[1] = " "*decideSpace(16,_seriesBody[1]) + _seriesBody[1]
        
        _seriesBody[2] = f'{float(_seriesBody[2]) :.6f}'
        # _seriesBody[2] = " "*(18-len(_seriesBody[2])) + _seriesBody[2]
        _seriesBody[2] = " "*decideSpace(18,_seriesBody[2]) + _seriesBody[2]
        
        _seriesBody[3] = f'{float(_seriesBody[3]) :.6f}'
        # _seriesBody[3] = " "*(18-len(_seriesBody[3])) + _seriesBody[3]
        _seriesBody[3] = " "*decideSpace(18,_seriesBody[3]) + _seriesBody[3]
        
        _seriesBody[4] = f'{float(_seriesBody[4]) :.6f}'
        # _seriesBody[4] = " "*(18-len(_seriesBody[4])) + _seriesBody[4]
        _seriesBody[4] = " "*decideSpace(18,_seriesBody[4]) + _seriesBody[4]

        #     print("returning")

        #     print(_seriesBody)
        return "".join(_seriesBody)

    def spaceAdjustmentFictMeter(_df) :
        _df[0] = spaceAdjustFictMeterHeader(_df[0].split())
        i = 1
        while i < 25 :
            _df[i] = spaceAdjustFictMeterBody(_df[i].split())
            i+=1
        return _df


    ######################################## SingleDay replacement ############################################################################

    def singleDayReplacement(dateObject,meterLocId,eq,fromTime,toTime) :    
        print(dateObject)
        
        try :
            if(getMeterInfoById(meterLocId) is not None) :
                data1 = pd.read_csv(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH', header = None)
                if not os.path.exists(realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH') :
                    Path(realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y")).mkdir(parents=True, exist_ok=True)
                    copyfile(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH',realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH')
            else :
                data1 = pd.read_csv(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH', header = None)
                if not os.path.exists(fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH') :
                    Path(fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y")).mkdir(parents=True, exist_ok=True)
                    copyfile(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH',fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH')


            dfSeries1 = pd.DataFrame(data1)
            df1 = dfSeries1[0]
        except FileNotFoundError :
            print(searchMeterNumber(meterLocId) + ".MWH not found")
            return {'errorCode' : 1 , 'msg' : searchMeterNumber(meterLocId) + ".MWH not found"}
        
        try :
            df2 = evaluate(searchMeterNumber(meterLocId), dateObject.strftime("%d-%m-%y"), eq)
        except FileNotFoundError as fnfe :
            meterNumber = fnfe.filename.split('/')[-1][:-4]
            meterId = searchMeterId(meterNumber)
            print("(" + meterId + " : " + meterNumber + ") not found, while calculating equation" + eq)
            return {'errorCode' : 2 , 'msg' : "File unavailability for date " + dateObject.strftime("%d-%m-%y")}
        except :
            print("Got error for " + eq)
            return {'errorCode' : 3 , 'msg' : "Error in equation"}

        if(type(df2) == float) :
            df2 = scalarToSeries(df2)

        print(df2)
        
        fromTimeHr , fromTimeMinute = [int(x) for x in fromTime.split(":")]
        toTimeHr , toTimeMinute = [int(x) for x in toTime.split(":")]


        if(fromTimeHr == toTimeHr) :
            hr = fromTimeHr
            print("Same Start End Hour")
            print(df1[hr+1].split())
            oldRow = df1[hr+1].split()
            newRow = df2[hr+1].split()
            for minute in range(fromTimeMinute//15 + 1, toTimeMinute//15 + 2) :
                oldRow[minute] = newRow[minute]
                
            oldRow = [oldRow[0]] + [f'{(float(x)) :.6f}' for x in oldRow[1:]]

            df1[hr+1] = ''.join(spaceAdjustmentRealMeterRow(oldRow))
        else: 
            for hr in range(fromTimeHr , toTimeHr+1):

                if(hr == fromTimeHr) :
                    print("Start Hour")
                    print(df1[hr+1].split())
                    oldRow = df1[hr+1].split()
                    newRow = df2[hr+1].split()

                    for minute in range(fromTimeMinute//15 + 1,5) :
                        oldRow[minute] = newRow[minute]
                        
                    oldRow = [oldRow[0]] + [f'{(float(x)) :.6f}' for x in oldRow[1:]]
                    
                    df1[hr+1] = ''.join(spaceAdjustmentRealMeterRow(oldRow)) 

                elif(hr == toTimeHr) :
                    print("End Hour")
                    print(df1[hr+1].split())
                    oldRow = df1[hr+1].split()
                    newRow = df2[hr+1].split()

                    for minute in range(1,toTimeMinute//15 + 2) :
                        oldRow[minute] = newRow[minute]
                    
                    oldRow = [oldRow[0]] + [f'{(float(x)) :.6f}' for x in oldRow[1:]]

                    df1[hr+1] = ''.join(spaceAdjustmentRealMeterRow(oldRow)) 

                else :
                    print("In between time")
                    oldRow = df1[hr+1].split()
                    newRow = df2[hr+1].split()
                    oldRow = newRow
                    oldRow = [oldRow[0]] + [f'{(float(x)) :.6f}' for x in oldRow[1:]]
                    df1[hr+1] = ''.join(spaceAdjustmentRealMeterRow(oldRow)) 


        print(df1)
         
        if(getMeterInfoById(meterLocId) is not None) :
            df1.to_csv(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) +'.MWH', header=False, index=None)
        elif(getFictMeterInfoById(meterLocId) is not None) :
            df1.to_csv(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) +'.MWH', header=False, index=None)
        else :
            return

        print("Success")


    ######################################## SingleDay replacement ############################################################################

 
    # startDate =  "12/07/2020 14:00:00"
    # endDate = "12/13/2020 20:45:00"
    # meterEndToReplace = "ER-02"
    # equationToReplaceWith = "2*(BI-02)"

    equationToReplaceWith = equationToReplaceWith.replace(' ','')
    equationToReplaceWith = equationToReplaceWith.replace(u'\xa0', u'') # Non breaking space.
    equationToReplaceWith = equationToReplaceWith.replace('\t','')
    equationToReplaceWith = equationToReplaceWith.replace('\n','')
    # print('after trim')
    # print(equation)
    # print(len(equation))

    if(equationToReplaceWith[0] == '+' or equationToReplaceWith[0] == '-') :
        equationToReplaceWith = '0' + equationToReplaceWith

    # equationToReplaceWith = re.sub('([A-Z]{2})-([0-9]{2})', r'\1_\2', equationToReplaceWith)

    startDateObject = datetime.strptime(startDate, "%m/%d/%Y %H:%M:%S")
    endDateObject = datetime.strptime(endDate, "%m/%d/%Y %H:%M:%S")

    if(startDateObject.date() == endDateObject.date()) :
        print("Start date end date same")
        fromTime = datetime.strftime(startDateObject, "%H:%M")
        toTime = datetime.strftime(endDateObject, "%H:%M")
        singleDayReplacement(startDateObject.date(),meterEndToReplace,equationToReplaceWith,fromTime,toTime)

    else :
        for day in range((endDateObject - startDateObject).days + 1) :
            dateObj = startDateObject+timedelta(days=day)
            print(dateObj)
            
            if(dateObj.date() == startDateObject.date()) :
                print("This is start date")
                fromTime = datetime.strftime(startDateObject, "%H:%M")
                singleDayReplacement(dateObj.date(),meterEndToReplace,equationToReplaceWith,fromTime,'23:45')
                
            elif(dateObj.date() == endDateObject.date()) :
                print("This is end date")
                toTime = datetime.strftime(endDateObject, "%H:%M")
                singleDayReplacement(dateObj.date(),meterEndToReplace,equationToReplaceWith,'00:00',toTime)

            else :
                print("Date in between")
                singleDayReplacement(dateObj.date(),meterEndToReplace,equationToReplaceWith,'00:00','23:45')


def changeMeterEndActiveReactiveDataWithEquation(path,startDate,endDate,meterEndToReplace,equationToReplaceWith,dataToChange) :

    dataToChangeIndexDict = {"Active Data" : 3, "Reactive High" : 4, "Reactive Low" : 5 }

    dataToChangeIndex = dataToChangeIndexDict[dataToChange]

    # startDate =  "12/07/2020 14:00:00"
    # endDate = "12/13/2020 20:45:00"
    # meterEndToReplace = "ER-02"
    # equationToReplaceWith = "2*(BI-02)"

    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    fictMeterMWHPathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    realMeterMWHPathCopy = meterFileMainFolder+'/Real Meter MWH Files(Copy)/'
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

    ################################################ Evaluate Function ###########################################################################

    def takeAbsolute(_fictMeterId,_mwhDate,valueToAppend) :
        print(type(valueToAppend))
        if(isinstance(valueToAppend, pd.core.series.Series)):
            print("Reached at takeAbsolute if. Need to take absolute of Series data")

            meterNumber = 'ZZZ-ZZZ-ZZZ'

            if((getMeterInfoById(_fictMeterId) is not None) and (getMeterInfoById(_fictMeterId).get('Meter_No') is not None)):
                meterNumber = getMeterInfoById(_fictMeterId).get('Meter_No')

            if((getFictMeterInfoById(_fictMeterId) is not None) and (getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No') is not None)):
                meterNumber = getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No')

            returnSeries = pd.Series([],dtype=object)
            seriesHeader = [_fictMeterId, meterNumber,_mwhDate] +  [str(e) for e in list(map(lambda x: abs(float(x)), valueToAppend[0].split()[3:]))]
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

        meterNumber = 'ZZZ-ZZZ-ZZZ'

        if((getMeterInfoById(_fictMeterId) is not None) and (getMeterInfoById(_fictMeterId).get('Meter_No') is not None)):
            meterNumber = getMeterInfoById(_fictMeterId).get('Meter_No')

        if((getFictMeterInfoById(_fictMeterId) is not None) and (getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No') is not None)):
            meterNumber = getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No')

        seriesHeader = [_fictMeterId, meterNumber, _mwhDate] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[0].split()[3:], b[0].split()[3:]))]
        #     print("sending")
        #     print(seriesHeader)

        #     seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)
        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[i].split()[1:], b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)
            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    def fsOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand float, second operand PandasSeries
        #     print("Inside fsOperation")

        returnSeries = pd.Series([],dtype=object)


        meterNumber = 'ZZZ-ZZZ-ZZZ'

        if((getMeterInfoById(_fictMeterId) is not None) and (getMeterInfoById(_fictMeterId).get('Meter_No') is not None)):
            meterNumber = getMeterInfoById(_fictMeterId).get('Meter_No')

        if((getFictMeterInfoById(_fictMeterId) is not None) and (getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No') is not None)):
            meterNumber = getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No')

        seriesHeader = [_fictMeterId, meterNumber, _mwhDate] +  [str(e) for e in list(map(lambda y : ffOperation(a,y,op), b[0].split()[3:]))]
        # seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)

        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [b[i].split()[0]] +  [str(e) for e in list(map(lambda y: ffOperation(a,y,op), b[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)

            returnSeries = returnSeries.append(pd.Series(" ".join(seriesBody)), ignore_index=True)

            i+=1

        return returnSeries

    def sfOperation(_fictMeterId,_mwhDate,a,b,op) : # First operand PandasSeries, second operand float

        returnSeries = pd.Series([],dtype=object)

        meterNumber = 'ZZZ-ZZZ-ZZZ'

        if((getMeterInfoById(_fictMeterId) is not None) and (getMeterInfoById(_fictMeterId).get('Meter_No') is not None)):
            meterNumber = getMeterInfoById(_fictMeterId).get('Meter_No')

        if((getFictMeterInfoById(_fictMeterId) is not None) and (getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No') is not None)):
            meterNumber = getFictMeterInfoById(_fictMeterId).get('Fict_Meter_No')


        seriesHeader = [_fictMeterId, meterNumber, _mwhDate] +  [str(e) for e in list(map(lambda x : ffOperation(x,b,op), a[0].split()[3:]))]
        # seriesHeader = spaceAdjustFictMeterHeader(seriesHeader)

        returnSeries = returnSeries.append(pd.Series(" ".join(seriesHeader)), ignore_index=True)

        i = 1
        while i < 25 :
            seriesBody = [a[i].split()[0]] +  [str(e) for e in list(map(lambda x: ffOperation(x,b,op), a[i].split()[1:]))] 
            # seriesBody = ["0000"] + Rest of the calculated data
            # print(seriesBody)
            # seriesBody = spaceAdjustFictMeterBody(seriesBody)

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
    # Function to find precedence of operators.
    def precedence(op):

        if op == '+' or op == '-':
            return 1
        if op == '*' or op == '/':
            return 2
        return 0


    # Function that returns value of expression after evaluation.
    def evaluate(_fictMeterId,_mwhDate,tokens,dataToChange):
        
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
                print("Closing Index is " + str(idx))
                #  We want to calculate the expression tokens[i+1 to idx - 1]

                newExp = tokens[i+4: idx]

                print(newExp)
                if(newExp[0] == '+' or newExp[0] == '-'):
                    newExp = '0' + newExp

                newExpValue = evaluate(_fictMeterId,_mwhDate,newExp,dataToChange)

                newExpValueAbsolute = takeAbsolute(_fictMeterId,_mwhDate,newExpValue)

                print(" Return value is ")
                print(newExpValueAbsolute)

                values.append(newExpValueAbsolute)

                # Finally we need to move i to idx + 1.
                i = idx # +1 will be done at last by default.


            # Current token is a meter ID, push 
            # it to stack for numbers.
            elif tokens[i].isalpha() and tokens[i : i + 4].upper() != 'ABS(' :
                val = tokens[i : i+5].replace("_","-")

                if(os.path.exists(realMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH')) :
                    data = pd.read_csv(realMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)  # May give FileNotFoundError
                else :
                    data = pd.read_csv(fictMeterMWHPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)
                # print(data)
                dfSeries = pd.DataFrame(data)
                df = dfSeries[0]
                # Now here we expect to work with one single float value only.
                values.append(float(df[0].split()[dataToChangeIndex]))

                i+=4              

            elif(tokens[i].isdigit() or tokens[i] == '.') :
                val = ""

                # There may be more than one
                # digits in the number.
                while (i < len(tokens) and (tokens[i].isdigit() or tokens[i] == '.')):             
                    val = val + tokens[i]
                    i += 1

                values.append(float(val))
                # print(values) 
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


    def scalarToSeries(floatValue,customHeader = ["No header"]) : # Replace header with desired value.
        scalarDf = pd.Series([],dtype=object)
        scalarDf = scalarDf.append(pd.Series(''.join(customHeader)), ignore_index=True)
        for timeStamp in range(24) :
            rowPart = [str((timeStamp)*100).zfill(4)] + [f'{(float(x)) :.6f}' for x in [str(floatValue)]*4]
            scalarDf = scalarDf.append(pd.Series(' '.join((rowPart))), ignore_index=True)
            scalarDf = scalarDf.reset_index(drop=True)
        return scalarDf

    ######################################## Space adjustments real mater ############################################################################


    def decideSpace(spaceValue,stringToCheck) :
        spaceOffset = max(spaceValue,len(stringToCheck)+1)
        return spaceOffset - len(stringToCheck)


    def generateMwhHeader(_meterHeaderData,_nextMeterHeaderData,_meterId,_meterName,_ctr,_ptr,_headerDate) :
        # We have [NP-5851-A,    97845.9,    35371.6,    00136.0,    07-12-20] and for 08-12-20

        actDiff = f'{((float(_nextMeterHeaderData[1]) - float(_meterHeaderData[1]))*_ctr*_ptr)/1000000 :.4f}'

        reactiveHighDiff = f'{((float(_nextMeterHeaderData[2]) - float(_meterHeaderData[2]))*_ctr*_ptr)/1000000 :.1f}'

        reactiveLowDiff = f'{((float(_nextMeterHeaderData[3]) - float(_meterHeaderData[3]))*_ctr*_ptr)/1000000 :.1f}'

        # Adjusting the spaces
        _mwhHeaderData = [_meterId," "+_meterName," "*3 + _headerDate," "*decideSpace(14,actDiff) + actDiff," "*decideSpace(11,reactiveHighDiff) + reactiveHighDiff," "*decideSpace(9,reactiveLowDiff) + reactiveLowDiff]
        return(_mwhHeaderData)



    ######################################## Space adjustments Fict mater ############################################################################

    def spaceAdjustFictMeterHeader(_seriesHeader) :
            
        _seriesHeader[1] = " " + _seriesHeader[1] + " " * decideSpace(12,_seriesHeader[1])

        _seriesHeader[3] = f'{float(_seriesHeader[3]) :.4f}'
        _seriesHeader[3] = " "*decideSpace(14,_seriesHeader[3]) + _seriesHeader[3]
    
        _seriesHeader[4] = f'{float(_seriesHeader[4]) :.1f}'
        _seriesHeader[4] = " "*decideSpace(11,_seriesHeader[4]) + _seriesHeader[4]

        _seriesHeader[5] = f'{float(_seriesHeader[5]) :.1f}'
        _seriesHeader[5] = " "*decideSpace(9,_seriesHeader[5]) + _seriesHeader[5]

        return "".join(_seriesHeader)

    def spaceAdjustFictMeterBody(_seriesBody) :
        _seriesBody[1] = f'{float(_seriesBody[1]) :.6f}'
        # _seriesBody[1] = " "*(16-len(_seriesBody[1])) + _seriesBody[1]
        _seriesBody[1] = " "*decideSpace(16,_seriesBody[1]) + _seriesBody[1]
        
        _seriesBody[2] = f'{float(_seriesBody[2]) :.6f}'
        # _seriesBody[2] = " "*(18-len(_seriesBody[2])) + _seriesBody[2]
        _seriesBody[2] = " "*decideSpace(18,_seriesBody[2]) + _seriesBody[2]
        
        _seriesBody[3] = f'{float(_seriesBody[3]) :.6f}'
        # _seriesBody[3] = " "*(18-len(_seriesBody[3])) + _seriesBody[3]
        _seriesBody[3] = " "*decideSpace(18,_seriesBody[3]) + _seriesBody[3]
        
        _seriesBody[4] = f'{float(_seriesBody[4]) :.6f}'
        # _seriesBody[4] = " "*(18-len(_seriesBody[4])) + _seriesBody[4]
        _seriesBody[4] = " "*decideSpace(18,_seriesBody[4]) + _seriesBody[4]

        #     print("returning")

        #     print(_seriesBody)
        return "".join(_seriesBody)

    def spaceAdjustmentFictMeter(_df) :
        _df[0] = spaceAdjustFictMeterHeader(_df[0].split())
        i = 1
        while i < 25 :
            _df[i] = spaceAdjustFictMeterBody(_df[i].split())
            i+=1
        return _df


    ######################################## SingleDay replacement ############################################################################

    def singleDayReplacementActiveReactive(dateObject,meterLocId,eq,dataToChange) :    
        print(dateObject)
        
        try :
            if(getMeterInfoById(meterLocId) is not None) :
                data1 = pd.read_csv(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH', header = None)
                if not os.path.exists(realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH') :
                    Path(realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y")).mkdir(parents=True, exist_ok=True)
                    copyfile(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH',realMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH')
            else :
                data1 = pd.read_csv(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH', header = None)
                if not os.path.exists(fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH') :
                    Path(fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y")).mkdir(parents=True, exist_ok=True)
                    copyfile(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH',fictMeterMWHPathCopy + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) + '.MWH')


            dfSeries1 = pd.DataFrame(data1)
            df1 = dfSeries1[0]
        except FileNotFoundError :
            print(searchMeterNumber(meterLocId) + ".MWH not found")
            return {'errorCode' : 1 , 'msg' : searchMeterNumber(meterLocId) + ".MWH not found"}
        
        try :
            df2 = evaluate(meterLocId, dateObject.strftime("%d-%m-%y"), eq, dataToChange)
        except FileNotFoundError as fnfe :
            meterNumber = fnfe.filename.split('/')[-1][:-4]
            meterId = searchMeterId(meterNumber)
            print("(" + meterId + " : " + meterNumber + ") not found, while calculating equation" + eq)
            return {'errorCode' : 2 , 'msg' : "File unavailability for date " + dateObject.strftime("%d-%m-%y")}
        # except :
        #     print("Got error for " + eq)
        #     return {'errorCode' : 3 , 'msg' : "Error in equation"}

        print(df2)

        if(type(df2) != float) :
            return {'errorCode' : 3 , 'msg' : "Error in equation"}
        
        # Since we are working with one single value only, so we expect that a float value will be returned.

        currentHeader = df1[0].split()
        currentHeader[dataToChangeIndex] = df2

        print(df1)
         
        if(getMeterInfoById(meterLocId) is not None) :
            newHeader = headerForMWHData(currentHeader)
            df1[0] = newHeader
            df1.to_csv(realMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) +'.MWH', header=False, index=None)
        elif(getFictMeterInfoById(meterLocId) is not None) :
            newHeader = spaceAdjustFictMeterHeader(currentHeader)
            df1[0] = newHeader
            df1.to_csv(fictMeterMWHPath + dateObject.strftime("%d-%m-%y") + "/" + searchMeterNumber(meterLocId) +'.MWH', header=False, index=None)
        else :
            return

        print("Success")


    ######################################## SingleDay replacement ############################################################################

 
    # startDate =  "12/07/2020 14:00:00"
    # endDate = "12/13/2020 20:45:00"
    # meterEndToReplace = "ER-02"
    # equationToReplaceWith = "2*(BI-02)"

    equationToReplaceWith = equationToReplaceWith.replace(' ','')
    equationToReplaceWith = equationToReplaceWith.replace(u'\xa0', u'') # Non breaking space.
    equationToReplaceWith = equationToReplaceWith.replace('\t','')
    equationToReplaceWith = equationToReplaceWith.replace('\n','')
    # print('after trim')
    # print(equation)
    # print(len(equation))

    if(equationToReplaceWith[0] == '+' or equationToReplaceWith[0] == '-') :
        equationToReplaceWith = '0' + equationToReplaceWith

    # equationToReplaceWith = re.sub('([A-Z]{2})-([0-9]{2})', r'\1_\2', equationToReplaceWith)

    print(path,startDate,endDate,meterEndToReplace,equationToReplaceWith,dataToChange)

    ####################################### main Logic here ##############################################################
    startDateObject = datetime.strptime(startDate, "%m/%d/%Y %H:%M:%S")
    endDateObject = datetime.strptime(endDate, "%m/%d/%Y %H:%M:%S")

    if(startDateObject.date() == endDateObject.date()) :
        print("Start date end date same")
        singleDayReplacementActiveReactive(startDateObject.date(),meterEndToReplace,equationToReplaceWith,dataToChange)

    else :
        for day in range((endDateObject - startDateObject).days + 1) :
            dateObj = startDateObject+timedelta(days=day)
            print(dateObj)
            singleDayReplacementActiveReactive(dateObj.date(),meterEndToReplace,equationToReplaceWith,dataToChange)

    ####################################### main Logic here ##############################################################



def revertMeterEndChanges(path,meterEndToReplace) :

    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    fictMeterMWHPathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    realMeterMWHPathCopy = meterFileMainFolder+'/Real Meter MWH Files(Copy)/'
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

    ################################################ Revert Function ###########################################################################


    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)

    for mwhDate in mwhDates :
        if(getMeterInfoById(meterEndToReplace) is not None) :  # So it is a real meter
            if os.path.exists(realMeterMWHPathCopy + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH') :
                copyfile(realMeterMWHPathCopy + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH',realMeterMWHPath + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH')
        else : # Fict Meter
            if os.path.exists(fictMeterMWHPathCopy + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH') :
                copyfile(fictMeterMWHPathCopy + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH',fictMeterMWHPath + mwhDate + "/" + searchMeterNumber(meterEndToReplace) + '.MWH')

    return {'errorCode' : 0 , 'msg' : "Success"}


def zeroFillMeter(path,_meterData,meterEndToZeroFill) :
    print("inside zeroFillMeter")
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    fictMeterMWHPath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    realMeterMWHPath = meterFileMainFolder+'/Real Meter MWH Files/'
    fictMeterMWHPathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    realMeterMWHPathCopy = meterFileMainFolder+'/Real Meter MWH Files(Copy)/'


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

    ################################################ Evaluate Function ###########################################################################
    def scalarToSeries(floatValue,customHeader = ["No header"]) : # Replace header with desired value.
        scalarDf = pd.Series([],dtype=object)
        scalarDf = scalarDf.append(pd.Series(''.join(customHeader)), ignore_index=True)
        for timeStamp in range(24) :
            rowPart = [str((timeStamp)*100).zfill(4)] + [f'{(float(x)) :.6f}' for x in [str(floatValue)]*4]
            scalarDf = scalarDf.append(pd.Series(' '.join((rowPart))), ignore_index=True)
            scalarDf = scalarDf.reset_index(drop=True)
        return scalarDf

    ###############################################################################################################################################

    # Stating with the new 0 filling part
    print("Stating with the new 0 filling part")

    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)

    # for realMeter in realMeterInfo : meterEndToZeroFill
    if(getMeterInfoById(meterEndToZeroFill) is not None) :
        realMeter = getMeterInfoById(meterEndToZeroFill)
        changeFlag = False
        for mwhDate in mwhDates :
            if not os.path.exists(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate + "/" + realMeter["Meter_No"] + ".MWH"):
                changeFlag = True
                scalarDf = scalarToSeries(0.0,[realMeter["Loc_Id"] + " " + realMeter["Meter_No"] + " "*3 + mwhDate + " "*8 + "0.0000" +  " "*8 + "0.0" + " "*6 + "0.0" ])
                i = 1
                while i < 25 :
                    scalarDf[i] = ''.join(spaceAdjustmentRealMeterRow(scalarDf[i].split()))
                    i = i + 1
                scalarDf.to_csv(meterFileMainFolder+'/Real Meter MWH Files/' + mwhDate + "/" + realMeter["Meter_No"] + ".MWH", header=False, index=None)

        if(changeFlag) :

            mwhDict = {'lastIndex' : 1}

            jsonOutput = dirJsonRealMeterMWH(os.path.splitext(realMeterMWHPath)[0],_meterData,mwhDict)

            realMeterMWHFileObject = RealMeterMWHFile.objects.get(meterFile=_meterData)

            realMeterMWHFileObject.mwhDictionary = json.dumps(mwhDict)
            realMeterMWHFileObject.dirStructureRealMWH = json.dumps(jsonOutput)

            realMeterMWHFileObject.save()

    elif(getFictMeterInfoById(meterEndToZeroFill) is not None) :
        fictMeter = getFictMeterInfoById(meterEndToZeroFill)
        changeFlag = False
        for mwhDate in mwhDates :
            if not os.path.exists(meterFileMainFolder+'/Fictitious Meter MWH Files/' + mwhDate + "/" + fictMeter["Fict_Meter_No"] + ".MWH"):
                changeFlag = True
                scalarDf = scalarToSeries(0.0,[fictMeter["Loc_Id"] + " " + fictMeter["Fict_Meter_No"] + " "*3 + mwhDate + " "*8 + "0.0000" +  " "*8 + "0.0" + " "*6 + "0.0" ])
                scalarDf = spaceAdjustmentFictMeter(scalarDf)
                scalarDf.to_csv(meterFileMainFolder+'/Fictitious Meter MWH Files/' + mwhDate + "/" + fictMeter["Fict_Meter_No"] + ".MWH", header=False, index=None)
        
        if(changeFlag) :

            mwhDict = {'lastIndex' : 1}

            jsonOutput = dirJsonFictMeterMWH(os.path.splitext(fictMeterMWHPath)[0],_meterData,mwhDict)

            fictMeterMWHFileObject = FictMeterMWHFile.objects.get(meterFile=_meterData)

            fictMeterMWHFileObject.fictMwhDictionary = json.dumps(mwhDict)
            fictMeterMWHFileObject.dirStructureFictMWH = json.dumps(jsonOutput)

            fictMeterMWHFileObject.save()
    else :
        pass

    print("Ending with the new 0 filling part")

   # Ending with the new 0 filling part