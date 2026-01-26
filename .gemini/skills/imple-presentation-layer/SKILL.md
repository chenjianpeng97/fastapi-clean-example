---
name: imple-presentation-layer
description: Use this skill when implementing the Presentation Layer in the fastapi-clean-example project. Focus on FastAPI integration, input validation, and proper dependency management.
---

# imple-presentation-layer Skill

This skill provides guidelines for implementing and testing the Presentation Layer in the `fastapi-clean-example` project.

# When to Activate

- Implementing new API endpoints.
- Modifying existing API endpoint behavior.
- Fixing bugs related to HTTP request/response handling or routing.
- Adding presentation layer tests.

## 1. Core Principles of the Presentation Layer

### A. Thin Controllers
- Controllers must be as thin as possible, containing no logic beyond basic input validation and routing. Their role is to act as an intermediary between the application and external systems (FastAPI).
- They should orchestrate calls to the Application Layer (Interactors/Query Services) and handle HTTP-specific concerns (status codes, response serialization).

### B. Input Validation
- **Basic Validation**: Controllers are responsible for basic input validation, suchs as checking the structure of the incoming request, type safety, and required fields. This is typically done using Pydantic models.
- **Business Rule Validation**: Business rule validation (e.g., uniqueness checks, specific value constraints) belongs to the Domain or Application Layer. Pydantic should **not** be used for business rule validation within the Presentation Layer to avoid coupling business logic to an external library.

### C. Dependency Management
- The Presentation Layer is an outer layer and depends on inner layers (Application and Domain). It should **not** contain any business logic itself.
- It can directly depend on the Domain Layer for exceptions or enums, bypassing the Application Layer if necessary.
- Dependency Injection (`dishka`) is used to inject interactors and query services into controllers.

## 2. Implementing Presentation Layer Components

### A. Controllers (`src/app/presentation/http/controllers/`)
- **Purpose**: Define API endpoints, handle incoming HTTP requests, perform basic input validation, delegate to the Application Layer, and format HTTP responses.
- **Implementation**:
    - Use `fastapi.APIRouter` for routing.
    - Use `fastapi_error_map.ErrorAwareRouter` for declarative error handling and mapping exceptions to HTTP status codes.
    - Inject dependencies (Interactors, Query Services) using `dishka.FromDishka` and `@inject`.
    - Accept request data via Pydantic models (e.g., `BaseModel`). These models should primarily serve for OpenAPI schema generation and basic structural validation.
    - Convert Pydantic request models to application-specific DTOs before passing them to Interactors/Query Services.
    - Return responses that are either application-specific Query Models or `None` for successful commands.
- **Examples**: `src/app/presentation/http/controllers/account/change_password.py`, `src/app/presentation/http/controllers/users/create_user.py`

### B. Feature Implementation: Authentication and Authorization Example

- **Purpose**: To safely expose and manage a specific feature (e.g., user authentication/authorization) via HTTP, adhering to Clean Architecture's dependency rules by orchestrating interactions with inner layers.
- **Presentation Layer's Role for a Specific Feature**:
    - **HTTP-Specific Handling**: Manage the transport of feature-related data and credentials (e.g., extracting request data from body/query/path, setting response headers or cookies).
    - **API Exposure**: Define API endpoints using FastAPI's routing capabilities for the feature's operations (e.g., login, logout, user creation).
    - **Security Marking**: When applicable, utilize FastAPI's `Security` dependency and OpenAPI security schemes to declare authentication/authorization requirements for routes, aiding documentation and enforcement.
    - **Input/Output Mapping**: Map incoming HTTP requests (often Pydantic models for validation) to application-layer DTOs and translate responses from interactors/query services back into HTTP-friendly formats.
    - **Middleware Integration**: Employ ASGI middleware for cross-cutting concerns related to the feature, such as automatically processing tokens on incoming requests or modifying response headers for session management.
- **General Implementation Steps and Considerations**:
    1.  **Define Endpoints**: Create FastAPI routes (`APIRouter`, `@router.get`, `@router.post`, etc.) for the feature's operations.
    2.  **Basic Input Validation**: Use Pydantic models for basic validation of incoming request bodies, query parameters, or path parameters (e.g., data types, required fields, basic format checks). Remember to convert these Pydantic models to application-layer DTOs (simple dataclasses or TypedDicts) before passing data to interactors/query services, to maintain layer separation.
    3.  **Delegate to Application Layer**: Inject and call the appropriate Application Layer interactors or query services (`FromDishka`, `@inject`) to perform the core business logic. The Presentation Layer should not contain business logic itself.
    4.  **Handle Responses**: Process the results returned from the Application Layer. This might involve serializing application-specific query models into JSON responses, returning HTTP status codes (200 OK, 201 Created, 204 No Content), or, for authentication, instructing a transport mechanism to set a security token (e.g., JWT in a cookie).
    5.  **Manage HTTP Transport Details**: For features involving complex HTTP interactions (like authentication), implement dedicated mechanisms (e.g., adapters implementing `AuthSessionTransport`) to abstract away how data or security tokens are sent and received via HTTP. This often involves ASGI middleware.
    6.  **OpenAPI Documentation**: Ensure routes are correctly documented with descriptions, request/response schemas, and, if applicable, security requirements using `fastapi.Security` and custom `APIKeyCookie` or similar for OpenAPI.
    7.  **Error Handling**: Map application-specific errors (from Application or Domain layers) to appropriate HTTP status codes and user-friendly error messages using `fastapi_error_map.ErrorAwareRouter` and `ErrorTranslator` implementations.

- **Project Example (Authentication and Authorization)**: The project uses JWT tokens with cookies for authentication. This is facilitated by components like `access_token_processor_jwt.py` (for token encoding/decoding), `session_transport_jwt_cookie.py` (adapting session transport to HTTP cookies), `asgi_middleware.py` (handling cookie lifecycle), and `openapi_marker.py` (for OpenAPI documentation of the cookie scheme). Controllers for account management (e.g., `log_in.py`, `log_out.py`, `sign_up.py`) demonstrate these principles, utilizing Pydantic for request validation and delegating to application-layer handlers.

### C. Error Handling (`src/app/presentation/http/errors/`)
- **Purpose**: Centralized handling and translation of exceptions that occur during request processing.
- **Implementation**:
    - `callbacks.py`: Defines logging callbacks (`log_info`, `log_error`) for handled exceptions.
    - `translators.py`: Provides `ErrorTranslator` implementations (e.g., `ServiceUnavailableTranslator`) to transform exceptions into user-friendly error response models.
    - `ErrorAwareRouter` uses these components via its `error_map` and `default_on_error` parameters.

## 3. Unit Testing the Presentation Layer (`tests/app/unit/presentation/`)

- **Location**: All unit tests for the presentation layer reside in `tests/app/unit/presentation/`. The subdirectories mirror the structure of `src/app/presentation/`.
- **Framework**: `pytest` and `pytest-asyncio` are used, often with `httpx.AsyncClient` for testing API endpoints.
- **Isolation**:
    - Controllers are tested by mocking their dependencies (Interactors, Query Services).
    - Authentication and middleware components are tested in isolation.
- **Test Scenarios**:
    - Verify correct HTTP status codes for various successful and error conditions.
    - Test input validation (Pydantic models) and ensure appropriate 400 Bad Request responses for invalid input.
    - Assert that controllers correctly call the Application Layer with transformed data.
    - Verify that responses are correctly formatted (e.g., JSON structure).
    - Test authentication and authorization flows, ensuring protected routes behave as expected.

## 4. Interfaces and Cross-Layer References

### A. Allowed References for the Presentation Layer
- The Presentation Layer can reference:
    - Components within the Presentation Layer itself.
    - The Application Layer (Interactors, Query Services, DTOs, Application-specific exceptions).
    - The Domain Layer (Value Objects, Enums, Domain-specific exceptions) for type hints or exception handling.
    - Approved external libraries that assist with HTTP handling (e.g., `FastAPI`, `Pydantic`, `jwt`).

### B. Disallowed References for the Presentation Layer
- The Presentation Layer should **not reference** the Infrastructure Layer directly, except for specific authentication/authorization components that are explicitly designed to be part of the HTTP interface (e.g., `app.infrastructure.auth.session.model.AuthSession` for internal details of authentication).
- It should **not contain any business logic**.

## 5. Pydantic Usage Best Practices
- Use Pydantic models for request bodies and response models to generate OpenAPI documentation and perform basic type validation.
- Avoid placing complex business logic directly within Pydantic validators (`@field_validator`, `@model_validator`) in the Presentation Layer. Delegate business rule validation to the Application or Domain Layers.
- When passing data from the Presentation Layer to the Application Layer, convert Pydantic models to simpler dataclasses or TypedDicts to maintain architectural boundaries and reduce coupling to Pydantic.