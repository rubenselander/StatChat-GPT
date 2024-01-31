# TODO
- Upload the the eurostat data to deeplake
- Implement the local flask api (functions for searching and retrieving data)
- Define the OpenAPI spec for the local api

- Define a OpenAPI spec for Eurostat API (writing our own will allow us to only define the relevant endpoints and also make it better suited for our use case)
- Write the instructions for our GPT to use the local api to find and retrieve data from Eurostat API (very simple just need to get the other parts done first)
- DEMO IS DONE AND SHOULD NOW BE READY TO GO!

# Further work
- Write deep memory training data. We need X number of question and dataset title pairs. The questions should be something like "How has the average life expectancy in Finland changed for men and woman since 2000?" title should be something like "Life expectancy by country, gender and year". Note: The titles MUST be real titles from our collection.
- Training data should be split into 2 parts. One for training and one for testing. The testing data should be used to evaluate the performance of the model.

- Make a template allowing users to easily connect their own deeplake instance to a GPT
- Make a prettier version of the workflow diagram (https://app.diagrams.net/)
- Make a diagram showcasing the improved performance of the GPT when using Deep Memory
