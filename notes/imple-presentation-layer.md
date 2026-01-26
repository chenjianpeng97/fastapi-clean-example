name: imple-presentation-layer
description: 在 fastapi-clean-example 项目中实现表现层时使用此技能。侧重于 FastAPI 集成、输入验证和适当的依赖管理。
---

# 表现层技能

此技能为在 `fastapi-clean-example` 项目中实现和测试表现层提供了指导。

# 何时激活

- 实现新的 API 端点。
- 修改现有 API 端点行为。
- 修复与 HTTP 请求/响应处理或路由相关的错误。
- 添加表现层测试。

## 1. 表现层的核心原则

### A. 精简控制器
- 控制器必须尽可能精简，除了基本的输入验证和路由之外，不包含任何逻辑。它们的作用是充当应用程序和外部系统 (FastAPI) 之间的中介。
- 它们应该协调对应用层 (Interactors/Query Services) 的调用，并处理 HTTP 特定的问题（状态码、响应序列化）。

### B. 输入验证
- **基本验证**：控制器负责基本的输入验证，例如检查传入请求的结构、类型安全和必填字段。这通常使用 Pydantic 模型完成。
- **业务规则验证**：业务规则验证（例如，唯一性检查、特定值约束）属于领域层或应用层。表现层应**避免**使用 Pydantic 进行业务规则验证，以避免将业务逻辑与外部库耦合。

### C. 依赖管理
- 表现层是外部层，依赖于内部层（应用层和领域层）。它本身**不应**包含任何业务逻辑。
- 在必要时，它可以直接依赖领域层以获取异常或枚举，从而绕过应用层。
- 依赖注入 (`dishka`) 用于将交互器和查询服务注入到控制器中。

## 2. 实现表现层组件

### A. 控制器 (`src/app/presentation/http/controllers/`)
- **目的**：定义 API 端点，处理传入的 HTTP 请求，执行基本的输入验证，委托给应用层，并格式化 HTTP 响应。
- **实现**：
    - 使用 `fastapi.APIRouter` 进行路由。
    - 使用 `fastapi_error_map.ErrorAwareRouter` 进行声明式错误处理和异常到 HTTP 状态码的映射。
    - 使用 `dishka.FromDishka` 和 `@inject` 注入依赖项（交互器、查询服务）。
    - 通过 Pydantic 模型（例如 `BaseModel`）接受请求数据。这些模型应主要用于 OpenAPI 架构生成和基本结构验证。
    - 在将 Pydantic 请求模型传递给交互器/查询服务之前，将其转换为应用程序特定的 DTO。
    - 返回应用程序特定的查询模型或成功命令的 `None`。
- **示例**：`src/app/presentation/http/controllers/account/change_password.py`、`src/app/presentation/http/controllers/users/create_user.py`

### B. 功能实现：身份验证和授权示例

- **目的**：通过 HTTP 安全地暴露和管理特定功能（例如，用户身份验证/授权），通过协调与内部层的交互来遵守清洁架构的依赖规则。
- **表现层在特定功能中的作用**：
    - **HTTP 特定处理**：管理功能相关数据和凭据的传输（例如，从请求体/查询/路径中提取请求数据，设置响应头或 cookie）。
    - **API 暴露**：使用 FastAPI 的路由功能定义功能的 API 端点（例如，登录、注销、用户创建）。
    - **安全标记**：在适用时，利用 FastAPI 的 `Security` 依赖项和 OpenAPI 安全方案声明路由的身份验证/授权要求，以帮助文档和强制执行。
    - **输入/输出映射**：将传入的 HTTP 请求（通常是用于验证的 Pydantic 模型）映射到应用层 DTO，并将来自交互器/查询服务的响应转换回 HTTP 友好的格式。
    - **中间件集成**：利用 ASGI 中间件处理与功能相关的横切关注点，例如在传入请求上自动处理令牌或修改响应头以进行会话管理。
- **通用实现步骤和注意事项**：
    1.  **定义端点**：为功能的各种操作创建 FastAPI 路由（`APIRouter`、`@router.get`、`@router.post` 等）。
    2.  **基本输入验证**：使用 Pydantic 模型对传入的请求体、查询参数或路径参数进行基本验证（例如，数据类型、必填字段、基本格式检查）。请记住，在将数据传递给交互器/查询服务之前，将这些 Pydantic 模型转换为应用层 DTO（简单的 dataclass 或 TypedDict），以保持层分离。
    3.  **委托给应用层**：注入并调用适当的应用层交互器或查询服务（`FromDishka`、`@inject`）来执行核心业务逻辑。表现层本身不应包含业务逻辑。
    4.  **处理响应**：处理从应用层返回的结果。对于成功的身份验证，这可能涉及指示传输机制设置安全令牌（例如，cookie 中的 JWT）。
    5.  **管理 HTTP 传输细节**：对于涉及复杂 HTTP 交互的功能（例如身份验证），实现专用机制（例如，实现 `AuthSessionTransport` 的适配器）来抽象化安全令牌如何通过 HTTP 发送和接收的细节。这通常涉及 ASGI 中间件。
    6.  **OpenAPI 文档**：确保路由在 OpenAPI 中使用 `fastapi.Security` 和自定义 `APIKeyCookie` 或类似机制正确地文档化了描述、请求/响应模式以及适用的安全要求。
    7.  **错误处理**：使用 `fastapi_error_map.ErrorAwareRouter` 和 `ErrorTranslator` 实现将应用层或领域层中的应用程序特定错误映射到适当的 HTTP 状态码和用户友好的错误消息。

- **项目示例（身份验证和授权）**：本项目使用带有 cookie 的 JWT 令牌进行身份验证。这由 `access_token_processor_jwt.py`（用于令牌编码/解码）、`session_transport_jwt_cookie.py`（将会话传输适配到 HTTP cookie）、`asgi_middleware.py`（处理 cookie 生命周期）和 `openapi_marker.py`（用于 cookie 方案的 OpenAPI 文档）等组件提供便利。帐户管理控制器（例如 `log_in.py`、`log_out.py`、`sign_up.py`）演示了这些原则，利用 Pydantic 进行请求验证并委托给应用层处理程序。

### C. 错误处理 (`src/app/presentation/http/errors/`)
- **目的**：集中处理和翻译请求处理过程中发生的异常。
- **实现**：
    - `callbacks.py`：定义处理异常的日志回调 (`log_info`、`log_error`)。
    - `translators.py`：提供 `ErrorTranslator` 实现（例如 `ServiceUnavailableTranslator`），将异常转换为用户友好的错误响应模型。
    - `ErrorAwareRouter` 通过其 `error_map` 和 `default_on_error` 参数使用这些组件。

## 3. 表现层的单元测试 (`tests/app/unit/presentation/`)

- **位置**：表现层的所有单元测试都位于 `tests/app/unit/presentation/` 中。子目录镜像了 `src/app/presentation/` 的结构。
- **框架**：使用 `pytest` 和 `pytest-asyncio`，通常结合 `httpx.AsyncClient` 来测试 API 端点。
- **隔离**：
    - 通过模拟其依赖项（交互器、查询服务）来测试控制器。
    - 身份验证和中间件组件是隔离测试的。
- **测试场景**：
    - 验证各种成功和错误条件下的正确 HTTP 状态码。
    - 测试输入验证 (Pydantic 模型)，并确保对无效输入返回适当的 400 Bad Request 响应。
    - 断言控制器使用转换后的数据正确调用应用层。
    - 验证响应格式是否正确（例如，JSON 结构）。
    - 测试身份验证和授权流程，确保受保护的路由按预期运行。

## 4. 接口和跨层引用

### A. 表现层允许的引用
- 表现层可以引用：
    - 表现层内部的组件。
    - 应用层（交互器、查询服务、DTO、应用程序特定异常）。
    - 领域层（值对象、枚举、领域特定异常）用于类型提示或异常处理。
    - 辅助 HTTP 处理的已批准的外部库（例如 `FastAPI`、`Pydantic`、`jwt`）。

### B. 表现层不允许的引用
- 表现层不应直接引用基础设施层，除非是明确设计为 HTTP 接口一部分的特定身份验证/授权组件（例如 `app.infrastructure.auth.session.model.AuthSession` 用于身份验证的内部详细信息）。
- 它不应包含任何业务逻辑。

## 5. Pydantic 使用最佳实践
- 使用 Pydantic 模型作为请求体和响应模型，以生成 OpenAPI 文档并执行基本类型验证。
- 避免在表现层中的 Pydantic 验证器 (`@field_validator`, `@model_validator`) 中直接放置复杂的业务逻辑。将业务规则验证委托给应用层或领域层。
- 将数据从表现层传递到应用层时，将 Pydantic 模型转换为更简单的 dataclass 或 TypedDict，以维护架构边界并减少与 Pydantic 的耦合。