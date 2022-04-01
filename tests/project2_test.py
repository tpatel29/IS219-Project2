"""Testing the Calculator"""
import pytest
from app.db.models import User


@pytest.mark.parametrize(
    ("email", "password", "message"), (
            ("tester@gmail.com", "wrongPassword", b"Invalid username or password"),
            ("tester@gmail.com", "notTheRightPassword", b"Invalid username or password"),
            ("tester@gmail.com", "password", b"Welcome"),
    ),
)
def test_bad_login_pass(client, email, password, message):
    response = client.post("/login", data={"email": email, "password": password},
                           follow_redirects=True)
    print(response.data)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "message"), (
            ("wrongEmail@gmail.com", "password", b"Invalid username or password"),
            ("testingEmail@gmail.com", "password", b"Invalid username or password"),
            ("tester@gmail.com", "password", b"Welcome"),
    ),
)
def test_bad_login_email(client, email, password, message):
    response = client.post("/login", data={"email": email, "password": password},
                           follow_redirects=True)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm", "message"), (
            ("", "password", "password", b'This field is required'),
    ),
)
def test_bad_regis_email(client, email, password, confirm, message):
    response = client.post("/register", data={"email": email, "password": password, "confirm": confirm},
                           follow_redirects=True)
    if message not in response.data:
        print(response.data)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm", "message"), (
            ("tester@gmail.com", "password", "notMatching", b'Passwords must match'),
            ("tester@gmail.com", "password", "NotTheRightOne", b'Passwords must match'),
            ("tester@gmail.com", "password", "ForSureNotMatching", b'Passwords must match'),
    ),
)
def test_bad_regis_confirm(client, email, password, confirm, message):
    response = client.post("/register",
                           data={"email": email, "password": password, "confirm": confirm},
                           follow_redirects=True)

    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm", "message"), (
            ("whatarethoses@gmail.com", "123", "123", b'Password must be between 6 and 35 characters'),
            ("whatarethoses@gmail.com", "1", "1", b'Password must be between 6 and 35 characters'),
            ("whatarethoses@gmail.com", "abcde", "abcde", b'Password must be between 6 and 35 characters'),
    ),
)
def test_bad_regis_pass(client, email, password, confirm, message):
    response = client.post("/register", data={"email": email, "password": password, "confirm": confirm},
                           follow_redirects=True)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm", "message"), (
            ("tester@gmail.com", "password", "password", b'Already Registered'),
            ("test@gmail.com", "password", "password", b'Already Registered'),
    ),
)
def test_already_regis(client, email, password, confirm, message):
    response = client.post("/register",
                           data={"email": email, "password": password, "confirm": confirm},
                           follow_redirects=True)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "message"), (
            ("tester@gmail.com", "password", b'Welcome'),
            ("test@gmail.com", "password", b'Welcome'),
    ),
)
def test_success_login(client, email, password, message):
    response = client.post("/login",
                           data={"email": email, "password": password},
                           follow_redirects=True)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm", "message"), (
            ("testtt@gmail.com", "password", "password", b'Congratulations, you are now a registered user'),
            ("testttttt@gmail.com", "password", "password", b'Congratulations, you are now a registered user'),
    ),
)
def test_success_regis(client, application, email, password, confirm , message):
    response = client.post("/register",
                           data={"email": email, "password": password, "confirm": confirm},
                           follow_redirects=True)
    assert message in response.data
    with application.app_context():
        """THIS IS TO LOGIN FOR ADMIN ACCOUNT SO WE CAN HAVE ACCESS TO THE DELETE ROUTE"""
        client.post("/login", data={"email": "test@gmail.com", "password": "password"}, follow_redirects=True)
        user = User.query.filter_by(email=email).first()
        response = client.post("/users/" + user.get_id() + "/delete", follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.parametrize(
    ("email", "password", "message"), (
            ("tester@gmail.com", "password",b'Please log in to access this page'),
            ("test@gmail.com", "password", b'Please log in to access this page'),
    ),
)
def test_deny_dashboard_assess(client, application, email, password, message):
    with application.app_context():
        client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
        client.get("/logout", follow_redirects=True)
        response = client.get("/dashboard", follow_redirects=True)
        assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "message"), (
            ("testing@gmail.com", "password", b'Dashboard'),
            ("test@gmail.com", "password", b'Dashboard'),
    ),
)
def test_allow_dashboard_assess(client, application, email, password, message):
    with application.app_context():
        client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
        response = client.get("/dashboard", follow_redirects=True)
        assert message in response.data
