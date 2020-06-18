$(document).ready(function(){
    var searchTimer;
    function clear_search_timer(){
        if (!searchTimer)
            return;
        clearTimeout(searchTimer);
        searchTimer = null;
    }
    function start_search(){
        clear_search_timer();
        search_persons();
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
            } else if (key == "global_search") {
                $.each(["firstname", "midname", "lastname"], function(){
                    query_bool.should.push({
                        "match": get_obj(this, value)
                    });
                });
            }
        });


        search("persons", query_bool).done(function( data ) {
            render_persons(data.hits.hits);

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
            "size": 20, // TODO: make pagination
            "query": {
                "bool": query_bool
            }
        };
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
            if (this._source.gb_spravka){
                gb_spravka_link = '<a href="/persons/{0}#gb">GB</a><br/>'.format(this._id);
            }

            $("#results").append(
                '<p><a href="/persons/{0}">{1}</a><br/>{2}{3}{4}TODO spiski<br/></p>'.format(
                    this._id,
                    this._source.nameshow,
                    spravka,
                    fond7,
                    gb_spravka_link
                ));
        });
    }
    function clear_results(){
        $("#results").empty();
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
