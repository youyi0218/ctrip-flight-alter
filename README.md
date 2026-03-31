# ctrip-flight-alter

携程机票价格监控脚本。

## 功能

- 读取 `url.txt` 中的携程单程机票网页 URL
- 自动识别 URL 中的出发地、到达地、出发日期，并与 `config.json.routes` 中的价格阈值匹配
- 通过真实浏览器抓取携程机票列表，并用页面展示价格做校验
- 识别航司、航班号、出发/到达时间、跨天到达、机场、总耗时、价格
- 价格按从低到高排序
- 每条行程一条通知
- 命中预期价时：推送该行程下所有命中的机票
- 未命中预期价时：推送提醒文案，并附带该行程最低价的 3 张机票
- 支持 PushPlus HTML 推送 + Resend 邮件推送
- 支持定时服务模式

## 准备

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 准备浏览器  
   支持系统已安装的 Chromium / Chrome，也可在 `config.json -> browser.executable_path` 指定路径。

3. 准备 `url.txt`  
   每行一个携程单程列表页 URL；前面可以保留备注文字，例如：

```text
出发：海口 到达：武汉 出发日期：5月1日 https://flights.ctrip.com/online/list/oneway-hak-wuh?depdate=2026-05-01&cabin=y_s_c_f&adult=1&child=0&infant=0
```

4. 可选：导出携程 Cookie  
   如果你希望复用登录态，可用浏览器插件 **Cookie-Editor** 导出到 `cookie.json`；不提供也能抓取公开机票页。

5. 复制配置

```bash
cp config.example.json config.json
```

## 配置

主要修改：

- `url_file`
- `pushplus.token`
- `email.api_key`
- `email.from`
- `email.to`
- `service.schedule_times`
- `service.capture_lead_minutes`
- `routes`

说明：

- `url_file` 指向 `url.txt`
- `routes` 主要用于覆盖每条航线的 `expected_price` / `enabled`
- `routes` 优先按 `source_url` 匹配；如果未提供 `source_url`，则按 `出发城市 + 到达城市 + 出发日期` 匹配 `url.txt` 中自动识别出的航线

标题格式：

```text
当日日期 航程 机票日期
```

例如：

```text
03月31日 武汉→海口 2026-05-05
```

## 运行

单次执行：

```bash
python flight_monitor.py
```

仅抓取不推送：

```bash
python flight_monitor.py --dry-run --dump-json
```

定时服务：

```bash
python flight_monitor.py --service
```

Service mode 会在配置的推送时间前预抓取价格，并在 `schedule_times` 对应时刻推送。

## Docker

### 本地构建

```bash
docker build -t ctrip-flight-alter .
docker run --rm \
  --user root \
  -v $(pwd):/app \
  ctrip-flight-alter
```

### 使用 GitHub Actions 构建好的镜像部署

工作流会构建并可推送镜像到：

```text
ghcr.io/youyi0218/ctrip-flight-alter:latest
```

拉取并运行：

```bash
docker pull ghcr.io/youyi0218/ctrip-flight-alter:latest
docker run -d \
  --name ctrip-flight-alter \
  --restart unless-stopped \
  --user root \
  -v $(pwd):/app \
  ghcr.io/youyi0218/ctrip-flight-alter:latest
```

### Docker Compose 部署

仓库已提供 `docker-compose.yml`，会把**当前项目目录**整体映射到容器 `/app`。

这些文件都会直接在项目根目录中读写：

- `config.json`
- `url.txt`
- `cookie.json`
- `.flight_monitor_history.json`
- `.flight_monitor_state.json`

如果当前目录里还没有程序文件，容器首次启动时会自动补出这些文件：

- `flight_monitor.py`
- `config.example.json`
- `README.md`
- `requirements.txt`
- `docker-compose.yml`
- `Dockerfile`
- `.gitignore`
- `.dockerignore`
- `docker-entrypoint.sh`
- `LICENSE`

如果当前目录里没有 `config.json`，容器也会自动用 `config.example.json` 生成一份。

首次部署：

```bash
docker login ghcr.io -u youyi0218
docker compose pull
docker compose up -d
```

第一次启动后，你只需要：

```bash
# 按需修改自动生成出来的 config.json
# 再把 url.txt / cookie.json 放到当前目录（cookie 可选）
docker compose restart
```

查看日志：

```bash
docker compose logs -f
```

停止：

```bash
docker compose down
```

如果你的环境使用旧版命令，也可以把 `docker compose` 改成 `docker-compose`。

容器默认启动命令：

```bash
python /app/flight_monitor.py --service --config /app/config.json
```

## GitHub Actions

已提供 Docker 构建工作流：

- `push`
- `workflow_dispatch`
