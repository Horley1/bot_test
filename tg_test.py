import time
import telebot
def main():
    bot = telebot.TeleBot('5199364372:AAGnaM9JbpyH2_JjTpCi1zb3EN5nWUtiwmE')
    tm = 0
    while True:
        time.sleep(2)
        tm += 2
        bot.send_message(327830972, f"Success, {tm // 3600} {(tm % 3600) // 60} {(tm % 3060) % 60}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()