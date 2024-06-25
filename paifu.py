import json
import argparse

from kyoku import Kyoku


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kyoku_num", type=int, help="kyoku number") #ここで曲数を指定
    parser.add_argument("file", help="paifu file") #ここでファイル名を指定
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


if __name__ == "__main__":
    # file = "/Users/notoya/Documents/Univ./2024/it_murao/ml-gamelog-parser/L001_S002_0008_01A.json"
    args = parse_args()
    json_data = load_paifu(args.file)
    kyoku_data = extract_one_kyoku(json_data, args.kyoku_num)

    with open("../2023-2024_paifu/L001_S002_0008_01A.json", "w") as f:
        json.dump(kyoku_data, f, indent=2)

    kyoku = Kyoku(kyoku_data)
    while kyoku.step():
        print("---------------------------")
        kyoku.show()
    print("====== 終局 ======")
    kyoku.show()
