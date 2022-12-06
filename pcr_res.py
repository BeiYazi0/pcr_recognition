import os
import random
import json

from .duel_data import CHARA_PROFILE


_dir = os.path.dirname(__file__)


def label2pcridx(idx: int):
    ids = list(CHARA_PROFILE.keys())
    pcridx = ids[idx]
    return pcridx


def render_forward_msg(msg_list: list, uid=2854196306, name='小冰'):
	forward_msg = []
	for msg in msg_list:
		forward_msg.append({
			"type": "node",
			"data": {
				"name": str(name),
				"uin": str(uid),
				"content": msg
			}
		})
	return forward_msg


def birth_text(idx: int, line: int):
    file = os.path.join(_dir, f"res\\pcr_text\\birthday\\{idx}.txt")
    with open(file, 'rt', encoding='utf_8') as f:
        res = f.readlines()
    if line==0:
        text = res[0]
    else:
        text = random.choice(res[1:])
    return text


def birth_card(idx: int):
    card = os.path.join(_dir, f"res\\pcr_img\\birthday\\{idx}.png")
    name = CHARA_PROFILE[idx]["名字"]
    cv = CHARA_PROFILE[idx]["声优"]
    img = f"[CQ:image,file=file:///{card}]"
    return name, cv, img


def pcr_img(idx: int):
    file_dir = os.path.join(_dir, f"res\\pcr_img\\{idx}")
    img_list = os.listdir(file_dir)
    jpg_file = random.choice(img_list)
    file = os.path.join(file_dir, jpg_file)
    name = CHARA_PROFILE[idx]["名字"]
    img = f"[CQ:image,file=file:///{file}]"
    return name, img


def pcr_audio(idx: int):
    text_file = os.path.join(_dir, f"res\\pcr_text\\{idx.txt}")
    if not os.path.exists(text_file):
        return False, False

    f = open(text_file, 'rt', encoding='utf_8')
    temp = random.choice(f.readlines())
    f.close()
    audio_file, text = temp.strip().split('|')

    file = os.path.join(_dir, f"res\\pcr_audio\\{idx}\\{audio_file}")
    audio = f"[CQ:record,file=file:///{file}]"
    return text, audio
        

def desc_info(idx: int, p:float):
    idx = label2pcridx(idx)
    name, img = pcr_img(idx)
    p = "%.2f%%"%(p*100)
    msg_list = [f"你有{p}的可能在找{name} {img}"]

    profile = CHARA_PROFILE[idx]
    kws = list(profile.keys())
    kws.remove('名字')
    random.shuffle(kws)
    kws = kws[:4]
    for i, k in enumerate(kws):
        msg_list.append(f"她的{k}是 {profile[k]}")

    msg = render_forward_msg(msg_list)
    return msg


def pcr_dynamic():
    url='https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history'
    params={'host_uid':353840826}
    res=requests.get(url,params)
    r=res.json()['data']["cards"][0]
    source='https://t.bilibili.com/'+r["desc"]["dynamic_id_str"]
    with open(_dir+'dynamic_id.txt','rt',encoding='utf_8') as f:
        url=f.read()
    if url == source:
        return None
    else:
        with open(_dir+'dynamic_id.txt','w',encoding='utf_8') as f:
            f.write(source)
    p=json.loads(r["card"])
    bot = hoshino.get_bot()
    try:
        text=p["item"]["description"]
        url=p["item"]["pictures"][0]["img_src"]
    except:
        try:
            p=json.loads(p["origin"])
            text=p["item"]["description"]
            url=p["item"]["pictures"][0]["img_src"]
        except:
            try:
                text=p["dynamic"]
                url=p["pic"]
            except:
                return 
    result='公主连结ReDive的bilibili动态:\n'+source+'\n------------\n'+text
    mycontent=f"{result} [CQ:image,file={url}]"
    return mycontent
