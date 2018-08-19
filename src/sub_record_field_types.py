import struct
from collections import namedtuple

SubRecordFieldType = namedtuple("SubRecordFieldType", "read write")

# https://docs.python.org/3.4/library/struct.html#format-characters
# https://docs.python.org/2.4/lib/bltin-file-objects.html

class SubRecordFieldFlags(object):
    def __init__(self, flag_names, flags_int):
        self.flag_names = flag_names
        self.flags_int = flags_int
    def get_flag_with_name(self, name):
        if self.flag_names is not None:
            for named_flag in self.flag_names:
                if named_flag[1] == name:
                    flag = self.flags_int & named_flag[0]
                    return True if flag else False
        raise LookupError("Unknown flag name \"%s\"." % name)
    def __getitem__(self, name):
        if isinstance(name, (int, long)):
            return self.fields[name]
        else:
            flag = (self.flags_int >> name) & 1
            return True if flag else False
    def __repr__(self):
        return "<flags 0b{0:b}>".format(self.flags_int)

# Signed integer
def sub_record_read_integer_signed(binary_data):
    if len(binary_data) == 1:
        return struct.unpack("b", binary_data)[0]
    elif len(binary_data) == 2:
        return struct.unpack("h", binary_data)[0]
    elif len(binary_data) == 4:
        return struct.unpack("i", binary_data)[0]
    elif len(binary_data) == 8:
        return struct.unpack("q", binary_data)[0]
    else:
        raise ValueError("Unacceptable integer size.")
def sub_record_write_integer_signed(value, byte_length):
    if byte_length == 1:
        return struct.pack("b", value)
    elif byte_length == 2:
        return struct.pack("h", value)
    elif byte_length == 4:
        return struct.pack("i", value)
    elif byte_length == 8:
        return struct.pack("q", value)
    else:
        raise ValueError("Unacceptable integer size.")
data_integer_signed = SubRecordFieldType(
    sub_record_read_integer_signed, sub_record_write_integer_signed
)

# Unsigned integer
def sub_record_read_integer_unsigned(binary_data):
    if len(binary_data) == 1:
        return struct.unpack("B", binary_data)[0]
    elif len(binary_data) == 2:
        return struct.unpack("H", binary_data)[0]
    elif len(binary_data) == 4:
        return struct.unpack("I", binary_data)[0]
    elif len(binary_data) == 8:
        return struct.unpack("Q", binary_data)[0]
    else:
        raise ValueError("Unacceptable integer size.")
def sub_record_write_integer_unsigned(value, byte_length):
    if byte_length == 1:
        return struct.pack("B", value)
    elif byte_length == 2:
        return struct.pack("H", value)
    elif byte_length == 4:
        return struct.pack("I", value)
    elif byte_length == 8:
        return struct.pack("Q", value)
    else:
        raise ValueError("Unacceptable integer size.")
data_integer_unsigned = SubRecordFieldType(
    sub_record_read_integer_unsigned, sub_record_write_integer_unsigned
)

# Floating point number
def sub_record_read_float(binary_data):
    if len(binary_data) == 4:
        return struct.unpack("f", binary_data)[0]
    elif len(binary_data) == 8:
        return struct.unpack("d", binary_data)[0]
    else:
        raise ValueError("Unacceptable float size.")
def sub_record_write_float(value, byte_length):
    if byte_length == 4:
        return struct.pack("f", value)
    elif byte_length == 8:
        return struct.pack("d", value)
    else:
        raise ValueError("Unacceptable float size.")
data_float = SubRecordFieldType(
    sub_record_read_float, sub_record_write_float
)

# Unknown purpose
def sub_record_read_unknown(binary_data):
    return binary_data
def sub_record_write_unknown(value, byte_length):
    assert len(value) == byte_length
    return value
data_unknown = SubRecordFieldType(
    sub_record_read_unknown, sub_record_write_unknown
)

# Padded string
def sub_record_read_string_padded(binary_data):
    for i in range(len(binary_data)):
        if binary_data[i] == b"\x00":
            return binary_data[0:i]
    return binary_data
def sub_record_write_string_padded(value, byte_length):
    assert len(value) <= byte_length
    return value.ljust(byte_length, b"\x00")
data_string_padded = SubRecordFieldType(
    sub_record_read_string_padded, sub_record_write_string_padded
)

# Exact length string (used for values that might contain null characters)
def sub_record_read_string_exact(binary_data):
    return binary_data
def sub_record_write_string_exact(value, byte_length):
    assert len(value) == byte_length
    return value
data_string_exact = SubRecordFieldType(
    sub_record_read_string_exact, sub_record_write_string_exact
)

# Null-terminated variable length string
def sub_record_read_string_variable(binary_file):
    value = b""
    while True:
        next_byte = binary_file.read(1)
        if not len(next_byte):
            raise EOFError()
        elif next_byte == b"\x00":
            break
        else:
            value += next_byte
    return value
def sub_record_write_string_variable(value, byte_length):
    return value + "\x00"
data_string_variable = SubRecordFieldType(
    sub_record_read_string_variable, sub_record_write_string_variable
)

# A list of null-terminated variable length strings
def sub_record_read_string_list(binary_data):
    string_list = []
    current_string = bytearray()
    for char in binary_data:
        if char == 0 or char == b"\x00":
            string_list.append(bytes(current_string))
            current_string = bytearray()
        else:
            current_string.append(char)
    if len(current_string):
        raise Exception("Unexpected end of string due to size error.")
    return string_list
def sub_record_write_string_list(value, byte_length):
    assert isinstance(value, list)
    binary_data = b"\x00".join(value)
    return binary_data
data_string_list = SubRecordFieldType(
    sub_record_read_string_list, sub_record_write_string_list
)

# Flags bitfield
def sub_record_read_flags(flag_names, binary_data):
    flags_int = sub_record_read_integer_signed(binary_data)
    return SubRecordFieldFlags(flag_names, flags_int)
def sub_record_write_flags(value, byte_length):
    return sub_record_write_integer_signed(value, byte_length)
def data_flags(flag_names=None):
    def read(binary_data):
        return sub_record_read_flags(flag_names, binary_data)
    return SubRecordFieldType(read, sub_record_write_flags)
