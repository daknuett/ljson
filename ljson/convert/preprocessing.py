from ..base.generic import get_ljson_type_from_python, get_ljson_type_from_loaded
from ..base.preprocessing import nothing_to_do, dump_json, dump_bytes, load_json, load_bytes

dump_functions_csv = {
	"int": nothing_to_do,
	"str": nothing_to_do,
	"float": nothing_to_do,
	"bool": nothing_to_do,
	"json": dump_json,
	"bytes": dump_bytes,
}
load_functions_csv = {
	"int": nothing_to_do,
	"str": nothing_to_do,
	"float": nothing_to_do,
	"bool": nothing_to_do,
	"json": load_json,
	"bytes": load_bytes,
}

def make_ready_for_csv(item, item_name, header):
	ljson_type = get_ljson_type_from_python(item, item_name, header)

	return dump_functions_csv[ljson_type](item)

def make_csv_postload(item, item_name, header):
	ljson_type = get_ljson_type_from_loaded(item, item_name, header)

	return load_functions_csv[ljson_type](item)


