#!/usr/bin/env python3
"""
Упрощенный клиент для удаленного выполнения SQL запросов через SSH
"""

import json
import subprocess
from typing import Dict, List, Any, Optional


class RemoteMSSQLClient:
    def __init__(self, target_host: str, server_script_path: str,
                 connection_string: str, target_user: str = "user"):
        """
        Упрощенный клиент - прямой SSH без jump host

        :param target_host: Хост с SQL Server
        :param server_script_path: Путь к скрипту на удаленном сервере
        :param connection_string: Строка подключения к MSSQL
        :param target_user: Пользователь для SSH подключения
        """
        self.target_host = target_host
        self.server_script_path = server_script_path
        self.connection_string = connection_string
        self.target_user = target_user

    def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Выполнение запроса через прямой SSH
        """
        request_data = {
            "connections": {"main_db": self.connection_string},
            "connection_name": "main_db",
            "query": query,
            "params": params or {}
        }

        json_input = json.dumps(request_data, ensure_ascii=False)

        try:
            # Прямой SSH вызов
            ssh_command = [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ConnectTimeout=30',
                # f'{self.target_user}@{self.target_host}',
                f'{self.target_host}',
                f'python3 {self.server_script_path}'
            ]

            # print(f"Подключаемся к {self.target_host}")

            result = subprocess.run(
                ssh_command,
                input=json_input.encode('utf-8'),
                capture_output=True,
                timeout=60
            )

            # Логируем ошибки если есть
            if result.stderr:
                pass
                # print(f"SSH stderr: {result.stderr.decode('utf-8')}")

            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8') if result.stderr else "Unknown SSH error"
                return {"error": f"SSH error (code {result.returncode}): {error_msg}"}

            # Парсим JSON ответ
            output = result.stdout.decode('utf-8').strip()
            if not output:
                return {"error": "Empty response from server"}

            return json.loads(output)

        except subprocess.TimeoutExpired:
            return {"error": "Request timeout (60 seconds)"}
        except json.JSONDecodeError as e:
            return {"error": f"Response parse error: {e}"}
        except Exception as e:
            return {"error": f"Client error: {e}"}

    def select(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Выполнить SELECT запрос"""
        result = self.execute_query(query, params)
        if "error" in result:
            raise Exception(f"Query failed: {result['error']}")
        return result.get("data", [])

    def update(self, query: str, params: Optional[Dict] = None) -> int:
        """Выполнить UPDATE/INSERT/DELETE запрос"""
        result = self.execute_query(query, params)
        if "error" in result:
            raise Exception(f"Query failed: {result['error']}")
        return result.get("affected_rows", 0)

    def execute(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнить произвольный запрос и вернуть полный результат"""
        return self.execute_query(query, params)