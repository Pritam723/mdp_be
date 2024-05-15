import os
from .models import NpcFile
from django.core.files import File


def dirJsonNPC(nPath,_meterData,npcDict):
    d = {'name': os.path.basename(nPath)}
    # d['size'] = str("{0:.2f}".format((os.stat(nPath).st_size / 1024)) + "KB")
    if os.path.isdir(nPath):
        d['type'] = "folder"
        d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')
        d['files'] = [dirJsonNPC(os.path.join(nPath, x),_meterData,npcDict) for x in os.listdir(nPath)]
    else:
        if(os.path.splitext(nPath)[1].lower() == '.npc' or os.path.splitext(nPath)[1].lower() == '.dat' or os.path.splitext(nPath)[1].lower() == '.cfg' or os.path.splitext(nPath)[1].lower() == '.xlsx') :
            print(os.path.basename(nPath))

            d['id'] = npcDict['lastIndex']
            npcDict[npcDict['lastIndex']] = os.path.relpath(nPath, 'fifteenmmdp/media')
            npcDict['lastIndex'] = npcDict['lastIndex'] + 1

            d['type'] = "file"
            d['path'] = os.path.relpath(nPath, 'fifteenmmdp/media')

        else : 
            pass
    return d

