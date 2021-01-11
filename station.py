import requests
import json
import asyncio
import nonebot
import hoshino
from hoshino import Service
from datetime import datetime

sv1 = Service('邦邦查询', enable_on_default=True)
sv2 = Service('车站推送', enable_on_default=False)


@sv1.on_suffix('车站人数')
async def query_number(bot, ev):
    resp = json.loads(requests.get('https://api.bandoristation.com/?function=get_online_number').content.decode('utf-8'))
    status = resp['status']
    if status == 'failure':
        sv1.logger.info('Api出错，请停用插件')
        await bot.finish(ev, '查询失败，请联系维护.', at_sender=True)
    else:
        res = resp['response']
        num = res['online_number']
        await bot.send(ev, f'车站目前有{num}人停留.')


@sv1.on_fullmatch(('查询房间', '查看房间', '房间查询'))
async def query_room(bot, ev):
    resp = json.loads(requests.get('https://api.bandoristation.com/?function=query_room_number').content.decode('utf-8'))
    status = resp['status']
    if status == 'failure':
        sv1.logger.info('Api出错，请停用插件')
        await bot.finish(ev, '查询失败，请联系维护.', at_sender=True)
    else:
        res = resp['response']
        if not res:
            await bot.finish(ev, '目前没有等待中的房间，请稍后查询.', at_sender=True)
        else:
            room = res[0]['number']
            putline = []
            if room:
                room = res[0]['number']
                raw_message = res[0]['raw_message']
                room_type = res[0]['type']
                if room_type == '25':
                    room_type = '25w room'
                elif room_type == '7':
                    room_type = '7w room'
                elif room_type == '12':
                    room_type = '12w room'
                elif room_type == '18':
                    room_type = '18w room'
                else:
                    room_type = 'Free room'
                time = datetime.fromtimestamp(res[0]['time'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                user_id = res[0]['user_info']['user_id']
                username = res[0]['user_info']['username']
                name = res[0]['source_info']['name']
                source_type = res[0]['source_info']['type']
                putline.append('--房间信息--')
                putline.append('房间号：{}'.format(room))
                putline.append('房间类型：{}'.format(room_type))
                putline.append('发布时间：{}'.format(time))
                putline.append('发布用户：{}({})'.format(username, user_id))
                putline.append('发布来源：{}({})'.format(name, source_type))
                putline.append('房间说明：{}'.format(raw_message))
            result = "\n".join(putline)
            await bot.send(ev, result)


@sv2.scheduled_job('interval', minutes=2)
async def query_schedule():
    bot = nonebot.get_bot()
    weihu = hoshino.config.SUPERUSERS[0]
    resp = json.loads(requests.get('https://api.bandoristation.com/?function=query_room_number').content.decode('utf-8'))
    status = resp['status']
    if status == 'failure':
        sv2.logger.info('Api出错，请停用插件')
        warn = 'BandoriStation api出错，请停用插件'
        await bot.send_private_msg(user_id=weihu, message=warn)
    else:
        res = resp['response']
        if not res:
            pass
        else:
            room = res[0]['number']
            putline = []
            if room:
                room = res[0]['number']
                raw_message = res[0]['raw_message']
                room_type = res[0]['type']
                if room_type == '25':
                    room_type = '25w room'
                elif room_type == '7':
                    room_type = '7w room'
                elif room_type == '12':
                    room_type = '12w room'
                elif room_type == '18':
                    room_type = '18w room'
                else:
                    room_type = 'Free room'
                time = datetime.fromtimestamp(res[0]['time'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                user_id = res[0]['user_info']['user_id']
                username = res[0]['user_info']['username']
                name = res[0]['source_info']['name']
                source_type = res[0]['source_info']['type']
                putline.append('--房间信息--')
                putline.append('房间号：{}'.format(room))
                putline.append('房间类型：{}'.format(room_type))
                putline.append('发布时间：{}'.format(time))
                putline.append('发布用户：{}({})'.format(username, user_id))
                putline.append('发布来源：{}({})'.format(name, source_type))
                putline.append('房间说明：{}'.format(raw_message))
            result = "\n".join(putline)
            for sid in hoshino.get_self_ids():
                gl = await bot.get_group_list(self_id=sid)
                gl = [ g['group_id'] for g in gl ]
                for g in gl:
                    await asyncio.sleep(0.5)
                    await bot.send_group_msg(self_id=sid, group_id=g, message=result)