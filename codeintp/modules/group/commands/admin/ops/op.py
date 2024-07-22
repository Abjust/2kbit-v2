import random
from typing import Any

from arclet.alconna import Alconna, Arg, Arparma
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna

import constants
from codeintp.bot_utils import permission
from codeintp.bot_utils.datautil import factory
from codeintp.bot_utils.identify import identify

__plugin_meta__ = PluginMetadata(
    name="群管·本群下管",
    description="撤销某个人在本群的机器人管理员权限",
    usage=""
)

op = on_alconna(
    Alconna("op", Arg("target", Any)),
    priority=10,
    use_cmd_start=True
)


@op.handle()
async def handle_function(event: GroupMessageEvent, result: Arparma):
    datautil = factory.DataUtilFactory.create_data_util()
    target = str(identify(result.query("target")).strip())
    is_valid = target.isdigit()
    compared = permission.compare(str(event.sender.user_id), target, str(event.group_id))
    has_permission = compared[0] >= 1 or event.sender.role == "owner"
    in_ops = permission.is_group_admin(identify(result.query("target")), str(event.group_id))
    if is_valid and has_permission and not in_ops:
        columns = [
            ("recordid", "int", True),
            ("userid", "varchar(16)", False),
            ("groupid", "varchar(16)", False)
        ]
        datautil.initialize("ops", columns)
        # 分类讨论
        if constants.BotConstants.db_type in ["mysql", "sqlite"]:
            r = random.randint(100000, 999999)
            if datautil.is_here("ops", f"recordid_{r}"):
                while datautil.is_here("ops", f"recordid_{r}"):
                    r = random.randint(100000, 999999)
            obj = {
                "_key.recordid": r,
                "userid": target,
                "groupid": event.group_id
            }
            datautil.add("ops", obj)
        else:
            if not datautil.is_here("ops", f"userid_{target}"):
                obj = {
                    "_key.userid": target,
                    "groups": [str(event.group_id)]
                }
                datautil.add("ops", obj)
            else:
                obj1 = datautil.lookup("ops", f"userid_{target}")
                groups = obj1['groups']
                groups.append(str(event.group_id))
                modified_data = {
                    "groups": groups
                }
                datautil.modify("ops", f"userid_{target}", modified_data)
        permission.update_cache("ops")
        await op.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(f" 已将 {target} 设置为本群机器人管理员")
        ]))
    elif not has_permission:
        await op.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(" 无法设置本群机器人管理员：宁踏马有权限吗？（恼）")
        ]))
    elif in_ops:
        await op.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(" 无法设置本群机器人管理员：目标已经具备相应权限")
        ]))
    elif not is_valid:
        await op.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.sender.user_id),
            MessageSegment.text(" 无法设置本群机器人管理员：宁这是数字吗？（恼）")
        ]))
