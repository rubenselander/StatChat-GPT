# StatChat: Building a Statistical Research GPT with DeepLake and Eurostat
In this article we will build a GPT that can answer statistical questions using DeepLake and the Eurostat API. We will also show you how to improve the performance of the GPT by using Deep Memory and reranking with Cohere.

## Introduction
Open data is great but it can be hard to find the data you need. Eurostat is the statistical office of the European Union and provides a lot of open, reliable data. However, finding relevant data can be a challenge. This is especially true if you don't have experience with finding and interacting with statistical databases. This is where our GPT comes in. It not only finds the data we need but also presents it in a way that is easy to understand and use. 

## Why not just use ChatGPT? 
Well, ChatGPT is great at answering questions but say you want to know something like "How has France's CO2 emissions changed since 1990?" or "Does life expectancy in the EU correlate with GDP per capita?", these are questions that require data to answer and are also not findable through a simple google search.

## Why not just use the Eurostat API?
This is a valid question. The Eurostat API is great and we will be using it in our project. However, it doesn't provide proper search functionality. Without knowing the exact dataset code and variables you need, the GPT would have a very hard time finding any relevant data at all. This is where DeepLake comes in. DeepLake is a vector store that allows us to search for relevant datasets using natural language combined with simple filters.

## Why Deeplake?
There are many options when it comes to vector stores. We chose Deeplake for a few reasons:
1. Deeplake is open source
2. Simple and easy to use. Well documented and active community.
3. Deeplake offers "Deep Memory" which will greatly improve the search performance and in turn our GPT's ability to find relevant datasets. More on this later.
<!-- Personal reasons: -->
4. Local development and usage is serverless making it so much easier and faster to both develop and use in your projects.  
5. Going from local, serverless, to a fully hosted solution literally takes 1 line of code. Maybe 2 if you want to be exact.
```python
from deeplake import deepcopy
deepcopy(src="<path to local deeplake>", dest="<path to new hosted instance>")
# That's it!
```
6. I've literally never interacted with a more accessible and helpful developer team than the one behind deeplake, ActiveLoop.







Deeplake is a open source vector store. We are going to use a local flask based api that allows the GPT to search for suiting and relevant datasets through natural language and filters. The local api acts as a bridge between the deeplake vector store and our GPT. Once the GPT has found a dataset/table it can use it can then perform an api call to eurostat api and retrieve the relevant data using the dataset code and variables (for which it specifies a selection that determines the data it needs). The code and corresponding variables is from our deeplake dataset.







