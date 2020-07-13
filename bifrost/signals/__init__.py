"""
The signals used in Bifrost
"""
from bifrost.signals.manager import SignalManager

service_started = object()
service_stopped = object()

email_sent = object()

connection_made = object()
connection_lost = object()
pause_writing = object()
resume_writing = object()
data_sent = object()
data_received = object()
eof_received = object()
