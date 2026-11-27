import back

ans = 0


def user_offline(username):
    print(username + " disconnected.")


back.set_callback("user_offline", user_offline)


def receive_user(name):
    print(name + " is online.")


back.set_callback("user", receive_user)


def start(string):
    print(string)


back.set_callback("start", start)


def stop(string):
    print(string)


back.set_callback("stop", stop)

print("------------Menu System------------ \n"
      "1: Start                    "
      "2: End")

name = input("name? \n")
back.set_name(name)

while True:

    try:
        ans = int(input("Choice:"))

    except ValueError:
        print("invalid command")
        continue

    if ans == 1:

        if not back.running:
            back.start()
        else:
            print("Already running")


    elif ans == 2:

        if back.running:
            back.end()
            break
        else:
            print("Start First")


    else:
        print("invalid command")
