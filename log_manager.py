#  Developed by Alan Hurdle on 13/6/19, 6:21 pm.
#  Last modified 13/6/19, 2:28 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
from reporting_events import *
from datetime import datetime, timedelta
from threading import Thread
from queue import Queue, Empty
import copy
from amazon.ion import simpleion, symbols
import os.path
import analytics_symbols
import hashlib
from typing import List, Union


DOCUMENT_VERSION_VALUE = '1.0.0'
LIBRARY_NAME_VALUE = 'analytic-arris'
LIBRARY_VERSION_VALUE = '0.1.0'
GIZMO_TYPE_VALUE = 'STB'
GIZMO_NAME_VALUE = 'PACE-iQ3'


class LogManager(Thread):
	def __init__(self, send_period: int = 3600, max_events: int = 20, path: str = './'):
		self._send_period = send_period
		self._max_events = max_events
		self._path = path
		self._flush_time = datetime.utcnow() + timedelta(seconds=send_period)
		self._header = {}
		self._events: List[OrderedDict] = []
		self._batches: List[str] = []
		self._hw_client_id = None
		self._application_session: Union[datetime, None] = None
		self._usage_session: Union[datetime, None] = None
		self._page_session: Union[datetime, None] = None
		self._last_page: str = Union[str, None]
		self._device_context: Union[OrderedDict, None] = None
		self._device_context_id: Union[datetime, None] = None
		self._last_activity_state = None
		self._ion_symbols = symbols.SymbolTable(
			symbols.SHARED_TABLE_TYPE,
			analytics_symbols.table,
			"foxtel.engagement.format", 1)

		# Implement a queue that the external devices push into.
		# A single thread pulls from the queue to guarantee correct processing of the event
		# stream context.
		self._event_queue = Queue(maxsize=20)
		super().__init__()

	def clear_state(self, timestamp: datetime):
		self._application_session = timestamp
		self._usage_session = timestamp
		self._page_session = timestamp
		self._last_page = None
		self._last_activity_state = None

	def set_identity(self, hw_version: str, hw_id: bytes, app_version: str, hw_client_id: str,
						hw_card_id: str, ams_id: bytes, ams_panel: int):
		self._hw_client_id = hw_client_id
		self._header = {
			DOC_VERSION: DOCUMENT_VERSION_VALUE,
			TIMESTAMP: datetime.utcnow(),
			LIBRARY_NAME: LIBRARY_NAME_VALUE,
			LIBRARY_VERSION: LIBRARY_VERSION_VALUE,
			DEVICE_TYPE: GIZMO_TYPE_VALUE,
			DEVICE_NAME: GIZMO_NAME_VALUE,
			DEVICE_VARIANT: hw_version,
			DEVICE_HW_ID: hw_id,
			DEVICE_CDSN: hw_client_id,
			DEVICE_CA_CARD: hw_card_id,
			CUSTOMER_AMS_ID: ams_id,
			CUSTOMER_AMS_PANEL: ams_panel,
			SOFTWARE_VERSION: app_version,
			'batch': []
		}

	# Application method to push an event into the log queue
	def push_event(self, event: EventHeader):
		self._event_queue.put(event)

	# Convenience method to stop the dequeue thread
	def stop(self):
		stop = EventHeader(timestamp=datetime.utcnow())
		stop.event_id = EventHeader.STOP_EVENT
		self._event_queue.put(stop)

	# Convenience method for the testing harness to get the list of generated filenames
	def get_batch_filenames(self) -> List[str]:
		self.join()
		return self._batches

	# Convenience method for the testing harness
	def flush(self):
		self._flush()

	# Flush the stored events
	def _flush(self):
		if len(self._events) > 0:
			print("Flushing stored events")
			header = copy.deepcopy(self._header)
			batch = header['batch']

			# Prepend a device context event to every batch and fudge the values
			# so that it appears as part of this batch.
			self._device_context[TIMESTAMP] = self._events[0][TIMESTAMP]
			self._device_context[APP_SESSION_ID] = self._events[0][APP_SESSION_ID]
			self._device_context[USAGE_SESSION_ID] = self._events[0][USAGE_SESSION_ID]
			self._device_context[PAGE_SESSION_ID] = self._events[0][PAGE_SESSION_ID]
			batch.append(self._device_context)

			for event in self._events:
				event[CONTEXT_EVENT_ID] = self._device_context_id
				batch.append(event)

			# Add the end of file event and use the timestamp of the last event
			# leave the Session and context values set to null
			batch.append(EndOfFileEvent(self._events[-1][TIMESTAMP]).pack_event())

			# Build a filename according to the specification
			filename = datetime.utcnow().strftime("%Y%m%d-%H%M%S%f") + '_' + self._hw_client_id + '.10n'
			filename = os.path.join(self._path, filename)
			with open(filename, "wb") as write_file:
				simpleion.dump(header, fp=write_file, imports=[self._ion_symbols], binary=True)
				self._batches.append(filename)

			self._flush_time += timedelta(seconds=self._send_period)

			# Clear the stored events
			self._events.clear()

	def _change_page_state(self, timestamp: datetime, page: str, page_activity: str = '') -> str:
		self._page_session = timestamp
		last_page = self._last_page
		self._last_page = page
		if page_activity != self._last_activity_state:
			self._usage_session = timestamp
			self._last_activity_state = page_activity

		return last_page

	# Private method executed by the read queue thread
	def run(self):
		print('Event collection thread started')
		while True:
			try:
				event: EventHeader = self._event_queue.get(block=True, timeout=2)
			except Empty:
				# Send the events if the send criteria are met
				if len(self._events) > 0:
					print(len(self._events), self._max_events, datetime.utcnow(), self._flush_time)
					if len(self._events) >= self._max_events or datetime.utcnow() >= self._flush_time:
						self._flush()
				continue

			data: OrderedDict = event.pack_event()

			# Exit out of the thread if a stop event is received
			if data[EVENT_ID] == EventHeader.STOP_EVENT:
				if len(self._events) > 0:
					self._flush()
				print('Stopping thread')
				return

			if data[EVENT_ID] == EventHeader.PAGE_VIEW_EVENT:
				page_name = data[PAGE_NAME]
				last_page = self._change_page_state(data[TIMESTAMP], page_name, PageActivityType.get_activity(page_name))
				data[PREVIOUS_PAGE] = last_page

			elif data[EVENT_ID] in [EventHeader.POWER_STATE_EVENT, EventHeader.VIDEO_OUTPUT_EVENT]:
				self._application_session = data[TIMESTAMP]
				if data[EVENT_ID] == EventHeader.POWER_STATE_EVENT and data[DEVICE_POWER_STATUS] == PowerStateType.POWER_ON.value:
					self._usage_session = data[TIMESTAMP]
					self._page_session = data[TIMESTAMP]

			elif data[EVENT_ID] == EventHeader.APPLICATION_LAUNCH_EVENT:
				self._change_page_state(data[TIMESTAMP], 'app:' + data[APP_NAME], 'application')

			elif data[EVENT_ID] == EventHeader.DEVICE_CONTEXT_EVENT:
				data[CONTEXT_EVENT_ID] = int(data[TIMESTAMP].timestamp())
				self._device_context = data
				self._device_context_id = data[CONTEXT_EVENT_ID]

			elif PAGE_NAME in data and data[EVENT_ID] != EventHeader.PAGE_VIEW_EVENT:
				data[PAGE_NAME] = self._last_page

			data[APP_SESSION_ID] = self._application_session
			data[USAGE_SESSION_ID] = self._usage_session
			data[PAGE_SESSION_ID] = self._page_session

			if data[EVENT_ID] in [EventHeader.VIEWING_STOP_EVENT, EventHeader.PLAYBACK_EVENT, EventHeader.LIVE_PLAY_EVENT,
									EventHeader.CONTENT_SELECTOR_EVENT]:
				m = hashlib.md5()
				m.update(data[CONTENT_PROGRAM_TITLE].encode('utf-8'))
				m.update(data[APP_SESSION_ID].isoformat().encode('utf-8'))
				data[SELECTOR_TRACK_ID] = m.digest()

			# We treat the device context specially so that emulates the header functionality of DINS 121
			# The Device Context is retained until a flush and always the first event in the batch.
			if data[EVENT_ID] != EventHeader.DEVICE_CONTEXT_EVENT:
				# Send the events if the send criteria are met
				if len(self._events) > self._max_events or datetime.utcnow() >= self._flush_time:
					self._flush()
				self._events.append(data)

			self._event_queue.task_done()
