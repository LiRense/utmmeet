from kubernetes import client, config

def reader(podname: str):
    try:
        # Замените на имя вашего пода и неймспейса
        pod_name = "my-pod-name"
        namespace = "default"
        container_name = "my-container-name"  # Опционально, если в поде несколько контейнеров

        # Получение логов пода
        # 'log_lines' может быть, например, 100, чтобы получить последние 100 строк
        pod_logs = api_instance.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container_name,
            # tail_lines=100 # Можно указать количество последних строк
        )
        print(pod_logs)

    except client.ApiException as e:
        print(f"Ошибка при получении логов: {e}")


import os

def waiter():
    # Пример: запуск команды, например, 'sleep 5'
    pid = os.fork() # Пример на POSIX-системах
    if pid == 0:
        # Дочерний процесс
        os.system("sleep 5") # Команда, которую нужно выполнить
        os._exit(0) # Важно для правильного завершения дочернего процесса
    else:
        # Родительский процесс
        print(f"Жду завершения процесса с PID: {pid}")
        exit_status = os.waitpid(pid)
        print(f"Процесс завершен с состоянием: {exit_status}")
        # Получить код выхода
        exit_code = os.waitstatus_to_exitcode(exit_status[1])
        print(f"Код выхода: {exit_code}")