# 录屏视频 GIF 分解说明

> 使用 ffmpeg 将录屏视频分解为 5 个 GIF 文件，每个 GIF 展示不同的操作流程。

---

## 📂 生成的文件

| 文件名 | 时间段 | 文件大小 | 描述 |
|--------|--------|----------|------|
| `gif_01_操作1.gif` | 0:00 - 0:21 | 6.8MB | 第一个操作步骤 |
| `gif_02_操作2.gif` | 0:21 - 0:42 | 7.4MB | 第二个操作步骤 |
| `gif_03_操作3.gif` | 0:42 - 1:03 | 9.9MB | 第三个操作步骤 |
| `gif_04_操作4.gif` | 1:03 - 1:24 | 6.7MB | 第四个操作步骤 |
| `gif_05_操作5.gif` | 1:24 - 1:45 | 3.6MB | 第五个操作步骤 |

**总大小**: 约 34.4MB（原视频: 91MB）

---

## 🛠 技术参数

### 原视频信息
- **分辨率**: 2826×1812
- **帧率**: 44.45 fps
- **时长**: 1分45.88秒
- **格式**: H.264 (.mov)
- **文件大小**: 91.5MB

### GIF 转换参数
- **分辨率**: 缩放至 799×512 (保持宽高比)
- **帧率**: 降至 10 fps
- **格式**: GIF
- **优化**: 自动色彩优化

---

## 📋 使用的 ffmpeg 命令

```bash
# 第一个 GIF (0-21秒)
ffmpeg -i "录屏2026-05-11 14.03.51.mov" \
       -t 21 \
       -vf "scale=800:512:force_original_aspect_ratio=decrease,fps=10" \
       -y gif_01_操作1.gif

# 第二个 GIF (21-42秒)  
ffmpeg -i "录屏2026-05-11 14.03.51.mov" \
       -ss 21 -t 21 \
       -vf "scale=800:512:force_original_aspect_ratio=decrease,fps=10" \
       -y gif_02_操作2.gif

# 第三个 GIF (42-63秒)
ffmpeg -i "录屏2026-05-11 14.03.51.mov" \
       -ss 42 -t 21 \
       -vf "scale=800:512:force_original_aspect_ratio=decrease,fps=10" \
       -y gif_03_操作3.gif

# 第四个 GIF (63-84秒)
ffmpeg -i "录屏2026-05-11 14.03.51.mov" \
       -ss 63 -t 21 \
       -vf "scale=800:512:force_original_aspect_ratio=decrease,fps=10" \
       -y gif_04_操作4.gif

# 第五个 GIF (84-结束)
ffmpeg -i "录屏2026-05-11 14.03.51.mov" \
       -ss 84 \
       -vf "scale=800:512:force_original_aspect_ratio=decrease,fps=10" \
       -y gif_05_操作5.gif
```

---

## 🎯 使用建议

### 展示方式
1. **按顺序展示**: 5个GIF按照操作流程顺序播放
2. **独立展示**: 每个GIF可以独立展示特定操作
3. **循环播放**: GIF自动循环，便于反复观看操作步骤

### 优化建议
如需进一步减小文件大小，可以：

```bash
# 使用更低的帧率 (5fps)
-vf "scale=800:512:force_original_aspect_ratio=decrease,fps=5"

# 使用更小的分辨率
-vf "scale=640:410:force_original_aspect_ratio=decrease,fps=10"

# 使用 gifsicle 优化 (如果可用)
gifsicle --optimize=3 --colors=128 input.gif > optimized.gif
```

---

## 📁 文件位置

所有生成的 GIF 文件已保存在项目根目录：
```
HelloVirtulCell/
├── gif_01_操作1.gif
├── gif_02_操作2.gif  
├── gif_03_操作3.gif
├── gif_04_操作4.gif
├── gif_05_操作5.gif
└── GIF分解说明.md (本文件)
```

---

## ✅ 完成状态

- [x] 视频分析完成
- [x] GIF 1: 操作1 (0-21s)
- [x] GIF 2: 操作2 (21-42s) 
- [x] GIF 3: 操作3 (42-63s)
- [x] GIF 4: 操作4 (63-84s)
- [x] GIF 5: 操作5 (84-105s)
- [x] 文档说明完成

**任务完成！** 🎉

---

*生成时间: 2026年5月11日*  
*工具: ffmpeg 4.4.2*  
*平台: Ubuntu 22.04 (ARM64)*