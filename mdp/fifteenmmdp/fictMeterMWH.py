import os
from .models import AllMeterFiles,FictMeterMWHFile
from django.core.files import File
from django.conf import settings
from .supportingFunctions import *
import pandas as pd
import json
from datetime import datetime

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

def scalarToSeries(floatValue,customHeader = ["No header"]) : # Replace header with desired value.
    scalarDf = pd.Series([],dtype=object)
    scalarDf = scalarDf.append(pd.Series(''.join(customHeader)), ignore_index=True)
    for timeStamp in range(24) :
        rowPart = [str((timeStamp)*100).zfill(4)] + [f'{(float(x)) :.6f}' for x in [str(floatValue)]*4]
        scalarDf = scalarDf.append(pd.Series(' '.join((rowPart))), ignore_index=True)
        scalarDf = scalarDf.reset_index(drop=True)
    return scalarDf


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


def createFictMeterMWH(path,_meterData, _listOfFictMetersSelected, _listOfDatesSelected) :
    ct1 = datetime.now()

    print("I am in createFictMeterMWH" + path)
    

    # meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    # relativeFilePathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)

    relativeFilePath = meterFileMainFolder+'/Fictitious Meter MWH Files/'
    relativeReadPath = meterFileMainFolder+'/Real Meter MWH Files/'
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)

    if not os.path.exists(meterFileMainFolder +'/Fictitious Meter MWH Files(Copy)'): 
        os.makedirs(meterFileMainFolder + '/Fictitious Meter MWH Files(Copy)')
    if not os.path.exists(meterFileMainFolder +'/Fictitious Meter MWH Files'):
        os.makedirs(meterFileMainFolder + '/Fictitious Meter MWH Files')

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

    #################################################### Evaluate Function ####################################################################
    

    def takeAbsolute(_fictMeterId,_mwhDate,valueToAppend) :
        print(type(valueToAppend))
        if(isinstance(valueToAppend, pd.core.series.Series)):
            print("Reached at takeAbsolute if. Need to take absolute of Series data")

            returnSeries = pd.Series([],dtype=object)
            seriesHeader = [_fictMeterId, getFictMeterInfoById(_fictMeterId)['Fict_Meter_No'],_mwhDate] +  [str(e) for e in list(map(lambda x: abs(float(x)), valueToAppend[0].split()[3:]))]
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
        seriesHeader = [_fictMeterId, getFictMeterInfoById(_fictMeterId)['Fict_Meter_No'],_mwhDate] +  [str(e) for e in list(map(lambda x,y: ffOperation(x,y,op), a[0].split()[3:], b[0].split()[3:]))]
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

        seriesHeader = [_fictMeterId, getFictMeterInfoById(_fictMeterId)['Fict_Meter_No'], _mwhDate] +  [str(e) for e in list(map(lambda y : ffOperation(a,y,op), b[0].split()[3:]))]
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

        seriesHeader = [_fictMeterId, getFictMeterInfoById(_fictMeterId)['Fict_Meter_No'],_mwhDate] +  [str(e) for e in list(map(lambda x : ffOperation(x,b,op), a[0].split()[3:]))]
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

                if(getMeterInfoById(val) is not None) :  # That is the meter is real meter
                    if(os.path.exists(relativeReadPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH')) :
                        data = pd.read_csv(relativeReadPath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None)
                        dfSeries = pd.DataFrame(data)
                        df = dfSeries[0]
                        values.append(df)  
                    else :
                        print("i work here for " + val)
                        print(values)
                        values.append(float(0))   # That is, in case of non-existance of real meter we will use 0 during calculation.
                else :
                    data = pd.read_csv(relativeFilePath + _mwhDate + "/" + searchMeterNumber(val) + '.MWH', header = None) # May give FileNotFoundError
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

    ################################################### Performing main operation until no change found #######################################

    # So we have fictMeterInfo (.dat file), realMeterInfo (.dat file) and fictMeterDict (.CFG file)
    # Now for every fictitious meter mentioned in 'FICTMTRS.dat', we will evaluate it's equation we get from fictMeterDict.
    # For Loc_Id to MeterName conversion & opposite, we will use fictMeterInfo & realMeterInfo
    # undefinedFictMetConf : Will have those fictmeter IDs which has no equation defined in CFG file i.e. no entry in fictMeterDict.

    fctData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FICTMTRS.dat', "r")
    fctDataList = fctData.readlines()
    fctData.close()
    undefinedFictMetConf = []
    fileNotFound = []

    nonCalculatedFictMeterIds = []

    for elem in fctDataList :
        # print(len(elem))
        if(len(elem)>1 and isMeterIdPattern(elem.split()[0])) :
            # print(elem.split()[0])
            fictMeterId = elem.split()[0]  # Will have IDs like : 'FK-91'
            if(fictMeterId not in _listOfFictMetersSelected) :
                continue
            eq = "("+fictMeterId+")"
            try :
                myExp = fictMeterDict[eq]    # "+3*MN-17+(MN-18)" . # This may throw KeyEroor if no equation exists. 
                myExp = myExp.replace(' ','')
                myExp = myExp.replace('\t','')
                
                print(myExp)

                if(myExp[0] == '+' or myExp[0] == '-') :
                    myExp = '0' + myExp

                myExp = re.sub('([A-Z]{2})-([0-9]{2})', r'\1_\2', myExp)
                
                if(getFictMeterInfoById(fictMeterId) is not None) :

                    for mwhDate in mwhDates :
                        if(mwhDate not in _listOfDatesSelected) :
                            continue
                        df = evaluate(fictMeterId,mwhDate,myExp)
                        print(df)
                        print("before space adjustment")
                        if(isinstance(df, float)) : 
                            df = scalarToSeries(float(df),[fictMeterId + " " + getFictMeterInfoById(fictMeterId)['Fict_Meter_No'] + " " + mwhDate + " " + "0.0000 0.0 0.0"])

                        df = spaceAdjustmentFictMeter(df)
                        # print(df)
                        # Check if df is a series or float now. Act accordingly. 
                        # If df is float, it implies that fictMeterId,mwhDate etc info never used. Only ffOperation() is called.
                     
                        if not os.path.exists(relativeFilePath+mwhDate+"/"):
                            os.makedirs(relativeFilePath+mwhDate+"/")

                        df.to_csv(relativeFilePath + mwhDate + "/" + getFictMeterInfoById(fictMeterId)['Fict_Meter_No'] +'.MWH', header=False, index=None)

                        print(df)

            except KeyError as ke :
                undefinedFictMetConf.append("No equation defined in FICTMTRS.CFG, for Fictitious Meter ID : " + fictMeterId)
            except FileNotFoundError as fnfe :
                nonCalculatedFictMeterIds.append(fictMeterId)
                meterNumber = fnfe.filename.split('/')[-1][:-4]
                meterId = searchMeterId(meterNumber)
                fileNotFound.append("(" + meterId + " : " + meterNumber + ") not found, while calculating Fictitious Meter equation for Meter ID : " + fictMeterId)
                # meterNumber = fnfe.filename
                # fileNotFound.append("("  + " : " + meterNumber + ") not found, while calculating Fictitious Meter equation for Meter ID : " + fictMeterId)

    # Now it may be the case that if I calculate equation for the meters in nonCalculatedFictMeterIds, we may be able to 
    # calculate them as rest dependency may be solved by now. So do until there is no change in nonCalculatedFictMeterIds

    # nonCalculatedFictMeterIdsUpdated = []

    nonCalculatedFictMeterIdsOld = []

    while(nonCalculatedFictMeterIds != nonCalculatedFictMeterIdsOld) :
        nonCalculatedFictMeterIdsOld = nonCalculatedFictMeterIds
        nonCalculatedFictMeterIdsUpdated = []

        print("......Re-calculating again......")
        fileNotFound.clear()
        for fictMeterId in nonCalculatedFictMeterIds :

            eq = "("+fictMeterId+")"
            try :
                myExp = fictMeterDict[eq]    # "+3*MN-17+(MN-18)" . # This may through KeyEroor if no equation exists. 
                myExp = myExp.replace(' ','')
                myExp = myExp.replace('\t','')

                print(myExp)

                if(myExp[0] == '+' or myExp[0] == '-') :
                    myExp = '0' + myExp

                myExp = re.sub('([A-Z]{2})-([0-9]{2})', r'\1_\2', myExp)
                
                if(getFictMeterInfoById(fictMeterId) is not None) :

                    for mwhDate in mwhDates :
                        df = evaluate(fictMeterId,mwhDate,myExp)
                        print(df)
                        print("before space adjustment")

                        if(isinstance(df, float)) :
                            df = scalarToSeries(float(df),[fictMeterId + " " + getFictMeterInfoById(fictMeterId)['Fict_Meter_No'] + " " + mwhDate + " " + "0.0000 0.0 0.0"])

                        df = spaceAdjustmentFictMeter(df)
                        # Check if df is a series or float now. Act accordingly.
                        # If df is float, it implies that fictMeterId,mwhDate etc info never used. Only ffOperation() is called.

                  
                        if not os.path.exists(relativeFilePath+mwhDate+"/"):
                            os.makedirs(relativeFilePath+mwhDate+"/")

                        df.to_csv(relativeFilePath + mwhDate + "/" + getFictMeterInfoById(fictMeterId)['Fict_Meter_No'] +'.MWH', header=False, index=None)

            except FileNotFoundError as fnfe :
                nonCalculatedFictMeterIdsUpdated.append(fictMeterId)
                meterNumber = fnfe.filename.split('/')[-1][:-4]
                meterId = searchMeterId(meterNumber)
                fileNotFound.append("(" + meterId + " : " + meterNumber + ") not found, while calculating Fictitious Meter equation for Meter ID : " + fictMeterId)
                # meterNumber = fnfe.filename
                # fileNotFound.append("("  + " : " + meterNumber + ") not found, while calculating Fictitious Meter equation for Meter ID : " + fictMeterId)

        nonCalculatedFictMeterIds = nonCalculatedFictMeterIdsUpdated
                
    print(len(undefinedFictMetConf))
    print(len(fileNotFound))

    failureLogDf = pd.Series([],dtype=object)
    if(len(undefinedFictMetConf)) :
        failureLogDf = failureLogDf.append(pd.Series(["No equation defined in FICTMTRS.CFG for following :"]), ignore_index=True)
        failureLogDf = failureLogDf.append(pd.Series([" "]), ignore_index=True)

        for item in undefinedFictMetConf :
            failureLogDf = failureLogDf.append(pd.Series([item]), ignore_index=True)
        failureLogDf = failureLogDf.reset_index(drop=True)

    failureLogDf = failureLogDf.append(pd.Series([" "]), ignore_index=True)

    if(len(fileNotFound)) :

        failureLogDf = failureLogDf.append(pd.Series(["Can not calculate following Fictitious Meter equations :"]), ignore_index=True)
        failureLogDf = failureLogDf.append(pd.Series([" "]), ignore_index=True)

        for item in fileNotFound :
            failureLogDf = failureLogDf.append(pd.Series([item]), ignore_index=True)
        failureLogDf = failureLogDf.reset_index(drop=True)

    if(len(failureLogDf)):
        failureLogDf.to_csv(relativeFilePath + 'FailureLog.log', header=False, index=None)

    if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 5)) :
        print("New fictMeterMWHFile creation executed")

        fictMwhDict = {'lastIndex' : 1}

        jsonOutput = dirJsonFictMeterMWH(os.path.splitext(relativeFilePath)[0],_meterData,fictMwhDict)
        print(json.dumps(jsonOutput))
        print(fictMwhDict)
        
        fictMeterMWHFileObject = FictMeterMWHFile.objects.create(fictMwhDictionary = json.dumps(fictMwhDict),dirStructureFictMWH=json.dumps(jsonOutput), meterFile = _meterData)
        fictMeterMWHFileObject.save()

        AllMeterFiles.objects.filter(id = _meterData.id).update(status="FictCreated")
    
    ct2 = datetime.now()
    print(str(ct2-ct1))
    print(ct1)
    print(ct2)