import numpy as np
#データを分割するツール
from sklearn.model_selection import train_test_split
#精度を評価するための混同行列とAUC(正解率)
from sklearn.metrics import confusion_matrix, accuracy_score
#データセットMNISTのインポート
from sklearn.datasets import fetch_openml
#pytorch用のパッケージのインストール
import torch
import torch.nn as nn
import torch.optim as optim

#GPUを使う
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device

x,labels = fetch_openml('mnist_784',return_X_y=True)
#データ型がobjectなのでint型に変換
y = labels.astype(np.int32)

#784次元のMNISTデータを画像形式に変換する
#もともと画像形式のデータはこの変換を行う必要はない
#-1は、他の値を決めた時に残りの値を調整してくれる
x = x.reshape(-1,1,28,28)


class Net(nn.Module):
  def __init__(self):
    super().__init__()

    #特徴量抽出器
    #畳み込み層+活性化関数+プーリング層が2回あり
    #kernel_sizeはフィルターの大きさ、strideはフィルターのずらし方、paddingは周りを何マス埋めるか(画像のサイズを変更しないように埋める)
    self.features = nn.Sequential(
        nn.Conv2d(1, 8, kernel_size = 3, stride = 1, padding = 1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size = 2),

        nn.Conv2d(8,16, kernel_size = 3, stride = 1, padding = 1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size = 2)
    )


    #分類器
    #2段階の全結合層
    #特徴抽出器によって最終的に16個のフィルターに7×7のデータとなっているので分類器への特徴量の入力は16×49=784となる。
    self.classifier = nn.Sequential(
        nn.Linear(784,20),
        nn.Sigmoid(),
        nn.Linear(20,10),
        nn.LogSoftmax(dim = 1)
    )

  #順伝播(データが実際に入ってきた時の処理を書く)  
  def forward(self, x):
    h = self.features(x)

    #畳み込み層の出力はまだ画像データの形になっているので、それをベクトルの形変換
    #view関数はテンソルの形を変形する関数で引数は(行、列)、-1を代入すると他の指定した数値に合わせてくれる
    h = h.view(len(x), -1)

    return self.classifier(h)


#ネットワークのインスタンスを作成
net = Net()

#モデルをGPUにおくる
net = net.to(device)
print(net)
  
  
  

#データを学習用と評価用に分割
split = train_test_split(x, y, train_size=0.8, test_size=0.2)
train_features, test_features, train_labels, test_labels = split

#学習用データの2割を検証用に利用
split = train_test_split(train_features, train_labels, train_size = 0.8, test_size =0.2 )
train_features, valid_features , train_labels, valid_labels = split



#データの準備

#学習用データ
train_features = torch.Tensor(train_features)
train_labels = torch.tensor(train_labels, dtype = torch.int64)
train_set = torch.utils.data.TensorDataset(train_features, train_labels)
train_loader = torch.utils.data.DataLoader(train_set,batch_size = 100, shuffle = True, num_workers = 2)

#検証用データ
valid_features = torch.Tensor(valid_features)
valid_labels = torch.tensor(valid_labels, dtype = torch.int64)
valid_set = torch.utils.data.TensorDataset(valid_features, valid_labels)
valid_loader = torch.utils.data.DataLoader(valid_set,batch_size = 100, shuffle = True, num_workers = 2)

#評価用データ
test_features = torch.Tensor(test_features)
test_labels = torch.tensor(test_labels, dtype = torch.int64)
test_set = torch.utils.data.TensorDataset(test_features, test_labels)
test_loader = torch.utils.data.DataLoader(test_set,batch_size = 4, shuffle = False, num_workers = 2)



#誤差関数(NLLLossはNegative Log Likelihood loss)
criterion = nn.NLLLoss()

#最適化
optimizer = optim.Adam(net.parameters(), lr = 0.001)



#学習のループ

num_epochs = 5

stages = {"train":train_loader,"valid":valid_loader}

for epoch in range(num_epochs):
  for stage, loader in stages.items():
    if stage == "train":
      #モデルを学習モードに変更
      net = net.train()
    else:
      #モデルを評価モードに変更(dropoutをoffにし、batch normを正規化のために使うようにする)
      net = net.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for inputs, labels in loader:
      #GPUに送る
      inputs = inputs.to(device)
      labels = labels.to(device)

      #勾配を初期化
      optimizer.zero_grad()

      #順伝播
      outputs = net(inputs)

      #誤差を計算
      loss = criterion(outputs, labels)

      if stage == "train":
        #逆伝播
        loss.backward()

        #パラメータの更新
        optimizer.step()
        
      #推定結果を保持
      predicted = outputs.max(1, keepdim=True)[1]
      total_correct += predicted.eq(labels.view_as(predicted)).sum().item()

      # 誤差を記録
      total_loss += loss.item()
      total_samples += len(inputs)

    # 1エポック分の計算結果をまとめて表示
    total_loss /= total_samples
    total_correct /= total_samples
    if stage == "train":
      print('[%d] loss: %e, accuracy: %.3f' % (epoch + 1, total_loss, total_correct), end=", ")
    else:
      print('val_loss: %e, val_accuracy: %.3f' % (total_loss, total_correct))

# 学習が終了したらモデルを保存する
print('Finished Training')
torch.save(net.state_dict(), "trained.pth")



#学習したモデルを読み込む

#モデルの形(インスタンス)を読み込む
test_net = Net()

#読み込んだ形の上にパラメータを読み込む
test_net.load_state_dict(torch.load("trained.pth"))


#モデルを評価モードに変更

test_net = test_net.eval()


# 評価のループ

losses = []
predicts = []
gts = []

for inputs, labels in test_loader:  # 学習データを1バッチ分取得
    # GPUがあればGPUに送る
    inputs = inputs.to(device)
    labels = labels.to(device)

    # 順伝播(torch.no_gradは勾配の計算をしないようにしている、それによりメモリ消費を抑えられる)
    with torch.no_grad():
        outputs = net(inputs)

    # 誤差を計算
    loss = criterion(outputs, labels)

    # 推定結果を記録
    predicted = outputs.max(1, keepdim=True)[1]

    # 誤差を記録
    total_loss += loss.item()

    #.detach().numpy()でtensorからnumpyに変換
    #.cpu()で、データをcpuに移せる
    predicts.extend(predicted.cpu().detach().numpy())
    gts.extend(labels.cpu().detach().numpy())

#total_lossの値をlen(gts)(labelsの長さ)で割って代入している、つまり誤差の総和の平均を出している
total_loss /= len(gts)
print('test_loss: %e, test_accuracy: %.3f' % (total_loss, accuracy_score(gts, predicts)))
