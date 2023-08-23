from tqdm import tqdm
from datetime import datetime

import os
import json
import math


class DataDealer:
    def __init__(self, file_cnt_in_page, max_check_len=5):
        self.max_check_len = max_check_len

        with open("user_logs/login_logs.json", "r") as jf:
            self.user_login_logs = json.load(jf)
        with open("user_logs/checked_data/user_check_tasks.json", "r") as jf:
            self.user_check_tasks = json.load(jf)

        self.total_data_cnt = len(os.listdir("./data/splits/flatten/"))
        print("--"*20)
        print("total data to be tagged: {}".format(self.total_data_cnt))

        with open("./data/user_dict.json", "r") as jf:
            self.user_dict = json.load(jf)

        info_path = "./data/splits/tag_info_dict.json"
        if os.path.exists(info_path):
            with open(info_path, "r") as jf:
                self.tag_info_dict = json.load(jf)
        else:
            with open(info_path, "w") as fout:
                self.tag_info_dict = dict([(str(index + 1), {}) for index in range(self.total_data_cnt)])
                json.dump(self.tag_info_dict, fout)

        self.user_name_to_data_index_list = {}
        self.user_name_to_total_page_cnt = {}
        for user_name in self.user_dict:
            data_index_list = []
            task_scopes = self.user_dict[user_name]["task_scopes"]
            for scope in task_scopes:
                print(scope)
                data_index_list.extend([i for i in range(scope[0], scope[1])])
            # check tag_info
            for data_index in data_index_list:
                info_item = self.tag_info_dict[str(data_index)]
                if len(info_item) > 0 and info_item["tagger"] != user_name:
                    self.tag_info_dict[str(data_index)]["tagger"] = user_name
            with open(info_path, "w") as fout:
                json.dump(self.tag_info_dict, fout)
            self.user_name_to_data_index_list[user_name] = data_index_list
            self.user_name_to_total_page_cnt[user_name] = math.ceil(len(data_index_list) / file_cnt_in_page)

        self.total_keyword_cnt = len(os.listdir("./data/splits/flatten_keywords/"))

        self.file_cnt_in_page = file_cnt_in_page
        self.user_name_to_data_in_tagging = {}
        self.user_name_to_index_in_tagging = {}
        self.user_name_to_now_page_index = {}

        # data_index --> [full_data_index, msg_index]
        with open("./data/index_to_full_data_index.json", "r") as jf:
            self.index_to_full_data_index = json.load(jf)
        

        # user_name --> full_data_index --> msg_index --> data_index
        self.user_name_to_full_data_index_info = {}

        # user_name --> full_data_index --> [data_index, ...]
        self.user_name_to_full_data_index_to_data_index_list = {}

        for user_name, data_index_list in self.user_name_to_data_index_list.items():
            full_data_index_to_msg_index_to_data_index = {}
            full_data_index_to_data_index_list = {}
            for data_index in data_index_list:
                if str(data_index) not in self.index_to_full_data_index:
                    print("Skip unfound index {}".format(data_index))
                    continue
                full_data_index, msg_index = self.index_to_full_data_index[str(data_index)]
                
                if full_data_index not in full_data_index_to_msg_index_to_data_index:
                    full_data_index_to_msg_index_to_data_index[full_data_index] = {}

                if full_data_index not in full_data_index_to_data_index_list:
                    full_data_index_to_data_index_list[full_data_index] = []

                full_data_index_to_msg_index_to_data_index[full_data_index][msg_index] = data_index
                full_data_index_to_data_index_list[full_data_index].append(data_index)
            self.user_name_to_full_data_index_info[user_name] = full_data_index_to_msg_index_to_data_index
            self.user_name_to_full_data_index_to_data_index_list[user_name] = full_data_index_to_data_index_list

        self.user_name_to_sorted_full_data_index_list = {}
        for user_name in self.user_name_to_full_data_index_to_data_index_list:
            full_data_index_list = list(self.user_name_to_full_data_index_to_data_index_list[user_name].keys())
            full_data_index_list = [int(full_data_index) for full_data_index in full_data_index_list]
            
            sorted_full_data_index_list = sorted(full_data_index_list, reverse=False)
            self.user_name_to_sorted_full_data_index_list[user_name] = sorted_full_data_index_list

    def check_user_login_today(self, user_name):
        if user_name not in self.user_login_logs:
            return False
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        if self.user_login_logs[user_name]["last_login"] == formatted_date:
            return True
        else:
            return False

    def get_show_index_data(self, show_index, user_name):
        index = self.user_name_to_data_index_list[user_name][int(show_index)]
        index = int(index)
        if len(self.user_name_to_data_in_tagging) > 0:
            with open("./data/splits/tag_info_dict.json", "w") as fout:
                json.dump(self.tag_info_dict, fout)
        if index <= self.total_data_cnt and index > 0:
            with open("./data/splits/flatten/flatten_{}.json".format(index), "r") as jf:
                index_data = json.load(jf)
        if index <= self.total_keyword_cnt and index > 0:
            with open("./data/splits/flatten_keywords/flatten_{}.json".format(index), "r") as jf:
                keywords_list = json.load(jf)
        else:
            keywords_list = [[] for i in range(len(index_data["resp"]))]
            
        self.user_name_to_data_in_tagging[user_name] = index_data
        self.user_name_to_index_in_tagging[user_name] = index
        star_id = index_data["star_id"]
        origin_resp = index_data["origin_resp"]
        dialog_list = index_data["context"]
        resp_with_label_list = index_data["resp"]
        resp_list = []
        for resp_with_label in resp_with_label_list:
            if resp_with_label[1] == "p":
                resp_tag = "positive-msg"
            elif resp_with_label[1] == "m":
                resp_tag = "medium-msg"
            else:
                resp_tag = "negative-msg"
            resp_list.append([resp_tag, resp_with_label[0]])

        return star_id, origin_resp, dialog_list, resp_list, keywords_list

    def get_user_tag_process(self, user_name):
        # get user today tag process
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        user_task_index_list = []
        task_scopes = self.user_dict[user_name]["task_scopes"]
        tag_process = {
            "skipped": 0,
            "tagged": 0
        }
        for scope in task_scopes:
            task_index_list_item = list(range(scope[0], scope[1]))
            user_task_index_list.extend(task_index_list_item)
        date_start = False
        for task_index in user_task_index_list:
            tag_info = self.tag_info_dict[str(task_index)]
            if "skipped" in tag_info and date_start and tag_info["skipped"] == 1:
                tag_process["skipped"] += 1
            elif "date_modified" in tag_info and tag_info["date_modified"] == formatted_date:
                tag_process["tagged"] += 1
        return tag_process
    
    def get_file_list(self, page_index, user_name):
        data_index_list = self.user_name_to_data_index_list[user_name]
        show_data_index_list = [i for i in range(len(data_index_list))]
        if page_index < self.user_name_to_total_page_cnt[user_name] and page_index >= 0:
            got_show_data_index_list = show_data_index_list[page_index*self.file_cnt_in_page:(page_index+1)*self.file_cnt_in_page]
        else:
            got_show_data_index_list = show_data_index_list[:self.file_cnt_in_page]
        tag_info_list = []
        for show_data_index in got_show_data_index_list:
            data_index = data_index_list[show_data_index]
            tag_info_list.append(self.tag_info_dict[str(data_index)])
        return got_show_data_index_list, tag_info_list

    def get_latest_file_list(self, user_name):
        data_index_list = self.user_name_to_data_index_list[user_name]
        last_show_data_index = 0
        for show_data_index, data_index in enumerate(data_index_list):
            tag_info_item = self.tag_info_dict[str(data_index)]
            if len(tag_info_item) > 0:
                last_show_data_index = show_data_index
        page_index = math.ceil(last_show_data_index / self.file_cnt_in_page) - 1
        self.user_name_to_now_page_index[user_name] = page_index
        got_show_data_index_list, tag_info_list = self.get_file_list(page_index, user_name)
        return got_show_data_index_list, tag_info_list

    def get_next_file_list(self, user_name):
        now_page_index = self.user_name_to_now_page_index[user_name]
        total_page_cnt = self.user_name_to_total_page_cnt[user_name]
        now_page_index += 1
        if now_page_index >= total_page_cnt:
            now_page_index -= 1
        self.user_name_to_now_page_index[user_name] = now_page_index
        got_show_data_index_list, tag_info_list = self.get_file_list(now_page_index, user_name)
        return got_show_data_index_list, tag_info_list

    def get_previous_file_list(self, user_name):
        now_page_index = self.user_name_to_now_page_index[user_name]
        total_page_cnt = self.user_name_to_total_page_cnt[user_name]
        now_page_index -= 1
        if now_page_index < 0:
            now_page_index += 1
        self.user_name_to_now_page_index[user_name] = now_page_index
        got_show_data_index_list, tag_info_list = self.get_file_list(now_page_index, user_name)
        return got_show_data_index_list, tag_info_list

    def modify_label(self, modify_resp_index, modify_resp_tag, user_name):
        modify_resp_index = int(modify_resp_index)
        self.user_name_to_data_in_tagging[user_name]["resp"][modify_resp_index][1] = modify_resp_tag
        with open("./data/splits/flatten/flatten_{}.json".format(self.user_name_to_index_in_tagging[user_name]), "w") as fout:
            json.dump(self.user_name_to_data_in_tagging[user_name], fout)
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["date_modified"] = formatted_date
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["tagger"] = user_name

    def set_all_n_labels(self, user_name):
        for i in range(len(self.user_name_to_data_in_tagging[user_name]["resp"])):
            self.user_name_to_data_in_tagging[user_name]["resp"][i][1] = "n"
        with open("./data/splits/flatten/flatten_{}.json".format(self.user_name_to_index_in_tagging[user_name]), "w") as fout:
            json.dump(self.user_name_to_data_in_tagging[user_name], fout)
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["date_modified"] = formatted_date
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["tagger"] = user_name

    def skip_page(self, user_name):
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["skipped"] = 1
        self.tag_info_dict[str(self.user_name_to_index_in_tagging[user_name])]["tagger"] = user_name

    def user_check_finish(self, user_name):
        for other_user_name, task_item in self.user_check_tasks.items():
            task_data_index_set = set(task_item["task_data_index_list"])
            checked_data_index_set = set(task_item["checked_data_index_list"])
            left_index_set = task_data_index_set - checked_data_index_set
            if len(left_index_set) > 0:
                return False
        return True
        
    def gen_check_data(self, user_name):
        added_user_name_list = os.listdir("./user_logs/checked_data/")
        if  user_name not in added_user_name_list:
            os.makedirs("./user_logs/checked_data/{}".format(user_name))
        user_name_set = set(list(self.user_dict.keys()))
        user_name_set.remove(user_name)
        other_user_name_list = list(user_name_set)

        if user_name not in self.user_check_tasks:
            self.user_check_tasks[user_name] = {}

        for other_user_name in other_user_name_list:
            self.user_check_tasks[other_user_name] = {}
            sorted_full_data_index_list = self.user_name_to_sorted_full_data_index_list[other_user_name]
            if other_user_name not in self.user_check_tasks[user_name]:
                self.user_check_tasks[user_name][other_user_name] = {"last_idx_in_full_data_index_list": 0, "task_data_index_list": [], "checked_data_index_list": []}
            self.user_check_tasks[user_name][other_user_name]["task_data_index_list"] = []
            last_idx_in_full_data_index_list = self.user_check_tasks[user_name][other_user_name]["last_idx_in_full_data_index_list"]
            task_data_index_list = []
            for idx in range(last_idx_in_full_data_index_list + 1, len(sorted_full_data_index_list)):
                full_data_index = sorted_full_data_index_list[idx]
                task_data_index_list.extend(self.user_name_to_full_data_index_to_data_index_list[full_data_index])
                if len(task_data_index_list) >= self.max_check_len:
                    self.user_check_tasks[user_name][other_user_name]["last_idx_in_full_data_index_list"] = idx
                    self.user_check_tasks[user_name][other_user_name]["task_data_index_list"] = task_data_index_list
                    break
        with open("user_logs/checked_data/user_check_tasks.json", "w") as fout:
            json.dump(self.user_check_tasks, fout)


    def login_success(self, user_name, user_password):
        user_password = str(user_password)
        if user_password is None:
            user_password = ""
        if user_name in self.user_dict and user_password == self.user_dict[user_name]["pwd"]:
            login_today = self.check_user_login_today(user_name)
            if user_name not in self.user_login_logs:
                self.user_login_logs[user_name] = {}
            current_date = datetime.now()
            formatted_date = current_date.strftime("%Y-%m-%d")
            self.user_login_logs[user_name]["last_login"] = formatted_date
            self.user_login_logs[user_name]["check_finish"] = False
            # if not login_today:
            #     self.gen_check_data(user_name)
            with open("user_logs/login_logs.json", "w") as fout:
                json.dump(self.user_login_logs, fout)
            return "p"
        elif user_name in self.user_dict and user_password != self.user_dict[user_name]["pwd"]:
            return "n_p"
        elif user_name not in self.user_dict:
            return "n_u"
        else:
            return "n"

    def admin_login_success(self, user_name, user_password):
        user_password = str(user_password)
        if user_password is None:
            user_password = ""
        if user_name in self.user_dict and not self.user_dict[user_name]["is_admin"]:
            return "n_a"
        elif user_name in self.user_dict and user_password == self.user_dict[user_name]["pwd"]:
            return "p"
        elif user_name in self.user_dict and user_password != self.user_dict[user_name]["pwd"]:
            return "n_p"
        elif user_name not in self.user_dict:
            return "n_u"
        else:
            return "n"

    def admin_get_user_name_list(self):
        return list(self.user_dict.keys())

    def admin_get_user_task_list(self, page_index, user_name):
        page_index = int(page_index)
        full_data_index_len = len(self.user_name_to_full_data_index_info[user_name])
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        show_data_index_list = [i for i in range(len(full_data_index_list))]
        tag_info_list = []
        got_show_data_index_list = show_data_index_list[page_index*self.file_cnt_in_page:(page_index+1)*self.file_cnt_in_page]
        for show_data_index in got_show_data_index_list:
            full_data_index = full_data_index_list[show_data_index]
            data_index_list = self.user_name_to_full_data_index_to_data_index_list[user_name][full_data_index]
            have_date_info = False
            append_info = {}
            for data_index in data_index_list:
                tag_info = self.tag_info_dict[str(data_index)]
                if len(tag_info) > 0 and "skipped" in tag_info and not have_date_info:
                    append_info = tag_info
                elif len(tag_info) > 0:
                    have_date_info = True
                    append_info = tag_info
            tag_info_list.append(append_info)
        return got_show_data_index_list, tag_info_list

    def get_latest_tagged_page_index(self, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        page_cnt = math.ceil(len(full_data_index_list) / self.file_cnt_in_page)
        tagged_page_index = 0

        for page_index in range(page_cnt):
            _, tag_info_list = self.admin_get_user_task_list(page_index, user_name)
            for tag_info in tag_info_list:
                if len(tag_info) > 0:
                    tagged_page_index = page_index
                    break
        return tagged_page_index

    def admin_get_show_index_data(self, show_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_index]
        with open("./data/splits/flatten/flatten_{}.json".format(full_data_index), "r") as jf:
            data_item = json.load(jf)
        with open("./data/splits/tag_info_dict.json", "w") as fout:
            json.dump(self.tag_info_dict, fout)
        dialog_list = data_item["context"]
        dialog_list.append(["advisor-msg", data_item["origin_resp"]])

        tag_info_list = []
        msg_index_list = []

        # user_name --> full_data_index --> msg_index --> data_index
        msg_index_info = self.user_name_to_full_data_index_info[user_name][full_data_index]
        for msg_index, data_index in msg_index_info.items():
            tag_info_list.append(self.tag_info_dict[str(data_index)])
            msg_index_list.append(msg_index)

        return dialog_list, tag_info_list, msg_index_list

    def get_order_tag_info_list(self, show_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_index]
        tag_info_list = []
        msg_index_list = []
        msg_index_info = self.user_name_to_full_data_index_info[user_name][full_data_index]
        for msg_index, data_index in msg_index_info.items():
            tag_info_list.append(self.tag_info_dict[str(data_index)])
            msg_index_list.append(msg_index)
        return tag_info_list, msg_index_list
    
    def admin_get_msg_index_resp_list(self, show_index, user_name, msg_index):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_index]
        data_index = self.user_name_to_full_data_index_info[user_name][full_data_index][int(msg_index)]
        with open("./data/splits/tag_info_dict.json", "w") as fout:
            json.dump(self.tag_info_dict, fout)

        with open("./data/splits/flatten/flatten_{}.json".format(data_index), "r") as jf:
            data_item = json.load(jf)

        resp_list = data_item["resp"]
        formatted_resp_list = []

        for resp_text, resp_label in resp_list:
            if resp_label == "p":
                resp_type = "positive-msg"
            elif resp_label == "n":
                resp_type = "negative-msg"
            elif resp_label == "m":
                resp_type = "medium-msg"
            formatted_resp_list.append([resp_type, resp_text])

        return formatted_resp_list

    def order_mode_modify(self, modify_resp_index, modify_resp_tag, show_data_index, msg_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_data_index]
        data_index = self.user_name_to_full_data_index_info[user_name][full_data_index][int(msg_index)]
        with open("./data/splits/flatten/flatten_{}.json".format(data_index), "r") as jf:
            data_item = json.load(jf)
        data_item["resp"][int(modify_resp_index)][1] = modify_resp_tag

        with open("./data/splits/flatten/flatten_{}.json".format(data_index), "w") as fout:
            json.dump(data_item, fout)

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        self.tag_info_dict[str(data_index)]["date_modified"] = formatted_date
        self.tag_info_dict[str(data_index)]["tagger"] = user_name

    def order_mode_skip_item(self, msg_index, show_data_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_data_index]
        data_index = self.user_name_to_full_data_index_info[user_name][full_data_index][int(msg_index)]
        self.tag_info_dict[str(data_index)]["skipped"] = 1
        self.tag_info_dict[str(data_index)]["tagger"] = user_name

    def order_mode_cancel_skip_item(self, msg_index, show_data_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_data_index]
        data_index = self.user_name_to_full_data_index_info[user_name][full_data_index][int(msg_index)]
        if "skipped" in self.tag_info_dict[str(data_index)]:
            self.tag_info_dict[str(data_index)].pop("skipped")
            if len(self.tag_info_dict[str(data_index)]) == 1:
                self.tag_info_dict[str(data_index)] = {}

    def admin_modify_label(self, modify_resp_index, modify_resp_tag, show_data_index, msg_index, user_name):
        full_data_index_list = list(self.user_name_to_full_data_index_info[user_name])
        full_data_index = full_data_index_list[show_data_index]
        data_index = self.user_name_to_full_data_index_info[user_name][full_data_index][int(msg_index)]
        with open("./data/splits/flatten/flatten_{}.json".format(data_index), "r") as jf:
            data_item = json.load(jf)
        data_item["resp"][int(modify_resp_index)][1] = modify_resp_tag

        with open("./data/splits/flatten/flatten_{}.json".format(data_index), "w") as fout:
            json.dump(data_item, fout)

        if len(self.tag_info_dict[str(data_index)]) > 0:
            self.tag_info_dict[str(data_index)][""]
            self.tag_info_dict[str(data_index)]["fixed_by"] = "LuJunFang"
            current_date = datetime.now()
            formatted_date = current_date.strftime("%Y-%m-%d")
            self.tag_info_dict[str(data_index)]["fixed_date"] = formatted_date

    def get_user_tagged_history(self):
        user_name_list = list(self.user_dict.keys())
        date_set = set([])
        tag_history_dict = {}
        for user_name in user_name_list:
            task_scopes = self.user_dict[user_name]["task_scopes"]
            index_list = []
            tag_history_dict[user_name] = {}

            for scope in task_scopes:
                index_list.extend(list(range(scope[0], scope[1])))

            last_date = ""
            all_n_cnt = 0
            for index in index_list:
                tag_info = self.tag_info_dict[str(index)]
                if len(tag_info) == 0:
                    all_n_cnt += 1
                    continue
                if "skipped" in tag_info and tag_info["skipped"] == 1 and last_date != "":
                    tag_history_dict[user_name][last_date]["skipped"] += 1
                    tag_history_dict[user_name][last_date]["tag"] += all_n_cnt
                    all_n_cnt = 0
                elif "date_modified" in tag_info:
                    date_modified = tag_info["date_modified"]
                    date_set.add(date_modified)
                    if date_modified not in tag_history_dict[user_name]:
                        tag_history_dict[user_name][date_modified] = {"skipped": 0, "tag": 0}
                    tag_history_dict[user_name][date_modified]["tag"] += 1
                    tag_history_dict[user_name][date_modified]["tag"] += all_n_cnt
                    all_n_cnt = 0
                    last_date = date_modified

        date_list = list(date_set)
        date_list.sort() 
        tagged_data_cnt = []
        skipped_cnt = []
        for user_name in user_name_list:
            data_cnt_list = []
            skipped_cnt_list = []
            for date in date_list:
                if date not in tag_history_dict[user_name]:
                    data_cnt_list.append(0)
                    skipped_cnt_list.append(0)
                else:
                    data_cnt_list.append(tag_history_dict[user_name][date]["tag"])
                    skipped_cnt_list.append(tag_history_dict[user_name][date]["skipped"])
            tagged_data_cnt.append(data_cnt_list)
            skipped_cnt.append(skipped_cnt_list)
        return user_name_list, date_list, tagged_data_cnt, skipped_cnt


def test():
    dealer = DataDealer(50)
    # latest_file_list = dealer.get_latest_file_list()
    # print(latest_file_list)
    index_data = dealer.get_index_data(1)
    print(index_data)


if __name__ == "__main__":
    test()

