from mediatr import GenericQuery

from app.application.models.user.UserModel import CreateModel, CreateResponse


class CreateCommand(GenericQuery[CreateResponse]):
    def __init__(self, user: CreateModel):
        self.user = user
