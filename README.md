# Python-JXES: Python Implementation of JSON Serialization for XES Standard
This package implements [JXES](https://arxiv.org/abs/2009.06363) [1] in Python. JXES is a JSON-based serialization format for the [XES](https://www.tf-pm.org/resources/xes-standard) standard [2].

## Installation
```bash
pip install jxes
```

## Usage
The interface is compatible with [PM4Py]()
```python
from jxes import read_jxes, write_jxes
# read log
log = read_jxes('filename.jxes')
# write log
write_jxes(log, 'filename.jxes')
```

#### More examples
##### 1. Reading XES logs and storing them as JXES
Read XES log using PM4Py. Either read as legacy log object directly:
```python
import pm4py
log = pm4py.read_xes(filename, return_legacy_log_object=True)
type(log)
# <class 'pm4py.objects.log.obj.EventLog'>
```
or convert existing event log to legacy format:
```python
import pm4py
log_df = pm4py.read_xes(filename)
type(log_df)
# <class 'pandas.core.frame.DataFrame'>
log = pm4py.convert_to_event_log(log_df)
type(log)
# <class 'pm4py.objects.log.obj.EventLog'>
```
To use XES 2.0 features like containers, use a corresponding configuration for PM4Py reader, JXES supports them too!
```python
log = pm4py.read_xes(filename, return_legacy_log_object=True, variant="iterparse_20")
```
Now, you can store your log file as JXES:
```python
import jxes
jxes.write_jxes(log, 'filename.jxes')
```
##### 2. Reading JXES logs and working with them in PM4Py
Simply read a legacy log object:
```python
import jxes
log = read_jxes(filename)
type(log)
# <class 'pm4py.objects.log.obj.EventLog'>
```
You can then use the legacy log in PM4Py directly or convert it to the new tabular format:
```python
import pm4py
log_df = pm4py.convert_to_dataframe(log)
type(log_df)
# <class 'pandas.core.frame.DataFrame'>
```
##### 3. Working with event streams
JXES supports PM4Py event streams out of the box with zero configuration! You can just store existing event stream object in JXES:
```python
type(stream)
# <class 'pm4py.objects.log.obj.EventStream'>
jxes.write_jxes(stream, 'filename.jxes')
```
Similarly, you can import JXES stream into PM4Py:
```python
stream = jxes.read_jxes(filename)
type(stream)
# <class 'pm4py.objects.log.obj.EventStream'>
```


## Demo
A short demo video is available at [https://youtu.be/8adiYqeczAs](https://youtu.be/8adiYqeczAs).

## License
This package is distributed under Apache 2.0 license.

[1] M. B. S. Narayana, H. Khalifa, W. M. P. van der Aalst, JXES: JSON support for the XES event log standard, CoRR abs/2009.06363 (2020). URL: https://arxiv.org/abs/2009.06363. arXiv:2009.06363.

[2] "IEEE Standard for eXtensible Event Stream (XES) for Achieving Interoperability in Event Logs and Event Streams," in IEEE Std 1849-2023 (Revision of IEEE Std 1849-2016) , vol., no., pp.1-55, 8 Sept. 2023, doi: 10.1109/IEEESTD.2023.10267858. keywords: {IEEE Standards;Event detection;System analysis and design;Behavioral sciences;XML;event log;event stream;extensions;IEEE 1849™;system behavior;XML}.
