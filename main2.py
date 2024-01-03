# Server.py

import socket
import threading
from dadata import Dadata

# Вставьте ваш API-ключ Dadata здесь
DADATA_API_KEY = 'e60303f2c8fe0485c94954749f1f4d47d24fb081'

# Создание экземпляра клиента Dadata
dadata = Dadata(DADATA_API_KEY)

# Функция для получения геолокации по IP-адресу через API Dadata
def get_location_by_ip(ip_address):
    try:
        # Выполнение запроса к API Dadata
        location = dadata.iplocate(ip=ip_address)
        if location and 'location' in location:
            # Возвращаем данные о местоположении, если они доступны
            return location['location']
        return None
    except Exception as e:
        print(f"Ошибка при запросе к Dadata: {e}")
        return None

# Функция для обработки подключения клиента
def handle_client(client_socket):
    while True:
        try:
            # Получение сообщения от клиента
            message = client_socket.recv(1024).decode('utf-8')
            # Проверка, является ли сообщение командой для вычисления IP
            if message.startswith('Вычисли его по ip'):
                # Извлечение IP-адреса из сообщения
                ip_address = message.split()[-1]
                # Отправка сообщения о начале вычисления
                client_socket.sendall("IP-бот: Вычисляю…".encode('utf-8'))
                # Получение геолокации по IP-адресу
                location_info = get_location_by_ip(ip_address)
                # Формирование и отправка ответа
                if location_info:
                  country = location_info.get("data", {}).get("country", "Неизвестно")
                  region = location_info.get("data", {}).get("region_with_type", "Неизвестно")
                  city = location_info.get("data", {}).get("city", "Неизвестно")
                  response = f"IP-бот: Страна: {country}, Регион: {region}, Город: {city}"
                else:
                  response = f"IP-бот: Не удалось определить местоположение по {ip_address}"
                broadcast(response)
            else:
              # Рассылка обычного сообщения всем клиентам
              broadcast(message)
        except ConnectionResetError:
            # Обработка случая, когда клиент неожиданно отключается
            print("Клиент удален")
            break
        except Exception as e:
          # Любые другие исключения
          print(f"Ошибка при обработке сообщения: {e}")
          break

# Функция для рассылки сообщений всем подключеннным клиентам
def broadcast(message):
    for client in clients:
      client.sendall(message.encode('utf-8'))

# Список для хранения подключенных клиентов
clients = []

# Функция для принятия входящих подключений 
def accept_connections(server_socket):
    while True:
        # Принятия подключения от клиента
        client_socket, _ = server_socket.accept()
        # Добавление клиента в список
        clients.append(client_socket)
        # Запуск потока для обработки сообщений от клиента
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == '__main__':
    try:
      # Создание сокета сервера
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Привязка сокета к порту
        server_socket.bind(('127.0.0.1', 12345))
        # Начало прослушивания входящих подключений
        server_socket.listen()
        print("Сервер чата запущен и ожидает подключений...")
        # Запуск функции для принятия подключений
        accept_connections(server_socket)
    finally:
        # Закрытие сессии клиента Dadata при завершении работы
        dadata.close()