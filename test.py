from IO import *
from Global import *

def new_level():
    if not In_100.value():
        return 4
    elif not In_75.value():
        return 3
    elif not In_50.value():
        return 2
    elif not In_25.value():
        return 1
    else:
        return 0

# For checking Changes in Tank Level
async def task_level():
    global level
    print("Level Check Task")
    while True:
        if new_level() != level:
            print(f"New Water Level Reading: {new_level()*25}%")
            await asyncio.sleep(1)
            if new_level() != level:
                await asyncio.sleep(1)
                if new_level() != level:
                    level = new_level()
                    print(f"Water Level is changed to {level*25}%")
        await asyncio.sleep(1)

async def task_main():
    print("started")
    asyncio.create_task(task_level())
    while True:
        print("Main Task")
        await asyncio.sleep(2)

asyncio.run(task_main())