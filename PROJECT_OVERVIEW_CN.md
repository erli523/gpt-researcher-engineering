# GPT Researcher 工程实践说明

> 本仓库是基于 [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) 的学习与二次开发分支，保留上游 Apache-2.0 许可证和提交历史。本文明确区分上游能力与本次工程改动。

## 项目定位

GPT Researcher 是一个面向开放网络与本地资料的深度研究 Agent。它把一个研究问题拆成检索任务，抓取并筛选上下文，再生成带引用的长报告；同时提供 WebSocket 实时事件、报告导出、MCP 工具和多 Agent 研究流程。

本次实践重点不是增加聊天界面，而是验证并增强“规划—检索—工具执行—写作—引用”这条完整链路，尤其关注来源可追溯性、MCP 多轮调用和检索约束是否真的生效。

## 核心技术栈

| 层次 | 技术与用途 |
|---|---|
| Agent 与编排 | Python 3.12、LangChain、LangGraph、Anthropic/OpenAI 兼容模型接口 |
| 检索与工具 | DuckDuckGo/Tavily 等搜索后端、网页抓取、LangChain Documents、向量检索、MCP Python SDK |
| 服务端 | FastAPI、WebSocket、异步并发、报告历史与导出接口 |
| 前端 | Next.js、React、TypeScript、Tailwind CSS、PWA |
| 输出 | Markdown、DOCX、PDF，报告内保留 URL 引用 |
| 工程化 | Docker、pytest、隔离式离线回归、真实 API 端到端验收 |

## 核心思路

```text
研究问题
  → 生成研究计划和子查询
  → 并发搜索、抓取与来源过滤
  → 压缩/筛选可用上下文
  → 单 Agent 或多 Agent 分工写作
  → 事实检查、引用整理与多格式导出
```

普通研究流程由 researcher 完成规划、检索和写作。多 Agent 流程进一步拆分 planner、researcher、writer、fact checker、visualizer 和 publisher。MCP 作为独立工具入口接入文件系统等外部能力；工具结果只有经过协议化解析后才进入后续研究上下文。

## 本次自主改进

1. **详细报告复用已抓取来源**：对子主题复用并去重已有网页上下文，避免同一来源被重复抓取，同时在没有可恢复来源时拒绝生成貌似完整的报告。
2. **MCP 多轮工具执行**：把原先单轮调用扩展为有上限的连续工具交换，规范化分析文本，并覆盖真实 filesystem MCP 的读取、越界拒绝和最终报告生成。
3. **检索约束与来源兼容**：修复 DuckDuckGo 域名限制未强制执行的问题，并兼容标准 LangChain `Document.metadata.source`，减少来源丢失。
4. **Windows 前端兼容**：修复报告日志与下载链接的路径处理，保证前端能重新打开历史报告。

## 验证结果

- 单 Agent 完成真实规划、搜索、抓取和写作，样本报告包含 8 个来源，抽查的 7 个 URL 均可回溯。
- 多 Agent 完整执行 planner/researcher/writer/fact checker/visualizer/publisher，并生成 Markdown、DOCX、PDF。
- 深度研究样本以 breadth=3、depth=2 执行，累计 66 个来源和 500 个事件。
- MCP 使用官方 filesystem server，发现 14 个工具并完成多轮读文件研究；越界路径被拒绝。
- 离线回归汇总为 **550 passed、1 skipped、0 unresolved failures**。真实网络/API 验收与离线回归分别记录，没有用 Mock 结果替代业务验证。

## 适合作为项目经历的价值

这个项目体现了 Agent 任务分解、异步工具编排、MCP、检索约束、长文本生成和引用溯源。自主改动集中在可复现的工程问题，并配有失败样本和回归测试，能在面试中具体说明“为什么改、改了哪条调用链、如何证明没有破坏原功能”。

## 已知边界

- 搜索质量、网页可抓取性和模型输出仍受外部服务影响；当前结果是固定样本验收，不代表生产 SLA。
- 引用存在并不自动等于每条断言都被充分支持；覆盖式抽查中仍发现推断支持和过度陈述样本。
- 当前工作区中的 PWA 构建产物未纳入本次提交，避免把机器生成文件混入工程改动。

## 上游与许可证

- 上游仓库：<https://github.com/assafelovic/gpt-researcher>
- 上游文档：<https://docs.gptr.dev>
- 许可证：Apache License 2.0
