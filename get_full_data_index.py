import json
import argparse
import os
from tqdm import tqdm


def is_next_context(context, next_context):
    if len(next_context) <= len(context):
        return False
    for i in range(len(context)):
        sender1, msg1 = context[i]
        sender2, msg2 = context[i]
        if sender1 != sender2 or msg1 != msg2:
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", help="", type=str, default="./data/splits/flatten")
    parser.add_argument("--out_path", help="", type=str, default="./data/index_to_full_data_index.json")
    args = parser.parse_args()

    file_name_list = os.listdir(args.data_dir)
    last_data = None

    index_to_full_data_index = {}
    now_index_list = []
    now_msg_index_list = []

    for i in tqdm(range(len(file_name_list))):
        index = i + 1
        file_path = "./data/splits/flatten/flatten_{}.json".format(index)

        with open(file_path, "r") as jf:
            data = json.load(jf)

        if last_data == None:
            now_index_list.append(index)
            now_msg_index_list.append(len(data["context"]))
            last_data = data
            continue 

        if is_next_context(last_data["context"], data["context"]):
            now_index_list.append(index)
            now_msg_index_list.append(len(data["context"]))
            last_data = data
        else:
            full_data_index = index - 1
            for item_index, msg_index in zip(now_index_list, now_msg_index_list):
                index_to_full_data_index[item_index] = [full_data_index, msg_index]
            now_index_list = [index]
            now_msg_index_list = [len(data["context"])]
            last_data = data
        
    with open(args.out_path, "w") as fout:
        json.dump(index_to_full_data_index, fout)


if __name__ == "__main__":
    main()
