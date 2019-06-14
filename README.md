# FOXTEL Reporting Toolkit
This project implements the Foxtel Amazon ION reporting format as specified in 
https://confluence.aws.foxtel.com.au/display/IQ35/04+Reporting

##Framework modules
There are three major files:
* log_manager
* analytics_symbols
* reporting_events

###log_manager
The log_manager emulates a logging system that takes structured reporting events and packages them into 
reporting bundles based on store and forward rules. The Amazon ION formatting is performed in the reporting 
bundle file creation process.

Reporting events are pushed into a queue and pulled asynchronously via a thread. The purpose of this 
implementation is to show how the session and page state can be contained entirely in this process. This 
removes that responsibility from device middleware and application layers.

###analytics_symbols
This defines the list of shared symbols that the Amazon ION client implementations use to convert between
symbol identifiers and keynames. The ordering of the symbol table array/list must match exactly between
implementations otherwise miss-labeling of values will occur. Symbol tables are versioned in the ION format
allowing receiving clients to support multiple symbol tables in a catalogue.

###reporting_events
This module implements the ION reporting format types and events allowing construction and consumption of
event data.

##Utility Scripts
There are two utility scripts that use the framework to generate and read Amazon ION files.
* test_data
* verify_ion_files

###test_data
The purpose of this script was to build example binary ION (10n) format files based around the activity 
sequences defined in the specification. The code uses the TiVo Content Discovery system to provide current
event information to the data model.

###verify_ion_data
The purpose of this script is to show how to ingest the ION binary files and populate the event data-model
defined in _reporting_events_. It is then possible to iterate through the data-model to produce other document 
formats or verify the contents of each event.

##Installation
The framework requires Python 3.7 and the following modules:
* reporting
* amazon-ion

Both of these modules support pip install.

There is an issue with the deserialization of boolean types in the amazon/ion/simpleion.py module. Replace
the _load method with the following to resolve this. Only the BOOL detection line has been added. 
```python
def _load(out, reader, end_type=IonEventType.STREAM_END, in_struct=False):

    def add(obj):
        if in_struct:
            # TODO what about duplicate field names?
            out[event.field_name.text] = obj
        else:
            out.append(obj)

    event = reader.send(NEXT_EVENT)
    while event.event_type is not end_type:
        ion_type = event.ion_type
        if event.event_type is IonEventType.CONTAINER_START:
            container = _FROM_ION_TYPE[ion_type].from_event(event)
            _load(container, reader, IonEventType.CONTAINER_END, ion_type is IonType.STRUCT)
            add(container)
        elif event.event_type is IonEventType.SCALAR:
            if event.value is None or ion_type is IonType.NULL or event.ion_type.is_container:
                scalar = IonPyNull.from_event(event)
            elif ion_type is IonType.BOOL:
                scalar = event.value
            else:
                scalar = _FROM_ION_TYPE[ion_type].from_event(event)
            add(scalar)
        event = reader.send(NEXT_EVENT)
```
 