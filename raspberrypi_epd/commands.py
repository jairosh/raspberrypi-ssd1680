DRIVER_OUTPUT_CONTROL = 0x01
GATE_DRIVING_VOLTAGE_CONTROL = 0x03
SOURCE_DRIVING_VOLTAGE_CONTRO = 0x04

INITIAL_CODE_SETTING_OTP = 0x08
# ICS = Initial Code Setting
WRITE_REGISTER_FOR_ICS = 0x09
READ_REGISTER_FOR_ICS = 0x0A

BOOSTER_SOFT_START_CONTROL = 0x0C

DEEP_SLEEP_MODE = 0x10

DATA_ENTRY_MODE = 0x11

SW_RESET = 0x12

HV_READY_DETECTION = 0x14

VCI_DETECTION = 0x15

TEMP_SENSOR_CONTROL = 0x18
TEMP_SENSOR_CONTROL_WRITE = 0x1A
TEMP_SENSOR_CONTROL_READ = 0x1B
TEMP_SENSOR_CONTROL_EXT = 0x1C

MASTER_ACTIVATION = 0x20

DISPLAY_UPDATE_CONTROL = 0x21
DISPLAY_UPDATE_CONTROL_2 = 0x22

WRITE_RAM_BW = 0x24
WRITE_RAM_RED = 0x26
READ_RAM = 0x27
READ_RAM_OPTION = 0x41
SET_RAM_X_STARTEND = 0x44
SET_RAM_Y_STARTEND = 0x45
AUTO_WRITE_RED_RAM = 0x46
AUTO_WRITE_BW_RAM = 0x47
SET_RAM_X_ADDR_COUNTER = 0x4E
SET_RAM_Y_ADDR_COUNTER = 0x4F

VCOM_SENSE = 0x28
VCOM_SENSE_DURATION = 0x29
PROGRAM_VCOM_OTP = 0x2A
WRITE_VCOM_CONTROL = 0x2B
WRITE_VCOM = 0x2C
OTP_REG_READ = 0x2D
USER_ID_READ = 0x2E
STATUS_BIT_READ = 0x2F
PROGRAM_WS_OTP = 0x30
LOAD_WS_OTP = 0x31

WRITE_LUT_REG = 0x32

CRC_CALCULATION = 0x34
CRC_STATUS_READ = 0x35

PROGRAM_OTP_SELECTION = 0x36
WRITE_REG_DISPLAY = 0x37
WRITE_REG_USERID = 0x38
OTP_PROGRAM_MODE = 0x39

BORDER_WAVEFORM_CONTROL = 0x3C
END_OPTION = 0x3F

NOP = 0x7F


"""
DATA CONSTANTS
"""
DEEP_SLEEP_MODE_NORMAL = 0x00
DEEP_SLEEP_MODE_ENTER_DSM1 = 0x01
DEEP_SLEEP_MODE_ENTER_DSM2 = 0x03
