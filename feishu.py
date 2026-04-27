import requests
import json



import requests
import time
import json
from typing import Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===================== 配置区（替换成你的自建应用信息）=====================
APP_ID = "cli_a8a87914e131900d"          # 替换为实际值
APP_SECRET = "xtX5mJaxU3C3NYkp7TuOjc6jcIfPkEts"  # 替换为实际值
CHAT_ID = "oc_db39129e7be54509cd647f7ad912ef5b"  # 飞书开放平台可查
# 自建应用限流规则（飞书官方：50次/秒、1000次/分钟）
QPS_LIMIT = 50
MINUTE_LIMIT = 1000
MESSAGE_MAX_SIZE = 20 * 1024  # 消息体最大20KB
# token缓存（有效期2小时，避免重复调用接口）
TOKEN_CACHE = {
    "tenant_access_token": None,
    "expire_time": 0
}

# ===================== 初始化配置 =====================
# 会话初始化（带网络重试）
session = requests.Session()
retry_strategy = Retry(
    total=3,  # 总重试次数
    backoff_factor=1,  # 指数退避：1s→2s→4s
    status_forcelist=[429, 500, 502, 503, 504]  # 触发重试的状态码
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
# 限流计数器
call_timestamps = []

# ===================== 核心工具函数 =====================
def check_rate_limit() -> None:
    """限流校验：控制QPS和分钟调用量，复用自建应用规则"""
    now = time.time()
    global call_timestamps
    # 过滤1分钟前的记录，校验分钟限额
    call_timestamps = [t for t in call_timestamps if now - t < 60]
    if len(call_timestamps) >= MINUTE_LIMIT:
        sleep_time = 60 - (now - call_timestamps[0]) + 0.1
        time.sleep(sleep_time)
    # 过滤1秒前的记录，校验QPS限额
    if len([t for t in call_timestamps if now - t < 1]) >= QPS_LIMIT:
        time.sleep(1.1)
    # 记录本次调用时间
    call_timestamps.append(time.time())

def get_tenant_access_token(force_refresh: bool = False) -> Optional[str]:
    """
    获取/缓存tenant_access_token（有效期2小时）
    :param force_refresh: 是否强制刷新token，默认False
    :return: 有效的token/None
    """
    now = time.time()
    # 缓存有效且不强制刷新，直接返回
    if TOKEN_CACHE["tenant_access_token"] and TOKEN_CACHE["expire_time"] > now and not force_refresh:
        return TOKEN_CACHE["tenant_access_token"]
    
    # 调用飞书接口获取新token
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        resp = session.post(
            url=url,
            json={"app_id": APP_ID, "app_secret": APP_SECRET},
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 0:
            token = result.get("tenant_access_token")
            expire = result.get("expire", 7200)  # 默认为7200秒（2小时）
            # 更新缓存（提前10分钟过期，避免边界问题）
            TOKEN_CACHE["tenant_access_token"] = token
            TOKEN_CACHE["expire_time"] = now + expire - 600
            return token
        else:
            print(f"获取token失败：{result.get('msg')}（code:{result.get('code')}）")
            return None
    except Exception as e:
        print(f"获取token异常：{str(e)}")
        return None

# ===================== 消息发送主函数 =====================
def send_app_msg(msg: Dict, chat_id: str = CHAT_ID) -> Dict:
    """
    飞书自建应用发送消息（群/个人）
    :param msg: 消息内容体，如{"text":"测试消息"}
    :param chat_id: 接收方chat_id，默认使用配置区的CHAT_ID
    :return: 调用结果（success: bool, data: 响应体, error: 错误信息）
    """
    try:
        # 1. 校验消息体大小
        msg_str = json.dumps(msg)
        if len(msg_str.encode("utf-8")) > MESSAGE_MAX_SIZE:
            return {"success": False, "data": None, "error": f"消息体超过20KB限制，当前大小：{len(msg_str.encode('utf-8'))}B"}
        
        # 2. 获取有效token
        token = get_tenant_access_token()
        if not token:
            # 首次获取失败，强制刷新一次
            token = get_tenant_access_token(force_refresh=True)
            if not token:
                return {"success": False, "data": None, "error": "获取tenant_access_token失败，无法发送消息"}
        
        # 3. 限流校验
        check_rate_limit()
        
        # 4. 构造请求发送消息
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        req_data = {
            "receive_id": chat_id,
            "content": json.dumps(msg),
            "msg_type": "text"  # 固定为text，与消息体匹配
        }
        resp = session.post(
            url=url,
            json=req_data,
            headers=headers,
            timeout=15
        )
        resp.raise_for_status()  # 抛出4xx/5xx HTTP异常
        result = resp.json()
        
        # 5. 处理飞书返回结果
        if result.get("code") == 0:
            return {"success": True, "data": result, "error": None}
        else:
            # 特殊处理：token过期（code=99991663），强制刷新后重试一次
            if result.get("code") == 99991663:
                token = get_tenant_access_token(force_refresh=True)
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    resp = session.post(url=url, json=req_data, headers=headers, timeout=15)
                    result = resp.json()
                    if result.get("code") == 0:
                        return {"success": True, "data": result, "error": None}
            return {"success": False, "data": result, "error": f"飞书接口返回错误：{result.get('msg')}（code:{result.get('code')}）"}
    
    except requests.exceptions.HTTPError as e:
        return {"success": False, "data": None, "error": f"HTTP请求错误：{str(e)}"}
    except requests.exceptions.Timeout:
        return {"success": False, "data": None, "error": "请求飞书接口超时"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "data": None, "error": "网络连接失败，无法调用飞书接口"}
    except Exception as e:
        return {"success": False, "data": None, "error": f"发送消息异常：{str(e)}"}

# ===================== 测试调用 =====================
if __name__ == "__main__":
    # 测试文本消息体
    test_msg = {
        "text": "飞书自建应用机器人测试成功！\n带限流+token缓存+异常处理"
    }
    # 发送消息
    res = send_app_msg(test_msg)
    # 打印结果
    if res["success"]:
        print(f"发送成功：{json.dumps(res['data'], ensure_ascii=False)}")
    else:
        print(f"发送失败：{res['error']}")