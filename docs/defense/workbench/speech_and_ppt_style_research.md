# 答辩演讲与 PPT 风格调研

## 演讲稿写法

调研结论：答辩演讲不应按论文逐章朗读，而应按“问题 -> 方法 -> 做到了什么 -> 意义/不足”来组织。现场语言要比论文更短，每段先给结论，再解释技术名词。

参考依据：

- Texas A&M University Writing Center 的 defense 建议强调要清楚准备开场汇报，并能解释研究问题、方法和贡献：<https://writingcenter.tamu.edu/guides/resources/dissertation-defense.html>
- MIT 的 presentation tips 强调不要照读 slide、语速不要太急、每页只放一个主要想法，并提醒技术场合不要用过度商业化的花哨图形：<https://web.mit.edu/course/3/3.041/html/presentations.html>
- MIT OCW 的 presentation tips 建议字体大而易读，正文不要小于 18pt，推荐 24pt，标题 36pt 以上：<https://ocw.mit.edu/courses/7-91j-foundations-of-computational-and-systems-biology-spring-2014/739210581c47ea8e629bb79bcb2ff2a9_MIT7_91JS14_Present_tips.pdf>
- MIT Libraries 的无障碍演示建议强调不要在 slide 里放整段文字，要抽取关键词，并保证足够对比度：<https://libguides.mit.edu/internal-comms-resources/events-presentations>

适合本项目的口径：

- 先说“为什么普通助手不够”，再说“所以需要场景 Agent”。
- 每个技术名词先用一句白话解释，再保留英文/缩写。
- 不堆实现细节，不念代码文件名。
- 例子只用项目真实流程：拍照、前台动作闭环、改日程 Task、主动提醒/邮件、Obsidian 日记。
- 不用奇怪类比，不把老师带到项目之外的故事里。

## PPT 风格判断

推荐风格：白底或近白底、深色中文大字、少量蓝色强调、截图作为证据图嵌入。

不推荐：

- 黑底炫技风。
- 大面积渐变和发光元素。
- 商业发布会风格的夸张 hero 页。
- 一页塞很多小字、论文式流程图、仓库 README 长截图。
- 花哨模板导致老师看不清系统结构。

## 模板关键词

可以这样找模板：

- `毕业答辩 PPT 白底 简约 技术`
- `软件工程 毕业答辩 PPT 简洁 蓝白`
- `计算机 毕业设计 答辩 PPT 架构图`
- `thesis defense presentation template clean blue white`
- `technical thesis defense powerpoint template minimal`

找模板时重点看：

- 是否支持大标题 + 大图 + 少字。
- 是否有干净的架构图页、流程图页、对比页、Demo 页。
- 背景是否干净，截图放进去会不会乱。
- 字体是否正常，不要艺术字。
- 颜色是否克制，最好蓝白、黑白、浅灰加单一强调色。

## 对 codex-ppt skill 的判断

本地记录显示 `codex-ppt` 适合生成“整页图片式”的幻灯片，再组装成 `.pptx`。

也就是说：

- 最终文件是 PowerPoint 可打开的 `.pptx`，不是 HTML 网页。
- 但它更接近“每页是一张设计好的图片放进 PPTX”，不是传统 PowerPoint 里每个文本框、箭头、图形都能单独编辑的那种。
- 因此前期必须先确认大纲、视觉风格和样张；否则后期改字、移动单个元素会比较麻烦。

## 给本项目的模板选择建议

最适合找“简约技术答辩 / 蓝白科研答辩 / 软件工程架构答辩”类型模板。

模板应该至少有这些页型：

- 封面页：项目名清楚，背景干净。
- 问题页：左右对比或三点问题。
- 输入源页：大图卡片。
- 总体架构页：白底模块图。
- 流程页：粗箭头、少节点。
- Demo 路线页：时间线或三段流程。
- 总结页：3-4 个创新点。

不需要找特别“AI 科幻”“AR 炫酷”“元宇宙风”的模板。那些第一眼好看，但放上代码架构、官方截图和中文解释后，通常会变乱。
