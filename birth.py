import datetime
import os
import json
import random
import sqlite3

from .duel_data import birthdays, CHARA_PROFILE
from .pcr_res import birth_card, pcr_img, birth_text


_dir = os.path.dirname(__file__)
SCORE_DB_PATH = os.path.expanduser('~/.hoshino/pcr_running_counter.db')
DUEL_DB_PATH = os.path.expanduser('~/.hoshino/pcr_duel.db')
SCORE_DAILY_LIMIT = 3


class DuelCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_charatable()
        self._create_uidtable()
        self._create_leveltable()
        self._create_queentable()
        self._create_favortable()
        self._create_gifttable()
        self._create_warehousetable()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    def _create_charatable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS CHARATABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建角色表发生错误')

    def _create_uidtable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS UIDTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _create_leveltable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS LEVELTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _get_card_owner(self, gid, cid):
        try:
            r = self._connect().execute(
                "SELECT UID FROM CHARATABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找角色归属发生错误')

    def _set_card_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO CHARATABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_card_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM CHARATABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )
    
    def _get_card_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM CHARATABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}

    def _get_level(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT LEVEL FROM LEVELTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找等级发生错误')

    def _get_cards(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT CID, NUM FROM UIDTABLE WHERE GID=? AND UID=? AND NUM>0", (
                    gid, uid)
            ).fetchall()
        return [c[0] for c in r] if r else {}

    def _get_card_num(self, gid, uid, cid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT NUM FROM UIDTABLE WHERE GID=? AND UID=? AND CID=?", (
                    gid, uid, cid)
            ).fetchone()
            return r[0] if r else 0

    def _add_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        if cid != 9999:
            self._set_card_owner(gid, cid, uid)
            self._set_favor(gid, uid, cid, 0)

    def _delete_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        self._delete_card_owner(gid, cid)
        self._delete_favor(gid, uid, cid)

    def _add_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _reduce_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _set_level(self, gid, uid, level):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _get_level_num(self, gid, level):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT COUNT(UID) FROM LEVELTABLE WHERE GID=? AND LEVEL=? ", (gid, level)
            ).fetchone()
            return r[0] if r else 0
    
    def _create_queentable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS QUEENTABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建皇后表发生错误')

    def _get_queen_owner(self, gid, cid):
        try:
            r = self._connect().execute(
                "SELECT UID FROM QUEENTABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找皇后归属发生错误')

    def _set_queen_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO QUEENTABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_queen_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM QUEENTABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )

    def _get_queen_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM QUEENTABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}
    
    def _search_queen(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT CID FROM QUEENTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找皇后发生错误')
    
    def _create_favortable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FAVORTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           FAVOR           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建好感表发生错误')

    def _set_favor(self, gid, uid, cid, favor):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _get_favor(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT FAVOR FROM FAVORTABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找好感发生错误')

    def _add_favor(self, gid, uid, cid, num):
        favor = self._get_favor(gid, uid, cid)
        if favor == None:
            favor = 0
        favor += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _reduce_favor(self, gid, uid, cid, num):
        favor = self._get_favor(gid, uid, cid)
        favor -= num
        favor = max(favor, 0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _delete_favor(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM FAVORTABLE  WHERE GID=? AND UID=? AND CID=?",
                (gid, uid, cid),
            )
    
    def _create_gifttable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GIFTTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           GFID             INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, GFID));''')
        except:
            raise Exception('创建礼物表发生错误')

    def _get_gift_num(self, gid, uid, gfid):
        try:
            r = self._connect().execute("SELECT NUM FROM GIFTTABLE WHERE GID=? AND UID=? AND GFID=?",
                                        (gid, uid, gfid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找礼物发生错误')

    def _add_gift(self, gid, uid, gfid, num=1):
        giftnum = self._get_gift_num(gid, uid, gfid)
        if giftnum == None:
            giftnum = 0
        giftnum += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GIFTTABLE (GID, UID, GFID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, gfid, giftnum),
            )

    def _reduce_gift(self, gid, uid, gfid, num=1):
        giftnum = self._get_gift_num(gid, uid, gfid)
        giftnum -= num
        giftnum = max(giftnum, 0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GIFTTABLE (GID, UID, GFID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, gfid, giftnum),
            )
    
    def _create_warehousetable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS WAREHOUSE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建仓库上限表发生错误')

    def _get_warehouse(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT NUM FROM WAREHOUSE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找上限发生错误')

    def _add_warehouse(self, gid, uid, num):
        housenum = self._get_warehouse(gid, uid)
        housenum += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO WAREHOUSE (GID, UID, NUM) VALUES (?, ?, ?)",
                (gid, uid, housenum),
            )


class ScoreCounter2:
    def __init__(self):
        os.makedirs(os.path.dirname(SCORE_DB_PATH), exist_ok=True)
        self._create_table()
        self._create_pres_table()

    def _connect(self):
        return sqlite3.connect(SCORE_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SCORECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SCORE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _add_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score + score))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _reduce_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score - score))
                conn.commit()
            else:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, 0))
                conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_score(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT SCORE FROM SCORECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    # 判断金币是否足够下注
    def _judge_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                return 1
            else:
                return 0
        except Exception as e:
            raise Exception(str(e))

    # 记录国王声望数据
    def _create_pres_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS PRESTIGECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           PRESTIGE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _set_prestige(self, gid, uid, prestige):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _get_prestige(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT PRESTIGE FROM PRESTIGECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return None if r is None else r[0]
        except:
            raise Exception('查找声望发生错误')

    def _add_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _reduce_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige -= num
        prestige = max(prestige, 0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )


def check_birth():
    today=datetime.date.today()
    today = str(today)
    file = os.path.join(_dir, "birth.json")
    with open(file, 'r', encoding='utf_8') as f:
        birth_info = json.loads(f.read())
    if birth_info["date"] == today:
        return True, birth_info["charalst"], birth_info["birthlst"]
    else:
        return False, [], []


def birth_update(today: str, charalst: list):
    file = os.path.join(_dir, "birth.json")
    birthlst = [CHARA_PROFILE[obj]["名字"] for obj in charalst]
    birth_info = {
        "date": today,
        "charalst": charalst,
        "birthlst": birthlst,
        "groups": {}
        }
    with open(file, 'w', encoding='utf_8') as f:
        f.write(json.dumps(birth_info, indent=4, ensure_ascii=False))


def birth_chara():
    today=datetime.date.today()
    today = str(today)
    _, month, day = today.split("-")
    charalst = birthdays.get(month+day, [])
    birth_update(today, charalst)
    return charalst


def celebrate_birth():
    charalst = birth_chara()
    msglst=[]
    for chara in charalst:
        name, cv, img = birth_card(chara)
        text = birth_text(chara, 0)
        msg = f'''今天是《公主连结Re:Dive》中的角色——{name}（CV：{cv}）的生日！

登录游戏即可观看观看角色生日特别剧情，仅限本日内观看哦！

一起为{name}的生日送上祝福吧～♪ {img}

尝试发送包含“生日快乐”和“{name}”在内的祝福语句来获取角色精选图片吧！
----------------------
{text}'''
        msglst.append(msg)
    return msglst


def gift(idx: int, gid: int, uid: int):
    file = os.path.join(_dir, "birth.json")
    with open(file, 'r', encoding='utf_8') as f:
        birth_info = json.loads(f.read())
    record = birth_info["groups"]

    gid, uid = str(gid), str(uid)
    if record.get(gid) == None:
        record[gid] = {}
    if record[gid].get(uid) == None:
        record[gid][uid] = 0
    record[gid][uid] += 1

    birth_info["groups"] = record
    print(birth_info)
    with open(file, 'w', encoding='utf_8') as f:
        f.write(json.dumps(birth_info, indent=4, ensure_ascii=False))

    count = record[gid][uid]
    _, img = pcr_img(idx)
    text = birth_text(idx, 1)
    msg = text+img

    duel = DuelCounter()
    gid, uid = int(gid), int(uid)
    if duel._get_level(gid, uid) != 0 and count <= SCORE_DAILY_LIMIT:
        score = random.randint(100,200)
        score_counter = ScoreCounter2()
        score_counter._add_score(gid, uid, score)
        msg += f"----------------------\n获得金币{score}。(今天第{count}/{SCORE_DAILY_LIMIT}次)"

    return msg