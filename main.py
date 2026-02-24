from playwright.sync_api import sync_playwright
import time
import random
import threading
import json
import os
from chat_bot import pdd_server
import sys
import getopt

def pdd_bot(cookies_file="all_cookies.json"):  # 添加cookies_file参数，默认值为"all_cookies.json"
    def get_user_input_with_timeout(timeout=10):
        """获取用户输入，超时后自动返回默认值"""
        result = {"input": None}

        def input_thread():
            user_input = input(f"需要重置cookie请在{timeout}秒内按数字键1并回车，并准备好拼多多商家版进行登录验证，不需要按其他键继续...")
            result["input"] = user_input

        thread = threading.Thread(target=input_thread)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            print(f"\n{timeout}秒已到，继续执行程序...")
            return False  # 超时未输入，默认不重置cookie
        else:
            return result["input"] == "1"

    if get_user_input_with_timeout(10):
        if os.path.exists(cookies_file):  # 使用传入的cookies_file参数
            os.remove(cookies_file)       # 使用传入的cookies_file参数

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        url = "https://mms.pinduoduo.com/chat-merchant/index.html#/"

        # 加载或设置 cookies
        if os.path.exists(cookies_file):  # 使用传入的cookies_file参数
            with open(cookies_file, "r", encoding="utf-8") as f:  # 使用传入的cookies_file参数
                web_cookies = json.load(f)
            context.add_cookies(web_cookies.get("pdd", []))
            print("Cookies 已加载")
        else:
            page.goto(url)
            print("请手动登录...")
            time.sleep(60)  # 给用户时间登录
            cookies = context.cookies()
            with open(cookies_file, "w", encoding="utf-8") as f:  # 使用传入的cookies_file参数
                json.dump({"pdd": cookies}, f, ensure_ascii=False, indent=4)
            print("Cookies 已保存")

        page.goto(url)
        print("登录成功！")

        if os.path.exists("history.json"):
            with open("history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {}
        while True:
            try:

                while True:
                    try:
                        try:
                            page.locator(".secondary-btn").click(timeout=500)
                        except:
                            pass
                        try:
                            page.locator(".close-button").click(timeout=500)
                        except:
                            pass
                        try:
                            page.locator(".cancel").click(timeout=500)
                        except:
                            pass
                        try:
                            page.locator(".gray-btn").click(timeout=500)
                        except:
                            pass
                        break
                    except:
                        pass
                customers = page.locator("xpath=/html/body/div[1]/div/div[1]/div[2]/div[2]/div[5]/div[1]/ul[1]/ul")
                if customers.count() == 0:
                    customers = page.locator("xpath=/html/body/div[1]/div/div[1]/div[2]/div[2]/div[6]/div[1]/ul[1]/ul")

                if customers.count() > 0:
                    for i in range(customers.count()):
                        customer = customers.nth(i)
                        nickname_locator = customer.locator("xpath=li/div[1]/div[2]/div[1]/span")
                        if nickname_locator.count() > 1:
                            # 如果匹配到多个元素，选择第一个或根据条件过滤
                            nickname = nickname_locator.first.inner_text()
                        else:
                            nickname = nickname_locator.inner_text()
                        print(nickname)
                        customer.click()

                        anwser = "你好,请问需要什么帮助吗？"
                        list_news = page.locator("xpath=/html/body/div[1]/div/div[1]/div[3]/div[1]/div[8]/div[2]/div[1]/div[3]/ul/li")

                        if list_news.count() > 0:
                            last_text = list_news.last.inner_text()
                            print("客户最后一句话是：", last_text)
                            anwser = pdd_server(last_text, history.get(nickname, [])[-5:])  # 最多取最近5条历史记录

                        page.locator("#replyTextarea").fill(anwser)
                        page.locator(".send-btn").click()

                        if nickname not in history:
                            history[nickname] = []
                        history[nickname].append({"role": "user", "content": last_text})
                        history[nickname].append({"role": "assistant", "content": anwser})

                        with open("history.json", "w", encoding="utf-8") as f:
                            json.dump(history, f, ensure_ascii=False, indent=4)

            except Exception as e:
                print(e)
                time.sleep(1)

def main():  # 新增main函数处理命令行参数
    cookies_file = "all_cookies.json"  # 默认cookies文件名

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["cookies="])
    except getopt.GetoptError:
        print('main.py -c <cookies_file> 或 main.py --cookies <cookies_file>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-c", "--cookies"):
            cookies_file = arg

    pdd_bot(cookies_file)

if __name__ == "__main__":
    main()  # 调用新增的main函数