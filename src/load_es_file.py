import struct

from record_classes import *
from record_types import get_record_type

def read_int32(binary_file):
    value_bin = binary_file.read(4)
    if len(value_bin) != 4: raise EOFError()
    return struct.unpack("I", value_bin)[0]

def read_elder_scrolls_paths(*paths):
    es_file_list = []
    for path in paths:
        print("Loading \"%s\"..." % path)
        with open(path, "rb") as binary_file:
            es_file = read_elder_scrolls_file(oath, binary_file)
            es_file_list.append(es_file)
    print("Finished loading data files.")
    return ESData(es_file_list)

def read_elder_scrolls_file(path, binary_file):
    es_file = ESFile(path, [])
    while True:
        record = read_record(es_file, binary_file)
        if record:
            if not len(es_file.records) and record.type_name != b"TES3":
                raise Exception("File is not a TES3 ESM or ESP.")
            es_file.records.append(record)
        else:
            break
    es_file.process_data()
    return es_file

def read_record(es_file, binary_file):
    # Read header data
    name = binary_file.read(4)
    if len(name) == 0: return None
    if len(name) != 4: raise EOFError()
    byte_length = read_int32(binary_file)
    unknown_flag = read_int32(binary_file)
    flag_bits = read_int32(binary_file)
    # Build a record object
    record_type = get_record_type(name)
    sub_record_list = []
    # Handle the case where this record type isn't known (skip it)
    if record_type is None:
        binary_file.seek(binary_file.tell() + byte_length)
    # Handle a known record type
    else:
        file_begin_position = binary_file.tell()
        while True:
            # Check for end of record
            file_current_position = binary_file.tell()
            current_byte_length = file_current_position - file_begin_position
            if current_byte_length == byte_length:
                break
            elif current_byte_length > byte_length:
                raise Exception("Record size error in \"%s\"." % record_type.name)
            # Read next sub-record
            sub_record = read_sub_record(record_type, binary_file)
            sub_record_list.append(sub_record)
    # Build and return a Record object
    return Record(
        es_file=es_file,
        record_type=record_type,
        record_type_name=name,
        unknown_flag=unknown_flag,
        flag_bits=flag_bits,
        sub_records=sub_record_list,
    )

def read_sub_record(record_type, binary_file):
    # Read header data
    name = binary_file.read(4)
    if len(name) != 4: raise EOFError()
    byte_length = read_int32(binary_file)
    # Build a sub-record object
    sub_record_type = record_type.get_sub_record_type(name, byte_length)
    field_list = []
    if sub_record_type is None:
        binary_file.seek(binary_file.tell() + byte_length)
    else:
        file_begin_position = binary_file.tell()
        for type_field in sub_record_type.fields:
            file_current_position = binary_file.tell()
            remaining_byte_length = (
                byte_length + file_begin_position - file_current_position
            )
            field_value = read_sub_record_field_value(
                type_field, remaining_byte_length, binary_file
            )
            field_list.append(SubRecordField(
                sub_record_field_type=type_field,
                value=field_value,
            ))
        # Check that the expected length was met
        file_end_position = binary_file.tell()
        actual_byte_length = file_end_position - file_begin_position
        if actual_byte_length != byte_length:
            raise Exception("Sub-record size error in \"%s\" > \"%s\". " % (
                record_type.name, sub_record_type.name
            ) + "Expected %s bytes but found %s bytes." % (
                byte_length, actual_byte_length
            ))
    # Build and return a SubRecord object
    return SubRecord(
        sub_record_type=sub_record_type,
        sub_record_type_name=name,
        fields=field_list,
    )

def read_sub_record_field_value(
    sub_record_type_field, sub_record_byte_length, binary_file
):
    if sub_record_type_field.byte_length == SubRecordTypeField.variable_size:
        return sub_record_type_field.data_type.read(binary_file)
    elif sub_record_type_field.byte_length == SubRecordTypeField.sub_record_size:
        binary_data = binary_file.read(sub_record_byte_length)
        if len(binary_data) != sub_record_byte_length:
            raise EOFError()
        return sub_record_type_field.data_type.read(binary_data)
    else:
        binary_data = binary_file.read(sub_record_type_field.byte_length)
        if len(binary_data) != sub_record_type_field.byte_length:
            raise EOFError()
        return sub_record_type_field.data_type.read(binary_data)
