$(document).ready(function(){
    var searchPersons = true;
    $('#search_form .tabs li').on('click', function() {
        searchPersons = $(this).attr('id') == "search_persons";

        $(this).parent().find('li').removeClass('is-active');
        $(this).addClass('is-active');

        // TODO: disable unused fields
    });


    var searchTimer;
    function clear_search_timer(){
        if (!searchTimer)
            return;
        clearTimeout(searchTimer);
        searchTimer = null;
    }
    function start_search(){
        clear_search_timer();
        if (searchPersons)
            search_persons();
        else
            search_lists();
    }

    $("#search_form input").on("input propertychange paste", function(event){
        clear_search_timer();
        searchTimer = setTimeout(function(){
            start_search();
        }, 300);
    });
    $("#search_form input").on("keypress", function(event){
        if (event.keyCode == 13){
            start_search();
        }
    });
    function get_obj(key, value){
        var d = {};
        d[key] = value;
        return d;
    }
    function search_persons(){
        // See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
        var query_bool = {
            "must": [],
            "should": []
        };
        $.each($("#search_form").serializeArray(), function(){
            var key = this.name;
            var value = this.value;
            if (!value)
                return;
            if (["firstname", "midname", "lastname"].indexOf(key) != -1) {
                query_bool.must.push({
                    "match": get_obj(key, value)
                });
            } else if (["underlined", "striked", "pometa"].indexOf(key) != -1) {
                    query_bool.must.push({
                        "match": get_obj(key, true)
                    });
            } else if (key == "global_search") {
                $.each(["firstname", "midname", "lastname"], function(){
                    query_bool.should.push({
                        "match": get_obj(this, value)
                    });
                });
                $.each(["spravka", "gb_spravka"], function(){
                    query_bool.should.push({
                        "match_phrase": get_obj(this, value)
                    });
                });
            }
        });

        search("persons", query_bool).done(function( data ) {
            render_persons(data.hits.hits);

        }).fail(function( data ) {
            console.log("Error", data);
            if (data){
                error_on_search(data);
            }else {
                empty_results();
            }
        });
    }

    function search_lists(){
        // See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
        var query_bool = {
            "must": [],
            "should": []
        };
        var date_range = {};
        $.each($("#search_form").serializeArray(), function(){
            var key = this.name;
            var value = this.value;
            if (!value)
                return;
            if (["date_from", "date_to"].indexOf(key) != -1) {
                var date = value.split(".");
                if (date.length != 3)
                    return;
                date = "{0}-{1}-{2}".format(
                    date[2],
                    date[1],
                    date[0]
                );
                if (key == "date_from")
                    date_range.gte = date;
                else
                    date_range.lte = date;
            } else if (["signstalin", "signmolotov", "signjdanov", "signkaganovic", "signvoroshilov", "signmikoyan", "signejov", "signkosior"].indexOf(key) != -1) {
                query_bool.must.push({
                    "match": get_obj(key, true)
                });
            }
        });
        if (! $.isEmptyObject(date_range)){
            query_bool.must.push({
                "range": {
                    "date": date_range
                }
            });
        }

        search("lists", query_bool).done(function( data ) {
            render_lists(data.hits.hits);

        }).fail(function( data ) {
            console.log("Error", data);
            if (!data){
                clear_results();
            }
        });
    }

    function search(index_name, query_bool){
        if (!query_bool.should.length){
            delete query_bool.should;
        } else {
            query_bool.minimum_should_match = 1;
        }
        if (!query_bool.must.length){
            delete query_bool.must;
        }
        if ($.isEmptyObject(query_bool)){
            // empty request
            var d = $.Deferred();
            d.reject();
            return d.promise();
        }

        var data = {
            "query": {
                "bool": query_bool
            }
        };
        if (index_name == "persons"){
            data.size = 20; // TODO: make pagination
        } else {
            data.size = 1000;
        }


        // TODO: don't load unused fields
        return $.ajax({
            method: "POST",
            url: ES_URL + index_name + "/_search?pretty=true",
            crossDomain: true,
            data: JSON.stringify(data),
            dataType : 'json',
            contentType: 'application/json',
        });
    }

    function render_persons(records){
        $("#results").empty();

        $.each(records, function(){
            var spravka = this._source.spravka_preview || "";
            if (spravka){
                spravka += "<br/>";
            }
            var fond7 = this._source.fond7 || "";
            if (fond7){
                fond7 = "По данным 7-го фонда ЦА ФСБ: {0}<br/>".format(fond7);
            }
            var gb_spravka_link = "";
            if (this._source.gb_spravka_preview){
                gb_spravka_link = '<a href="/persons/{0}#gb">GB</a><br/>'.format(this._id);
            }
            var spiski_data = JSON.parse(this._source.lists);
            var spiski = "";
            $.each(spiski_data, function(){
                spiski += '* <a href="{0}">{1}</a><br/>'.format(
                    this.url,
                    this.title,
                );
            });
            $("#results").append(
                '<p class="mt-3"><a href="/persons/{0}">{1}</a><br/>{2}{3}{4}{5}</p>'.format(
                    this._id,
                    this._source.nameshow,
                    spravka,
                    fond7,
                    gb_spravka_link,
                    spiski,
                ));
        });
    }

    function render_lists(records){
        $("#results").empty();

        $.each(records, function(){
            $("#results").append(
                '<p class="mt-3">{0} <a href="/lists/{1}">{2}</a></p>'.format(
                    this._source.date,
                    this._id,
                    this._source.title
                ));
        });
    }
    function clear_results(){
        $("#results").empty();
    }
    function empty_results(){
        $("#results").html("<h1>Ничего не найдено. Уточните запрос</h1>")
    }
    function error_on_search(data){
        $("#results").html("<h1>Ошибка сервера: {0}".format(data))
    }

    // credits: https://stackoverflow.com/questions/610406/javascript-equivalent-to-printf-string-format
    if (!String.prototype.format) {
        String.prototype.format = function() {
            var args = arguments;
            return this.replace(/{(\d+)}/g, function(match, number) {
                return typeof args[number] != 'undefined'
                    ? args[number]
                    : match
                ;
            });
        };
    }

    // data/db/tables/korpusa.csv
    var KORPUSA = {
        "1": {
            "name": "Основной корпус",
            "toms": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        },
        "2": {
            "name": "Списки января 1940 года",
            "toms": ["12"]
        },
        "3": {
            "name": "Списки сентября 1940 года",
            "toms": ["13", "14"]
        },
        "4": {
            "name": "Списки 1942 года",
            "toms": ["15"]
        },
        "5": {
            "name": "Списки 1950 года",
            "toms": ["16"]
        }
    };

    // data/db/tables/groups.csv
    var GROUPS = {
        "1": "Бывшие сотрудники НКВД",
        "2": "Иностранные подданные",
        "3": "Военные",
        "4": "Жены врагов народа",
        "5": "Брандлеровцы",
        "6": "Децисты",
        "7": "Меньшевики",
        "8": "Правые",
        "9": "Троцкисты",
        "10": "Эсеры",
        "11": "Группа Гофман-Леова",
        "12": "Военные округа",
        "13": "Железные дороги и ДТО",
        "14": "ГУЛАГ НКВД",
        "15": "Члены и кандидаты ЦК",
        "16": "Члены КПК и КСК",
        "17": "Секретари обкомов",
        "18": "Наркомы",
        "19": "Работники наркоматов"
    };
    // data/db/tables/geogr.csv
    // first line is ignored "1","1","1","СССР"
    var GEO = {
        "2":"Азербайджанская ССР",
        "3":"Армянская ССР",
        "4":"Белорусская ССР",
        "5":"Грузинская ССР",
        "6":"Казахская ССР",
        "7":"mdash; Актюбинская область",
        "8":"mdash; Алма-Атинская область",
        "9":"mdash; Восточно-Казахстанская область",
        "10":"mdash; Гурьевская область",
        "11":"mdash; Западно-Казахстанская область",
        "12":"mdash; Карагандинская область",
        "13":"mdash; Кустанайская область",
        "14":"mdash; Северо-Казахстанская область",
        "15":"mdash; Южно-Казахстанская область",
        "16":"Киргизская ССР",
        "17":"РСФСР",
        "18":"mdash; Азово-Черноморский край",
        "19":"mdash; Алтайский край",
        "20":"mdash; Амурская область",
        "21":"mdash; Архангельская область",
        "22":"mdash; Башкирская АССР",
        "23":"mdash; Бурято-Монгольская АССР",
        "24":"mdash; Вологодская область",
        "25":"mdash; Воронежская область",
        "26":"mdash; Восточно-Сибирская область",
        "27":"mdash; Горьковская область",
        "28":"mdash; Дагестанская АССР",
        "29":"mdash; Дальне-Восточный край",
        "30":"mdash; Западная область",
        "31":"mdash; Западно-Сибирский край",
        "32":"mdash; Ивановская область",
        "33":"mdash; Иркутская область",
        "34":"mdash; Кабардино-Балкарская АССР",
        "35":"mdash; Калининская область",
        "36":"mdash; Калмыцкая АССР",
        "37":"mdash; Камчатская область",
        "38":"mdash; Карельская АССР",
        "39":"mdash; Кировская область",
        "40":"mdash; Коми АССР",
        "41":"mdash; Краснодарский край",
        "42":"mdash; Красноярский край",
        "43":"mdash; Крымская АССР",
        "44":"mdash; Куйбышевская область",
        "45":"mdash; Курская область",
        "46":"mdash; Ленинградская область",
        "47":"mdash; Марийская АССР",
        "48":"mdash; Мордовская АССР",
        "49":"mdash; Московская область",
        "50":"mdash; Новосибирская область",
        "51":"mdash; Омская область",
        "52":"mdash; Орджоникидзевский край",
        "53":"mdash; Оренбургская область",
        "54":"mdash; Орловская область",
        "55":"mdash; Ростовская область",
        "56":"mdash; Рязанская область",
        "57":"mdash; Саратовская область",
        "58":"mdash; Свердловская область",
        "59":"mdash; Северная область",
        "60":"mdash; Северо-Осетинская АССР",
        "61":"mdash; Смоленская область",
        "62":"mdash; Сталинградская область",
        "63":"mdash; Тамбовская область",
        "64":"mdash; Татарская АССР",
        "65":"mdash; Томская область",
        "66":"mdash; Тульская область",
        "67":"mdash; Хабаровский край",
        "68":"mdash; Челябинская область",
        "69":"mdash; Чечено-Ингушская АССР",
        "70":"mdash; Читинская область",
        "71":"mdash; Ярославская область",
        "72":"Таджикская ССР",
        "73":"Туркменская ССР",
        "74":"Узбекская ССР",
        "75":"Украинская ССР",
        "76":"mdash; Винницкая область",
        "77":"mdash; Днепропетровская область",
        "78":"mdash; Донецкая область",
        "79":"mdash; Житомирская область",
        "80":"mdash; Каменец-Подольская область",
        "81":"mdash; Киевская область",
        "82":"mdash; Молдавская АССР",
        "83":"mdash; Николаевская область",
        "84":"mdash; Одесская область",
        "85":"mdash; Полтавская область",
        "86":"mdash; Харьковская область",
        "87":"mdash; Черниговская область"
    };

    // copy of data2hugo/geosub.json generated by data2hugo/titles2geosub.py

});
