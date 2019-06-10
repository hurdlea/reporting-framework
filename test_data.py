#  Developed by Alan Hurdle on 11/6/19, 9:52 am.
#  Last modified 11/6/19, 9:12 am
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from log_manager import LogManager
from reporting_events import *
from datetime import timedelta, timezone
import json
import requests
from amazon import ion
import six
import random
from typing import List

channels = ['F8D', 'SCD', 'NGD', 'BKH', 'SOD', 'STN', 'MO1', 'FDH', 'S3D', 'BE3', 'ARD', 'F4D', 'EPD', 'E1D', 'FS3']


class JSONEncoderForIonTypes(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ion.core.Timestamp):
			return obj.replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds")
		if isinstance(obj, six.binary_type):
			return obj.hex()
		if isinstance(obj, ion.simple_types.IonPyNull):
			return None
		if isinstance(obj, ion.simple_types.IonPyDict):
			# print(ion.simple_types.IonPyDict(obj))
			keys = OrderedDict()
			for (k, v) in obj.items():
				keys[k] = v
			return keys
		if isinstance(obj, ion.simple_types.IonPyBool):
			return 'true' if obj == 1 else 'false'
		return json.JSONEncoder.default(self, obj)


def device_context(timestamp: datetime) -> DeviceContextEvent:
	event = DeviceContextEvent(
		timestamp=timestamp,
		hw_version='110114213330000000',
		os_version='539032',
		temperature=45,
		num_resets=82,
		uptime=2566526,
		pvr_hdd_size=926,
		pvr_cust_free=27,
		pvr_pvod_free=100,
		pvr_num_recordings=241,
		display_HDMI_HCDP_conn='1.x:1.x',
		display_name='SAMSUNG',
		display_manufacturer='SAM:X',
		display_build_date='1:27',
		display_optimal_res='117:218',
		display_hdr_support='13',
		tuner_ber=0,
		tuner_cnr=408,
		tuner_signal_level=62,
		network_connectivity=1,
		rcu_version='',
		rcu_keys_pressed=bytes.fromhex('0000000000000000'),
		ui_design_version='PHOENIX3',
		epg_version='274_A_538953:v10R0815',
		epg_install_timestamp=datetime(2019,5,20,0,0,0,0),
		location_flag_set=bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
		app_flags_set=bytes.fromhex('0000000000000000000000000fac4000')
	)
	return event


@dataclass
class ProgrammeMetadata:
	content_provider: str
	program_id: str
	schedule_id: str
	start_time: datetime
	duration: timedelta
	program_title: str
	episode_title: str
	classification: str
	resolution: str

	@classmethod
	def _get_programme(cls, root: dict):
		item = root['metadata']
		schedule = random.choice(root['relevantSchedules'])
		# Fix-up missing programme event title
		if 'programEventTitle' not in item:
			item['programEventTitle'] = item['title']

		return cls(
			content_provider=schedule['channelTag'],
			program_id=item['programId'],
			schedule_id=schedule['id'],
			start_time=datetime.utcfromtimestamp(schedule['startTime']/1000),
			duration=datetime.utcfromtimestamp(schedule['endTime']/1000) - datetime.utcfromtimestamp(schedule['startTime']/1000),
			program_title=item['programEventTitle'],
			episode_title=item['episodeTitle'] if 'episodeTitle' in item else None,
			classification=schedule['classification'],
			resolution=schedule['videoQuality']
		)

	@classmethod
	def convert(cls, values: dict):
		root = values['groups'][0]['hits'][0]
		metadata = cls._get_programme(root)
		return metadata

	@classmethod
	def get_schedule(cls, channel: str, values: dict) -> list:
		events: list[ProgrammeMetadata] = []
		root = values['hits']
		for event in root:
			for schedule in event['relevantSchedules']:
				if schedule['channelTag'] == channel:
					schedules = event['relevantSchedules']
					event['relevantSchedules'] = [schedule]
					events.append(cls._get_programme(event))
					event['relevantSchedules'] = schedules
		return events

	def __repr__(self):
		return repr((self.content_provider, self.program_id, self.schedule_id, self.start_time,
						self.duration, self.program_title, self.episode_title, self.classification, self.resolution))


class Media:
	content_type: ContentTypeType
	view_status: ViewStatusType
	booking_source: BookingType
	event_source: EventSourceType
	create_timestamp: datetime
	duration: timedelta

	def __init__(self, content_type: ContentTypeType, view_status: ViewStatusType, booking_source: BookingType,
					event_source: EventSourceType, create_timestamp:datetime, duration: timedelta):
		self.content_type = content_type
		self.view_status = view_status
		self.booking_source = booking_source
		self.event_source = event_source
		self.create_timestamp = create_timestamp
		self.duration = duration


def request_channel_events(channel: str) -> List[ProgrammeMetadata]:
	business_rule = "rid=LIVE_TODAY&fxid=02f0935e4cd5920aa6c7c996a5ee53a70fd41d8cd98f00b204e9800998ecf8427e&hwid=b552ae163e9da40d7d39bfc8ac65399d"
	proxy_host = 'localhost:3128'
	host = "http://foxtel-staging-admin-0.digitalsmiths.net/sd/foxtel/"
	tap = "taps/sources/linear"
	fields = "__fl=metadata.programEventTitle,metadata.episodeTitle,relevantSchedules.videoQuality,metadata.programId,\
metadata.publishDuration,metadata.title,relevantSchedules.channelTag,relevantSchedules.startTime,\
relevantSchedules.endTime,relevantSchedules.classification,relevantSchedules.id,relevantSchedules.type"
	filter_query = "__fq=relevantSchedules.channelTag:{0}".format(channel)
	url = host + tap + '?' + business_rule + '&' + filter_query + '&' + fields + '&limit=25'
	response = requests.get(url, proxies={'http': proxy_host, 'https': proxy_host})
	# response = requests.get(url)
	return sorted(ProgrammeMetadata.get_schedule(channel, json.loads(response.text)), key=lambda prog: prog.start_time)


def request_live_event(channel: str) -> ProgrammeMetadata:
	proxy_host = 'localhost:3128'
	host = "http://foxtel-staging-admin-0.digitalsmiths.net/sd/foxtel/"
	tap = "taps/sources/linearonnow"
	fields = "__fl=metadata.programEventTitle,metadata.episodeTitle,relevantSchedules.videoQuality,metadata.programId,\
metadata.publishDuration,metadata.title,relevantSchedules.channelTag,relevantSchedules.startTime,\
relevantSchedules.endTime,relevantSchedules.classification,relevantSchedules.id,relevantSchedules.EventId"
	filter_query = "__fq=relevantSchedules.channelTag:"
	url = host + tap + '?' + filter_query + channel + '&' + fields
	response = requests.get(url, proxies={'http': proxy_host, 'https': proxy_host})
	# response = requests.get(url)
	print(response.text)
	return ProgrammeMetadata.convert(json.loads(response.text))


def get_live_event(timestamp: datetime, active_dur: int = 0) -> ProgrammeMetadata:
	event = request_live_event(random.choice(channels))
	return event


def make_live_play_event(timestamp: datetime, event: ProgrammeMetadata) -> LivePlayEvent:
	return LivePlayEvent(
		timestamp, timestamp, event.content_provider, event.program_id, event.schedule_id, event.start_time,
		event.duration.seconds, event.program_title, event.classification, event.resolution,
		ContentTypeType(ContentTypeType.TUNER_SUB), ViewStatusType(ViewStatusType.CAPTIONS), bytes(16),
		event.episode_title
	)


def make_playback_event(timestamp: datetime, viewing_start: datetime, event: ProgrammeMetadata, media: Media, offset: int, speed: int) -> PlaybackEvent:
	return PlaybackEvent(
		timestamp=timestamp,
		viewing_start=viewing_start,
		content_provider=event.content_provider,
		program_id=event.program_id,
		program_event_id=event.schedule_id,
		program_start_timestamp=event.start_time,
		program_duration=event.duration.seconds,
		program_title=event.program_title,
		program_episode_title=event.episode_title,
		program_classification=event.classification,
		program_resolution=event.resolution,
		content_type=media.content_type,
		view_status=media.view_status,
		booking_source=media.booking_source,
		event_source=media.event_source,
		record_timestamp=media.create_timestamp,
		record_duration=media.duration.seconds,
		player_offset=offset,
		player_trickmode_speed=speed
	)


def make_live_stop_event(timestamp: datetime, viewing_start: datetime, event: ProgrammeMetadata, viewed: int):
	return ViewingStopEvent(
		timestamp=timestamp,
		viewing_start=viewing_start,
		content_provider=event.content_provider,
		program_id=event.program_id,
		program_event_id=event.schedule_id,
		program_start_timestamp=event.start_time,
		program_duration=event.duration.seconds,
		program_title=event.program_title,
		program_episode_title=event.episode_title,
		program_classification=event.classification,
		program_resolution=event.resolution,
		content_type=ContentTypeType(ContentTypeType.TUNER_SUB),
		view_status=ViewStatusType(ViewStatusType.CAPTIONS),
		player_offset=(timestamp - event.start_time).seconds,
		player_viewed_duration=viewed
	)


def make_pvr_stop_event(timestamp: datetime, viewing_start: datetime, event: ProgrammeMetadata, media: Media, offset: int, viewed: int):
	return ViewingStopEvent(
		timestamp=timestamp,
		viewing_start=viewing_start,
		content_provider=event.content_provider,
		program_id=event.program_id,
		program_event_id=event.schedule_id,
		program_start_timestamp=event.start_time,
		program_duration=event.duration.seconds,
		program_title=event.program_title,
		program_episode_title=event.episode_title,
		program_classification=event.classification,
		program_resolution=event.resolution,
		content_type=ContentTypeType(ContentTypeType.TUNER_SUB),
		view_status=ViewStatusType(ViewStatusType.CAPTIONS),
		booking_source=media.booking_source,
		event_source=media.event_source,
		record_timestamp=media.create_timestamp,
		record_duration=media.duration.seconds,
		player_offset=offset,
		player_viewed_duration=viewed
	)


def find_event_on_air(timestamp: datetime, events: List[ProgrammeMetadata]):
	for event in events:
		if event.start_time <= timestamp < (event.start_time + event.duration):
			return event

	print('Whoops')
	return events[0]


def live_event_change(log: LogManager, timestamp: datetime, ch_onair: ProgrammeMetadata, ch_next: ProgrammeMetadata,
					viewing_start: datetime):
	stop = make_live_stop_event(timestamp, viewing_start, ch_onair, (timestamp - viewing_start).seconds)
	log.push_event(stop)
	play = make_live_play_event(timestamp, ch_next)
	log.push_event(play)
	return ch_next


# ============================================================================
# Activity sequences
# ============================================================================


def power_states_activity(m: LogManager):
	timestamp = datetime.utcnow()
	m.clear_state(timestamp)

	m.push_event(device_context(timestamp))
	power_on = PowerStatusEvent(timestamp, PowerStateType.POWER_ON)
	m.push_event(power_on)

	timestamp += timedelta(seconds=1)
	display_on = VideoOutputEvent(timestamp, True, '', '1.x', '1.x', '1080i', '50', '2b9c5d351a879a25b86851adc36acea6')
	m.push_event(display_on)

	timestamp += timedelta(seconds=1)
	player = PageViewEvent(timestamp, 'player')
	m.push_event(player)

	timestamp += timedelta(seconds=1)
	viewing_start = timestamp
	viewing_dur = 60
	event = get_live_event(timestamp, viewing_dur)
	view_1 = make_live_play_event(timestamp, event)
	m.push_event(view_1)

	timestamp += timedelta(seconds=viewing_dur)
	stop_1 = make_live_stop_event(timestamp, viewing_start, event, viewing_dur)
	m.push_event(stop_1)

	standby = PageViewEvent(timestamp, 'standby')
	m.push_event(standby)

	power_standby = PowerStatusEvent(timestamp, PowerStateType.STANDBY)
	m.push_event(power_standby)

	display_off = VideoOutputEvent(timestamp, False)
	m.push_event(display_off)

	timestamp += timedelta(hours=8)
	active = PowerStatusEvent(timestamp, PowerStateType.ACTIVE)
	m.push_event(active)

	timestamp += timedelta(seconds=1)
	display_on.timestamp = timestamp
	m.push_event(display_on)

	timestamp += timedelta(seconds=1)
	player.timestamp = timestamp
	m.push_event(player)


def channel_surfing(m: LogManager):
	timestamp = datetime.utcnow()
	m.clear_state(timestamp)
	m.push_event(device_context(timestamp))

	player = PageViewEvent(timestamp, 'player')
	m.push_event(player)

	viewing_start = timestamp
	f8d_events = request_channel_events('F8D')
	shc_events = request_channel_events('SHC')
	sha_events = request_channel_events('SHA')

	event = find_event_on_air(timestamp, f8d_events)
	view_1 = make_live_play_event(timestamp, event)
	m.push_event(view_1)

	timestamp = event.start_time + event.duration
	event = live_event_change(m, timestamp, event, find_event_on_air(timestamp, f8d_events), viewing_start)
	viewing_start = timestamp

	timestamp += timedelta(seconds=90)
	mini_guide = PageViewEvent(timestamp, 'miniGuide')
	m.push_event(mini_guide)

	timestamp += timedelta(seconds=5)
	event = live_event_change(m, timestamp, event, find_event_on_air(timestamp, shc_events), viewing_start)
	viewing_start = timestamp

	timestamp += timedelta(seconds=5)
	live_event_change(m, timestamp, event, find_event_on_air(timestamp, sha_events), viewing_start)

	timestamp += timedelta(seconds=5)
	player = PageViewEvent(timestamp, 'player')
	m.push_event(player)


def trickmode_viewing(m: LogManager):
	timestamp = datetime.utcnow()
	m.clear_state(timestamp)
	m.push_event(device_context(timestamp))

	player = PageViewEvent(timestamp, 'player')
	m.push_event(player)

	viewing_start = timestamp
	f8d_events = request_channel_events('F8D')

	event = find_event_on_air(timestamp, f8d_events)
	view_1 = make_live_play_event(timestamp, event)
	m.push_event(view_1)

	offset = (timestamp - event.start_time).seconds
	remaining_duration = event.duration.seconds - offset
	offset += int(remaining_duration/2)
	timestamp += timedelta(seconds=int(remaining_duration/2))
	stop = make_live_stop_event(timestamp, viewing_start, event, offset)
	m.push_event(stop)
	media = Media(
		content_type=ContentTypeType(ContentTypeType.TUNER_SUB_TRICKMODE),
		view_status=ViewStatusType(ViewStatusType.CAPTIONS),
		booking_source=None,
		event_source=None,
		create_timestamp=timestamp,
		duration=timestamp - viewing_start
	)
	playback_pause = make_playback_event(timestamp, viewing_start, event, media, offset, 0)
	m.push_event(playback_pause)

	pause_duration = timedelta(minutes=15)
	timestamp += pause_duration
	media.duration += pause_duration
	playback_play = make_playback_event(timestamp, viewing_start, event, media, offset, 1000)
	m.push_event(playback_play)

	timestamp += pause_duration
	media.duration += pause_duration
	pvr_stop = make_pvr_stop_event(timestamp, viewing_start, event, media, event.duration.seconds, (event.duration - (viewing_start - event.start_time)).seconds)
	m.push_event(pvr_stop)


def read_data(filename: str):
	catalog = ion.symbols.SymbolTableCatalog()
	symbols = ion.symbols.SymbolTable(ion.symbols.SHARED_TABLE_TYPE, table, "foxtel.engagement.format", 1)
	catalog.register(symbols)

	with open(filename, "rb") as read_file:
		data = ion.simpleion.load(read_file, catalog, single_value=True)

	print(json.dumps(data, indent=4, cls=JSONEncoderForIonTypes))


manager = LogManager(max_events=100, send_period=60, path="c:/Users/hurdlea/Temp")
# manager = LogManager(send_period=60, path="/Users/alanhurdle/tmp")
manager.set_identity(
	hw_version='17.27.0.C',
	hw_id=bytes.fromhex('2b9c5d351a879a25b86851adc36acea6'),
	hw_client_id='62081957540',
	hw_card_id='000229047600',
	ams_id=bytes.fromhex('026b45850456f79041d9fcf54b8fddf51ad41d8cd98f00b204e9800998ecf8427e'),
	ams_panel=1,
	app_version='1.16.1.9'
)

try:
	manager.start()
	power_states_activity(manager)
	manager._flush()
	channel_surfing(manager)
	manager._flush()
	trickmode_viewing(manager)
	manager.stop()

	manager.join()

	for file in manager.get_batch_filenames():
		read_data(file)

except Exception as e:
	manager.stop()
	print(e.__doc__)
	print(e.message)
