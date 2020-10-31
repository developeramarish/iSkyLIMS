import datetime, os
from django.db import models
from django import forms
from django.contrib.auth.models import User
#from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField
from django.utils.timezone import now as timezone_now

#from iSkyLIMS_wetlab.models import RunProcess, Projects

from django_utils.models import Profile,Center
from django.contrib.auth.models import User

from iSkyLIMS_core.models import Samples
from iSkyLIMS_drylab import drylab_config


STATUS_CHOICES = (
			('recorded',_("Recorded")),
	   		('approved',_("Approved")),
			('rejected',_("Rejected")),
			('queued',_("Queued")),
			('in_progress',_('In progress')),
			('delivered',_("Delivered")),
			('archived',_("Archived"))
		)

def service_files_upload(instance,filename):
	now = timezone_now()
	filename_base,filename_ext = os.path.splitext(filename)
	return 'iSkyLIMS_drylab/servicesRequest/%s_%s%s' % (
			now.strftime("%Y%m%d%H%M%S"),
			filename_base.lower(),
			filename_ext.lower(),
	)

class ResolutionStates(models.Model):
	resolutionStateName = models.CharField(max_length=50)

	def __str__ (self):
		return '%s' %(self.resolutionStateName)

	def get_resolution_state (self):
		return '%s' %(self.resolutionStateName)

class FileExt(models.Model):
	fileExt=models.CharField(_("File extension"),max_length=10)
	def __str__ (self):
		return '%s' %(self.fileExt)

class Platform(models.Model):
	platformName=models.CharField(_("Sequencing platform"),max_length=20)

	def __str__ (self):
 		return '%s' %(self.platformName)

	def get_platform_name(self):
		return '%s'  %(self.platformName)

class Machines (models.Model) :
	platformID = models.ForeignKey(Platform ,on_delete=models.CASCADE)
	machineName = models.CharField(_("Machine Name"),max_length=255)
	machineDescription = models.CharField(_("Description"),max_length=255,null=True,blank=True)
	machineLocation = models.CharField(_("Location"),max_length=255,null=True,blank=True)
	machineProvider = models.CharField(_("Machine owner brand"),max_length=255,null=True,blank=True)
	machineSerialNumber = models.CharField(_("Serial Number"),max_length=255,null=True,blank=True)
	machineState =  models.CharField(_("Machine State"),max_length=50,null=True,blank=True)
	machineOperationStart = models.DateField(auto_now_add=False, null=True,blank=True)
	machineOperationEnd = models.DateField(auto_now_add=False, null=True,blank=True)
	machineNumberLanes = models.CharField("Number of Lanes", max_length= 5)

	def __str__ (self) :
		return '%s' %(self.machineName)


	def get_machine_name(self):
		return '%s'  %(self.machineName)

	def get_number_of_lanes(self):
		return '%s' %(self.machineNumberLanes)

class AvailableService(MPTTModel):
	availServiceDescription=models.CharField(_("Available services"),max_length=100)
	parent=TreeForeignKey('self',models.SET_NULL,null=True,blank=True)

	def __str__(self):
		return '%s' %(self.availServiceDescription)

	def get_service_description(self):
		return '%s' %(self.availServiceDescription)

	class Meta:
		ordering = ["tree_id","lft"]
		verbose_name = ("AvailableService")
		verbose_name_plural = ("AvailableServices")


class PipelinesManager (models.Manager):
	def create_pipeline(self, data):
		availableService = AvailableService.objects.get(pk__exact = data['availableService_id'])

		new_pipeline = self.create(availableService = availableService, userName = data['userName'],
				pipelineName = data['pipelineName'], pipelineInUse = True,
				pipelineVersion	= data['pipelineVersion'],
				#externalRequest = data['externalRequest'], useRunFolder = data['useRunFolder']
				)
		return new_pipeline

class Pipelines(models.Model):
	availableService = models.ForeignKey(
				AvailableService,
				on_delete = models.CASCADE)
	userName = models.ForeignKey(
                User,
                on_delete=models.CASCADE)
	pipelineName = models.CharField(max_length = 50)
	pipelineVersion = models.CharField(max_length = 10)
	#useRunFolder = models.BooleanField(default = True, null = True)
	#externalRequest = models.BooleanField(default = True)
	#default = models.BooleanField(default = False)
	pipelineInUse = models.BooleanField(default = True)
	generated_at = models.DateTimeField(auto_now_add = True)
	#automatic = models.BooleanField(default = True)

	def __str__ (self):
		return '%s_%s' %(self.pipelineName, self.pipelineVersion)

	'''
	def get_all_pipeline_data(self):
		data = []
		data.append(self.availableService.get_service_description())
		data.append(self.userName.username)
		data.append(self.pipelineName)
		data.append(self.pipelineVersion)
		data.append(self.generated_at.strftime("%B %d, %Y"))
		data.append(self.default)
		data.append(self.pipelineInUse)
		return data
	'''


	def get_pipeline_name (self):
		return '%s' %(self.pipelineName)

	def get_external_request(self):
		return '%s' %(self.externalRequest)

	def get_pipleline_service(self):
		return  '%s' %(self.availableService.get_service_description())

	def get_pipleline_service_obj(self):
		return self.availableService

	def get_pipeline_version(self):
		return '%s' %(self.pipelineVersion)

	def get_pipeline_additional(self):
		data = []
		data.append(self.userName.username)
		data.append(self.generated_at.strftime("%B %d, %Y"))

		data.append(self.default)
		data.append(self.pipelineInUse)
		data.append(self.externalRequest)
		return data

	def get_pipeline_basic (self):
		data = []
		data.append(self.pipelineName)
		data.append(self.pipelineVersion)
		data.append(self.availableService.get_service_description())
		return data

	def get_pipeline_info(self):
		data = []
		data.append(self.availableService.get_service_description())
		data.append(self.userName.username)
		data.append(self.pipelineName)
		data.append(self.pipelineVersion)
		data.append(self.generated_at.strftime("%B %d, %Y"))
		data.append(self.default)
		data.append(self.pipelineInUse)
		data.append(self.pk)
		return data

	def get_used_run_folder (self):
		return '%s' %(self.useRunFolder)

	def remove_default_pipeline(self):
		self.default = False
		self.save()
		return self

	def set_default_pipeline(self):
		self.default = True
		self.save()
		return self


	objects = PipelinesManager()

class ServiceManager (models.Manager):
	def create_service(self, data):
		new_service = self.create(serviceUserId = data['serviceUserId'], serviceSeqCenter= data['serviceSeqCenter'],
		serviceRequestNumber = data['serviceRequestNumber'], serviceRequestInt = data['serviceRequestInt'],
		serviceStatus= data['serviceStatus'], serviceNotes = data['serviceNotes'])
		return new_service


class Service(models.Model):
	## User requesting service:
	# 'serviceUsername' refactored to 'serviceUserid' which shows better its true nature
	#  decision taken to change Foreign Key from 'Profile'  to 'User' until full develop of "user registration"
	serviceUserId = models.ForeignKey(
				User ,
				on_delete=models.CASCADE, null=True)
	servicePlatform = models.ForeignKey(
				Platform ,
				on_delete=models.CASCADE ,
				verbose_name=_("Sequencing platform"),blank=True,null=True)
	serviceFileExt = models.ForeignKey(
				FileExt ,
				on_delete=models.CASCADE ,
				verbose_name=_("File extension"),blank=True,null=True)
	serviceAvailableService = TreeManyToManyField(
				AvailableService,
				verbose_name=_("AvailableServices"))

	serviceProjectNames = models.ManyToManyField(
				'iSkyLIMS_wetlab.Projects',
				verbose_name=_("User's projects"),blank=True)

	serviceSeqCenter=models.CharField(_("Sequencing center"),max_length=50,blank=False,null=True)
	serviceRequestNumber=models.CharField(max_length=80, null=True)
	serviceRequestInt=models.CharField(max_length=80, null=True)
	serviceRunSpecs=models.CharField(_("Run specifications"),max_length=10,blank=True,null=True)
	serviceFile=models.FileField(_("Service description file"),upload_to=service_files_upload, null=True,blank=True)
	serviceStatus=models.CharField(_("Service status"),max_length=15,choices=STATUS_CHOICES)
	serviceNotes=models.TextField(_("Service Notes"),max_length=2048,null=True, blank=True)
	serviceCreatedOnDate= models.DateField(auto_now_add=True,null=True)

	serviceOnApprovedDate = models.DateField(auto_now_add=False, null=True,blank=True)
	serviceOnRejectedDate = models.DateField(auto_now_add=False, null=True,blank=True)

	serviceOnDeliveredDate = models.DateField(auto_now_add=False, null=True, blank=True)



	def __str__ (self):
		return '%s' %(self.serviceRequestNumber)

	def get_service_information (self):
		platform = str(self.servicePlatform)

		return '%s;%s;%s;%s'  %(self.serviceRequestNumber ,self.serviceRunSpecs, self.serviceSeqCenter, platform)

	def get_service_id (self):
		return '%s' %self.pk

	def get_service_dates (self):
		service_dates =[]
		service_dates.append(self.serviceCreatedOnDate.strftime("%d %B, %Y"))
		if self.serviceOnApprovedDate is None:
			if self.serviceStatus == 'rejected':
				service_dates.append('--')
			else:
				service_dates.append('Approved Date not set')
		else:
			service_dates.append(self.serviceOnApprovedDate.strftime("%d %B, %Y"))
		if self.serviceOnRejectedDate is None:
			if self.serviceStatus != 'recorded':
				service_dates.append('--')
			else:
				service_dates.append('Rejected Date not set')
		else:
			service_dates.append(self.serviceOnRejectedDate.strftime("%d %B, %Y"))

		return service_dates

	def get_stats_information (self):

		stats_information =[]
		stats_information.append(self.id)
		stats_information.append(self.serviceRequestNumber)
		stats_information.append(self.serviceStatus)

		stats_information.append(self.serviceCreatedOnDate.strftime("%d %B, %Y"))
		if self.serviceOnApprovedDate is None:
			if self.serviceOnRejectedDate is None:
				stats_information.append('--')
			else:
				stats_information.append(self.serviceOnRejectedDate.strftime("%d %B, %Y"))
		else:
			stats_information.append(self.serviceOnApprovedDate.strftime("%d %B, %Y"))
		if self.serviceOnDeliveredDate is None:
			stats_information.append('--')
		else:
			stats_information.append(self.serviceOnDeliveredDate.strftime("%d %B, %Y"))

		return stats_information

	def get_service_creation_time (self):
		return self.serviceCreatedOnDate.strftime("%d %B, %Y")

	def get_service_file(self):
		if self.serviceFile != None :
			return '%s' %(self.serviceFile)
		return None
	def get_service_request_number(self):
		return '%s' %(self.serviceRequestNumber)

	def get_service_requested_user(self):
		return '%s' %(self.serviceUserId.username)

	def get_service_state(self):
		return '%s' %(self.serviceStatus)

	def get_service_user_notes(self):
		return '%s' %(self.serviceNotes)

	def get_time_to_delivery (self):
		if self.serviceOnDeliveredDate == self.serviceCreatedOnDate :
			return 1
		else:
			number_days, time = str(self.serviceOnDeliveredDate - self.serviceCreatedOnDate).split(',')
			number, string_value = number_days.split(' ')
		return number

	def get_username(self):
		return '%s' %(self.serviceUserId.username)

	def get_user_email(self):
		return '%s' %(self.serviceUserId.email)

	def get_child_services (self):
		children_services = []
		all_services = self.serviceAvailableService.all()
		for service in all_services :
			if not service.get_children().exists():
				children_services.append([service.pk, service.get_service_description()])
		return children_services

	def update_approved_date(self, date):
		self.serviceOnApprovedDate = date
		self.save()

	def update_service_status(self, status):
		self.serviceStatus = status
		self.save()

	def update_service_approved_date(self, date):
		self.serviceOnApprovedDate = date
		self.save()

	def update_service_delivered_date(self, date):
		self.serviceOnDeliveredDate = date
		self.save()

	def update_service_rejected_date(self, date):
		self.serviceOnRejectedDate = date
		self.save()

	objects = ServiceManager()

'''
class RequestedProjectInServicesManager(models.Manager):
	def create_request_project_service(self, data):
		new_project_request =self.create( projectService = data['projectService'], externalProjectKey = data['externalProjectKey'],
					externalProjectName = data['externalProjectName'])
		return new_project_request

class RequestedProjectInServices (models.Model):
	projectService = models.ForeignKey(
					Service,
					on_delete = models.CASCADE)
	externalProjectKey = models.CharField(max_length = 5, null = True, blank = True)
	externalProjectName = models.CharField(max_length = 70, null = True, blank = True)
	generated_at = models.DateField(auto_now_add = True)

	def __str__ (self):
		return '%s' %(self.externalProjectName)

	def get_requested_project_name (self):
		return '%s' %(self.externalProjectName)

	def get_requested_external_project_id (self):
		return '%s' %(self.externalProjectKey)

	def get_requested_project_id (self):
		return '%s' %(self.pk)

	objects = RequestedProjectInServicesManager()

'''

class RequestedSamplesInServicesManager (models.Manager):
	def create_request_sample (self, data):
		new_req_sample_service = self.create( samplesInService= data['samplesInService'], externalRunName = data['run_name'],
					externalRunNameKey = data['run_id'], externalProjectName = data['project_name'],  externalProjectKey = data['project_id'],
					externalSampleName = data['sample_name'],  externalSampleKey = data['sample_id'], sample = data['sample'])
		return new_req_sample_service


class RequestedSamplesInServices (models.Model):
	samplesInService = models.ForeignKey(
					Service,
					on_delete = models.CASCADE)
	sample = models.ForeignKey(
					Samples,
					null = True, blank = True, on_delete = models.CASCADE)
	# project = models.ForeignKey(
	# 				RequestedProjectInServices,
	# 				null = True, blank = True, on_delete = models.CASCADE)
	# run = models.ForeignKey(
	# 				RequestedProjectInServices,
	# 				null = True, blank = True, on_delete = models.CASCADE)
	externalSampleKey = models.CharField(max_length = 5, null = True, blank = True)
	externalSampleName = models.CharField(max_length = 50, null = True, blank = True)
	externalSamplePath =  models.CharField(max_length = 250, null = True, blank = True)
	externalRunNameKey = models.CharField(max_length = 5, null = True, blank = True)
	externalRunName = models.CharField(max_length = 50, null = True, blank = True)
	externalProjectKey = models.CharField(max_length = 5, null = True, blank = True)
	externalProjectName = models.CharField(max_length = 50, null = True, blank = True)
	generated_at = models.DateField(auto_now_add = True)

	def __str__ (self):
		return '%s' %(self.externalSampleName)

	def get_external_sample_name  (self):
		return '%s' %(self.externalSampleName)

	def get_external_sample_id(self):
		return '%s' %(self.externalSampleKey)

	objects = RequestedSamplesInServicesManager()


class ResolutionManager(models.Manager):
	def create_resolution (self, resolution_data):
		today = datetime.date.today()
		resolutionAsignedUser = User.objects.get(pk__exact = resolution_data['resolutionAsignedUser'])
		resolutionServiceID = Service.objects.get(pk__exact = resolution_data['service_id'])
		state = ResolutionStates.objects.get(resolutionStateName__exact = 'Recorded')
		new_resolution = self.create(resolutionServiceID = resolutionServiceID, resolutionAsignedUser  = resolutionAsignedUser,
					resolutionNumber = resolution_data['resolutionNumber'],  resolutionEstimatedDate= resolution_data['resolutionEstimatedDate'],
					resolutionOnQueuedDate =  datetime.date.today(), resolutionNotes = resolution_data['resolutionNotes'],
					resolutionFullNumber = resolution_data['resolutionFullNumber'], resolutionState = state)
		return new_resolution


class Resolution(models.Model):
	resolutionServiceID =  models.ForeignKey(
				Service ,
				on_delete=models.CASCADE)
	resolutionAsignedUser = models.ForeignKey(
				User,
				related_name='groups+',
				on_delete=models.CASCADE, null=True,blank=True )
	resolutionState = models.ForeignKey(
				ResolutionStates,
				on_delete=models.CASCADE, null=True,blank=True )


	servicePipelines = models.ManyToManyField(Pipelines, blank = True)

	availableServices = models.ManyToManyField(AvailableService, blank = True)
	resolutionNumber=models.CharField(_("Resolutions name"),max_length=255,null=True)
	resolutionEstimatedDate=models.DateField(_(" Estimated resolution date"), null = True,blank=False)
	resolutionDate=models.DateField(_("Resolution date"),auto_now_add=True,blank=True)
	resolutionOnQueuedDate = models.DateField(auto_now_add=False, null=True,blank=True)
	resolutionOnInProgressDate = models.DateField(auto_now_add=False, null=True,blank=True)
	resolutionDeliveryDate = models.DateField(auto_now_add=False, null=True,blank=True)
	resolutionNotes=models.TextField(_("Resolution notes"),max_length=1000, null=True, blank=True)
	resolutionFullNumber = models.CharField(_("Acronym Name"),max_length=255,null=True,blank=True)
	resolutionPdfFile = models.FileField(upload_to = drylab_config.RESOLUTION_FILES_DIRECTORY, null=True,blank=True)


	def __str__ (self):
		return '%s' %(self.resolutionNumber)

	def get_resolution_number(self):
		return '%s' %self.resolutionNumber

	def get_service_request_number(self):
		return '%s' %self.resolutionServiceID.get_service_request_number()

	def get_available_services(self):
		if self.availableServices.all().exists():
			avail_services = self.availableServices.all()
			service_list = []
			for avail_service in avail_services:
				service_list.append(avail_service.get_service_description())
			return service_list
		return ['None']

	def get_available_services_ids(self):
		if self.availableServices.all().exists():
			avail_services = self.availableServices.all()
			service_ids_list = []
			for avail_service in avail_services:
				service_ids_list.append(avail_service.pk)
			return service_ids_list
		return ['None']

	def get_resolution_id(self):
		return '%s' %(self.pk)

	def get_resolution_information (self):
		resolution_info =[]
		resolution_info.append(self.get_available_services())
		resolution_info.append(self.resolutionState.get_resolution_state())
		resolution_info.append(self.resolutionFullNumber)
		resolution_info.append(self.resolutionAsignedUser.username)
		if self.resolutionEstimatedDate is not None:
			resolution_info.append(self.resolutionEstimatedDate.strftime("%d %B, %Y"))
		else:
		    resolution_info.append("Not defined yet")

		if self.resolutionOnQueuedDate is not None:
		    resolution_info.append(self.resolutionOnQueuedDate.strftime("%d %B, %Y"))
		else:
		    resolution_info.append("Not defined yet")

		if self.resolutionOnInProgressDate is None:
			resolution_info.append('--')
		else:
			resolution_info.append(self.resolutionOnInProgressDate.strftime("%d %B, %Y"))

		resolution_info.append(self.resolutionNotes)
		resolution_info.append(self.resolutionPdfFile)
		return resolution_info

	def get_information_for_pending_resolutions (self):
		if self.resolutionOnQueuedDate is None:
			on_queued_date = 'Not defined'
		else:
			on_queued_date = self.resolutionOnQueuedDate.strftime("%d %B, %Y")
		if self.resolutionEstimatedDate is None:
			on_estimated_date = 'Not defined'
		else:
			on_estimated_date = self.resolutionEstimatedDate.strftime("%d %B, %Y")
		data = []
		data.append(self.resolutionServiceID.get_service_id())
		data.append(self.resolutionServiceID.get_service_request_number())
		data.append(self.resolutionNumber)
		data.append(self.resolutionFullNumber)
		data.append(self.resolutionAsignedUser.username)
		data.append(on_queued_date)
		data.append(on_estimated_date)
		return data


	def get_service_obj(self):
		return self.resolutionServiceID

	def get_resolution_state(self):
		if self.resolutionState != None:
			return '%s' %(self.resolutionState.get_resolution_state())
		else:
			return 'Not assigned'

	def get_resolution_full_number(self):
		return '%s' %(self.resolutionFullNumber)

	def get_resolution_estimated_date(self):
		if self.resolutionEstimatedDate != None:
			return '%s' %(self.resolutionEstimatedDate)
		return 'Not yet defined'

	def update_resolution_in_progress_date(self):
		today = datetime.date.today()
		self.resolutionOnInProgressDate = today
		self.resolutionState = ResolutionStates.objects.get(resolutionStateName__exact = 'In Progress')
		self.save()
		return self

	def update_resolution_in_delivered(self):
		today = datetime.date.today()
		self.resolutionDeliveryDate = today
		self.resolutionState = ResolutionStates.objects.get(resolutionStateName__exact = 'Delivery')
		self.save()
		return self

	def update_resolution_file(self, file):
		self.resolutionPdfFile = file
		self.save()
		return self

	objects = ResolutionManager()

class ResolutionParametersManager(models.Manager):
	def create_resolution_parameters(self,data):
		new_resolution_parameter = self.create(resolution = data['resolution'],
				resolutionParameter = data ['resolutionParameter'], resolutionParamValue = data['resolutionParamValue'],
				resolutionParamNotes = data['resolutionParamNotes'])
		return new_resolution_parameter

class ResolutionParameters (models.Model):
	resolution = models.ForeignKey(
				Resolution,
				on_delete = models.CASCADE)
	resolutionParameter = models.CharField(max_length = 50)
	resolutionParamValue = models.CharField(max_length = 80)
	resolutionParamNotes = models.CharField(max_length = 200, null = True, blank = True)
	generated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return '%s' %(self.resolutionParameter)

	def get_resolution_parameter_name(self):
		return '%s' %(self.resolutionParameter)

	objects = ResolutionParametersManager()


class DeliveryManager(models.Manager):
	def create_delivery (self, delivery_data):
		new_delivery = self.create( deliveryResolutionID = delivery_data['deliveryResolutionID'], deliveryNotes= delivery_data['deliveryNotes'],
				executionStartDate = delivery_data['executionStartDate'], executionEndDate = delivery_data['executionEndDate'],
				executionTime = delivery_data['executionTime'], permanentUsedSpace = delivery_data['permanentUsedSpace'],
				temporaryUsedSpace = delivery_data['temporaryUsedSpace'])
		return new_delivery

class Delivery(models.Model):
	deliveryResolutionID = models.ForeignKey(
						Resolution ,
						on_delete=models.CASCADE )
	pipelinesInDelivery = models.ManyToManyField(Pipelines, blank = True)

	deliveryDate = models.DateField(auto_now_add=True,null=True,blank=True)

	deliveryNotes = models.TextField(max_length=1000, null=True, blank =True)
	executionStartDate = models.DateField(null=True,blank=True)
	executionEndDate = models.DateField(null=True,blank=True)
	executionTime = models.CharField(max_length = 80,null=True,blank=True)
	permanentUsedSpace = models.CharField(max_length = 80, null = True, blank = True)
	temporaryUsedSpace = models.CharField(max_length = 80, null = True, blank = True)

	def __str__ (self):
		return '%s' %(self.deliveryResolutionID)

	def get_delivery_information (self):
		delivery_info = []
		delivery_info.append(self.deliveryResolutionID.resolutionNumber)
		delivery_info.append(self.deliveryDate.strftime("%d %B, %Y"))
		delivery_info.append(self.deliveryNotes)
		return delivery_info

	objects = DeliveryManager()

class RunIDFolder (models.Model):
	servicerequest = models.ForeignKey(
				Service,
				on_delete = models.CASCADE)
	run_id_Folder = models.CharField(max_length = 50)

	def __str__ (self):
		return '%s' %(self.run_id_Folder)



class ParameterPipelineManager(models.Manager):
	def create_pipeline_parameters(self, pipeline_parameters):
		new_parameter_action_pipeline = self.create(parameterPipeline = pipeline_parameters['parameterPipeline'],
					parameterName = pipeline_parameters['parameterName'], parameterValue = pipeline_parameters['parameterValue'])
		return new_parameter_action_pipeline

class ParameterPipeline (models.Model):
	parameterPipeline = models.ForeignKey(
				Pipelines,
				on_delete = models.CASCADE)
	parameterName = models.CharField(max_length = 80)
	parameterValue = models.CharField(max_length = 80)

	def __str__ (self):
		return '%s' %(self.parameterName)

	def get_pipeline_parameter_name (self):
		return '%s' %(self.parameterName)

	def get_pipeline_parameter_value (self):
		return '%s' %(self.parameterValue)

	def get_pipeline_parameters(self):
		data = []
		data.append(self.parameterName)
		data.append(self.parameterValue)
		return data

	objects = ParameterPipelineManager()

class JobStates (models.Model):
	jobStateName = models.CharField(max_length = 20)

	def __str__ (self):
		return '%s' %(self.jobStateName)

	def get_job_state (self):
		return '%s' %(self.jobStateName)


class PipelineExternalDataJobsManager(models.Manager):
	def create_pipeline_external_data_job (self, preparation_data):
		jobState = JobStates.objects.get(jobStateName__exact = 'Queued')
		new_preparation_pipeline = self.create(pipeline = preparation_data['pipeline'],
				availableService = preparation_data['availableService'], jobState =  jobState,
				pipelineName = preparation_data['pipelineName'],  pipelineVersion = preparation_data['pipelineVersion'],
				serviceRequestNumber = preparation_data ['serviceRequestNumber'], pendingToSetFolder = preparation_data['pendingToSetFolder'],
				folderData = preparation_data['folderData'] )
		return new_preparation_pipeline

class PipelineExternalDataJobs (models.Model):
	pipeline = models.ForeignKey(
				Pipelines,
				on_delete = models.CASCADE)
	availableService = models.ForeignKey(
				AvailableService,
				on_delete = models.CASCADE)
	jobState =  models.ForeignKey(
				JobStates,
				on_delete = models.CASCADE)

	pipelineName = models.CharField(max_length = 50)
	pipelineVersion = models.CharField(max_length = 10)
	serviceRequestNumber =  models.CharField(max_length = 20, null = True, blank = True)
	pendingToSetFolder = models.BooleanField(default = False)
	folderData = models.CharField(max_length = 80, null = True, blank = True)
	generated_at = models.DateTimeField(auto_now_add = True)
	lastRequestedTime = models.DateTimeField(auto_now_add = False, null = True, blank = True)

	def __str__ (self):
		return '%s_%s' %(self.pipeline, self.availableService)

	def update_state(self, state):
		self.jobState = state
		self.save()
		return self

	objects = PipelineExternalDataJobsManager()

class ExternalParameterData (models.Model):
	serviceRequest = models.ForeignKey(
					Service,
					on_delete = models.CASCADE)
	availableServiceID = models.CharField(max_length = 20)
	serviceName =  models.CharField(max_length = 50)
	parameterName = models.CharField(max_length = 50)
	parameterValue = models.CharField(max_length = 100)
	generated_at = models.DateTimeField(auto_now_add = True)

	def __str__ (self):
		return '%s' %(self.serviceRequest)

	def get_service_request(self):
		return '%s' %(self.serviceRequest)
