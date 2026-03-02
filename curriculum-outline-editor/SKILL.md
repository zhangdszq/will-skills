---
name: curriculum-outline-editor
description: >
  Teaching curriculum outline editor for 4-6 year old Chinese children's English courses.
  Expert in CEFR (Pre-A1/A1), CCSS, and Chinese National Kindergarten Curriculum Standards (3-6岁儿童学习与发展指南).
  Reads an Excel curriculum file, fixes unnatural/stilted language, applies the vocabulary recycling
  (复现) principle across lessons, then outputs a corrected Excel file plus a Chinese summary of all changes.
  Use when user provides a curriculum Excel and asks to "修改大纲", "检查课程", "优化词汇复现", or "fix curriculum outline".
---

# Curriculum Outline Editor

专为 4-6 岁中国儿童英语课程设计的大纲审校工具。

## 工作流程

### 第一步：读取 Excel

运行 `scripts/process_curriculum.py read <filepath>` 输出 JSON，获取所有 sheet、行列数据。

```bash
python3 scripts/process_curriculum.py read /path/to/file.xlsx
```

### 第二步：分析并修改内容

参考 `references/curriculum-principles.md` 中的详细原则，对每个 lesson 执行两类修改：

#### 修改类型 A：语言自然度（Language Authenticity）

目标：去除中式英语、生硬表达，换成 4-6 岁儿童课堂中真实使用的地道英语。

常见问题及对应处理：
- 过度形式化的指令（如 "Please stand up." → "Stand up!"）
- 动词搭配错误（如 "learn the colors" → "learn colors" 或 "practice colors"）
- 奇怪的功能句型（如 "I have a apple." → "I have an apple."）
- 不适龄的词汇/句式（如 "utilize" → "use"）
- 中文逻辑直译的英文（逐字对译的句子，需重写）

#### 修改类型 B：词汇复现原则（Vocabulary Recycling）

规则：
1. **新词密度**：每课引入新词不超过 5 个（4-6 岁认知负荷上限）
2. **首次出现**：新词在某 lesson 第一次出现，标记为 NEW
3. **复现窗口**：新词须在后续 1-3 课内至少复现一次（标记为 RECYCLE）
4. **渐进复现**：复现时嵌入新语境（不能原封不动重复同一活动）
5. **主题词优先**：主题核心词须保证在整个 unit 内多次复现

典型复现结构示例：
```
Lesson 1: yellow(NEW) blue(NEW) green(NEW)
Lesson 2: red(NEW) white(NEW) black(NEW) + yellow(RECYCLE) blue(RECYCLE)
Lesson 3: pink(NEW) orange(NEW) + green(RECYCLE) red(RECYCLE)
Lesson 4: purple(NEW) + pink(RECYCLE) orange(RECYCLE) + yellow(RECYCLE)
```

### 第三步：生成修改后的 Excel

运行 `scripts/process_curriculum.py write <original_path> <changes_json> <output_path>` 输出修改版 Excel。

```bash
python3 scripts/process_curriculum.py write /path/to/original.xlsx changes.json /path/to/output.xlsx
```

### 第四步：输出变更摘要

用中文逐条列出所有改动，格式如下：

```
## 修改摘要

### 语言自然度修改（共 X 处）
| Sheet | 位置 | 原文 | 修改后 | 原因 |
|-------|------|------|--------|------|
| ...   | ...  | ...  | ...    | ...  |

### 词汇复现调整（共 X 处）
| 词汇 | 原复现结构 | 调整后结构 | 说明 |
|------|-----------|-----------|------|
| ...  | ...       | ...       | ...  |

### 总计
- 语言修改：X 处
- 复现结构调整：X 处
- 新增复现安排：X 处
```

## 注意事项

- 始终保留原始文件，输出文件加 `-revised` 后缀（如 `outline-revised.xlsx`）
- 如 Excel 有多个 sheet，每个 sheet 均需处理
- 修改量大时先给用户确认修改方向，再执行批量修改
- 参考详细原则：`references/curriculum-principles.md`
