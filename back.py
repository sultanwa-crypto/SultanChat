import logging

logger = logging.getLogger(__name__)

try:
    import socket
    import threading
    import time

    running = False
    sock = None
    udp_sock = None

    callbacks = {}  # list of functions
    online_users = {}

    name = ""
    udp_broadcast = ""


    def set_callback(event, new_function):
        if event in callbacks:
            callbacks[event].append(new_function)
        else:
            callbacks[event] = [new_function]


    def trigger_event(event, data):
        if event in callbacks:
            for new_function in callbacks[event]:
                new_function(data)


    def set_name(new_name):
        global name
        name = new_name
        global udp_broadcast
        udp_broadcast = "UDP_BROADCAST | " + name


    def start():
        global sock
        sock = socket.socket()

        global running
        running = True

        global udp_sock
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        udp_sock.bind(("", 5000))

        udp_sock.settimeout(0.5)

        threading.Thread(target=receive_udp, daemon=True).start()

        trigger_event("start", "started")

        threading.Thread(target=send_heartbeat, daemon=True).start()


    def end():
        global running
        if sock and udp_sock is not None:
            sock.close()
            udp_sock.close()

        trigger_event("stop", "\nstopped")
        running = False


    def receive_udp():
        while running:
            try:
                data, address = udp_sock.recvfrom(1024)

            except socket.timeout:
                pass

            except Exception as e:
                logger.exception("back.py error")
                trigger_event("error", e)

            else:
                try:
                    name_udp = data.decode().split("|")[1].strip()
                    ip = address[0]
                    if name_udp != name:
                        last_seen = time.time()
                        is_new = name_udp not in online_users
                        online_users[name_udp] = {
                            "ip": ip,
                            "last_seen": last_seen
                        }
                        if is_new:
                            trigger_event("user", name_udp)
                except Exception as e:
                    logger.exception("back.py error")
                    trigger_event("error", e)
                try:

                    for username, info in list(online_users.items()):
                        if time.time() - info["last_seen"] > 2:
                            trigger_event("user_offline", username)
                            online_users.pop(username)

                except Exception as e:
                    logger.exception("back.py error")
                    trigger_event("error", e)


    def send_heartbeat():
        try:
            while running:
                udp_sock.sendto(udp_broadcast.encode(), ("255.255.255.255", 5000))
                time.sleep(0.5)
        except Exception as e:
            logger.exception("back.py error")
            trigger_event("error", e)

except Exception as r:
    logger.exception("back.py error")
