import torch
import torch.nn as nn
import torch.nn.functional as F
from gensim import models
import numpy

'''
w = models.KeyedVectors.load_word2vec_format('/home/nvinden/ML/CNNFORNLP2014/google_embeddings/GoogleNews-vectors-negative300.bin', binary=True)
google_vector_size = w.vector_size
google_data_length = int(w.vectors.size/google_vector_size)


idx_2_embeddings = torch.Tensor(w.vectors)
idx_2_word = w.index2word
idx_2_entity = w.index2entity

'''

idx_2_embeddings = torch.rand(1000, 300)
google_vector_size = 10
google_data_length = 1000

#Hyperparameters
p = 0.5


class network(nn.Module):
    def __init__(self, sentence_length, embedding_dimension = 300, trained_words = True, static_words = False,
    filter_windows=(5,4,3), feature_maps=100, dropout_rate = 0.5, l2_constraint = 3, mini_batch_size=50, num_tags = 2):
        super(network, self).__init__()
        #Hyper Parameters of Model
        self.feature_maps = feature_maps
        self.dropout_rate = dropout_rate
        self.l2_constraint = l2_constraint
        self.mini_batch_size = mini_batch_size
        self.trained_words = trained_words
        self.static_words = static_words
        self.sentence_length = sentence_length
        self.embedding_dimension = embedding_dimension
        self.filter_windows = filter_windows
        self.num_tags = num_tags

        #Network Layers
        self.embedding = nn.Embedding.from_pretrained(idx_2_embeddings)
        self.convolution = []
        for i in range(len(filter_windows)):
            self.convolution.append(nn.Conv2d(1, feature_maps, (filter_windows[i], embedding_dimension)))
        self.linear = nn.Linear(feature_maps * len(filter_windows), num_tags)

    def forward(self, input):
        mini_batch_size = len(input) #number of rows -> mini batch size inputted
        embedding = self.embedding(input)
        linear_inp = torch.empty(mini_batch_size, 0)
        for i in range(len(self.filter_windows)):
            convolution = F.relu(self.convolution[i](embedding.view(mini_batch_size, 1, self.sentence_length, self.embedding_dimension)))
            maxed_out = torch.max(convolution, dim = 2)[0].view(mini_batch_size, self.feature_maps)
            linear_inp = torch.cat((linear_inp, maxed_out), dim=1)
        dropout = torch.randint(0,2,(mini_batch_size, self.embedding_dimension), requires_grad=False)
        out = F.softmax(self.linear(dropout*linear_inp), dim=1)
        return out

    #input is torch tensors of size number of sentences * batch size
    #tag is a vector of shape 1 x batch size
    def cost(self, input, tag):
        y_bar = self.forward(input)
        y = torch.zeros(self.num_tags, 1)
        
batch_size = 50
max_sentence_length = 20
embedding_dim = 5

net = network(max_sentence_length)
#inp = torch.LongTensor(batch_size, max_sentence_length).random_(0, google_data_length)
#out = net(inp)
net.cost(torch.LongTensor(50, 20).random_(0, google_data_length), 1)