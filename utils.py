def to_gb(bytes_value):
    return round(bytes_value / (1024**3), 2)

def uptime_to_str(seconds):
    d = seconds // 86400
    h = (seconds % 86400) // 3600
    m = (seconds % 3600) // 60
    return f"{d}d {h}h {m}m"
