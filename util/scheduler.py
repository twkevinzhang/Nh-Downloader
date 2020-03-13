import math
from threading import Thread

from util.logger import logger


class Scheduler():
    def __init__(self,start,end,thread_cnt,queue,function, wait_other_thread):
        threads=[]
        r=end-start+1
        if thread_cnt < r:
            fragment = math.ceil(r / thread_cnt)
            big_trd = r % thread_cnt
            for i in range(big_trd):
                f_start = i * fragment + start
                f_end = (i + 1) * fragment + start
                threads.append(Thread(target=lambda q, start2,end2: q.put(function(start2,end2)), args=(queue, f_start,f_end)))

            fragment -= 1
            small_trd = thread_cnt - big_trd
            for i in range(big_trd, big_trd + small_trd):
                f_start = i * fragment + big_trd + start
                f_end = (i + 1) * fragment + big_trd + start
                threads.append(Thread(target=lambda q, start2,end2: q.put(function(start2,end2)), args=(queue, f_start,f_end)))
        else:
            thread_cnt = r
            for i in range(thread_cnt):
                f_start = start+i
                f_end = f_start+1
                threads.append(Thread(target=lambda q, start2,end2: q.put(function(start2,end2)), args=(queue, f_start,f_end)))

        for t in threads:
            try:
                t.start()
            except Exception as e:
                logger(e)

        for t in threads:
            t.join()

        if wait_other_thread:
            for i in threads:
                i.join()
