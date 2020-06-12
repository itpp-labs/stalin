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

upload_search:
	curl -H "Content-Type: application/json" -XPOST "localhost:9200/persons/_bulk?pretty&refresh" --data-binary "@search/elasticsearch-persons.json"
	curl "localhost:9200/_cat/indices?v"

website:
	#hugo --minify -s hugo/
	hugo -s hugo/ --templateMetrics
