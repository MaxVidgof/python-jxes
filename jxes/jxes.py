from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.log.obj import EventLog, Trace, Event, EventStream
from io import BytesIO, StringIO
import json
from datetime import datetime,timezone
import tqdm
import re
from tqdm.auto import tqdm

#ENCODING = "utf-8"

# load -from stream or file; loads - from stirng
# dump -to stream or file; dumps - to string

timestamp_pattern = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[\+\-]\d{2}:\d{2})?$'
)


def get_attr_value(value):
	if type(value) == datetime:
		return value.isoformat()
	else:
		return value

def export_attribute(attr_name, attr_value):
	if attr_name is None or attr_value is None:
		return {}
#	if not attr_type == xes_util.TAG_LIST:
#	else:

#	if type(attr_value) == list:
		# list
#		return {attr_name:[export_attributes(item)]}
	if type(attr_value) == dict:
		if attr_value["value"] is None:
			print(attr_value["children"])
			if type(attr_value["children"])==list:
				# list
				return {attr_name:[export_attribute(k,v) for (k,v) in attr_value["children"]]}
			else:
				# container
				return {attr_name:{key:value for (k,v) in attr_value["children"] for key,value in export_attribute(k,v).items()}}

		else:
			# nested attribute
			return {attr_name: {"value": attr_value["value"], "nested-attributes":{key:value for k,v in attr_value["children"].items() for key,value in export_attribute(k,v).items()}}}

	return {attr_name:get_attr_value(attr_value)}


def extract_trace(trace):
	out_trace = {"attrs":{}, "events":[]}
	for attr_name, attr_value in trace.attributes.items():
		out_trace["attrs"].update(export_attribute(attr_name,attr_value))
	for event in trace:
		out_trace["events"].append({key:value for attr_name, attr_value in event.items() for key,value in export_attribute(attr_name,attr_value).items()})
	return out_trace

def log_to_jxes(log):
	progress = None

	jxes_log = {}
	jxes_log["log-properties"] = {}
	jxes_log["log-properties"]["xes.version"] = "1849-2023" # todo: fix
	jxes_log["log-properties"]["xes.features"] = "nested-attributes"

	jxes_log["log-attrs"] = {}
	for attr_name, attr_value in log.attributes.items():
		jxes_log["log-attrs"].update(export_attribute(attr_name,attr_value))

	jxes_log["extensions"] = []
	for ext_name, ext_value in log.extensions.items():
		jxes_log["extensions"].append({"name":ext_name,"prefix":ext_value[xes_util.KEY_PREFIX],"uri":ext_value[xes_util.KEY_URI]})

	jxes_log["global-attrs"] = {}
	for scope in log.omni_present:
		jxes_log["global-attrs"][scope] = {}
		for attr_name, attr_value in log.omni_present[scope].items():
			jxes_log["global-attrs"][scope].update(export_attribute(attr_name,attr_value))

	jxes_log["classifiers"] = {}
	for clas_name, clas_attributes in log.classifiers.items():
		jxes_log["classifiers"][clas_name] = [str(attr) for attr in clas_attributes]

	if type(log)==EventLog:
		progress = tqdm(total=len(log), desc="processing log, completed traces :: ")
		jxes_log["traces"] = []
		for trace in log:
			jxes_log["traces"].append(extract_trace(trace))
			if progress is not None:
				progress.update()
	elif type(log)==EventStream:
		progress = tqdm(total=len(log), desc="processing stream, completed events :: ")
		jxes_log["events"] = []
		for event in log:
			jxes_log["events"].append({key:value for attr_name, attr_value in event.items() for key,value in export_attribute(attr_name,attr_value).items()})
			if progress is not None:
				progress.update()
	else:
		raise ValueError(f"Unsupported event log type: {type(log)}. Supported types: 'pm4py.objects.log.obj.EventStream and pm4py.objects.log.obj.EventLog")
	if progress is not None:
		progress.close()
	del progress

	return jxes_log

def write_log(log, f):
	#f.write("test") #.encode(encoding))
	json.dump(log_to_jxes(log),f,indent='\t')
	return f

def write_jxes(log, filename):
	with open(filename, 'w') as f:
		write_log(log,f)

def parse_attr_value(value):
	if (type(value) == str) and timestamp_pattern.match(value):
		return datetime.fromisoformat(value)
	return value

def import_attributes(attributes: dict):
	out_dict = dict()
	for attr_name, attr_value in attributes.items():
		if type(attr_value) == list:
			# list
			out_dict[attr_name] = {"value":None,"children":[]}
			for child in attr_value:
				(child_attr_name, child_attr_value), = child.items()
				out_dict[attr_name]["children"].append((child_attr_name,parse_attr_value(child_attr_value)))
		elif type(attr_value) == dict:
			out_dict[attr_name] = {"value":None,"children":None}
			if "value" in attr_value:
				# nested attribute
				out_dict[attr_name]["value"] = parse_attr_value(attr_value["value"])
				out_dict[attr_name]["children"] = dict()
				for child_attr_name, child_attr_value in import_attributes(attr_value["nested-attributes"]).items():
					out_dict[attr_name]["children"].update({child_attr_name:parse_attr_value(child_attr_value)})
			else:
				# container
				out_dict[attr_name]["children"] = set()
				for child_attr_name, child_attr_value in import_attributes(attr_value).items():
					out_dict[attr_name]["children"].add((child_attr_name,parse_attr_value(child_attr_value)))
		else:
			out_dict[attr_name] = parse_attr_value(attr_value)
	return out_dict

def jxes_to_log(jxes_log):
	progress = None
	if "traces" in jxes_log:
		log = EventLog()
	else:
		log = EventStream()
	trace = None
	event = None
	if "log-properties" in jxes_log:
		pass
	if "log-attrs" in jxes_log:
		for attr_name, attr_value in import_attributes(jxes_log["log-attrs"]).items():
			log.attributes[attr_name] = parse_attr_value(attr_value)
	if "extensions" in jxes_log:
		for extension in jxes_log["extensions"]:
			log.extensions[extension["name"]] = {xes_util.KEY_PREFIX:extension["prefix"], xes_util.KEY_URI:extension["uri"]}
	if "global-attrs" in jxes_log:
		for scope in jxes_log["global-attrs"]:
			log.omni_present[scope] = {}
			for attr_name, attr_value in import_attributes(jxes_log["global-attrs"][scope]).items():
				log.omni_present[scope][attr_name] = parse_attr_value(attr_value)
	if "classifiers" in jxes_log:
		for clas_name, clas_attributes in jxes_log["classifiers"].items():
			log.classifiers[clas_name] = clas_attributes.copy()
	if "traces" in jxes_log:
		progress = tqdm(total=len(jxes_log["traces"]), desc="reading log, completed traces :: ")
		for jxes_trace in jxes_log["traces"]:
			trace = Trace()
			for attr_name, attr_value in jxes_trace["attrs"].items():
				trace.attributes[attr_name] = parse_attr_value(attr_value)
			for jxes_event in jxes_trace["events"]:
				event = Event(import_attributes(jxes_event))
				#{attr_name: parse_attr_value(attr_value) for attr_name, attr_value in jxes_event.items()}
				trace.append(event)
			log.append(trace)
			if progress is not None:
				progress.update()

	if "events" in jxes_log:
		progress = tqdm(total=len(jxes_log["events"]), desc="reading stream, completed events :: ")
		for jxes_event in jxes_log["events"]:
			event = Event(import_attributes(jxes_event))
			log.append(event)
			if progress is not None:
				progress.update()

	if progress is not None:
		progress.close()
	del progress
	return log

def read_log(f,file_size=None):
	return jxes_to_log(json.load(f))

def read_jxes(filename):
	with open(filename, 'r') as f:
		log = read_log(f)
	return log

#file_size = os.stat(filename).st_size

if __name__=="__main__":
	from pm4py import read_xes, write_xes
	import sys
	filename = sys.argv[1]
	if filename.endswith(".xes"):
		log = read_xes(filename, return_legacy_log_object=True, variant='iterparse_20')
		# Output to file
		with open(filename.replace(".xes",".jxes"), "w") as w:
			write_log(log,w)
	elif filename.endswith(".jxes"):
		with open(filename,'r') as f:
			out_log = read_log(f)
		write_xes(out_log,'ttt.xes')
	else: print("Error")

	#encoding = ENCODING
	#b = BytesIO()
	#b.write("test".encode(encoding))
	#print(b.getvalue().decode(encoding))

	# Output to stdout
	#s = StringIO()
	#r = write_log(log,s)
	#print(r.getvalue()) #.decode(encoding))

__all__ = ["get_attr_value", "export_attribute", "extract_trace", "log_to_jxes",
	"write_log", "write_jxes", "parse_attr_value", "import_attributes",
	"jxes_to_log", "read_log", "read_jxes"]
