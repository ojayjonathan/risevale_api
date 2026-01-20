# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session
#
# from app.core.config import Settings
# from app.models import User
# from app.repository.otp import otp_service
# from app.tests.conftest import client, get_test_db, get_test_user, settings
#
#
# def test_login(
#     client: TestClient,
#     get_test_db: Session,
#     get_test_user: User,
#     settings: Setting,
# ):
#     response = client.post(
#         "/users/login/",
#         json={
#             "password": settings.TEST_USER_PASSWORD,
#             "phone_number": settings.TEST_USER_PHONE,
#         },
#     )
#     assert response.status_code == 200
#
#     # test the users token
#     response = client.get(
#         "/users/profile/",
#         headers={
#             "Authorization": f"Bearer {response.json().get('access_token')}",
#         },
#     )
#
#     assert response.status_code == 200
# def test_admin_login(
#     client: TestClient,
#     get_test_db: Session,
#     get_test_user: User,
#     settings: Setting,
# ):
#     response = client.post(
#         "/admin/users/login/",
#         json={
#             "password": settings.TEST_USER_PASSWORD,
#             "phone_number": settings.TEST_USER_PHONE,
#         },
#     )
#     assert response.status_code in [200, 429]
# def test_login_incorrect_password(
#     client: TestClient,
#     get_test_db: Session,
#     get_test_user: User,
#     settings: Setting,
# ):
#     response = client.post(
#         "/users/login/",
#         json={
#             "password": "112334eddssi*6554",
#             "phone_number": settings.TEST_USER_PHONE,
#         },
#     )
#     assert response.status_code == 403
#
# def test_password_reset_request(client: TestClient, settings: Setting):
#     response = client.post(
#         "/users/password-reset/request/",
#         json={"identifier": settings.TEST_USER_EMAIL},
#     )
#     assert response.status_code == 200
#     assert response.json()["message"]
#
#
# def test_password_reset_complete(
#     client: TestClient, get_test_db: Session, settings: Setting
# ):
#     reset_token = otp_service.generate_otp()
#     new_password = settings.TEST_USER_PASSWORD
#
#     response = client.post(
#         "/users/password-reset/complete/",
#         json={
#             "reset_code": reset_token,
#             "new_password": new_password,
#             "email_or_phone": settings.TEST_USER_EMAIL,
#         },
#     )
#     print(
#         response.json(),
#         {
#             "reset_code": reset_token,
#             "new_password": new_password,
#             "email_or_phone": settings.TEST_USER_EMAIL,
#         },
#     )
#     assert response.status_code == 200
#
#     # re-use a reset token
#     response = client.post(
#         "/users/password-reset/complete/",
#         json={
#             "reset_code": reset_token,
#             "new_password": new_password,
#             "email_or_phone": settings.TEST_USER_EMAIL,
#         },
#     )
#     assert response.status_code == 400
#
#
# #
# def test_token_refresh(client: TestClient, settings: Setting):
#     login_response = client.post(
#         "/users/login/",
#         json={
#             "password": settings.TEST_USER_PASSWORD,
#             "phone_number": settings.TEST_USER_PHONE,
#         },
#     )
#     assert login_response.status_code == 200
#
#     refresh_token = login_response.json().get("refresh_token")
#     assert refresh_token
#
#     refresh_response = client.post(
#         "/users/refresh-token/",
#         json={"refresh_token": refresh_token},
#     )
#     assert refresh_response.status_code == 200
#     assert "access_token" in refresh_response.json()
#
#
# def test_update_password(client: TestClient, settings: Setting, test_user_headers):
#     login_response = client.post(
#         "/users/update-password/",
#         json={
#             "old_password": settings.TEST_USER_PASSWORD,
#             "new_password": settings.TEST_USER_PASSWORD,
#         },
#         headers=test_user_headers,
#     )
#     assert login_response.status_code == 200
#
#
# # def test_deactivate_account(
# #     client: TestClient, settings: Setting, test_user_headers, get_test_db
# # ):
# #     login_response = client.post(
# #         "/users/deactivate/",
# #         json={"reason": random_string(100)},
# #         headers=test_user_headers,
# #     )
# #     assert login_response.status_code == 200
# #
# #     # login a deactivated account
# #     response = client.post(
# #         "/users/login/",
# #         json={
# #             "password": settings.TEST_USER_PASSWORD,
# #             "phone_number": settings.TEST_USER_PHONE,
# #         },
# #     )
# #     assert response.status_code == 403
# #
# #     user = (
# #         get_test_db.query(models.User).filter_by(email=settings.TEST_USER_EMAIL).first()
# #     )
# #
# #     user.is_active = True
# #     get_test_db.commit()
