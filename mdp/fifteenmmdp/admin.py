from django.contrib import admin
# from .models import AllMeterFiles,NpcFile,MergedFile,DateFilteredFile,ValidatedFile,RealMeterMWHFile,FictMeterMWHFile,FinalOutputFile
from .models import *
# Register your models here.


admin.site.register(AllMeterFiles)
admin.site.register(NpcFile)
admin.site.register(MergedFile)
admin.site.register(DateFilteredFile)
admin.site.register(ValidatedFile)
admin.site.register(RealMeterMWHFile)
admin.site.register(FictMeterMWHFile)
admin.site.register(FinalOutputFile)
admin.site.register(NecessaryFile)