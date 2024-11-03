import json
import random
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .nltk_utils import tokenize, bag_of_words
from .model import NeuralNet

# Load the trained model once, when the server starts
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
FILE = r'P:\Kannur\blogplatform\chatbot\data.pth'

# Load data and model
data = torch.load(FILE)
input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Load intents file
with open(r'P:\Kannur\blogplatform\chatbot\intents.json', 'r') as f:
    intents = json.load(f)

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        message = json.loads(request.body).get("message")
        if not message:
            return JsonResponse({"error": "No message provided"}, status=400)

        # Tokenize and process the message
        sentence = tokenize(message)
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
                    response = random.choice(intent["responses"])
                    return JsonResponse({"response": response})
        else:
            return JsonResponse({"response": "I do not understand"})

    return JsonResponse({"error": "Invalid request method"}, status=405)
