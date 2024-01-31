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




Rewrite the get_data endpoint so that it specifies the query as a json object. The keys should be variable ids/codes (same as in the variables retrieved from the get_table_variables endpoint) and the values for each key should be a list of value codes/ids which correspond to the values the user wants to retrieve for that variable.
For example, after calling "get_table_variables" with "table_code": "table123" we get back:
{
    "freq": {
        "text": "Time frequency",
        "values": {
            "A": "Annual"
        }
    },
    "na_item": {
        "text": "National accounts indicator (ESA 2010)",
        "values": {
            "EXP_PPS_EU27_2020_HAB": "Real expenditure per capita (in PPS_EU27_2020)",
            "VI_PPS_EU27_2020_HAB": "Volume indices of real expenditure per capita (in PPS_EU27_2020=100)",
            "CV_VI_HAB": "Coefficient of variation of volume indices of expenditure per capita (percentage)"
        }
    },
    "ppp_cat": {
        "text": "Analytical categories for purchasing power parities (PPPs) calculation",
        "values": {
            "GDP": "Gross domestic product"
        }
    },
    "unit": {
        "text": "Unit of measure",
        "values": {
            "PC": "Percentage"
        }
    },
    "geo": {
        "text": "Geopolitical entity (reporting)",
        "values": {
            "BE": "Belgium",
            "DK": "Denmark",
            "DE": "Germany",
            "EL": "Greece",
            "ES": "Spain",
            "FR": "France",
            "IT": "Italy",
            "NL": "Netherlands",
            "AT": "Austria",
            "PL": "Poland",
            "PT": "Portugal",
            "FI": "Finland",
            "SE": "Sweden",
            "IS": "Iceland",
            "NO": "Norway",
            "CH": "Switzerland",
            "UK": "United Kingdom"
        }
    },
    "time": {
        "text": "Time",
        "values": {
            "2000": "2000",
            "2001": "2001",
            "2002": "2002",
            "2003": "2003",
            "2004": "2004",
            "2005": "2005",
            "2006": "2006",
            "2007": "2007",
            "2008": "2008",
            "2009": "2009",
            "2010": "2010",
            "2011": "2011",
            "2012": "2012",
            "2013": "2013",
            "2014": "2014",
            "2015": "2015",
            "2016": "2016",
            "2017": "2017",
            "2018": "2018",
            "2019": "2019",
            "2020": "2020",
            "2021": "2021",
            "2022": "2022"
        }
    }
}

If the user wants to know the GDP, expenditure and volume indices for Sweden and Finland for the years 2010-2020 then the query should look something like this:
{
    "table_code": "table123",
    "query": {
        "freq": ["A"],
        "na_item": ["EXP_PPS_EU27_2020_HAB", "VI_PPS_EU27_2020_HAB"],
        "unit": ["PC"],
        "geo": ["SE", "FI"],
        "time": ["*"],
        "ppp_cat": ["GDP"]
    }
}

Note that by using "*" for the time variable we are telling the api to retrieve all values for that variable. This is the same as not specifying the time variable at all. The same goes for the other variables. If we want to retrieve all values for all variables we can simply not specify the query at all. The api will then assume that we want all values for all variables.
