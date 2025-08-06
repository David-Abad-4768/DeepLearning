from mediatr import Mediator

from app.application.models.user.UserModel import CreateResponse, User
from app.application.services.AuthService import AuthService
from app.core.utils.Logger import get_logger
from app.domain.entities.User import UserEntity
from app.infrastructure.repositories.UserRepository import UserRepository

from .CreateUserCommand import CreateCommand

logger = get_logger(__name__)


@Mediator.handler
class CreateCommandHandler:
    def __init__(self):
        self.user_repository = UserRepository.instance()

    async def handle(self, request: CreateCommand) -> CreateResponse:
        logger.info("Creating user: %s", request.user.username)

        user = UserEntity(
            username=request.user.username,
            email=request.user.email,
            password=AuthService.hash_password(request.user.password),
        )

        try:
            self.user_repository.create(user)

            return CreateResponse(
                user=User.model_validate(user, from_attributes=True),
                message="User created successfully.",
            )
        except ValueError as exc:
            logger.exception("Error creating user")
            raise ValueError(f"Error creating user: {exc}")
