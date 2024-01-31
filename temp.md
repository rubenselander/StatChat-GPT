### StatChat - Making Eurostat data more accessible


Building a Statistical Research GPT: Integrating ChatGPT with DeepLake and Eurostat API


## Introduction
ToDo: Short introduction.
# Problem
ToDo: Describe the problem. What is the motivation, why is it important?
# Background
- Define what deeplake is
- Define Eurostat
- Define GPT
# Why not another vector store?
1. Deeplake is open source
2. Deeplake offers "Deep Memory" which will greatly improve the search performance and our GPTs ability to find relevant datasets.
<!-- - Define Deep Memory -->
<!-- Personal reasons: -->
3. Local development and usage is serverless making it so much easier to both develop and deploy.
4. Going from local, serverless, to a fully hosted solution literally takes 1 line of code.
5. Its open source but surprisingly well documented and easy to use.






Deeplake is a open source vector store. We are going to use a local flask based api that allows the GPT to search for suiting and relevant datasets through natural language and filters. The local api acts as a bridge between the deeplake vector store and our GPT. Once the GPT has found a dataset/table it can use it can then perform an api call to eurostat api and retrieve the relevant data using the dataset code and variables (for which it specifies a selection that determines the data it needs). The code and correpsponding variables is from our deeplake dataset.