
data = [
{
	"age": 42,
	"name": "peter",
	"lname": "griffin",
	"some_data": b"\0x45"
},
{
	"age": 41,
	"name": "louis",
	"lname": "griffin",
	"some_data": b"\0x45"
},
{
	"age": 12,
	"name": "chris",
	"lname": "griffin",
	"some_data": b"\0x45"
}
]

header_descriptor = {
	"age": {"type": "int", "modifiers": []},
	"name": {"type": "str", "modifiers": []},
	"lname": {"type": "str", "modifiers": []},
	"some_data": {"type": "bytes", "modifiers": []}
}

item_meg = {
	"age": 16,
	"name": "meg",
	"lname": "griffin",
	"some_data": b"\x67"
}
data_slapdash = [
{
	"test1": "foo",
	"test2": "bar",
	"test3": "baz"
},
{
	"test4": 4,
},
{
	"test1": "foo",
	"test2": "fool",
	"test4": 231,
	"some_bytes": b"\x89\x45asd"
},
{
	"test1": True,
	"test2": "baz"
}
]
