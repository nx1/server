import sys
from datetime import datetime
import socket
import psutil

class SystemInfo:
    def __init__(self):
        self.hostname        = socket.gethostname()
        self.boot_time       = datetime.fromtimestamp(psutil.boot_time())
        self.uptime          = datetime.now() - self.boot_time
        self.python_version  = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.connected_users = len(psutil.users())
        self.cpu_percent     = psutil.cpu_percent(interval=1)
        self.cpu_freq        = psutil.cpu_freq().current
        self.memory          = psutil.virtual_memory()
        self.mem_used        = self.memory.used / (1024 ** 3)
        self.mem_available   = self.memory.available / (1024 ** 3)
        self.mem_total       = self.memory.total / (1024 ** 3)
        self.mem_percent     = self.memory.percent
        self.temps           = psutil.sensors_temperatures()
        self.cpu_temp        = self.get_cpu_temp()
        self.disk            = psutil.disk_usage('/')
        self.disk_used       = self.disk.used / (1024 ** 3)
        self.disk_free       = self.disk.free / (1024 ** 3)
        self.disk_total      = self.disk.total / (1024 ** 3)
        self.disk_percent    = self.disk.percent
        self.net             = psutil.net_io_counters()
        self.net_sent        = self.net.bytes_sent / (1024 ** 2)
        self.net_recv        = self.net.bytes_recv / (1024 ** 2)
        self.net_con         = psutil.net_connections()

    def get_cpu_temp(self):
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps:
            return temps['cpu_thermal'][0].current
        else:
            return None

    def __repr__(self):
        return (
            f"Hostname:        {self.hostname}\n"
            f"Uptime:          {self.uptime.seconds/3600:.2f} h\n"
            f"Python Version:  {self.python_version}\n"
            f"Connected Users: {self.connected_users}\n"
            f"CPU Usage:       {self.cpu_percent}%\n"
            f"CPU Frequency:   {self.cpu_freq:.0f} MHz\n"
            f"CPU Temperature: {self.cpu_temp} °C\n"
            f"Memory:          {self.mem_used:.2f} / {self.mem_total:.2f} GB ({self.mem_percent:.2f}%)\n"
            f"Disk Space:      {self.disk_used:.2f} / {self.disk_total:.2f} GB ({self.disk_percent:.2f}%)\n"
            f"Disk Free:       {self.disk_free:.2f} GB\n"
            f"Network:         Up: {self.net_sent:.2f} Mb Down: {self.net_recv:.2f} Mb"
        )

if __name__ == "__main__":
    print(SystemInfo())