from arclet.alconna import Alconna
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna

from codeintp.bot_utils import permission

__plugin_meta__ = PluginMetadata(
    name="群管·列举全局黑名单",
    description="列举出所有全局被加黑的人",
    usage=""
)

blocklist = on_alconna(
    Alconna("blocklistg"),
    priority=10,
    use_cmd_start=True
)


@blocklist.handle()
async def handle_function(event: GroupMessageEvent):
    ops = [permission.cache["blocklist"][x] for x in range(len(permission.cache["blocklist"]))]
    qualified = [y for x in ops for y in x if "0" in x[y]['groups']]
    if len(qualified) > 0:
        await blocklist.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(f"\n全局黑名单：{str(qualified)}")
        ]))
    else:
        await blocklist.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(f" 当前还没有设置全局黑名单")
        ]))
