# import os
# from .models import AllMeterFiles,RealMeterMWHFile
# from django.core.files import File
# from django.conf import settings
# from .supportingFunctions import *
# import pandas as pd
# import json
# from datetime import datetime

# def generateMwhHeader(_meterHeaderData,_nextMeterHeaderData,_meterId,_meterName,_ctr,_ptr,_headerDate) :
#     # We have [NP-5851-A,    97845.9,    35371.6,    00136.0,    07-12-20] and for 08-12-20

#     actDiff = f'{((float(_nextMeterHeaderData[1]) - float(_meterHeaderData[1]))*_ctr*_ptr)/1000000 :.4f}'

#     reactiveHighDiff = f'{((float(_nextMeterHeaderData[2]) - float(_meterHeaderData[2]))*_ctr*_ptr)/1000000 :.1f}'

#     reactiveLowDiff = f'{((float(_nextMeterHeaderData[3]) - float(_meterHeaderData[3]))*_ctr*_ptr)/1000000 :.1f}'

#     # Adjusting the spaces
#     _mwhHeaderData = [_meterId," "+_meterName," "*3 + _headerDate," "*(14 - len(actDiff)) + actDiff," "*(11 - len(reactiveHighDiff)) + reactiveHighDiff," "*(9 - len(reactiveLowDiff)) + reactiveLowDiff]
#     return(_mwhHeaderData)


# def spaceAdjustmentRealMeterRow(_part) :
#     spaceAdjustedPart = []
#     for i in range(len(_part)) :
#         if(i == 0) :
#             spaceAdjustedPart.append(_part[i])
#         elif(i == 1) :
#             spaceAdjustedPart.append(" "*(16-len(_part[i])) + _part[i])
#         else :
#             spaceAdjustedPart.append(" "*(18-len(_part[i])) + _part[i])
#     return spaceAdjustedPart


# def dirJsonRealMeterMWH(path0,nPath,_meterData):
#     d = {'name': os.path.basename(nPath)}
#     # d['size'] = str("{0:.2f}".format((os.stat(path0).st_size / 1024)) + "KB")
#     if os.path.isdir(path0):
#         d['type'] = "folder"
#         # d['path'] = nPath
#         d['files'] = [dirJsonRealMeterMWH(os.path.join(path0, x),os.path.join(nPath, x),_meterData) for x in os.listdir(path0)]
#     else:
#         print(os.path.basename(nPath))
#         local_file = open(path0,"rb")  #Open file from path0 i.e. extracted first path.
#         realMeterMWHFileObject = RealMeterMWHFile.objects.create(fileName = os.path.basename(nPath), filePath = nPath, meterFile = _meterData)
#         realMeterMWHFileObject.realMeterMWHFile.save(os.path.basename(nPath),  File(local_file))
#         realMeterMWHFileObject.save()
#         local_file.close()
#         d['id'] = realMeterMWHFileObject.id
#         d['type'] = "file"
#         # d['path'] = nPath

#     return d

# def createRealMeterMWH(path,_meterData) :
#     print("i am in createRealMeterMWH " + path)
#     meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path) #Later "Validated File" path is added
#     relativeFilePathCopy = meterFileMainFolder+'/Real Meter MWH Files(Copy)/'
#     relativeFilePath = meterFileMainFolder+'/Real Meter MWH Files/'

#     if not os.path.exists(meterFileMainFolder +'/Real Meter MWH Files(Copy)'): 
#         os.makedirs(meterFileMainFolder + '/Real Meter MWH Files(Copy)')
#     if not os.path.exists(meterFileMainFolder +'/Real Meter MWH Files'):
#         os.makedirs(meterFileMainFolder + '/Real Meter MWH Files')


#     realMeterInfo = []
#     masterData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/master.dat', "r")
#     masterDataList = masterData.readlines()
#     masterData.close()
#     for elem in masterDataList :
#         if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
#             # print(elem.split())
#             realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3] })

#     # print(realMeterInfo)

#     def getMeterInfoById(Loc_Id) :
        
#         meterDetails =  [meter for meter in realMeterInfo if meter['Loc_Id'] == Loc_Id]  
        
#         if(len(meterDetails) < 1) :
#             print(Loc_Id + " not found in master.dat")
#             return None
#         else :
#             return(meterDetails[0])
        
            
            
#     def getMeterInfoByNo(Meter_No) :
        
#         meterDetails =  [meter for meter in realMeterInfo if meter['Meter_No'] == Meter_No]
        
#         if(len(meterDetails) < 1) :
#             return None
#         else :
#             return(meterDetails[0])

#     # Reading Master Frequency Info
#     masterFreqMeter = {"Loc_Id" : '' , "Meter_No" : '' , "ctr" : 0 , "ptr" : 0 }
#     masterFreqData = open(meterFileMainFolder+'/NPC Files/Necessary Files Local Copy/FRQMASTR.dat', "r")
#     masterFreqDataList = masterFreqData.readlines()
#     masterFreqData.close()
#     for elem in masterFreqDataList :
#         if(len(elem) > 1) :
#             # print(elem.split())
#             if(elem.split()[0] == 'LOC_ID') :
#                 masterFreqMeter['Loc_Id'] = elem.split()[1]
#             if(elem.split()[0] == 'METER_NO') :
#                 masterFreqMeter['Meter_No'] = elem.split()[1]
#             if(elem.split()[0] == 'CT_RATIO') :
#                 masterFreqMeter['ctr'] = elem.split()[1]
#             if(elem.split()[0] == 'PT_RATIO') :
#                 masterFreqMeter['ptr'] = elem.split()[1]
                
                
#     print(masterFreqMeter)

#     # Reading validated,datefiltered data
#     data = pd.read_csv(meterFileMainFolder+'/Validated File/ValidatedFile.npc', header = None)
#     dfSeries = pd.DataFrame(data)
#     df = dfSeries[0]
#     df


#     ct1 = datetime.now()

#     realMeterNotInDB = []

#     # errorList = []
#     # errorLine = 0
#     weekList = []
#     meterHeaderList = []

#     for i in range(len(df)-1) :
#         rowList = df[i].split()
#         rowList = extraCharHandler(rowList) # there can be extra char coz when validated we just ignored them. Didn't remove them.
#         if(rowList[0] == "WEEK") : weekList.append(i) # Rest already validated.
#         if(isMeterNumberPattern(rowList[0])) : meterHeaderList.append(i)
#     weekList.append(len(df)-1) #EOF index must be added

#     informationDict = getDfInfo(weekList,meterHeaderList)
#     print(informationDict)

#     for weekListIndex in weekList[:-1] :  # Will not take the EOFs index
#     # We don't need week header info here.
        
#         print("For weekheader"+str(weekListIndex)+" : "+str(informationDict[weekListIndex]))
        
#         for k in range(len(informationDict[weekListIndex])-2): 

#             mwhFile = pd.Series([],dtype=object)
#             frequencyData = [] # To store the frequency data.Later we will only take the frequency of master frequency only.

#     #         meterHeaderDataRaw = df[informationDict[weekListIndex][k]] # "NP-5851-A    97845.9    35371.6    00136.0    07-12-20"
#             meterHeaderData = extraCharHandler(df[informationDict[weekListIndex][k]].split()) 
#             nextMeterHeaderData = extraCharHandler(df[informationDict[weekListIndex][k+1]].split()) 
#             meterName = meterHeaderData[0] # Must be same as nextMeterHeaderData[0]. Check. Otherwise error. # Filename
#             ######################  Will be fetched from masterDataCtPtRatio  #####################
#             meterDetail = getMeterInfoByNo(meterName) # Actually it is called meter no, not meter name
#             if(meterDetail is None) :
#                 realMeterNotInDB.append("Meter Entry not in Database : " + meterName)
#                 continue
#             meterId = meterDetail['Loc_Id']
#             ctr = float(meterDetail['ctr'])
#             ptr = float(meterDetail['ptr'])
#             #######################################################################################
            
#             headerDate = meterHeaderData[4] # Foldername
#             # print(meterHeaderData)
            
#             mwhHeaderData = generateMwhHeader(meterHeaderData,nextMeterHeaderData,meterId,meterName,ctr,ptr,headerDate)
            
#             # mwhHeaderData = [ET-79, ER-1010-A,   07-12-20,    -3897.4000,      424.2,      0.0]"

#             mwhFile = mwhFile.append(pd.Series(''.join(mwhHeaderData)), ignore_index=True)
#             timeStamp = 0
#             for line in range(informationDict[weekListIndex][k]+1,informationDict[weekListIndex][k+1]):
#                 meterMainDataRaw = df[line]
#                 meterMainData = extraCharHandler(meterMainDataRaw.split())
#                 frequencyData = frequencyData + meterMainData[1 : 33 : 2]  # Only taking the frequency data
#                 # This row must be divided into 4 parts
#                 part1 = [str((timeStamp)*100).zfill(4)] + [f'{(float(initialCharHandler(x))*ctr*ptr)/1000000 :.6f}' for x in meterMainData[2:9:2]]
#                 part2 = [str((timeStamp+1)*100).zfill(4)] + [f'{(float(initialCharHandler(x))*ctr*ptr)/1000000 :.6f}' for x in meterMainData[10:17:2]]
#                 part3 = [str((timeStamp+2)*100).zfill(4)] + [f'{(float(initialCharHandler(x))*ctr*ptr)/1000000 :.6f}' for x in meterMainData[18:25:2]]
#                 part4 = [str((timeStamp+3)*100).zfill(4)] + [f'{(float(initialCharHandler(x))*ctr*ptr)/1000000 :.6f}' for x in meterMainData[26:33:2]]
                
#                 # print(part1)
                
#                 mwhFile = mwhFile.append(pd.Series(''.join(spaceAdjustmentRealMeterRow(part1))), ignore_index=True)
#                 mwhFile = mwhFile.append(pd.Series(''.join(spaceAdjustmentRealMeterRow(part2))), ignore_index=True)
#                 mwhFile = mwhFile.append(pd.Series(''.join(spaceAdjustmentRealMeterRow(part3))), ignore_index=True)
#                 mwhFile = mwhFile.append(pd.Series(''.join(spaceAdjustmentRealMeterRow(part4))), ignore_index=True)

#                 timeStamp = timeStamp + 4
            
            
#             mwhFile = mwhFile.reset_index(drop=True)
#             #print(mwhFile)
            
#             if not os.path.exists(relativeFilePathCopy+headerDate+"/"):
#                 os.makedirs(relativeFilePathCopy+headerDate+"/")
#             if not os.path.exists(relativeFilePath+headerDate+"/"):
#                 os.makedirs(relativeFilePath+headerDate+"/")

#             mwhFile.to_csv(relativeFilePathCopy + headerDate + "/" + meterName +'.MWH', header=False, index=None)
#             mwhFile.to_csv(relativeFilePath + headerDate + "/" + meterName +'.MWH', header=False, index=None)
            
#             if meterName == masterFreqMeter['Meter_No'] :
#                 masterFreq = pd.Series([],dtype=object)
#                 masterFreq = masterFreq.append(pd.Series(''.join('Master Frequency Data for the date: ' + headerDate)), ignore_index=True)

#                 masterFreq = masterFreq.append(pd.Series(' '.join(frequencyData)), ignore_index=True)
#                 masterFreq.to_csv(relativeFilePathCopy + headerDate + '/masterFrequency.MFD', header=False, index=None)
#                 masterFreq.to_csv(relativeFilePath + headerDate + '/masterFrequency.MFD', header=False, index=None)

#                 print("Meter name : " + meterName + ". Freq : " + str(frequencyData))
            
#             print("Changing meter header")
#         print("----------------------Changing Week header------" + str(weekListIndex) + "-----------------------------")
#     print("-------------------------Done-------------------------")

#     # print(realMeterNotInDB)

#     for elem in ((list(set(realMeterNotInDB)))) :
#         print(elem)
#     # print((len(realMeterNotInDB)))
#     # print(len(set(realMeterNotInDB)))
#     realMeterMWHFilesCopyFolderPath = os.path.join("fifteenmmdp/media/meterFile",path,'Real Meter MWH Files(Copy)')
#     realMeterMWHFilesFolderPath = os.path.join("meterFile",path,'Real Meter MWH Files')
#     if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 4)) :
#         print("New realMeterMWHFile creation executed")
#         jsonOutput = dirJsonRealMeterMWH(os.path.splitext(realMeterMWHFilesCopyFolderPath)[0],os.path.splitext(realMeterMWHFilesFolderPath)[0],_meterData)
#         print(json.dumps(jsonOutput))
#         AllMeterFiles.objects.filter(id = _meterData.id).update(dirStructureRealMWH = json.dumps(jsonOutput),status="MWHCreated")
    
#     ct2 = datetime.now()
#     print(str(ct2-ct1))
#     print(ct1)
#     print(ct2)