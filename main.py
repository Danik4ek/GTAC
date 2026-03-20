#!/usr/bin/env python3
import socket
import time
import threading
import struct
import random
import hashlib
from typing import Optional


class GorillaTagBot:
    """
    Простой бот для Gorilla Tag - только подключение к комнате
    """

    def __init__(self, room_code: str = "RUSSIAN300"):
        self.auth_server = ("45.67.210.16", 5055)
        self.room_code = room_code
        self.MY_GUID = "5dc33b5-d5fc-4b4c-bf88-eb70baab"

        # Сокет
        self.sock = None
        self.client_port = 55806
        self.room_server = None  # Игровой сервер

        # Динамические ID
        self.temp_session_id: Optional[bytes] = None
        self.server_token: Optional[bytes] = None
        self.server_id: Optional[bytes] = None

        # Счетчики
        self.packets_sent = 0
        self.packets_received = 0

        # P0 пакет (инициализация Photon)
        self.P0_PACKET = bytes.fromhex(
            "c3 00 00 00 01 08 78 e7 98 46 bb f3 79 84 00 00"
            "44 9e b2 e2 1b 4d 8b cc 2f c9 3e ef 81 49 95 4a"
            "5b a6 36 4b 91 19 1b 7d 0e e9 3f 38 ff 91 92 fd"
            "16 ef b7 a2 03 e5 43 c7 72 31 e3 fc f6 8f 00 bb"
            "2f c3 4b 06 5a a2 45 df 19 eb 8e c2 84 a7 7d 1b"
            "50 7b 73 b3 71 92 bc 8a 6a 3d 98 58 26 0c 1c 6b"
            "fb 2d 74 29 bc 3c a1 d6 d0 1c 79 37 29 32 91 0c"
            "3d 3f f2 0e 52 24 09 10 04 82 96 34 ba ab 8d 9d"
            "fe d6 d0 aa f6 9e 86 70 30 1c de aa 3e 50 2c 27"
            "26 40 fa 4b ed f3 24 32 a9 fd 3e b4 e4 e0 4d 5d"
            "9d 02 59 3e fc 68 67 fa a7 b4 b8 a9 87 d9 22 19"
            "53 c1 a2 e9 0b 70 d1 7e 7a 14 e9 f8 ce 79 a9 42"
            "9b cd 93 a2 e2 35 e4 e6 73 d9 27 5d 78 03 3d e0"
            "32 e9 77 3a 51 e9 1b 22 17 9d 32 be 9e 97 84 61"
            "ab b4 6e 1a a9 55 7e 4b 35 eb c3 15 24 83 23 2b"
            "2f c8 63 32 51 06 bd 18 d7 4b b2 87 55 d6 b5 58"
            "71 04 35 96 9b 01 a9 69 9c 46 d2 63 8f bb ab e4"
            "eb db 59 16 19 d9 e9 69 76 d2 50 77 3d 6f e9 bc"
            "f8 48 d9 f6 e4 9e 16 20 1a 4d 9b aa 8c 2a e0 f0"
            "0c 2a fd b3 3d 92 6c 43 1d b8 f4 4a b5 f1 19 25"
            "28 bc a7 01 9a 34 20 ec df 0d eb 8d 52 b5 b7 74"
            "15 80 b6 30 a1 0b 9d 8b 51 dd 96 83 2c 2c 33 d1"
            "e6 6c 24 ac de fe a8 7e b5 af 11 4a 6d 04 f7 b1"
            "8f 70 a5 c4 d7 b6 5d 6d f5 6d fd e1 7e ef b0 2a"
            "f8 9f 39 9d 6c 65 0a 17 8b 7e b0 49 a8 d3 76 0c"
            "36 d5 e7 ab 8a ab ff 55 21 61 d1 db d4 d7 63 fb"
            "d6 43 45 07 cc f9 f9 2a 91 bd 54 ed 8c e3 08 cc"
            "cd 9a 0d 7e 04 d8 f5 87 00 f8 29 55 b8 53 8c d0"
            "11 ee 0a 0e b1 d8 b0 2d b1 1f 3e 39 fa fa 17 48"
            "61 fc 12 73 4e 62 f5 f9 d5 a8 ce 7a a1 09 e5 be"
            "3c 2e 31 f4 d4 1d 7b cb 52 85 36 e7 84 5a 70 b8"
            "24 4b d5 2d 1c f8 fc b6 ae f4 09 b4 6c db 8f d3"
            "50 0b 3f a3 1d a4 93 a5 9d f9 85 b7 50 69 b8 db"
            "ea 35 ad 28 1d 96 b3 fb 5c dd 64 99 83 35 55 49"
            "72 c3 d9 d3 a0 c1 70 b0 6e 1a 7b bd b1 2c 43 30"
            "4f 00 6f 33 72 0d 35 9a 9d f3 57 76 c0 f6 ed 0d"
            "eb a3 5e d2 89 f9 63 7d 14 23 bf 5c 5e c0 61 c2"
            "ea a2 be 66 16 db 1a 47 35 3f a8 f0 b2 fb 66 19"
            "a2 9b 24 88 13 17 b2 2c 35 92 39 24 9f 3e ed f7"
            "b5 f7 e7 22 5e 0f 8e 5e 3c a7 41 b7 05 17 6b dd"
            "29 ea 86 65 b5 0d 01 4a 97 55 ce 0d 11 10 4c 0c"
            "0b e5 d6 2e d3 43 60 67 d8 04 f4 d1 e3 e9 41 af"
            "d1 68 a6 ee af 45 57 32 d3 2b 70 b4 9d 4a ec d8"
            "45 4f 05 98 4e 70 a6 8e 80 e1 f3 f0 be 13 d3 ab"
            "ca d3 68 5a 13 e2 7f 9f 53 6c 2b 14 1f 7c 6f 5e"
            "3a c6 6f 99 8f c6 f2 20 0f 77 8a e7 45 05 7c c3"
            "5b c4 3e 07 30 c8 88 29 01 f4 44 30 31 23 0d 9a"
            "34 44 ba 40 75 6e 07 43 48 01 9a e1 63 78 a4 90"
            "df 24 50 85 16 b0 bb 89 a4 ad 93 9f ea f7 d9 45"
            "2e 96 b7 be 30 c7 4b 38 09 44 94 c1 5c b2 53 e5"
            "a0 1c c3 e7 59 3a e5 8e 59 28 cf ad 4b 1d 70 ed"
            "79 d1 19 6e 0f e5 0f 5b e3 03 7a 6d db fa d8 99"
            "8c 66 cf bf 8f f3 ed 28 cd 8b b8 58 09 51 c4 6f"
            "81 c0 c5 99 3f 4a af 9f 03 50 36 d6 14 10 76 fd"
            "8b f7 df 29 57 16 fc 81 ce ef f9 d2 49 be 09 20"
            "8f f3 e7 ea 07 ee 8b 48 55 51 d2 12 a8 71 74 05"
            "99 b0 3c ca 8c 21 48 9e 94 63 c4 62 f7 6b 02 41"
            "1e 7a be 50 bc 44 07 7f a7 41 b2 fa b1 00 a3 7b"
            "10 46 a1 c2 12 00 9f 68 49 72 2d 51 c3 dc ea d0"
            "71 78 0f cb f7 ba 0c 3a 93 b2 14 c8 d1 fc e4 d8"
            "35 64 49 8c a7 03 13 0e d4 ba 04 4e 39 12 3e 38"
            "30 2c 3a 98 0b b5 ee 01 cb 62 2c 1b 23 29 ec 48"
            "6c 8b 8e 59 35 88 13 f8 e9 5e 02 04 9d 90 ad 04"
            "21 b9 16 81 01 37 d0 d0 15 20 44 68 6e c8 fa 14"
            "6b 88 28 bc e5 a5 51 08 6f 6f 7a 14 13 bb 3d b9"
            "c9 5f 7c 2d 32 39 f7 cc 5d 70 4f 19 4a 5b 22 49"
            "73 f4 2c 84 a2 05 76 ef 62 38 ac e6 c7 4f 53 f9"
            "12 6e 34 0a 70 b6 cd 48 4c 6b 51 0d cf d1 88 75"
            "fa 66 e8 a1 c7 0d a5 64 78 8a 51 72 b2 b8 dc f5"
            "13 33 a3 f2 c8 5d 9c 3f 02 90 46 b0 94 ff b7 d3"
            "5c 4a 03 d1 a1 6b ea a9 ed 27 83 74 2f 8a a8 51"
            "ca 0c 5c 64 92 73 aa 38 1d d9 0c 95 22 8c bf bd"
            "9f b4 5b 0e ed f6 4c 69 c4 69 a2 42 90 4f 95 40"
            "4a fd e3 0a 0d 03 c4 b1 8a 01 6f 5b b7 4a b6 91"
            "06 4a a3 ed 89 cc 95 05 0b 22 23 46 ad 0c 70 56"
        )

    def create_socket(self):
        """Создает сокет на фиксированном порту"""
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.client_port))
        self.sock.settimeout(5.0)
        print(f"🔌 Сокет создан на порту {self.client_port}")

    def send_packet(self, packet: bytes, addr: Optional[tuple] = None,
                    wait_response: bool = True, timeout: float = 5.0) -> Optional[bytes]:
        """Отправляет пакет и ждет ответ"""
        if addr is None:
            addr = self.auth_server

        try:
            self.packets_sent += 1
            self.sock.sendto(packet, addr)
            print(f"  📤 [{self.packets_sent}] Sent {len(packet)} bytes")

            if wait_response:
                self.sock.settimeout(timeout)
                try:
                    response, resp_addr = self.sock.recvfrom(4096)
                    self.packets_received += 1
                    print(f"  📥 [{self.packets_received}] Received {len(response)} bytes")
                    return response
                except socket.timeout:
                    print(f"  ⏰ Timeout")
                    return None
            return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None

    def generate_temp_session_id(self) -> bytes:
        """Генерирует временный Session ID"""
        hash_input = f"{self.MY_GUID}_{time.time()}".encode()
        return hashlib.md5(hash_input).digest()[:4]

    def create_auth_request_packet(self, temp_session_id: bytes) -> bytes:
        """Создает пакет для запроса аутентификации"""
        template = bytes.fromhex(
            "ff ff 00 01 00 00 00 02 00 00 00 00 02 ff 01 04"
            "00 00 00 2c 00 00 00 01 00 00 04 b0 00 00 80 00"
            "00 00 00 02 00 00 00 00 00 00 00 00 00 00 13 88"
            "00 00 00 02 00 00 00 02"
        )
        packet = bytearray(template)
        packet[8:12] = temp_session_id
        return bytes(packet)

    def create_final_auth_packet(self, temp_session_id: bytes, server_token: bytes) -> bytes:
        """Создает финальный пакет аутентификации"""
        template = bytes.fromhex(
            "ff ff 00 01 00 00 00 a5 00 00 00 00 01 ff 00 04"
            "00 00 00 14 00 00 00 00 00 00 00 00 00 00 00 00"
        )
        packet = bytearray(template)
        packet[8:12] = temp_session_id
        if len(server_token) == 4:
            packet[24:28] = server_token
        return bytes(packet)

    def create_join_request_packet(self) -> bytes:
        """Создает пакет для запроса на подключение"""
        packet = bytearray(56)
        packet[0:4] = bytes.fromhex("ff ff 00 01")
        packet[4:8] = struct.pack('<I', 0x00000015)
        packet[8:12] = self.temp_session_id if self.temp_session_id else bytes(4)
        packet[12:16] = bytes.fromhex("02 ff 01 04")
        packet[16:20] = bytes.fromhex("00 00 00 2c")
        packet[20:24] = bytes.fromhex("00 00 00 01")
        packet[24:28] = bytes.fromhex("00 00 04 b0")
        packet[28:32] = bytes.fromhex("00 00 80 00")
        packet[32:36] = bytes.fromhex("00 00 00 02")
        packet[36:56] = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 13 88 00 00 00 02 00 00 00 02")
        return bytes(packet)

    def create_guid_packet(self) -> bytes:
        """Создает пакет для отправки GUID"""
        packet = bytearray(85)
        packet[0:4] = bytes.fromhex("82 d0 00 02")
        packet[4:8] = struct.pack('<I', 0x00000078)

        if self.server_id:
            packet[8:12] = self.server_id
        else:
            packet[8:12] = bytes.fromhex("0a 03 c2 37")

        packet[12:16] = bytes.fromhex("01 ff 00 04")
        packet[16:20] = bytes.fromhex("00 00 00 14")
        packet[20:36] = bytes.fromhex("00 00 00 00 00 00 00 01 d0 d9 a9 59 06 00 01 04")
        packet[36:40] = bytes.fromhex("00 00 00 35")
        packet[40:44] = bytes.fromhex("00 00 00 01")
        packet[44:48] = bytes.fromhex("f3 00 01 08")
        packet[48:52] = bytes.fromhex("1e 41 08 0f")
        packet[52:56] = bytes.fromhex("00 37")

        # Добавляем GUID
        guid_bytes = self.MY_GUID.encode('ascii')
        packet[56:56 + len(guid_bytes)] = guid_bytes

        return bytes(packet)

    def create_key_exchange_packet(self) -> bytes:
        """Создает пакет для обмена ключами"""
        packet = bytearray(159)
        packet[0:4] = bytes.fromhex("82 d0 00 03")
        packet[4:8] = struct.pack('<I', 0x000000d4)

        if self.server_id:
            packet[8:12] = self.server_id
        else:
            packet[8:12] = bytes.fromhex("0a 03 c2 37")

        packet[12:16] = bytes.fromhex("01 00 00 04")
        packet[16:20] = bytes.fromhex("00 00 00 14")
        packet[20:36] = bytes.fromhex("00 00 00 00 00 00 00 01 17 01 26 17 06 00 01 04")
        packet[36:40] = bytes.fromhex("00 00 00 73")
        packet[40:44] = bytes.fromhex("00 00 00 02")
        packet[44:48] = bytes.fromhex("f3 06 00 01")
        packet[48:52] = bytes.fromhex("01 43 60")

        # Случайные данные для ключа
        random_bytes = bytes([random.randint(0, 255) for _ in range(107)])
        packet[52:159] = random_bytes

        return bytes(packet)

    def create_create_game_packet(self) -> bytes:
        """Создает пакет для создания/подключения к комнате"""
        packet = bytearray(61)
        packet[0:4] = bytes.fromhex("82 d0 00 02")
        packet[4:8] = struct.pack('<I', 0x00000155)

        if self.server_id:
            packet[8:12] = self.server_id
        else:
            packet[8:12] = bytes.fromhex("0a 03 c2 37")

        packet[12:16] = bytes.fromhex("01 00 00 04")
        packet[16:20] = bytes.fromhex("00 00 00 14")
        packet[20:36] = bytes.fromhex("00 00 00 00 00 00 00 03 d0 d9 aa 44 06 00 01 04")
        packet[36:40] = bytes.fromhex("00 00 00 1d")
        packet[40:44] = bytes.fromhex("00 00 00 04")
        packet[44:48] = bytes.fromhex("f3 02 e2 01")
        packet[48:52] = bytes.fromhex("ff 07 0a")

        # Добавляем название комнаты
        room_bytes = self.room_code.encode('ascii')
        packet[52:52 + len(room_bytes)] = room_bytes

        return bytes(packet)

    def create_keepalive_packet(self) -> bytes:
        """Создает простой пакет для поддержания соединения"""
        packet = bytearray(32)
        packet[0:4] = bytes.fromhex("ff ff 00 01")
        packet[4:8] = struct.pack('<I', 0x0000000e)
        packet[8:12] = self.temp_session_id if self.temp_session_id else bytes(4)
        packet[12:16] = bytes.fromhex("01 ff 00 04")
        packet[16:20] = bytes.fromhex("00 00 00 14")
        packet[20:24] = bytes.fromhex("00 00 00 00")
        packet[24:28] = bytes.fromhex("c3 05 82 0d")  # Random ID
        return bytes(packet)

    def extract_server_id_from_response(self, response: bytes) -> Optional[bytes]:
        """Извлекает server_id из ответа сервера"""
        if len(response) < 30:
            return None

        # Ищем паттерн: после 01 ff 00 00 00 00 00 14 00 00
        marker = bytes.fromhex("01 ff 00 00 00 00 00 14 00 00")
        pos = response.find(marker)
        if pos != -1 and pos + len(marker) + 4 <= len(response):
            potential_id = response[pos + len(marker):pos + len(marker) + 4]
            if potential_id != b'\x00\x00\x00\x00':
                print(f"      Найден server_id: {potential_id.hex()}")
                return potential_id

        # Альтернативный поиск
        for i in range(20, len(response) - 4):
            candidate = response[i:i + 4]
            if all(b != 0 for b in candidate):
                if candidate != self.server_token:
                    print(f"      Найден server_id на смещении {i}: {candidate.hex()}")
                    return candidate

        return None

    def keep_alive_loop(self):
        """Простой цикл для поддержания соединения"""
        print("\n🔄 Запуск keep-alive...")
        while self.running:
            try:
                if self.room_server and self.in_room:
                    # Отправляем простой пакет каждые 30 секунд
                    keepalive = self.create_keepalive_packet()
                    self.send_packet(keepalive, addr=self.room_server, wait_response=False)
                time.sleep(30)
            except Exception as e:
                print(f"Ошибка keep-alive: {e}")
                break

    def run(self):
        """Основной метод - только подключение к комнате"""
        print("\n" + "=" * 70)
        print("🤖 Gorilla Tag Bot - ПОДКЛЮЧЕНИЕ К КОМНАТЕ")
        print("=" * 70)
        print(f"🎮 Комната: {self.room_code}")
        print(f"🆔 GUID: {self.MY_GUID}")
        print()

        try:
            # Создаем сокет
            self.create_socket()
            self.running = True

            # ФАЗА 0: 12 инициализационных пакетов
            print("\n" + "=" * 60)
            print("🟢 ФАЗА 0: Инициализация (12 пакетов)")
            print("=" * 60)
            for i in range(12):
                print(f"   Пакет {i + 1}/12")
                self.send_packet(self.P0_PACKET, wait_response=False)
                time.sleep(0.001)

            # ФАЗА 1: Аутентификация
            print("\n" + "=" * 60)
            print("🟢 ФАЗА 1: Аутентификация")
            print("=" * 60)

            self.temp_session_id = self.generate_temp_session_id()
            print(f"🆕 Session ID: {self.temp_session_id.hex()}")

            auth_request = self.create_auth_request_packet(self.temp_session_id)
            response = self.send_packet(auth_request, timeout=5.0)

            if not response:
                print("❌ Нет ответа на аутентификацию")
                return

            self.server_token = response[-4:]
            print(f"🔑 Server Token: {self.server_token.hex()}")

            time.sleep(0.05)

            # ФАЗА 2: Еще 12 пакетов
            print("\n" + "=" * 60)
            print("🟢 ФАЗА 2: Продолжение инициализации")
            print("=" * 60)
            for i in range(12):
                print(f"   Пакет {i + 1}/12")
                self.send_packet(self.P0_PACKET, wait_response=False)
                time.sleep(0.001)

            # Финальный пакет аутентификации
            print("\n📡 Финальный пакет...")
            final_packet = self.create_final_auth_packet(self.temp_session_id, self.server_token)
            response = self.send_packet(final_packet, timeout=5.0)

            if not response:
                print("❌ Нет ответа на финальный пакет")
                return

            self.server_id = self.extract_server_id_from_response(response)
            if not self.server_id:
                print("❌ Не удалось найти server_id")
                return

            print(f"✅ Server ID: {self.server_id.hex()}")

            # ФАЗА 3: Инициализация Photon
            print("\n" + "=" * 60)
            print("🟢 ФАЗА 3: Photon Join")
            print("=" * 60)

            # Еще 12 пакетов
            for i in range(12):
                print(f"   Пакет {i + 1}/12")
                self.send_packet(self.P0_PACKET, wait_response=False)
                time.sleep(0.001)

            # Join Request
            print("\n📡 Join Request...")
            join_request = self.create_join_request_packet()
            response = self.send_packet(join_request, timeout=5.0)

            if not response:
                print("❌ Нет ответа на Join Request")
                return

            # Еще 12 пакетов
            print("\n🟢 Еще 12 пакетов...")
            for i in range(12):
                print(f"   Пакет {i + 1}/12")
                self.send_packet(self.P0_PACKET, wait_response=False)
                time.sleep(0.001)

            # Отправка GUID
            print("\n📡 Отправка GUID...")
            guid_packet = self.create_guid_packet()
            response = self.send_packet(guid_packet, timeout=5.0)

            if not response:
                print("❌ Нет ответа на GUID")
                return

            print("✅ GUID подтвержден")

            # Обмен ключами
            print("\n📡 Обмен ключами...")
            key_packet = self.create_key_exchange_packet()
            response = self.send_packet(key_packet, timeout=5.0)

            if not response:
                print("❌ Нет ответа на обмен ключами")
                return

            print("✅ Ключи обменяны")

            # Запрос комнаты
            print(f"\n📡 Запрос комнаты '{self.room_code}'...")
            room_request = self.create_create_game_packet()
            response = self.send_packet(room_request, timeout=5.0)

            if not response:
                print("❌ Нет ответа на запрос комнаты")
                return

            # Проверяем ответ
            if b"Game does not exist" in response:
                print("\n⚠️  Комната не существует - создаем новую")

                # Отправляем подтверждение создания
                confirm_packet = bytes.fromhex(
                    "ff ff 00 01 00 00 00 15" + self.temp_session_id.hex() +
                    "01 00 00 04 00 00 00 14 00 00 00 00 00 00 00 04 d1 0f 13 1e 04 ff 01 04 00 00 00 0c 00 00 00 03"
                )
                response = self.send_packet(confirm_packet, timeout=5.0)

                if response:
                    print("✅ Комната успешно создана!")
            else:
                print("\n✅ Комната существует, подключение выполнено!")

            # Определяем игровой сервер
            self.room_server = ("45.67.211.78", 5055)
            print(f"🎮 Игровой сервер: {self.room_server[0]}:{self.room_server[1]}")

            self.in_room = True
            print("\n" + "=" * 60)
            print("✅ БОТ УСПЕШНО ПОДКЛЮЧЕН К КОМНАТЕ!")
            print("=" * 60)
            print("📡 Ожидание... (нажмите Ctrl+C для выхода)")
            print()

            # Запускаем keep-alive в отдельном потоке
            keep_alive_thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
            keep_alive_thread.start()

            # Просто ждем, ничего не делаем
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n👋 Завершение...")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            if self.sock:
                self.sock.close()
            print("🔌 Соединение закрыто")


if __name__ == "__main__":
    bot = GorillaTagBot("RUSSIAN300")
    bot.run()
