import boto3
import os

s3 = boto3.client('s3')

# output_bucket
result_bucket = "546proj2output-1"

if "csv" not in os.listdir():
    os.makedirs("csv")

for e in os.listdir(os.path.join("test_cases", "test_case_2")):
    key = e.split(".")[0] + ".csv"
    s3.download_file(result_bucket, key, os.path.join("csv",key))
    f = open(os.path.join("csv", key))
    content = f.read()
    f.close()
    f = open("mapping")
    mapping = f.read().split("\n")
    flag = True
    for map in mapping:
        inFlag = False
        if map.split(":")[0].split(".")[0] == key.split(".")[0]:
            inFlag = True
            map_content = map.split(":")[1].split(",")
            content = content.split(",")[1:]
            content[-1] = content[-1].replace("\n", "")
            i = 0
            while i < len(content):
                if map_content[i] != content[i]:
                    if (map_content[i] == "freshman" and content[i] == "freshmen") == False:
                        flag = False
                        break
                i += 1
        if inFlag:
            if flag:
                break
            else:
                print("There is error in", e)
                print("\n")
                break

if flag:
    print("All the recognition results are correct")
