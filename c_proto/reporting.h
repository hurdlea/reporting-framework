/*
#  Developed by Alan Hurdle on 24/6/19, 12:05 pm.
#  Last modified 27/6/19, 9:07 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
*/
#ifndef REPORTING_H
#define REPORTING_H

#include <string>
#include <vector>
#include "ion_binary_writer.h"

using namespace std;

enum ReportingEventId {
    END_OF_FILE_EVENT = 1,
    ERROR_MESSAGE_EVENT = 2,
    POWER_STATE_EVENT = 3,
    REBOOT_REQUEST_EVENT = 4,
    CODE_DOWNLOAD_EVENT = 5,
    LIVE_PLAY_EVENT = 16,
    RECORDING_EVENT = 17,
    PLAYBACK_EVENT = 18,
    VIEWING_STOP_EVENT = 19,
    VIDEO_OUTPUT_EVENT = 20,
    PAGE_VIEW_EVENT = 32,
    COLLECTION_SELECTOR_EVENT = 33,
    CONTENT_SELECTOR_EVENT = 34,
    SEARCH_QUERY_EVENT = 35,
    APPLICATION_LAUNCH_EVENT = 36,
    BOOK_ACTION = 48,
    WATCH_ACTION = 49,
    DOWNLOAD_ACTION = 50,
    DELETE_ACTION = 51,
    KEEP_ACTION = 52,
    UPGRADE_ACTION = 53,
    RENT_ACTION = 54,
    NEXT_EPISODE_ACTION = 55,
    JUMP_ACTION = 56,
    DEVICE_CONTEXT_EVENT = 64,
    FEATURE_USAGE_CONTEXT_EVENT = 65
};

enum PowerStateType {
    PowerOn = 0,
    StandByIn,
    StandByOut
};

class ReportingEvent {
public:
    int event_id;
    timeb * timestamp;
    timeb * application_session;
    timeb * usage_session;
    timeb * page_session;
    int device_context_id;


    ReportingEvent(int event_id, timeb * timestamp);

    virtual IonBinaryCollection * ionize_event() = 0;

    void ionize_context(IonBinaryCollection * parent);
};

class PowerStateEvent: public ReportingEvent {
    static const string states[];

public:
    PowerStateType status;
    bool user_initiated;

    PowerStateEvent(timeb * timestamp, PowerStateType status, bool user_initiated);
    
    IonBinaryCollection * ionize_event();
};

class IonWrapper {
    IonBinaryCollection * header;
    string symbol_schema;
    int schema_version;

public:
    uint8_t * ion_buffer;

    IonWrapper(string symbol_schema, int schema_version);
    void set_header(IonBinaryCollection * header);
    int serialize();
};


class ReportingHeader {
public:
    string document_version;
    timeb * timestamp;
    int sequence;
    string library_name;
    string library_version;
    string device_type;
    string device_name;
    string device_variant;
    string device_hw_id;
    string software_version;
    string device_cdsn;
    string device_ca_card;
    string ams_id;
    string ams_panel;
    vector<ReportingEvent *> * batch;

    ReportingHeader(timeb * timestamp, int sequence, string device_variant, const char * device_hw_id, const char * software_version, 
              const char * device_cdsn, const char * device_ca_card, const char * ams_id, const char * ams_panel);
    void addEvent(ReportingEvent * event);
    IonBinaryCollection * ionize();
};

#endif