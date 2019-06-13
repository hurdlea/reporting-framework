#  Developed by Alan Hurdle on 13/6/19, 6:21 pm.
#  Last modified 13/6/19, 6:11 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from enum import Enum, IntFlag, IntEnum
from datetime import datetime
from dataclasses import dataclass, field
from collections import OrderedDict
from analytics_symbols import *
from typing import List, Union, Any
from amazon.ion import simple_types


def get_booking_type(value: Any):
	if value is None:
		return None
	else:
		return BookingType(value)


def get_event_source_type(value: Any):
	if value is None:
		return None
	else:
		return EventSourceType(value)


def conditional_fill(key: str, items: simple_types.IonPyDict):
	if key in items:
		return items[key]
	else:
		return None


class SearchTypeType(Enum):
	EPG_SEARCH = 1
	EPG_POPULAR = 2
	EPG_RECENT = 3
	VOICE_SEARCH = 4
	VOICE_COMMAND = 5


class NetworkConnectionType(IntEnum):
	NONE = 0
	ETHERNET = 1
	WIRELESS = 2


class BookingType(IntFlag):
	# Set when scheduling a future EPG event
	EPG_FUTURE = 0x01
	# Set when a scheduling came from a bookable promo
	BOOKABLE_PROMO = 0x02
	# Value not used
	UNUSED_1 = 0x04
	# Set for series and team linked schedule recordings
	LINKED_BOOKING = 0x08
	# Set when booking came from a remote booking request
	REMOTE_BOOKING = 0x10
	# Set when scheduling a Teaming link recording must also invoke
	# SERIES_LINK_AUTO to indicate a series recording
	IS_TEAM_LINK = 0x20
	# Recording of a current EPG event
	EPG_CURRENT = 0x40
	# Is the event series linked
	IS_SERIES_LINK = 0x80
	# Series linked scheduled recording
	SERIES_RECORDING = 0x89
	# Team linked scheduled recording
	TEAM_RECORDING = 0x29


class JumpType(Enum):
	BOOKMARK = 'bookmark'
	START = 'start'
	HALF = 'half'
	END = 'end'
	TIME = 'time'


class ApplicationStateType(Enum):
	START = 'start'
	END = 'end'
	LAUNCH = 'launch'
	EXIT = 'exit'
	SUSPEND = 'suspend'
	RESUME = 'resume'


class DownloadStateType(Enum):
	START = 'start'
	DOWNLOADING = 'downloading'
	DOWNLOADED = 'complete'
	PAUSED = 'pause'
	FAILED = 'failed'


class PowerStateType(Enum):
	POWER_ON = 'PowerOn'
	STANDBY = 'StandByIn'
	ACTIVE = 'StandByOut'


class RebootTypeType(Enum):
	REBOOT_OWM = 'OWM'
	REBOOT_EMM = 'EMM'
	REBOOT_USER = 'button'


class EventSourceType(IntEnum):
	BACKGROUND_REC = 0
	REVIEW_BUFFER_REC = 1


class ViewStatusType(IntFlag):
	# Has the content been watched before
	VIEWED = 0x01
	# Where viewing required a pin access parental or channel blocking
	PIN_ACCESS = 0x20
	# Player captions viewing state
	CAPTIONS = 0x80


class RecordingStatusType(IntFlag):
	WATCHED = 0x01
	PARTIAL_REC = 0x02
	SIGNAL_LOSS = 0x04
	FAILED_REC = 0x08
	CA_ERROR = 0x10
	CLASH = 0x20


class ContentTypeType(IntEnum):
	TUNER_SUB = 2
	TUNER_SUB_TRICKMODE = 3
	TUNER_SUB_RECORD = 4
	TUNER_PPV = 5
	TUNER_PPV_TRICKMODE = 6
	TUNER_PPV_RECORD = 7

	PVR_RECORD = 21
	PVR_RECORD_SUB = 22
	PVR_RECORD_PPV = 23

	ABR_GENERIC = 41
	ABR_LIVE = 42
	ABR_START_OVER = 43
	ABR_SVOD = 44
	ABR_REPG = 45
	ABR_TVOD = 46

	PDL_GENERIC = 51
	PDL_SVOD = 53
	PDL_REPG = 54
	PDL_TVOD = 55


class PageActivityType:
	activity = {
		'miniGuide': 'player',
		'player': 'player',
		'playNext': 'player',
		'standby': 'standby',
	}

	@staticmethod
	def get_activity(name: str):
		if name in PageActivityType.activity:
			return PageActivityType.activity[name]
		else:
			return 'navigation'


# Default values for the Identity Header
DOCUMENT_VERSION_VALUE = '1.0.0'
LIBRARY_NAME_VALUE = 'analytic-arris'
LIBRARY_VERSION_VALUE = '0.1.0'
GIZMO_TYPE_VALUE = 'STB'
GIZMO_NAME_VALUE = 'PACE-iQ3'


@dataclass()
class IdentityHeader:
	timestamp: datetime
	hw_version: str
	hw_id: bytes
	hw_client_id: str
	hw_card_id: str
	ams_id: bytes
	ams_panel: int
	app_version: str

	document_version: str = DOCUMENT_VERSION_VALUE
	library_name: str = LIBRARY_NAME_VALUE
	library_version: str = LIBRARY_VERSION_VALUE
	device_type: str = GIZMO_TYPE_VALUE
	device_name: str = GIZMO_NAME_VALUE

	events: List = field(init=False, default_factory=list)

	def pack_header(self) -> OrderedDict:
		header = OrderedDict()
		header[DOC_VERSION] = self.document_version
		header[TIMESTAMP] = self.timestamp
		header[LIBRARY_NAME] = self.library_version
		header[LIBRARY_VERSION] = self.library_version
		header[DEVICE_TYPE] = self.device_type
		header[DEVICE_NAME] = self.device_name
		header[DEVICE_VARIANT] = self.hw_version
		header[DEVICE_HW_ID] = self.hw_id
		header[DEVICE_CDSN] = self.hw_client_id
		header[DEVICE_CA_CARD] = self.hw_card_id
		header[CUSTOMER_AMS_ID] = self.ams_id
		header[CUSTOMER_AMS_PANEL] = self.ams_panel
		header[SOFTWARE_VERSION] = self.app_version
		header[EVENT_LIST] = List[EventHeader]

		return header

	@staticmethod
	def unpack_event(properties):
		obj = IdentityHeader(
			properties[TIMESTAMP],
			properties[DEVICE_VARIANT],
			properties[DEVICE_HW_ID],
			properties[DEVICE_CDSN],
			properties[DEVICE_CA_CARD],
			properties[CUSTOMER_AMS_ID],
			properties[CUSTOMER_AMS_PANEL],
			properties[SOFTWARE_VERSION],
			document_version=properties[DOC_VERSION],
			library_name=properties[LIBRARY_NAME],
			library_version=properties[LIBRARY_VERSION],
			device_type=properties[DEVICE_TYPE],
			device_name=properties[DEVICE_NAME]
		)

		return obj, properties[EVENT_LIST]


class EventFactory:

	def __init__(self):
		# Here we are building a look-up table for the factory method.
		# The look-up binds the event id to the instantiating Class where
		# each class is a sub-class of EventHeader. Each class has a method
		# that exposes the event id and this is used to create the linkage.
		self.classes: List[Union[None, EventHeader]] = [None] * 128
		# Get all of the sub-classes
		event_classes: List[Any] = EventHeader.__subclasses__()
		for cls in event_classes:
			# make the association of the defining class to the event identifier value
			event: EventHeader = cls
			event_id: int = event.get_event_id()
			self.classes[event_id] = event

	# Factory method to instantiate a class from the received ION event properties
	def factory(self, event_type: int, properties):
		for item in properties:
				if isinstance(properties[item], simple_types.IonPyNull):
					properties[item] = None

		return self.classes[event_type].unpack_event(properties)


@dataclass()
class EventHeader:
	timestamp: datetime
	event_id: int = field(init=False, default=None)
	app_session: datetime = field(init=False, default=None)
	usage_session: datetime = field(init=False, default=None)
	page_session: datetime = field(init=False, default=None)
	device_context_id: datetime = field(init=False, default=None)

	# Event type codes

	# Device and format specific events
	END_OF_FILE_EVENT = 1
	ERROR_MESSAGE_EVENT = 2
	POWER_STATE_EVENT = 3
	REBOOT_REQUEST_EVENT = 4
	CODE_DOWNLOAD_EVENT = 5

	# Viewing Events
	LIVE_PLAY_EVENT = 16
	RECORDING_EVENT = 17
	PLAYBACK_EVENT = 18
	VIEWING_STOP_EVENT = 19
	VIDEO_OUTPUT_EVENT = 20

	# Navigation Events
	PAGE_VIEW_EVENT = 32
	COLLECTION_SELECTOR_EVENT = 33
	CONTENT_SELECTOR_EVENT = 34
	SEARCH_QUERY_EVENT = 35
	APPLICATION_LAUNCH_EVENT = 36

	# Content interactions
	BOOK_ACTION = 48
	WATCH_ACTION = 49
	DOWNLOAD_ACTION = 50
	DELETE_ACTION = 51
	KEEP_ACTION = 52
	UPGRADE_ACTION = 53
	RENT_ACTION = 54
	NEXT_EPISODE_ACTION = 55
	JUMP_ACTION = 56

	# Context and Configuration events
	DEVICE_CONTEXT_EVENT = 64
	FEATURE_USAGE_CONTEXT_EVENT = 65

	# This is an event to stop the log manager thread pulling events from the log queue and is not a production
	# event.
	STOP_EVENT = 0xFFFF

	@staticmethod
	def get_event_id() -> int:
		raise NotImplemented()

	def pack_event(self) -> OrderedDict:
		event = OrderedDict()
		if self.event_id is None:
			raise AttributeError()

		event[EVENT_ID] = self.event_id
		event[TIMESTAMP] = self.timestamp
		event[APP_SESSION_ID] = self.app_session
		event[USAGE_SESSION_ID] = self.usage_session
		event[PAGE_SESSION_ID] = self.page_session
		event[CONTEXT_EVENT_ID] = self.device_context_id
		return event

	def _set_header_from_event(self, properties):
		self.event_id = properties[EVENT_ID]
		self.app_session = properties[APP_SESSION_ID]
		self.usage_session = properties[USAGE_SESSION_ID]
		self.page_session = properties[PAGE_SESSION_ID]
		self.device_context_id = properties[CONTEXT_EVENT_ID]


@dataclass()
class ErrorMessageEvent(EventHeader):
	page: str
	error_num_message: str
	technical_message: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.ERROR_MESSAGE_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[ERROR_FNUM_MESSAGE] = self.error_num_message
		properties[ERROR_TECHNICAL_MESSAGE] = self.technical_message

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = ErrorMessageEvent(
			properties[TIMESTAMP],
			properties[PAGE_NAME],
			properties[ERROR_FNUM_MESSAGE],
			technical_message=properties[ERROR_TECHNICAL_MESSAGE]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class EndOfFileEvent(EventHeader):

	@staticmethod
	def get_event_id():
		return EventHeader.END_OF_FILE_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		return properties

	@staticmethod
	def unpack_event(properties):
		obj = EndOfFileEvent(
			properties[TIMESTAMP]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class PowerStatusEvent(EventHeader):
	power_status: PowerStateType

	@staticmethod
	def get_event_id():
		return EventHeader.POWER_STATE_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[DEVICE_POWER_STATUS] = self.power_status.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = PowerStatusEvent(properties[TIMESTAMP], properties[DEVICE_POWER_STATUS])
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class RebootEvent(EventHeader):
	reboot_type: RebootTypeType

	@staticmethod
	def get_event_id():
		return EventHeader.REBOOT_REQUEST_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[REBOOT_TYPE] = self.reboot_type.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = RebootEvent(
			properties[TIMESTAMP],
			properties[REBOOT_TYPE]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class CodeDownloadEvent(EventHeader):
	software_version: str
	epg_version: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.CODE_DOWNLOAD_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[SOFTWARE_VERSION] = self.software_version
		if self.epg_version is not None:
			properties[EPG_VERSION] = self.epg_version

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = CodeDownloadEvent(
			properties[TIMESTAMP],
			properties[SOFTWARE_VERSION],
			conditional_fill(EPG_VERSION, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class ApplicationLaunchEvent(EventHeader):
	content_provider: str
	app_name: str
	app_provider: str
	app_state: ApplicationStateType

	@staticmethod
	def get_event_id():
		return EventHeader.APPLICATION_LAUNCH_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[APP_NAME] = self.app_name
		properties[APP_PROVIDER] = self.app_provider
		properties[APP_STATE] = self.app_state

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = ApplicationLaunchEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[APP_NAME],
			properties[APP_PROVIDER],
			properties[APP_STATE]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class LivePlayEvent(EventHeader):
	viewing_start: datetime
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	view_status: ViewStatusType

	selector_track_id: bytes = None
	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.LIVE_PLAY_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PLAYER_VIEWING_START_TIMESTAMP] = self.viewing_start
		properties[SELECTOR_TRACK_ID] = self.selector_track_id
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[PLAYER_VIEW_STATUS] = self.view_status.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = LivePlayEvent(
			properties[TIMESTAMP],
			properties[PLAYER_VIEWING_START_TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			ViewStatusType(properties[PLAYER_VIEW_STATUS]),
			selector_track_id=properties[SELECTOR_TRACK_ID],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class RecordingEvent(EventHeader):
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	booking_source: BookingType
	event_source: EventSourceType
	record_timestamp: datetime
	record_duration: int
	record_status: RecordingStatusType
	record_expiry: datetime

	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.RECORDING_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_DURATION] = self.record_duration
		properties[MEDIA_REC_STATUS] = self.record_status.value
		properties[MEDIA_EXPIRY_TIMESTAMP] = self.record_expiry

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = RecordingEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			BookingType(properties[MEDIA_BOOKING_SOURCE]),
			EventSourceType(properties[MEDIA_EVENT_SOURCE]),
			properties[MEDIA_REC_START_TIMESTAMP],
			properties[MEDIA_DURATION],
			RecordingStatusType(properties[MEDIA_REC_STATUS]),
			properties[MEDIA_EXPIRY_TIMESTAMP],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class PlaybackEvent(EventHeader):
	viewing_start: datetime
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	view_status: ViewStatusType
	booking_source: BookingType
	event_source: EventSourceType
	record_timestamp: datetime
	record_duration: int
	player_offset: int
	player_trickmode_speed: int

	program_episode_title: str = None
	selector_track_id: bytes = None

	@staticmethod
	def get_event_id():
		return EventHeader.PLAYBACK_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PLAYER_VIEWING_START_TIMESTAMP] = self.viewing_start
		properties[SELECTOR_TRACK_ID] = self.selector_track_id
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value if self.content_type is not None else None
		properties[PLAYER_VIEW_STATUS] = self.view_status.value if self.view_status is not None else None
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value if self.booking_source is not None else None
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value if self.event_source is not None else None
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_DURATION] = self.record_duration
		properties[PLAYER_MEDIA_OFFSET] = self.player_offset
		properties[PLAYER_TRICKMODE_SPEED] = self.player_trickmode_speed

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = PlaybackEvent(
			properties[TIMESTAMP],
			properties[PLAYER_VIEWING_START_TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			ViewStatusType(properties[PLAYER_VIEW_STATUS]),
			get_booking_type(properties[MEDIA_BOOKING_SOURCE]),
			get_event_source_type(properties[MEDIA_EVENT_SOURCE]),
			properties[MEDIA_REC_START_TIMESTAMP],
			properties[MEDIA_DURATION],
			properties[PLAYER_MEDIA_OFFSET],
			properties[PLAYER_TRICKMODE_SPEED],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties),
			selector_track_id=properties[SELECTOR_TRACK_ID],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class ViewingStopEvent(EventHeader):
	viewing_start: datetime
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	view_status: ViewStatusType
	player_offset: int
	player_viewed_duration: int

	booking_source: BookingType = None
	event_source: EventSourceType = None
	record_timestamp: datetime = None
	record_duration: int = None
	program_episode_title: str = None
	selector_track_id: bytes = None
	qos_avg_bitrate_kbps: int = None
	qos_startup_ms: int = None
	qos_buffing_duration_ms: int = None
	qos_buffering_count: int = None
	qos_abr_shifts: int = None

	@staticmethod
	def get_event_id():
		return EventHeader.VIEWING_STOP_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PLAYER_VIEWING_START_TIMESTAMP] = self.viewing_start
		properties[SELECTOR_TRACK_ID] = self.selector_track_id
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[PLAYER_VIEW_STATUS] = self.view_status.value
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value if self.booking_source is not None else None
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value if self.event_source is not None else None
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_DURATION] = self.record_duration
		properties[PLAYER_MEDIA_OFFSET] = self.player_offset
		properties[PLAYER_VIEWED_DURATION] = self.player_viewed_duration

		if self.qos_avg_bitrate_kbps is not None:
			properties[PLAYER_QOS_AVG_BITRATE_KBPS] = self.qos_avg_bitrate_kbps
		if self.qos_startup_ms is not None:
			properties[PLAYER_QOS_STARTUP_MS] = self.qos_startup_ms
		if self.qos_buffing_duration_ms is not None:
			properties[PLAYER_QOS_BUFFERING_MS] = self.qos_buffing_duration_ms
		if self.qos_buffering_count is not None:
			properties[PLAYER_QOS_BUFFERING_COUNT] = self.qos_buffering_count
		if self.qos_abr_shifts is not None:
			properties[PLAYER_QOS_ABR_SHIFTS] = self.qos_abr_shifts

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = ViewingStopEvent(
			properties[TIMESTAMP],
			properties[PLAYER_VIEWING_START_TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			ViewStatusType(properties[PLAYER_VIEW_STATUS]),
			properties[PLAYER_MEDIA_OFFSET],
			properties[PLAYER_VIEWED_DURATION],
			booking_source=get_booking_type(properties[MEDIA_BOOKING_SOURCE]),
			event_source=get_event_source_type(properties[MEDIA_EVENT_SOURCE]),
			record_timestamp=properties[MEDIA_REC_START_TIMESTAMP],
			record_duration=properties[MEDIA_DURATION],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties),
			selector_track_id=properties[SELECTOR_TRACK_ID],
			qos_avg_bitrate_kbps=conditional_fill(PLAYER_QOS_AVG_BITRATE_KBPS, properties),
			qos_startup_ms=conditional_fill(PLAYER_QOS_STARTUP_MS, properties),
			qos_buffing_duration_ms=conditional_fill(PLAYER_QOS_BUFFERING_MS, properties),
			qos_buffering_count=conditional_fill(PLAYER_QOS_BUFFERING_COUNT, properties),
			qos_abr_shifts=conditional_fill(PLAYER_QOS_ABR_SHIFTS, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class VideoOutputEvent(EventHeader):
	display_on: bool
	detected_HDR: str = None
	negotiated_HDMI: str = None
	negotiated_HDCP: str = None
	negotiated_resolution: str = None
	negotiated_framerate: str = None
	edid_hash: str = None
	edid_block: bytes = None

	@staticmethod
	def get_event_id():
		return EventHeader.VIDEO_OUTPUT_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[DISPLAY_ON] = self.display_on
		if self.display_on:
			properties[DISPLAY_DETECTED_HDR] = self.detected_HDR
			properties[DISPLAY_NEG_HDMI] = self.negotiated_HDMI
			properties[DISPLAY_NEG_HDCP] = self.negotiated_HDCP
			properties[DISPLAY_NEG_RESOLUTION] = self.negotiated_resolution
			properties[DISPLAY_NEG_FRAMERATE] = self.negotiated_framerate
			properties[DISPLAY_EDID_SIG] = self.edid_hash
			if self.edid_block is not None:
				properties[DISPLAY_EDID_BLOCK] = self.edid_block

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = VideoOutputEvent(
			properties[TIMESTAMP],
			properties[DISPLAY_ON],
			detected_HDR=conditional_fill(DISPLAY_DETECTED_HDR, properties),
			negotiated_HDMI=conditional_fill(DISPLAY_NEG_HDMI, properties),
			negotiated_HDCP=conditional_fill(DISPLAY_NEG_HDCP, properties),
			negotiated_resolution=conditional_fill(DISPLAY_NEG_RESOLUTION, properties),
			negotiated_framerate=conditional_fill(DISPLAY_NEG_FRAMERATE, properties),
			edid_hash=conditional_fill(DISPLAY_EDID_SIG, properties),
			edid_block=conditional_fill(DISPLAY_EDID_BLOCK, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class PageViewEvent(EventHeader):
	name: str
	previous: str = None
	filter: str = None
	sort: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.PAGE_VIEW_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = self.name
		properties[PREVIOUS_PAGE] = self.previous
		if self.filter is not None:
			properties[PAGE_FILTER] = self.filter
		if self.sort is not None:
			properties[PAGE_SORT] = self.sort

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = PageViewEvent(
			properties[TIMESTAMP],
			properties[PAGE_NAME],
			previous=properties[PREVIOUS_PAGE],
			filter=conditional_fill(PAGE_FILTER, properties),
			sort=conditional_fill(PAGE_SORT, properties)
		)
		obj._set_header_from_event(properties)
		return obj

	def page_activity(self) -> str:
		return PageActivityType.get_activity(self.name)


@dataclass()
class SelectorContentEvent(EventHeader):
	type: str
	title: str
	row: str
	column: str
	program_id: str
	content_provider: str
	program_title: str
	program_brand: str
	tile_locked: bool
	selector_track_id: str
	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.CONTENT_SELECTOR_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[SELECTOR_TYPE] = self.type
		properties[SELECTOR_TITLE] = self.title
		properties[SELECTOR_ROW] = self.row
		properties[SELECTOR_COLUMN] = self.column
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_BRAND] = self.program_brand
		properties[TILE_LOCKED] = self.tile_locked
		properties[SELECTOR_TRACK_ID] = self.selector_track_id

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = SelectorContentEvent(
			properties[TIMESTAMP],
			properties[SELECTOR_TYPE],
			properties[SELECTOR_TITLE],
			properties[SELECTOR_ROW],
			properties[SELECTOR_COLUMN],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_BRAND],
			properties[TILE_LOCKED],
			properties[SELECTOR_TRACK_ID],
			page=properties[PAGE_NAME]

		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class SelectorCollectionEvent(EventHeader):
	type: str
	title: str
	row: str
	column: str
	collection_title: str
	collection_source: str
	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.COLLECTION_SELECTOR_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[SELECTOR_TYPE] = self.type
		properties[SELECTOR_TITLE] = self.title
		properties[SELECTOR_ROW] = self.row
		properties[SELECTOR_COLUMN] = self.column
		properties[COLLECTION_TITLE] = self.collection_title
		properties[COLLECTION_SOURCE] = self.collection_source

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = SelectorCollectionEvent(
			properties[TIMESTAMP],
			properties[SELECTOR_TYPE],
			properties[SELECTOR_TITLE],
			properties[SELECTOR_ROW],
			properties[SELECTOR_COLUMN],
			properties[COLLECTION_TITLE],
			properties[COLLECTION_SOURCE],
			page=properties[PAGE_NAME],

		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class BookContentActionEvent(EventHeader):
	user_initiated: bool
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	booking_source: BookingType
	event_source: EventSourceType
	record_timestamp: datetime
	record_extend_duration: int

	page: str = None
	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.BOOK_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[EVENT_USER_INITIATED] = self.user_initiated
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_start_timestamp
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_EXTEND_REC_DURATION] = self.record_extend_duration

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = BookContentActionEvent(
			properties[TIMESTAMP],
			properties[EVENT_USER_INITIATED],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			BookingType(properties[MEDIA_BOOKING_SOURCE]),
			EventSourceType(properties[MEDIA_EVENT_SOURCE]),
			properties[MEDIA_REC_START_TIMESTAMP],
			properties[MEDIA_EXTEND_REC_DURATION],
			page=properties[PAGE_NAME],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class WatchContentActionEvent(EventHeader):
	program_id: str
	program_title: str
	content_type: ContentTypeType
	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.WATCH_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_TYPE] = self.content_type.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = WatchContentActionEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_PROGRAM_TITLE],
			ContentTypeType(properties[CONTENT_TYPE]),
			page=properties[PAGE_NAME],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class DownloadContentActionEvent(EventHeader):
	user_initiated: bool
	content_provider: str
	program_id: str
	program_event_id: str
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	download_state: DownloadStateType
	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.DOWNLOAD_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[EVENT_USER_INITIATED] = self.user_initiated
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[MEDIA_DOWNLOAD_STATE] = self.download_state.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = DownloadContentActionEvent(
			properties[TIMESTAMP],
			properties[EVENT_USER_INITIATED],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			DownloadStateType(properties[MEDIA_DOWNLOAD_STATE]),
			page=properties[PAGE_NAME]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class DeleteContentActionEvent(EventHeader):
	user_initiated: bool
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	booking_source: BookingType
	event_source: EventSourceType
	record_timestamp: datetime
	record_duration: int
	record_status: RecordingStatusType
	record_expiry: datetime
	max_viewed_offset: int

	page: str = None
	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.DELETE_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[EVENT_USER_INITIATED] = self.user_initiated
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_DURATION] = self.record_duration
		properties[MEDIA_REC_STATUS] = self.record_status.value
		properties[MEDIA_EXPIRY_TIMESTAMP] = self.record_expiry
		properties[MEDIA_MAX_VIEWED_OFFSET] = self.max_viewed_offset

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = DeleteContentActionEvent(
			properties[TIMESTAMP],
			properties[EVENT_USER_INITIATED],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			get_booking_type(properties[MEDIA_BOOKING_SOURCE]),
			get_event_source_type(properties[MEDIA_EVENT_SOURCE]),
			properties[MEDIA_REC_START_TIMESTAMP],
			properties[MEDIA_DURATION],
			RecordingStatusType(properties[MEDIA_REC_STATUS]),
			properties[MEDIA_EXPIRY_TIMESTAMP],
			properties[MEDIA_MAX_VIEWED_OFFSET],
			page=properties[PAGE_NAME],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class KeepContentActionEvent(EventHeader):
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_duration: int
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	booking_source: BookingType

	page: str = None
	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.KEEP_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_DURATION] = self.program_duration
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = KeepContentActionEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_DURATION],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			get_booking_type(properties[MEDIA_BOOKING_SOURCE]),
			page=properties[PAGE_NAME],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class UpgradeContentActionEvent(EventHeader):
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_title: str
	program_resolution: str
	content_type: ContentTypeType

	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.UPGRADE_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = UpgradeContentActionEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			page=properties[PAGE_NAME],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class RentContentActionEvent(EventHeader):
	program_id: str
	program_title: str
	program_resolution: str
	program_price: int
	content_type: ContentTypeType

	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.RENT_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[CONTENT_PRICE] = self.program_price

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = RentContentActionEvent(
			properties[TIMESTAMP],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			properties[CONTENT_PRICE],
			page=properties[PAGE_NAME],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class NextEpContentActionEvent(EventHeader):
	user_initiated: bool
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType

	page: str = None
	program_episode_title: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.NEXT_EPISODE_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[EVENT_USER_INITIATED] = self.user_initiated
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		if self.program_episode_title is not None:
			properties[CONTENT_EPISODE_TITLE] = self.program_episode_title
		properties[CONTENT_CLASSIFICATION] = self.program_classification
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = NextEpContentActionEvent(
			properties[TIMESTAMP],
			properties[EVENT_USER_INITIATED],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_SCHEDULE_ID],
			properties[CONTENT_START_TIMESTAMP],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_CLASSIFICATION],
			properties[CONTENT_RESOLUTION],
			ContentTypeType(properties[CONTENT_TYPE]),
			page=properties[PAGE_NAME],
			program_episode_title=conditional_fill(CONTENT_EPISODE_TITLE, properties)
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class JumpContentActionEvent(EventHeader):
	jump_type: JumpType

	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.JUMP_ACTION

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[PLAYER_JUMP_TO] = self.jump_type.value

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = JumpContentActionEvent(
			properties[TIMESTAMP],
			properties[PLAYER_JUMP_TO],
			page=properties[PAGE_NAME],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class SearchQueryEvent(EventHeader):
	initiator_type: SearchTypeType
	query_term: str
	result_score: str

	page: str = None

	@staticmethod
	def get_event_id():
		return EventHeader.SEARCH_QUERY_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[SEARCH_INITIATOR_SOURCE] = self.initiator_type.value
		properties[SEARCH_TERM] = self.query_term
		properties[SEARCH_SCORE] = self.result_score

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = SearchQueryEvent(
			properties[TIMESTAMP],
			properties[SEARCH_INITIATOR_SOURCE],
			properties[SEARCH_TERM],
			properties[SEARCH_SCORE],
			page=properties[PAGE_NAME],
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class DeviceContextEvent(EventHeader):
	hw_version: str
	os_version: str
	temperature: int
	num_resets: int
	uptime: int
	pvr_hdd_size: int
	pvr_cust_free: int
	pvr_pvod_free: int
	pvr_num_recordings: int
	display_HDMI_HCDP_conn: str
	display_name: str
	display_manufacturer: str
	display_build_date: str
	display_optimal_res: str
	display_hdr_support: str
	tuner_ber: int
	tuner_cnr: int
	tuner_signal_level: int
	network_connectivity: int
	rcu_version: str
	rcu_keys_pressed: bytes
	ui_design_version: str
	epg_version: str
	epg_install_timestamp: datetime
	location_flag_set: bytes
	app_flags_set: bytes

	@staticmethod
	def get_event_id():
		return EventHeader.DEVICE_CONTEXT_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[HARDWARE_VERSION] = self.hw_version
		properties[OS_VERSION] = self.os_version
		properties[DEVICE_TEMP] = self.temperature
		properties[DEVICE_RESETS] = self.num_resets
		properties[DEVICE_UPTIME] = self.uptime
		properties[PVR_HDD_SIZE] = self.pvr_hdd_size
		properties[PVR_CUST_FREE_PERC] = self.pvr_cust_free
		properties[PVR_PVOD_FREE_PERC] = self.pvr_pvod_free
		properties[PVR_NUM_RECORDINGS] = self.pvr_num_recordings
		properties[DISPLAY_CONNECTION] = self.display_HDMI_HCDP_conn
		properties[DISPLAY_NAME] = self.display_name
		properties[DISPLAY_MANUFACTURER] = self.display_manufacturer
		properties[DISPLAY_BUILD_DATE] = self.display_build_date
		properties[DISPLAY_OPTIMAL_RES] = self.display_optimal_res
		properties[DISPLAY_HDR_SUPPORT] = self.display_hdr_support
		properties[TUNER_BER] = self.tuner_ber
		properties[TUNER_CNR] = self.tuner_cnr
		properties[TUNER_SIGNAL_LEVEL] = self.tuner_signal_level
		properties[NETWORK_TYPE] = self.network_connectivity
		properties[RCU_VERSION] = self.rcu_version
		properties[RCU_KEYS_PRESSED] = self.rcu_keys_pressed
		properties[UI_VERSION] = self.ui_design_version
		properties[EPG_VERSION] = self.epg_version
		properties[EPG_VERSION_INSTALL_DATE] = self.epg_install_timestamp
		properties[LOCATION_FLAG_SET] = self.location_flag_set
		properties[APPLICATION_FLAG_SET] = self.app_flags_set

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = DeviceContextEvent(
			properties[TIMESTAMP],
			properties[HARDWARE_VERSION],
			properties[OS_VERSION],
			properties[DEVICE_TEMP],
			properties[DEVICE_RESETS],
			properties[DEVICE_UPTIME],
			properties[PVR_HDD_SIZE],
			properties[PVR_CUST_FREE_PERC],
			properties[PVR_PVOD_FREE_PERC],
			properties[PVR_NUM_RECORDINGS],
			properties[DISPLAY_CONNECTION],
			properties[DISPLAY_NAME],
			properties[DISPLAY_MANUFACTURER],
			properties[DISPLAY_BUILD_DATE],
			properties[DISPLAY_OPTIMAL_RES],
			properties[DISPLAY_HDR_SUPPORT],
			properties[TUNER_BER],
			properties[TUNER_CNR],
			properties[TUNER_SIGNAL_LEVEL],
			properties[NETWORK_TYPE],
			properties[RCU_VERSION],
			properties[RCU_KEYS_PRESSED],
			properties[UI_VERSION],
			properties[EPG_VERSION],
			properties[EPG_VERSION_INSTALL_DATE],
			properties[LOCATION_FLAG_SET],
			properties[APPLICATION_FLAG_SET]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class ApplicationConfigEvent(EventHeader):
	pin_classification: str
	pin_info: str
	pin_no_classification: bool
	channel_blocking_on: bool
	pin_on_purchase: bool
	pin_protect_keep: bool
	pin_ip_video: bool
	pin_app_launch: bool
	num_schedule_reminders: int
	num_schedule_recordings: int
	num_team_links: int
	favourites_setup: bool
	dtt_setup: bool
	energy_saving_on: bool
	spdif_audio_mode: str
	hdmi_audio_mode: str
	download_hd: bool
	stream_from_store: bool

	@staticmethod
	def get_event_id():
		return EventHeader.FEATURE_USAGE_CONTEXT_EVENT

	def __post_init__(self):
		self.event_id = self.get_event_id()

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[CONF_PIN_CLASSIFICATION] = self.pin_classification
		properties[CONF_PIN_INFO] = self.pin_info
		properties[CONF_PIN_NC] = self.pin_no_classification
		properties[CONF_CHANNEL_BLOCKING_ON] = self.channel_blocking_on
		properties[CONF_PIN_ON_PURCHASE] = self.pin_on_purchase
		properties[CONF_PIN_PROTECT_KEEP] = self.pin_protect_keep
		properties[CONF_PIN_IP_VIDEO] = self.pin_ip_video
		properties[CONF_PIN_APP_LAUNCH] = self.pin_app_launch
		properties[CONF_NUM_SCHED_REMINDERS] = self.num_schedule_reminders
		properties[CONF_NUM_SCHED_RECORDINGS] = self.num_schedule_recordings
		properties[CONF_NUM_TEAM_LINKS] = self.num_team_links
		properties[CONF_FAVOURITES_SETUP] = self.favourites_setup
		properties[CONF_DTT_SETUP] = self.dtt_setup
		properties[CONF_ENERGY_SAVING_ON] = self.energy_saving_on
		properties[CONF_SPDIF_AUDIO_MODE] = self.spdif_audio_mode
		properties[CONF_HDMI_AUDIO_MODE] = self.hdmi_audio_mode
		properties[CONF_DOWNLOAD_HD] = self.download_hd
		properties[CONF_STREAM_FROM_STORE] = self.stream_from_store

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = ApplicationConfigEvent(
			properties[TIMESTAMP],
			properties[CONF_PIN_CLASSIFICATION],
			properties[CONF_PIN_INFO],
			properties[CONF_PIN_NC],
			properties[CONF_CHANNEL_BLOCKING_ON],
			properties[CONF_PIN_ON_PURCHASE],
			properties[CONF_PIN_PROTECT_KEEP],
			properties[CONF_PIN_IP_VIDEO],
			properties[CONF_PIN_APP_LAUNCH],
			properties[CONF_NUM_SCHED_REMINDERS],
			properties[CONF_NUM_SCHED_RECORDINGS],
			properties[CONF_NUM_TEAM_LINKS],
			properties[CONF_FAVOURITES_SETUP],
			properties[CONF_DTT_SETUP],
			properties[CONF_ENERGY_SAVING_ON],
			properties[CONF_SPDIF_AUDIO_MODE],
			properties[CONF_HDMI_AUDIO_MODE],
			properties[CONF_DOWNLOAD_HD],
			properties[CONF_STREAM_FROM_STORE]
		)
		obj._set_header_from_event(properties)
		return obj
