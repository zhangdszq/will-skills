---
name: minimax-tts
description: 使用 MiniMax API 将文本转换为语音（TTS）。当用户需要将文字转成语音、生成音频文件、朗读文本时使用。触发词：文字转语音、TTS、生成语音、朗读、minimax tts、语音合成。
---

# MiniMax TTS

使用 MiniMax `/v1/t2a_v2` 接口将文本转换为语音，输出 MP3 文件。

## 配置

凭据存储在 AI Team 配置目录 `~/.vk-cowork/.env`（优先级最高），也支持项目根目录 `.env` 或 `~/.env` 作为 fallback：

```bash
# ~/.vk-cowork/.env
MINIMAX_TTS_API_KEY=sk-api-...
MINIMAX_TTS_GROUP_ID=1922837262983238413
MINIMAX_TTS_VOICE_ID=Chinese (Mandarin)_Soft_Girl   # 默认音色
```

## 快速使用

运行 `scripts/tts.py`：

```bash
python3 ~/.claude/skills/minimax-tts/scripts/tts.py "要转换的文本" output.mp3
```

带选项：

```bash
python3 ~/.claude/skills/minimax-tts/scripts/tts.py "文本内容" output.mp3 \
  --voice "Chinese (Mandarin)_Soft_Girl" \
  --speed 1.0 \
  --emotion happy
```

## 脚本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `text` | 要转换的文本（位置参数） | 必填 |
| `output` | 输出文件路径（位置参数） | 必填 |
| `--voice` | 音色 ID | 读取 `MINIMAX_TTS_VOICE_ID` |
| `--speed` | 语速（0.5-2.0） | `1.0` |
| `--emotion` | 情绪 | 无（自然） |
| `--model` | 模型 | `speech-02-hd` |

## 可用音色（部分）

| voice_id | 描述 |
|----------|------|
| `Chinese (Mandarin)_Soft_Girl` | 温柔女声（默认） |
| `male-qn-qingse` | 青涩男声 |
| `female-shaonv` | 少女音 |
| `presenter_male` | 男性主播 |
| `audiobook_female_1` | 有声书女声 |

## 情绪选项

`happy` / `sad` / `angry` / `fearful` / `disgusted` / `surprised` / `neutral`

> 情绪仅在 `speech-02-hd` 和 `speech-02-turbo` 模型下有效。

## API 说明

- **Endpoint**: `https://api.minimax.io/v1/t2a_v2?GroupId={GROUP_ID}`
- **Auth**: `Authorization: Bearer {API_KEY}`
- **响应格式**: JSON，`data.audio` 字段为 hex 编码的音频数据
