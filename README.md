# Search-Engine
## Installation: 
Use the python package manager pip to install nltk, BeautifulSoup, and Flask: 

	pip install nltk
	pip install bs4
	pip install Flask


## How to build the indexes:
From the command line, run the following command in the main directory:

	python3 build_indexes.py -trace
	
To view the build progress on the command line, use the “-trace” argument. 
	

## How to start the search engine:
If using command line, run the following commands from the main directory:

	cd WebInterface
	python3 app.py 

If using an IDE, run the app.py script.

Go to http://127.0.0.1:5000/ or the link that is prompted in the terminal if different. 


## How to run a simple query:
Type your query (ex: “uc irvine”) into the box under “Please enter a search query”. 

Press ENTER or click the Submit button. The top 10 results will be displayed in order of descending relevance in addition to the runtime. 

## Contributors
[@ileenf](https://github.com/ileenf)

[@shridhar](https://github.com/sonashridhar)
