#  Developed by Alan Hurdle on 14/6/19, 5:42 pm.
#  Last modified 14/6/19, 5:35 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from reporting_events import *
from amazon.ion import symbols as ion_symbols, simpleion, simple_types
import sys


def decode_ion_event(event: EventFactory, data):
	event = event.factory(data[EVENT_ID], data)
	return event


def decode_ion_data(data):
	factory = EventFactory()
	header, events = IdentityHeader.unpack_header(data)
	for item in events:
		# Here is the handler for each event
		if isinstance(item, simple_types.IonPyDict):
			header.events.append(decode_ion_event(factory, item))
			continue

		raise RuntimeError("ION format is incorrect")

	return header


# Here we are reading the 10n file and then parsing the resulting data model
def read_data(filename: str):
	# Build the shared symbol table from the analytics symbols
	# Don't know how much time this takes but I presume that this only needs to be done once
	catalog = ion_symbols.SymbolTableCatalog()
	symbols = ion_symbols.SymbolTable(ion_symbols.SHARED_TABLE_TYPE, table, "foxtel.engagement.format", 1)
	catalog.register(symbols)

	# Pull in the file and transition from ION format to the internal data-model
	# from here we can either generate XML, JSON or send events to Segment.
	# Rather than performing class inspection it maybe better to add handlers to
	# the reporting event model.
	with open(filename, "rb") as read_file:
		data = simpleion.load(read_file, catalog, single_value=True)
		event_model = decode_ion_data(data)

	events = event_model.events
	for event in events:
		if isinstance(event, ViewingStopEvent):
			pass

		if isinstance(event, RecordingEvent):
			pass

		if isinstance(event, BookContentActionEvent):
			pass

		if isinstance(event, DeviceContextEvent):
			pass

	return event_model


if len(sys.argv) > 1:
	start = datetime.utcnow()
	data_model = read_data(sys.argv[1])
	end = datetime.utcnow()
	print(data_model)
	print('Read and ingest time:', end - start)
