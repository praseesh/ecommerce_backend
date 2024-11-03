import random 
import json
import torch
from nltk_utils import tokenize, bag_of_words
from .model import NeuralNet

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
with open('intents.json', 'r')as f:
    intents = json.load(f)
FILE= "data.pth"
data = torch.load(FILE)
input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.evaluate

bot_name = "Eva"
print("Lets chat!...type 'quit' to Exit ")
while True:
    sentence = input("You: ")
    if sentence == "quit":
        break
    sentence = tokenize(sentence)
    x = bag_of_words(sentence,all_words)
    x = x.reshape(1,x_shape[0])
    x = torch.from_numpy(x)
    output = model(x)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output,dim=1)
    probs = probs[0][predicted.item()]
    if probs.item > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                print(f'{bot_name}: {random.choice(intent["responses"])}')
    else:
        print(f'{bot_name}: "I do not understand"')