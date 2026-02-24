from openai import OpenAI
import json
import time
from retrying import retry
@retry(stop_max_attempt_number=10, wait_fixed=5000)
def pdd_server(messeage,history=[]):
    '''拼多多客服'''
    with open("settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    with open("小智AI聊天机器人说明书.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    messages = [
        {'role': 'system', 'content': f"请尽力扮演infj型人格的拼多多真人客服，你非常耐心体贴，你会用尽可能简短且温柔富有同情心的话语帮消费者解决问题，不能答非所问，对于不合理的要求你也应该委婉拒绝。1.回答问题请参考使用说明书{text}。\n\n2.回答问题请参考对话历史：{str(history)}"},
        {'role': 'user', 'content': f"{messeage}"}
    ]
    
    try:
        completion = client.chat.completions.create(
            model=config['model'],
            messages=messages,
            temperature=config['temperature'],
            max_tokens=config['max_tokens'],
        )
        
        anwser = completion.choices[0].message.content
        return anwser
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        # 如果是账户余额不足或频率限制，等待较长时间再重试
        if hasattr(e, 'response') and e.response.status_code in [403, 429]:
            print("检测到API限制错误，将等待更长时间后重试...")
            time.sleep(30)  # 等待30秒
        else:
            time.sleep(5)   # 其他错误等待5秒
        raise e  # 重新抛出异常以触发重试机制

if __name__ == '__main__':
    print(pdd_server("小智怎么用",""))