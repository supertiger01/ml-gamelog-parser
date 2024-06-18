import json
import argparse

code2hai = ["0",
            # 萬子
            "1m", "2m", "3m", "4m", "5m", "5M", "6m", "7m", "8m", "9m",
            # 筒子
            "1p", "2p", "3p", "4p", "5p", "5P", "6p", "7p", "8p", "9p",
            # 索子
            "1s", "2s", "3s", "4s", "5s", "5S", "6s", "7s", "8s", "9s",
            # 東南西北白発中
            "1z", "2z", "3z", "4z", "5z", "6z", "7z"]

commands = {
    "haipai", "ryukyoku", "dice", "sutehai", "kyokustart",
    "tsumo", "point", "dora", "open", "kyokuend", "say", "richi"
}

players = {"A0", "B0", "C0", "D0"}

class PlayerData:
    def __init__(self):
        self.tehai = []
        self.tsumo = 0
        self.furo = []
        self.sutehai = []
        self.richi = False
        self.tsumogiri = False
        self.point = 0

    def __str__(self):
        return "tehai: " + str(self.tehai) + ", tsumo: " + str(self.tsumo) + ", furo: " + str(self.furo) + ", sutehai: " + str(self.sutehai) + ", richi: " + str(self.richi) + ", tsumogiri: " + str(self.tsumogiri) + ", point: " + str(self.point)

kyoku_data = {
    "teban": "A0",
    "prev": "A0",
    "dora": [],
    "A0": PlayerData(),
    "B0": PlayerData(),
    "C0": PlayerData(),
    "D0": PlayerData(),
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="paifu file")
    return parser.parse_args()


def load_paifu(file):
    with open(file) as f:
        json_data = json.load(f)
    return json_data


def count_kyoku(json_data):
    cnt = 0
    for entry in json_data:
        if entry["cmd"] == "kyokustart":
            cnt += 1
    return cnt


def extract_one_kyoku(json_data, kyoku_num):
    max_kyoku_num = count_kyoku(json_data)
    if max_kyoku_num <= kyoku_num:
        raise ValueError("kyoku_num is too large")

    kyoku = []
    for entry in json_data:
        if entry["cmd"] == "kyokustart":
            kyoku_num -= 1
            if kyoku_num == 0:
                kyoku.append(entry)
        elif kyoku_num == 0:
            kyoku.append(entry)
            if entry["cmd"] == "kyokuend":
                break
    return kyoku

def show_kyoku(kyoku):
    print("----------------------------")
    print("teban: ", kyoku_data["teban"])
    for player in players:
        print(player, str(kyoku_data[player]))

def ripai(tehai):
    tehai.sort()

def do_haipai(args):
    kyoku_data["prev"] = kyoku_data["teban"]
    kyoku_data["teban"] = who = args[0]
    haipai_str = args[1]
    haipai = [code2hai.index(haipai_str[idx:idx+2]) for idx in range(0,len(haipai_str),2)]
    kyoku_data[who].tehai.extend(haipai)
    ripai(kyoku_data[who].tehai)

def do_tsumo(args):
    kyoku_data["prev"] = kyoku_data["teban"]
    kyoku_data["teban"] = who = args[0]
    tsumo_code = code2hai.index(args[2])
    kyoku_data[who].tsumo = tsumo_code
    kyoku_data[who].tehai.append(tsumo_code)
    kyoku_data[who].tsumogiri = False

def do_sutehai(args):
    kyoku_data["prev"] = kyoku_data["teban"]
    kyoku_data["teban"] = who = args[0]
    sutehai_code = code2hai.index(args[1])
    tsumogiri = True if len(args) == 3 and args[2] == "tsumogiri" else False
    kyoku_data[who].sutehai.append(sutehai_code)
    kyoku_data[who].tehai.remove(sutehai_code)
    kyoku_data[who].tsumo = 0
    kyoku_data[who].tsumogiri = tsumogiri
    ripai(kyoku_data[who].tehai)

def do_dora(args):
    dora_code = code2hai.index(args[1])
    kyoku_data["dora"].append(dora_code)

def do_say(args):
    pass

def do_open(args):
    kyoku_data["prev"] = kyoku_data["teban"]
    kyoku_data["teban"] = who = args[0]
    open_flag = args[1][0]

    if open_flag not in ["[", "(", "<"]:
        return

    tedashi_str = args[1][1:-1]
    tedashi_code = [code2hai.index(tedashi_str[idx:idx+2]) for idx in range(0,len(tedashi_str),2)]
    tsumo_code = code2hai.index(args[2]) if len(args) == 3 else 0

    print(args[0], args[1])

    if open_flag != "[":
        for hai in tedashi_code:
            kyoku_data[who].tehai.remove(hai)
            kyoku_data[who].furo.append(hai)
    if tsumo_code != 0:
        kyoku_data[who].furo.append(tsumo_code)

    if open_flag == "[":
        if who != kyoku_data["prev"]:
            kyoku_data[kyoku_data["prev"]].sutehai.remove(tsumo_code)
        else:
            kyoku_data[who].tsumo = 0
    elif open_flag == "(":
        kyoku_data[who].tsumo = 0
    elif open_flag == "<":
        kyoku_data[kyoku_data["prev"]].sutehai.remove(tsumo_code)
    else:
        raise ValueError("Invalid open flag")
    

def do_richi(args):
    who = args[0]
    kyoku_data[who].richi = True

def parse_kyoku(kyoku_data):
    for entry in kyoku_data:
        if entry["cmd"] not in commands:
            raise ValueError("Invalid command")
        if entry["cmd"] == "haipai":
            do_haipai(entry["args"])
        elif entry["cmd"] == "tsumo":
            do_tsumo(entry["args"])
        elif entry["cmd"] == "sutehai":
            do_sutehai(entry["args"])
        elif entry["cmd"] == "say":
            do_say(entry["args"])
        elif entry["cmd"] == "open":
            do_open(entry["args"])
        elif entry["cmd"] == "dora":
            do_dora(entry["args"])
        elif entry["cmd"] == "richi":
            do_richi(entry["args"])
        elif entry["cmd"] == "point":
            pass
        elif entry["cmd"] == "ryukyoku":
            pass
        elif entry["cmd"] == "dice":
            pass
        elif entry["cmd"] == "kyokuend":
            pass
        elif entry["cmd"] == "kyokustart":
            pass
        show_kyoku(kyoku_data)

if __name__ == "__main__":
    args = parse_args()
    json_data = load_paifu(args.file)
    kyoku = extract_one_kyoku(json_data, 3)
    parse_kyoku(kyoku)
    for player in players:
        print(player, kyoku_data[player])
