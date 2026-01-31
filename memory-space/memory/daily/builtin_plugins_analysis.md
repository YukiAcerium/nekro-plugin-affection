# NekroAgent 内置插件深度分析

**分析日期**: 2026-01-29
**分析者**: Yuki
**目标**: 读透每一个内置插件的设计和实现

---

## 📊 插件总览

### 单文件插件 (16个)
1. `ai_voice.py` - AI 语音合成
2. `basic.py` - 基础交互功能
3. `bilibili_live_utils.py` - Bilibili 直播工具
4. `dice.py` - 骰子插件
5. `dynamic_importer.py` - 动态导入器
6. `email_utils.py` - 邮件工具
7. `emotion.py` - 表情包管理 ⭐
8. `google_search.py` - Google 搜索
9. `group_honor.py` - 群荣誉系统
10. `history_travel.py` - 历史回溯
11. `judgement.py` - 评判系统
12. `minecraft_utils.py` - Minecraft 工具
13. `note.py` - 笔记功能
14. `status.py` - 状态查询
15. `timer.py` - 定时器
16. `view_image.py` - 图片查看

### 目录插件 (2个)
17. `draw/` - 绘图系统
18. `github/` - GitHub 集成

---

## 🔍 分析模板

对于每个插件，我将从以下维度分析：

1. **功能概述** - 插件做什么
2. **核心方法** - 实现了哪些沙盒方法
3. **配置系统** - 如何管理配置
4. **存储使用** - 如何持久化数据
5. **设计模式** - 采用的设计模式
6. **最佳实践** - 可学习的代码规范
7. **创新点** - 独特的实现方式

---

*文档创建时间: 2026-01-29 15:35*
