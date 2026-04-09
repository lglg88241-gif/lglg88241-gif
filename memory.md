学习记忆快照 · 2026-04-09
【当前项目】Epic Game API
【已完成模块】

缓存策略（Caching Strategies）：实现了 GET /players/ 接口的内存缓存。

性能指标监控（Performance Metrics）：新增全局中间件，记录所有接口的耗时并写入响应头 X-Process-Time。理清了 FastAPI 洋葱模型与客户端 / 服务端 HTTP 缓存的交互逻辑。
【本次新增 / 修改】

新增文件：无

修改文件：

epic_game/main.py：新增 add_process_time_header 中间件。

新增接口或功能：全局接口处理耗时统计。
【当前进度】

正在进行：代码已提交至独立开发分支 feature-fastapi-epic-game，README 与记忆快照已更新。

遇到的问题 / 待解决：无。
【Roadmap 剩余】

下一个待学习 / 开发的节点：待选择。
【已安装的主要依赖】

fastapi-cache2

学习记忆快照 · 2026-04-09 (模块 3：全局错误处理)
【已完成模块】

全局错误处理 (Error Handling)：实现了 GameBusinessError 自定义异常及全局拦截器，统一了业务错误的返回格式。
【本次新增 / 修改】

修改文件：epic_game/main.py (定义异常与处理器), epic_game/routers/players.py (应用异常抛出逻辑)。

新增功能：标准化的业务错误 JSON 响应结构。
【当前进度】

正在进行：错误处理模块已落地，代码已提交至分支 feature-fastapi-epic-game。
