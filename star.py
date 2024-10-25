import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_ALAPI = "https://v2.alapi.cn/api/"
BASE_URL_VVHAN = "https://api.vvhan.com/api/" #https://api.vvhan.com/


@plugins.register(name="star",
                  desc="star插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class star(Plugin):
    content = None
    config_data = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f""
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        
        if self.content in [
            '白羊座', '白羊', '金牛座', '金牛', '双子座', '双子', '巨蟹座', '巨蟹', '狮子座', '狮子',
            '处女座', '处女', '天秤座', '天秤', '天蝎座', '天蝎', '射手座', '射手', '摩羯座', '摩羯',
            '水瓶座', '水瓶', '双鱼座', '双鱼'
        ]:
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__),"config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return
            
            reply = Reply()
            result = self.star()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def star(self):
        match self.content:
            case "白羊座" | "白羊":
                zodiac = "aries"
            case "金牛座" | "金牛":
                zodiac = "taurus"
            case "双子座" | "双子":
                zodiac = "gemini"
            case "巨蟹座" | "巨蟹":
                zodiac = "cancer"
            case "狮子座" | "狮子":
                zodiac = "leo"
            case "处女座" | "处女":
                zodiac = "virgo"
            case "天秤座" | "天秤":
                zodiac = "libra"
            case "天蝎座" | "天蝎":
                zodiac = "scorpio"
            case "射手座" | "射手":
                zodiac = "sagittarius"
            case "摩羯座" | "摩羯":
                zodiac = "capricorn"
            case "水瓶座" | "水瓶":
                zodiac = "aquarius"
            case "双鱼座" | "双鱼":
                zodiac = "pisces"
        try:
            # 主接口
            url = BASE_URL_VVHAN + "horoscope"
            payload = f"type={zodiac}&time=today"
            headers = {'Content-Type': "application/x-www-form-urlencoded"}
            response = requests.get(url, params=payload, headers=headers,timeout=2)
            if response.status_code == 200:
                json_data = response.json()
                if json_data['success'] and json_data['data']:
                    data = json_data['data']
                    text = (
                        f"{data['title']} ({data['time']}):\n\n"
                        f"💡【每日建议】\n宜：{data['todo']['yi']}\n忌：{data['todo']['ji']}\n\n"
                        f"📊【运势指数】\n"
                        f"总运势：{data['index']['all']}\n"
                        f"爱情：{data['index']['love']}\n"
                        f"工作：{data['index']['work']}\n"
                        f"财运：{data['index']['money']}\n"
                        f"健康：{data['index']['health']}\n\n"
                        f"🍀【幸运提示】\n数字：{data['luckynumber']}\n"
                        f"颜色：{data['luckycolor']}\n"
                        f"星座：{data['luckyconstellation']}\n\n"
                        f"✍【简评】\n{data['shortcomment']}\n\n"
                        f"📜【详细运势】\n"
                        f"总运：{data['fortunetext']['all']}\n"
                        f"爱情：{data['fortunetext']['love']}\n"
                        f"工作：{data['fortunetext']['work']}\n"
                        f"财运：{data['fortunetext']['money']}\n"
                        f"健康：{data['fortunetext']['health']}"
                    )
                    logger.info(f"主接口返回:{json_data}")
                    return text
                else:
                    logger.error(f"主接口返回参数错误:{json_data}")
                    raise ValueError('notfound')
            else:
                logger.error(f"主接口请求失败:{response.status_code}")
                raise requests.exceptions.ConnectionError
        except Exception as e:
            logger.error(f"主接口抛出异常:{e}")
            try:
                # 备用接口
                url = BASE_URL_ALAPI + "star"
                payload = f"token={self.config_data['alapi_token']}&star={zodiac}"
                headers = {'Content-Type': "application/x-www-form-urlencoded"}
                response = requests.get(url, params=payload, headers=headers)
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data['code'] == 200 and json_data['data']:
                        print(json_data)
                        data = json_data['data']['day']
                        text = (
                            f"📅 日期：{data['date']}\n\n"
                            f"💡【每日建议】\n宜：{data['yi']}\n忌：{data['ji']}\n\n"
                            f"📊【运势指数】\n"
                            f"总运势：{data['all']}\n"
                            f"爱情：{data['love']}\n"
                            f"工作：{data['work']}\n"
                            f"财运：{data['money']}\n"
                            f"健康：{data['health']}\n\n"
                            f"🔔【提醒】：{data['notice']}\n\n"
                            f"🍀【幸运提示】\n数字：{data['lucky_number']}\n"
                            f"颜色：{data['lucky_color']}\n"
                            f"星座：{data['lucky_star']}\n\n"
                            f"✍【简评】\n总运：{data['all_text']}\n"
                            f"爱情：{data['love_text']}\n"
                            f"工作：{data['work_text']}\n"
                            f"财运：{data['money_text']}\n"
                            f"健康：{data['health_text']}\n"
                        )
                        logger.info(f"备用接口返回:{json_data}")
                        return text
                    else:
                        logger.error(f"备用接口返回参数错误:{json_data}")
                else:
                    logger.error(f"备用接口请求失败:{response.status_code}")
            except Exception as e:
                logger.error(f"备用接口抛出异常:{e}")

        logger.error("所有接口都挂了,无法获取")
        return None
