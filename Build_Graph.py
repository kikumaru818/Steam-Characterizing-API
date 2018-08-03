import sklearn.manifold as sm
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle

folder="test/1c"
input_file = folder+'output_float2.txt'


output_embed = 'output/embedding_shared_5.png'
output_center = '1centers_shared5.png'
output_embed = folder+'1embedding_my_3.png'
output_center = folder+'1centers_my_3.png'

dim = 3
customPalette = ['#CC0000', '#00CC00', '#0000CC', '#00CCCC', '#CCCC00', '#CC00CC', '#FFB6C1', '#D8BFD8']


# embedding using TSNE
def embed_TSNE(features, d=3):
    model = sm.TSNE(n_components=d, init='pca', random_state=0)
    ret = model.fit_transform(features)
    return ret


# embedding using Isomap, dimension of target space, number of neighbors
def embed_isomap(features, d=3, k=5):
    model = sm.Isomap(n_components=d, n_neighbors=k)
    ret = model.fit_transform(features)
    return ret


# drawing embedding plot, two options for methods, one is TSNE, the other one is ISOMAP
# ISOMAP seems to work better
def draw_embedding_plot(data, labels, method='ISOMAP'):

    if method == 'ISOMAP':
        ret = embed_isomap(data, d=dim)
    elif method == 'TSNE':
        ret = embed_TSNE(data, d=dim)
    else:
        print('No method chosen.')
        return

    colors = [customPalette[x] for x in labels]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(ret[:, 0], ret[:, 1], ret[:, 2], c=colors)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(method)
    plt.savefig(output_embed, format='png')
    plt.close()


# Haven't calculate variance or so yet.
def draw_line_plot(centers, vocab):

    leng = len(centers)
    labels = range(leng)

    colors = [customPalette[x] for x in labels]
    fig = plt.figure(figsize=(8,10))
    ax = fig.add_subplot(111)
    for i in range(leng):
        ax.plot(centers[i], c=colors[i], label='center of cluster ' + str(i))

    ticks = {}
    for key in vocab.keys():
        ticks[vocab[key]] = key

    # print(ticks)
    new_ticks = [str(ticks[i]) for i in range(len(ticks))]

    ax.set_xticks(range(len(new_ticks)))
    ax.tick_params(axis='x', rotation=90, labelsize=6)
    ax.set_xticklabels(new_ticks)
    ax.set_ylabel('value')
    ax.set_xlabel('attributes')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_center, format='png')
    plt.close()


if __name__ == '__main__':


    with open(input_file, 'rb') as file:
        [points, label, vocab, centers] = pickle.load(file)

        draw_embedding_plot(points, label)
        draw_line_plot(centers, vocab)

