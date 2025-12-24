# # re-save file 
# import chardet

# with open("data.json", "rb") as f:
#     rawdata = f.read()

# result = chardet.detect(rawdata)
# print(result)


with open("data.json", "r", encoding="utf-16") as f:
    data = f.read()

with open("data_fixed.json", "w", encoding="utf-8") as f:
    f.write(data)
