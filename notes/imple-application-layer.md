---
name: imple-application-layer
description: 在fastapi-clean-example项目中实现应用层时使用此技能。重点关注协调领域逻辑、定义DTO以及通过端口管理对基础设施的依赖。
---

# imple-application-layer 技能

此技能为 `fastapi-clean-example` 项目中应用层的实现和测试提供指导。

# 何时激活

- 实现新的用例或业务操作（命令或查询）。
- 修复与应用层编排或数据流相关的错误。
- 重构交互器、查询服务或应用特定的DTO。
- 添加应用层测试。

## 1. 应用层的核心原则

### A. 依赖规则遵循
- 应用层依赖于领域层（内层），但不依赖于基础设施层或表示层（外层）。
- 它定义了自己的端口（接口），基础设施层必须实现这些端口。
- 它只能导入那些扩展编程语言能力的外工具和库，类似于领域层，但不能是那些将业务逻辑绑定到实现细节（框架、数据库）的工具和库。

### B. 无状态的交互器和查询服务
- 交互器和查询服务应该是无状态的。它们封装单个业务操作或查询。
- 它们通过端口协调领域逻辑和对基础设施的调用；它们本身不包含核心业务逻辑。

### C. DTO使用
- 应用层使用数据传输对象（DTO）与外部层（表示层、基础设施层）交换数据。
- 这些DTO主要应该是基于 `dataclass`（或用于查询结果的 `TypedDict`），并且应该是简单的、无行为的数据载体。避免在核心应用层直接使用特定框架的模型（例如 Pydantic）。

### D. 编排而非实现
- 应用层的主要职责是编排用例的执行。这包括：
    - 从表示层接收输入DTO。
    - 验证应用特定的规则（与领域不变性不同）。
    - 调用领域服务、实体和值对象来执行业务逻辑。
    - 通过端口与基础设施层交互（例如，持久化、外部服务）。
    - 向表示层返回输出DTO。
    - 处理事务管理和权限验证。

## 2. 实现应用层组件

### A. 命令（交互器）(`src/app/application/commands/`)
- **目的**：处理写操作和业务关键读取（修改状态的用例）。每个交互器对应一个业务操作。
- **实现**：
    - 具有单个公共方法（例如 `execute` 或 `handle`）的无状态类。
    - 接受基于 `dataclass` 的DTO作为输入。
    - 编排对领域层组件和基础设施端口的调用。
    - 执行权限检查和事务管理。
    - 返回基于 `dataclass` 的DTO或 `TypedDict` 作为结果。
- **示例**：`src/app/application/commands/create_user.py`、`activate_user.py`

### B. 查询（查询服务）(`src/app/application/queries/`)
- **目的**：处理优化后的读操作，通常返回为表示层量身定制的数据。
- **实现**：
    - 具有单个公共方法的无状态类。
    - 接受基于 `dataclass` 的DTO作为输入（查询参数）。
    - 与基础设施端口（例如，查询读取器）交互以检索数据。
    - 以 `TypedDict` 或简化的基于 `dataclass` 的查询模型返回数据。
- **示例**：`src/app/application/queries/list_users.py`

### C. DTO（数据传输对象）(`src/app/application/common/query_models/`, `src/app/application/common/query_params/`)
- **目的**：定义交互器和查询服务的输入和输出结构。
- **实现**：
    - 对输入（命令/查询参数）和部分输出使用 `dataclass`。
    - 对于不需要行为且性能关键的复杂查询输出，使用 `TypedDict`。
    - 必须是简单的数据结构，没有复杂的行为。
- **示例**：检查 `src/app/application/common/query_models/` 和 `src/app/application/common/query_params/` 中现有的模式。如果为空，这些目录就是为此目的设计的。

### D. 端口 (`src/app/application/common/ports/`)
- **目的**：定义应用层所需但由基础设施层实现的功能接口（契约）（例如，持久化网关、外部服务客户端）。这遵循了依赖倒置原则。
- **实现**：
    - 使用 `typing.Protocol` 或 `abc.ABC` 定义接口。
    - 这些端口使应用层能够与具体的基础设施实现解耦。
- **示例**：检查 `src/app/application/common/ports/` 中现有的模式。

### E. 应用服务 (`src/app/application/common/services/`)
- **目的**：封装跨多个交互器或查询共享的应用特定逻辑，例如授权。
- **实现**：
    - 应该是无状态的。
    - 通过构造函数注入接受依赖项。
    - 协调与应用层相关的检查或操作。
- **示例**：`src/app/application/common/services/authorization/`

### F. 异常 (`src/app/application/common/exceptions/`)
- **目的**：表示应用特定的错误或违规（例如，授权失败，通过表示层验证但未能通过应用层检查的无效输入数据）。
- **实现**：
    - 继承自通用的应用基础异常（如果存在）。
    - 应该具体并传达清晰的应用层含义。
- **示例**：`src/app/application/common/exceptions/authorization.py`

## 3. 应用层单元测试 (`tests/app/unit/application/`)

- **位置**：应用层的所有单元测试都位于 `tests/app/unit/application/` 中。子目录镜像了 `src/app/application/` 的结构。
- **框架**：使用 `pytest` 和 `pytest-asyncio`。
- **隔离**：
    - 交互器和查询服务与其依赖项隔离测试。
    - **模拟**用于：
        - 领域层组件（实体、值对象、领域服务），以确保只测试应用逻辑。
        - 基础设施端口（例如，`UserGateway`、`QueryReader`）。
    - `unittest.mock.create_autospec` 与 `pytest.fixture` 是标准方法。
- **测试数据**：利用测试数据工厂（例如，`tests.app.unit.factories.user_entity`、`tests.app.unit.factories.value_objects`）生成一致且可重用的测试数据。考虑为DTO创建应用特定的工厂。
- **场景覆盖**：编写覆盖以下内容的测试：
    - 使用有效输入成功执行用例。
    - 边界情况和边缘条件。
    - 失败场景，断言处理了适当的应用层异常（例如，`AuthorizationError`）或重新抛出的领域层异常。
    - 与模拟的领域层组件和基础设施端口的正确交互。
- **异步代码**：使用 `@pytest.mark.asyncio` 测试异步交互器和查询服务。

## 4. 接口和跨层引用

### A. 对领域层的引用
- 应用层可以自由引用和使用领域层的组件（实体、值对象、领域服务、枚举、异常）。

### B. 应用层定义的端口
- 应用层定义了描述其从基础设施层所需能力的端口（接口）。这些位于 `src/app/application/common/ports/` 中。
- 基础设施层将实现这些端口。

### C. 禁止事项
- 应用层**不得直接引用**基础设施层或表示层的代码。这意味着不允许直接从 `src/app/infrastructure/` 或 `src/app/presentation/` 导入。
- 它不应包含任何特定于框架（例如 FastAPI）或特定于数据库（例如 SQLAlchemy）的代码。