import requests
import json
import os
import argparse


def load_data(data_dir):
    data_path_list = [os.path.join(data_dir, "flatten_{}.json".format(i + 1)) for i in range(len(os.listdir(data_dir)))]

    with open("./data/cluster/resp_to_cluster_idx_v9.json", "r") as jf:
        corpus = json.load(jf)

    for data_path in data_path_list:
        with open(data_path, "r") as jf:
            data_item = json.load(jf)
        for resp_text, _ in data_item["resp"]:
            if resp_text not in corpus:
                import pdb;pdb.set_trace()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus_path", help="", type=str, default="./data/cluster/resp_to_cluster_idx_v9.json")
    parser.add_argument("--data_dir", help="", type=str, default="./flatten_bak/")
    args = parser.parse_args()

    load_data(args.data_dir)


if __name__ == "__main__":
    main()
