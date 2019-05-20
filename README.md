# spider
中国裁判文书网爬虫
## Overview
This is a spider for [中国裁判文书网](http://wenshu.court.gov.cn/).
## Features
- 支持代理
- 根据时间、省份划分数据，支持全量爬取
- 支持多进程
## Run
```Shell
python spider.py -num_processes 1 -start_time 2016-1-2 -end_time 2016-1-2
```
## Result
- raw data

![image](https://github.com/wuyifan18/spider/blob/master/result1.jpg)
- processed data

![image](https://github.com/wuyifan18/spider/blob/master/result2.jpg)
---
**If you have any questions, please open an** ***[issue](https://github.com/wuyifan18/spider/issues).***

**Welcome to** ***[pull requests](https://github.com/wuyifan18/spider/pulls)*** **to improve this project!**
