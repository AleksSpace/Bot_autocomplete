# Бот для автозаполнения формы
Бот предназначен для автозаполнения формы на сайте https://b24-iu5stq.bitrix24.site/backend_test/


## Запуск проекта
## Клонируйте репозиторий на свой компьютер
```
HTTPS - https://github.com/AleksSpace/bot_autocomplete.git
SSH - git@github.com:AleksSpace/bot_autocomplete.git
GitHub CLI - gh repo clone AleksSpace/bot_autocomplete
```

## Создайте и активируйте виртуальное окружение
```
python -m venv venv
```
```
. venv/Scripts/activate
```

## Обновите менеджер пакетов pip и установите зависимости из файла requirements.txt
Обновить менеджер пакетов pip
```
python -m pip install --upgrade pip
```
установить зависимости из файла requirements.txt
```
python -m pip install -r requirements.txt
```

## Создайте и заполните файл .env
После клонирования репозитория перейдите в папку проекта, там вы найдёте файл .env.example
скопируйте его в эту же директорию и поменяйте название файла на .env. После этого вам нужно заменитьданные в файле на свои.

## Сборка и запуск контейнера
Для начала нужно собрать контейнер при помощи docker-compose:
```
docker-compose build
```

### Запуск контейнера
Теперь можно запустить контейнер. В терминале это делается командой:
```
docker-compose up
```

### Об авторе
- [Заикин Алексей](https://github.com/AleksSpace "GitHub аккаунт")
