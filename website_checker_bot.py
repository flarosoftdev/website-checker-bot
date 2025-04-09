# (c) 2025 Flarosoft Development.
# Github Repository: https://github.com/flarosoftdev/Telegram-Mesage-Sender.git
# Developer's Telegram channel: https://t.me/flarosoftdev
# Telegram Channel with Flarosoft Bots: https://t.me/FlarosoftBots

__author__ = "Flarosoft"
__version__ = "0.1"
__author_email__ = "flarosoft.dev@gmail.com"

import telebot
import requests
from bs4 import BeautifulSoup
import logging
import os
from time import sleep
import re
import sys
import time

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

FILES_PATH = "website_checker_bot/"

if not os.path.exists(FILES_PATH):
    os.makedirs(FILES_PATH)

def analyze_site(url):
    result = {}
    try:
        response = requests.get(url, timeout=10)
        html_code = response.text
        result["html_code"] = html_code
        result["status_code"] = response.status_code
        headers = response.headers
        result["headers"] = dict(headers)
        
        score = 100
        
        if not url.startswith("https"):
            score -= 20
            result["https_warning"] = "Сайт НЕ использует HTTPS"
        else:
            result["https_warning"] = "Сайт использует HTTPS"
        
        required_headers = {
            "Content-Security-Policy": "Отсутствует заголовок Content-Security-Policy",
            "X-Frame-Options": "Отсутствует заголовок X-Frame-Options",
            "X-XSS-Protection": "Отсутствует заголовок X-XSS-Protection",
            "Strict-Transport-Security": "Отсутствует заголовок Strict-Transport-Security"
        }
        for header, warning in required_headers.items():
            if header not in headers:
                score -= 15
                result[header] = warning
            else:
                result[header] = "Присутствует"
        
        soup = BeautifulSoup(html_code, "html.parser")
        
        result["headings"] = {
            "h1": [h.get_text() for h in soup.find_all("h1")],
            "h2": [h.get_text() for h in soup.find_all("h2")],
            "h3": [h.get_text() for h in soup.find_all("h3")],
            "h4": [h.get_text() for h in soup.find_all("h4")],
            "h5": [h.get_text() for h in soup.find_all("h5")],
            "h6": [h.get_text() for h in soup.find_all("h6")]
        }

        result["links"] = [a.get('href') for a in soup.find_all('a', href=True)]
        
        result["meta_tags"] = {meta.get('name', meta.get('property')): meta.get('content') for meta in soup.find_all('meta')}

        text_content = soup.get_text()
        result["text_content"] = text_content
        
        css_code = ""
        for link in soup.find_all("link", {"rel": "stylesheet"}):
            css_code += f"\n{link.get('href')}\n"
        for style in soup.find_all("style"):
            css_code += f"\n{style.get_text()}\n"
        result["css_code"] = css_code

        js_code = ""
        for script in soup.find_all("script"):
            if script.get("src"):
                js_code += f"\n{script.get('src')}\n"
            else:
                js_code += f"\n{script.get_text()}\n"
        result["js_code"] = js_code
        
        result["security_percentage"] = max(score, 0)

        result["html_file"] = save_file("html_code.html", html_code)
        result["css_file"] = save_file("css_code.css", css_code)
        result["js_file"] = save_file("js_code.js", js_code)
        result["text_file"] = save_file("text_content.txt", text_content)
        result["headings_file"] = save_file("headings.txt", str(result["headings"]))
        result["links_file"] = save_file("links.txt", "\n".join(result["links"]))
        result["meta_tags_file"] = save_file("meta_tags.txt", str(result["meta_tags"]))
    except Exception as e:
        logger.error(f"Ошибка при анализе сайта {url}: {e}")
        result["error"] = str(e)
    
    return result

def save_file(file_name, content):
    try:
        file_path = os.path.join(FILES_PATH, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла {file_name}: {e}")
        return None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! "
        "Пришлите мне URL сайта, и я отправлю его глубокий security-чек. "
        "Я проверю HTTPS, заголовки, сделаю анализ кода, соберу все ссылки, мета-теги и многое другое!"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    analysis = analyze_site(url)
    chat = message.chat.id

    logging.info(f"Received request from {chat}: {url}")
    
    if "error" in analysis:
        bot.reply_to(message, f"Произошла ошибка: {analysis['error']}")
    else:
        response_message = (
            f"*Статус-код*: {analysis['status_code']}\n"
            f"*Процент безопасности*: {analysis['security_percentage']}%\n"
            f"HTTPS: {analysis.get('https_warning', 'Нет данных')}\n"
            "*Заголовки безопасности*:\n"
            f"  *Content-Security-Policy*: {analysis.get('Content-Security-Policy', 'Нет данных')}\n"
            f"  *X-Frame-Options*: {analysis.get('X-Frame-Options', 'Нет данных')}\n"
            f"  *X-XSS-Protection*: {analysis.get('X-XSS-Protection', 'Нет данных')}\n"
            f"  *Strict-Transport-Security*: {analysis.get('Strict-Transport-Security', 'Нет данных')}\n"
        )
        if analysis["html_file"]:
            try:
                with open(analysis["html_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="HTML код сайта")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти HTML код сайта. Подробности: {e}")
        if analysis["css_file"]:
            try:
                with open(analysis["css_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="CSS код сайта")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти CSS код сайта. Подробности: {e}")

        if analysis["js_file"]:
            try:
                with open(analysis["js_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="JavaScript код сайта")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти JavaScript код сайта. Подробности: {e}")

        if analysis["text_file"]:
            try:
                with open(analysis["text_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="Текстовое содержимое сайта")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти текстовое содержимое сайта. Подробности: {e}")
        
        if analysis["headings_file"]:
            try:
                with open(analysis["headings_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="Заголовки сайта (h1, h2, h3, и т.д.)")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти заголовки сайта. Подробности: {e}")

        if analysis["links_file"]:
            try:
                with open(analysis["links_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="Ссылки на сайте")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти ссылки на сайте. Подробности: {e}")

        if analysis["meta_tags_file"]:
            try:
                with open(analysis["meta_tags_file"], 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="Мета-теги сайта")
            except Exception as e:
                bot.send_message(message.chat.id, f"Невозможно найти мета-теги сайта. Подробности: {e}")

        bot.reply_to(message, response_message, parse_mode="Markdown")


def restart_bot():
    logging.info("Restarting the bot...")
    time.sleep(5)
    os.execv(sys.executable, [sys.executable] + sys.argv)
    

if __name__ == "__main__":
    while True:
        try:
            logging.info("Starting the bot...")
            bot.polling(none_stop=True, timeout=60)
        except (Exception, OSError, ConnectionError) as e:
            logging.error(f"An error occurred: {e}. The bot will be restarted")
            restart_bot()
        except KeyboardInterrupt:
            logging.info("Bot manually stopped. Exiting...")
            break
