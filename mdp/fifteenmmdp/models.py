from django.db import models
from .validators import validate_file_extension,validate_file_extension_npc,validate_file_extension_MWH
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
# Create your models here.

class OverwriteStorage(FileSystemStorage):
    def get_valid_name(self, name):
        print("inside OverwriteStorage")
        print(name)
        # return get_valid_filename(name)
        return name
    def get_available_name(self, name,max_length=None):
        if self.exists(name):
            print("inside OverwriteStorage")
            print(name)
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

def upload_path(instance, filename):
    return '/'.join(['meterFile', 'meterFile' + str(instance.id), filename])

class AllMeterFiles(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    
    startDate = models.DateField(null=True) 
    endDate = models.DateField(null=True) 

    zippedMeterFile = models.FileField(upload_to = upload_path,validators=[validate_file_extension],max_length=1023)
    
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(null=True,max_length=255)  

    # {'Uploaded' , 'Extracted' , 'Merged' ,'Verified', 'DateFiltered', 'MWHCreated', 'FictCreated' , 'FinalOutputCreated' }

    def __str__(self):
        return("Meter ID : "+ str(self.id) +". Data for " + self.month + "," + self.year)
    
    def myId(self):
        return self.id

def upload_path_mergedFile(instance, filename):
    # return '/'.join(['meterFile', 'meterFile' + str(instance.id),'Merged File', filename])
    return instance.filePath


def upload_path_dateFilteredFile(instance, filename):
    # return '/'.join(['meterFile', 'meterFile' + str(instance.id),'Merged File', filename])
    return instance.filePath

def upload_path_validatedFile(instance, filename):
    # return '/'.join(['meterFile', 'meterFile' + str(instance.id),'Merged File', filename])
    return instance.filePath

def upload_path_realMeterMWH(instance, filename):
    # return '/'.join(['meterFile', 'meterFile' + str(instance.id),'Merged File', filename])
    return instance.filePath
def upload_path_npc(instance, filename):
    # return '/'.join(['meterFile', 'meterFile' + str(instance.id),'Merged File', filename])
    return instance.filePath

def upload_path_necessaryFile(instance, filename):
    # return '/'.join(['necessaryFiles', filename])
    return instance.filePath

class NpcFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    dirStructureNPC = models.TextField(null=True) # JSON-serialized (text) version of your "NPC Files" Folder Structure.
    npcDictionary = models.TextField(null=True)
    meterFile = models.OneToOneField(AllMeterFiles, on_delete=models.CASCADE)

    def __str__(self):
        return("NPC Data for Meter ID : "+ str(self.meterFile.id))
    def npcFileMeterId(self):
        return(str(self.meterFile.id))


class MergedFile(models.Model):
    id = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255)
    filePath = models.CharField(max_length=1023)
    meterFile = models.OneToOneField(AllMeterFiles,on_delete=models.CASCADE)
    mergedFile = models.FileField(upload_to = upload_path_mergedFile,null=True,validators=[validate_file_extension_npc],max_length=1023,storage=OverwriteStorage())

    def __str__(self):
        return("Merged File for Meter ID : "+ str(self.meterFile.id))
    def mergedFileMeterId(self):
        return(str(self.meterFile.id))


class DateFilteredFile(models.Model):
    id = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255)
    filePath = models.CharField(max_length=1023)
    meterFile = models.OneToOneField(AllMeterFiles,on_delete=models.CASCADE)
    dateFilteredFile = models.FileField(upload_to = upload_path_dateFilteredFile,null=True,validators=[validate_file_extension_npc],max_length=1023,storage=OverwriteStorage())

    def __str__(self):
        return("DateFiltered File for Meter ID : "+ str(self.meterFile.id))
    def dateFilteredFileMeterId(self):
        return(str(self.meterFile.id))


class ValidatedFile(models.Model):
    id = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255)
    filePath = models.CharField(max_length=1023)
    meterFile = models.OneToOneField(AllMeterFiles,on_delete=models.CASCADE)
    validatedFile = models.FileField(upload_to = upload_path_validatedFile,null=True,validators=[validate_file_extension_npc],max_length=1023,storage=OverwriteStorage())

    def __str__(self):
        return("ValidatedFile File for Meter ID : "+ str(self.meterFile.id))
    def validatedFileMeterId(self):
        return(str(self.meterFile.id))

class RealMeterMWHFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    dirStructureRealMWH = models.TextField(null=True) # JSON-serialized (text) version of your "Real Meter MWH Files" Folder Structure.
    mwhDictionary = models.TextField(null=True)
    meterFile = models.OneToOneField(AllMeterFiles, on_delete=models.CASCADE)

    def __str__(self):
        return("Real MWH File for Meter ID : "+ str(self.meterFile.id))
    def realMeterMWHFileMeterId(self):
        return(str(self.meterFile.id))

class FictMeterMWHFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    dirStructureFictMWH = models.TextField(null=True) # JSON-serialized (text) version of your "Fict Meter MWH Files" Folder Structure.
    fictMwhDictionary = models.TextField(null=True)
    meterFile = models.OneToOneField(AllMeterFiles, on_delete=models.CASCADE)

    def __str__(self):
        return("Fict MWH File for Meter ID : "+ str(self.meterFile.id))
    def fictMeterMWHFileMeterId(self):
        return(str(self.meterFile.id))

class FinalOutputFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    dirStructureFinalOutput = models.TextField(null=True) # JSON-serialized (text) version of your "Final Output Files" Folder Structure.
    finalOutputDictionary = models.TextField(null=True)
    meterFile = models.OneToOneField(AllMeterFiles, on_delete=models.CASCADE)

    def __str__(self):
        return("Final Output File for Meter ID : "+ str(self.meterFile.id))
    def finalOutputFileMeterId(self):
        return(str(self.meterFile.id))

class NecessaryFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    fileName = models.CharField(max_length=1023,null=True)
    filePath = models.CharField(max_length=1023,null=True)
    subTitle = models.TextField(null=True)
    description = models.TextField(null=True)
    necessaryFile = models.FileField(upload_to = upload_path_necessaryFile,max_length=1023,storage=OverwriteStorage())

    def __str__(self):
        return(str(self.fileName))
