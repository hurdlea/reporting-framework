#  Developed by Alan Hurdle on 17/6/19, 12:05 pm.
#  Last modified 17/6/19, 9:07 am
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved

from reporting_events import *
import json
from amazon.ion import symbols as ion_symbols, simpleion, simple_types, core as ion_core
import sys
import six
from datetime import timezone


class JSONEncoderForIonTypes(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ion_core.Timestamp):
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
		if isinstance(obj, simple_types.IonPyBool):
			return 'true' if obj == 1 else 'false'
		return json.JSONEncoder.default(self, obj)


# Here we are reading back the 10n file and creating a JSON output in the same directory
def read_data(filename: str):
	catalog = ion_symbols.SymbolTableCatalog()
	symbols = ion_symbols.SymbolTable(ion_symbols.SHARED_TABLE_TYPE, table, "foxtel.engagement.format", 1)
	catalog.register(symbols)

	with open(filename, "rb") as read_file:
		data = simpleion.load(read_file, catalog, single_value=True)
		with open(filename + '.json', 'w', encoding='utf-8') as outfile:
			json.dump(data, outfile, ensure_ascii=False, indent=4, cls=JSONEncoderForIonTypes)
			print(json.dumps(data, ensure_ascii=False, indent=4, cls=JSONEncoderForIonTypes))


# MAIN program start

if len(sys.argv) > 1:
	read_data(sys.argv[1])
