import json

def make_json(vacancy_list_json, file_output_name):
    with open(file_output_name, "w", encoding="utf-8", newline="") as fjson:
        json.dump(vacancy_list_json, fjson, ensure_ascii=False, indent=2)

    print(f'Файл {file_output_name} сохранён в корневом каталоге.')

if __name__ == '__main__':
    pass