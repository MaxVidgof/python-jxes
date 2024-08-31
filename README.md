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

## Demo
A short demo video is available at [https://youtu.be/8adiYqeczAs](https://youtu.be/8adiYqeczAs).

## License
This package is distributed under Apache 2.0 license.

[1] M. B. S. Narayana, H. Khalifa, W. M. P. van der Aalst, JXES: JSON support for the XES event log standard, CoRR abs/2009.06363 (2020). URL: https://arxiv.org/abs/2009.06363. arXiv:2009.06363.
[2] "IEEE Standard for eXtensible Event Stream (XES) for Achieving Interoperability in Event Logs and Event Streams," in IEEE Std 1849-2023 (Revision of IEEE Std 1849-2016) , vol., no., pp.1-55, 8 Sept. 2023, doi: 10.1109/IEEESTD.2023.10267858. keywords: {IEEE Standards;Event detection;System analysis and design;Behavioral sciences;XML;event log;event stream;extensions;IEEE 1849™;system behavior;XML}.
