import re
def isMeterNumberPattern(value) :
    meterNumberPattern = re.compile(r'^[A-Z]{2}-[0-9]{4}-[A-Z]$')
    result = re.match(meterNumberPattern, value)
    if result:
        return True
    else:
        return False
    
def isMeterIdPattern(value) :
    meterIdPattern = re.compile(r'^[A-Z]{2}-[0-9]{2}$')
    result = re.match(meterIdPattern, value)
    if result:
        return True
    else:
        return False

class MeterUtil :
        
    realMeterInfo = []
    fictMeterInfo = []
    realMetersToBeListed = []
    fictMetersToBeListed = []
    fictMeterDict = {}

    # constructor function    
    def __init__(self, configPath):
        
        self.realMeterInfo = []
        self.fictMeterInfo = []
        self.realMetersToBeListed = []
        self.fictMetersToBeListed = []
        self.fictMeterDict = {}

        # Setting Real Meter Data
        masterData = open(f'{configPath}/master.dat', "r")
        masterDataList = masterData.readlines()
        masterData.close()
        for elem in masterDataList :
            if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
                # print(elem.split())
                self.realMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1] , "ctr" : elem.split()[2] , "ptr" : elem.split()[3], "Place_Of_Inst" : ' '.join(elem.split()[4 : ]) })

        # print(self.realMeterInfo)

        # Setting Fictitious Meter Data
        # [{'Loc_Id': 'FK-91', 'Meter_No': 'FKK-TOT-LN'} ,{'Loc_Id': 'FK-93', 'Meter_No': 'FKK-TOT-CL'}]
    
        fictInfoData = open(f'{configPath}/FICTMTRS.dat', "r")

        fictInfoDataList = fictInfoData.readlines()
        fictInfoData.close()
        for elem in fictInfoDataList :
            if(len(elem) > 1 and isMeterIdPattern(elem.split()[0])) :
                # print(elem.split())
                self.fictMeterInfo.append({"Loc_Id" : elem.split()[0] , "Meter_No" : elem.split()[1], "Description" : ' '.join(elem.split()[2 : ]) })


        # Setting Fictitious Config/Equation Data

        # 'fictMeterDict' stores equation data. 
        # fictMeterDict['(BM-99)'] gives      -(BI-09)*0.97899. trim spaces later. \n trimmed

        fctCFG = open(f'{configPath}/FICTMTRS.CFG', "r")
        fList = fctCFG.readlines()
        # print(len(fList[len(fList)-2]))
        # print((fList[len(fList)-2])[:3])

        fctCFG.close()
        startIndex = 1
        # print(fList)


        fictMeterIdIndex = []
        for elemIndex in range(len(fList)) :
            if(fList[elemIndex].isspace()) :
                continue
            if(fList[elemIndex].split()[0].isdigit() and int(fList[elemIndex].split()[0]) == startIndex) :
                fictMeterIdIndex.append(elemIndex)
                startIndex += 1
        if(fList[len(fList)-2][:3] == "END") :
            fictMeterIdIndex.append(len(fList)-2)  # Must append END index too
        else :
            print("Error")

        for i in range(len(fictMeterIdIndex)-1) :
        #     print("i value " + str(fictMeterIdIndex[i]))
            self.fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] = ""

            for j in range(fictMeterIdIndex[i]+1,fictMeterIdIndex[i+1]) :
                self.fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] = self.fictMeterDict[fList[fictMeterIdIndex[i]].split()[1]] + (fList[j].replace('\n',''))
        
        # print(fictMeterDict['(BM-99)'])
        # print(len(fictMeterDict))
        
    def getAllRealMeters(self) :
        return self.realMeterInfo
    
    def getAllFictitiousMeters(self) :
        return self.fictMeterInfo
    
    ################################################### All RealMeters here. List of Real meters : #############################################
    
    def getMeterInfoById(self, Loc_Id) :

        meterDetails =  [meter for meter in self.realMeterInfo if meter['Loc_Id'] == Loc_Id]  

        if(len(meterDetails) < 1) :
            print(Loc_Id + " not found in master.dat")
            return None
        else :
            return(meterDetails[0])

    def getMeterInfoByNo(self, Meter_No) :

        meterDetails =  [meter for meter in self.realMeterInfo if meter['Meter_No'] == Meter_No]

        if(len(meterDetails) < 1) :
            return None
        else :
            return(meterDetails[0])


    ################################################### All FictMeters here. List of fict meters : #############################################

    def getFictMeterInfoById(self, Loc_Id) :

        fictMeterDetails =  [meter for meter in self.fictMeterInfo if meter['Loc_Id'] == Loc_Id]

        if(len(fictMeterDetails) < 1) :
            print(Loc_Id + " not found in FICTMTRS.dat")
            return None
        else :
            return(fictMeterDetails[0])

    ################################################### Search any meter here. #################################################################

    def searchMeterNumber(self, Loc_Id) : # Any meter real or fictitious. Returns meter number.
        meterDetails =  [meter for meter in self.realMeterInfo if meter['Loc_Id'] == Loc_Id]
        fictMeterDetails =  [meter for meter in self.fictMeterInfo if meter['Loc_Id'] == Loc_Id]
        if(len(meterDetails) != 0) : return meterDetails[0]['Meter_No']
        if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Meter_No']
        return "FileNotFound"

    def searchMeterId(self, Meter_No) : # Any meter real or fictitious. Returns meter Loc_Id.
        meterDetails =  [meter for meter in self.realMeterInfo if meter['Meter_No'] == Meter_No]
        fictMeterDetails =  [meter for meter in self.fictMeterInfo if meter['Meter_No'] == Meter_No]
        if(len(meterDetails) != 0) : return meterDetails[0]['Loc_Id']
        if(len(fictMeterDetails) != 0) : return fictMeterDetails[0]['Loc_Id']
        # return None
        return "Loc_Id not found"

    ################################################### get Meters To Be Listed Here. #################################################################

    def getRealMeters(self, fetchBy):
                
        if(fetchBy == 'meterID') :
            self.realMetersToBeListed = [{'name' : f'{realMeter["Loc_Id"]}', 'code' : f'{realMeter["Loc_Id"]}'} for realMeter in self.realMeterInfo]
        if(fetchBy == 'meterNO') :
            self.realMetersToBeListed = [{'name' : f'{realMeter["Meter_No"]}', 'code' : f'{realMeter["Meter_No"]}'} for realMeter in self.realMeterInfo]


        return self.realMetersToBeListed


    def getFictitiousMeters(self, fetchBy):

        if(fetchBy == 'meterID') :
            self.fictMetersToBeListed = [{'name' : f'{fictMeter["Loc_Id"]}', 'code' : f'{fictMeter["Loc_Id"]}'} for fictMeter in self.fictMeterInfo]
        if(fetchBy == 'meterNO') :
            self.fictMetersToBeListed = [{'name' : f'{fictMeter["Meter_No"]}', 'code' : f'{fictMeter["Meter_No"]}'} for fictMeter in self.fictMeterInfo]

        return self.fictMetersToBeListed



    ################################################### Get all the equations of Fictitious Meters #############################################

    # 'fictMeterDict' stores equation data. 
    # fictMeterDict['(BM-99)'] gives      -(BI-09)*0.97899. trim spaces later. \n trimmed

    def getFictitiousMeterEqutation(self, Loc_Id) :
        return self.fictMeterDict[Loc_Id]
    
    
    def getAllFictitiousMeterEqutation(self) :
        return self.fictMeterDict