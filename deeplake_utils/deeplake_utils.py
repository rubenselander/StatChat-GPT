import deeplake
import numpy as np
import os
import json


def load_jsonl_file(jsonL_file_path):
    with open(jsonL_file_path, "r", encoding="utf-8") as f:
        json_lines = f.readlines()
    dicts = []
    for json_line in json_lines:
        try:
            dicts.append(json.loads(json_line))
        except:
            print(json_line)
    return dicts


file_path = "all_tables_formatted.jsonl"
ds_title = "all_tables_formatted_1"
ds_path = f"hub://rubenselander/{ds_title}"


tensor_dicts = [
    {
        "name": "code",
        "htype": "text",
        "chunk_compression": "lz4",
    },
    {
        "name": "provider_id",
        "htype": "text",
        "chunk_compression": "lz4",
    },
    {
        "name": "language",
        "htype": "text",
        "chunk_compression": "lz4",
    },
    {
        "name": "url",
        "htype": "text",
        "chunk_compression": "lz4",
    },
    {
        "name": "title",
        "htype": "text",
        "chunk_compression": "lz4",
    },
    {
        "name": "variables",
        "htype": "json",
        "chunk_compression": "lz4",
    },
    {
        "name": "metadata",
        "htype": "json",
        "chunk_compression": "lz4",
    },
]


ds = deeplake.empty(ds_path)
# ds.add_creds_key(os.environ["ACTIVELOOP_TOKEN"],


with ds:
    # Define tensors
    for tensor_args_dict in tensor_dicts:
        ds.create_tensor(**tensor_args_dict)


# # replace key "map" with "valueTexts" and if the value is a string, convert it to a list
# import json


# def load_jsonl_file(jsonL_file_path):
#     with open(jsonL_file_path, "r", encoding="utf-8") as f:
#         json_lines = f.readlines()
#     dicts = []
#     for json_line in json_lines:
#         try:
#             dicts.append(json.loads(json_line))
#         except:
#             print(json_line)
#     return dicts


# def save_as_jsonl(dicts, jsonL_file_path):
#     with open(jsonL_file_path, "w", encoding="utf-8") as f:
#         for dict in dicts:
#             f.write(json.dumps(dict, ensure_ascii=False) + "\n")


# tables = load_jsonl_file("all_tables.jsonl")
# formatted_tables = []

# fixed_tables = 0
# for table in tables:
#     if table.get("provider_id", None) == "statists_norway":
#         new_table = {key: value for key, value in table.items()}
#         current_title = table["title"]
#         # the title always starts with a 5 digit number followed by ": " and then the actual title
#         # extract the 5 digit number and remove it + ": " from the title
#         new_table["title"] = current_title[7:]
#         digit_code = current_title.split(":")[0]
#         new_table["code"] = digit_code
#         new_url = "https://data.ssb.no/api/v0/en/table/" + digit_code
#         new_table["url"] = new_url
#         formatted_tables.append(new_table)

#     else:
#         formatted_tables.append(table)


# save_as_jsonl(formatted_tables, "all_tables_formatted.jsonl")
