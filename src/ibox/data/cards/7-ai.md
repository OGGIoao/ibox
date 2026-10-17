# AI 工具

## 启动本地大模型服务（ollama）
- id: ollama-serve
- 别名: 启动ollama,开ollama服务,ollama后台,起服务
- 作用: 启动 ollama 本地服务（默认监听 11434 端口），供本机程序调用

### mac
- 命令: ollama
- 用法: `ollama serve` （后台常驻；macOS 也可用 `brew services start ollama` 开机自启）
- 示例: `ollama serve &`  → 后台启动；`curl -s http://localhost:11434/api/tags` 验证在跑
- 踩坑: 端口 11434 被占会起不来；`api/tags` 返回空 `{"models":[]}` 说明服务在跑但还没拉模型

### win
- 命令: ollama
- 用法: `ollama serve`（装了 Ollama 桌面版时它通常已在托盘里自动运行）
- 示例: `ollama serve` → 启动；另开一个窗口 `Invoke-RestMethod http://localhost:11434/api/tags` 验证在跑
- 踩坑: 托盘里已有 Ollama 时再 `ollama serve` 会报端口 11434 被占用——说明它本来就在跑；返回空 `models` 说明还没拉模型

## 下载一个本地模型
- id: ollama-pull
- 别名: 下载模型,拉模型,装模型,获取模型
- 作用: 从模型库拉取模型到本机（首次使用某模型必须这一步）

### mac
- 命令: ollama
- 用法: `ollama pull <模型名>`
- 示例: `ollama pull bge-m3` 后无需改配置，ibox 检测到本机有 bge-m3 会自动切换
- 踩坑: 网络中途掉线会断（如到 36%/87% 报 EOF），ollama 会缓存已下 blob **断点续传**，重试即可；极不稳时连 manifest 都拉不下，换网络/时段再试

### win
- 命令: ollama
- 用法: `ollama pull <模型名>`
- 示例: `ollama pull bge-m3` 后无需改配置，ibox 检测到本机有 bge-m3 会自动切换
- 踩坑: 网络中途掉线会断（如到 36%/87% 报 EOF），ollama 会缓存已下 blob **断点续传**，重试即可；极不稳时连 manifest 都拉不下，换网络/时段再试

## 和本地模型对话
- id: ollama-run
- 别名: 跑模型,聊天,和模型对话,开聊
- 作用: 进入模型对话（没有会自动先 pull）

### mac
- 命令: ollama
- 用法: `ollama run <模型名>`
- 示例: `ollama run qwen2.5:0.5b`  → 进对话筐，输入 `/bye` 退出
- 踩坑: 嵌入模型和聊天模型是两回事——ibox 用嵌入模型(nomic/bge-m3)，聊天请用 qwen2.5/llama 等

### win
- 命令: ollama
- 用法: `ollama run <模型名>`
- 示例: `ollama run qwen2.5:0.5b`  → 进对话筐，输入 `/bye` 退出
- 踩坑: 嵌入模型和聊天模型是两回事——ibox 用嵌入模型(nomic/bge-m3)，聊天请用 qwen2.5/llama 等

## 看已下载的本地模型
- id: ollama-list
- 别名: 看有哪些模型,模型列表,已装模型
- 作用: 列出本机已拉取的模型

### mac
- 命令: ollama
- 用法: `ollama list`
- 示例: 确认嵌入底座在位 —— 列表里应有 `nomic-embed-text` 或 `bge-m3`（ibox 语义检索依赖其中之一）
- 踩坑: 列表为空不代表服务没起，只是还没 pull 任何模型

### win
- 命令: ollama
- 用法: `ollama list`
- 示例: 确认嵌入底座在位 —— 列表里应有 `nomic-embed-text` 或 `bge-m3`（ibox 语义检索依赖其中之一）
- 踩坑: 列表为空不代表服务没起，只是还没 pull 任何模型

## 看正在运行的模型
- id: ollama-ps
- 别名: 看运行中的模型,模型进程,谁在跑
- 作用: 查看正在运行的模型进程（占多少内存）

### mac
- 命令: ollama
- 用法: `ollama ps`
- 示例: `ollama ps`  → 看已加载模型的显存/内存占用
- 踩坑: 模型加载后常驻，不用时 `ollama stop <名>` 释放资源

### win
- 命令: ollama
- 用法: `ollama ps`
- 示例: `ollama ps`  → 看已加载模型的显存/内存占用
- 踩坑: 模型加载后常驻，不用时 `ollama stop <名>` 释放资源

## 删除本地模型
- id: ollama-rm
- 别名: 删模型,卸载模型,移除模型
- 作用: 删除本机模型，释放磁盘

### mac
- 命令: ollama
- 用法: `ollama rm <模型名>`
- 示例: `ollama rm qwen2.5:0.5b`
- 踩坑: 删除后下次 run 会重新下载（再等一次）；`nomic-embed-text` 是 ibox 语义检索底座，别乱删

### win
- 命令: ollama
- 用法: `ollama rm <模型名>`
- 示例: `ollama rm qwen2.5:0.5b`
- 踩坑: 删除后下次 run 会重新下载（再等一次）；`nomic-embed-text` 是 ibox 语义检索底座，别乱删

## 用程序调用本地模型做向量化
- id: ollama-embed
- 别名: 向量化接口,embedding调用,语义向量,文本转向量
- 作用: 用任意程序调 ollama 做文本向量化（ibox 的语义检索就是这么干的）

### mac
- 命令: curl
- 用法: POST http://localhost:11434/api/embeddings   body: {"model":...,"prompt":...}
- 示例: `curl -s -X POST http://localhost:11434/api/embeddings -H "Content-Type: application/json" -d '{"model":"nomic-embed-text","prompt":"要向量化的文本"}'`
- 踩坑: 向量缓存 （`~/.config/ibox/vectors.json`） 按「内容hash+模型名」存，换模型会自动重建，不会用错旧向量

### win
- 命令: Invoke-RestMethod
- 用法: `Invoke-RestMethod http://localhost:11434/api/embeddings -Method Post -Body '<JSON>'`
- 示例: `Invoke-RestMethod http://localhost:11434/api/embeddings -Method Post -Body '{"model":"bge-m3","prompt":"你好"}'`
- 踩坑: Windows PowerShell 5.1 里 `curl` 是 Invoke-WebRequest 的别名，照抄 mac 的 curl 命令会报错；要用真 curl 写 `curl.exe`

## 查看模型的详细信息
- id: ollama-show
- 别名: 看模型详情,模型参数,模型信息,查模型配置
- 作用: 查看已拉模型的元信息（参数/上下文窗口/license/模板/系统提示），排查"为啥这个模型表现不对"

### mac
- 命令: ollama
- 用法: `ollama show <模型名>` ；对话中也可用 `/show`
- 示例: `ollama show nomic-embed-text`    → 确认它是嵌入模型(dim 768)、不可用于聊天
- 踩坑: 模型名带标签时要写全，如 `qwen2.5:0.5b`，否则按 latest 解析

### win
- 命令: ollama
- 用法: `ollama show <模型名>` ；对话中也可用 `/show`
- 示例: `ollama show nomic-embed-text`    → 确认它是嵌入模型(dim 768)、不可用于聊天
- 踩坑: 模型名带标签时要写全，如 `qwen2.5:0.5b`，否则按 latest 解析
