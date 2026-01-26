---
name: imple-domain-layer
description: Use this skill when implementing the Domain Layer in the fastapi-clean-example project. Focus on pure Python, immutability, and adherence to the Dependency Rule.
---

# imple-domain-layer Skill

This skill provides guidelines for implementing and testing the Domain Layer in the `fastapi-clean-example` project.

# When to Activate

- Implementing new features in the Domain Layer.
- Fixing bugs related to domain logic.
- Refactoring domain entities, value objects, or services.
- Adding domain layer tests.


## 1. Core Principles of the Domain Layer

### A. Dependency Rule Adherence
- The Domain Layer is the innermost layer and has no dependencies on outer layers (Application, Infrastructure, Presentation).
- It can import external tools and libraries only if they extend programming language capabilities (e.g., math utilities, time zone conversion), but not those binding business logic to implementation details (frameworks, databases).

### B. Pure Python and Immutability
- The Domain Layer should consist of pure Python code. Avoid framework-specific constructs (e.g., Pydantic models directly).
- Value Objects should be immutable (`dataclass(frozen=True, slots=True)`). Entities are mutable by design but their `id_` attribute is immutable after creation.

## 2. Implementing Domain Layer Components

### A. Entities (`src/app/domain/entities/`)
- **Purpose**: Represent core business concepts with a unique identity and lifecycle.
- **Implementation**:
    - Inherit from `app.domain.entities.base.Entity`.
    - Must have an `id_` attribute, which is immutable after initialization.
    - Compose entities using Value Objects and Enums.
    - Entities are mutable for their non-`id_` attributes.
- **Example**: `src/app/domain/entities/user.py`

### B. Value Objects (`src/app/domain/value_objects/`)
- **Purpose**: Represent descriptive aspects of the domain with no conceptual identity. They are defined by their attributes.
- **Implementation**:
    - Inherit from `app.domain.value_objects.base.ValueObject` or be a `dataclass(frozen=True, slots=True)`.
    - **Must be immutable**.
    - Implement validation logic within `__init__` or `__post_init__` to enforce invariants. Raise `app.domain.exceptions.base.DomainTypeError` for invalid construction.
    - Use `repr=False` for sensitive fields in the dataclass definition.
- **Example**: `src/app/domain/value_objects/username.py`, `src/app/domain/value_objects/raw_password.py`

### C. Domain Services (`src/app/domain/services/`)
- **Purpose**: Encapsulate business logic that does not naturally fit within a single Entity or Value Object, or coordinates multiple domain objects.
- **Implementation**:
    - Should be **stateless**.
    - Accept dependencies (ports) via constructor injection.
    - Orchestrate operations on Entities and Value Objects.
    - Do not perform I/O operations directly.
- **Example**: `src/app/domain/services/user.py`

### D. Ports (`src/app/domain/ports/`)
- **Purpose**: Define interfaces for functionalities that the Domain Layer needs but are implemented in an outer layer (Infrastructure). This adheres to the Dependency Inversion Principle.
- **Implementation**:
    - Define interfaces using `typing.Protocol` or `abc.ABC`.
    - These serve as contracts. The Domain Layer depends on these abstractions, not their concrete implementations.
- **Example**: `src/app/domain/ports/password_hasher.py`, `src/app/domain/ports/user_id_generator.py`

### E. Enums (`src/app/domain/enums/`)
- **Purpose**: Define a set of named constant values within the domain.
- **Implementation**:
    - Use `enum.StrEnum` for string-based enums.
    - Can include properties or methods for domain-specific logic related to the enum values (e.g., `is_assignable`, `is_changeable`).
- **Example**: `src/app/domain/enums/user_role.py`

### F. Exceptions (`src/app/domain/exceptions/`)
- **Purpose**: Represent specific domain rule violations or invalid constructions.
- **Implementation**:
    - Inherit from `app.domain.exceptions.base.DomainError` for business rule violations.
    - Inherit from `app.domain.exceptions.base.DomainTypeError` for invalid Value Object construction.
    - Custom exceptions should be specific and convey clear domain meaning.
- **Example**: `src/app/domain/exceptions/user.py`

## 3. Unit Testing the Domain Layer (`tests/app/unit/domain/`)

- **Location**: All unit tests for the domain layer reside in `tests/app/unit/domain/`. The subdirectories mirror the structure of `src/app/domain/`.
- **Framework**: `pytest` and `pytest-asyncio` are used.
- **Isolation**:
    - Domain services are tested in isolation from their dependencies.
    - **Mocks** are used for `Ports` (e.g., `PasswordHasher`, `UserIdGenerator`). `unittest.mock.create_autospec` with `pytest.fixture` is the standard approach (`tests/app/unit/domain/services/conftest.py`).
- **Test Data**: Utilize test data factories (e.g., `tests.app.unit.factories.user_entity`, `tests.app.unit.factories.value_objects`) for consistent and reusable test data generation.
- **Invariants Testing**:
    - For Value Objects, test the validation rules by attempting to create objects with invalid data and asserting that `DomainTypeError` is raised.
    - For Entities and Domain Services, test that `DomainError` (or its specific subclasses) is raised when business rules are violated.
- **Comprehensive Scenarios**: Write tests that cover:
    - Successful operations with valid inputs.
    - Edge cases and boundary conditions (e.g., minimum/maximum lengths for Value Objects).
    - Failure scenarios, asserting that appropriate exceptions are raised.
    - Side effects on entity state.
- **Asynchronous Code**: Use `@pytest.mark.asyncio` for testing asynchronous domain services.

## 4. Interfaces and Cross-Layer References

### A. Interfaces Defined by the Domain Layer (Ports)
- The Domain Layer defines `Ports` (interfaces) that describe the capabilities it requires from external layers. These are found in `src/app/domain/ports/`.
- **Examples**: `PasswordHasher`, `UserIdGenerator`.
- The Application Layer (and ultimately the Infrastructure Layer) will implement these `Ports`.

### B. Allowed References for the Domain Layer
- The Domain Layer **should not reference** code from the Application, Infrastructure, or Presentation layers.
- It can reference:
    - Other components within the Domain Layer (Entities, Value Objects, Services, Enums, Exceptions).
    - Standard Python library modules.
    - Approved external libraries that do not tie business logic to infrastructure concerns (e.g., `uuid`, `re`).