import os, sys
import toml
import time
import json
import random
import logging
import requests

from typing import List, Optional, Dict
from collections import namedtuple
from easydict import EasyDict as edict
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, Request, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from snowflake import generator


from data_dealer import DataDealer


def setup_logger(save_dir, name=None, log_level=logging.DEBUG):
    if not name:
        logger = logging.getLogger()
        name = 'api_svr'
    else:
        logger = logging.getLogger(name=name)
    logger.setLevel(log_level)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if save_dir:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        fh = logging.FileHandler(os.path.join(save_dir, "api_log.txt"), mode='a+')
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

id_gen = generator(1, 1)
config_path = './tag.conf'
conf = toml.load(config_path)
print('server config: %s'% conf)
conf = edict(conf)
setup_logger(conf.main.log_dir, log_level=conf.main.log_level)
logging.info('conf: %s', conf)

load_start = time.time()

app = FastAPI()

origins = [
    "*",
]

dealer = DataDealer(conf.main.file_cnt_in_page)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TagReq(BaseModel):
    log_id: Optional[str] = None
    mode: Optional[str] = None
    page_index: Optional[int] = None
    show_index_data_to_get: Optional[int] = None
    modify_resp_index: Optional[int] = None
    modify_resp_tag: Optional[str] = None
    user_name: Optional[str] = None
    user_password: Optional[str] = None
    msg_index: Optional[int] = None
    show_data_index: Optional[int] = None

class TagRsp(BaseModel):
    log_id: Optional[str] = None
    show_data_index_list: Optional[List[int]] = None
    tag_info_list: Optional[List[dict]] = None
    star_id: Optional[str] = None
    origin_resp: Optional[str] = None
    dialog_list: Optional[List] = None
    resp_list: Optional[List] = None
    keywords_list: Optional[List] = None
    login_signup_result: Optional[str] = None
    user_name_list: Optional[List[str]] = None
    tagged_page_index: Optional[int] = None
    msg_index_list: Optional[List] = None
    date_list: Optional[List] = None
    tagged_data_cnt: Optional[List] = None
    skipped_cnt: Optional[List] = None
    tag_process: Optional[dict] = None
    user_login_today: Optional[bool] = None
    check_finish: Optional[bool] = None


tag_rank_api = FastAPI()
@tag_rank_api.post("/", response_model=TagRsp)
def tag_rank(req: TagReq):
    log_id = req.log_id or f'{next(id_gen):x}'
    mode = req.mode

    if mode == "check_user_login_today":
        user_name = req.user_name
        user_login_today = dealer.check_user_login_today(user_name)
        rsp = TagRsp(
                user_login_today = user_login_today
                )
    elif mode == "initial_get_file_list":
        user_name = req.user_name
        show_data_index_list, tag_info_list = dealer.get_latest_file_list(user_name)
        rsp = TagRsp(
                log_id = log_id,
                show_data_index_list = show_data_index_list,
                tag_info_list = tag_info_list,
                )
        # logging.info('(%s): %s <-> %s', log_id, query, rsp)
    elif mode == "get_latest_file_list":
        user_name = req.user_name
        show_data_index_list, tag_info_list = dealer.get_latest_file_list(user_name)
        rsp = TagRsp(
                log_id = log_id,
                show_data_index_list = show_data_index_list,
                tag_info_list = tag_info_list,
                )
    elif mode == "get_next_file_list":
        user_name = req.user_name
        show_data_index_list, tag_info_list = dealer.get_next_file_list(user_name)
        rsp = TagRsp(
                log_id = log_id,
                show_data_index_list = show_data_index_list,
                tag_info_list = tag_info_list,
                )
    elif mode == "get_previous_file_list":
        user_name = req.user_name
        show_data_index_list, tag_info_list = dealer.get_previous_file_list(user_name)
        rsp = TagRsp(
                log_id = log_id,
                show_data_index_list = show_data_index_list,
                tag_info_list = tag_info_list,
                )
    elif mode == "get_show_index_data":
        show_index_data_to_get = req.show_index_data_to_get
        user_name = req.user_name
        star_id, origin_resp, dialog_list, resp_list, keywords_list = dealer.get_show_index_data(show_index_data_to_get, user_name)
        rsp = TagRsp(
                log_id = log_id,
                star_id = star_id,
                origin_resp = origin_resp,
                dialog_list = dialog_list,
                resp_list = resp_list,
                keywords_list = keywords_list,
                )
    elif mode == "get_user_tag_process":
        user_name = req.user_name 
        tag_process = dealer.get_user_tag_process(user_name)
        rsp = TagRsp(\
                log_id = log_id,
                tag_process = tag_process
                )
    elif mode == "modify_label":
        modify_resp_index = req.modify_resp_index
        modify_resp_tag = req.modify_resp_tag
        user_name =  req.user_name
        dealer.modify_label(modify_resp_index, modify_resp_tag, user_name)
        rsp = TagRsp(
                log_id = log_id,
                )
    elif mode == "set_all_n_labels":
        user_name =  req.user_name
        dealer.set_all_n_labels(user_name)
        rsp = TagRsp(
                log_id = log_id
                )
    elif mode == "skip_page":
        user_name = req.user_name
        dealer.skip_page(user_name)
        rsp = TagRsp(
                log_id = log_id,
                )
    elif mode == "user_login":
        user_name = req.user_name
        user_password = req.user_password
        result = dealer.login_success(user_name, user_password)
        rsp = TagRsp(
                log_id = log_id,                
                login_signup_result = result,
                )
    elif mode == "admin_login":
        user_name = req.user_name
        user_password = req.user_password
        result = dealer.admin_login_success(user_name, user_password)
        rsp = TagRsp(
                log_id = log_id,                
                login_signup_result = result,
                )
    elif mode == "admin_get_user_name_list":
        user_name_list = dealer.admin_get_user_name_list()
        rsp = TagRsp(
                log_id = log_id,
                user_name_list = user_name_list
                )
    elif mode == "admin_get_user_task_list":
        user_name = req.user_name
        page_index = req.page_index
        got_show_data_index_list, tag_info_list = dealer.admin_get_user_task_list(page_index, user_name)
        rsp = TagRsp(
                show_data_index_list = got_show_data_index_list,
                tag_info_list = tag_info_list,
                )
    elif mode == "get_latest_tagged_page_index":
        user_name = req.user_name
        tagged_page_index = dealer.get_latest_tagged_page_index(user_name)
        rsp = TagRsp(
                tagged_page_index = tagged_page_index
                )
    elif mode == "admin_get_show_index_data":
        user_name = req.user_name
        show_index_data_to_get = req.show_index_data_to_get
        dialog_list, tag_info_list, msg_index_list = dealer.admin_get_show_index_data(show_index_data_to_get, user_name)
        rsp = TagRsp(
                dialog_list = dialog_list,
                tag_info_list = tag_info_list,
                msg_index_list = msg_index_list
                )
    elif mode == "get_order_tag_info_list":
        user_name = req.user_name
        show_data_index = req.show_data_index
        tag_info_list, msg_index_list = dealer.get_order_tag_info_list(show_data_index, user_name)
        rsp = TagRsp(
                tag_info_list = tag_info_list,
                msg_index_list = msg_index_list
                )

    elif mode == "admin_get_msg_index_resp_list":
        user_name = req.user_name
        msg_index = req.msg_index
        show_index_data_to_get = req.show_index_data_to_get
        resp_list = dealer.admin_get_msg_index_resp_list(show_index_data_to_get, user_name, msg_index)
        rsp = TagRsp(
                resp_list = resp_list,
                )
    elif mode == "admin_modify_label":
        modify_resp_index = req.modify_resp_index
        modify_resp_tag = req.modify_resp_tag
        user_name =  req.user_name
        msg_index = req.msg_index
        show_data_index = req.show_data_index
        dealer.admin_modify_label(modify_resp_index, modify_resp_tag, show_data_index, msg_index, user_name)
        rsp = TagRsp()
    elif mode == "order_mode_modify":
        modify_resp_index = req.modify_resp_index
        modify_resp_tag = req.modify_resp_tag
        user_name =  req.user_name
        msg_index = req.msg_index
        show_data_index = req.show_data_index
        dealer.order_mode_modify(modify_resp_index, modify_resp_tag, show_data_index, msg_index, user_name)
        rsp = TagRsp()
    elif mode == "order_mode_skip_item":
        msg_index = req.msg_index
        show_data_index = req.show_data_index
        user_name = req.user_name
        dealer.order_mode_skip_item(msg_index, show_data_index, user_name)
        rsp = TagRsp()
    elif mode == "order_mode_cancel_skip_item":
        msg_index = req.msg_index
        show_data_index = req.show_data_index
        user_name = req.user_name
        dealer.order_mode_cancel_skip_item(msg_index, show_data_index, user_name)
        rsp = TagRsp()

    # user_name_list, date_list, tagged_data_cnt, skipped_cnt
    elif mode == "get_user_tagged_history":
        user_name_list, date_list, tagged_data_cnt, skipped_cnt = dealer.get_user_tagged_history()
        rsp = TagRsp(
                user_name_list = user_name_list,
                date_list = date_list,
                tagged_data_cnt = tagged_data_cnt,
                skipped_cnt = skipped_cnt
                )
    elif mode == "user_check_finish":
        user_name = req.user_name
        check_finish = dealer.user_check_finish(user_name)
        rsp = TagRsp(
                check_finish = check_finish
                )

    print(rsp)
    return rsp

@app.on_event("startup")
async def set_default_executor():
    from anyio.lowlevel import RunVar
    from anyio import CapacityLimiter
    logging.getLogger().setLevel(conf.main.log_level)

    thread_num = 3
    RunVar("_default_thread_limiter").set(CapacityLimiter(thread_num))
    logging.info('set default thread pool size %s', thread_num)

app.mount('/api/v0/tag_rank', tag_rank_api)

if __name__ == "__main__":
    # start uvicorn server
    import uvicorn
    logging.getLogger().setLevel(logging.INFO)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8280
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", workers=1)
