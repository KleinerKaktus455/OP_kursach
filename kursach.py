import json
from datetime import datetime
import copy
import re


def main():
    choice = menu()
    data = []
    while choice:
        if choice == 1:
            if data:
                print('Внимание! Вы пересоздать базу, не сохранив результаты работы.')
                choice = yes_no_inp('Старые данные будут удалены. Вы хотите продолжить?[Y/N] ')
            else:
                save_json({})
            if choice == 'y':
                save_json({})
        elif choice == 2:     # добавление записи
            add_data(data)
        elif choice == 3:   # удаление записи
            delete(data)
        elif choice == 4:   # редактирование записи
            edit(data)
        elif choice == 5:   # сортировка данных
            sort(data)
        elif choice == 6:   # загрузка данных из файла
            if data:
                print('Внимание! Вы пытаетесь загрузить данные из базы, не сохранив результаты работы.')
                choice = yes_no_inp('Старые данные будут удалены. Вы хотите продолжить?[Y/N] ')
            else:
                data = get_json_data()
            if choice == 'y':
                data = get_json_data()
        elif choice == 7:   # сохранение файла
            save_json(data)
        elif choice == 8:   # вывод таблицы
            output(data)
        elif choice == 9:   # поиск данных
            find(data)
        elif choice == 0:
            return
        else:
            print(f'Вы ввели несуществующий пункт меню ({choice}). Повторите попытку')
        choice = menu()



def menu():
    menu_list = ['Выход из программы','Пересоздание базы данных', 'Добавление записей', 'Удаление записи',
                 'Редактирование записи', 'Сортировка данных', 'Загрузка данных из базы данных',
                 'Сохранение файла', 'Вывод данных', 'Поиск записи по фамилии человека']
    menu_len = len(menu_list)
    print(f'\nВыберите желаемое действие:\n{"*"*20}' )
    for x in range(menu_len):
        print(f'{x}) {menu_list[x]}')
    print("*"*20)

    while True:
        try:
            choice = int(input())
        except ValueError:
            print('Ошибка! Вы ввели не число! Повторите попытку')
            continue
        if choice < 0 or choice > menu_len:
            num = ['маленькое', 'большое'][choice >= menu_len]
            print(f'Ошибка! Вы ввели слишком {num} число. Повторите попытку')
            continue
        else:
            break
    return choice


def output(data_list):
    try:
        if data_list:
            print('{:^20} | {:^20} | {:^20} | {:^20}'.format('Имя',
                                                              'Фамилия',
                                                              'Дата рождения',
                                                              'Знак зодиака'))
            print('-'* 89)

            for pers_dict in data_list:
                date = '{0}.{1}.{2}'.format(*pers_dict['Дата рождения'])

                print('{:^20} | {:^20} | {:^20} | {:^20}'.format(pers_dict['Имя'],
                                                                  pers_dict['Фамилия'],
                                                                  date,
                                                                  pers_dict['Знак зодиака']))

        else:
            print('Внимание! Вы не выгрузили данные из файла/база данных пуста')
    except Exception:
        print('Внимание! На вход функции поданы неверные данные')


def save_json(data_list):
    try:
        with open("database.json", "w", ) as write_file:  # данная функция
            # автоматически закрывает открытый файл; кодировка позволяет работать с русскими буквами
            json.dump(data_list, write_file, indent=4, ensure_ascii=False)
        print('Файл сохранен')
    except Exception:
        print('Внимание! Во время сохранения файла произошли непредвиденные ошибки')


def get_json_data():
    try:
        is_error = False
        data = []
        with open('database.json', 'r') as f:
            raw_data = json.load(f)
        N = len(raw_data)
        for i in range(N):
            pers_dict = raw_data[i]
            pers_dict['Имя'] = pers_dict['Имя'].strip().title()
            pers_dict['Фамилия'] = pers_dict['Фамилия'].strip().title()
            name = pers_dict['Имя'].title()
            if not name.isalpha():
                print(f'Внимание! В имени {name} присутствуют посторонние символы. Запись пропускается')
                is_error = True
                continue

            is_surname_ok = True
            surname = pers_dict['Фамилия'].title()
            for letter in surname:
                if not letter.isalpha():
                    if letter != '-' and letter != "'":
                        print(f'Внимание! В фамили {surname} присутствуют посторонние символы. Запись пропущена')
                        is_error = True
                        is_surname_ok = False
                        break
            if not is_surname_ok:
                continue

            date = pers_dict['Дата рождения']
            is_date_ok = True
            if isinstance(date, list) and len(date) == 3:
                for num in date:
                    if not str(num).isdigit():
                        print('Внимание! Дата ', end='')
                        print(*date, sep='.', end='')
                        print(' неверна. Запись пропускается')
                        is_error = True
                        is_date_ok = False
                        if not is_date_ok:

                            break
                if not is_date_ok:
                    continue

                if not is_date_valid(date):
                    print('Внимание! Дата ', end='')
                    print(*date, sep='.', end='')
                    print(' неверна. Запись пропускается')
                    is_error = True
                    continue

            else:
                print('Внимание! Дата ', end='')
                if isinstance(date, list):
                    print(*pers_dict["Дата рождения"], sep='.', end='')
                else:
                    print(pers_dict['Дата рождения'], end='')
                print(' неверна. Запись пропускается')
                is_error = True
                continue



            correct_zodiac = zodiac_sign(pers_dict['Дата рождения'])
            if correct_zodiac != pers_dict['Знак зодиака']:
                pers_dict['Знак зодиака'] = correct_zodiac
                print(f'Внимание! В следующей записи {name} {surname} был неверный знак зодиака. Данные исправлены')
                is_error = True

            if pers_dict not in data:
                data.append(pers_dict)
            else:
                print('Внимание! В файле присутствуют одинаковые записи. Копии пропущены')
        if is_error:
            save_json(data)

        print('Данные из файла успешно загружены в программу')
        return data
    except FileNotFoundError:
        print('Внимание! Файл базы данных отсутствует. Вы можете создать его при помощи соответствующего пункта меню')
    except Exception:
        print('Во время обработки файла произошли непредвиденные ошибки')


def delete(data_list):
    if data_list:
        indexes = find(data_list)
        if indexes == 'exit':
            return
        if len(indexes) == 1:
            data_list.pop(indexes[0])

            print('Удаление завершено')
            choice = yes_no_inp('Вы хотите сохранить измененную базу данных?[Y/N]')
            if choice == 'y':
                save_json(data_list)
            return
        elif len(indexes) > 1:
            while True:
                try:
                    choice = int(input('Введите номер записи, которую вы хотите удалить'))
                except ValueError:
                    print('Ошибка! Вы ввели не цифру! Повторите попытку')
                    continue
                if (choice < 1) or (choice > len(indexes)):
                    print('Вы ввели несуществующий индекс! Пожалуйста, перечитайте инструкцию и повторите ввод!')
                    continue
                else:
                    break
            try:
                data_list.pop(indexes[choice-1])
                print('Удаление завершено')

                choice = yes_no_inp('Вы хотите сохранить измененную базу данных?[Y/N]')
                if choice == 'y':
                    save_json(data_list)

            except Exception:
                print('Внимание! Во время удаления произошла непредвиденная ошибка. Данные не изменены')

    else:
        print('Внимание! Вы не выгрузили данные из файла/база данных пуста')


def find(data_list):
    try:
        if data_list:
            print('Для выхода в меню введите "exit"')
            surname = surname_input()
            if surname.lower() == 'exit':
                return 'exit'

            answer = []

            for person_dict in data_list:
                if surname in person_dict.values():
                    answer.append(data_list.index(person_dict))

            if answer:
                print('Найдены следующие записи:')
                i = 0

                print('{:^20} | {:^20} | {:^20} | {:^20} | {:^20}'.format( '№ результата','Имя',
                                                                 'Фамилия',
                                                                 'Дата рождения',
                                                                 'Знак зодиака'))
                print('-' * 109)

                for index in answer:
                    i += 1
                    pers_dict = data_list[index]

                    date = '{0}.{1}.{2}'.format(*pers_dict['Дата рождения'])

                    print('{:^20} | {:^20} | {:^20} | {:^20} | {:^20}'.format(i,
                                                                     pers_dict['Имя'],
                                                                     pers_dict['Фамилия'],
                                                                     date,
                                                                     pers_dict['Знак зодиака']))



            else:
                print('По вашему запросу ничего не найдено')

            return(answer)
        else:
            print('Внимание! Вы не выгрузили данные из файла/база данных пуста')
    except Exception:
        print('Внимание! На вход функции поданы неверные данные')


def sort(data_list):
    if data_list:
        while True:
            print('По какому значению будет производится сортировка? \n0) Вернуться в меню\n1) Имя\n'
                  '2) Фамилия\n3) Дата рождения\n4)Знак зодиака')
            try:
                choice = int(input())
            except ValueError:
                print('Вы ввели неверное значение')
                continue
            if choice >= 0 and choice <= 4:
                break
            else:
                print('Внимание! Вы ввели неверный параметр')

        if choice == 0:
            return

        while True:
            print('Каким образом должна быть произведена сортировка?\n0) По возврастанию\n1) По убыванию (алфавитный порядок)')
            try:
                is_reverse = bool(int(input()))
            except ValueError:
                print('Вы ввели неверное значение')
                continue
            if is_reverse == 0 or is_reverse == 1:
                break
            else:
                print('Внимание! Вы ввели неверный параметр')


        if choice == 1:
            choice = 'Имя'
        if choice == 2:
            choice = 'Фамилия'
        if choice == 3:
            choice = 'Дата рождения'
        if choice == 4:
            choice = 'Знак зодиака'

        if choice == 'Имя' or choice == 'Фамилия' or choice == 'Знак зодиака':
            print('Данные отсортированны')
            return data_list.sort(key=lambda man: man[choice].lower(), reverse=not(is_reverse))
        else:
            if choice == 'Дата рождения':
                N = len(data_list)
                for i in range(N - 1):
                    for j in range(N - i - 1):

                        str_j = str(data_list[j]["Дата рождения"][2])

                        if len(str(data_list[j]["Дата рождения"][1])) < 2:
                            str_j += '0' + str(data_list[j]["Дата рождения"][1])
                        else:
                            str_j += str(data_list[j]["Дата рождения"][1])

                        if len(str(data_list[j]["Дата рождения"][0])) < 2:
                            str_j += '0' + str(data_list[j]["Дата рождения"][0])
                        else:
                            str_j += str(data_list[j]["Дата рождения"][0])

                        str_j1 = str(data_list[j+1]["Дата рождения"][2])

                        if len(str(data_list[j+1]["Дата рождения"][1])) < 2:
                            str_j1 += '0' + str(data_list[j+1]["Дата рождения"][1])
                        else:
                            str_j1 += str(data_list[j+1]["Дата рождения"][1])

                        if len(str(data_list[j+1]["Дата рождения"][0])) < 2:
                            str_j1 += '0' + str(data_list[j+1]["Дата рождения"][0])
                        else:
                            str_j1 += str(data_list[j+1]["Дата рождения"][0])

                        if is_reverse == True: # чем больше число, тем человек младше
                            if int(str_j) > int(str_j1):
                                data_list[j], data_list[j + 1] = data_list[j + 1], data_list[j]
                        else:
                            if int(str_j) < int(str_j1): # чем меньше число, тем человек младше
                                data_list[j], data_list[j + 1] = data_list[j + 1], data_list[j]
                print('Данные отсортированны')

                return data_list


    else:
        print('Внимание! Вы не выгрузили данные из файла/база данных пуста')


def edit(data_list):
    try:
        if data_list:
            indexes = find(data_list)
            if indexes == 'exit':
                return

            if indexes:
                if len(indexes) == 1:
                    index = indexes[0]
                elif len(indexes) > 1:
                    while True:
                        try:
                            choice = int(input('Введите номер записи, которую вы хотите отредактировать: '))
                        except ValueError:
                            print('Ошибка! Вы ввели не цифру! Повторите попытку')
                            continue
                        if (choice < 1) or (choice > len(indexes)):
                            print('Вы ввели несуществующий ответ! Пожалуйста, перечитайте инструкцию и повторите ввод!')
                            continue
                        else:
                            index = indexes[choice-1]
                            break

                while True:
                    try:
                        choice2 = int(input('Выберите поле, которое вы хотите отредактировать:'
                                        '\n1)Имя, \n2)Фамилия, \n3) Дата рождения\n '))

                    except ValueError:
                        print('Ошибка! Вы ввели не цифру! Повторите попытку')

                    if (choice2 > 3) or (choice2 < 1):
                        print('Внимание, вы ввели неверное число! Повторите попытку')
                        continue
                    else:
                        break

                new_data = copy.deepcopy(data_list[index])
                print('Для возвращения в меню введите "exit" вместо значения редактируемого поля')
                if choice2 == 1:
                    name = name_input()
                    if name == 'exit':
                        return
                    else:
                        new_data['Имя'] = name
                elif choice2 == 2:
                    surname = surname_input()
                    if surname == 'exit':
                        return
                    else:
                        new_data['Фамилия'] = surname

                elif choice2 == 3:
                    date = date_input()
                    if date == 'exit':
                        return
                    else:
                        new_data['Дата рождения'] = date

                    correct_zodiac = zodiac_sign(new_data['Дата рождения'])
                    if correct_zodiac != new_data['Знак зодиака']:
                        new_data['Знак зодиака'] = correct_zodiac

                if new_data in data_list:
                    print('Внимание! Данная запись уже существует в базе данных. Внесенные изменения не сохраняются')
                    return
                else:
                    data_list[index] = new_data

                choice = yes_no_inp('Вы хотите сохранить измененную базу данных?[Y/N]')
                if choice == 'y':
                    save_json(data_list)
            else:
                print('Внимание! Указанная фамилия не найдена')
        else:
            print('Внимание! Вы не выгрузили данные из файла/база данных пуста')

    except Exception:
        print('Внимание! На вход функции были поданы неверные данные')


def zodiac_sign(date):
    if len(date) == 3 and isinstance(date, list):

        zodiacs = [(201, 'Козерог'), (218, 'Водолей'), (320, 'Рыбы'), (420, 'Овен'), (521, 'Телец'),
                   (621, 'Близнецы'), (722, 'Рак'), (823, 'Лев'), (923, 'Дева'), (1023, 'Весы'),
                   (1122, 'Скоропион'), (1222, 'Стрелец'), (1231, 'Козерог')]
        date_str = [str(date[x]) for x in [1, 0]]
        if len(date_str[0]) < 2:
            date_str[0] = '0'+ date_str[0]
        date_number = int("".join(date_str))    # создание числа, выглядещее как ДеньМесяц
        for z in zodiacs:
            if date_number <= z[0]:
                return z[1]
    else:
        print('На вход функции поданы неверные данные')


def add_data(data_list):
    if isinstance(data_list, list):
        choice = ''

        if not data_list:
            choice_newbase = yes_no_inp('Внимание! Вы, скорее всего, не выгрузили данные из файла либо создаете новую базу данных.\n'
                              'При первом варианте база данных будет перезаписана. Вы хотите продолжить?[Y/N] ')
            if choice_newbase == 'n':
                return
        print('Введенные данные будут автоматичеси сохранены в файл.')

        while choice != 'n':
            new_data = data_input()
            if new_data in data_list:
                print('Внимание! Вы ввели существующую запись. Сохранение не производитя')
            else:
                if new_data == 'exit':
                    print('Ввод данных остановлен. Данная запись не сохраняется')
                else:
                    data_list.append(new_data)
            choice = yes_no_inp('Вы хотите добавить еще одну запись в базу данных?[Y/N] ')
        save_json(data_list)
    else:
        print('На вход функции поданы неверные данные')


def is_date_valid(date_list):
    m_length = [31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30]
    cur_year = datetime.now().year
    try:
        day = date_list[0]
        month = date_list[1]
        year = date_list[2]
        if (month != 2):
            if ((month <= 0) or (month > 12) or (year <= 0) or (day > m_length[month % 12])
                    or (day <= 0) or (year > cur_year) or (year < 1000)):
                answer = False
            else:
                answer = True

        else:
            if ((year % 4 != 0) or ((year % 100 == 0) and (year % 400 != 0))):
                if ((month <= 0) or (month > 12) or (year <= 0) or (day > m_length[2]) or (day <= 0)
                        or (year > cur_year) or (year < 1000)):
                    answer = False
                else:
                    answer = True
            else:
                if ((month <= 0) or (month > 12) or (year <= 0) or (day > 29) or (day <= 0)
                        or (year > cur_year) or (year < 1000)):
                    answer = False
                else:
                    answer = True

        if (answer == -1) or len(date_list) > 3:
            print('Внимание! На вход функции поступили неверные входные данные!')
        return answer

    except Exception:
        print('Внимание! На вход функции поступили неверные входные данные!')


def yes_no_inp(question):
    while True:
        try:
            choice = str(
                input(question)).lower().strip()  # проверка на choice
        except ValueError:
            print('Ошибка! Вы ввели не буквы! Повторите попытку')
            continue
        if choice != 'y' and choice != 'n':
            print('Вы ввели несуществующий ответ! Пожалуйста, перечитайте инструкцию и повторите ввод!')
            continue
        else:
            break
    return choice


def data_input():
    new_data = {}
    print('Для выхода в меню введите "exit"')
    new_data['Имя'] = name_input()
    if new_data['Имя'].lower() == 'exit':
        return 'exit'
    new_data['Фамилия'] = surname_input()
    if new_data['Фамилия'].lower() == 'exit':
        return 'exit'
    new_data['Дата рождения'] = date_input()
    if new_data['Дата рождения'] == 'exit':
        return 'exit'
    new_data['Знак зодиака'] = zodiac_sign(new_data['Дата рождения'])

    return new_data


def date_input():
    date_template = r'\d{2}\.\d{2}\.\d{4}'
    while True:
        data_str = str(input('Введите дату в формате ДД.ММ.ГГГГ: ')).strip()
        if data_str.lower() == 'exit':
            return 'exit'
        if re.match(date_template, data_str) is None:
            print('Вы ввели дату в неверном формате. Повторите попытку.')
            continue
        else:
            date = [int(x) for x in data_str.split('.')]
            if is_date_valid(date):
                break
            else:
                print('Вы ввели неверную дату.Повторите попытку')
                continue
    return date


def surname_input():

    while True:
        is_error = False
        surname = str(input(f'Введите фамилию: ')).title().strip()
        if surname.lower() == 'exit':
            return 'exit'
        for letter in surname:
            if not letter.isalpha():
                if letter != '-' and letter != "'":
                    print(f'Внимание! В фамилии присутствуют посторонние символы. '
                                        f'Введите корректную фамилию: ')
                    is_error = True
                    break
        if is_error:
            continue
        else:
            break

    return surname.title()


def name_input():
    name = str(input(f'Введите имя: ')).strip()
    if name.lower() == 'exit':
        return 'exit'
    name.title()
    while not name.isalpha():
        name = str(input(f'Внимание! В имени присутствуют посторонние символы. '
                                            f'Введите корректное имя: ')).strip()
        continue
    return name.title()


if __name__ == "__main__":  # точка входа в программу
    main()

