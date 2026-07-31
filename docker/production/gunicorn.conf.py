import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker type
worker_class = "sync"

# Restart worker after serving these many requests
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 60
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = True

# Process naming
proc_name = "weather-tracker"

# Temporary directory
worker_tmp_dir = "/dev/shm"