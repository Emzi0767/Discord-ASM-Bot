import json
import asyncio
import multiprocessing as mp
import asmbotlauncher
import asmbot
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import CancelledError
from os import getenv, environ as env


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    asmbot.log("ASM version {} booting".format(asmbot.__version__), tag="ASM LDR")

    asmbot.log("Loading config", tag="ASM LDR")
    configName = f"/run/secrets/{env['DOCKER_SECRET']}" if getenv("DOCKER_SECRET") else "config.json"
    asmbot.log("Config will be loaded from {}".format(configName), tag="ASM LDR")
    with open(configName, "r") as f:
        cts = f.read()
        tkd = json.loads(cts)

    asmbot.log("Launching ASM", tag="ASM LDR")

    mp.set_start_method("spawn")
    executor = ThreadPoolExecutor(max_workers=int(tkd["shard_count"]))
    processes = []

    for i in range(0, int(tkd["shard_count"])):
        args = {
            "token": tkd["token"],
            "shard_id": i,
            "shard_count": int(tkd["shard_count"]),
            "script": tkd["script"],
            "guild_blacklist": tkd["guild_blacklist"],
            "guild_exempt_list": tkd["guild_exempt_list"]
        }

        loop.create_task(launch_process(executor, asmbotlauncher.initialize_asmbot, **args))

        if i != int(tkd["shard_count"]) - 1:
            loop.run_until_complete(asyncio.sleep(10))

    asmbot.log("Running", tag="ASM LDR")

    try:
        loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks(loop)))

    except KeyboardInterrupt:
        pass

    finally:
        asmbot.log("Shutting down", tag="ASM LDR")
        for process in processes:
            process.join()

    asmbot.log("Shutdown finalized", tag="ASM LDR")


def wait_for(process):
    process.join()


async def launch_process(executor, callback, **kwargs):
    try:
        while True:
            p = mp.Process(target=callback, kwargs=kwargs)
            p.start()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, wait_for, p)

    except CancelledError:
        pass

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
