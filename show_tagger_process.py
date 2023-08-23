import json
import argparse

from rich.console import Console


console = Console()


def main():
    parser =  argparse.ArgumentParser()
    parser.add_argument("--tagged_data_info_path", help="", type=str, default="./data/splits/tag_info_dict.json")
    args = parser.parse_args()

    with open(args.tagged_data_info_path, "r") as jf:
        tagged_data_info_dict = json.load(jf)

    tagger_process_dict = {}
    tagged_cnt = 0

    for index, info_item in tagged_data_info_dict.items():
        index = int(index)
        if len(info_item) > 0:
            tagger = info_item["tagger"]
            if tagger not in tagger_process_dict:
                tagger_process_dict[tagger] = {"min": len(tagged_data_info_dict), "max": 0}
            if index >= tagger_process_dict[tagger]["max"]:
                tagger_process_dict[tagger]["max"] = index
            if index <= tagger_process_dict[tagger]["min"]:
                tagger_process_dict[tagger]["min"] = index
        if "date_modified" in info_item:
            tagged_cnt += 1

    console.print(tagger_process_dict)
    console.print("total tagged: {}".format(tagged_cnt))


if __name__ == "__main__":
    main()
