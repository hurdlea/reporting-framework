/*
#  Developed by Alan Hurdle on 24/6/19, 12:05 pm.
#  Last modified 27/6/19, 9:07 pm
#  Copyright (c) 2019 Foxtel Management Pty Limited. All rights reserved
*/
#include <vector>
#include <cstddef>
#include <assert.h>
#include <cstring>
#include <ctime>
#include "ion_binary_writer.h"
#include <typeinfo>

using namespace std;

IonBinaryFieldBase::IonBinaryFieldBase() {
    buffer = new vector<uint8_t>();
}

IonBinaryFieldBase::~IonBinaryFieldBase() {
    buffer = NULL;
}

int IonBinaryFieldBase::get_size() {
    return this->buffer->size();
}

uint8_t * IonBinaryFieldBase::pack(uint8_t * dest) {
    std::memcpy(dest, buffer->data(), buffer->size());
    return dest + this->buffer->size();
}

int IonBinaryFieldBase::typed_field(int typed_value, uint length, uint offset) {
    int len_field = 0;
    uint8_t * buff = this->buffer->data();

    if (length >= 0 && length < 14) {
        buff[offset++] = (typed_value << 4) | (length & 0x0F);
    } else {
        buff[offset++] = (typed_value << 4) | 0x0E;
        offset = var_uint(length, offset);
    }
    return offset;
}

int IonBinaryFieldBase::typed_field_size(int typed_value, uint length) {
    int size = 0;
    if (length >= 0 && length < 14) {
        return 1;
    } else {
        return 1 + var_uint_size(length);
    }
}

int IonBinaryFieldBase::var_uint_size(uint32_t value) {
    return (find_msb(value) / 7) + 1;
}

int IonBinaryFieldBase::var_int_size(int32_t value) {
    // Add the additional bit for the sign bit
    uint high_bit = find_msb(abs(value));
    if (high_bit % 7 == 6) high_bit += 1;
    return (high_bit / 7) + 1;
}

int IonBinaryFieldBase::int_size(int32_t value) {
    // Add the additional bit for the sign
    uint high_bit = find_msb(abs(value));
    if (high_bit % 8 == 7) high_bit += 1;
    return (high_bit / 8) + 1;
}

int IonBinaryFieldBase::uint_size(uint32_t value) {
    // Add the additional bit for the sign
    return (find_msb(value) / 8) + 1;
}

int IonBinaryFieldBase::ion_int(int32_t value, uint offset) {
    int bytes = 0;
    uint sign = value < 0 ? 0x80 : 0;
    uint uint_value = abs(value);
    uint8_t * buff = this->buffer->data();

    bytes = int_size(value);
    for (int index = (bytes-1); index >= 0; index--) {
        buff[offset] = (uint_value >> (index * 8)) & 0xFF;
        if (sign != 0) { buff[offset] |= sign; sign = 0; }
        offset++;
    }
    // Set the sign bit

    return offset;
}

int IonBinaryFieldBase::ion_uint(uint32_t value, uint offset) {
    int bytes = 0;
    uint8_t * buff = this->buffer->data();

    bytes = uint_size(value);
    for (int index = (bytes-1); index >= 0; index--) {
        buff[offset] = (value >> (index * 8)) & 0xFF;
        offset++;
    }

    return offset + bytes;
}

// Make a VarUInt from an integer value
int IonBinaryFieldBase::var_uint(uint value, uint offset) {
    uint bytes = var_uint_size(value);
    uint8_t * buff = this->buffer->data();

    for (int index = (bytes - 1); index >= 0; index--) {
        buff[offset] = (value >> (index * 7)) & 0x7F;
        if (index == 0) buff[offset] |= 0x80;
        offset++;
    }

    return offset;
}

// Make a VarInt from an integer value
int IonBinaryFieldBase::var_int(int32_t value, uint offset) {
    int sign = value < 0 ? 0x40 : 0;
    uint uint_value = abs(value);
    // This is the number of occupied octects for the var_int
    // Where the octect contains 7 bits
    uint bytes = var_int_size(uint_value);
    uint8_t * buff = this->buffer->data();

    for (int index = (bytes - 1); index >= 0; index--) {
        buff[offset] = (uint_value >> (index * 7)) & 0x7F;
        if (index == 0) buff[offset] |= 0x80;
        if (sign != 0) { buff[offset] |= sign; sign = 0; };
        offset++;
    }

    return offset;
}

uint32_t IonBinaryFieldBase::find_msb(uint32_t v)
{
    static const int MultiplyDeBruijnBitPosition[32] =
    {
        0, 9, 1, 10, 13, 21, 2, 29, 11, 14, 16, 18, 22, 25, 3, 30,
        8, 12, 20, 28, 15, 17, 24, 7, 19, 27, 23, 6, 26, 5, 4, 31
    };

    v |= v >> 1; // first round down to one less than a power of 2
    v |= v >> 2;
    v |= v >> 4;
    v |= v >> 8;
    v |= v >> 16;

    return MultiplyDeBruijnBitPosition[(uint32_t)(v * 0x07C4ACDDU) >> 27];
}    

IonBinaryInt::IonBinaryInt(uint symbol_id) : IonBinaryFieldBase() {
    int size = 0;
    int offset = 0;

    size += var_uint_size(symbol_id);
    buffer->resize(size);

    // Symbol
    offset = var_uint(symbol_id, offset);
}
/*
           7       4 3       0
          +---------+---------+
Int value |  2 or 3 |    L    |
          +---------+---------+======+
          :     length [VarUInt]     :
          +==========================+
          :     magnitude [UInt]     :
          +==========================+
*/
IonBinaryInt::IonBinaryInt(uint symbol_id, int32_t value) : IonBinaryFieldBase() {
    int size = 0;
    int offset = 0;
    uint8_t type_id = (value < 0) ? ion_neg_int : ion_pos_int;      
    uint uint_value = abs(value);
    int bytes = uint_size(uint_value);

    if (symbol_id != 0) size += var_uint_size(symbol_id);
    size += typed_field_size(type_id, bytes);
    size += bytes;
    buffer->resize(size);

    // Symbol
    if (symbol_id != 0) offset = var_uint(symbol_id, offset);
    // Type definition
    offset = typed_field(type_id, bytes, offset);
    // Value
    offset = ion_uint(uint_value, offset);
}

/* 
              7       4 3       0
             +---------+---------+
String value |    8    |    L    |
             +---------+---------+======+
             :     length [VarUInt]     :
             +==========================+
             :  representation [UTF8]   :
             +==========================+
*/
IonBinaryString::IonBinaryString(uint symbol_id, string value)  : IonBinaryFieldBase() {
    int size = 0;
    int length = value.size();
    char * p;
    int offset = 0;
    uint8_t type_id = ion_string;

    // Length of the symbol
    size += var_uint_size(symbol_id);
    size += typed_field_size(type_id, length);
    size += length;
    buffer->resize(size);

    // Write the symbol and type fields
    offset = var_uint(symbol_id, offset);
    offset = typed_field(ion_string, length, offset);
    // Write the string contents need to make this a UTF-8 for production
    p = (char *)buffer->data() + offset;
    value.copy(p, value.size());
}

/*
                 7       4 3       0
                +---------+---------+
Timestamp value |    6    |    L    |
                +---------+---------+========+
                :      length [VarUInt]      :
                +----------------------------+
                |      offset [VarInt]       |
                +----------------------------+
                |       year [VarUInt]       |
                +----------------------------+
                :       month [VarUInt]      :
                +============================+
                :         day [VarUInt]      :
                +============================+
                :        hour [VarUInt]      :
                +====                    ====+
                :      minute [VarUInt]      :
                +============================+
                :      second [VarUInt]      :
                +============================+
                : fraction_exponent [VarInt] :
                +============================+
                : fraction_coefficient [Int] :
                +============================+
 */
IonBinaryTimestamp::IonBinaryTimestamp(int symbol_id, timeb * value)  : IonBinaryFieldBase() {
    int size = 0;
    int t_size = 0;
    int offset = 0;

    struct tm * time_fields;

    time_fields = gmtime(&value->time);
    // offset value
    t_size += var_int_size(time_fields->tm_gmtoff/60);
    t_size += var_uint_size(time_fields->tm_year + 1900);
    t_size += var_uint_size(time_fields->tm_mon + 1);
    t_size += var_uint_size(time_fields->tm_mday);
    t_size += var_uint_size(time_fields->tm_hour);
    t_size += var_uint_size(time_fields->tm_min);
    t_size += var_uint_size(time_fields->tm_sec);
    t_size += var_int_size(-3);
    t_size += int_size(value->millitm);

    size += var_uint_size(symbol_id);
    size += typed_field_size(ion_timestamp, t_size);
    buffer->resize(size + t_size);

    // Symbol
    offset = var_uint(symbol_id, offset);
    // Type definition
    offset = typed_field(ion_timestamp, t_size, offset);
    // Value
    offset = var_int(time_fields->tm_gmtoff/60, offset);
    offset = var_uint(time_fields->tm_year + 1900, offset);
    offset = var_uint(time_fields->tm_mon + 1, offset);
    offset = var_uint(time_fields->tm_mday, offset);
    offset = var_uint(time_fields->tm_hour, offset);
    offset = var_uint(time_fields->tm_min, offset);
    offset = var_uint(time_fields->tm_sec, offset);
    offset = var_int(-3, offset);
    offset = ion_int(value->millitm, offset);
}

/* 
            7       4 3       0
           +---------+---------+
Bool value |    1    |   rep   |
           +---------+---------+
*/
IonBinaryBoolean::IonBinaryBoolean(int symbol_id, bool value)  : IonBinaryFieldBase() {
    int size = 0;
    int offset = 0;
    uint8_t type_id = ion_bool;      

    size += var_uint_size(symbol_id);
    size += typed_field_size(type_id, 1);
    buffer->resize(size);

    // Symbol
    offset = var_uint(symbol_id, offset);
    // Type definition
    offset = typed_field(type_id, value ? 1 : 0, offset);
}

/* 
            7       4 3       0
           +---------+---------+
Null value |    0    |    15   |
           +---------+---------+
*/
IonBinaryNull::IonBinaryNull(int symbol_id)  : IonBinaryFieldBase() {
    int size = 0;
    int offset = 0;
    uint8_t type_id = ion_null;      

    size += var_uint_size(symbol_id);
    size += typed_field_size(type_id, 1);
    buffer->resize(size);

    // Symbol
    offset = var_uint(symbol_id, offset);
    // Type definition
    offset = typed_field(type_id, 0xF, offset);
}

/* 
            7       4 3       0
           +---------+---------+
List       |   11    |    L    |
           +---------+---------+======+
           :     length [VarUInt]     :
           +==========================+
           :           value          :
           +==========================+

           7       4 3       0
           +---------+---------+
Struct     |   13    |    L    |
           +---------+---------+======+
           :     length [VarUInt]     :
           +======================+===+==================+
           : field name [VarUInt] :        value         :
           +======================+======================+

           7       4 3       0
           +---------+---------+
Annotation |   14    |    L    |
wrapper    +---------+---------+======+
           |  annot_length [VarUInt]  |
           +--------------------------+
           |      annot [VarUInt]     |
           +--------------------------+
           |          value           |
           +--------------------------+
*/
IonBinaryCollection::IonBinaryCollection(uint type_id, int size, int symbol_id) : IonBinaryFieldBase(), type_id(type_id), symbol_id(symbol_id) {
    assert(type_id == ion_struct || type_id == ion_list || type_id == ion_annotation);
    this->has_symbol = symbol_id != 0 ? true : false; 
    total_field_size = 0;

    fields = new vector<IonBinaryFieldBase *>();
}

void IonBinaryCollection::append(IonBinaryFieldBase *field) {
    fields->push_back(field);
}

int IonBinaryCollection::get_size() {
    int size = 0;
    uint offset = 0;

    // Get the size of all of the child elements.
    // This caters for collections within collections.
    total_field_size = 0;

    IonBinaryFieldBase ** ion_fields = this->fields->data();
    for (uint index = 0; index < this->fields->size(); index++) {
        total_field_size += ion_fields[index]->get_size();
    }

    // Account for the header of the collection which is variable
    // based on the size of the contained elements.
    if (has_symbol) size += var_uint_size(symbol_id);
    size += typed_field_size(type_id, total_field_size);

    // Create the struct ion type binary representation with the
    // length of the contained items.
    buffer->resize(size);
    if (has_symbol) offset = var_uint(symbol_id, offset);
    offset = typed_field(type_id, total_field_size, offset);
    offset = var_uint(total_field_size, offset);

    return size + total_field_size;
}

uint8_t * IonBinaryCollection::pack(uint8_t * dest) {
    // Pack the type definition and contained fields / collections
    std::memcpy(dest, buffer->data(), buffer->size());
    dest += buffer->size();

    if (fields->size() > 0) {
        for (vector<IonBinaryFieldBase *>::iterator it = this->fields->begin() ; it != this->fields->end(); ++it) {
            dest = (*it)->pack(dest);
        }
    }
    return dest;
}