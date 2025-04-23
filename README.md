# COSC364 RIP Assignment
An implementation of parts of the RIP routing protocol, designed to run as several
instances on the same machine. Each instance runs as a separate process, and these
processes communicate through local sockets. Designed for emulation of a small network,
and exploring the response of the RIP protocol to different types of faults.

## Usage
1. Populate config files. For examples, see [/config](config).

2. Start the 'routers'. For each config file, run the below: 
```python3
python3 main.py /path/to/config.ini
```