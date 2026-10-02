# 一手来源与适用范围

核验日期：2026-10-01。以下自主总结不复制长段原文。重新用于某模型生成时检查现行官方版本；创作原则和项目阈值不冒充模型保证。

| 来源 | 支持的原则 | 范围 |
|---|---|---|
| [MiniMax官方Ref2VA指南](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md) | 参考图/视频/声音作用明确；同一音色可组织不同情绪与节奏；对白/声音和具体动作需编排 | H3特定模式与当前指南，不扩展到所有模型 |
| [Runway Gen-4官方提示指南](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide) | 主要运动先行、简洁正向、逐项迭代；多人用位置或清楚身份区分；首图承担起始构图 | Gen-4；不能套其他型号输入契约/片长 |
| [Google DeepMind Veo提示指南](https://deepmind.google/models/veo/prompt-guide/) | 摄影、光线、风格、人物、场景、动作和声音可按目标组织 | 所展示Veo版本；详述也需实测执行 |
| [ACMI电影摄影教育](https://www.acmi.net.au/education/school-program-and-resources/film-it-cinematography/) | 景别、角度、构图、光线和移动共同传递信息和感受 | 电影语言教育，不是AI可执行性保证 |
| [Oklahoma State大学连续性剪辑](https://open.library.okstate.edu/introfilmtv/part/editing/) | 镜头关系、空间连续、视线/动作匹配，故意打破需有表达理由 | 基本剪辑语言，没有统一镜头配比 |
| [Oklahoma State大学声音章节](https://open.library.okstate.edu/introfilmtv/part/sound/) | 区分现场/主观/配乐，注意画内外、同步与声音透视；声音参与叙事 | 声音概念教育，不保证模型原生声音表现 |

本 skill 的状态账本、80分设计起点、代表性小样和重复警报为项目方法；按项目使用，不是来自上述来源的固定标准。新增规则标清官方、教育原则、项目推断或实测，并写适用条件。

## 战斗分支补充来源

核验日期：2026-10-02。以下支持电影/兵器动作的组织方法；本技能的高武力量规则、动作链与审片条件属于结合项目失败提出的导演方法，不是这些资料对AI生成的保证。

| 来源 | 支持的原则 | 范围 |
|---|---|---|
| [Film Independent：动作指导Darrin Prescott访谈](https://www.filmindependent.org/blog/bonus-stunt-coordinator-darrin-prescott-dissects-john-wicks-best-action-scenes/) | 摄影机位置与动作编排共同设计；具有角色/情境理由的动作比孤立招式更有意义 | 参与者的电影制作经验，不把具体招数或拍法变为统一配方 |
| [ASC：《卧虎藏龙》摄影制作访谈](https://theasc.com/article/crouching-tiger-hidden-dragon-cinematography/) | 相对自然舒适的写实视觉与武侠超常动作可以共存；场地、摄影和叙事共同塑造段落 | 摄影师的制作说明，不等于当前模型可复制该效果 |
| [国际武联套路规则：第27条剑枪等自选项目要求](https://www.iwuf.org/wp-content/uploads/2018/12/Rules_of_Taolu-English.pdf) | 剑、枪均有多样的动作技术和不同器械要求，可核对动作词的含义 | 历史发布版本的竞技套路资料，不用于声称当前竞赛标准、实战有效性或所有角色固定打法 |
| [《尚气》总视效监督Christopher Townsend访谈](https://www.artofvfx.com/shang-chi-and-the-legend-of-the-ten-rings-christopher-townsend-overall-vfx-supervisor/) | 特效随动作展开、与人物交互并产生后果；生物结构与表演影响重量、速度和尺度；特效不吞没角色 | 参与者的制作经验；本技能的属性推导与效果阶段是自建方法，不是该访谈公布的AI公式 |
| [《沙丘》重录混音师Ron Bartlett与Doug Hemphill等访谈](https://www.asoundeffect.com/dune-film-sound/) | 声音选择、删减、动态/密度对比及空间运动服务规模与主观体验 | 电影混音经验，不保证视频模型能精确控制声场、生成分轨或达到影院交付规格 |
