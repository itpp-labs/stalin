PYTHON = python3

hugo: hugo_data hugo_content

hugo_data:
	${PYTHON}	data2hugo/lists_data.py

hugo_content:
	${PYTHON}	data2hugo/lists_content.py

website:
	#hugo --minify -s hugo/
	hugo -s hugo/
