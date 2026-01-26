---
name: imple-application-layer
description: Use this skill when implementing the Application Layer in the fastapi-clean-example project. Focus on orchestrating domain logic, defining DTOs, and managing dependencies on infrastructure through ports.
---

# imple-application-layer Skill

This skill provides guidelines for implementing and testing the Application Layer in the `fastapi-clean-example` project.

# When to Activate

- Implementing new use cases or business operations (commands or queries).
- Fixing bugs related to application-level orchestration or data flow.
- Refactoring interactors, query services, or application-specific DTOs.
- Adding application layer tests.

## 1. Core Principles of the Application Layer

### A. Dependency Rule Adherence
- The Application Layer depends on the Domain Layer (inner layer) but does not depend on the Infrastructure or Presentation Layers (outer layers).
- It defines its own ports (interfaces) that the Infrastructure Layer must implement.
- It can import external tools and libraries only if they extend programming language capabilities, similar to the Domain Layer, but not those binding business logic to implementation details (frameworks, databases).

### B. Stateless Interactors and Query Services
- Interactors and Query Services should be stateless. They encapsulate a single business operation or query.
- They orchestrate domain logic and calls to infrastructure via ports; they do not contain core business logic themselves.

### C. DTO Usage
- The Application Layer uses Data Transfer Objects (DTOs) to exchange data with external layers (Presentation, Infrastructure).
- These DTOs should primarily be `dataclasses` (or `TypedDict` for query results) and should be simple, behavior-free data carriers. Avoid framework-specific models (e.g., Pydantic) directly within the core Application Layer.

### D. Orchestration, not Implementation
- The primary responsibility of the Application Layer is to orchestrate the execution of a use case. This includes:
    - Receiving input DTOs from the Presentation Layer.
    - Validating application-specific rules (distinct from domain invariants).
    - Calling Domain Services, Entities, and Value Objects to execute business logic.
    - Interacting with the Infrastructure Layer via ports (e.g., persistence, external services).
    - Returning output DTOs to the Presentation Layer.
    - Handling transaction management and permission verification.

## 2. Implementing Application Layer Components

### A. Commands (Interactors) (`src/app/application/commands/`)
- **Purpose**: Handle write operations and business-critical reads (use cases that modify state). Each interactor corresponds to a single business operation.
- **Implementation**:
    - Stateless classes with a single public method (e.g., `execute` or `handle`).
    - Accept input as `dataclass`-based DTOs.
    - Orchestrate calls to Domain Layer components and Infrastructure Ports.
    - Perform permission checks and transaction management.
    - Return `dataclass`-based DTOs or `TypedDict` for results.
- **Example**: `src/app/application/commands/create_user.py`, `activate_user.py`

### B. Queries (Query Services) (`src/app/application/queries/`)
- **Purpose**: Handle optimized read operations, typically returning data tailored for presentation.
- **Implementation**:
    - Stateless classes with a single public method.
    - Accept input as `dataclass`-based DTOs (query parameters).
    - Interact with Infrastructure Ports (e.g., query readers) to retrieve data.
    - Return data as `TypedDict` or simplified `dataclass`-based query models.
- **Example**: `src/app/application/queries/list_users.py`

### C. DTOs (Data Transfer Objects) (`src/app/application/common/query_models/`, `src/app/application/common/query_params/`)
- **Purpose**: Define the input and output structures for interactors and query services.
- **Implementation**:
    - Use `dataclass` for inputs (command/query parameters) and some outputs.
    - Use `TypedDict` for complex query outputs where behavior is not needed and performance is critical.
    - Must be simple data structures without complex behavior.
- **Example**: Check `src/app/application/common/query_models/` and `src/app/application/common/query_params/` for existing patterns. If empty, these directories are meant for this purpose.

### D. Ports (`src/app/application/common/ports/`)
- **Purpose**: Define interfaces (contracts) for functionalities that the Application Layer needs but are implemented in the Infrastructure Layer (e.g., persistence gateways, external service clients). This adheres to the Dependency Inversion Principle.
- **Implementation**:
    - Define interfaces using `typing.Protocol` or `abc.ABC`.
    - These ports allow the Application Layer to remain decoupled from concrete Infrastructure implementations.
- **Example**: Check `src/app/application/common/ports/` for existing patterns.

### E. Application Services (`src/app/application/common/services/`)
- **Purpose**: Encapsulate application-specific logic that is shared across multiple interactors or queries, such as authorization.
- **Implementation**:
    - Should be stateless.
    - Accept dependencies via constructor injection.
    - Orchestrate checks or operations relevant to the application layer.
- **Example**: `src/app/application/common/services/authorization/`

### F. Exceptions (`src/app/application/common/exceptions/`)
- **Purpose**: Represent application-specific errors or violations (e.g., authorization failures, invalid input data that passed Presentation Layer validation but fails application-level checks).
- **Implementation**:
    - Inherit from a common application base exception (if one exists).
    - Should be specific and convey clear application-level meaning.
- **Example**: `src/app/application/common/exceptions/authorization.py`

## 3. Unit Testing the Application Layer (`tests/app/unit/application/`)

- **Location**: All unit tests for the application layer reside in `tests/app/unit/application/`. The subdirectories mirror the structure of `src/app/application/`.
- **Framework**: `pytest` and `pytest-asyncio` are used.
- **Isolation**:
    - Interactors and Query Services are tested in isolation from their dependencies.
    - **Mocks** are used for:
        - Domain Layer components (Entities, Value Objects, Domain Services) to ensure only the application logic is tested.
        - Infrastructure Ports (e.g., `UserGateway`, `QueryReader`).
    - `unittest.mock.create_autospec` with `pytest.fixture` is the standard approach.
- **Test Data**: Utilize test data factories (e.g., `tests.app.unit.factories.user_entity`, `tests.app.unit.factories.value_objects`) for consistent and reusable test data generation. Consider creating application-specific factories for DTOs.
- **Scenario Coverage**: Write tests that cover:
    - Successful execution of the use case with valid inputs.
    - Edge cases and boundary conditions.
    - Failure scenarios, asserting that appropriate application-level exceptions (e.g., `AuthorizationError`) or re-raised Domain Layer exceptions are handled.
    - Correct interaction with mocked Domain Layer components and Infrastructure Ports.
- **Asynchronous Code**: Use `@pytest.mark.asyncio` for testing asynchronous interactors and query services.

## 4. Interfaces and Cross-Layer References

### A. References to the Domain Layer
- The Application Layer can freely reference and utilize components from the Domain Layer (Entities, Value Objects, Domain Services, Enums, Exceptions).

### B. Ports Defined by the Application Layer
- The Application Layer defines `Ports` (interfaces) that describe the capabilities it requires from the Infrastructure Layer. These are found in `src/app/application/common/ports/`.
- The Infrastructure Layer will implement these `Ports`.

### C. Prohibitions
- The Application Layer **must not reference** code from the Infrastructure or Presentation layers directly. This means no direct imports from `src/app/infrastructure/` or `src/app/presentation/`.
- It should not contain any framework-specific (e.g., FastAPI) or database-specific (e.g., SQLAlchemy) code.