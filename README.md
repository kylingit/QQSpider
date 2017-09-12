### QQSpider
基于 Python 的 QQ 空间爬虫程序

特性

#### version 2.0
> 2017.07.28 更新

由于 qq 加密算法改动，通过 qqlib 登录已失效，各种测试后发现变化还挺大的，没摸清加密细节，故删去此模块。改为通过 selenium 登录，加载的是 phantomjs 驱动程序，在网络不畅的情况下可能会比较缓慢


- qqlib 失效，改用 selenium 调用 phantomjs 登录
- 支持 python3
- 贴近 PEP8 代码规范，改进一些 bug

部分运行截图
登录
![](https://raw.githubusercontent.com/kylingit/QQSpider/master/QQSpider_v2/screenshot/snipaste08262333.png)

爬取说说
![](https://raw.githubusercontent.com/kylingit/QQSpider/master/QQSpider_v2/screenshot/snipaste08262330.png)

![](https://raw.githubusercontent.com/kylingit/QQSpider/master/QQSpider_v2/screenshot/snipaste08262331.png)

读取当前状态
![](https://raw.githubusercontent.com/kylingit/QQSpider/master/QQSpider_v2/screenshot/snipaste08272248.png)

![](https://raw.githubusercontent.com/kylingit/QQSpider/master/QQSpider_v2/screenshot/snipaste08262332.png)

#### version 1.0
> 2017.07 由于 qq 加密算法改动，qqlib 登录已失效

- 基于 [qqlib](https://github.com/gera2ld/qqlib)，通过账号密码登录，支持验证码处理
- cookie 保存功能。第一次登录成功后保存 cookie 到文件，在 cookie 有效期内可以从文件读取 cookie 登录
- 断点续爬。爬取数据的时候由于异常原因，会保存当前爬取的状态，重新运行程序的时候会检测上一次爬取的位置，从当前位置开始继续爬取
- 数据统计分析功能。这部分是扩展的，结合可视化软件可以展示一些统计结果
