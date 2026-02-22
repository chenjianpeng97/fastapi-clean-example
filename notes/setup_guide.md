# 本地环境（local）启动说明

说明：在 WSL 环境中按此流程操作。假设你已在项目根目录（包含 Makefile、pyproject.toml、README.md）下。

注意事项：

- 本项目通过环境变量 APP_ENV 决定读取哪个 config 目录（local / dev / prod）。
- 推荐在 WSL 下使用 Makefile / docker compose；如果你要用 Docker Desktop 图形界面启动 Postgres，请参照步骤 3 的「Docker Desktop 启动」部分。
- 所有命令在项目根目录执行（即包含 Makefile 的目录）。

前置:

1. desktop docker设置postgres数据库

```config
environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=123456
      - POSTGRES_DB=app_db
```

2. WSL环境中安装make命令

```sh
sudo apt install build-essential
make -v # 检查是否安装成功
```

3. WSL环境安装uv

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

步骤：

1. 设置环境变量并检查

```sh
# 在当前 shell 设置 APP_ENV=local
export APP_ENV=local
# 检查是否设置成功
echo $APP_ENV
# 检查（可选）
make env
# 若成功会显示
> APP_ENV=local
```

1. 生成 .env（供 Docker Compose 等使用）

```sh
# 运行 toml 配置生成 .env.local（Makefile 调用 config/toml_config_manager.py）
make dotenv
# 会输出生成路径，例如 .env.local（位于 config/local/）
```

1. 安装项目依赖并激活虚拟环境

- 推荐使用项目 README 推荐的 uv（可选），也可直接用系统 Python + venv/pip。
- 使用 uv（若未安装 uv，请按 README 的说明先安装 pipx 并 pipx install uv）：

```sh
# 安装项目依赖（生产 + dev group）
uv sync --group dev

# 激活虚拟环境
source .venv/bin/activate
```

4. 启动 PostgreSQL（两种方式，任选其一）

- 方式 A — 使用 Docker Desktop（GUI）：
  - 打开 Docker Desktop，选择 “Compose” 或直接在 GUI 中打开项目下 `config/local/docker-compose.yaml`（如果存在），然后启动服务 `web_app_db_pg`（或直接 Up All）。
  - 确保容器运行并监听端口（参见 .env.local 中的配置）。

- 方式 B — 在 WSL 用 Makefile（会调用 docker compose）：

```sh
# 需先 export APP_ENV=local（步骤1）
make up.db
# 若想在前台查看日志： make up.db-echo
```

5. 应用数据库迁移

```sh
# 在已激活虚拟环境 (.venv) 中执行
alembic upgrade head
# （alembic.ini 在项目根，可直接运行 alembic）
```

6. 启动应用（开发模式）

```sh
# 确保 APP_ENV=local 仍然在环境中
export APP_ENV=local

# 用 uvicorn 启动（与 Dockerfile 中一致的 factory 调用）
uvicorn app.run:make_app --factory --host 127.0.0.1 --port 8000 --loop uvloop
```

7. 验证

- 打开浏览器访问 http://127.0.0.1:8000/docs 查看 Swagger UI。
- 健康检查：GET /api/v1/health（或 README 中列出的其他接口）。

8. 常用清理/停止命令

```sh
# 停止并移除 Docker Compose 服务（若用 Makefile 管理）
export APP_ENV=local
make down

# 停止单个数据库容器（Docker Desktop 中直接停止或在 WSL 用 docker compose down）
```

附注与调试建议：

- 如果配置未加载，确认 APP_ENV 已导出（[`get_current_env`](src/app/setup/config/loader.py) 读取此变量）。
- 应用配置由 [`load_settings`](src/app/setup/config/settings.py) 读取并构建 `AppSettings`，所以启动前请保证生成的 toml/.env 与 `config/local/` 匹配。
- 如果 Alembic 报错，检查数据库是否已启动且 .env 中的连接信息正确（可在容器日志或 psql 中验证）。
- 需要在 IDE/运行配置中也设置 APP_ENV=local（方便直接从 IDE 启动）。

历史记录：

- 此文档位于 notes/local_setup.md，供本地快速启动参照。
