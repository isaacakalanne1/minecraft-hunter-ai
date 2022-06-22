import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, l1_dims, l2_dims, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, l1_dims)
        self.linear2 = nn.Linear(l1_dims, l2_dims)
        self.linear3 = nn.Linear(l2_dims, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        return x
    
    def save(self, file_name='model.pth'):
        file_name = self.getFilePath(file_name)
        torch.save(self.state_dict(), file_name)

    def load_ryoshi_model(self, file_name='model-ryoshi-run-2.2.pth'):
        file_name = self.getFilePath(file_name)
        self.load_state_dict(torch.load(file_name))
        print('Loaded ryoshi model!')

    def getFilePath(self, file_to_load):
        model_folder_path = '/Users/iakalann/Documents/minecraft-hunter-ai/Plot'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_to_load)
        return file_name

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        # self.model.load_ryoshi_model()
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: Predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for i in range(len(done)):
            Q_New = reward[i]
            if not done[i]:
                Q_New = reward[i] + self.gamma * torch.max(self.model(next_state[i]))

            target[i][torch.argmax(action).item()] = Q_New

        # 2: Q_New = Reward + gamma * max(next_predicted_q_value)
        # pred.clone()
        # preds[argmax(action)] = Q_New
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

    def get_action(self, state):

        lookYawIndex = torch.tensor([0])
        lookYawValue = torch.index_select(state, 0, lookYawIndex).item()

        jumpIndexesAll = torch.tensor([1, 2])
        jumpTensor = torch.index_select(state, 0, jumpIndexesAll)
        jumpValue = torch.argmax(jumpTensor).item()

        final_move = [lookYawValue, jumpValue]
        return final_move