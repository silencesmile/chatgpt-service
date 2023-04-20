# -*- coding: utf-8 -*-
# @FileName  : openaiSDK.py
# @Author： 公众号：阿三先生
# @Date 11/17/22 3:54 PM
# @Version 1.0

import openai
import logging
from settings import *

logger = logging.getLogger()

def sdk_openai_text(checked_param):
    # openai.organization = openai_org_id
    openai.api_key = API_KEY

    if checked_param["stop"] is not None and len(checked_param["stop"]) <= 0:
        stop = None
    else:
        stop = checked_param["stop"]

    try:
        if checked_param["openai_parameter"]:
            openai_response = openai.Completion.create(engine=checked_param["model"],
                                                       prompt=checked_param["query"],
                                                       temperature=0.0,
                                                       max_tokens=500,
                                                       timeout=3)
        else:
            openai_response = openai.Completion.create(engine=checked_param["model"],
                                                       prompt=checked_param["query"],
                                                       temperature=checked_param["temperature"],
                                                       max_tokens=checked_param["max_tokens"],
                                                       stop=stop,
                                                       top_p=checked_param["top_p"],
                                                       frequency_penalty=checked_param["frequency_penalty"],
                                                       presence_penalty=checked_param["presence_penalty"],
                                                       best_of=checked_param["best_of"],
                                                       timeout=3)

        response = openai_response.choices[0]
        result = response.get("text", "")

        usage = openai_response.usage
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        prompt_completion = f"{prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} tokens"

        openai_dict = {
            "code": 200,
            "response_text": result,
            "prompt_completion": prompt_completion,
            "data": None
        }
    except Exception as e:
        openai_dict = {
            "code": 500,
            "response_text": "",
            "prompt_completion": "",
            "data": str(e)
        }

    return openai_dict
