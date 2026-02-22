import logging

from app.application.common.ports.user_query_gateway import UserQueryModel
from app.application.common.services.current_user import CurrentUserService

log = logging.getLogger(__name__)


class GetCurrentUserQueryService:
    """
    - Open to any authenticated user.
    - Retrieves the current authenticated user's information.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
    ) -> None:
        self._current_user_service = current_user_service

    async def execute(self) -> UserQueryModel:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        log.info("Get current user: started.")

        current_user = await self._current_user_service.get_current_user()

        result = UserQueryModel(
            id_=current_user.id_.value,
            username=current_user.username.value,
            role=current_user.role,
            is_active=current_user.is_active,
        )

        log.info(
            "Get current user: done. User ID: '%s', username: '%s'.",
            current_user.id_.value,
            current_user.username.value,
        )

        return result
