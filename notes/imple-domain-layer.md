---
name: imple-domain-layer
description: 在fastapi-clean-example项目中实现领域层时使用此技能。专注于纯Python、不变性以及遵循依赖规则。
---

# imple-domain-layer 技能

此技能为 `fastapi-clean-example` 项目中的领域层实现和测试提供指导。

## 1. 领域层的核心原则

### A. 遵守依赖规则
- 领域层是最内层，不依赖于外层（应用层、基础设施层、表示层）。
- 只有在扩展编程语言功能（例如，数学工具、时区转换）的情况下，它才能导入外部工具和库，但不能导入将业务逻辑绑定到实现细节（框架、数据库）的工具和库。

### B. 纯 Python 和不变性
- 领域层应由纯 Python 代码组成。避免使用特定于框架的构造（例如，直接使用 Pydantic 模型）。
- 值对象应是不可变的 (`dataclass(frozen=True, slots=True)`)。实体在设计上是可变的，但它们的 `id_` 属性在创建后是不可变的。

## 2. 领域层组件的实现

### A. 实体 (`src/app/domain/entities/`)
- **目的**：表示具有唯一标识和生命周期的核心业务概念。
- **实现**：
    - 继承自 `app.domain.entities.base.Entity`。
    - 必须具有 `id_` 属性，该属性在初始化后不可变。
    - 使用值对象和枚举来组合实体。
    - 实体的非 `id_` 属性是可变的。
- **示例**：`src/app/domain/entities/user.py`

### B. 值对象 (`src/app/domain/value_objects/`)
- **目的**：表示领域的描述性方面，没有概念上的标识。它们由其属性定义。
- **实现**：
    - 继承自 `app.domain.value_objects.base.ValueObject` 或为 `dataclass(frozen=True, slots=True)`。
    - **必须是不可变的**。
    - 在 `__init__` 或 `__post_init__` 中实现验证逻辑以强制执行不变性。对于无效的构造，抛出 `app.domain.exceptions.base.DomainTypeError`。
    - 在数据类定义中，对敏感字段使用 `repr=False`。
- **示例**：`src/app/domain/value_objects/username.py`、`src/app/domain/value_objects/raw_password.py`

### C. 领域服务 (`src/app/domain/services/`)
- **目的**：封装不自然地属于单个实体或值对象，或协调多个领域对象的业务逻辑。
- **实现**：
    - 应为**无状态的**。
    - 通过构造函数注入接受依赖项（端口）。
    - 编排实体和值对象上的操作。
    - 不直接执行 I/O 操作。
- **示例**：`src/app/domain/services/user.py`

### D. 端口 (`src/app/domain/ports/`)
- **目的**：定义领域层需要但由外层（基础设施层）实现的功能接口。这遵循了依赖反转原则。
- **实现**：
    - 使用 `typing.Protocol` 或 `abc.ABC` 定义接口。
    - 这些作为契约。领域层依赖于这些抽象，而不是它们的具体实现。
- **示例**：`src/app/domain/ports/password_hasher.py`、`src/app/domain/ports/user_id_generator.py`

### E. 枚举 (`src/app/domain/enums/`)
- **目的**：定义领域内一组命名常量值。
- **实现**：
    - 对于基于字符串的枚举，使用 `enum.StrEnum`。
    - 可以包含与枚举值相关的领域特定逻辑的属性或方法（例如，`is_assignable`、`is_changeable`）。
- **示例**：`src/app/domain/enums/user_role.py`

### F. 异常 (`src/app/domain/exceptions/`)
- **目的**：表示特定的领域规则违规或无效构造。
- **实现**：
    - 对于业务规则违规，继承自 `app.domain.exceptions.base.DomainError`。
    - 对于无效的值对象构造，继承自 `app.domain.exceptions.base.DomainTypeError`。
    - 自定义异常应具体并传达清晰的领域含义。
- **示例**：`src/app/domain/exceptions/user.py`

## 3. 领域层的单元测试 (`tests/app/unit/domain/`)

- **位置**：所有领域层的单元测试都位于 `tests/app/unit/domain/` 中。子目录镜像了 `src/app/domain/` 的结构。
- **框架**：使用 `pytest` 和 `pytest-asyncio`。
- **隔离**：
    - 领域服务与其依赖项隔离测试。
    - **模拟对象**用于 `Ports`（例如，`PasswordHasher`、`UserIdGenerator`）。`unittest.mock.create_autospec` 与 `pytest.fixture` 是标准方法 (`tests/app/unit/domain/services/conftest.py`)。
- **测试数据**：利用测试数据工厂（例如，`tests.app.unit.factories.user_entity`、`tests.app.unit.factories.value_objects`）来生成一致且可重用的测试数据。
- **不变性测试**：
    - 对于值对象，通过尝试使用无效数据创建对象并断言抛出 `DomainTypeError` 来测试验证规则。
    - 对于实体和领域服务，测试当业务规则被违反时抛出 `DomainError`（或其特定子类）。
- **全面场景**：编写测试涵盖：
    - 有效输入的成功操作。
    - 边界情况和边界条件（例如，值对象的最小/最大长度）。
    - 失败场景，断言抛出适当的异常。
    - 对实体状态的副作用。
- **异步代码**：使用 `@pytest.mark.asyncio` 来测试异步领域服务。

## 4. 接口和跨层引用

### A. 领域层定义的接口（端口）
- 领域层定义了 `Ports`（接口），描述了它从外部层所需的功能。这些接口位于 `src/app/domain/ports/` 中。
- **示例**：`PasswordHasher`、`UserIdGenerator`。
- 应用层（最终是基础设施层）将实现这些 `Ports`。

### B. 领域层允许的引用
- 领域层**不应引用**应用层、基础设施层或表示层的代码。
- 它可以引用：
    - 领域层内的其他组件（实体、值对象、服务、枚举、异常）。
    - 标准 Python 库模块。
    - 不将业务逻辑绑定到基础设施问题的经批准的外部库（例如，`uuid`、`re`）。