#  Developed by Alan Hurdle on 13/6/19, 6:21 pm.
#  Last modified 13/6/19, 6:18 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from reporting_events import *
from amazon.ion import symbols as ion_symbols, simpleion, simple_types, core
from datetime import timedelta, timezone
import six
import sys

# from collections import OrderedDict
# from dataclasses import dataclass
# from typing import List, Union


def decode_ion_event(event: EventFactory, data):
	event = event.factory(data[EVENT_ID], data)
	return event


def decode_ion_data(data):
	factory = EventFactory()
	header, events = IdentityHeader.unpack_event(data)
	for item in events:
		# Here is the handler for each event
		if isinstance(item, simple_types.IonPyDict):
			header.events.append(decode_ion_event(factory, item))
			continue

		raise RuntimeError("ION format is incorrect")

	return header


# Here we are reading back the 10n file and creating a JSON output in the same directory
def read_data(filename: str):
	catalog = ion_symbols.SymbolTableCatalog()
	symbols = ion_symbols.SymbolTable(ion_symbols.SHARED_TABLE_TYPE, table, "foxtel.engagement.format", 1)
	catalog.register(symbols)

	with open(filename, "rb") as read_file:
		data = simpleion.load(read_file, catalog, single_value=True)
		event_model = decode_ion_data(data)

	print(event_model)
	return event_model


if len(sys.argv) > 1:
	start = datetime.utcnow()
	read_data(sys.argv[1])
	end = datetime.utcnow()
	print('Read and ingest time:', end - start)