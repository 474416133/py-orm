#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import asyncio

class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        print (cls._instance)
        if cls._instance == None:
            return super(Singleton, cls).__call__(*args, *kwargs)
        return cls._instance


import asyncio

class IDgen(object):
    """
    id生成器
    """

    def __init__(self):

        self.partion = 1
        self.partion_bit = 10
        self.seq_bit = 11
        self.max_seq = 1<<10
        self.seq = 0
        self.last_time = None

        self.time_bit_skip = self.partion_bit + self.seq_bit

    async def __call__(self):
        _loop = asyncio.get_event_loop()
        time_now = int(_loop.time())

        if self.last_time == time_now:
            if self.seq < self.max_seq:
                self.seq += 1

            else:
                await asyncio.sleep(0.1)
                _id = await self()
                return _id
        elif not self.last_time or self.last_time < time_now:
            self.last_time = time_now
            self.seq = 0

        return (time_now << self.time_bit_skip) + \
               (self.partion << self.seq_bit) + \
                self.seq


async def _f():
    count = 0
    idgen = IDgen()
    while 1:
        _id = await idgen()
        print("id:%s"%_id)
        if count > 11:
            break
        count += 1



if __name__ == "__main__":

    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    #idgen = IDgen()
    count = 0
    loop = asyncio.get_event_loop()
    task = loop.create_task(_f())
    loop.run_until_complete(task)
    print("========================")
    loop.run_forever()

    #print(len(s))