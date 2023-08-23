import os
import argparse
import json

from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag_info_path", help="", type=str, default="./data/splits/tag_info_dict.json")
    parser.add_argument("--insert_thres", help="", type=int, default=7000)
    args = parser.parse_args()
    
    with open(args.tag_info_path, "r") as jf:
        tag_info_dict = json.load(jf)

    # search max len
    max_zhou = 0
    for info_index, info_item in tag_info_dict.items():
        info_index = int(info_index)
        if int(info_index) >= 7000:
            break
        if len(info_item) > 0 and info_index > max_zhou:
            max_zhou = info_index

    insert_cnt = 0
    print("Inserting......")
    for info_index, info_item in tqdm(tag_info_dict.items()):
        info_index = int(info_index)
        if len(info_item) == 0:
            continue
        if info_index >= 7000:
            print(info_item)
            info_item["tagger"] = "LuJunFang"
            print(info_item)
            insert_cnt += 1
        elif info_index <= max_zhou:
            info_item["tagger"] = "ZhouJingPing"
            insert_cnt += 1

    with open(args.tag_info_path, "w") as fout:
        json.dump(tag_info_dict, fout)


if __name__ == "__main__":
    main()
