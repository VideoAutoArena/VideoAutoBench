import json
import pickle

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def dump_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

def load_jsonl(file_path):
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            lines.append(json.loads(line))
    return lines

def dump_jsonl(data, file):
    with open(file, "w") as f:
        for line in data:
            f.write(json.dumps(line) + "\n")

def dump_jsonl_append(data, file):
    with open(file, "a") as f:
        for line in data:
            f.write(json.dumps(line) + "\n")

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)