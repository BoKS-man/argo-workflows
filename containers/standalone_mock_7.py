import argparse
from datetime import datetime as dt
import torch
import numpy as np
from torch import nn

model_size_factor = 7
model_tensor_modificator = 1

def run(args):
    logger = Logger(model_size_factor, model_tensor_modificator)
    model = ModelMock(model_size_factor, model_tensor_modificator)
    if args.weights_path is not None:
        load_weights(model, args.weights_path)
    logger.log(f'The mock model is initialized (Size: {model_size_factor}, Add: {model_tensor_modificator}). Weights size is {check_model_size(model)} Mb')
    try:
        result = process_model(model, args.input_path, logger)
        logger.log(f'Resulted tensor mean is {result.mean()}')
    except Exception as e:
        logger.log(f'Model processing failure: {e}')
        raise e
    save_result(result, args.output_path)

def check_model_size(model):
    mem_params = sum([param.nelement()*param.element_size() for param in model.parameters()])
    mem_bufs = sum([buf.nelement()*buf.element_size() for buf in model.buffers()])
    mem = mem_params + mem_bufs # in bytes
    return round(mem / 1024 / 1024, 3)

def process_model(model, input_path, logger):
    tensor = torch.load(input_path)
    logger.log(f'Incoming tensor mean is {tensor.mean()}')
    return model(tensor)

def load_weights(model, weights_path):
    model.load_state_dict(torch.load(weights_path))

def save_result(tensor, path):
    torch.save(tensor, path)

class Logger():
    def __init__(self, model_size_factor, model_tensor_modificator):
        self.log_path = f'model{model_size_factor}-{model_tensor_modificator}_{dt.now().date()}.log'

    def log(self, text):
        print(text)
        try:
            with open(self.log_path, 'a') as l:
                l.write(f'{dt.now().time()}: {text}\n')
        except Exception as e:
            print(f'Log write failure: {e}')
            raise e

class ModelMock(nn.Module):
    def __init__(self, n, added_number=1): #allocated memory is increased according to N in geometric progression
        super(ModelMock, self).__init__()
        self.__added_number = added_number
        self.func = torch.add #random action with input tensor that indicates model was used
        layers = [nn.Linear(32, 1024),
            nn.ReLU()] + \
            list(np.array([[nn.Linear(int(1024*(i)), int(1024*(i+1))), nn.ReLU()] for i in range(1, n)]).flatten()) + \
            [nn.Linear(int(1024*(n)), 512),
            nn.ReLU(),
            nn.Linear(512, 10)] #just unused layers to allocate some memory
        self.linear_relu_stack = nn.Sequential(*layers)
    def forward(self, x):
        return self.func(x, self.__added_number) #we can hardcode added number here or bring it as argument this does not matter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='/input.pt')
    parser.add_argument('--output_path', type=str, default='/output.pt')
    parser.add_argument('--weights_path', type=str, default=None)
    args = parser.parse_args()
    run(args)