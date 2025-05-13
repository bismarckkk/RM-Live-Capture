## RoboMaster Live Capture
#### RM录播姬

### 功能
* 录制官方流，支持分辨率选择
* 自动切片、自动启动与停止录制
* 基于网页的管理面板
* 在线播放已经完成的录制
* 一键批量上传至B站（由于上游神秘问题，该功能可能无法正常使用，如遇问题可自行升级bilibili api尝试）

### 工作原理
* 通过直接拉取官方直播间HLS流实现录制，因性能考量不在本地执行转码，直接原样保存`.ts`数据，自行拼接`.m3u8`进行播放
* 通过拉取赛事流程JSON实现自动切片与自动启动和停止

### 部署
1. 安装必要依赖：Python、Ffmpeg（不需要转码功能可以不安装ffmpeg）
2. 从release中下载最新版本`RM_Live_Capture.tar.gz`并解压
3. 进入backend目录，执行`pip install -r requirements.txt`安装后端依赖
4. 编辑`config.py`修改相关配置（特别注意修改HTTP Basic Security的账号密码）
5. 创建`config.py`中对应的两个存储路径
6. 运行`main.py`启动程序
* 可选：执行`backend/video.py`可以将所有`.m3u8`文件转码到`.mp4`（该转码不会进行编解码，速度很快，不占用CPU

### 编译部署（不推荐）
1. 安装必要依赖：NodeJs、Yarn、Python、Ffmpeg（不需要转码功能可以不安装ffmpeg）
2. Clone项目到本地并进入项目文件夹
3. 进入web目录，执行`yarn && yarn build`构建前端项目
4. 将`web/dist`目录中的所有文件拷贝到`backend/static`目录
5. 进入backend目录，执行`pip install -r requirements.txt`安装后端依赖
6. 编辑`config.py`修改相关配置（特别注意修改HTTP Basic Security的账号密码）
7. 运行`main.py`启动程序
* 可选：执行`backend/video.py`可以将所有`.m3u8`文件转码到`.mp4`（该转码不会进行编解码，速度很快，不占用CPU）
