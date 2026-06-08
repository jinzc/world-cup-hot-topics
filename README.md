# 🏆 2026世界杯话题热榜

聚合 **微博、百度、B站、知乎、抖音、虎扑、懂球帝、小红书、咪咕** 等平台的世界杯相关热点话题。

> 自动过滤：只展示与世界杯相关的内容（球星、球队、赛事术语等）

## 访问地址

部署后访问：`https://你的用户名.github.io/world-cup-hot-topics/`

## 技术栈

- 前端：纯 HTML/CSS/JS（无需构建）
- 后端：Python3 标准库爬虫（无额外依赖）
- 部署：GitHub Actions 自动更新 + GitHub Pages

## 更新频率

- **每小时整点**自动更新（UTC 时间）
- 支持手动触发 GitHub Actions

## 部署步骤

### 1. 创建 GitHub 仓库

1. 在 GitHub 创建仓库 `world-cup-hot-topics`
2. 上传本项目所有代码（保持文件夹结构）
3. GitHub Actions 会自动开启

### 2. 开启 GitHub Pages

- 仓库 → **Settings** → **Pages**
- Source 选择 `Deploy from a branch`
- Branch 选择 `main`，目录 `/ (root)`
- 点击 Save

### 3. 配置小红书 Cookie（可选但推荐）

小红书无公开 API，需要配置 Cookie 才能抓取：

**方式 A：GitHub Secrets（推荐，安全）**
1. 浏览器打开 https://www.xiaohongshu.com/explore
2. 登录账号（建议用小号）
3. F12 → Console → 输入 `document.cookie` → 回车 → 复制输出
4. 仓库 → **Settings** → **Secrets and variables** → **Actions**
5. 点击 **New repository secret**
6. Name 填 `XIAOHONGSHU_COOKIE`
7. Secret 填你复制的 Cookie 内容
8. 点击 **Add secret**

**方式 B：本地环境变量**
```bash
export XIAOHONGSHU_COOKIE="你的Cookie"
python scripts/fetch_hot_topics.py
```

**方式 C：直接修改代码（不推荐）**
编辑 `scripts/fetch_hot_topics.py`，找到 `XIAOHONGSHU_COOKIE = os.environ.get(...)` 改为直接赋值。

> ⚠️ **注意**：Cookie 会过期（通常几天到几周），失效后需重新获取。

### 4. 首次运行

- 进入 **Actions** 页面 → `Update World Cup Hot Topics` → **Run workflow**
- 等待运行完成，数据会自动提交到 `data/world_cup_topics.json`
- 访问 GitHub Pages 地址即可查看

## 文件结构

```
world-cup-hot-topics/
├── .github/workflows/
│   └── update.yml              # GitHub Actions 配置（支持 Secrets）
├── data/
│   └── world_cup_topics.json  # 热榜数据（自动更新）
├── scripts/
│   ├── fetch_hot_topics.py    # 主爬虫脚本
│   └── utils.py               # 工具函数（关键词过滤）
├── index.html                 # 前端页面
└── README.md
```

## 平台抓取状态

| 平台 | 状态 | 数据来源 | 说明 |
|------|------|---------|------|
| 微博 | ✅ 可用 | 公开 API | 自动过滤世界杯关键词 |
| 百度 | ✅ 可用 | 公开 API | 自动过滤世界杯关键词 |
| B站 | ✅ 可用 | 公开 API | 自动过滤世界杯关键词 |
| 知乎 | ✅ 可用 | 公开 API | 自动过滤世界杯关键词 |
| 抖音 | ⚠️ 可能受限 | 公开 API | 可能需反爬验证 |
| 虎扑 | ⚠️ 可能受限 | 移动端 API | 接口可能变动 |
| 懂球帝 | ⚠️ 可能受限 | 内容 API | 接口可能变动 |
| 小红书 | ❌→⚠️ | **需 Cookie** | 无公开 API，配置 Cookie 后可用 |
| 咪咕 | ⚠️ 数据有限 | 网页端 | 无公开 API，网页正则抓取 |

## 核心逻辑

1. **全量抓取**：从各平台抓取全站热榜/热搜数据
2. **关键词过滤**：使用 200+ 世界杯关键词（球星、球队、赛事术语等）自动筛选
3. **数据存储**：保存为 `data/world_cup_topics.json`
4. **前端展示**：按来源分列展示，支持平台筛选

## 自定义配置

### 调整关键词

编辑 `scripts/utils.py` 中的 `WORLD_CUP_KEYWORDS` 列表，添加或删除关键词。

### 修改更新频率

编辑 `.github/workflows/update.yml` 中的 `cron` 表达式：
- `0 * * * *` — 每小时（世界杯期间推荐）
- `0 */2 * * *` — 每 2 小时
- `0 0,6,12,18 * * *` — 每 6 小时

## 免责声明

本项目仅供学习交流使用，所有数据来源于各平台公开接口，版权归原平台所有。
