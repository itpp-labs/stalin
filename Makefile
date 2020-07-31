.PHONY: search
PYTHON = python3

hugo: hugo_data hugo_content

hugo_data:
	${PYTHON}	data2hugo/home_data.py
	${PYTHON}	data2hugo/lists_data.py
	${PYTHON}	data2hugo/persons_data.py

hugo_content:
	${PYTHON}	data2hugo/lists_content.py
	${PYTHON}	data2hugo/persons_content.py

search:
	${PYTHON} hugo2search.py

upload_search: upload_search_person upload_search_lists
	# check results
	curl "localhost:9200/_cat/indices?v"

upload_search_person:
	# prepare index
	curl -X PUT "localhost:9200/persons?pretty" -H 'Content-Type: application/json' --data-binary "@search/index-persons.json"

	# upload index
	curl -H "Content-Type: application/json" -XPOST "localhost:9200/persons/_bulk?pretty&refresh" --data-binary "@search/elasticsearch-persons.json" > /tmp/elasticsearch-persons.logs
	echo ""

upload_search_lists:
	# prepare index
	curl -X PUT "localhost:9200/lists?pretty" -H 'Content-Type: application/json' --data-binary "@search/index-lists.json"
	# upload index
	curl -H "Content-Type: application/json" -XPOST "localhost:9200/lists/_bulk?pretty&refresh" --data-binary "@search/elasticsearch-lists.json" > /tmp/elasticsearch-lists.logs
	echo ""

spravki: data/spravki/all.csv
	rm hugo/data/spravki/*.yaml
	${PYTHON} data2hugo/spravki-csv2yaml.py


website:
	#hugo --minify -s hugo/
	hugo -s hugo/ --templateMetrics
