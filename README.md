# pcr识别+生日祝福


## 本项目地址：

https://github.com/BeiYazi0/pcr_recognition

## 部署教程：

1.下载或git clone本插件：

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目

git clone https://github.com/BeiYazi0/pcr_recognition

2.下载模型

下载release中的pcr_recognition.h5，并放在models文件夹下。

3.启用：

在 HoshinoBot\hoshino\config\ **bot**.py 文件的 MODULES_ON 加入 'pcr_recognition'

然后重启 HoshinoBot

## 指令

【princess connect】 + 图片(@xx)

识别图片中的公主连结角色，以聊天记录形式返回判断结果(概率和角色精选图片)和该角色的四个描述。

【生日祝福】 

角色生日当天发送通知，收到包含“生日快乐”和角色名在内的祝福语，返回生日剧情语句和角色精选图片。


## 备注

模型训练集数量为35000左右，包含75个角色（见duel_data.py），准确率约为91%，识别图像包含角色全身效果较好。

感觉比起模型本身，精选图片价值更高hhh。已经尽量排除r18，但也难免手抖。

等待更新中。。。
