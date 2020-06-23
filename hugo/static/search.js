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

});
