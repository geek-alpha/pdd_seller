# pdd_seller —— 拼多多电商 AI 客服

> 2026 最强拼多多电商免费 AI 客服，可自接 API。Playwright 驱动浏览器接管拼多多商家后台，
> AI 自动回复买家消息，7×24 小时值守店铺。

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Playwright](https://img.shields.io/badge/Playwright-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-green)

## ✨ 功能特性

- 🤖 **AI 自动回复**：接入 OpenAI 兼容 API（硅基流动/DeepSeek/OpenAI 等任意 base_url），
  自动识别买家消息并生成拟人回复（INFJ 温柔客服人设，简短、耐心、有同理心）；
- 🛒 **多店铺支持**：一套代码多店运行（极客阿尔法 / 极客贝塔 / 极客伽马 / 友权杂货店 / 解忧山货店...），
  每店独立 cookie 与会话历史；
- 📚 **产品知识库**：读取「小智AI聊天机器人说明书」作为回答依据，答得准、不瞎编；
- 🧠 **对话记忆**：按买家昵称维护历史会话，回复参考最近 5 轮上下文，不重复不跳戏；
- 🧩 **MCP 工具扩展**（进阶版）：注册商品查询等工具，AI 可主动调用工具找答案再回复；
- 🔐 **Cookie 自动管理**：首次手动登录自动保存，之后免登录；过期可一键重置；
- 🚀 **断线自愈**：弹窗自动关闭、异常自动重试（10 次退避），长期挂机不宕机。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置 API

编辑 `settings.json`：

```json
{
  "api_key": "sk-你的密钥",
  "base_url": "https://api.siliconflow.cn/v1",
  "model": "Qwen/Qwen3-8B",
  "max_tokens": 4096,
  "temperature": 0.2
}
```

> 任意 OpenAI 兼容接口都能用：换 `base_url` + `model` 即可。

### 3. 准备产品知识库

把店铺产品信息写进 `小智AI聊天机器人说明书.txt`，AI 会以此为依据回答买家问题。

### 4. 启动

```bash
python main.py
```

首次运行会弹出浏览器，**手动登录拼多多商家后台**（约 60 秒），登录成功后
cookie 自动保存到 `all_cookies.json`，之后每次启动免登录。

> 想重置 cookie？启动后 10 秒内按 `1` 回车即可。

## 📁 项目结构

```text
pdd_seller/
    ├── main.py          主程序：浏览器接管 + 消息监听 + 自动回复
    ├── chat_bot.py      AI 客服核心（OpenAI 兼容 API + 重试机制）
    ├── chat_bot_mcp.py  MCP 进阶版：工具注册/调用（商品查询等）
    ├── settings.json    API 配置
    ├── 小智AI聊天机器人说明书.txt   产品知识库
    ├── all_cookies.json 登录态（自动生成）
    ├── history.json     会话历史（自动生成）
    └── requirements.txt
```

## 🧠 工作原理

```
拼多多买家发消息
      ↓
Playwright 监听商家后台聊天窗口
      ↓
读取买家最新消息 + 最近 5 轮历史
      ↓
调用 AI（Qwen3-8B / 任意 OpenAI 兼容模型）
      ↓
参考产品说明书生成拟人回复
      ↓
自动填入输入框并发送
```

## 🧩 MCP 进阶版（友权杂货店）

`chat_bot_mcp.py` 实现了轻量 MCP 主机：注册 `ProductTool` 等工具后，
AI 会**主动调用工具查询商品信息**再组织回答——适合商品多、需要精确报价/库存的店铺。

```python
from chat_bot_mcp import MCPHost, MCPServer, ProductTool, GetProductTool

host = MCPHost("settings.json")
host.register_tool(ProductTool()).register_tool(GetProductTool())
server = MCPServer(host)
answer = server.process_request("这个多少钱？", history=[])
```

## 📌 路线图

- [x] 多店铺并行值守
- [x] MCP 工具扩展
- [ ] CSV 商品库外接（自行配置商品表，自动导入知识库）
- [ ] 飞书/钉钉告警联动（部分店铺已内置）

## ⚠️ 免责声明

本项目仅用于辅助商家合法经营，请遵守拼多多平台规则与相关法律法规。
请勿用于刷单、虚假宣传等违规行为。

## 📄 许可证

MIT