# Памятка редакторам

## Работа со справками

### Штучное обновление

Штучное обновление было изначально запланировано и реализовано, но потом было принято решение от него отказаться для избежания конфликтов с пакетным обновлением справок. Тем не менее, описанный ниже процесс можно использовать для накопления штучных изменений с целью последующего переноса этих изменений в общий csv-файл.

* Откройте страницу персонажа на сайте
* Удерживая кнопку Ctrl дважды кликните по имени персонажа
* Появится кнопка "редактировать\добавить"
* После нажатия данной кнопки вы будете перенаправленны на соответствующий файл в папке [hugo/data/spravki](hugo/data/spravki)
* Вам нужно будет залогиниться на сайте github.com, отредактировать файл, **создать "пул-реквест"**
<!-- Шаги для схемы когда штучное обновление не поддерживается -->
* Пул-реквест используется только как место для проверки и обсуждения изменения, а также для учета внесенных изменений. **Не нажимать кнопку Merge!**
* Изменения в пул-реквесте нужно вручную перенести в общий csv-файл (см. раздел "Обновление пачкой"). После этого можно закрыть пул-реквест

<!--
Следующие два шага не применимы к текущей схеме обновления, но оставлены на случай изменения схемы в будущем.

* НЕ ИСПОЛЬЗОВАТЬ. Далее кто-то должен одобрить и принять "пул-реквест". Подробнее можно узнать у администратора.
* НЕ ИСПОЛЬЗОВАТЬ. После принятия пул-реквеста, обновления будут доступны на сайте либо автоматически, либо после обновления сайта администратором
-->

### Обновление пачкой

Замечание: пачка может состоять из обновления одной справки; обновление пачкой это единственный способ обновить/добавить справки.

Для обновления справок нужно:

* скачать последнюю версию файла [data/spravki/all.csv](data/spravki/all.csv)
* внести необходимые справки
* передать новую версию файла администратору

Формат файла:

* разделитель это точка с запятой ``;``
* в теле справки для перевода строки используется знак ``#``
* кодировка файла: utf-8

  * если есть необходимость работать с обычной кодировкой (cp1251), обратитесь к
    админстратору для изменения кодировки

Администратор:

* если файл предоставлен в кодировки cp1215 его нужно сначала конвертнуть в utf:

      iconv -f cp1251 all-cp1251.csv > all.csv

* замените файл [data/spravki/all.csv](data/spravki/all.csv) на новую версию 
* проверьте изменения

      git diff

* сделайте комит
* сделайте пул-реквест
* после вливания пул-реквеста, гитхаб автоматически обновит сборку
* далее следуйте инструкциям по обновлению сайта (в частности, инструкция по обновлению сайта после изменений в папке hugo/ -- см ниже "Памятка Администраторам") и по обновлению индекса (раздел "Elasticsearch")

## Редактирование раздела "О проекта"

Текст данного раздела хранится в файле [hugo/content/about/index.md](hugo/content/about/index.md). Это копия оригинального сайта. Используется формат *html*. При редактировании можно использовать формат *markdown*. Для обновления раздела, пришлите новую версию файла адмниистратору

## Редактирование главной страницы

* Дополнительный текст главной страницы (т.е. помимо перечня списков) хранится в файле [hugo/content/_index.md](hugo/content/_index.md). Используется формат *markdown*. Для обновления раздела, пришлите новую версию файла адмниистратору
* В случае необходимости изменить структуру главной страницы, необходимо обновить шаблон страницы [hugo/layout/index.html](hugo/layout/index.html). По данному вопросу нужно обратиться к программисту


# Техническая часть

## Подготовка

* Clone repo to your machine

      git clone --recursive <URL>

* Install hugo:

      cd /tmp
      wget https://github.com/gohugoio/hugo/releases/download/v0.71.1/hugo_0.71.1_Linux-64bit.deb
      sudo dpkg -i hugo*.deb

* Install python packages

      sudo pip3 install oyaml

* Get and run Elasticsearch
  
      docker run -d \
      --name=elasticsearch \
      -p 127.0.0.1:9200:9200 \
      -p 127.0.0.1:9300:9300 \
      -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
      -e "discovery.type=single-node" \
      -e "http.cors.enabled=true" \
      -e "http.cors.allow-origin=*" \
      docker.elastic.co/elasticsearch/elasticsearch:7.7.1

  * After starting docker, you may need some time before elasticsearch is initialized
  * Under ES_JAVA_OPTS memory heap is set to 1GB. For more information about it, see https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html
  * For CORS settings check docs: https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-http.html
  * For other installation options see https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
  * Elasticsearch is available from localhost only. You need to configure web server (e.g. Nginx) to pass `/persons/_search` and `/lists/_search` search requests to elasticsearch, for example:
  
        upstream upstream_static {
           server 185.199.109.153;
        }
        upstream upstream_elasticsearch {
           server localhost:9200;
        }
        server {
               listen 80;
               location ~ /(persons|lists)/_search {
                    proxy_set_header Host $host;
                    proxy_pass http://upstream_elasticsearch;
        
                    auth_basic           "Administrator’s Area";
                    auth_basic_user_file /etc/apache2/.htpasswd; 
        
               }
               location / {
                    proxy_set_header Host $host;
                    proxy_pass http://upstream_static;
        
                    auth_basic           "Administrator’s Area";
                    auth_basic_user_file /etc/apache2/.htpasswd; 
        
               }
        }



## Памятка администраторам

* Don't forget to configure [robots.txt](hugo/static/robots.txt)

* To compile website after changes in ``data``, ``data2hugo`` folders run the following command:

      make hugo

  -- it will make updates in ``hugo`` folder

* To compile website after changes in ``hugo`` (including ``hugo/data/spravki``) folder run the following command:

      make website

  -- it will generate website in ``hugo/public/`` folder.

  You may also need to check ``baseURL`` setting in [hugo/config.toml](hugo/config.toml)
  
* It's recommended to automate CI/CD process. Check [GIthub Actions scripts](.github/workflows/) for examples.

* It's recommended upload static pages first and then update search index.

      Лучше всего сначала обновить страницы сайта, а потом поиск, чтобы в течение
      промежутка вермени между этими обновлениями пользователь не оказался в
      ситуации, когда он нашел персону в поиске со справкой, перешел на
      страницу и не нашел полную версию справки.

## Памятка верстальщикам

В качестве css-фреймворка используется [bulma](https://bulma.io/documentation/)

## Памятка программистам

### To preview updates

      cd hugo
      hugo server --templateMetrics

To run hugo on remote server, you may need to add following arguments:

      hugo server --templateMetrics --bind="0.0.0.0" --baseURL=your-dev-server.example.com 

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

### Lists with special formating

* two columns (primzv)

  * /lists/list68
  * /lists/list410
  * /lists/list413 -- also, an example of a list with big amount of pages

* lists with gb spravka near the name

  * /lists/list409
  * /lists/list411
  * /lists/list412

### Pages with sperical formating

* title pages

  * /lists/list184/#image-211

* list spravka

  * /lists/list254/#image-33
  * /lists/list184/#image-212

## Elasticsearch

### Загрузка индексов

    # generate index files
    make search
    # upload index files to local Elasticsearch
    make upload_search

### Настройка адреса

See [hugo/config.toml](hugo/config.toml)

# Добавление списков

В случае обнаружения в архивных документах недостающих списков, информацию нужно будет вносить в следующих файла и папках

* База данных диска: [csv-файлы](data/db/tables)
* Фотографии документов: [hugo/static/disk/pictures](hugo/static/disk/pictures)
* Расшифровки справок [data/disk/vkvs/z3/spravki](data/disk/vkvs/z3/spravki)

Далее следует воспользоваться памяткой Администратора, чтобы проверить результат. Если страницы списка и персонажей созданы удачно, не забудьте обновить страницу с переченем списков.

