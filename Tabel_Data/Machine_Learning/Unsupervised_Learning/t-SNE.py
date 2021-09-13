#以下がt-SNEに必要なコード
from sklearn.manifold import TSNE

import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import torchvision
import torchvision.transforms as transforms


#データの読み込み
visualizeset = torchvision.datasets.FashionMNIST(root='./data', train=False, download=True)

images = visualizeset.test_data
labels = visualizeset.test_labels

# 画像をベクトル化する
images = images.numpy().reshape(len(images), -1)
# t-SNEするには多すぎるので削減
_, images, _, labels = train_test_split(images, labels, test_size=0.3)


images.shape

#t-SNEを実行し二次元データにする
tsne = TSNE(n_components=2,random_state=42)
x_reduced = tsne.fit_transform(images)


x_reduced.shape


plt.figure(figsize=(13,7))
plt.scatter(x_reduced[:,0],x_reduced[:,1],c=labels,
            cmap='jet',s=15,alpha = 0.5)
plt.show()
