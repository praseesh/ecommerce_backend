import random
import json
import torch
from nltk_utils import tokenize, bag_of_words
from model import NeuralNet

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents and model data
with open('P:\\Kannur\\ecommerce_backend\\chatbot\\intents.json', 'r') as f:
    intents = json.load(f)

FILE = "data.path"  # Corrected typo from 'data.path' to 'data.pth'
data = torch.load(FILE)

input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

# Initialize model and load saved state
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Eva"
print("Let's chat!...type 'quit' to Exit")

while True:
    sentence = input("You: ")
    if sentence.lower() == "quit":
        break

    # Tokenize and convert input sentence to a bag of words
    sentence = tokenize(sentence)
    x = bag_of_words(sentence, all_words)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x).to(device)

    # Get model output
    output = model(x)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # Calculate probability of predicted tag
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # Respond if probability is above threshold
    if prob.item() > 0.60:  
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                print(f'{bot_name}: {random.choice(intent["responses"])}')
    else:
        print(f'{bot_name}: "I do not understand"')
