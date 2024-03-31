import time 
from datetime import datetime, timedelta

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = (end_time - start_time)
        print(f"  Invoking {func.__name__}")
        print(f"  Took {duration:0.4f} s")
        return result
    return wrapper

def every_new_day(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                current_datetime = datetime.now()
                next_midnight = (current_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time_until_midnight = (next_midnight - current_datetime).total_seconds()
                time.sleep(time_until_midnight)
                func(*args, **kwargs)
                
            except Exception as e:
                print(f"An error occurred: {e}")
    
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