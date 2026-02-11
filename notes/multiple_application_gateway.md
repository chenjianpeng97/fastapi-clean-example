# 多应用层网关：设计笔记

## 问题

在分层架构中，单个应用层查询/命令通常通过 IoC 绑定到一个具体网关。但在真实场景（例如测试用例来自 Markdown/Excel/ALM API/DB）中，同一用例需要适配多个数据源。

## 核心思路

让**用例保持业务语义**，并把**数据源选择视为应用层策略**。DI（IoC）只负责装配对象，不负责业务流程决策。

## 推荐设计

- **用例保持语义化**：`ActivateTestCase`、`UpdateTestCase`、`ListTestCases`。
- **请求包含 `source`**（如 csv/excel/jira/db）。
- **应用层路由/选择器**在运行时选择具体网关。
- **基础设施网关**实现实际的数据访问。

这样可以保持核心逻辑稳定、测试更容易，并避免把业务决策隐藏在 IoC 配置里。

## 为什么不把 `source` 放进 Gateway 接口

把 `source` 加进 gateway 方法会把选择逻辑塞进端口，导致接口臃肿、内聚性降低，也会让本该抽象的契约泄漏基础设施选择细节。

## 最小示例（Activate）

```python
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

class TestCaseSource(str, Enum):
    CSV = "csv"
    JIRA = "jira"
    DB = "db"

@dataclass(frozen=True, slots=True)
class ActivateTestCaseRequest:
    test_case_id: str
    source: TestCaseSource

class TestCaseCommandGateway(Protocol):
    async def activate(self, test_case_id: str) -> None:
        ...

class TestCaseCommandRouter:
    def __init__(self, csv: TestCaseCommandGateway, jira: TestCaseCommandGateway, db: TestCaseCommandGateway) -> None:
        self._csv = csv
        self._jira = jira
        self._db = db

    def select(self, request: ActivateTestCaseRequest) -> TestCaseCommandGateway:
        if request.source == TestCaseSource.CSV:
            return self._csv
        if request.source == TestCaseSource.JIRA:
            return self._jira
        return self._db

class ActivateTestCaseInteractor:
    def __init__(self, router: TestCaseCommandRouter) -> None:
        self._router = router

    async def execute(self, request: ActivateTestCaseRequest) -> None:
        gateway = self._router.select(request)
        await gateway.activate(request.test_case_id)
```

## 结论

- **命令/查询体现业务动作，而不是数据源**。
- **选择逻辑属于应用层**，不应交给 DI 容器。
- **多个网关没问题**，但由路由/选择器进行编排。
