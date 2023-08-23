import argparse
import os
import json

from tqdm import tqdm
from keybert import KeyBERT


def generate_candidates(text, args):
    word_list = text.split(" ")
    candidates = []
    for word_cnt in range(args.ngram_min, args.ngram_max + 1):
        for begin_index in range(len(word_list)):
            next_index = begin_index + word_cnt - 1
            if next_index >= len(word_list):
                break
            else:
                candidate = " ".join(word_list[begin_index:next_index+1])
                candidates.append(candidate)
    return candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flatten_data_dir", help="", type=str, default="./data/splits/flatten/")
    parser.add_argument("--out_data_dir", help="", type=str, default="./data/splits/flatten_keywords/")
    parser.add_argument("--ngram_max", help="", type=int, default=5)
    parser.add_argument("--ngram_min", help="", type=int, default=1)
    args = parser.parse_args()

    file_name_list = ["flatten_{}.json".format(i+1) for i in range(len(os.listdir(args.flatten_data_dir)))]
    exist_file_name_set = set(os.listdir(args.out_data_dir))
    file_path_list = [args.flatten_data_dir + file_name for file_name in file_name_list]
    ngram_range = (args.ngram_min, args.ngram_max)
    kw_model = KeyBERT()
    for file_path in tqdm(file_path_list):
        file_name = file_path.split("/")[-1]
        if file_name in exist_file_name_set:
            continue
        keywords_list = []
        with open(file_path, "r") as jf:
            data_item = json.load(jf)
        sentence_list = data_item["resp"]
        for sentence_idx, sentence_item in enumerate(sentence_list):
            text = sentence_item[0]
            candidates = generate_candidates(text, args)
            result = kw_model.extract_keywords(docs=text, keyphrase_ngram_range=ngram_range)
            keywords = [result_item[0] for result_item in result[:3]]
            keywords_list.append(keywords)
        with open(args.out_data_dir + file_name, "w") as fout:
            json.dump(keywords_list, fout)


if __name__  == "__main__":
    main()
