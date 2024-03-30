import time 
from datetime import datetime

def timer(fn):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = fn(*args, **kwargs)
        end_time = time.perf_counter()
        duration = (end_time - start_time)
        print(f"  Took {duration:0.4f} s")
        return result
    return wrapper

def every_new_day(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                current_time = datetime.now().time()
                if current_time.hour == 0 and current_time.minute == 0:
                    func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            time.sleep(60)
    return wrapper

def every_x_minutes(x):
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"An error occurred: {e}")
                time.sleep(x * 60)
        return wrapper
    return decorator