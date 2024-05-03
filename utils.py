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
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                current_datetime = datetime.now()
                next_midnight = (current_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time_until_midnight = (next_midnight - current_datetime).total_seconds()
                time.sleep(time_until_midnight)
                func(*args, **kwargs)
                break
            except Exception as e:
                retry_count += 1
                time.sleep(60)
                print(f"An error occurred: {e}. Retrying...")
        else:
            print("Max retries reached. Update process failed.")
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

def convert_timestamp_to_iso8601(timestamp):
    if timestamp:
        try:
            date_obj_as_iso8601 = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z").isoformat()
            return date_obj_as_iso8601
        except ValueError:
            try:
                date_obj_as_iso8601 = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %Y").isoformat()
                return date_obj_as_iso8601
            except ValueError as e:
                print(f"An error occurred during timestamp conversion: {e}")
                return None
    else:
        return None