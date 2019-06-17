#  Developed by Alan Hurdle on 17/6/19, 12:05 pm.
#  Last modified 17/6/19, 11:48 am
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
DOC_VERSION = "document-version"
TIMESTAMP = "timestamp"
SEQUENCE_ID = "sequence"
LIBRARY_NAME = "library-name"
LIBRARY_VERSION = "library-version"
DEVICE_TYPE = "gizmo-type"
DEVICE_NAME = "gizmo-name"
DEVICE_VARIANT = "gizmo-version"
DEVICE_HW_ID = "gizmo-id"
DEVICE_CDSN = "gizmo-idClient"
DEVICE_CA_CARD = "gizmo-idCard"
CUSTOMER_AMS_ID = "sojourner-idFx"
CUSTOMER_AMS_PANEL = "sojourner-idPanel"
SOFTWARE_VERSION = "application-appVersionShort"
EVENT_LIST = "batch"
HARDWARE_VERSION = "gizmo-fwVersion"  # Device Context Event
OS_VERSION = "gizmo-osVersion"
DEVICE_MODEL_ID = "gizmo-modelId"
DEVICE_RESETS = "gizmo-pwrcycle"
DEVICE_UPTIME = "gizmo-uptime"
PVR_HDD_SIZE = "gizmo-storageCapacity"
PVR_CUST_FREE_PERC = "gizmo-storageCustSpaceLeft"
PVR_PVOD_FREE_PERC = "gizmo-storageProdSpaceLeft"
PVR_NUM_RECORDINGS = "gizmo-storageTotalRecordings"
DISPLAY_CONNECTION = "display-connection"
DISPLAY_NAME = "display-edidName"
DISPLAY_MANUFACTURER = "display-edidIdManufacturer"
DISPLAY_BUILD_DATE = "display-edidBuildDate"
DISPLAY_OPTIMAL_RES = "display-edidOptimalMaxResolution"
DISPLAY_HDR_SUPPORT = "display-edidIdHdr"
APP_REGION_ID = "application-regionId"
APP_POSTCODE = "application-postcode"
APP_DTT_REGION = "application-dttRegion"
NETWORK_TYPE = "connectivity-connectionType"
RCU_VERSION = "rcu-version"
RCU_KEYS_PRESSED = "rcu-keysPressed"
RCU_TYPE = "rcu-type"
UI_VERSION = "application-id"
EPG_VERSION = "application-idSupplemental"
EPG_VERSION_INSTALL_DATE = "application-installDate"
EVENT_ID = "event-idClass"  # Event header
APP_SESSION_ID = "behavioural-idSessionApp"
USAGE_SESSION_ID = "behavioural-idSessionUsage"
PAGE_SESSION_ID = "behavioural-idSessionPage"
CONTEXT_EVENT_ID = "gizmo-deviceContextId"
EVENT_PROPERTY_STRUCT = "properties"
EVENT_ACTION = "navigation-action"  # Common Event Properties
EVENT_USER_INITIATED = "behavioural-userInitiated"
PAGE_NAME = "navigation-page"  # Page
PREVIOUS_PAGE = "navigation-previousPage"
PAGE_FILTER = "navigation-filter"
PAGE_SORT = "navigation-sort"
CONTENT_PROVIDER = "metadata-contentProvider"  # Content Metadata
CONTENT_PROMO_CHANNEL = "metadata-channelProviderPromo"
CONTENT_PROGRAM_ID = "metadata-programmeId"
CONTENT_SCHEDULE_ID = "metadata-programmeEventId"
CONTENT_START_TIMESTAMP = "metadata-programmeStartDateTime"
CONTENT_DURATION = "metadata-programmeDuration"
CONTENT_PROGRAM_TITLE = "metadata-programmeTitle"
CONTENT_EPISODE_TITLE = "metadata-nameEpisode"
CONTENT_CLASSIFICATION = "metadata-programmeClassification"
CONTENT_RESOLUTION = "metadata-resolution"
CONTENT_PRICE = "metadata-price"
CONTENT_TYPE = "media-contentType"  # Media specific data
PLAYER_VIEW_STATUS = "media-viewStatus"
MEDIA_EVENT_SOURCE = "media-eventSource"
MEDIA_BOOKING_SOURCE = "media-bookingSource"
MEDIA_REC_START_TIMESTAMP = "media-recordStartTime"
MEDIA_DURATION = "media-duration"
MEDIA_REC_STATUS = "media-recordStatus"
MEDIA_EXPIRY_TIMESTAMP = "media-expiryDateTime"
MEDIA_EXTEND_REC_DURATION = "media-extendRecordDuration"
MEDIA_DOWNLOAD_STATE = "media-downloadState"
MEDIA_MAX_VIEWED_OFFSET = "media-maxViewedOffset"
PLAYER_VIEWING_START_TIMESTAMP = "player-viewingStartDateTime"  # Player specific data
PLAYER_TRICKMODE_SPEED = "player-mediaSpeed"
PLAYER_MEDIA_OFFSET = "player-mediaOffset"
PLAYER_VIEWED_DURATION = "player-mediaViewedDuration"
PLAYER_QOS_AVG_BITRATE_KBPS = "player-averageBitrateKbps"
PLAYER_QOS_STARTUP_MS = "player-startupTime"
PLAYER_QOS_BUFFERING_MS = "player-bufferingDuration"
PLAYER_QOS_BUFFERING_COUNT = "player-bufferingCount"
PLAYER_QOS_ABR_SHIFTS = "player-abrShiftCount"
PLAYER_JUMP_TO = "player-jumpTo"
ERROR_FNUM_MESSAGE = "behavioural-idMessageError"  # Error Message
ERROR_TECHNICAL_MESSAGE = "behavioural-idMessageErrorTechnical"
DEVICE_POWER_STATUS = "gizmo-statusPower"  # Power State Event
DISPLAY_ON = "display-connected"  # Video Output properties
DISPLAY_DETECTED_HDR = "display-detectedHDRCapability"
DISPLAY_NEG_HDMI = "display-negotiatedHDMI"
DISPLAY_NEG_HDCP = "display-negotiatedHDCP"
DISPLAY_NEG_RESOLUTION = "display-negotiatedResolution"
DISPLAY_NEG_FRAMERATE = "display-negotiatedFramerate"
DISPLAY_EDID_SIG = "display-edidHash"
DISPLAY_EDID_BLOCK = "display-edidBlock"
SELECTOR_TRACK_ID = "navigation-selectorTrackId"  # Selector
SELECTOR_TYPE = "navigation-selectorType"
SELECTOR_TITLE = "navigation-selectorTitle"
SELECTOR_ROW = "navigation-selectorRow"
SELECTOR_COLUMN = "navigation-selectorColumn"
CONTENT_BRAND = "metadata-brand"
TILE_LOCKED = "navigation-locked"
COLLECTION_TITLE = "metadata-collectionTitle"
COLLECTION_SOURCE = "metadata-collectionSource"
SEARCH_INITIATOR_SOURCE = "navigation-searchResultType"  # Search
SEARCH_TERM = "navigation-searchTerm"
SEARCH_SCORE = "navigation-searchScore"
CONF_PIN_CLASSIFICATION = "application-pinClassification"  # Application Configuration
CONF_PIN_INFO = "application-pinInfo"
CONF_PIN_NC = "application-pinNC"
CONF_CHANNEL_BLOCKING_ON = "application-channelBlocking"
CONF_PIN_ON_PURCHASE = "application-pinPurchase"
CONF_PIN_PROTECT_KEEP = "application-pinProtectKeep"
CONF_PIN_IP_VIDEO = "application-pinIPVideo"
CONF_PIN_APP_LAUNCH = "application-pinAppLaunch"
CONF_NUM_SCHED_REMINDERS = "application-numScheduledReminders"
CONF_NUM_SCHED_RECORDINGS = "application-numScheduledRecordings"
CONF_NUM_TEAM_LINKS = "application-numTeamLinks"
CONF_FAVOURITES_SETUP = "application-favouritesConfigured"
CONF_DTT_SETUP = "application-dttConfigured"
CONF_ENERGY_SAVING_ON = "application-energySavingOn"
CONF_SPDIF_AUDIO_MODE = "application-spdifAudioOutput"
CONF_HDMI_AUDIO_MODE = "application-hdmiAudioOutput"
CONF_DOWNLOAD_HD = "application-downloadHD"
CONF_STREAM_FROM_STORE = "application-streamFromStore"
CONF_CEC_POWER = "application-cecPower"
CONF_CEC_VOLUME = "application-cecVolume"
APP_NAME = "application-name"  # Application Launch Event
APP_PROVIDER = "application-provider"
APP_STATE = "application-state"
REBOOT_TYPE = "gizmo-rebootType"

table = [
	DOC_VERSION,
	TIMESTAMP,
	SEQUENCE_ID,
	LIBRARY_NAME,
	LIBRARY_VERSION,
	DEVICE_TYPE,
	DEVICE_NAME,
	DEVICE_VARIANT,
	DEVICE_HW_ID,
	DEVICE_CDSN,
	DEVICE_CA_CARD,
	CUSTOMER_AMS_ID,
	CUSTOMER_AMS_PANEL,
	SOFTWARE_VERSION,
	EVENT_LIST,
	HARDWARE_VERSION,  # Device Context Event
	OS_VERSION,
	DEVICE_MODEL_ID,
	DEVICE_RESETS,
	DEVICE_UPTIME,
	PVR_CUST_FREE_PERC,
	PVR_PVOD_FREE_PERC,
	PVR_NUM_RECORDINGS,
	DISPLAY_CONNECTION,
	DISPLAY_NAME,
	DISPLAY_MANUFACTURER,
	DISPLAY_BUILD_DATE,
	DISPLAY_OPTIMAL_RES,
	DISPLAY_HDR_SUPPORT,
	APP_POSTCODE,
	APP_DTT_REGION,
	APP_REGION_ID,
	NETWORK_TYPE,
	RCU_VERSION,
	RCU_KEYS_PRESSED,
	UI_VERSION,
	EPG_VERSION,
	EPG_VERSION_INSTALL_DATE,
	RCU_TYPE,
	EVENT_ID,  # Event header
	APP_SESSION_ID,
	USAGE_SESSION_ID,
	PAGE_SESSION_ID,
	CONTEXT_EVENT_ID,
	EVENT_PROPERTY_STRUCT,
	EVENT_ACTION,  # Common Event Properties
	EVENT_USER_INITIATED,
	PAGE_NAME,  # Page
	PREVIOUS_PAGE,
	PAGE_FILTER,
	PAGE_SORT,
	CONTENT_PROVIDER,  # Content Metadata
	CONTENT_PROMO_CHANNEL,
	CONTENT_PROGRAM_ID,
	CONTENT_SCHEDULE_ID,
	CONTENT_START_TIMESTAMP,
	CONTENT_DURATION,
	CONTENT_PROGRAM_TITLE,
	CONTENT_EPISODE_TITLE,
	CONTENT_CLASSIFICATION,
	CONTENT_RESOLUTION,
	CONTENT_PRICE,
	CONTENT_TYPE,  # Media specific data
	PLAYER_VIEW_STATUS,
	MEDIA_EVENT_SOURCE,
	MEDIA_BOOKING_SOURCE,
	MEDIA_REC_START_TIMESTAMP,
	MEDIA_DURATION,
	MEDIA_REC_STATUS,
	MEDIA_EXPIRY_TIMESTAMP,
	MEDIA_EXTEND_REC_DURATION,
	MEDIA_DOWNLOAD_STATE,
	MEDIA_MAX_VIEWED_OFFSET,
	PLAYER_VIEWING_START_TIMESTAMP,  # Player specific data
	PLAYER_TRICKMODE_SPEED,
	PLAYER_MEDIA_OFFSET,
	PLAYER_VIEWED_DURATION,
	PLAYER_QOS_AVG_BITRATE_KBPS,
	PLAYER_QOS_STARTUP_MS,
	PLAYER_QOS_BUFFERING_MS,
	PLAYER_QOS_BUFFERING_COUNT,
	PLAYER_QOS_ABR_SHIFTS,
	PLAYER_JUMP_TO,
	ERROR_FNUM_MESSAGE,  # Error Message
	ERROR_TECHNICAL_MESSAGE,
	DEVICE_POWER_STATUS,  # Power State Event
	DISPLAY_ON,  # Video Output properties
	DISPLAY_DETECTED_HDR,
	DISPLAY_NEG_HDMI,
	DISPLAY_NEG_HDCP,
	DISPLAY_NEG_RESOLUTION,
	DISPLAY_NEG_FRAMERATE,
	DISPLAY_EDID_SIG,
	DISPLAY_EDID_BLOCK,
	SELECTOR_TRACK_ID,  # Selector
	SELECTOR_TYPE,
	SELECTOR_TITLE,
	SELECTOR_ROW,
	SELECTOR_COLUMN,
	CONTENT_BRAND,
	TILE_LOCKED,
	COLLECTION_TITLE,
	COLLECTION_SOURCE,
	SEARCH_INITIATOR_SOURCE,  # Search
	SEARCH_TERM,
	SEARCH_SCORE,
	CONF_PIN_CLASSIFICATION,  # Application Configuration
	CONF_PIN_INFO,
	CONF_PIN_NC,
	CONF_CHANNEL_BLOCKING_ON,
	CONF_PIN_ON_PURCHASE,
	CONF_PIN_PROTECT_KEEP,
	CONF_PIN_IP_VIDEO,
	CONF_PIN_APP_LAUNCH,
	CONF_NUM_SCHED_REMINDERS,
	CONF_NUM_SCHED_RECORDINGS,
	CONF_NUM_TEAM_LINKS,
	CONF_FAVOURITES_SETUP,
	CONF_DTT_SETUP,
	CONF_ENERGY_SAVING_ON,
	CONF_SPDIF_AUDIO_MODE,
	CONF_HDMI_AUDIO_MODE,
	CONF_DOWNLOAD_HD,
	CONF_STREAM_FROM_STORE,
	CONF_CEC_POWER,
	CONF_CEC_VOLUME,
	APP_NAME,  # Application Launch Event
	APP_PROVIDER,
	APP_STATE,
	REBOOT_TYPE
]
