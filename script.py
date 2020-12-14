import json
import os
from typing import IO

from jsonschema.validators import Draft7Validator


def load_data_from_json(json_file: IO, log: list):
    """
    Возвращает данные из json файла.
    Проверяет формат файла (.json), и не пустой ли он.
    """
    try:
        data = json.load(json_file)
        if not data:
            log.append([
                file,
                'Представленный файл пуст, исправьте его'])
        return data
    except json.JSONDecodeError:
        log.append([
            file,
            'Представленный файл не формата JSON, исправьте его'])


def parse_event_field_from_data(data, log: list):
    """Возвращает значение поля event. Проверяет наличие поля event."""
    try:
        return data['event']
    except KeyError:
        log.append([
            file,
            'Поле event отсутствует, проверьте содержимое файла'])


def link_json_to_schema(event: str, log: list):
    """
    Возвращает schema к конкретному event.
    Если такой схемы нет, сообщает, что поле event некорректно.
    """
    try:
        with open(f'schema/{event}.schema', 'r') as schema:
            return json.load(schema)
    except FileNotFoundError:
        log.append([
            file,
            'Некорректро задано поле event, проверьте его содержимое'
        ])


def json_validation(data: dict, schema: dict, log: list):
    result_errors_list = []
    validator = Draft7Validator(schema)
    errors = validator.iter_errors(data['data'])
    for error in errors:
        if error.path:
            error_path = ' '.join(map(str, error.path))
            result_errors_list.append(
                f'{error.message}, обратите внимание на ключ {error_path}')
        else:
            result_errors_list.append(error.message)
    if result_errors_list:
        log.append([
            file,
            result_errors_list
        ])


log_data = []  # список [название файла, описание ошибки]
files = os.listdir('event')  # список с названиями всех json файлов в event/
for file in files:
    with open(f'event/{file}', 'r', encoding='utf-8') as json_file:
        data = load_data_from_json(json_file, log_data)
        if data:
            event = parse_event_field_from_data(data, log_data)
            if event:
                schema = link_json_to_schema(event, log_data)
                if schema:
                    json_validation(data, schema, log_data)

result = []
for i in log_data:
    if isinstance(i[1], list):
        convert_data = '; '.join(map(str, i[1]))
        del i[1]
        result.append([i[0], convert_data])
    else:
        result.append(i)

with open('log.txt', 'w', encoding='utf-8') as log_file:
    log_file.writelines("%s\n" % ': '.join(map(str, i)) for i in result)
