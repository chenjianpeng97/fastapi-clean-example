---
name: imple-infrastructure-layer
description: Use this skill when implementing the Infrastructure Layer in the fastapi-clean-example project. Focus on implementing ports, adapting to external systems, and adhering to the project's specific dependency rules.
---

# imple-infrastructure-layer Skill

This skill provides guidelines for implementing and testing the Infrastructure Layer in the `fastapi-clean-example` project.

# When to Activate

- Implementing concrete adapters for Domain or Application Layer ports.
- Integrating with external systems like databases, message brokers, or external APIs.
- Developing or modifying persistence mechanisms (e.g., SQLAlchemy repositories).
- Implementing authentication and authorization mechanisms that interact with external systems or provide concrete services.
- Fixing bugs related to data access, external service calls, or concrete implementations of interfaces.
- Adding tests for infrastructure components.

## 1. Core Principles of the Infrastructure Layer

### A. Adapting the Core to External Systems
- The Infrastructure Layer is responsible for connecting the core (Domain and Application Layers) to the outside world.
- It contains "driven adapters" that implement ports defined by the Domain and Application Layers, allowing the core to remain decoupled from implementation details.
- It may also contain "driving adapters" (often part of the Presentation Layer in this project, but conceptually relevant) that translate external requests into calls to the Application Layer.

### B. Dependency Rule Adherence (Project-Specific Interpretation)
- The Infrastructure Layer is an outer layer and **can depend on** inner layers (Application and Domain). It **must not be depended upon by** the Domain or Application Layers directly.
- **Crucially, the project's revised Dependency Rule states**: "Dependencies must never point outwards **within the core**." This implies that the Infrastructure Layer, being outside the core, serves as a "bridge" and can interact with external components and internal layers.
- It *implements* interfaces (Ports) defined by the Domain and Application Layers, thereby adhering to the Dependency Inversion Principle.

### C. Technology and Framework Specificity
- This layer is where external frameworks, libraries, and technologies (e.g., SQLAlchemy, FastAPI's specific features, bcrypt) are used to provide concrete implementations.
- It encapsulates the details of these external components, shielding the inner layers from their specifics.

## 2. Implementing Infrastructure Layer Components

### A. General Implementation Guidelines
- **Port Implementation**: The primary goal of most infrastructure components is to provide concrete implementations for ports (interfaces) defined in the Domain and Application Layers.
- **Encapsulation of External Details**: All interactions with external frameworks, databases, or third-party APIs should be encapsulated within this layer. Inner layers should only interact with the abstractions (ports).
- **Data Mapping**: Infrastructure components are responsible for mapping between the data structures of the core (e.g., Domain Entities, Application DTOs) and the data structures required by external systems (e.g., ORM models, API request/response formats).
- **Error Translation**: Infrastructure-specific errors (e.g., database connection errors, API rate limits) should ideally be translated into more generic or domain-specific exceptions where appropriate, especially when propagating to the Application Layer.

### B. Adapters (`src/app/infrastructure/adapters/`)
- **Purpose**: Implement the `typing.Protocol` or `abc.ABC` interfaces (ports) defined in the Domain or Application Layers. These adapters provide concrete functionality by interacting with external systems.
- **Implementation**:
    - Each adapter should implement a specific port.
    - Examples include `password_hasher_bcrypt.py` (implementing `PasswordHasher` from Domain), `user_id_generator_uuid.py` (implementing `UserIdGenerator` from Domain), and `user_data_mapper_sqla.py` (for persistence).
    - Data mapping between domain/application models and infrastructure-specific models (e.g., SQLAlchemy ORM models) is a key responsibility here.
- **Example**: `src/app/infrastructure/adapters/password_hasher_bcrypt.py`

### C. Persistence (`src/app/infrastructure/persistence_sqla/`)
- **Purpose**: Handle all database interactions using SQLAlchemy. This includes defining ORM models, repository implementations, and transaction management.
- **Implementation**:
    - Define SQLAlchemy models that represent the data storage structure.
    - Implement concrete repositories that perform CRUD operations and data queries, translating between SQLAlchemy models and Domain/Application entities/query models.
    - Leverage SQLAlchemy's features for efficient data access and transaction management.

### D. Authentication (Example) (`src/app/infrastructure/auth/`)
- **Purpose**: This section serves as an example of how a cross-cutting concern like authentication can be implemented within the infrastructure layer. It provides concrete services for authentication and authorization, such as session management and JWT handling.
- **Implementation**:
    - This part handles the specifics of token generation, validation, session storage, and retrieval, demonstrating the general guidelines for encapsulating external details and providing concrete services.
    - It might expose handlers (as described in `README.md`'s "Infrastructure Controller - Handler" section) that, while residing in Infrastructure, operate similarly to Application-level interactors but are specifically tied to an "authentication context" that is treated as an infrastructure detail in this project.

### E. Exceptions (`src/app/infrastructure/exceptions/`)
- **Purpose**: Define and handle exceptions specific to the infrastructure, and where necessary, translate them into domain-specific exceptions.
- **Implementation**:
    - Infrastructure exceptions might stem from database errors, external API failures, or configuration issues.
    - In some cases (e.g., `UNIQUE CONSTRAINT` violation in the database), it may be appropriate to raise domain-specific exceptions (like `UsernameAlreadyExistsError`) to be handled by the Application Layer, ensuring business logic control.

## 3. Unit Testing the Infrastructure Layer (`tests/app/unit/infrastructure/`)

- **Location**: All unit tests for the infrastructure layer reside in `tests/app/unit/infrastructure/`. The subdirectories should mirror the structure of `src/app/infrastructure/`.
- **Framework**: `pytest` and `pytest-asyncio` are used.
- **Isolation**:
    - Infrastructure components (especially adapters) are tested in isolation.
    - When testing an adapter that interacts with an external system (e.g., a database or external API), **mock** the external dependency to ensure the test focuses solely on the adapter's logic. For persistence, this might involve using in-memory databases or mocking the SQLAlchemy session.
- **Test Data**: Utilize test data factories for consistent and reusable test data generation, similar to other layers.
- **Port Implementation Verification**: Ensure that infrastructure adapters correctly implement the contracts (ports) defined by the Domain and Application Layers.
- **Error Handling**: Test that infrastructure components correctly handle errors from external systems and raise appropriate (or translated) exceptions.
- **Comprehensive Scenarios**: Write tests that cover:
    - Successful interactions with mocked external systems.
    - Edge cases and failure scenarios of the infrastructure component.
    - Correct data mapping and translation.
- **Integration Tests (`tests/app/integration/`)**: For more complex interactions involving multiple infrastructure components or actual external systems (e.g., a real database), integration tests should be written in `tests/app/integration/`.

## 4. Interfaces and Cross-Layer References

### A. Implementing Ports
- The Infrastructure Layer's primary role regarding interfaces is to **implement** the Ports (`typing.Protocol` or `abc.ABC`) defined in `src/app/domain/ports/` and `src/app/application/common/ports/`.

### B. Allowed References for the Infrastructure Layer
- The Infrastructure Layer **can reference**:
    - Components within the Application Layer (e.g., DTOs, query models).
    - Components within the Domain Layer (e.g., Entities, Value Objects, Enums, Exceptions).
    - Standard Python library modules.
    - External libraries and frameworks specific to its implementation concerns (e.g., SQLAlchemy, bcrypt, `uuid`, `fastapi`).
    - Other components within the Infrastructure Layer.
- The Infrastructure Layer **should not be referenced by** the Domain or Application Layers. Direct dependencies from inner to outer layers are forbidden.