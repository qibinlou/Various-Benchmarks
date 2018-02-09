import os
import time
import threading
import multiprocessing
import concurrent.futures

import gevent
import gevent.pool

NUM_WORKERS = os.cpu_count()


def only_sleep(unused_arg=None):
    """ Do nothing, wait for a timer to expire """
    print("PID: %s, Process Name: %s, Thread Name: %s" % (
        os.getpid(),
        multiprocessing.current_process().name,
        threading.current_thread().name)
          )
    time.sleep(1)


def only_sleep_gevent(unused_arg=None):
    """ Do nothing, wait for a timer to expire """
    print("PID: %s, Process Name: %s, Thread Name: %s" % (
        os.getpid(),
        multiprocessing.current_process().name,
        threading.current_thread().name)
          )
    gevent.sleep(1)


def crunch_numbers(unused_arg=None):
    """ Do some computations """
    print("PID: %s, Process Name: %s, Thread Name: %s" % (
        os.getpid(),
        multiprocessing.current_process().name,
        threading.current_thread().name)
          )
    x = 0
    while x < 100000000:
        x += 1
    return x


def test_sleep():
    print("\n\ntesting sleep...")
    ## Run tasks serially
    start_time = time.time()
    for _ in range(NUM_WORKERS):
        only_sleep()
    end_time = time.time()
    print("Serial time=", end_time - start_time, '\n')

    # Run tasks using threads
    start_time = time.time()
    threads = [threading.Thread(target=only_sleep) for _ in range(NUM_WORKERS)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    end_time = time.time()
    print("Threads time=", end_time - start_time, '\n')

    # Run tasks using concurrent futures
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(only_sleep, arg) for arg in range(NUM_WORKERS)}
        concurrent.futures.wait(futures)
    end_time = time.time()
    print("Concurrent future time=", end_time - start_time, '\n')

    # Run tasks using process pool
    start_time = time.time()
    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        results = pool.map(only_sleep, range(NUM_WORKERS))
        # results.wait()
    end_time = time.time()
    print("Process pool time=", end_time - start_time, '\n')

    # Run tasks using processes
    start_time = time.time()
    processes = [multiprocessing.Process(target=only_sleep()) for _ in range(NUM_WORKERS)]
    [process.start() for process in processes]
    [process.join() for process in processes]
    end_time = time.time()
    print("Parallel time=", end_time - start_time, '\n')

    start_time = time.time()
    pool = gevent.pool.Pool(NUM_WORKERS)
    for arg in range(NUM_WORKERS):
        pool.spawn(only_sleep_gevent, arg)
    pool.join()
    end_time = time.time()
    print("gevent poll time=", end_time - start_time, '\n')


def test_crunch():
    print("\n\ntesting crunch...")
    start_time = time.time()
    for _ in range(NUM_WORKERS):
        crunch_numbers()
    end_time = time.time()
    print("Serial time=", end_time - start_time, '\n')

    start_time = time.time()
    threads = [threading.Thread(target=crunch_numbers) for _ in range(NUM_WORKERS)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    end_time = time.time()
    print("Threads time=", end_time - start_time, '\n')

    # Run tasks using concurrent futures
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(crunch_numbers, arg) for arg in range(NUM_WORKERS)}
        concurrent.futures.wait(futures)
    end_time = time.time()
    print("Concurrent future time=", end_time - start_time, '\n')

    # Run tasks using process pool
    start_time = time.time()
    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        results = pool.map_async(crunch_numbers, range(NUM_WORKERS))
        results.wait()
    end_time = time.time()
    print("Process pool time=", end_time - start_time, '\n')

    start_time = time.time()
    processes = [multiprocessing.Process(target=crunch_numbers) for _ in range(NUM_WORKERS)]
    [process.start() for process in processes]
    [process.join() for process in processes]
    end_time = time.time()
    print("Parallel time=", end_time - start_time, '\n')

    start_time = time.time()
    pool = gevent.pool.Pool(NUM_WORKERS)
    pool.map(crunch_numbers, range(NUM_WORKERS))
    pool.kill()
    end_time = time.time()
    print("gevent poll time=", end_time - start_time, '\n')


def main():
    test_sleep()
    test_crunch()


if __name__ == '__main__':
    main()
