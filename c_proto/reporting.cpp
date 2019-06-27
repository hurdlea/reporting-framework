/*
#  Developed by Alan Hurdle on 24/6/19, 12:05 pm.
#  Last modified 27/6/19, 9:07 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
*/
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sys/timeb.h>
#include <assert.h>
#include "ion_binary_writer.h"
#include "reporting_symbols.h"
#include "reporting.h"

using namespace std;

#define DOCUMENT_VERSION_VALUE "1.0.0"
#define LIBRARY_NAME_VALUE "analytic-arris"
#define LIBRARY_VERSION_VALUE "0.1.0"
#define GIZMO_TYPE_VALUE "STB"
#define GIZMO_NAME_VALUE "DGS7000NF15"

// As in the Python example the device context and session values are calculated on insertion.
ReportingEvent::ReportingEvent(int event_id, timeb * timestamp) : event_id(event_id), timestamp(timestamp) {
        device_context_id = 0;
        application_session = timestamp;
        usage_session = timestamp;
        page_session = timestamp;
}


void ReportingEvent::ionize_context(IonBinaryCollection * parent) {
    parent->append(new IonBinaryInt(EVENT_ID, event_id));
    parent->append(new IonBinaryTimestamp(TIMESTAMP, timestamp));
    parent->append(new IonBinaryTimestamp(APP_SESSION_ID, application_session));
    parent->append(new IonBinaryTimestamp(USAGE_SESSION_ID, usage_session));
    parent->append(new IonBinaryTimestamp(PAGE_SESSION_ID, page_session));
    parent->append(new IonBinaryInt(CONTEXT_EVENT_ID, device_context_id));
}

const string PowerStateEvent::states[3] = {"PowerOn", "StandByIn", "StandByOut"};

PowerStateEvent::PowerStateEvent(timeb * timestamp, PowerStateType status, bool user_initiated) : 
    ReportingEvent(POWER_STATE_EVENT, timestamp), status(status), user_initiated(user_initiated)
{
}

IonBinaryCollection * PowerStateEvent::ionize_event() {
    // Power event has 8 fields including the base event header
    IonBinaryCollection * event = new IonBinaryCollection(ion_struct, 8);
    // Stuff the event header values 
    ionize_context(event);
    event->append(new IonBinaryString(DEVICE_POWER_STATUS, states[static_cast<int>(status)]));
    event->append(new IonBinaryBoolean(EVENT_USER_INITIATED, user_initiated));

    return event;
}

ReportingHeader::ReportingHeader(timeb * timestamp, int sequence, string device_variant, const char * device_hw_id, const char * software_version, 
            const char * device_cdsn, const char * device_ca_card, const char * ams_id, const char * ams_panel)
{
    this->timestamp = timestamp;
    this->sequence = sequence;
    this->device_variant = device_variant;
    this->device_hw_id = device_hw_id;
    this->software_version = software_version;
    this->device_cdsn = device_cdsn;
    this->device_ca_card = device_ca_card;
    this->ams_id = ams_id;
    this->ams_panel = ams_panel;

    this->document_version = DOCUMENT_VERSION_VALUE;
    this->library_name = LIBRARY_NAME_VALUE;
    this->library_version = LIBRARY_VERSION_VALUE;
    this->device_type = GIZMO_TYPE_VALUE;
    this->device_name = GIZMO_NAME_VALUE;

    // Store the raw reporting events
    this->batch = new vector<ReportingEvent *>();
}

// It would probably be best to include the page, session and context state management
// within this method as shown in the Python example. 
void ReportingHeader::addEvent(ReportingEvent * event) {
    batch->push_back(event);
}

IonBinaryCollection * ReportingHeader::ionize() {
    // Reporting Header has 15 fields
    IonBinaryCollection * header_struct = new IonBinaryCollection(ion_struct, 15);

    header_struct->append(new IonBinaryString(DOC_VERSION, document_version));
    header_struct->append(new IonBinaryTimestamp(TIMESTAMP, timestamp));
    header_struct->append(new IonBinaryInt(SEQUENCE_ID, sequence));
    header_struct->append(new IonBinaryString(LIBRARY_NAME, library_name));
    header_struct->append(new IonBinaryString(LIBRARY_VERSION, library_version));
    header_struct->append(new IonBinaryString(DEVICE_TYPE, device_type));
    header_struct->append(new IonBinaryString(DEVICE_NAME, device_name));
    header_struct->append(new IonBinaryString(DEVICE_VARIANT, device_variant));
    header_struct->append(new IonBinaryString(DEVICE_HW_ID, device_hw_id));
    header_struct->append(new IonBinaryString(SOFTWARE_VERSION, software_version));
    header_struct->append(new IonBinaryString(DEVICE_CDSN, device_cdsn));
    header_struct->append(new IonBinaryString(DEVICE_CA_CARD, device_ca_card));
    header_struct->append(new IonBinaryString(CUSTOMER_AMS_ID, ams_id));
    header_struct->append(new IonBinaryString(CUSTOMER_AMS_PANEL, ams_panel));
    IonBinaryCollection * event_list = new IonBinaryCollection(ion_list, batch->size(), EVENT_LIST);
    header_struct->append(event_list);

    // Ion format all of the events that are atached to this reporting bundle.
    // Each event is appended to the header container to allow for KLV calculations.
    for (vector<ReportingEvent *>::iterator it = this->batch->begin() ; it != this->batch->end(); ++it) {
        event_list->append((*it)->ionize_event());
    }

    return header_struct;
}

IonWrapper::IonWrapper(string symbol_schema, int schema_version): symbol_schema(symbol_schema), schema_version(schema_version) {
}

void IonWrapper::set_header(IonBinaryCollection * reporting_header) {
    this->header = reporting_header;
}

int IonWrapper::serialize() {
    int size = 0;
    uint8_t * offset;
    uint8_t binary_version_marker[] = { 0xe0, 0x01, 0x00, 0xea };

    // Build the ion binary annotation sequence that describes the shared
    // symbol table name and version.
    IonBinaryCollection * annotation = new IonBinaryCollection(ion_annotation, 2);
    annotation->append(new IonBinaryInt(SYSTEM_ION));
    IonBinaryCollection * system_symbol_table = new IonBinaryCollection(ion_struct, 1, SYSTEM_ION_SYMBOL_TABLE);
    annotation->append(system_symbol_table);
    IonBinaryCollection * system_imports = new IonBinaryCollection(ion_list, 2, SYSTEM_ION_IMPORTS);
    system_symbol_table->append(system_imports);
    IonBinaryCollection * import = new IonBinaryCollection(ion_struct, 3);
    system_imports->append(import);
    import->append(new IonBinaryString(SYSTEM_ION_NAME, symbol_schema));
    import->append(new IonBinaryInt(SYSTEM_ION_VERSION, schema_version));
    import->append(new IonBinaryInt(SYSTEM_ION_MAX_ID, MAX_IMPORT_SYMBOLS));
    // There are no local symbols so this is an empty table
    IonBinaryCollection * symbols = new IonBinaryCollection(ion_list, 0, SYSTEM_ION_SYMBOLS);
    system_symbol_table->append(symbols);

    // Get the size of the required buffer
    size += sizeof(binary_version_marker);
    // Ion Binary format annotation section
    size += annotation->get_size();
    // Reporting event section
    size += this->header->get_size();

    // Create the ion serialization buffer
    ion_buffer = new uint8_t[size];
    offset = ion_buffer;

    // Construct the ion payload
    memcpy(offset, binary_version_marker, sizeof(binary_version_marker));
    offset += sizeof(binary_version_marker);
    offset = annotation->pack(offset);
    header->pack(offset);

    // Return the size of the buffer
    return size;
}

int main() {
    ofstream ion_file;
    const char * filename = "./test.10n";
    timeb * timestamp;
    ReportingHeader * reporting_header;
    ReportingEvent * reporting_event;
    IonWrapper * ion_wrapper;

    timestamp = new timeb;
    ftime(timestamp);

    ion_file.open(filename, ios::binary | ios::out | ios::trunc);
    if (ion_file.is_open()) {
        ion_wrapper = new IonWrapper(REPORTING_SYMBOLS_SCHEMA, REPORTING_SYMBOLS_VERSION);

        reporting_header = new ReportingHeader(
            timestamp,
            1,
            "17.27.0.C",
            "2b9c5d351a879a25b86851adc36acea6",
            "1.16.1.9",
            "62081957540",
            "000229047600",
            "026b45850456f79041d9fcf54b8fddf51ad41d8cd98f00b204e9800998ecf8427e",
            "1"
        );
        // Here we add the events that need to be stored before sending
        reporting_header->addEvent(new PowerStateEvent(timestamp, StandByIn, false));
        reporting_header->addEvent(new PowerStateEvent(timestamp, PowerOn, true));
        // This is the packing for sending phase where the reporting obects are turned
        // into ion format structures with the corect ion binary format wrapping.
        ion_wrapper->set_header(reporting_header->ionize());

/*
        IonBinaryCollection * c = new IonBinaryCollection(ion_list,1);
        for (int i = -999; i < 1000; i++) {
            c->append(new IonBinaryInt(0,i));
        }
        ion_wrapper->set_header(c);
*/
        int size = ion_wrapper->serialize();

        ion_file.write((char *)ion_wrapper->ion_buffer, size);
        ion_file.close();
    } else {
        printf("Couldn't open file for writing: %s", filename);
    }
}