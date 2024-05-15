from django.http import HttpResponse
from .lossAnalysisCompareEnds import singleDayViolations
# from .supportingFunctions import *
from django.conf import settings
from datetime import time,timedelta,datetime
import pandas as pd
import numpy as np

def violationForParticularFeeder(request, path) :

    parameter = request.POST['parameter']
    percentageDiff = request.POST['percentageDiff']
    mwhDiff = request.POST['mwhDiff']
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    end1 = request.POST['end1']
    end2 = request.POST['end2']
    # Dates are in String Format. For 12th June 2023 we have 06/12/2023 00:00:00
    
    startDateObject = datetime.strptime(startDate, '%m/%d/%Y %H:%M:%S')
    endDateObject = datetime.strptime(endDate, '%m/%d/%Y %H:%M:%S')

    violations = []
    if(startDateObject == endDateObject) :
        print("Start date end date same")
        fromTime = datetime.strftime(startDateObject, "%H:%M")
        toTime = datetime.strftime(endDateObject, "%H:%M")
        singleDayViolations(startDateObject.date(), end1, end2, fromTime, toTime, violations,parameter,percentageDiff,mwhDiff, path, violationCountOnly = False)

    else :
        for day in range((endDateObject - startDateObject).days + 1) :
            dateObj = startDateObject+timedelta(days=day)
            print(dateObj)

            if(dateObj.date() == startDateObject.date()) :
                print("This is start date")
                fromTime = datetime.strftime(startDateObject, "%H:%M")
                singleDayViolations(dateObj.date(), end1, end2, fromTime, '23:45', violations,parameter,percentageDiff,mwhDiff, path, violationCountOnly = False)

            elif(dateObj.date() == endDateObject.date()) :
                print("This is end date")
                toTime = datetime.strftime(endDateObject, "%H:%M")
                singleDayViolations(dateObj.date(), end1, end2, '00:00', toTime, violations,parameter,percentageDiff,mwhDiff, path, violationCountOnly = False)

            else :
                print("Date in between")
                singleDayViolations(dateObj.date(), end1, end2, '00:00', '23:45', violations,parameter,percentageDiff,mwhDiff, path, violationCountOnly = False)

    print(violations)


    content = f"{end1} vs {end2} Comparison"
    content = content + "\n----------------------------------------------------------------------------------------------\n"
    content = content + "----------------------------------------------------------------------------------------------\n\n"

    for violation in violations :
        content = content + violation['label'] + "\n"
        
        for info in violation['violationInfo'] :
            content = content + info + "\n"
        content = content + "----------------------------------------------------------------------------------------------\n"

    filename = f"{end1} vs {end2} Comparison.txt"
    # content = f"{end1} vs {end2} Comparison"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
