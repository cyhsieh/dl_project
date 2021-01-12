import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
import os
import matplotlib.pyplot as plt
import numpy as np

# ============================= #
# you can define your own model #
# ============================= #
# class myNet(nn.Module):
#     #define the layers
#     def __init__(self):
#         super(myNet, self).__init__()

#     def forward(self, x):
#         return x


class LeNet(nn.Module):
    # define the layers
    def __init__(self):
        super(LeNet, self).__init__()
        print('Building model...')
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 317 * 317 , 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 60)
        self.relu = nn.ReLU()

    # connect these layers
    def forward(self, x):
        # print("begin", x.shape)
        x = self.pool(self.relu(self.conv1(x)))
        # print("after conv1", x.shape)
        x = self.pool(self.relu(self.conv2(x)))
        # print("after conv2", x.shape)
        x = x.view(-1, 16 * 317* 317)
        # print("after xview", x.shape)
        # x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        # print("after fc1", x.shape)
        x = self.relu(self.fc2(x))
        # print("after fc2", x.shape)
        x = self.fc3(x)
        # print("after fc3", x.shape)
        return x


class ChineseOCR(object):
    """docstring for ChineseOCR"""

    def __init__(self, in_path, epoch, batch_size, lr):
        super(ChineseOCR, self).__init__()
        self.in_path = in_path
        self.epoch = epoch
        self.batch_size = batch_size
        self.lr = lr

        # self.classes = ['one', 'two', 'three', 'four', 'five',
                        # 'six', 'seven', 'eight', 'nine', 'ten']

        self.classes = ['c-10', 'c-9', 'c-8', 'c-7', 'c-6', 'c-5', 'c-4', 'c-3', 'c-2', 'c-1', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13', 'c14', 'c15', 'c16', 'c17', 'c18', 'c19', 'c20', 'c21', 'c22', 'c23', 'c24', 'c25', 'c26', 'c27', 'c28', 'c29', 'c30', 'c31', 'c32', 'c33', 'c34', 'c35', 'c36', 'c37', 'c38', 'c39', 'c40', 'c41', 'c42', 'c43', 'c44', 'c45', 'c46', 'c47', 'c48', 'c49']

        self.checkdevice()
        self.prepareData()
        self.getModel()
        self.train_acc = self.train()
        self.saveModel()
        # self.loadModel('./model.pt')
        self.test()

        # self.showWeights()

    def checkdevice(self):
        # To determine if your system supports CUDA
        print("Check devices...")
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Current device:", self.device)

        # device = torch.device("cuda" if self.device else "cpu")

        # Also can print your current GPU id, and the number of GPUs you can use.
        if self.device == "cuda":
            print("Our selected device:", torch.cuda.current_device())
            print(torch.cuda.device_count(), "GPUs is available")
        return

    def prepareData(self):
        # The output of torchvision datasets are PILImage images of range [0, 1]
        # We transform them to Tensor type
        # And normalize the data
        # Be sure you do same normalization for your train and test data
        print('Preparing dataset...')

        # The transform function for train data
        transform_train = transforms.Compose([
            transforms.RandomCrop(1280, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (1, 1, 1)),
            # you can apply more augment function
            # [document]: https://pytorch.org/docs/stable/torchvision/transforms.html
        ])

        # The transform function for test data
        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (1, 1, 1)),
        ])

        # TODO
        # source_path = os.path.join(self.in_path, '../images/classes')
        self.trainset = torchvision.datasets.ImageFolder(
            os.path.join(self.in_path,'data/train/classes'), transform=transform_train)
        self.testset = torchvision.datasets.ImageFolder(
            os.path.join(self.in_path,'data/valid/classes'), transform=transform_test)

        self.trainloader = torch.utils.data.DataLoader(
            self.trainset, batch_size=self.batch_size, shuffle=True)
        self.testloader = torch.utils.data.DataLoader(
            self.testset, batch_size=self.batch_size, shuffle=False)
        # you can also split validation set
        # self.validloader = torch.utils.data.DataLoader(self.validset, batch_size=self.batch_size, shuffle=True)
        return

    def getModel(self):
        # Build a Convolution Neural Network
        self.net = LeNet()
        print(self.net)

        # Define loss function and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adadelta(
            self.net.parameters(), lr=self.lr)
        # self.optimizer = optim.SGD(
        #     self.net.parameters(), lr=self.lr, momentum=0.9)
        return

    def train(self):
        print('Training model...')
        # Change all model tensor into cuda type
        # something like weight & bias are the tensor
        self.net = self.net.to(self.device)

        # Set the model in training mode
        # because some function like: dropout, batchnorm...etc, will have
        # different behaviors in training/evaluation mode
        # [document]: https://pytorch.org/docs/stable/nn.html#torch.nn.Module.train
        self.net.train()
        for e in range(self.epoch):  # loop over the dataset multiple times
            running_loss = 0.0
            correct = 0
            for i, (inputs, labels) in enumerate(self.trainloader, 0):

                # change the type into cuda tensor
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)

                # zero the parameter gradients
                self.optimizer.zero_grad()

                # forward + backward + optimize
                outputs = self.net(inputs)
                # select the class with highest probability
                _, pred = outputs.max(1)
                # if the model predicts the same results as the true
                # label, then the correct counter will plus 1
                correct += pred.eq(labels).sum().item()

                loss = self.criterion(outputs, labels)

                loss.backward()
                self.optimizer.step()

                # print statistics
                running_loss += loss.item()
                if i % 100 == 99:    # print every 200 mini-batches
                    print('[%d, %5d] loss: %.3f' %
                          (e + 1, i + 1, running_loss / 100))
                    running_loss = 0.0

            print('%d epoch, training accuracy: %.4f' %
                  (e+1, 100.*correct/len(self.trainset)))
        print('Finished Training')
        return 100.*correct/len(self.trainset)

    def test(self):
        print('==> Testing model..')
        # Change model to cuda tensor
        # or it will raise when images and labels are all cuda tensor type
        self.net = self.net.to(self.device)

        # Set the model in evaluation mode
        # [document]: https://pytorch.org/docs/stable/nn.html#torch.nn.Module.eval
        self.net.eval()

        correct = 0
        running_loss = 0.0
        iter_count = 0
        class_correct = [0 for i in range(len(self.classes))]
        class_total = [0 for i in range(len(self.classes))]
        with torch.no_grad():  # no need to keep the gradient for backpropagation
            for data in self.testloader:
                images, labels = data
                images = images.to(self.device)
                labels = labels.to(self.device)
                outputs = self.net(images)
                _, pred = outputs.max(1)
                correct += pred.eq(labels).sum().item()
                c_eachlabel = pred.eq(labels).squeeze()
                loss = self.criterion(outputs, labels)
                iter_count += 1
                running_loss += loss.item()
                for i in range(len(labels)):
                    cur_label = labels[i].item()
                    try:
                        class_correct[cur_label] += c_eachlabel[i].item()
                    except:
                        print(class_correct[cur_label])
                        print(c_eachlabel[i].item())
                    class_total[cur_label] += 1

        print('Total accuracy is: {:4f}% and loss is: {:3.3f}'.format(
            100 * correct/len(self.testset), running_loss/iter_count))
        print('For each class in dataset:')
        for i in range(len(self.classes)):
            print('Accruacy for {:18s}: {:4.2f}%'.format(
                self.classes[i], 100 * class_correct[i]/class_total[i]))

    def saveModel(self):
        # After training , save the model first
        # You can saves only the model parameters or entire model
        # Some difference between the two is that entire model
        # not only include parameters but also record hwo each
        # layer is connected(forward method).
        # [document]: https://pytorch.org/docs/master/notes/serialization.html
        print('Saving model...')

        # only save model parameters
        torch.save(self.net.state_dict(), './weight.t7')

        # you also can store some log information
        state = {
            'net': self.net.state_dict(),
            'acc': self.train_acc,
            'epoch': self.epoch
        }
        torch.save(state, './weight.t7')

        # save entire model
        torch.save(self.net, './model.pt')
        return

    def loadModel(self, path):
        print('Loading model...')
        if path.split('.')[-1] == 't7':
            # If you just save the model parameters, you
            # need to redefine the model architecture, and
            # load the parameters into your model
            self.net = LeNet()
            checkpoint = torch.load(path)
            self.net.load_state_dict(checkpoint['net'])
        elif path.split('.')[-1] == 'pt':
            # If you save the entire model
            self.net = torch.load(path)
        return

    def showWeights(self):
        # TODO
        w_conv1 = self.net.conv1.weight.reshape(-1).detach().numpy()
        w_conv2 = self.net.conv2.weight.reshape(-1).detach().numpy()
        w_fc1 = self.net.fc1.weight.reshape(-1).detach().numpy()
        w_fc2 = self.net.fc2.weight.reshape(-1).detach().numpy()
        w_fc3 = self.net.fc3.weight.reshape(-1).detach().numpy()

        print(w_conv1)

        plt.figure(figsize=(24, 6))
        plt.subplot(1, 5, 1)
        plt.title("conv1 weight")
        plt.hist(w_conv1)

        plt.subplot(1, 5, 2)
        plt.title("conv2 weight")
        plt.hist(w_conv2)

        plt.subplot(1, 5, 3)
        plt.title("fc1 weight")
        plt.hist(w_fc1)

        plt.subplot(1, 5, 4)
        plt.title("fc2 weight")
        plt.hist(w_fc2)

        plt.subplot(1, 5, 5)
        plt.title("fc3 weight")
        plt.hist(w_fc3)

        plt.savefig('weights.png')


if __name__ == '__main__':
    # you can adjust your hyperperamers
    # for test, try epoch from 75 to 7
    ocr = ChineseOCR('./', 75, 8, 0.001)
