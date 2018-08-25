import sys

from get_terminal_size import get_terminal_size

def update_load_progress(path):
    def fn(es_file, record):
        loaded_records_num = len(es_file.records)
        if not record or loaded_records_num <= 4 or loaded_records_num % 500 == 0:
            first = es_file.records[0]
            total_records_num = first.prop("header", "num_records")
            percent = int(100 * loaded_records_num / total_records_num)
            cols = get_terminal_size().columns
            max_path_len = cols - 20
            show_path = path
            if len(show_path) > max_path_len:
                show_path = ".." + show_path[-max_path_len + 2:]
            sys.stdout.write("\r[%s%%] Loading \"%s\"" % (
                str(percent).rjust(3), show_path
            ))
            sys.stdout.flush()
    return fn
