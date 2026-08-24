# 🧪 黑白胶片显影时间数据库（Film Dev Times DB）— BETA 测试版

> ⚠️ **本目录为 BETA 测试版**：以后的新改动都在这里进行，测试通过后再同步回正式版。
>
> ✅ **正式版（最终版，冻结）**：`/Users/zyh/Documents/harness/film-dev-db/` → 在线 **https://zyhiloveyou.github.io/film-dev-db/**
>
> 🧪 **测试版**：本目录 → 在线 **https://zyhiloveyou.github.io/film-dev-db-beta/**

全网搜集的黑白胶片 × 显影液冲洗时间数据库，覆盖 **手冲（倒置搅拌）与滚冲（连续搅拌/rotary）**、多种温度、多种稀释、增感（push）场景。

> 🌐 **在线访问（BETA）**：**https://zyhiloveyou.github.io/film-dev-db-beta/** （GitHub Pages，手机/电脑通用）
>
> 💻 **本地版**：`web/index.html` + `web/data_web.js` 两个文件，双击即用、离线可用。

---

## 一、数据总览（`data/summary.json`）

| 数据集 | 行数 | 胶片数 | 显影液数 | 来源 |
|---|---|---|---|---|
| `mdc_all.csv / .json` | **14,929** | 352 | 235 | Massive Dev Chart（digitaltruth.com，2026-07 版） |
| `rotary_guide.csv` | 11,998 | — | — | 由 MDC 20°C 手冲时间换算的滚冲时间（×0.85 / ×0.90） |
| `labo_los_alos.json` | 666 | 34 | 23 | Labo Los Alos 开源库（CC0，厂商官方数据） |
| `official_ilfotec_hc.csv` | 74 | 11 | 1 | Ilford Ilfotec HC 官方数据表（2025-02） |
| `official_foma.csv` | 93 | 4 | 21 | Foma 官方产品目录显影表 |
| `official_kodak_trix.csv` | 93 | 1 | 10 | Kodak Tri-X 400 官方数据表 F-4017 |
| `official_rollei.csv` | 164 | 5 | 29 | Rollei RPX 25/100/400、Retro 80S、Superpan 200 官方数据表 |
| `temp_conversion.csv` | 16 | — | — | 温度换算系数（Ilford/Kodak 规则 + Foma 官方系数） |

MDC 温度覆盖：**15°C ~ 40.5°C**（共 22 档，20°C 为主；组合中 1,126 个 胶片×显影液×稀释×ISO 有多个温度/来源记录）。MDC 备注链接覆盖 5,389 行（`mdc_row` 字段，可在官网查原始备注）。

---

## 二、文件结构

```
film-dev-db/
├── README.md
├── data/                      # 成品数据（可直接使用）
│   ├── mdc_all.csv            # ★ 主数据库：MDC 全量（编码 UTF-8）
│   ├── mdc_all.json           # ★ 同上 JSON 版
│   ├── rotary_guide.csv       # ★ 滚冲时间表（手冲→滚冲换算）
│   ├── temp_conversion.csv    # 温度换算系数
│   ├── official_*.csv         # 厂商官方数据表
│   ├── labo_los_alos.json     # 开源库原样（含增感/温度派生字段）
│   └── summary.json           # 汇总统计
├── sources/                   # 原始抓取件/PDF（备查）
│   ├── mdc_raw/               # MDC 每胶片查询的原始 markdown（157 个文件）
│   ├── ilford/ kodak/ foma/ adox/ rollei/   # 官方 PDF
│   └── films_labolosalos.json # Labo Los Alos 原始库
├── parse_mdc.py               # MDC 原始数据→CSV 解析器
├── parse_ilfotec_hc.py        # Ilfotec HC PDF 解析器
├── parse_rollei.py            # Rollei 数据表解析器
├── curate_foma.py             # Foma 官方表（人工核对固化）
├── curate_kodak_trix.py       # Kodak Tri-X 官方表（人工核对固化）
├── build_derived.py           # 生成 rotary_guide / temp_conversion / summary
└── fetch_mdc.sh               # MDC 抓取脚本（r.jina.ai 渲染）
```

---

## 三、字段说明

### `mdc_all.csv`（主库）
| 字段 | 说明 |
|---|---|
| `film` | 胶片名（如 `Ilford HP5+`、`Kodak Tri-X 400`、`Fomapan 400`） |
| `developer` | 显影液（MDC 规范化短名：`D-76`、`Rodinal`、`Xtol`、`Ilfotec DD-X`、`TMax Dev`…） |
| `dilution` | 稀释比（`1+50`、`Stock` 原液、`1+31`…） |
| `iso` | 感光度/增感档位（如 `400`、`800`、`1600`；`100-200` 表示区间） |
| `t35mm_min` / `t120_min` / `t_sheet_min` | 35mm / 120 / 页片（sheet）冲洗时间（分钟；空 = 该格式无数据） |
| `temp_c` | 温度 °C |
| `mdc_row` | MDC 官网备注行 ID（可在 https://www.digitaltruth.com/devchart.php?devrow=<id> 查看原始备注/出处） |
| `source` | 固定 `MassiveDevChart` |

> MDC 时间绝大多数为 **20°C 小罐倒置搅拌（inversion）** 数据；不同温度的行直接在 `temp_c` 区分，增感通过 `iso` 列区分。

### `rotary_guide.csv`（滚冲表）
对 MDC 中所有 20°C 手冲数据，按官方规则换算滚冲（连续搅拌）时间：
- `rotary_20c_min_0.85` = 手冲 × **0.85**（Ilford 官方规则：连续搅拌 = 间歇搅拌 × 0.85）
- `rotary_20c_min_0.90` = 手冲 × **0.90**（Rollei 官方规则：滚冲比手冲短 10–15%）

### 官方表（`official_*.csv`）
- `official_ilfotec_hc.csv`：Ilfotec HC 官方——**1+11@24°C（连续/机冲/滚冲）、1+15/1+31/1+47@20°C（小罐）**，含 Delta/FP4/HP5/PanF/SFX/Ortho Plus/Kentmere 各 ISO 与增感档
- `official_foma.csv`：Foma 官方——Fomapan 100/200/400 + Retropan 320，含时间**范围**（`t_min_minutes`~`t_max_minutes`，低值=低反差，高值=高反差）
- `official_kodak_trix.csv`：Tri-X 400 官方——小罐（30s 间隔倒置）与大罐（60s 间隔）两套 × 5 档温度（18/20/21/22/24°C）× 10 种显影液
- `official_rollei.csv`：Rollei 官方——20°C（个别 22/24/25°C）各显影液/稀释/ISO

### `labo_los_alos.json`
CC0 开源库，字段：`film`、`iso`、`dev`、`dil`、`t20`（20°C 时间）、`p1_20c`/`p2_20c`/`p3_20c`（+1/+2/+3 档增感时间）、`src`（官方数据出处，如 `Kodak F-4017`）。其 `meta.methodology` 记录了增感公式（Langford）与温度/滚冲规则。

---

## 四、使用方法

**查一个配方**（示例：Tri-X 400 在 Rodinal 1+50 @20°C）：
```bash
grep -E 'Kodak Tri-X 400,.*Rodinal,1\+50,400' data/mdc_all.csv
# → Kodak Tri-X 400,Rodinal,1+50,400,13.0,13.0,,20.0,4110,MassiveDevChart
#   （35mm=13 分钟，120=13 分钟）
```

**Python 快速查询**：
```python
import csv
rows = list(csv.DictReader(open('data/mdc_all.csv')))
hits = [r for r in rows if r['film']=='Ilford HP5+' and r['developer']=='Ilfotec DD-X']
for r in hits: print(r['dilution'], r['iso'], r['t35mm_min'], r['temp_c'])
```

**Excel**：直接用 Excel/Numbers 打开 `data/mdc_all.csv`，按 `film`/`developer` 列筛选即可；需要滚冲时间时按 `film`+`developer`+`dilution`+`iso` 关联 `rotary_guide.csv`。

---

## 五、手冲 vs 滚冲（重要规则）

| 来源 | 规则 |
|---|---|
| **Ilford**（Ilfotec HC 数据表） | 连续搅拌（滚冲/机冲）= 间歇搅拌时间 × **0.85**；1+11 稀释按 24°C 连续机冲计时 |
| **Rollei**（RPX 数据表） | 滚冲时间比手冲短 **10–15%**（×0.85~0.90） |
| **Kodak**（Tri-X F-4017） | 小罐 = 每 30s 倒置 5–7 次；大罐 = 每 60s 一次；页片盘显 = 连续搅拌；滚冲数据见各显影液数据表 |
| **Foma**（官方目录） | 螺旋罐：前 30s 连续搅拌，之后每分钟开头搅拌 10s |

本库的 `rotary_guide.csv` 已按上述规则生成可直接使用的滚冲时间。

---

## 六、温度换算

**通用规则（Ilford/Kodak 官方）**：从 20°C 起，每升高 1°C 时间缩短 10%，每降低 1°C 时间延长 10%（即 ×1.1^(20−T)）。

**Foma 官方系数**（`temp_conversion.csv`）：

| °C | 16 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 26 |
|---|---|---|---|---|---|---|---|---|---|
| 系数 | 1.45 | 1.20 | 1.10 | 1.00 | 0.90 | 0.85 | 0.80 | 0.75 | 0.60 |

> 例：20°C 9 分钟 → 24°C ≈ 9 × 0.75 ≈ 6.75 分钟。

---

## 八、网站使用说明（`web/`）

`web/index.html` + `web/data_web.js` 两个文件构成一个**响应式单页网站**（约 650KB，无任何依赖，离线可用），手机和电脑通用：

| 用法 | 步骤 |
|---|---|
| 电脑本地 | 双击打开 `web/index.html` 即可（数据已内嵌，无需联网） |
| 手机局域网访问 | 在 `web/` 目录运行 `python3 -m http.server 8080`，手机连同一 Wi-Fi 访问 `http://<电脑IP>:8080` |
| 公网部署 | 把两个文件传到 GitHub Pages / Vercel / Netlify 任意静态托管即可 |

**功能：**
- 🔍 **查配方（负片 / 正冲双入口）**：顶部切换「黑白负片」/「黑白正冲」
  - **负片**：搜索/字母浏览 352 款胶片 → 点开显示全部配方卡（显影液 × 稀释 × ISO 档位），每行给出 35mm / 120 / 页片时间
  - **正冲**（反转冲洗）：3 套官方黑白反转流程 —— [Rollei B&W Reversal Kit](https://www.rolleianalog.com/wp-content/uploads/2020/09/BW_Reversal-Kit_Instruction_DE_EN.pdf)（24°C，10 款胶片首显/二显表，含 Kodak TX 400 / Ilford Delta / Agfa Copex Rapid）、[Adox Scala Kit](https://www.fotoimpex.com/shop/images/products/media/59440_5_PDF-Datasheet.pdf)（Scala 50@20°C / Scala 160@24°C，Jobo 滚冲 -15%）、[Ilford PQ Universal 反转流程](https://www.ilfordphoto.com/wp/wp-content/uploads/2019/06/REVERSAL-180619.pdf)（Pan F+ / FP4+ / Delta 100，20°C）
- 🔄 **手冲 / 滚冲切换**：一键切换 手冲（官方原值）→ 滚冲 ×0.85（Ilford 规则）→ 滚冲 ×0.90（Rollei 规则）；正冲页的首显/二显时间同样联动
- 🌡️ **温度换算**：滑杆 15–30°C 实时换算（±10%/°C 规则）；有官方多温度记录的条目优先显示官方实测值（标蓝 = 换算值）
- 📋 **官方数据**：Ilfotec HC / Foma / Kodak Tri-X / Rollei 四张官方表，可搜索
- ❤️ **收藏**：常用胶片收藏（保存在浏览器本地）
- 🌙 **暗房模式**：右上角月亮按钮切换深色主题（暗房友好），记忆偏好
- 🔗 **深链接**：`index.html#film=Kodak%20Tri-X%20400` 直达配方；`#of=foma` 直达官方表；`#kind=rev` 直达正冲页

> 数据更新：重跑 `python3 build_web_data.py` 即可把 `data/` 下的最新 CSV 重新打包进 `web/data_web.js`。

---

## 九、数据来源与许可

| 来源 | 网址 | 许可/使用限制 |
|---|---|---|
| Massive Dev Chart | https://www.digitaltruth.com/devchart.php | 官网声明：允许**个人/教育用途**打印与分发，禁止任何形式转载（本库仅供个人查询，勿再公开转发） |
| FilmDev.org | https://filmdev.org | 社区配方库（含用户各温度/搅拌方式实测）；其站点要求**批量下载前先联系作者**，故本库未批量抓取，可按需在线查询 |
| Labo Los Alos Dev Chart | https://github.com/labolosalos/LaboLosAlosDevChartV1 | **CC0 1.0 公有领域**，可自由使用 |
| Ilford / Kodak / Foma / Rollei / Adox | 各厂商官网数据表 | 官方技术文档，可自由参考 |

抓取说明：digitaltruth 有 Cloudflare 反爬，本库通过 r.jina.ai 渲染代理抓取（2026-07-14 版数据，"Last updated: 14-Jul-2026"）；抓取频率 ≤ 20 次/分钟，未对目标站点造成压力。

---

## 十、注意事项

1. 所有时间都是**起点值（starting point）**，需结合自己的显影罐、搅拌手法、水浴温度、放大机类型（聚光/漫射）微调。
2. 同一 胶片×显影液×稀释×ISO 存在多行时，表示**多个来源/温度**的记录，可对比取平均或按 `mdc_row` 查备注选可信来源。
3. 增感（push）数据：MDC 通过 `iso` 列直接给出（如 Tri-X 400 → iso 1600）；LaboLosAlos 给出 +1/+2/+3 档时间；无官方数据时可用 Langford 公式：`T_push = T_base × 1.3^n`（T-grain 乳剂用 1.25）。
4. 滚冲（rotary）注意**药量**：滚冲机（如 Jobo）通常需要更少药液但显影更均匀，时间按第五节规则缩短后，建议先做一卷测试。
5. 本库数据为公开网络信息汇总，不构成厂商保证；商业用途请自行确认各来源许可。
