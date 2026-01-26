# Project Guidelines Skill

This skill provides guidelines for working on the `fastapi-clean-example` project. It adheres to Clean Architecture, CQRS, and Domain-Driven Design (DDD) principles.

---

## When to Use

Reference this skill when:
- Developing features or fixing bugs in the `fastapi-clean-example` project.
- You need to understand the project's layered architecture and dependency rules.
- You are unsure where to place new logic (Domain, Application, Infrastructure, or Presentation).
- You need to configure the application or run local development environments.

---

## Architecture Overview

### File structure

```
.
├── config/...                                   # configuration files and scripts, includes Docker
├── Makefile                                     # shortcuts for setup and common tasks
├── scripts/...                                  # helper scripts
├── pyproject.toml                               # tooling and environment config (uv)
├── ...
└── src/
    └── app/
        ├── domain/                              # domain layer
        │   ├── services/...                     # domain layer services
        │   ├── entities/...                     # entities (have identity)
        │   │   ├── base.py                      # base declarations
        │   │   └── ...                          # concrete entities
        │   ├── value_objects/...                # value objects (no identity)
        │   │   ├── base.py                      # base declarations
        │   │   └── ...                          # concrete value objects
        │   └── ...                              # ports, enums, exceptions, etc.
        │
        ├── application/...                      # application layer
        │   ├── commands/                        # write ops, business-critical reads
        │   │   ├── create_user.py               # interactor
        │   │   └── ...                          # other interactors
        │   ├── queries/                         # optimized read operations
        │   │   ├── list_users.py                # query service
        │   │   └── ...                          # other query services
        │   └── common/                          # common layer objects
        │       ├── services/...                 # authorization, etc.
        │       └── ...                          # ports, exceptions, etc.
        │
        ├── infrastructure/...                   # infrastructure layer
        │   ├── adapters/...                     # port adapters
        │   ├── auth/...                         # auth context (session-based)
        │   └── ...                              # persistence, exceptions, etc.
        │
        ├── presentation/...                     # presentation layer
        │   └── http/                            # http interface
        │       ├── auth/...                     # web auth logic
        │       ├── controllers/...              # controllers and routers
        │       └── errors/...                   # error handling helpers
        │
        ├── setup/
        │   ├── ioc/...                          # dependency injection setup
        │   ├── config/...                       # app settings
        │   └── app_factory.py                   # app builder
        │  
        └── run.py                               # app entry point
```


### Code patterns

*   **Clean Architecture Layers**:
    *   **Domain**: Pure Python. `dataclasses` only. No Pydantic. No SQL.
    *   **Application**: `dataclasses` for DTOs. Orchestrates Domain. Defines Ports.
    *   **Infrastructure**: Implements Ports. Depends on SQL/libs.
    *   **Presentation**: FastAPI controllers. Uses **Pydantic** for HTTP Request/Response only.

*   **Dependency Injection (DI)**:
    *   Use **Dishka** (`src/app/setup/ioc`), not FastAPI `Depends`.
    *   Controllers accept dependencies via `FromDishka[...]`.

*   **CQRS (Command Query Responsibility Segregation)**:
    *   **Commands**: Handle writes/business logic. Located in `application/commands`.
    *   **Queries**: Handle reads. Located in `application/queries`. Optimize for data retrieval.

*   **Configuration**:
    *   **Source of Truth**: TOML files in `config/` (e.g., `config.toml`, `.secrets.toml`).
    *   **Access**: Application reads TOML directly or via generated `.env` for infrastructure.

### Testing requirements

*   **Frameworks**: `pytest`, `pytest-asyncio`.
*   **Tools**: `coverage` for metrics, `line-profiler` for performance.
*   **Location**: `tests/` directory.
    *   `tests/unit`: Isolated tests for Domain/Application logic.
    *   `tests/app`: Integration/E2E tests (TODO per README).
*   **Execution**:
    *   Run all tests: `pytest`
    *   Run with coverage: `coverage run -m pytest`

### Deployment workflow

1.  **Configuration**:
    *   Navigate to `config/local/` (or `dev`/`prod`).
    *   Edit `config.toml` or `.secrets.toml` (do not commit secrets).
    *   **Do not** edit `.env` files manually.

2.  **Environment Generation**:
    *   Run `make env` to verify the environment variable export.
    *   Run `make dotenv` to generate the `.env` file from TOML configs.

3.  **Local Execution (Docker)**:
    *   Start full stack: `make up` (App + DB).
    *   Start DB only: `make up.db`.
    *   Stop containers: `make down`.

4.  **Database Migrations**:
    *   Apply migrations: `alembic upgrade head`.
    *   Create new migration: `alembic revision --autogenerate -m "message"`.