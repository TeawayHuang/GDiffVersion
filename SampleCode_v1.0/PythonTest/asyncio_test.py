import imp
import requests
import time
import asyncio

url = 'https://www.google.com.tw/'
loop = asyncio.get_event_loop()

start_time = time.time()

async def send_req(i, url):
    t = time.time()
    print(i, "Send a request at",t-start_time,"seconds.")

    res = await loop.run_in_executor(None, requests.get, url)

    t = time.time()
    print(i, "Receive a response at",t-start_time,"seconds.")

tasks = []

for i in range(10):
    task = loop.create_task(send_req(i, url))
    tasks.append(task)

loop.run_until_complete(asyncio.wait(tasks))

for i in range(20):
    task = loop.create_task(send_req(i, url))
    tasks.append(task)