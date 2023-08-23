import argparse
import os
import json

from tqdm import tqdm


def export_tagged_data(args):
    with open(args.info_dict_path, "r") as jf:
        tag_info_dict = json.load(jf)

    tagged_data_index_list = []

    for key, info in tag_info_dict.items():
        if len(info) > 0:
            tagged_data_index_list.append(key)

    tagged_data_list = []

    for index in tagged_data_index_list:
        with open(args.data_dir + "flatten_{}.json".format(index), "r") as jf:
            tagged_data = json.load(jf)
            tagged_data_list.append(tagged_data)

    with open(args.out_path, "w") as fout:
        json.dump(tagged_data_list, fout)


def filter_tagged_data(args):
    with open(args.info_dict_path, "r") as jf:
        tag_info_dict = json.load(jf)

    with open(args.user_info_path, "r") as jf:
        user_info_dict = json.load(jf)

    tagger_max_index_dict = {}
    for index, item in tag_info_dict.items():
        index = int(index)
        if len(item) > 0:
            tagger = item["tagger"]
            if tagger not in tagger_max_index_dict:
                tagger_max_index_dict[tagger] = index
            elif index > tagger_max_index_dict[tagger]:
                tagger_max_index_dict[tagger] = index

    for tagger, max_index in tagger_max_index_dict.items():
        export_indexes = [max_index + 1 + i for i in range(args.add_max_length)]
        for index in export_indexes:
            with open(args.data_dir + "flatten_{}.json".format(index), "r") as jf:
                data = json.load(jf)
            resp_list = data["resp"]
            p_resp_list = []
            n_resp_list = []
            for resp_text, resp_label in resp_list:
                if resp_label == "p":
                    p_resp_list.append([resp_text, resp_label])
                else:
                    n_resp_list.append([resp_text, resp_label])
            p_resp_list.extend(n_resp_list)
            data["resp"] = p_resp_list
            with open(args.data_dir + "flatten_{}.json".format(index), "w") as fout:
                json.dump(data, fout)
            


def export_empty_data(args):
    with open(args.info_dict_path, "r") as jf:
        tag_info_dict = json.load(jf)

    with open(args.user_info_path, "r") as jf:
        user_info_dict = json.load(jf)

    tagger_max_index_dict = {}
    for index, item in tag_info_dict.items():
        index = int(index)
        if len(item) > 0:
            tagger = item["tagger"]
            if tagger not in tagger_max_index_dict:
                tagger_max_index_dict[tagger] = index
            elif index > tagger_max_index_dict[tagger]:
                tagger_max_index_dict[tagger] = index

    for tagger, max_index in tagger_max_index_dict.items():
        export_indexes = [max_index + 1 + i for i in range(args.add_max_length)]
        print(max_index)
        print(export_indexes)
        for index in export_indexes:
            with open(args.data_dir + "flatten_{}.json".format(index), "r") as jf:
                data = json.load(jf)
            with open(args.empty_out_dir + "flatten_{}.json".format(index), "w") as fout:
                json.dump(data, fout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", help="", type=str, default="./data/splits/flatten/")
    parser.add_argument("--info_dict_path", help="", type=str, default="./data/splits/tag_info_dict.json")
    parser.add_argument("--out_path", help="", type=str, default="./data/tagged_data.json")
    parser.add_argument("--user_info_path", help="", type=str, default="./data/user_dict.json")
    parser.add_argument("--add_max_length", help="", type=int, default=5000) 
    parser.add_argument("--empty_out_dir", help="", type=str, default="./data/empty/")
    args = parser.parse_args()

    # export_tagged_data(args)
    # export_empty_data(args)
    filter_tagged_data(args)



if __name__ == "__main__":
    main()
