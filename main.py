from dotenv import load_dotenv
from udemy import Udemy, LoginException

load_dotenv()


def main():
    udemy = Udemy("cli")
    login_error = True
    while login_error:
        try:
            # if os.getenv("EMAIL") and os.getenv("PASSWORD"):
            #     email, password = os.getenv("EMAIL"), os.getenv("PASSWORD")
            # else:
            #     email = input("Email: ")
            #     password = input("Password: ")
            # print("Trying to login")
            # udemy.manual_login(email, password)
            # udemy.get_session_info()
            login_error = False
            # print(f"Logged in as {udemy.display_name}")
            udemy.export_cookie_to_file()
            udemy.convertCookieFileToAnotherFormat()
        except LoginException as e:
            print(str(e))


def read_cookie_from_file():
    with open("cookies_udemy.json", "r") as f:
        cookie = f.read()
    return cookie


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

