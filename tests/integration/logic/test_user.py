class TestUserService:
    async def test_add_user_correct(self, user_service_with_db_data, user_ivanov_db, new_user_dto):
        new_user = await user_service_with_db_data.add_user(new_user_dto)
