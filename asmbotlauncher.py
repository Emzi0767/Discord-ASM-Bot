import argparse
import asyncio
import asmbot

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asmbot.utils.log("Using uvloop event loops", tag="AIO INIT")
except ImportError:
    asmbot.utils.log("Using asyncio event loops", tag="AIO INIT")


class AsmBotLauncher:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = value

    def run(self, **kwargs):
        loop = self.loop

        # core bot config
        asmbot_shard = kwargs.get("shard_id", 0)
        asmbot_totalshards = kwargs.get("shard_count", 1)
        asmbot_token = kwargs.get("token", None)
        asmbot_script = kwargs.get("script", None)
        asmbot_blacklist = kwargs.get("guild_blacklist", [])
        asmbot_exempt_list = kwargs.get("guild_exempt_list", [])

        # init pam
        asmbot.log("Initializing ASM", tag="ASM")
        asmbot_config = {"shard_id": asmbot_shard, "shard_count": asmbot_totalshards}

        asmbot_bot = asmbot.AsmBot(asmbot_blacklist, asmbot_exempt_list, **asmbot_config)
        asmbot_bot.remove_command("help")

        asmbot_cmd = asmbot.AsmBotCommands(asmbot_bot)
        asmbot_cmd.script = asmbot_script
        asmbot_bot.add_cog(asmbot_cmd)

        try:
            asmbot.log("Shard {} logging in".format(asmbot_bot.shard_id), tag="SHARDMGR")

            loop.run_until_complete(asmbot_bot.login(asmbot_token))

            asmbot.log("Shard {} connecting".format(asmbot_bot.shard_id), tag="SHARDMGR")

            loop.run_until_complete(asmbot_bot.connect())

        except KeyboardInterrupt:
            pass

        finally:
            asmbot.log("Shard {} dying".format(asmbot_bot.shard_id), tag="SHARDMGR")

            loop.run_until_complete(asmbot_bot.logout())
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
                try:
                    loop.run_until_complete(task)
                except:
                    pass

            loop.close()

            asmbot.log("Shard {} died".format(asmbot_bot.shard_id), tag="SHARDMGR")


def initialize_asmbot(**kwargs):
    core = AsmBotLauncher()
    core.run(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--shard", type=int, dest="shard_id", help="Shard ID to connect with", default=0)
    parser.add_argument("-c", "--shard-count", type=int, dest="shard_count", help="Total shard count", default=1)
    parser.add_argument("-t", "--token", type=str, dest="token", help="Bot's token", default=None)
    parser.add_argument("-a", "--assembler-script", type=str, dest="script", help="Assembler script path", default=None)
    parser.add_argument("-b", "--guild-blacklist", type=str, dest="guild_blacklist", help="Guilds to blacklist", default=None)
    parser.add_argument("-x", "--guild-exempt-list", type=str, dest="guild_exempt_list", help="Guilds to exempt from blacklist checks", default=None)

    args = parser.parse_args()
    args = vars(args)

    blacklist = args.get("guild_blacklist", None)
    blacklist = blacklist or ""
    args["guild_blacklist"] = blacklist.split(",")

    exempt_list = args.get("guild_exempt_list", None)
    exempt_list = exempt_list or ""
    args["guild_exempt_list"] = exempt_list.split(",")

    initialize_asmbot(**args)
