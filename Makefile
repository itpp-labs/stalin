PYTHON = python3

hugo: hugo_data hugo_content

hugo_data:
	${PYTHON}	data2hugo/home_data.py
	${PYTHON}	data2hugo/lists_data.py
	${PYTHON}	data2hugo/persons_data.py

hugo_content:
	${PYTHON}	data2hugo/lists_content.py
	${PYTHON}	data2hugo/persons_content.py

search: search/elasticsearch-persons.json

search/elasticsearch-persons.json: hugo/content/persons/*
	hugo-elasticsearch \
	--input "hugo/content/persons/*" \
	--output "search/elasticsearch-persons.json" \
	--language "yaml" \
	--delimiter "---" \
	--index-name "persons"

	#hugo-elasticsearch \
	#  --input "hugo/content/lists/**" \
	#  --output "search/elasticsearch-lists.json" \
	#  --language "yaml" \
	#  --delimiter "---" \
	#  --index-name "lists"

website:
	#hugo --minify -s hugo/
	hugo -s hugo/ --templateMetrics
