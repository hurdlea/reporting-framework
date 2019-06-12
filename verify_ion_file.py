#  Developed by Alan Hurdle on 12/6/19, 9:33 pm.
#  Last modified 12/6/19, 8:50 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from reporting_events import *
from amazon.ion import symbols as ion_symbols, simpleion, simple_types, core
from datetime import timedelta, timezone
import six
import sys

# from collections import OrderedDict
# from dataclasses import dataclass
# from typing import List, Union


def get_py_type(obj):
	if isinstance(obj, core.Timestamp):
		return obj.replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds")
	if isinstance(obj, six.binary_type):
		return obj.hex()
	if isinstance(obj, simple_types.IonPyNull):
		return None
	if isinstance(obj, simple_types.IonPyDict):
		# print(ion.simple_types.IonPyDict(obj))
		keys = OrderedDict()
		for (k, v) in obj.items():
			keys[k] = v
		return keys
	return obj


def decode_ion_event(event: EventFactory, data):
	event = event.factory(data[EVENT_ID], data)
	print(event)
	return event


def decode_ion_data(data):
	factory = EventFactory()
	for item in data:
		# Here is the handler for each event
		if isinstance(item, simple_types.IonPyDict):
			decode_ion_event(factory, item)
			continue

		value = data[item]

		# Here is the batch list handler
		if isinstance(value, list):
			#print(value)
			decode_ion_data(value)
			continue

		# Here are the individual values
		#print(item, get_py_type(value))


# Here we are reading back the 10n file and creating a JSON output in the same directory
def read_data(filename: str):
	catalog = ion_symbols.SymbolTableCatalog()
	symbols = ion_symbols.SymbolTable(ion_symbols.SHARED_TABLE_TYPE, table, "foxtel.engagement.format", 1)
	catalog.register(symbols)

	with open(filename, "rb") as read_file:
		data = simpleion.load(read_file, catalog, single_value=True)
		decode_ion_data(data)


if len(sys.argv) > 1:
	start = datetime.utcnow()
	print('Start:', datetime.utcnow())
	read_data(sys.argv[1])
	end = datetime.utcnow()
	print('End:', end)
	print('Time:', end - start)