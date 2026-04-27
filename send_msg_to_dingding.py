import requests
import json
def send_realman_message_for_help(content, msgtype="text"):
    """
    最简单的钉钉消息发送函数
    
    :param content: 消息内容
    :param msgtype: 消息类型，默认为"text"，也可以是"markdown"
    :return: 发送结果
    """
    if msgtype == "text":
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
    elif msgtype == "markdown":
        # 如果是markdown格式，假设content是一个包含标题和文本的字典
        if isinstance(content, dict) and "title" in content and "text" in content:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": content["title"],
                    "text": content["text"]
                }
            }
        else:
            # 如果content是字符串，则作为markdown文本，标题与内容相同
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "通知",
                    "text": content
                }
            }
    
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    
    try:
        response = requests.post(url= "https://oapi.dingtalk.com/robot/send?access_token=f6ec8335e7608e7df4cd2d0ba148522ab14937191c1ce063b822aeb920cd462a", headers=headers, data=json.dumps(data))
        result = response.json()
        if result.get("errcode") == 0:
            return "消息发送成功。"
        else:
            return f"消息发送失败: {result}"
    except Exception as e:
        return f"发送消息失败: {e}"