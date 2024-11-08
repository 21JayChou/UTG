from device import Device
from builder import Builder
from graph.utg import UTG
from datetime import datetime

start_time = datetime.now()
device = Device(start_time=start_time)
utg = UTG(device=device, start_time=start_time)
builder = Builder(device=device, utg=utg, max_step=100)
builder.build()
