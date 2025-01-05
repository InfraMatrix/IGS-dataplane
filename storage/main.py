from .storage_manager import StorageManager

sm = StorageManager()

part = sm.disk_manager.create_partition(disk_name="/dev/sda", size_gb=1)

print(f"Created partition: {part}")
