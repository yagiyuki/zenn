---
title: "Pythonとmatplotlibで楕円を外接する多角形を描く方法 詳細解説あり"
emoji: "🐍"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["math", "Python", "matplotlib"]
published: true
---

楕円を外接する多角形の描き方を説明します。
「こんなマニアックなことやって何がしたいの!?」という声が聞こえて来そうですが、とある案件で実際に必要になりました。
高校数学が実際の仕事で生きる場面があるんだなーという気楽な感じで読んでいただければと思います。

## 前提知識
楕円を外接する多角形を書くにあたる前提知識として、以下2点が必要です。

* 真円の外接多角形の座標
* 楕円と真円の関係

### 前提知識1: 真円の外接多角形の座標

真円の半径を`r`、真円の外接多角形の頂点のなす角を`θ`とすると、「真円の中心」から「真円の外接多角形の頂点」までの距離は、`r/cos(θ/2)`になります。
よって、外接多角形の座標は、`(x, y) = (r/cos(θ/2)*cos(α), r/cos(θ/2)*sin(α))` となります。(`α`は外接多角形のなす角)
![](https://storage.googleapis.com/zenn-user-upload/evbebd2ecc4x0r3zxihzdb9tutdg)

### 前提知識2: 楕円と真円の関係

中心を原点とした半径aの真円と半長径a・半短径bの楕円について考えます。
この２つの図形には、以下の関係があります。

```
真円の座標(x, y)=楕円の座標(x, (b/a)y)
```
つまり半径a真円をy方向にb/a倍すると半長径a・半短径bの楕円ができます。

![](https://storage.googleapis.com/zenn-user-upload/jhaw1lwg4ira10f4gjrcr7qt5bao)

## (結論)描画手法

以下の手順で、半長径a・半短径bの楕円を描画することができます。

* 半径aの真円の外接多角形を生成 (前提知識1)
* 生成した外接多角形の各頂点のy座標を`(b/a)`倍する (前提知識2)


## Matplotlibで描画

実際にMatplotlibで描画すると以下のようになります。
![](https://storage.googleapis.com/zenn-user-upload/nzn1m1o25oov7my4yynhjqfs2zil)

比較のために、楕円の外接多角形を含めて合計4つの図形を描画しました。
* 真円(TrueCircle)
* 真円を外接する多角形(OutTrueCircle)
* 長径が真円の半径と同値の楕円(Ellipse)
* 楕円を外接する多角形(OutEllipse)


楕円を外接する多角形が描けていることがわかります。
ちなみに、ソースコードは、こんな感じです。

```python
# numpyをインポート
import math
import matplotlib.pyplot as plt
import pylab
inRadius = 5.0
radius_a = 5.0
radius_b = 3.0

#
# 真円の描画
#
def draw_circle():
    # 中心(0.2,0.2)で半径0.2の円を描画
    list = plt.Circle((0.0, 0.0), inRadius, fc="#f0f0f0", label = "TrueCircle")
    plt.gca().add_patch(list)
    plt.axis('scaled')

#
# 真円外接多角形の描画
#
def draw_out_circle():
    outSeg = 10
    deg = math.radians(360 / outSeg)
    angle = 0
    x = []
    y = []
    outRadius = inRadius / math.cos(deg / 2)
    for i in range(outSeg + 1):
        angle += deg
        x.append(outRadius*math.cos(angle))
        y.append(outRadius*math.sin(angle))

    plt.plot(x, y, label = "OutTrueCircle")

#
# 楕円の描画
#
def draw_ellipse():
    outSeg = 360
    deg = math.radians(360 / outSeg)
    angle = 0
    x = []
    y = []
    outRadius = radius_a / math.cos(deg / 2)
    for i in range(outSeg + 1):
        angle += deg
        x.append(outRadius*math.cos(angle))
        y.append(outRadius*math.sin(angle) * (radius_b / radius_a))

    plt.plot(x, y, label = "Ellipse")

#
# 楕円外接多角形の描画
#
def draw_out_ellipse():
    outSeg = 10
    deg = math.radians(360 / outSeg)
    angle = 0
    x = []
    y = []
    outRadius = radius_a / math.cos(deg / 2)
    for i in range(outSeg + 1):
        angle += deg
        x.append(outRadius*math.cos(angle))
        y.append(outRadius*math.sin(angle) * (radius_b / radius_a))

    plt.plot(x, y, label = "OutEllipse")


if __name__ == '__main__':
    draw_circle()
    draw_out_circle()
    draw_ellipse()
    draw_out_ellipse()
    plt.legend()  # 凡例を表示
    pylab.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    pylab.subplots_adjust(right=0.7)
    plt.title("Graph Title")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()
```

以上です。面白いと思っていただけた方は、「いいね」いただけるとうれしいです。
