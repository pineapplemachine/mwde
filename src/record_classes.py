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
    def iter_info_records(self, include_overwritten=False):
        num_files = len(self.es_files)
        for i in range(num_files):
            es_file = self.es_files[i]
            for record in es_file.records:
                if record.type_name != b"INFO":
                    continue
                if len(record["DELE"]):
                    continue # Deletion of dialog from a previous file
                is_overwritten = False
                for later_file in self.es_files[i + 1:]:
                    if record.id_number in later_file.info_id_map:
                        is_overwritten = True
                        later_record = later_file.info_id_map[record.id_number]
                        record.overwritten_by_record = later_record
                        break
                if is_overwritten and not include_overwritten:
                    continue
                yield record
    def get_faction_rank_name(self, faction_name, rank_index):
        if rank_index < 0:
            return None
        faction_record = self.get_record_by_name_id(b"FACT", faction_name)
        if faction_record:
            rank_names = faction_record[b"RNAM"]
            if rank_index < len(rank_names):
                return rank_names[rank_index][0].value
            else:
                return None
    def get_record_by_name_id(self, record_name, name_id):
        for es_file in self.es_files[::-1]:
            record = es_file.get_record_by_name_id(record_name, name_id)
            if record:
                return record
        return None
    def get_info_record_by_id(self, info_id):
        for es_file in self.es_files[::-1]:
            record = es_file.get_info_record_by_id(info_id)
            if record:
                return record
        return None
    def get_record_by_name_input(self, record_name, name_input):
        for es_file in self.es_files[::-1]:
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
    def __init__(self, path, records, info_id_map=None):
        self.path = path
        self.records = records
        self.info_id_map = info_id_map if info_id_map else {}
        self.record_name_map = {}
    # Associate INFO records with their preceding DIAL records
    # Build a map of INFO by ID, this will be used by ESData to detect
    # records from this ESM overwritten in one later in the load order
    # Map various records by name
    def process_data(self):
        last_dialog_topic_record = None
        for record in self.records:
            if record.type_name == b"DIAL":
                last_dialog_topic_record = record
            elif record.type_name == b"INFO":
                record.dialog_topic_record = last_dialog_topic_record
                id_number_string = record.prop("info_id", "info_id")
                if id_number_string:
                    record.id_number = int(id_number_string)
                    self.info_id_map[record.id_number] = record
                else:
                    record.id_number = None
            elif record.type_name in (b"FACT", b"NPC_", b"CELL"):
                name_record = record.prop(b"NAME")
                if name_record:
                    self.record_name_map[name_record[0].value] = record
    def get_record_by_name_id(self, record_name, name_id):
        record_name_bytes = get_bytes(record_name)
        name_id_bytes = get_bytes(name_id)
        record = self.record_name_map.get(name_id_bytes)
        if record and (record.type_name == record_name_bytes or (
            record.type and record.type.long_name == record_name
        )):
            return record
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
    def get_info_record_by_id(self, info_id):
        return self.info_id_map.get(info_id)
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
        es_file, record_type, record_type_name,
        unknown_flag, flag_bits, sub_records
    ):
        self.es_file = es_file
        self.type = record_type
        self.type_name = get_bytes(record_type_name)
        self.unknown_flag = unknown_flag
        self.flag_bits = flag_bits
        self.sub_records = sub_records
        self.dialog_topic_record = None # Populated later for INFO records
        self.overwritten_by_record = None # Populated later for INFO records
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
