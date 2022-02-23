import torch
from datetime import datetime as dt

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