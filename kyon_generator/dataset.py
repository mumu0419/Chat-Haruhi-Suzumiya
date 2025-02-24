import torch
import json
from torch.utils.data import Dataset
import os
import jsonlines
from torch.utils.data import ConcatDataset

# file_names = ['xiaofeng_test_output_dialogue.jsonl', 'baizhantang_test_output_dialogue.jsonl', 'wangduoyu_test_output_dialogue.jsonl', 'guofurong_test_output_dialogue.jsonl', 'weixiaobao_test_output_dialogue.jsonl', 'haruhi_synthesis_dialogue.jsonl', 'murongfu_test_output_dialogue.jsonl', 'McGonagall_test_output_dialogue.jsonl', 'Ron_test_output_dialogue.jsonl', 'Sheldon_test_output_dialogue.jsonl', 'yuqian_test_output_dialogue.jsonl', 'duanyu_test_output_dialogue.jsonl', 'xuzhu_test_output_dialogue.jsonl', 'jiumozhi_test_output_dialogue.jsonl', 'liyunlong_synthesis_dialogue.jsonl', 'Malfoy_test_output_dialogue.jsonl', 'tongxiangyu_test_output_dialogue.jsonl', 'ayaka_test_output_dialogue.jsonl', 'Raj_test_output_dialogue.jsonl', 'Harry_test_output_dialogue.jsonl', 'Snape_test_output_dialogue.jsonl', 'Penny_test_output_dialogue.jsonl', 'zhongli_test_output_dialogue.jsonl', 'tangshiye_test_output_dialogue.jsonl', 'Luna_test_output_dialogue.jsonl', 'hutao_test_output_dialogue.jsonl', 'Dumbledore_test_output_dialogue.jsonl', 'Hermione_test_output_dialogue.jsonl', 'qiaofeng_test_output_dialogue.jsonl', 'wangyuyan_test_output_dialogue.jsonl', 'wanderer_test_output_dialogue.jsonl', 'raidenShogun_test_output_dialogue.jsonl']
def read_jsonl_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    json_data = json.loads(line)
                    data.append(json_data)
                except json.JSONDecodeError:
                    # print(f"Failed to parse JSON: {line}")
                    continue
    return data

def collate_fn(batch):
    inputs = [sample["input"] for sample in batch]
    targets = [sample["answer"] for sample in batch]

    # batch_inputs = torch.stack(inputs)
    # batch_targets = torch.stack(targets)

    return inputs, targets

class CharacterDataset(Dataset):
    def __init__(self, json_data, character_path, memory_number, memory_length):
        pass
        self.data = json_data
        self.character_path = character_path
        self.memory_number = memory_number
        self.memory_path = "jsonl/title_text_embed.jsonl"
        self.system_prompt_name = "system_prompt.txt"
        self.system_prompt = self.getSystemPrompt()
        self.memory_embed, self.memory_text = self.read_jsonl_and_convert_to_tensor(os.path.join(self.character_path,self.memory_path))
        self.memory_length = memory_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        query_embed = torch.tensor(sample["embedding"])
        top_k = self.getMemory(query_embed)
        # print(self.memory_text[0].split("｜｜｜")[1])
        retrieved_memory = [self.memory_text[i].split("｜｜｜")[1] for i in top_k]
        retrieved_memory = self.join_with_limit(retrieved_memory, self.memory_length)
        # retrieved_memory = '\n'.join(retrieved_memory)
        chat_history = sample["chat_history"]
        chat_history = '###'.join(chat_history)
        chat_history += '###'
        query = sample["query"]
        input = self.system_prompt + "###" + retrieved_memory + chat_history + query
        # print(retrieved_memory)
        data = {
            "query": sample["query"],
            "system_prompt": self.system_prompt,
            "retrieved_memory": retrieved_memory,
            "chat_history": chat_history,
            "answer": sample["answer"],
            "embedding": query_embed,
            "source": sample["source"],
            "input": input
        }
        return data

    def join_with_limit(self, items, max_length, separator="###"):
        result = ""
        for item in items:
            # 如果加入当前元素不会导致超过上限，就将其添加到结果字符串中
            if len(result) + len(item) + len(separator) <= max_length:
                if result:
                    result += separator
                result += item
            else:
                break  # 如果已经超过上限，就停止添加新元素
        return result


    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    def read_jsonl_and_convert_to_tensor(self, file_path):
        embed_list = []
        data_list = []
        with jsonlines.open(file_path) as reader:
            for item in reader:
                embed_list.append(next(iter(item.values())))
                data_list.append(next(iter(item.keys())))
        data_tensor = torch.tensor(embed_list)
        return data_tensor, data_list

    def getSystemPrompt(self):
        file_path = os.path.join(self.character_path, self.system_prompt_name)
        file_content = self.read_file_content(file_path)
        return file_content

    def getMemory(self, vector):
        pass
        similarity = torch.matmul(self.memory_embed, vector)

        # 找出最大的几个元素的索引
        top_indices = torch.topk(similarity, self.memory_number).indices

        return top_indices
        # print("Top indices:", top_indices)


# jsonl_file_path = '/Users/pufferfish/Downloads/real_train_data/'
# character_path = "/Users/pufferfish/Chat-Haruhi-Suzumiya/characters/"
# file_names = ['xiaofeng_test_output_dialogue.jsonl', 'baizhantang_test_output_dialogue.jsonl', 'wangduoyu_test_output_dialogue.jsonl', 'guofurong_test_output_dialogue.jsonl', 'weixiaobao_test_output_dialogue.jsonl', 'haruhi_synthesis_dialogue.jsonl', 'murongfu_test_output_dialogue.jsonl', 'McGonagall_test_output_dialogue.jsonl', 'Ron_test_output_dialogue.jsonl', 'Sheldon_test_output_dialogue.jsonl', 'yuqian_test_output_dialogue.jsonl', 'duanyu_test_output_dialogue.jsonl', 'xuzhu_test_output_dialogue.jsonl', 'jiumozhi_test_output_dialogue.jsonl', 'liyunlong_synthesis_dialogue.jsonl', 'Malfoy_test_output_dialogue.jsonl', 'tongxiangyu_test_output_dialogue.jsonl', 'ayaka_test_output_dialogue.jsonl', 'Raj_test_output_dialogue.jsonl', 'Harry_test_output_dialogue.jsonl', 'Snape_test_output_dialogue.jsonl', 'Penny_test_output_dialogue.jsonl', 'zhongli_test_output_dialogue.jsonl', 'tangshiye_test_output_dialogue.jsonl', 'Luna_test_output_dialogue.jsonl', 'hutao_test_output_dialogue.jsonl', 'Dumbledore_test_output_dialogue.jsonl', 'Hermione_test_output_dialogue.jsonl', 'qiaofeng_test_output_dialogue.jsonl', 'wangyuyan_test_output_dialogue.jsonl', 'wanderer_test_output_dialogue.jsonl', 'raidenShogun_test_output_dialogue.jsonl']
# all_datasets = []
# for file_name in file_names:
#     character_name = file_name.split("_")[0]
#     character = os.path.join(character_path, character_name)
#     jsonl_file = os.path.join(jsonl_file_path, file_name)
#     jsonl_data = read_jsonl_file(jsonl_file)
#     c = CharacterDataset(jsonl_data, character, 8, 2000)
#     all_datasets.append(c)
#     # print(character_name)
#     # print(c.system_prompt)
#     # print(c[0]["query"])

# combined_dataset = ConcatDataset(all_datasets)

# print(combined_dataset[0]["query"])
# print(combined_dataset[0]["retrieved_memory"])
# print(combined_dataset[3000]["query"])
# print(combined_dataset[3000]["retrieved_memory"])

# path = '/Users/pufferfish/Downloads/real_train_data/yuqian_test_output_dialogue.jsonl'
# with open(path, "r") as file:
#     for line in file:
#         try:
#             json.loads(line)
#         except:
#             print(line)


# path = "/Users/pufferfish/Downloads/training_data/"
# for file_name in file_names:
#     with open(path+file_name, 'r') as json_file:
#         for line in json_file:
#             new_line = line.replace("}", "}\n")
#             new_line_list = new_line.split("\n")
#             with open('/Users/pufferfish/Downloads/real_train_data/'+file_name, "w") as output_file:
#                 output_file.write('\n'.join(new_line_list))