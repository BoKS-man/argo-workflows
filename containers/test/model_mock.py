import torch
import numpy as np
from torch import nn

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