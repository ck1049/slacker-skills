# 可机查计划数据

只在跨镜状态/声音条件复杂、确实需要自动查错时使用，不要求普通单镜写JSON。脚本Python3.10+、仅标准库；不触发生成、下载、收费或上传。

入口：`python scripts/validate_scene_plan.py plan.json --phase planning`，可加 `--report report.json` 输出新报告；拒绝覆盖既有报告。退出码0表示声明检查无错误，1表示逻辑错误，2表示输入/文件错误。警报不阻断，不自动认定画面无聊。

## 字段

- `entities`：稳定物理/角色ID到说明，至少注册出场角色、道具和声音来源；两台表要有可辨识身份，脚本不能判断两张图是否实际一样。
- `initial_state`：被跟踪对象的完整起始状态，字段值为字符串/数字/布尔/null。只登记对剧情有用的字段；null为未知，规划阶段警报、执行阶段错误。角度等数值在`entities`的说明中另记单位、零轴、方向和观察坐标（如`angle_basis`）；仅数字相同不足以证明同一视觉角度，坐标仍须人工/媒体核对。
- `tolerances`：可选数值量测容差，键为`对象.字段`；默认精确一致。来自测量误差，不能用大容差掩盖重新复位。
- `units`：顺序数组，每镜唯一字符串`id`、`cast`、`composition`、`camera`、可选`dialogue`和正数`duration_s`（规划镜长而非API保证）；需要跨镜记录的对象必须在本镜`start_state`/`end_state`完整列出当前字段。
- `events`：按时间顺序列本镜事件：唯一`id`、具体`cause`、前提`requires`和改变`effects`。改变不能凭空发生；已建立的连续过程也写出持续原因。事件效果逐个应用；终态必须匹配。
- `sounds`：`domain`为`diegetic`/`offscreen_diegetic`/`subjective`/`score`，都写`purpose`。现场声注册`source`与`requires`，离散声绑定本镜`at_event`，声音条件在该事件**效果之后**检查；已经存在的连续环境声写`continuous:true`，条件在本镜起态检查。现场声另写`stop_condition`说明如何停下或有意延续到哪里；可用`ends_at_event`绑定本镜终止事件，脚本查存在与先后顺序。声明`duration_s`后，每声音另写`window_s:[开始秒,结束秒]`，检查在镜长内，不认证实际音轨。需要事件发生前的声响时拆为先发声再变状态两个事件。主观声写`listener`，配乐不冒充物件实际发声。
- 有意违反普通物理的声事件写`exception_rule`、`setup_unit`（本镜或先前镜）、`reaction`、`payoff`（兑现或明确有意悬念）。这只是声明完整性，仍需检查观众能否看懂。普通物理条件不成立时，不用异常字段偷偷免掉条件，应正确分类/重设计。
- 执行检查另要`selected`：`media_path`、`end_evidence`与`state_reviewed:true`；路径相对计划所在目录或绝对路径。实际状态复核后才能填true；文件存在不代表内容真实，脚本也不做媒体验证。执行账本须填实际状态，不能把计划值换标签当实测。

## 两镜例子

以下仅为规划，无生成素材或虚构文件：

```json
{
  "entities": {
    "chenmo": {"kind": "character"},
    "load-gauge": {"kind": "prop", "identity": "左台银色圆壳黑针", "angle_basis": "表盘平面：右向水平为0度，上方为正角，下降为顺时针；不是压力单位"}
  },
  "initial_state": {"load-gauge": {"needle_deg": 47, "load": "charged"}},
  "units": [
    {
      "id": "release", "cast": ["chenmo"], "composition": "insert", "camera": "locked",
      "start_state": {"load-gauge": {"needle_deg": 47, "load": "charged"}},
      "events": [{"id": "unload", "cause": "陈默松开已确认的释放阀",
        "requires": {"load-gauge": {"load": "charged"}},
        "effects": {"load-gauge": {"needle_deg": 35, "load": "partially_released"}}}],
      "sounds": [{"domain": "diegetic", "source": "load-gauge", "at_event": "unload",
        "requires": {"load-gauge": {"load": "partially_released"}}, "purpose": "阀释放后的机械泄压声", "stop_condition": "本镜少量泄放结束后停止，不在等待镜重放"}],
      "end_state": {"load-gauge": {"needle_deg": 35, "load": "partially_released"}}
    },
    {
      "id": "wait", "cast": ["chenmo"], "composition": "over-shoulder", "camera": "locked",
      "dialogue": "还有一点。", "events": [], "sounds": [],
      "start_state": {"load-gauge": {"needle_deg": 35, "load": "partially_released"}},
      "end_state": {"load-gauge": {"needle_deg": 35, "load": "partially_released"}}
    }
  ]
}
```

若第二镜重新写47度，会报`state_reset`；终态改变却无相应事件报`unexplained_transition`；离散物件声没有事件报`sound_trigger`；未供电/未连接却声明正常播放条件报`sound_precondition`。四个连续固定单人对白近景提示检查节奏，不判定必然不好看。

检查器不解析自然语言因果真假，不能从自由提示词可靠推断连接/动力条件；条件遗漏或写错仍需导演复核。角度坐标说明与真实姿态、声窗与真实发声/停止都还须观感核对。它不代替官方参数检查、对话/音色绑定、画面/音轨解码、机械动作实测或创作评分。
