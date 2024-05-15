from . import views
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
# from django.conf.urls import url
from django.urls import re_path
from django.views.static import serve






# urlpatterns = [
#     path('', views.index, name='index'),
# ]


urlpatterns = [
	path('', views.apiOverview, name="api-overview"),


    # path('addMasterData/', views.addMasterData, name="addMasterData"),
    # path('fetchMD/', views.fetchMD, name="fetchMD"),

    path('addNewMeterFile/', views.addNewMeterFile, name="addNewMeterFile"),
    path('getAllMeterData/', views.getAllMeterData, name="getAllMeterData"),
	path('getMeterData/<str:meter_id>', views.getMeterData, name = "getMeterData"),
	path('deleteNewMeterFile/<str:meter_id>', views.deleteNewMeterFile, name = "deleteNewMeterFile"),
	# path('editNewMeterFile/<str:meter_id>', views.editNewMeterFile, name = "editNewMeterFile"),
    
	path('getNPCData/<str:meter_id>', views.getNPCData, name ="getNPCData"),
	path('extract/<str:meter_id>', views.extract, name = "extract"),
	path('changeNPCFile/<str:meter_id>/<str:npc_id>', views.changeNPCFile, name ="changeNPCFile"),
	path('downloadNPCFile/<str:meter_id>/<str:npc_id>', views.downloadNPCFile, name ="downloadNPCFile"),
	path('reloadNPCData/<str:meter_id>', views.reloadNPCData, name ="reloadNPCData"),


	
	path('merge/<str:meter_id>', views.merge, name = "merge"),
	path('getMergedFile/<str:meter_id>', views.getMergedFile, name ="getMergedFile"),
	path('downloadMergedFile/<str:mergedFile_id>', views.downloadMergedFile, name ="downloadMergedFile"),
	path('changeMergedFile/<str:mergedFile_id>', views.changeMergedFile, name ="changeMergedFile"),

	path('dateFilter/<str:meter_id>', views.dateFilter, name = "dateFilter"),
	path('getDateFilteredFile/<str:meter_id>', views.getDateFilteredFile, name ="getDateFilteredFile"),
	path('downloadDateFilteredFile/<str:dateFilteredFile_id>', views.downloadDateFilteredFile, name ="downloadDateFilteredFile"),
	path('changeDateFilteredFile/<str:dateFilteredFile_id>', views.changeDateFilteredFile, name ="changeDateFilteredFile"),
	path('downloadNrxFile/<str:meter_id>', views.downloadNrxFile, name ="downloadNrxFile"),
	path('downloadNewNrxFile/<str:meter_id>', views.downloadNewNrxFile, name ="downloadNewNrxFile"),


	path('validate/<str:meter_id>', views.validate, name = "validate"),
	path('getValidatedFile/<str:meter_id>', views.getValidatedFile, name ="getValidatedFile"),
	path('downloadValidatedFile/<str:validatedFile_id>', views.downloadValidatedFile, name ="downloadValidatedFile"),
	path('changeValidatedFile/<str:validatedFile_id>', views.changeValidatedFile, name ="changeValidatedFile"),

    path('getRealMeterMWHData/<str:meter_id>', views.getRealMeterMWHData, name ="getRealMeterMWHData"),
	path('realMeterMWH/<str:meter_id>/<str:overWrite>', views.realMeterMWH, name = "realMeterMWH"),
	path('changeRealMeterMWHFile/<str:meter_id>/<str:realMeterMWH_id>', views.changeRealMeterMWHFile, name ="changeRealMeterMWHFile"),
	path('downloadRealMeterMWHFile/<str:meter_id>/<str:realMeterMWH_id>', views.downloadRealMeterMWHFile, name ="downloadRealMeterMWHFile"),
	path('downLoadFullRealMeterMWHFiles/<str:meter_id>', views.downLoadFullRealMeterMWHFiles, name ="downLoadFullRealMeterMWHFiles"),
	path('fetchFrequencyGraphData/<str:meter_id>', views.fetchFrequencyGraphData, name ="fetchFrequencyGraphData"),
	path('reloadRealMeterMWHData/<str:meter_id>', views.reloadRealMeterMWHData, name ="reloadRealMeterMWHData"),



	path('getFictMeterMWHData/<str:meter_id>', views.getFictMeterMWHData, name ="getFictMeterMWHData"),
	path('fictMeterMWH/<str:meter_id>', views.fictMeterMWH, name = "fictMeterMWH"),
	# path('testfictMeterMWH/<str:meter_id>', views.testfictMeterMWH, name = "testfictMeterMWH"),
	path('changeFictMeterMWHFile/<str:meter_id>/<str:fictMeterMWH_id>', views.changeFictMeterMWHFile, name ="changeFictMeterMWHFile"),
	path('downloadFictMeterMWHFile/<str:meter_id>/<str:fictMeterMWH_id>', views.downloadFictMeterMWHFile, name ="downloadFictMeterMWHFile"),
	path('downLoadFullFictMeterMWHFiles/<str:meter_id>', views.downLoadFullFictMeterMWHFiles, name ="downLoadFullFictMeterMWHFiles"),
	path('downLoadFullAllMWHFiles/<str:meter_id>', views.downLoadFullAllMWHFiles, name ="downLoadFullAllMWHFiles"),
	path('reloadFictMeterMWHData/<str:meter_id>', views.reloadFictMeterMWHData, name ="reloadFictMeterMWHData"),


	path('getFinalOutputData/<str:meter_id>', views.getFinalOutputData, name ="getFinalOutputData"),
	path('finalOutput/<str:meter_id>', views.finalOutput, name = "finalOutput"),
	path('finalOutputExcel/<str:meter_id>', views.finalOutputExcel, name = "finalOutputExcel"),
	path('nldcLossExcel/<str:meter_id>', views.nldcLossExcel, name = "nldcLossExcel"),
	path('changeFinalOutputFile/<str:meter_id>/<str:finalOutput_id>', views.changeFinalOutputFile, name ="changeFinalOutputFile"),
	path('downloadFinalOutputFile/<str:meter_id>/<str:finalOutput_id>', views.downloadFinalOutputFile, name ="downloadFinalOutputFile"),
	path('downLoadFullFinalOutputFiles/<str:meter_id>', views.downLoadFullFinalOutputFiles, name ="downLoadFullFinalOutputFiles"),
	path('reloadFinalOutputData/<str:meter_id>', views.reloadFinalOutputData, name ="reloadFinalOutputData"),


	path('analyseData/<str:meter_id>', views.analyseData, name = "analyseData"),
	path('fetchGraphData/<str:meter_id>/<str:end1>/<str:end2>/<str:polarity>/<str:dataType>',views.fetchGraphData,name="fetchGraphData"),
	path('fetchGraphDataExcel/<str:meter_id>/<str:end1>/<str:end2>/<str:polarity>/<str:dataType>',views.fetchGraphDataExcel,name="fetchGraphDataExcel"),
	path('fetchMeterChangeLog/<str:meter_id>',views.fetchMeterChangeLog,name="fetchMeterChangeLog"),
	path('fetchDateInfo/<str:meter_id>', views.fetchDateInfo, name="fetchDateInfo"),
	path('zeroFillMeterEndData/<str:meter_id>', views.zeroFillMeterEndData, name="zeroFillMeterEndData"),
	path('changeMeterEndData/<str:meter_id>', views.changeMeterEndData, name="changeMeterEndData"),
	path('revertMeterEndData/<str:meter_id>', views.revertMeterEndData, name="revertMeterEndData"),
	path('componentWiseAnalysis/<str:meter_id>', views.componentWiseAnalysis, name="componentWiseAnalysis"),
	path('componentWiseExcelData/<str:meter_id>/<str:meterEndToExcelData>', views.componentWiseExcelData, name="componentWiseExcelData"),

	# path('deleteWeeklyMeterData/<str:meter_id>', views.deleteWeeklyMeterData, name="deleteWeeklyMeterData"),
	path('pushWeeklyMeterDataToArchive/<str:meter_id>', views.pushWeeklyMeterDataToArchive, name="pushWeeklyMeterDataToArchive"),

	path('specialReports/<str:meter_id>', views.specialReports, name="specialReports"),
	path('compareEndsDataForLossAnalysis/<str:meter_id>', views.compareEndsDataForLossAnalysis, name="compareEndsDataForLossAnalysis"),
	path('downloadViolationForParticularFeeder/<str:meter_id>', views.downloadViolationForParticularFeeder, name="downloadViolationForParticularFeeder"),

	path('getNecessaryFiles', views.getNecessaryFiles, name ="getNecessaryFiles"),
	path('downLoadNecessaryFile/<str:necessaryFileId_id>', views.downLoadNecessaryFile, name ="downLoadNecessaryFile"),
	path('changeNecessaryFile/<str:necessaryFileId_id>', views.changeNecessaryFile, name ="changeNecessaryFile"),

	
	path('getAllDates/<str:meter_id>', views.getAllDates, name ="getAllDates"),
	path('getRealMetersListed/<str:meter_id>', views.getRealMetersListed, name ="getRealMetersListed"),
	path('getFictMetersListed/<str:meter_id>', views.getFictMetersListed, name ="getFictMetersListed"),



    re_path(r'^download/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

]
if settings.DEBUG:
	urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
	urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
