#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

from prometheus_client import start_http_server, Gauge
import psutil
import platform
import time

NODE_HEALTH = Gauge('node_health', 'Overall node health status (1 = healthy, 0 = unhealthy)')
COMPONENT_HEALTH = Gauge('component_health', 'Component health status', ['component', 'detail'])

MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage percentage')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage percentage')
SWAP_USAGE = Gauge('swap_usage_percent', 'Swap usage percentage')
LOAD_AVERAGE = Gauge('load_average', 'System load average (1 minute)')

class NodeHealthExporter:
    def __init__(self):
        self.thresholds = {
            'memory': 90,
            'cpu': 80,
            'disk': 85,
            'swap': 50,
            'load': 5,
        }
        self.hostname = platform.node()
        
    def check_memory(self):
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.percent)
        is_healthy = memory.percent < self.thresholds['memory']
        status = f"{memory.percent:.1f}% used (threshold: {self.thresholds['memory']}%)"
        return is_healthy, status

    def check_cpu(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)
        is_healthy = cpu_percent < self.thresholds['cpu']
        status = f"{cpu_percent:.1f}% used (threshold: {self.thresholds['cpu']}%)"
        return is_healthy, status

    def check_disk(self):
        disk = psutil.disk_usage('/')
        DISK_USAGE.set(disk.percent)
        is_healthy = disk.percent < self.thresholds['disk']
        status = f"{disk.percent:.1f}% used (threshold: {self.thresholds['disk']}%)"
        return is_healthy, status

    def check_swap(self):
        swap = psutil.swap_memory()
        SWAP_USAGE.set(swap.percent)
        is_healthy = swap.percent < self.thresholds['swap']
        status = f"{swap.percent:.1f}% used (threshold: {self.thresholds['swap']}%)"
        return is_healthy, status

    def check_load(self):
        cpu_count = psutil.cpu_count()
        load_avg = psutil.getloadavg()[0]
        LOAD_AVERAGE.set(load_avg)
        is_healthy = load_avg < (cpu_count * self.thresholds['load'])
        status = f"Load: {load_avg:.1f} (threshold: {cpu_count * self.thresholds['load']})"
        return is_healthy, status

    def run_checks(self):
        while True:
            try:
                for item in COMPONENT_HEALTH._metrics.copy():
                    COMPONENT_HEALTH.remove(*item)

                checks = {
                    'memory': self.check_memory(),
                    'cpu': self.check_cpu(),
                    'disk': self.check_disk(),
                    'swap': self.check_swap(),
                    'load': self.check_load()
                }

                all_healthy = True
                for component, (is_healthy, status) in checks.items():
                    COMPONENT_HEALTH.labels(
                        component=component,
                        status=status
                    ).set(1 if is_healthy else 0)
                    
                    if not is_healthy:
                        all_healthy = False

                NODE_HEALTH.set(1 if all_healthy else 0)
                
                time.sleep(10)

            except Exception as e:
                time.sleep(10)

if __name__ == '__main__':
    port = 9101
    start_http_server(port)
    
    exporter = NodeHealthExporter()
    exporter.run_checks()
