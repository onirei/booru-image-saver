import os, json, requests, math, time

#замер времени загрузки
def time_statistics(start):
    start_time = time.time()
    def wrapper(self):
        start(self)
        return print('Времени всего ' + str(int(round(((time.time() - start_time) / 60), 0)))
                     + ' min ' + str(round((time.time() - start_time) % 60, 2)) + ' sec')
    return wrapper

class Booru:

    #инициализация атрибутов
    def __init__(self):
        self.__path = str
        self.__tags = str
        self.booru_select = str
        self.__url_api = str


    #геттер пути
    @property
    def path(self):
        return self.__path


    #сеттер пути
    @path.setter
    def path(self, path=r''):
        self.__path = path


    #геттер тэгов
    @property
    def tags(self):
        return self.__tags


    #сеттер тэгов
    @tags.setter
    def tags(self, tags=''):
        self.__tags = tags


    #очистка тэгов, также сборщик мусора (жисона и папки с повторами если она пустая)
    @tags.deleter
    def tags(self):
        if os.path.isfile('data.json'):
            os.remove('data.json')
        if bool(os.listdir(str(self.__path)+r'\repetition')) is False:
            os.rmdir(str(self.__path)+r'\repetition')
        if bool(os.listdir(str(self.__path))) is False:
            os.rmdir(str(self.__path))
        del self.__tags


    #проверка директорий на существование
    def __check_dir(self):
        self.__path = self.__path+ '\\' + self.__tags
        if not os.path.exists(self.__path):
            os.makedirs(self.__path)
        if not os.path.exists(self.__path + r'\repetition'):
            os.makedirs(self.__path + r'\repetition')


    #проверка соединения, если есть то вернут ьпрокси False, если нет доступа, то вернуть параметр прокси
    @staticmethod #допилить обновление прокси, иногда отваливаются, лучше через апи получать актуальные прокси
    def __connection_check(url, params, proxy=False):
        proxies = {
            'http': 'http://134.209.108.243:8080',
            'https': 'https://134.209.108.243:8080',
        }
        print('Connect...')
        try:
            r = requests.get(url, params=params)
        except requests.ConnectionError:
            print('''Connection ERROR Try connect with PROXY SERVER''')
            try:
                r = requests.get(url, params=params, proxies=proxies)
            except requests.ConnectionError:
                print('Connection ERROR with PROXY SERVER')
                exit()
            else:
                if str(r) == '<Response [200]>':
                    print('Connection OK\n')
                proxy = proxies
        else:
            if str(r) == '<Response [200]>':
                print('Connection OK\n')
        return proxy


    #запись полученных данных в жисон
    @staticmethod
    def __write_json(data):
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=2, ensure_ascii=True)


    #скачивать по ссылке, с проверкой на то, что уже существует такой файл перед загрузкой
    @staticmethod
    def __download(url, path):
        #имя файла получаем из ссылки на него
        filename = url.split('/')[-1]
        r = requests.get(url, stream=True)
        if os.path.isfile(path + r'/' + filename):
            # filename = str(filename.rsplit('.', 1)[0]) + 'copy' + '.' + str(filename.rsplit('.', 1)[1])
            # путь сохранения
            with open(os.path.join(path + r'\repetition', filename), 'bw') as file:
                for chunk in r.iter_content(2048):
                    file.write(chunk)
        else:
            # путь сохранения
            with open(os.path.join(path, filename), 'bw') as file:
                for chunk in r.iter_content(2048):
                    file.write(chunk)


    #на базе API Gelbooru
    def __gelbooru(self):
        # проверка соединения
        proxy = self.__connection_check(self.__url_api, {'page': 'dapi', 's': 'post', 'q': 'index', 'limit': 0})
        # определение кол-ва элементов из запроса
        quantity = requests.get(self.__url_api,
                           params={'page': 'dapi', 's': 'post', 'q': 'index', 'tags': self.__tags, 'limit': 0, 'pid': 0,
                                   'json': 0}, proxies=proxy)
        #получаем числовое значение
        quantity = quantity.text.split('"')
        print(str(quantity[5]) + ' файлов к загрузке')
        #узнаём кол-во страниц на которые будем перебирать
        qt = int(math.ceil(int(quantity[5]) / 100))
        #переопределяем на инкремент кол-во скачанных файлов
        quantity = 0
        #открываем джисон для записи
        open('data.json', 'w')
        #цикл перебора постраницам доски
        for page_id in range(qt):
            #запрос к апи с параметрами страницы
            r = requests.get(self.__url_api,
                             params={'page': 'dapi', 's': 'post', 'q': 'index', 'tags': self.__tags,
                                     'limit': 100, 'pid': page_id, 'json': 1}, proxies=proxy)
            #запись в жисон
            self.__write_json(r.json())
            #открывает список для загрузки
            photos = json.load(open('data.json'))
            #перебираем все линки на файлы
            for photo in photos:
                #выводит ссылку на файл
                print(photo['file_url'])
                #скачиваем файл по ссылке
                self.__download(photo['file_url'], self.__path)
                #инкремент кол-ва скачанных файлов
                quantity += 1
        #вывод кол-ва скачанных файлов
        print('Файлов скачано: ', quantity)
            # # определение конца
            # if (page_id + 1) == qt:
            #     print('\n\nКоличество файлов на доске ' + str(quantity[5]))


    #на базе API Danbooru
    def __danbooru(self):
        #начальные значения кол-фа файлов и страниа с которой будет происходить выборка
        page = 1
        quantity = 0
        #проверка соединения
        proxy = self.__connection_check(self.__url_api, {'page': 'dapi', 's': 'post', 'q': 'index', 'limit': 0})
        #открыть жисон для записи
        open('data.json', 'w')
        #цикл перебора страниц доски
        while True:
            #запрос к апи с параметром страницы
            r = requests.get('https://danbooru.donmai.us/posts.json',
                             params={'page': page, 'tags': self.__tags}, proxies=proxy)
            #проверяем вернул ли запрос нам что-то, если нет, значит картинки кончились
            if not bool(r.json()): break
            #запись в жисон
            self.__write_json(r.json())
            #открывает список для загрузки
            photos = json.load(open('data.json'))
            # print('\n', 'страница ', page, '\n')
            #перебираем все линки на файлы
            for photo in photos:
                #выводит ссылку на фвйл
                print(photo['file_url'])
                #скачиваем по ссылке
                self.__download(photo['file_url'], self.__path)
                #инкремент кол-ва скачанных файлов
                quantity += 1
            #перелистываем страницу
            page += 1
        #кол-во скачанных файлов
        print('Файлов скачано: ', quantity)


    #запуск методов для определённой доски
    @time_statistics #декоратор для получения затраченного времени на выполнение поиска и загрузки файлов
    def start(self):
        if self.booru_select == 'gelbooru':
            self.__url_api = 'https://gelbooru.com/index.php'
            self.__path += '/gelbooru'
            self.__check_dir()
            self.__gelbooru()
        elif self.booru_select == 'danbooru':
            self.__url_api = 'https://danbooru.donmai.us/posts.json'
            self.__path += '/danbooru'
            self.__check_dir()
            self.__danbooru()
        else:
            return print('error')


def main():
    #дефолтный путь для скачивания файлов, используется только при повторном использовании скрипта
    default_path = ''
    #получаем экземпляр класса
    booru = Booru()
    #цикл ввода параметров
    while True:
        #выбираем доску, при повторном вызове будет иметь значение поумолчанию
        print('Gelbooru or Danbooru?')
        if booru.booru_select is str: #при первом вызове
            booru.booru_select = str.lower(input('> '))
        else: #при втором и далее вызовых
            buffer = input('Использовать '+str(booru.booru_select)+' снова?')
            if buffer is not '':
                booru.path = buffer
        #выбираем путь для загрузки
        if booru.path is str: #при первом вызове
            booru.path = input('Path: ')
            default_path = booru.path
        else: #при втором и далее вызовых
            buffer = input('Использовать '+str(default_path)+' снова?')
            if buffer is '':
                booru.path = default_path
            else:
                booru.path = buffer
        #вводим тэги для поиска на доске
        booru.tags = input('Tags: ')
        #запуск
        booru.start()
        #очистка атрибута тэги
        del booru.tags
        #повторый запуск или выход из скрипта
        if str.lower(input('Exit?')) == 'exit':
            del booru
            raise SystemExit

if __name__ == '__main__':
    main()