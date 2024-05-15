import os
from .models import AllMeterFiles,FinalOutputFile
from django.core.files import File
from django.conf import settings
from .supportingFunctions import *
import pandas as pd
import json
from datetime import time,timedelta,datetime
import math
from .nldcLossExcelFile import createNldcLossExcel

def headerInfoSpaceFix(_headerInfo,_spacingInfo):
    for i in range(len(_headerInfo[0])) :
        for j in range(len(_headerInfo)) :
            _headerInfo[j][i] = " " * (_spacingInfo[i] - len(_headerInfo[j][i].split('@')[0].rstrip())) + _headerInfo[j][i].split('@')[0].rstrip()
    return _headerInfo

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

def createFinalOutputExcel(path):
    print("Inside createFinalOutputExcel")

    # meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path)
    # relativeFilePathCopy = meterFileMainFolder+'/Fictitious Meter MWH Files(Copy)/'
    meterFileMainFolder = os.path.join("fifteenmmdp/media/meterFile",path)

    relativeFilePath = meterFileMainFolder+'/Final Output Files/'
    mwhDates = list(filter(isDate, os.listdir(meterFileMainFolder+'/Real Meter MWH Files')))
    mwhDates = sortDateStrings(mwhDates)

    ################################################### Performing main operation #######################################
    
    ################################################# Reading the Configuration File ####################################

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

    allFinalOutputDF = []
    allExtensions = []
    
    for configuration in (allConfigurations) :
        configName = configuration['Configuration Name']
        extension = configuration['EXTENSION']
        
        
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

    #     print(spacingInfo)


        headerInfoSpacingFixed = headerInfoSpaceFix(headerInfo,spacingInfo)
    #     print(headerInfoSpacingFixed)
        
        
        headerInfoSpacingFixedPrefixAdded = []

        for item in range(len(headerInfoSpacingFixed)) :

            headerArray = [''] + [item.lstrip() for item in headerInfoSpacingFixed[item]]

            #     headerInfoSpacingFixedPrefixAdded.append(headerArray.insert(0,''))

            #     print(headerArray)
            headerInfoSpacingFixedPrefixAdded.append(headerArray)

    #     print(headerInfoSpacingFixedPrefixAdded)
    #     print(configName,extension)
    #     print(numberOfHeaders)

    ################################################# Reading the Configuration File Done ####################################

        numberOfHeaders = len(headerInfoSpacingFixedPrefixAdded)
        
        colNames = []
        for i in range(len(headerInfoSpacingFixedPrefixAdded[0])) : # Runs from 0 to 51
            colTup = []
            for j in range(numberOfHeaders) : # Runs from 0 to 
                colTup.append(headerInfoSpacingFixedPrefixAdded[j][i])
            colNames.append(tuple(colTup))
            
        finalData = []
        
        for mwhDate in mwhDates :

            _mwhDate = mwhDate.replace('-','')
            if os.path.exists(meterFileMainFolder + '/Final Output Files/'+ mwhDate + "/" + _mwhDate + '.' + extension):

                data = pd.read_csv(meterFileMainFolder + '/Final Output Files/'+ mwhDate + "/" + _mwhDate + '.' + extension, header = None, skiprows = 5 + numberOfHeaders)

                dfSeries = pd.DataFrame(data)
                df = dfSeries[0]

                for i in range(96) :
                    dataArray = df[i].split()
                    dataArray =  [mwhDate] + dataArray
                    finalData.append(dataArray)

                spaceArray = ['']*len(finalData[0])
                finalData.append(spaceArray)
                weeklyCumulative = df[97].split()[1:]
                weeklyCumulative = [f'Total for {mwhDate}', '',''] + weeklyCumulative 
                finalData.append(weeklyCumulative)
                finalData.append(spaceArray)

            else :
                print(meterFileMainFolder + '/Final Output Files/'+ mwhDate + "/" + _mwhDate + '.' + extension + " Does not exist")
                

        finalDataFrame = pd.DataFrame(data = finalData, columns = pd.MultiIndex.from_tuples(colNames))
        finalDataFrame = finalDataFrame.set_index('')
        #             finalDataFrame.to_excel(f'{extension}.xlsx')

        allFinalOutputDF.append(finalDataFrame)
        allExtensions.append(extension)

    with pd.ExcelWriter(meterFileMainFolder + '/Final_Output_Excel.xlsx', mode='w') as writer:
        for index,extension in enumerate(allExtensions) :
            allFinalOutputDF[index].to_excel(writer, sheet_name=extension)


    ## Create/Update NLDC Loss File.
    createNldcLossExcel(path)

################################################### End ##################################################################
