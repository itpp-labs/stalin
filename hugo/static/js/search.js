$(document).ready(function(){
    if (!$("#search_form").length){
        // we are not in search page
        return;
    }
    search_init();
    var cal_options = {
        "dateFormat": "d.m.Y",
        "disableMobile": true,
        "locale": "ru"
    };
    $("input[name='date_from']").flatpickr($.extend({
        "defaultDate": "27.02.1937",
    }, cal_options)).clear();
    $("input[name='date_to']").flatpickr($.extend({
        "defaultDate": "29.09.1938",
    }, cal_options)).clear();

    $("#nav-search-button").click(function(e){
        // prevent reloading page if user understand button as "Make Search"
        e.preventDefault();
    });

    // korpus, tom
    $("select[name='korpus'] option").not(":first").remove();
    $.each(KORPUSA, function(id, data){
        if (id == "0")
            return;
        $("select[name='korpus']").append(
            '<option value="{0}">{1}</option>'.format(id, data.name)
        );
    });
    function update_tom_options(korpus_id){
        var toms = KORPUSA[korpus_id].toms;
        var val = $("select[name='tom']").val();
        if (toms.indexOf(val) === -1)
            val = "0";
        $("select[name='tom'] option").not(":first").remove();
        $.each(toms, function(){
            $("select[name='tom']").append(
                '<option value="{0}">Том {0}</option>'.format(this)
            );
        });
        $("select[name='tom']").val(val);
    };
    update_tom_options("0");

    // geo, geosub, groups
    $("select[name='geo'] option").not(":first").remove();
    $.each(GEO, function(id, name){
        $("select[name='geo']").append(
            '<option value="{0}">{1}</option>'.format(id, name)
        );
    });
    $("select[name='group'] option").not(":first").remove();
    $.each(GROUPS, function(id, name){
        $("select[name='group']").append(
            '<option value="{0}">{1}</option>'.format(id, name)
        );
    });

    function update_geosub_options(geo_id){
        var geosubs = GEOSUB[geo_id] || {};
        $("select[name='geosub'] option").not(":first").remove();
        $.each(geosubs, function(geosub_id, title){
            $("select[name='geosub']").append(
                '<option value="{0}">{1}</option>'.format(geosub_id, title)
            );
        });
        if ($.isEmptyObject(geosubs)){
            $("select[name='geosub']").attr("disabled", "disabled");
        } else {
            $("select[name='geosub']").removeAttr("disabled")
        }
    };
    update_geosub_options("0");


    var searchPersons = true;
    var ALL_FIELDS;
    $('#search_form .tabs li').on('click', function() {
        if (!ALL_FIELDS){
            ALL_FIELDS = PERSON_FIELDS.concat(LIST_FIELDS);
            // https://stackoverflow.com/questions/9229645/remove-duplicate-values-from-js-array
            ALL_FIELDS.filter(function(item, pos) {
                return ALL_FIELDS.indexOf(item) === pos;
            });
        }

        var id = $(this).attr('id');
        if (id == "clear_form"){
            clear_results();
            $.each(ALL_FIELDS, function(){
                $elem = $("[name='{0}']".format(this));
                if ($elem.is("select")){
                    $elem.val("0");
                } else if ($elem.is(":checkbox")){
                    $elem.prop("checked", false);
                } else {
                    $elem.val("");
                }
            });
            return;
        }
        searchPersons = id == "search_persons";

        $(this).parent().find('li').removeClass('is-active');
        $(this).addClass('is-active');

        // disable unused fields
        var active_fields;
        if (searchPersons) {
            active_fields = PERSON_FIELDS;
        } else {
            active_fields = LIST_FIELDS;
        }
        $.each(ALL_FIELDS, function(i, name){
            $elem = $("[name='{0}']".format(name));
            if (active_fields.indexOf(name) !== -1){
                if (!$elem.is("select") || $elem.find("option").length > 1) {
                    $elem.removeAttr("disabled");
                    if ($elem.attr("type") === "checkbox"){
                        $elem.parent().removeAttr("disabled");
                    }
                }
            } else {
                $elem.attr("disabled", "disabled");
                if ($elem.attr("type") === "checkbox"){
                    $elem.parent().attr("disabled", "disabled");
                }
            }
        });
        make_search();

    });

    var searchTimer;
    function start_search_timer(){
        clear_search_timer();
        searchTimer = setTimeout(function(){
            make_search();
        }, 300);
    }
    function clear_search_timer(){
        if (!searchTimer)
            return;
        clearTimeout(searchTimer);
        searchTimer = null;
    }
    $("#more").on("click", function(event){
        // hide to avoid another click before data is loaded
        $(this).addClass("is-hidden");

        make_search(search_offset);
    });
    $("#search_form input").on("input", function(event){
        start_search_timer();
    });
    $("#search_form input").on("propertychange paste", function(event){
        make_search();
    });
    $("#search_form select").on("change", function(event){
        $elem = $(this);
        if ($elem.attr("name") == "korpus"){
            update_tom_options($elem.val());
        } else if ($elem.attr("name") == "geo"){
            update_geosub_options($elem.val());
        }
        make_search();
    });
    $("#search_form input").on("keypress", function(event){
        if (event.keyCode == 13){
            make_search();
        }
    });
    function get_obj(key, value){
        var d = {};
        d[key] = value;
        return d;
    }
    // Keep search results on using "Back", "Reload" buttons
    var search_state = {};
    function update_url(){
        var form_data = $("#search_form").serializeArray();
        search_state.form_data = form_data;
        var hash_url = "#" + $.param(form_data);
        history.pushState(search_state, "", hash_url);
    }
    var renders = {
        "render_persons": render_persons,
        "render_lists": render_lists,
        "render_stats": render_stats,
    };
    function restore_state(state){
        if (state.form_data){
            var checkboxes = {};
            $.each(CHECKBOX_FIELDS, function(index, value){
                checkboxes[value] = false;
            });
            for (var i = 0; i < state.form_data.length; i++) {
                var name = state.form_data[i].name;
                var value = state.form_data[i].value;
                if (CHECKBOX_FIELDS.indexOf(name) !== -1){
                    checkboxes[name] = value == "on";
                } else {
                    $("input[name='" + name + "'], select[name='" + name + "']").val(value);
                }
            }
            $.each(checkboxes, function(name, value){
                $("input[type='checkbox'][name='" + name + "']").prop("checked", value);
            });
        }
        $.each(["render_persons", "render_lists", "render_stats"], function(index, value){
            if (state[value]){
                renders[value].apply(null, state[value]);
            }
        });
    };
    window.addEventListener('popstate', function(event) {
        if (!event.state){
            return;
        }
        restore_state(event.state);
    });
    if (history.state){
        restore_state(history.state);
    } else if (location.hash){
        function parseParams(str) {
            return str.split('&').reduce(function (params, param) {
                var paramSplit = param.split('=').map(function (value) {
                    return decodeURIComponent(value.replace(/\+/g, ' '));
                });
                params.push({
                    "name": paramSplit[0],
                    "value": paramSplit[1]
                });
                return params;
            }, []);
        }
        try {
            var form_data = parseParams(location.hash.substr(1));
            restore_state({"form_data": form_data});
            make_search();
        } catch (error){
            console.log(error);
        }
    }

    // pagination is applied for persons only
    var SEARCH_SIZE_FIRST = 30;
    var SEARCH_SIZE = 1000;
    function make_search(offset){
        clear_search_timer();

        offset = offset || 0;
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
            if (["korpus", "tom", "geo", "geosub", "group", "kat"].indexOf(key) !== -1) {
                value = parseInt(value);
                if (!value)
                    return;
            }
            if (searchPersons && ["firstname", "midname", "lastname"].indexOf(key) !== -1) {
                if (value.indexOf("*") == -1){
                    query_bool.must.push({
                        "match_phrase": get_obj(key, value)
                    });
                } else {
                    // see https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-wildcard-query.html
                    query_bool.must.push({
                        "wildcard": get_obj(key, {
                            "value": value,
                        })
                    });
                }
            } else if (["underlined", "striked", "pometa"].indexOf(key) !== -1) {
                if (!searchPersons){
                    key = "has_" + key;
                }
                query_bool.must.push({
                    "term": get_obj(key, {"value": true})
                });
            } else if (key == "korpus") {
                if ($("select[name='tom']").val() === "0"){
                    // korpus is specified, but tom is not
                    var toms = $.map(KORPUSA[value.toString()].toms, function(t){
                        return parseInt(t);
                    });
                    query_bool.must.push({
                        "terms": {
                            "tom": toms
                        }
                    });
                }
            } else if (searchPersons && ["tom", "geo", "geosub", "group", "kat"].indexOf(key) !== -1
                       || key == "tom") {
                query_bool.must.push({
                    "term": get_obj(key, {"value": value})
                });
            } else if (!searchPersons && key == "kat") {
                key = "has_kat" + value;
                value = true;
                query_bool.must.push({
                    "term": get_obj(key, {"value": value})
                });
            } else if (!searchPersons && ["geo", "geosub", "group"].indexOf(key) !== -1) {
                key = key + "_ids";
                query_bool.must.push({
                    "match": get_obj(key, value)
                });
            } else if (searchPersons && key == "global_search") {
                $.each(["firstname", "midname", "lastname"], function(){
                    query_bool.should.push({
                        "match": get_obj(this, value)
                    });
                });
                $.each(["spravka", "gb_spravka", "spravka_fio", "fond7_primtext"], function(){
                    query_bool.should.push({
                        "match": get_obj(this, value)
                    });
                });
            } else if (!searchPersons && key == "global_search") {
                $.each(["title", "deloname", "delonum"], function(){
                    query_bool.should.push({
                        "match": get_obj(this, value)
                    });
                });
            } else if (["date_from", "date_to"].indexOf(key) !== -1) {
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
            } else if (SIGN_FIELDS.indexOf(key) !== -1) {
                query_bool.must.push({
                    "match": get_obj(key, true)
                });
            }



        });
        if (! $.isEmptyObject(date_range)){
            var date_field;
            if (searchPersons)
                date_field = "lists_date";
            else
                date_field = "date";
            query_bool.must.push({
                "range": get_obj(date_field, date_range)
            });
        }

        var def;
        $("#more").addClass("is-hidden");
        if (searchPersons){
            def = search("persons", query_bool, offset).done(function( data ) {
                render_persons(data.hits.hits, offset);
                var fetched = data.hits.hits.length;
                // total includes offset
                var total = data.hits.total.value;
                if (!offset) {
                    // it's first request
                    render_stats(data.hits.total);
                }
                offset += fetched;
                search_state.search_offset = offset;
                if (search_state.search_offset < total) {
                    $("#more").removeClass("is-hidden");
                }
            });
        } else {
            def = search("lists", query_bool).done(function( data ) {
                render_lists(data.hits.hits);
                render_stats(data.hits.total);
            });
        }
        def.done(update_url).fail(function( data ) {
            if (data){
                console.log("Error", data);
                error_on_search(data);
            }else {
                // empty request
                clear_results();
            }
        });
    }

    function search(index_name, query_bool, offset){
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
            "track_total_hits": true,
            "query": {
                "bool": query_bool
            }
        };
        if (index_name == "persons"){
            data.size = offset ? SEARCH_SIZE : SEARCH_SIZE_FIRST;
            data.from = offset;
            data._source = {
                "excludes": ["spravka", "gb_spravka", "sign*"]
            };
            data.sort = ["sort"];
        } else {
            data.size = 1000;
            data.sort = ["date", "_score"];
        }


        return $.ajax({
            method: "POST",
            url: ES_URL + index_name + "/_search?pretty=true",
            crossDomain: true,
            data: JSON.stringify(data),
            dataType : 'json',
            contentType: 'application/json',
        });
    }

    function render_persons(records, append){
        search_state.render_persons = [records, append];
        search_state.render_lists = false;
        if (!append) {
            $("#results").empty();
        }
        if (!records.length){
            empty_results();
        }

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
                gb_spravka_link = '<a href="/persons/{0}#gb" title="Имеется версия следствия"><i class="fas fa-id-card"></i></a><br/>'.format(this._id);
            }
            var spiski_data = JSON.parse(this._source.lists);
            var spiski = "";
            $.each(spiski_data, function(){
                var style = "";
                if (this.striked){
                    style += "text-decoration: line-through;";
                }
                if (this.underline){
                    style += "text-decoration: underline;";
                }
                var pometa = "";
                if (this.pometa){
                    pometa = "<sup>Есть помета</sup>";
                }
                spiski += '* <a href="{0}" style="{1}">{2}</a>{3}<br/>'.format(
                    this.url,
                    style,
                    this.title,
                    pometa,
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
        search_state.render_persons = false;
        search_state.render_lists = [records];
        $("#results").empty();
        if (!records.length){
            empty_results();
        }
        $.each(records, function(){
            $("#results").append(
                '<p class="mt-3">{0} <a href="/lists/{1}">{2}</a></p>'.format(
                    format_date(this._source.date),
                    this._id,
                    this._source.title
                ));
        });
    }
    function render_stats(total) {
        search_state.render_stats = [total];
        $("#stats").removeClass("is-hidden");
        var text = total.value;
        if (total.relation != "eq"){
            // it may happen only when track_total_hits is disabled
            text += "+";
        }
        $("#search_count").text(text);
    }

    function clear_results(){
        $("#results").empty();
        $("#stats").addClass("is-hidden");
        $("#more").addClass("is-hidden");
    }
    function empty_results(){
        clear_results();
        $("#results").html("<h1>Ничего не найдено. Уточните запрос</h1>");
    }
    function error_on_search(data){
        $("#results").html("<h1>Ошибка сервера</h1><pre><code>{0}</code></pre>".format(data.responseText || ""));
    }

    function format_date(value){
        if (!value)
            return '';
        var date = value.split("-");
        if (date.length != 3)
            return value;
        date = "{0}.{1}.{2}".format(
            date[2],
            date[1],
            date[0]
        );
        return date;

    }


});

function search_init(){

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

window.SIGN_FIELDS = ["signstalin", "signmolotov", "signjdanov", "signkaganovic", "signvoroshilov", "signmikoyan", "signejov", "signkosior"];
window.CHECKBOX_FIELDS = SIGN_FIELDS.concat([
    "underlined", "striked", "pometa"
]);
window.LIST_FIELDS = CHECKBOX_FIELDS.concat([
    "global_search",
    "korpus", "tom",
    "geo", "geosub", "group", "kat",
    "date_from", "date_to"
]);

window.PERSON_FIELDS = LIST_FIELDS.concat([
    "firstname", "midname", "lastname"
]);



// data/db/tables/korpusa.csv
window.KORPUSA = {
    "0": {
        "toms": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"],
    },
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
window.GROUPS = {
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
window.GEO = {
    "1":"СССР",
    "2":"Азербайджанская ССР",
    "3":"Армянская ССР",
    "4":"Белорусская ССР",
    "5":"Грузинская ССР",
    "6":"Казахская ССР",
    "7":"&mdash; Актюбинская область",
    "8":"&mdash; Алма-Атинская область",
    "9":"&mdash; Восточно-Казахстанская область",
    "10":"&mdash; Гурьевская область",
    "11":"&mdash; Западно-Казахстанская область",
    "12":"&mdash; Карагандинская область",
    "13":"&mdash; Кустанайская область",
    "14":"&mdash; Северо-Казахстанская область",
    "15":"&mdash; Южно-Казахстанская область",
    "16":"Киргизская ССР",
    "17":"РСФСР",
    "18":"&mdash; Азово-Черноморский край",
    "19":"&mdash; Алтайский край",
    "20":"&mdash; Амурская область",
    "21":"&mdash; Архангельская область",
    "22":"&mdash; Башкирская АССР",
    "23":"&mdash; Бурято-Монгольская АССР",
    "24":"&mdash; Вологодская область",
    "25":"&mdash; Воронежская область",
    "26":"&mdash; Восточно-Сибирская область",
    "27":"&mdash; Горьковская область",
    "28":"&mdash; Дагестанская АССР",
    "29":"&mdash; Дальне-Восточный край",
    "30":"&mdash; Западная область",
    "31":"&mdash; Западно-Сибирский край",
    "32":"&mdash; Ивановская область",
    "33":"&mdash; Иркутская область",
    "34":"&mdash; Кабардино-Балкарская АССР",
    "35":"&mdash; Калининская область",
    "36":"&mdash; Калмыцкая АССР",
    "37":"&mdash; Камчатская область",
    "38":"&mdash; Карельская АССР",
    "39":"&mdash; Кировская область",
    "40":"&mdash; Коми АССР",
    "41":"&mdash; Краснодарский край",
    "42":"&mdash; Красноярский край",
    "43":"&mdash; Крымская АССР",
    "44":"&mdash; Куйбышевская область",
    "45":"&mdash; Курская область",
    "46":"&mdash; Ленинградская область",
    "47":"&mdash; Марийская АССР",
    "48":"&mdash; Мордовская АССР",
    "49":"&mdash; Московская область",
    "50":"&mdash; Новосибирская область",
    "51":"&mdash; Омская область",
    "52":"&mdash; Орджоникидзевский край",
    "53":"&mdash; Оренбургская область",
    "54":"&mdash; Орловская область",
    "55":"&mdash; Ростовская область",
    "56":"&mdash; Рязанская область",
    "57":"&mdash; Саратовская область",
    "58":"&mdash; Свердловская область",
    "59":"&mdash; Северная область",
    "60":"&mdash; Северо-Осетинская АССР",
    "61":"&mdash; Смоленская область",
    "62":"&mdash; Сталинградская область",
    "63":"&mdash; Тамбовская область",
    "64":"&mdash; Татарская АССР",
    "65":"&mdash; Томская область",
    "66":"&mdash; Тульская область",
    "67":"&mdash; Хабаровский край",
    "68":"&mdash; Челябинская область",
    "69":"&mdash; Чечено-Ингушская АССР",
    "70":"&mdash; Читинская область",
    "71":"&mdash; Ярославская область",
    "72":"Таджикская ССР",
    "73":"Туркменская ССР",
    "74":"Узбекская ССР",
    "75":"Украинская ССР",
    "76":"&mdash; Винницкая область",
    "77":"&mdash; Днепропетровская область",
    "78":"&mdash; Донецкая область",
    "79":"&mdash; Житомирская область",
    "80":"&mdash; Каменец-Подольская область",
    "81":"&mdash; Киевская область",
    "82":"&mdash; Молдавская АССР",
    "83":"&mdash; Николаевская область",
    "84":"&mdash; Одесская область",
    "85":"&mdash; Полтавская область",
    "86":"&mdash; Харьковская область",
    "87":"&mdash; Черниговская область"
};

// copy of data2hugo/geosub.json generated by data2hugo/titles2geosub.py
// geo_id -> geosub_id -> title
window.GEOSUB = {
    "1": {
        "51": "Список",
        "82": "I Быв.члены и кандидаты ЦК ВКП(б)",
        "83": "II Быв.члены КПК и КСК и Рев.Ком.ЦК",
        "84": "III Быв.секретари Обкомов, Крайкомов",
        "85": "IV Быв.Наркомы,Зам.Наркомов и Пред.Обл.исполкомов",
        "86": "V Быв.ответ.работники Наркоматов",
        "87": "VI Быв.военные работники",
        "88": "VII (быв.сотрудники НКВД)",
        "169": "М"
    },
    "10": {
        "160": "Казахская ССР // Гурьевская область"
    },
    "11": {
        "134": "Казахская ССР // Западно-Казахстанская область"
    },
    "12": {
        "75": "Казахская ССР // Карагандинская область"
    },
    "13": {
        "135": "Казахская ССР // Кустанайская область"
    },
    "14": {
        "120": "Казахская ССР // Северо-Казахстанская область"
    },
    "15": {
        "119": "Казахская ССР // Южно-Казахстанская область"
    },
    "16": {
        "142": "Киргизская ССР"
    },
    "17": {
        "27": "Представлен НКВД СССР - Бельский",
        "40": "г.Магнитогорск",
        "50": "Верхнеуральская тюрьма особого назначения",
        "123": "Ржев. Калининская жел.дор.",
        "161": "Управление НКВД по Дальстрою",
        "166": "ВОЛГОЛАГ НКВД"
    },
    "18": {
        "10": "Азово-Черноморский край"
    },
    "19": {
        "139": "Алтайский край"
    },
    "2": {
        "12": "Баку",
        "39": "Азербайджанская ССР"
    },
    "20": {
        "140": "г.Свободный. Амурская жел.дор."
    },
    "21": {
        "131": "Архангельская область"
    },
    "22": {
        "60": "Башкирская АССР",
        "79": "ДТО ГУГБ ж.д.им.Куйбышева. (Уфа)"
    },
    "23": {
        "153": "Бурято-Монгольская АССР"
    },
    "24": {
        "132": "Вологодская область",
        "162": "г.Вологда.-Северная жел.дор."
    },
    "25": {
        "35": "Воронежская область",
        "129": "г.Воронеж Московско-Донбасск. ж.д.",
        "130": "г.Воронеж Юго-Восточная жел.дор."
    },
    "26": {
        "34": "Восточно-Сибирская область"
    },
    "27": {
        "16": "Горьковская область",
        "99": "г.Горький - Горьковская жел.дор."
    },
    "28": {
        "168": "Дагестанская АССР"
    },
    "29": {
        "48": "Дальне-Восточный край"
    },
    "3": {
        "28": "Армянская ССР"
    },
    "30": {
        "33": "Западная область"
    },
    "31": {
        "9": "Западно-Сибирский край"
    },
    "32": {
        "19": "Ивановская область"
    },
    "33": {
        "151": "Иркутская область"
    },
    "34": {
        "62": "Кабардино-Балкарская АССР"
    },
    "35": {
        "42": "Калининградская область",
        "46": "Калининская область",
        "156": "Калининская жел.дор."
    },
    "36": {
        "155": "Калмыцкая АССР"
    },
    "37": {
        "118": "Камчатская область"
    },
    "38": {
        "102": "Карельская АССР",
        "165": "БЕЛБАЛТЛАГ НКВД"
    },
    "39": {
        "148": "Кировская область"
    },
    "4": {
        "37": "Белорусская ССР",
        "64": "НКВД Белорусской ССР",
        "110": "г.Гомель.-Белорусская ж.д."
    },
    "40": {
        "149": "Коми АССР"
    },
    "41": {
        "145": "Краснодарский край"
    },
    "42": {
        "13": "Красноярский край",
        "98": "г.Красноярск. Красноярская жел.дор."
    },
    "43": {
        "49": "Крымская АССР"
    },
    "44": {
        "17": "Куйбышевская область",
        "128": "г.Куйбышев. Куйбышевская жел.дор."
    },
    "45": {
        "32": "Курская область"
    },
    "46": {
        "20": "г.Ленинград",
        "44": "Ленинградская область",
        "113": "[Ленинградская обл. октябрь 1936 - <I>сост</I>]",
        "158": "Гор.Ленинград-Октябрьская ж.д.",
        "159": "Гор.Ленинград-Кировская ж.д."
    },
    "47": {
        "126": "Марийская АССР"
    },
    "48": {
        "63": "Темниковский лагерь НКВД",
        "127": "Мордовская АССР"
    },
    "49": {
        "1": "Москва-центр",
        "8": "Московская область",
        "43": "М",
        "65": "г.Калуга - Московско-Киевская жел.дорога",
        "80": "Д",
        "94": "г.Москва. Жел.дор.им.Дзержинского",
        "95": "г.Москва.Ленинская жел.дор.",
        "96": "Москва. ДТО Метро",
        "114": "[",
        "136": "г.Москва. Московско-окружн.ж.д.",
        "137": "г.Калуга. Моск.Киевская жел.дор.",
        "154": "Г",
        "164": "Л"
    },
    "5": {
        "24": "Грузинская ССР",
        "141": "г.Тбилиси - Закавказская жел.дор."
    },
    "50": {
        "78": "Новосибирская область",
        "122": "г.Новосибирск. Томская жел.дор."
    },
    "51": {
        "21": "Омская область",
        "107": "Гор.Омск.-Омская жел.дор."
    },
    "52": {
        "22": "Орджоникидзевский край",
        "23": "Орджоникидзевский край // г.Пятигорск",
        "150": "Гор.Орджоникидзе - Орджоникидзевская ж.д."
    },
    "53": {
        "38": "Оренбургская область",
        "116": "Оренбург - Оренбургская жел.дорога"
    },
    "54": {
        "144": "Орловская область"
    },
    "55": {
        "81": "Ростовская область",
        "97": "Гор.Ростов - ж.д.им.Ворошилова"
    },
    "56": {
        "146": "Рязанская область"
    },
    "57": {
        "14": "Саратовская область",
        "157": "гор.Саратов - Рязано-Уральская жел.дор."
    },
    "58": {
        "11": "Свердловская область",
        "100": "гор.Свердловск - ж.д. им.Кагановича"
    },
    "59": {
        "30": "Северная область"
    },
    "6": {
        "18": "Казахская ССР"
    },
    "60": {
        "133": "Северо-Осетинская АССР"
    },
    "61": {
        "93": "Смоленская область",
        "143": "гор.Смоленск. Западная жележная дорога"
    },
    "62": {
        "15": "Сталинградская область",
        "117": "г.Сталинград - Сталинградская ж.д."
    },
    "63": {
        "115": "Тамбовская область"
    },
    "64": {
        "29": "Татарская АССР",
        "111": "г.Казань. Казанская жел.дор."
    },
    "65": {
        "89": "ДТО ГУГБ НКВД Томской жел.дор."
    },
    "66": {
        "124": "Тульская область"
    },
    "67": {
        "41": "г.Хабаровск",
        "138": "г.Хабаровск - Дальне-Восточная жел.дорога"
    },
    "68": {
        "45": "Челябинская область",
        "77": "г.Челябинск. Южно-Уральская ж.д."
    },
    "69": {
        "108": "Чечено-Ингушская АССР"
    },
    "7": {
        "121": "Казахская ССР // Актюбинская область"
    },
    "70": {
        "152": "Гор.Чита - Забайкальский Военный Округ"
    },
    "71": {
        "31": "Ярославская область",
        "109": "г.Ярославль - Ярославская жел.дор."
    },
    "72": {
        "147": "Таджикская ССР"
    },
    "73": {
        "59": "Туркменская ССР",
        "163": "г.Ашхабад-Ашхабадская жел.дор."
    },
    "74": {
        "36": "Узбекская ССР",
        "125": "г.Ташкент - Ташкентская жел.дорога"
    },
    "75": {
        "47": "Донецкая область"
    },
    "76": {
        "25": "Украинская ССР // г.Винница",
        "56": "Винницкая область",
        "72": "Донецкая область"
    },
    "77": {
        "4": "г.Днепропетровск",
        "55": "Днепропетровская область",
        "67": "г.Днепропетровск - Сталинская жел.дорога",
        "70": "Донецкая область"
    },
    "78": {
        "5": "Донецкая область"
    },
    "79": {
        "103": "Украинская ССР // Житомирская область"
    },
    "8": {
        "74": "Казахская ССР // г.Алма-Ата и Алма-Атинская область",
        "76": "г.Алма-Ата - Туркестано-Сибирская ж.д."
    },
    "80": {
        "106": "Украинская ССР // Каменец-Подольская область"
    },
    "81": {
        "2": "г.Киев",
        "53": "Киевская область",
        "66": "Гор.Киев.-Юго-Западная ж.д.",
        "68": "Донецкая область",
        "90": "Украинская ССР // Киев-центр",
        "92": "Украинская ССР // Киевский военный округ"
    },
    "82": {
        "7": "Украина // А.М. С.С.Р.",
        "26": "Украинская ССР // г.Тирасполь",
        "104": "Украинская ССР // Молдавская АССР"
    },
    "83": {
        "91": "Николаевская область"
    },
    "84": {
        "6": "г.Одесса",
        "54": "Одесская область",
        "71": "Донецкая область",
        "101": "Гор.Одесса - Одесская ж.д."
    },
    "85": {
        "105": "Украинская ССР // Полтавская область",
        "167": "Украинская ССР // г.Полтава"
    },
    "86": {
        "3": "г.Харьков",
        "52": "Харьковский Военный Округ",
        "57": "Харьковская область",
        "61": "Украинская ССР // Харьков - Южная жел.дор.",
        "69": "Донецкая область"
    },
    "87": {
        "58": "Черниговская область",
        "73": "Донецкая область"
    },
    "9": {
        "112": "Казахская ССР // Восточно-Казахстанская область"
    }
};

};
