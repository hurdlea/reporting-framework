/*
#  Developed by Alan Hurdle on 24/6/19, 12:05 pm.
#  Last modified 27/6/19, 9:07 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
*/
#ifndef ION_BINARY_WRITER
#define ION_BINARY_WRITER

#include <string>
#include <sys/timeb.h>
#include <typeinfo>

using namespace std;

typedef unsigned int uint;

enum BinaryTypedValue {
    ion_null = 0,
    ion_bool = 1,
    ion_pos_int = 2,
    ion_neg_int = 3,
    ion_timestamp = 6,
    ion_string = 8,
    ion_blob = 10,
    ion_list = 11,
    ion_struct = 13,
    ion_annotation = 14
};
    
class IonBinaryFieldBase {
protected:
    vector<uint8_t> * buffer;

public:
    IonBinaryFieldBase();
    ~IonBinaryFieldBase();

    virtual int get_size();

    virtual uint8_t * pack(uint8_t * dest);

protected:
    int typed_field(int typed_value, uint length, uint offset);

    int typed_field_size(int typed_value, uint length);

    int var_uint_size(uint32_t value);

    int var_int_size(int32_t value);

    int int_size(int32_t value);

    int uint_size(uint32_t value);

    int ion_int(int32_t value, uint offset);

    int ion_uint(uint32_t value, uint offset);

    int var_uint(uint value, uint offset);

    int var_int(int32_t value, uint offset);

    uint32_t find_msb(uint32_t v);
};

class IonBinaryInt: public IonBinaryFieldBase {
public:
    IonBinaryInt(uint symbol_id);
    IonBinaryInt(uint symbol_id, int32_t value);
};

class IonBinaryString: public IonBinaryFieldBase {
public:
    IonBinaryString(uint symbol_id, string value);
};

class IonBinaryTimestamp: public IonBinaryFieldBase {
public:
    IonBinaryTimestamp(int symbol_id, timeb * value);
};

class IonBinaryBoolean: public IonBinaryFieldBase {
public:
    IonBinaryBoolean(int symbol_id, bool value);
};

class IonBinaryNull: public IonBinaryFieldBase {
public:
    IonBinaryNull(int symbol_id);
};

class IonBinaryCollection: public IonBinaryFieldBase {
    vector<IonBinaryFieldBase *> *fields;
    bool has_symbol;
    uint symbol_id;
    uint total_field_size;
    uint type_id;    
public:
    IonBinaryCollection(uint type_id, int size, int symbol_id = 0);

    void append(IonBinaryFieldBase *field);

    int get_size();

    uint8_t * pack(uint8_t * dest);
};
















#endif