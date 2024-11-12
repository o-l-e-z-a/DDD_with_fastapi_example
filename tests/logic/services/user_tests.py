class TestUserService:
    def test_add_user_correct(self, user_service_with_data, new_user_dto):
        user_service_with_data.add_user(new_user_dto)
