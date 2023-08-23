import argparse
import os
import json

from tqdm import tqdm


def format_data_item(data_item):
    # 'humanMachineDialogue', 'resp', 'origin_resp', 'star_id'
    new_data_item = {}
    new_data_item["star_id"] = data_item["star_id"]
    new_data_item["origin_resp"] = data_item["origin_resp"]
    context = []
    origin_context = data_item["humanMachineDialogue"]
    for context_item in origin_context:
        if context_item["author"] == "user":
            context.append(["user-msg", context_item["text"]])
        else:
            context.append(["advisor-msg", context_item["text"]])
    new_data_item["context"] = context
    resp = []
    label_studio_resp_list = data_item["resp"]
    for resp_item in label_studio_resp_list:
        tag = resp_item["author"].split("_")[1]
        resp.append([resp_item["text"], "n"])
    new_data_item["resp"] = resp
    return new_data_item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin_dir", help="", type=str, default="./data/splits/orders.star1-2.cont_resp_cluster_result.label-studio-v4/")
    parser.add_argument("--flatten_dir", help="", type=str, default="./data/splits/flatten/")
    args = parser.parse_args()
    file_name_list = os.listdir(args.origin_dir)
    flatten_index = 1

    for i in tqdm(range(len(file_name_list))):
        file_name = "split_{}.json".format(i + 1)
        with open(args.origin_dir + file_name, "r") as jf:
            data = json.load(jf)

        for data_item in data:
            formatted_data = format_data_item(data_item)
            with open(args.flatten_dir + "flatten_{}.json".format(flatten_index), "w") as fout:
                json.dump(formatted_data, fout)
                flatten_index += 1


if __name__ == "__main__":
    main()
