try:
    test_long_name = long
    def is_number(value):
        return isinstance(value, (int, long))
except NameError:
    def is_number(value):
        return isinstance(value, int)

def get_bytes(text):
    if isinstance(text, bytes):
        return text
    return bytes(text.encode("latin-1", "ignore"))

class ESData(object):
    def __init__(self, es_files):
        self.es_files = es_files
    def iter_records(self):
        for es_file in self.es_files:
            for record in es_file.records:
                yield record
    def get_record_by_name_id(self, record_name, name_id):
        for es_file in self.es_files:
            record = es_file.get_record_by_name_id(record_name, name_id)
            if record:
                return record
        return None
    def get_record_by_name_input(self, record_name, name_input):
        for es_file in self.es_files:
            record = es_file.get_record_by_name_input(record_name, name_input)
            if record:
                return record
        return None
    def iter_records_with_name(self, name):
        for es_file in self.es_files:
            for record in es_file.iter_records_with_name(name):
                yield record
    def __getitem__(self, name):
        return list(self.iter_records_with_name(name))
    def add_file(self, es_file):
        self.es_files.append(es_file)

class ESFile(object):
    def __init__(self, path, records):
        self.path = path
        self.records = records
    def get_record_by_name_id(self, record_name, name_id):
        record_name_bytes = get_bytes(record_name)
        name_id_bytes = get_bytes(name_id)
        for record in self.records:
            if record.type_name == record_name_bytes or (
                record.type and record.type.long_name == record_name
            ):
                name_sub_record = record["NAME"]
                if name_sub_record and name_sub_record[0] == name_id_bytes:
                    return record
        return None
    def get_record_by_name_input(self, record_name, name_input):
        record_name_bytes = get_bytes(record_name)
        name_input_bytes = get_bytes(name_input)
        for record in self.records:
            if record.type_name == record_name_bytes or (
                record.type and record.type.long_name == record_name
            ):
                id_name = record.prop("NAME", "name").lower()
                str_name = record.prop("FNAM", "name").lower()
                if id_name == name_input_bytes or str_name == name_input_bytes:
                    return record
        return None
    def iter_records_with_name(self, name):
        name_bytes = get_bytes(name)
        for record in self.records:
            if record.type_name == name_bytes or (
                record.type and record.type.long_name == name
            ):
                yield record
    def __getitem__(self, name):
        return list(self.iter_records_with_name(name))

class Record(object):
    def __init__(self,
        record_type, record_type_name, unknown_flag, flag_bits, sub_records
    ):
        self.type = record_type
        self.type_name = get_bytes(record_type_name)
        self.unknown_flag = unknown_flag
        self.flag_bits = flag_bits
        self.sub_records = sub_records
    def iter_sub_records_with_name(self, name):
        name_bytes = get_bytes(name)
        for sub_record in self.sub_records:
            if sub_record.type_name == name_bytes or (
                sub_record.type and sub_record.type.long_name == name
            ):
                yield sub_record
    def prop(self, sub_record_name, field_name=None):
        for sub_record in self.iter_sub_records_with_name(sub_record_name):
            if field_name is None:
                return sub_record
            else:
                return sub_record[field_name]
        return None
    def __getitem__(self, name):
        return list(self.iter_sub_records_with_name(name))

class SubRecord(object):
    def __init__(self, sub_record_type, sub_record_type_name, fields):
        self.type = sub_record_type
        self.type_name = get_bytes(sub_record_type_name)
        self.fields = fields
    def get_field_with_name(self, name):
        for field in self.fields:
            if field.type.name == name:
                return field
        return None
    def __getitem__(self, name):
        if is_number(name):
            return self.fields[name]
        else:
            field = self.get_field_with_name(name)
            return field.value if field else None

class SubRecordField(object):
    def __init__(self, sub_record_field_type, value):
        self.type = sub_record_field_type
        self.value = value

class RecordType(object):
    def __init__(self, name, long_name, sub_record_types):
        self.name = get_bytes(name)
        self.long_name = long_name
        self.sub_record_types = sub_record_types
    def get_sub_record_type(self, name, byte_length):
        for sub_record_type in self.sub_record_types:
            if sub_record_type.name == get_bytes(name) and (
                sub_record_type.required_size is None or
                sub_record_type.required_size == byte_length
            ):
                return sub_record_type
        return None

class SubRecordType(object):
    def __init__(self, name, long_name, fields, required_size=None):
        self.name = get_bytes(name)
        self.long_name = long_name
        self.fields = fields
        self.required_size = required_size

class SubRecordTypeField(object):
    def __init__(self, byte_length, name, data_type):
        self.name = name
        self.byte_length = byte_length
        self.data_type = data_type
    @staticmethod
    def repeat(count, type_fields):
        field_list = []
        for i in range(count):
            for type_field in type_fields:
                field_list.append(SubRecordTypeField(
                    name=("%s_%s" % (type_field.name, i + 1)),
                    data_type=type_field.data_type,
                    byte_length=type_field.byte_length,
                ))
        return field_list
