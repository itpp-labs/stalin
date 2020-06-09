# Памятка редакторам

## Работа со справками
* Откройте страницу персонажа на сайте
* Удерживая кнопку Ctrl дважды кликните по имени персонажа
* Появится кнопка "редактировать\добавить"
* После нажатия данной кнопки вы будете перенаправленны на соответсвующий файл в папке [hugo/data/spravki](hugo/data/spravki)
* Вам нужно будет залогиниться на сайте github.com, отредактировать файл, создать "пул-реквест"
* Далее кто-то должен одобрить и принять "пул-реквест". Подробнее можно узнать у администратора.
* После принятия пул-реквеста, обновления будут доступны на сайте либо автоматически, либо после обновления сайта администратором


## Редактирование раздела "О проекта"

Текст данного раздела хранится в файле [hugo/content/about.md](hugo/content/about.md). Используется формат *markdown*. Для обновления раздела, пришлите новую версию файла адмниистратору

## Редактирование главной страницы
TODO: check this section

* Текст главной страницы хранится в файле [hugo/content/index.md](hugo/content/index.md). Используется формат *markdown*. Для обновления раздела, пришлите новую версию файла адмниистратору
* В случае необходимости изменить структуру главной страницы, необходимо обновить шаблон страницы [hugo/layout/index.html](hugo/layout/index.html). По данному вопросу нужно обратиться к программисту


# Техническая часть

## Подготовка

* Clone repo to your machine

      git clone --recursive <URL>

* Install hugo:

      cd /tmp
      wget https://github.com/gohugoio/hugo/releases/download/v0.71.1/hugo_0.71.1_Linux-64bit.deb
      sudo dpkg -i hugo*.deb
## Памятка администраторам

* To compile website after changes in ``data``, ``data2hugo`` folders run the following command:

      make hugo

  -- it will make updates in ``hugo`` folder
* To compile website after changes in ``hugo`` (including ``hugo/data/spravki``) folder run the following command:

      make website

  -- it will generate website in ``hugo/public/`` folder
  
* It's recommended to automate CI/CD process. Check [GIthub Actions scripts](.github/workflows/) for examples.
## Памятка программистам

### To preview updates

      cd hugo
      hugo server -D

### To update content

* check scripts ``data2hugo``
* make updates
* preview updates with `make hugo` command
* send pull request to this repo


### To update theme

* check folder ``hugo/themes/``
* copy files you want to modify to `hugo/` folder
* make updates
* preview updates
* make git commit
* send pull request to this repo

# Добавление списков

В случае обнаружения в архивных документах недостающих списков, данные нужно будет вносить в следующих файла и папках

* База данных диска: [csv-файлы](data/db/tables)
* Фотографии документов: [hugo/static/disk/pictures](hugo/static/disk/pictures)
* Расшифровки справок [data/disk/vkvs/z3/spravki](data/disk/vkvs/z3/spravki)
* Далее следует воспользоваться памяткой Администратора чтобы проверить результат
* Если страницы списка и персонажей созданы удачно, не забудьте обновить главную страницу

