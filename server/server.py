# -*- coding: utf-8 -*-
# @FileName  : server.py
# @Author： 公众号：阿三先生
# @Date 11/9/22 2:14 PM
# @Version 1.0
import requests
import tornado.web
from abc import ABC
import time
import json
import tornado.gen
import tornado.web
import tornado.concurrent
import threading

from settings import *
from tools.logger_utils import get_logger_conf
from concurrent.futures import ThreadPoolExecutor
from script.openaiSDK import sdk_openai_text
from script.chatgptSDK import chat_openai_text


module_name = str(os.path.basename(__file__)).split('.')[0]
logger = get_logger_conf(log_path, module_name, 'INFO')


class OpenaiService(tornado.web.RequestHandler, ABC):
    # 定义线程池数量一定叫executor
    executor = ThreadPoolExecutor(100)  # 并发数量

    def check_params(self, params):
        query = params.get("query", "").strip()
        messages = params.get("messages", [])
        openai_parameter = params.get("openai_arameter", True)
        model = params.get("model", "gpt-3.5-turbo").strip()
        max_tokens = params.get("max_tokens", 500)
        temperature = params.get("temperature", 0.0)
        top_p = params.get("top_p", 1)
        frequency_penalty = params.get("frequency_penalty", 0.0)
        presence_penalty = params.get("presence_penalty", 0.0)
        stop = params.get("stop", ["Human:"])
        best_of = params.get("best_of", 1)

        if model == "gpt-3.5-turbo" or model == "gpt-4":
            if not isinstance(messages, list) or len(messages) <= 0:
                raise ValueError(f"param messages error")
        else:
            if not isinstance(query, str) or len(query) <= 0:
                raise ValueError(f"param query error")

        if not isinstance(openai_parameter, bool):
            raise ValueError(f"param openai_parameter error")

        if not isinstance(model, str) or len(model) <= 0:
            raise ValueError(f"param model error")

        if not isinstance(max_tokens, int) or (max_tokens < 1 or max_tokens > 4097):
            raise ValueError(f"param max_tokens out of range(0~4097): {max_tokens}")

        if not isinstance(float(temperature), float) or (temperature < 0.0 or temperature > 1.0):
            raise ValueError(f"param temperature out of range(0~1.0): {temperature}")

        if not isinstance(float(top_p), float) or (top_p < 0.0 or top_p > 1.0):
            raise ValueError(f"param top_p out of range(0.0~1.0): {top_p}")

        if not isinstance(float(frequency_penalty), float) or (frequency_penalty < 0.0 or frequency_penalty > 2.0):
            raise ValueError(f"param frequency_penalty out of range(0.0~2.0): {frequency_penalty}")

        if not isinstance(float(presence_penalty), float) or (presence_penalty < 0.0 or presence_penalty > 2.0):
            raise ValueError(f"param presence_penalty out of range(0.0~2.0): {presence_penalty}")

        if not isinstance(best_of, int) or (best_of < 0 or best_of > 20):
            raise ValueError(f"param best_of out of range(0~20): {best_of}")

        if not isinstance(stop, list) or len(stop) <= 0:
            raise ValueError("param stop error")

        stop = [tmp.strip() for tmp in stop if len(tmp.strip()) > 0]

        checked_param = {
            "query": query,
            "messages": messages,
            "model": model,
            "openai_parameter": openai_parameter,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop,
            "best_of": best_of
        }
        return checked_param

    @tornado.concurrent.run_on_executor
    def query_match(self, checked_param):
        if checked_param["model"] == "gpt-3.5-turbo" or checked_param["model"] == "gpt-4":
            openai_dict = chat_openai_text(checked_param)
        else:
            openai_dict = sdk_openai_text(checked_param)

        return openai_dict

    @tornado.gen.coroutine
    def post(self):
        response_ = {}
        try:
            request_js = json.loads(str(self.request.body, encoding='utf-8'))

            logger.info('rcv: {} {}'.format(self.request.uri, request_js))
            if self.request.uri == '/chatgpt-service/v1/chat':
                s_time = time.time()
                checked_param = self.check_params(request_js)

                openai_dict = yield self.query_match(checked_param)

                logger_info = {
                            "code": openai_dict["code"],
                            "param": checked_param,
                            "response": openai_dict["response_text"],
                            "request_tokens": openai_dict["prompt_completion"]
                }
                if openai_dict["code"] != 200:
                    logger_info["error"] = f'{openai_dict["code"]}:{openai_dict["data"]}'
                    response_ = {
                        "code": openai_dict["code"],
                        "msg": f'{openai_dict["code"]}:{openai_dict["data"]}',
                        "data": logger_info
                    }
                else:
                    response__text = logger_info["response"]

                    response_ = {
                        "code": 0,
                        "msg": "ok",
                        "data": {"response": response__text}
                    }

                e_time = time.time()
                diff_time = "%.3f" % (e_time - s_time)
                logger_info["request_time"] = diff_time
                logger.info(json.dumps(logger_info, ensure_ascii=False))

        except json.decoder.JSONDecodeError:
            response_ = {
                "code": -4,
                "msg": "JSONDecodeError",
            }
            logger.error(response_)

        except KeyError as e:
            response_ = {
                "code": -1,
                "msg": f'param error:{e.args[0]}'
            }
            logger.error(response_)

        except ValueError as e:
            response_ = {
                "code": -2,
                "msg": f'param error:{e.args[0]}'
            }
            logger.error(response_)

        except EOFError:
            response_ = {
                "code": -3,
                "msg": "EOFError",
            }
            logger.error(response_)

        except Exception as e:
            response_ = {
                "code": -100,
                "msg": e.args[0]
            }
            logger.error(response_)

        finally:
            self.set_header("Content-type", "application/json;charset=UTF-8")
            self.write(json.dumps(response_, ensure_ascii=False, indent=None))
            self.flush()
