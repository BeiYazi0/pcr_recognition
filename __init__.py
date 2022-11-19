import asyncio
import random
import nonebot

import hoshino
from hoshino.typing import CQEvent
from hoshino import Service

from .recognition import pcr_matching
from .birth import check_birth, celebrate_birth, gift


sv_help = '''
[princess connect] + 图片(@xx)
'''.strip()
sv = Service('PCR匹配',help_=sv_help, bundle='娱乐')


@sv.on_prefix('princess connect')
async def matching(bot, ev: CQEvent): 
    content=ev.message
    code=content[0]["data"]
    if content[0]["type"]=='at':
        url = f"http://q1.qlogo.cn/g?b=qq&nk={code['qq']}&s=640"
    else:
        url = code.get("url")
    if url:
        forward_msg = await pcr_matching(url)
        await bot.send_group_forward_msg(group_id=ev.group_id, messages=forward_msg)
 
    
@sv.scheduled_job('cron', hour=10, minute=0)
async def birthday_daily_push():
    birth_msg_lst = celebrate_birth()
    if birth_msg_lst == []:
        return
    bot = hoshino.get_bot()
    glist = await sv.get_enable_groups()
    for gid, selfids in glist.items():
        sid = random.choice(selfids)
        for msg in birth_msg_lst:
            await bot.send_group_msg(self_id=sid, group_id=gid, message=msg)
        await asyncio.sleep(2)


async def birthday_daily_push_test():
    birth_msg_lst = celebrate_birth()
    if birth_msg_lst == []:
        return
    bot = hoshino.get_bot()
    glist = await sv.get_enable_groups()
    print(birth_msg_lst)
    for msg in birth_msg_lst:
        sid = random.choice(glist[780448247])
        await bot.send_group_msg(self_id=sid, group_id=780448247, message=msg)


@sv.on_rex("生日快乐")
async def birthday_bless(bot, ev: CQEvent):
    flag, charalst, birthlst = check_birth()
    if not flag:
        await birthday_daily_push()
        return
    if charalst == []:
        return
    gid = ev.group_id
    uid = ev.user_id
    content = ev.message.extract_plain_text()
    for i, val in enumerate(birthlst):
        if val in content:
            msg = gift(charalst[i], gid, uid)
            await bot.send(ev, msg, at_sender = True)
            break