$(document).ready(function(){
    $("#search_form input").on("input propertychange paste", function(event){
        search_persons();
        event.preventDefault();
    });
    function search_persons(){
        // See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
        var query_bool = {
            "must": {
                "match": {}
            },
            "should": {
                "match": {}
            }
        };
        $.each($("#search_form").serializeArray(), function(){
            var key = this.name;
            var value = this.value;
            if (!value)
                return;
            if (["firstname", "midname", "lastname"].indexOf(key) != -1) {
                query_bool.must.match[key] = value;
            } else if (key == "global_search") {
                $.each(["firstname", "midname", "lastname"], function(){
                    query_bool.should.match[this] = value;
                });
            }
        });


        search("persons", query_bool).done(function( data ) {
            render_persons(data.hits.hits);

        }).fail(function( data ) {
            console.log(data);
        });
    }

    function search(index_name, query_bool){
        if ($.isEmptyObject(query_bool.should.match)){
            delete query_bool.should.match;
            delete query_bool.should;
        } else {
            query_bool.minimum_should_match = 1;
        }
        var data = {
            "size": 20, // TODO: make pagination
            "query": {
                "bool": query_bool
            }
        }
        return $.ajax({
            method: "POST",
            url: ES_URL + index_name + "/_search?pretty=true",
            crossDomain: true,
            async: false,
            data: JSON.stringify(data),
            dataType : 'json',
            contentType: 'application/json',
        });
    }

    function render_persons(records){
        $("#results").empty();

        $.each(records, function(){
            $("#results").append(
                '<p><a href="/persons/{0}">{1}</a>TODO spravka<br/>TODO spiski</p>'.format(
                    this._id,
                    this._source.nameshow,
                ));
        });
    }

    String.format = function() {
        var s = arguments[0];
        for (var i = 0; i < arguments.length - 1; i++) {
            var reg = new RegExp("\\{" + i + "\\}", "gm");
            s = s.replace(reg, arguments[i + 1]);
        }

        return s;
    }

});
