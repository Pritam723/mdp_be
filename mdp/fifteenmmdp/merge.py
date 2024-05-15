from pathlib import Path
import pandas as pd
import os
from django.conf import settings
from .models import AllMeterFiles,MergedFile
from .supportingFunctions import *

def mergeNPCs(path,_meterData):
    print("i am in merge " + path)
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile",path) #Later "NPC Files" path is added

    if not os.path.exists(meterFileMainFolder +'/Merged File(Copy)'):
        os.makedirs(meterFileMainFolder + '/Merged File(Copy)')
    if not os.path.exists(meterFileMainFolder +'/Merged File'):
        os.makedirs(meterFileMainFolder + '/Merged File')
    # count = 0;
    npcFileList = []
    for file_path in Path(os.path.join(meterFileMainFolder,"NPC Files")).glob('**/*.npc'):  #Takes care of all case insensitive .NPC files.
    #     count =  count + 1
        npcFileList.append(str(file_path))    
    # print(npcFileList)
    print(len(npcFileList))
    # print(count)


    masterDf = pd.Series([],dtype=object)
    errorList = []
    for npcFile in npcFileList :
        errorLine = 1
        try : 
            data = pd.read_csv(npcFile, header = None)
            dfSeries = pd.DataFrame(data)
            df = dfSeries[0]
            for i in range(len(df)) :
                errorLine = i
                if(not (df[i].split()[0] == 'WEEK' or df[i].split()[0] in checkTimeStamp or isMeterNumberPattern(df[i].split()[0]))) :
                    df = df.drop([i])
            df = df.reset_index(drop=True)
    #         print(type(df))
            masterDf = pd.concat([masterDf,df],ignore_index=True)
        #     print(masterDf)
    #         print("*************Again*************")
        except UnicodeDecodeError as uniE :
            errorList.append("Can't append file : " + os.path.relpath(npcFile, meterFileMainFolder) + ". Contains invalid characters.")
        except Exception as e:
            errorList.append(str(e) + " in file " + os.path.relpath(npcFile, meterFileMainFolder) + " at line no " + str(errorLine))

    masterDf = masterDf.append(pd.Series(["EOF"]), ignore_index=True)
    masterDf = masterDf.reset_index(drop=True)
    print(masterDf)
    print("No. of errors : " + str(len(errorList)))

    if(len(errorList) == 0) :
        print("Success")

        masterDf.to_csv(meterFileMainFolder+'/Merged File(Copy)/MergedFile.npc'  , header=False, index=None)
        masterDf.to_csv(meterFileMainFolder+'/Merged File/MergedFile.npc'  , header=False, index=None)

        if(not (_meterData.status is None) and (statusCodes.index(_meterData.status) == 1)) :
            print("New MergeFileId added")
            local_file = open(meterFileMainFolder+'/Merged File(Copy)/MergedFile.npc',"rb")
            mergedFileObject = MergedFile.objects.create(fileName = 'MergedFile.npc', filePath = os.path.join("meterFile",path,"Merged File/MergedFile.npc"), meterFile = _meterData)
            mergedFileObject.mergedFile.save("MergedFile.npc",  File(local_file))
            mergedFileObject.save()
            local_file.close()
            AllMeterFiles.objects.filter(id = _meterData.id).update(status="Merged")

        return errorList
    else :
        print("Failed")
        # print(errorList)
        return errorList
