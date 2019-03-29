from booru_image_saver import Booru

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