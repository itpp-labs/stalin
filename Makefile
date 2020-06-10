PYTHON = python3

hugo: hugo_data hugo_content

hugo_data:
	${PYTHON}	data2hugo/home_page_data.py
	${PYTHON}	data2hugo/lists_data.py
	${PYTHON}	data2hugo/persons_data.py

hugo_content:
	${PYTHON}	data2hugo/lists_content.py
	${PYTHON}	data2hugo/persons_content.py

website:
	#hugo --minify -s hugo/
	hugo -s hugo/ --templateMetrics
