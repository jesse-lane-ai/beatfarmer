import time
import threading

def time_function_execution(func, *args):
    results = {}  # To store the result of the function

    # This function will be run in a separate thread
    def target_function():
        results["output"] = func(*args)
        event.set()  # Signal the main thread that the function has finished

    event = threading.Event()
    thread = threading.Thread(target=target_function)
    
    # Start the thread
    thread.start()

    start_time = time.time()
    try:
        # This loop keeps running and updating the terminal with elapsed time
        while not event.is_set():
            elapsed_time = time.time() - start_time
            print(f"\rThe function has been running for {elapsed_time:.2f} seconds", end="")
            time.sleep(1)  # Update every second
    except KeyboardInterrupt:
        print("\nInterrupted!")
        return None

    thread.join()
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nThe function took {duration:.2f} seconds to complete.")
    return results.get("output")
