"""
The signals used in Bifrost
"""
from bifrost.signals.manager import SignalManager

service_started = object()
service_stopped = object()

data_sent = object()
data_received = object()

email_sent = object()
