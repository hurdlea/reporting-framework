#  Developed by Alan Hurdle on 12/6/19, 9:33 pm.
#  Last modified 12/6/19, 9:29 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from enum import Enum, IntFlag, IntEnum
from datetime import datetime
from dataclasses import dataclass, field
from collections import OrderedDict
from analytics_symbols import *
from typing import List, Dict
from amazon.ion import simple_types


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


class ContentActionType(Enum):
	BOOK_ACTION = 'book'
	WATCH_ACTION = 'watch'
	DOWNLOAD_ACTION = 'download'
	DELETE_ACTION = 'delete'
	KEEP_ACTION = 'keep'
	UPGRADE_ACTION = 'upgrade'
	RENT_ACTION = 'rent'
	NEXT_EPISODE_ACTION = 'nextEp'
	JUMP_ACTION = 'jump'


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


property_list = {
	EVENT_ID: 'event_id', TIMESTAMP: 'timestamp', APP_SESSION_ID: 'app_session',
	USAGE_SESSION_ID: 'usage_session', PAGE_SESSION_ID: 'page_session',
	CONTEXT_EVENT_ID: 'device_context_id'
}

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

	def pack_header(self) -> OrderedDict:
		header = OrderedDict()
		header[DOC_VERSION] = DOCUMENT_VERSION_VALUE
		header[TIMESTAMP] = self.timestamp
		header[LIBRARY_NAME] = LIBRARY_NAME_VALUE
		header[LIBRARY_VERSION] = LIBRARY_VERSION_VALUE
		header[DEVICE_TYPE] = GIZMO_TYPE_VALUE
		header[DEVICE_NAME] = GIZMO_NAME_VALUE
		header[DEVICE_VARIANT] = self.hw_version
		header[DEVICE_HW_ID] = self.hw_id
		header[DEVICE_CDSN] = self.hw_client_id
		header[DEVICE_CA_CARD] = self.hw_card_id
		header[CUSTOMER_AMS_ID] = self.ams_id
		header[CUSTOMER_AMS_PANEL] = self.ams_panel
		header[SOFTWARE_VERSION] = self.app_version
		header[EVENT_LIST] = List[EventHeader]

		return header

	def unpack_header(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


class EventFactory:
	classes = {}
	content_classes = {}
	selector_classes = {}

	def __init__(self):
		self.classes[EventHeader.ERROR_MESSAGE_EVENT] = ErrorMessageEvent
		self.classes[EventHeader.END_OF_FILE_EVENT] = EndOfFileEvent
		self.classes[EventHeader.POWER_STATE_EVENT] = PowerStatusEvent
		self.classes[EventHeader.REBOOT_REQUEST_EVENT] = RebootEvent
		self.classes[EventHeader.CODE_DOWNLOAD_EVENT] = CodeDownloadEvent
		self.classes[EventHeader.APPLICATION_LAUNCH_EVENT] = ApplicationConfigEvent
		self.classes[EventHeader.LIVE_PLAY_EVENT] = LivePlayEvent
		self.classes[EventHeader.RECORDING_EVENT] = RecordingEvent
		self.classes[EventHeader.PLAYBACK_EVENT] = PlaybackEvent
		self.classes[EventHeader.VIEWING_STOP_EVENT] = ViewingStopEvent
		self.classes[EventHeader.VIDEO_OUTPUT_EVENT] = VideoOutputEvent
		self.classes[EventHeader.PAGE_VIEW_EVENT] = PageViewEvent
		self.classes[EventHeader.SELECTOR_EVENT] = SelectorFactory
		self.classes[EventHeader.CONTENT_ACTION_EVENT] = ContentActionFactory
		self.classes[EventHeader.SEARCH_QUERY_EVENT] = SearchQueryEvent
		self.classes[EventHeader.DEVICE_CONTEXT_EVENT] = DeviceContextEvent
		self.classes[EventHeader.FEATURE_USAGE_CONTEXT_EVENT] = ApplicationConfigEvent

		self.content_classes[ContentActionType.BOOK_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.WATCH_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.DOWNLOAD_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.DELETE_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.KEEP_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.UPGRADE_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.RENT_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.NEXT_EPISODE_ACTION] = BookContentActionEvent
		self.content_classes[ContentActionType.JUMP_ACTION] = BookContentActionEvent

	def factory(self, event_type: int, properties):
		print(self.classes[event_type])
		if event_type == EventHeader.SELECTOR_EVENT:
			if CONTENT_PROGRAM_ID in properties:
				return SelectorContentEvent.unpack_event(properties)
			elif COLLECTION_SOURCE in properties:
				return SelectorCollectionEvent.unpack_event(properties)
			else:
				raise RuntimeError('Missing required key in Selector Event' + str(properties))
		elif event_type == EventHeader.CONTENT_ACTION_EVENT:
			action = properties[EVENT_ACTION]
			return self.content_classes[action].unpack_event(properties)
		else:
			return self.classes[event_type].unpack_event(properties)


class SelectorFactory:
	@staticmethod
	def unpack_event(event):
		pass


class ContentActionFactory:
	@staticmethod
	def unpack_event(properties):
		action = properties[EVENT_ACTION]
		if action == ContentActionType.BOOK_ACTION: return BookContentActionEvent
		pass


@dataclass()
class EventHeader:
	timestamp: datetime
	event_id: int = field(init=False, default=None)
	app_session: datetime = field(init=False, default=None)
	usage_session: datetime = field(init=False, default=None)
	page_session: datetime = field(init=False, default=None)
	device_context_id: datetime = field(init=False, default=None)

	# Event type codes
	ERROR_MESSAGE_EVENT = 1
	END_OF_FILE_EVENT = 4
	POWER_STATE_EVENT = 8
	REBOOT_REQUEST_EVENT = 9
	CODE_DOWNLOAD_EVENT = 10
	APPLICATION_LAUNCH_EVENT = 12
	LIVE_PLAY_EVENT = 13
	RECORDING_EVENT = 17
	PLAYBACK_EVENT = 18
	VIEWING_STOP_EVENT = 21
	VIDEO_OUTPUT_EVENT = 24
	PAGE_VIEW_EVENT = 32
	SELECTOR_EVENT = 33
	CONTENT_ACTION_EVENT = 34
	SEARCH_QUERY_EVENT = 35
	DEVICE_CONTEXT_EVENT = 64
	FEATURE_USAGE_CONTEXT_EVENT = 65
	# This is an event to stop the log manager thread pulling events from the log queue and is not a production
	# event.
	STOP_EVENT = 0xFFFF

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

	def __post_init__(self):
		self.event_id = EventHeader.ERROR_MESSAGE_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.END_OF_FILE_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.POWER_STATE_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.REBOOT_REQUEST_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.CODE_DOWNLOAD_EVENT

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
			properties[EPG_VERSION] if EPG_VERSION in properties else None
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class ApplicationLaunchEvent(EventHeader):
	content_provider: str
	app_name: str
	app_provider: str
	app_state: ApplicationStateType

	def __post_init__(self):
		self.event_id = EventHeader.APPLICATION_LAUNCH_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.LIVE_PLAY_EVENT

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
		)
		if CONTENT_EPISODE_TITLE in properties:
			obj.program_episode_title = properties[CONTENT_EPISODE_TITLE]
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

	def __post_init__(self):
		self.event_id = EventHeader.RECORDING_EVENT

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
			program_episode_title=properties[CONTENT_EPISODE_TITLE] if CONTENT_EPISODE_TITLE in properties else None,
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

	def __post_init__(self):
		self.event_id = EventHeader.PLAYBACK_EVENT

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
			BookingType(properties[MEDIA_BOOKING_SOURCE]),
			EventSourceType(properties[MEDIA_EVENT_SOURCE]),
			properties[MEDIA_REC_START_TIMESTAMP],
			properties[MEDIA_DURATION],
			properties[PLAYER_MEDIA_OFFSET],
			properties[PLAYER_TRICKMODE_SPEED],
			program_episode_title=properties[CONTENT_EPISODE_TITLE] if CONTENT_EPISODE_TITLE in properties else None,
			selector_track_id = properties[SELECTOR_TRACK_ID],
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

	def __post_init__(self):
		self.event_id = EventHeader.VIEWING_STOP_EVENT

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
			booking_source=BookingType(properties[MEDIA_BOOKING_SOURCE]) if not isinstance(properties[MEDIA_BOOKING_SOURCE], simple_types.IonPyNull) else None,
			event_source=EventSourceType(properties[MEDIA_EVENT_SOURCE]) if not isinstance(properties[MEDIA_EVENT_SOURCE], simple_types.IonPyNull) else None,
			record_timestamp=properties[MEDIA_REC_START_TIMESTAMP],
			record_duration=properties[MEDIA_DURATION],
			program_episode_title=properties[CONTENT_EPISODE_TITLE] if CONTENT_EPISODE_TITLE in properties else None,
			selector_track_id = properties[SELECTOR_TRACK_ID],
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

	def __post_init__(self):
		self.event_id = EventHeader.VIDEO_OUTPUT_EVENT

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
			detected_HDR=properties[DISPLAY_DETECTED_HDR] if DISPLAY_DETECTED_HDR in properties else None,
			negotiated_HDMI=properties[DISPLAY_NEG_HDMI] if DISPLAY_NEG_HDMI in properties else None,
			negotiated_HDCP=properties[DISPLAY_NEG_HDCP] if DISPLAY_NEG_HDCP in properties else None,
			negotiated_resolution=properties[DISPLAY_NEG_RESOLUTION] if DISPLAY_NEG_RESOLUTION in properties else None,
			negotiated_framerate=properties[DISPLAY_NEG_FRAMERATE] if DISPLAY_NEG_FRAMERATE in properties else None,
			edid_hash=properties[DISPLAY_EDID_SIG] if DISPLAY_EDID_SIG in properties else None,
			edid_block=properties[DISPLAY_EDID_BLOCK] if DISPLAY_EDID_BLOCK in properties else None
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class PageViewEvent(EventHeader):
	name: str
	previous: str = None
	filter: str = None
	sort: str = None

	def __post_init__(self):
		self.event_id = EventHeader.PAGE_VIEW_EVENT

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
			filter=properties[PAGE_FILTER] if PAGE_FILTER in properties else None,
			sort=properties[PAGE_SORT] if PAGE_SORT in properties else None,
		)
		obj._set_header_from_event(properties)
		return obj

	def page_activity(self) -> str:
		return PageActivityType.get_activity(self.name)


@dataclass()
class SelectorContentEvent(EventHeader):
	page: str
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

	def __post_init__(self):
		self.event_id = EventHeader.SELECTOR_EVENT

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
			properties[PAGE_NAME],
			properties[SELECTOR_TYPE],
			properties[SELECTOR_TITLE],
			properties[SELECTOR_ROW],
			properties[SELECTOR_COLUMN],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[CONTENT_PROGRAM_TITLE],
			properties[CONTENT_BRAND],
			properties[TILE_LOCKED],
			properties[SELECTOR_TRACK_ID]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class SelectorCollectionEvent(EventHeader):
	page: str
	type: str
	title: str
	row: str
	column: str
	collection_title: str
	collection_source: str

	def __post_init__(self):
		self.event_id = EventHeader.SELECTOR_EVENT

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
			properties[PAGE_NAME],
			properties[SELECTOR_TYPE],
			properties[SELECTOR_TITLE],
			properties[SELECTOR_ROW],
			properties[SELECTOR_COLUMN],
			properties[COLLECTION_TITLE],
			properties[COLLECTION_SOURCE]
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
	program_title: str
	program_classification: str
	program_resolution: str
	content_type: ContentTypeType
	booking_source: BookingType
	event_source: EventSourceType
	record_timestamp: datetime
	record_extend_duration: int

	program_episode_title: str = None

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.BOOK_ACTION.value
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
		properties[MEDIA_BOOKING_SOURCE] = self.booking_source.value
		properties[MEDIA_EVENT_SOURCE] = self.event_source.value
		properties[MEDIA_REC_START_TIMESTAMP] = self.record_timestamp
		properties[MEDIA_EXTEND_REC_DURATION] = self.record_extend_duration

		return properties

	@staticmethod
	def unpack_event(properties):
		obj = SelectorCollectionEvent(
			properties[TIMESTAMP],
			properties[EVENT_USER_INITIATED],
			properties[CONTENT_PROVIDER],
			properties[CONTENT_PROGRAM_ID],
			properties[SELECTOR_ROW],
			properties[SELECTOR_COLUMN],
			properties[COLLECTION_TITLE],
			properties[COLLECTION_SOURCE]
		)
		obj._set_header_from_event(properties)
		return obj


@dataclass()
class WatchContentActionEvent(EventHeader):
	program_id: str
	program_title: str
	content_type: ContentTypeType

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.WATCH_ACTION.value
		properties[PAGE_NAME] = None
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_TYPE] = self.content_type.value

		return properties

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


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

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.DOWNLOAD_ACTION.value
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

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


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

	program_episode_title: str = None

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.DELETE_ACTION.value
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

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


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

	program_episode_title: str = None

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.KEEP_ACTION.value
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

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


@dataclass()
class UpgradeContentActionEvent(EventHeader):
	content_provider: str
	program_id: str
	program_event_id: str
	program_start_timestamp: datetime
	program_title: str
	program_resolution: str
	content_type: ContentTypeType

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.UPGRADE_ACTION.value
		properties[PAGE_NAME] = None
		properties[CONTENT_PROVIDER] = self.content_provider
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_SCHEDULE_ID] = self.program_event_id
		properties[CONTENT_START_TIMESTAMP] = self.program_start_timestamp
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value

		return properties

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


@dataclass()
class RentContentActionEvent(EventHeader):
	program_id: str
	program_title: str
	program_resolution: str
	program_price: int
	content_type: ContentTypeType

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.RENT_ACTION.value
		properties[PAGE_NAME] = None
		properties[CONTENT_PROGRAM_ID] = self.program_id
		properties[CONTENT_PROGRAM_TITLE] = self.program_title
		properties[CONTENT_RESOLUTION] = self.program_resolution
		properties[CONTENT_TYPE] = self.content_type.value
		properties[CONTENT_PRICE] = self.program_price

		return properties

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


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

	program_episode_title: str = None

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.NEXT_EPISODE_ACTION.value
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

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


@dataclass()
class JumpContentActionEvent(EventHeader):
	jump_type: JumpType

	def __post_init__(self):
		self.event_id = EventHeader.CONTENT_ACTION_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[EVENT_ACTION] = ContentActionType.JUMP_ACTION.value
		properties[PAGE_NAME] = None
		properties[PLAYER_JUMP_TO] = self.jump_type.value

		return properties

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


@dataclass()
class SearchQueryEvent(EventHeader):
	initiator_type: SearchTypeType
	query_term: str
	result_score: str

	def __post_init__(self):
		self.event_id = EventHeader.SEARCH_QUERY_EVENT

	def pack_event(self) -> OrderedDict:
		properties = super().pack_event()
		properties[PAGE_NAME] = None
		properties[SEARCH_INITIATOR_SOURCE] = self.initiator_type.value
		properties[SEARCH_TERM] = self.query_term
		properties[SEARCH_SCORE] = self.result_score

		return properties

	def unpack_event(self, properties: OrderedDict):
		raise NotImplementedError("Not implemented yet!")


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

	def __post_init__(self):
		self.event_id = EventHeader.DEVICE_CONTEXT_EVENT

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

	def __post_init__(self):
		self.event_id = EventHeader.FEATURE_USAGE_CONTEXT_EVENT

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
		obj = DeviceContextEvent(
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
