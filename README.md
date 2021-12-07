# <img width="60px" src="/README/icon.png"/> hang out! 邊緣人揪團

## Introduction 
+ 以 LINE 作為操作介面，運用對話方式完成開團及報名
+ 開團：透過 chatbot 問答，提供活動必要資訊，並寫入後端資料庫
+ 報名：依照活動類型分類，查詢目前可供報名的活動
+ 查詢記錄：查看歷史開團及報名紀錄，以及活動詳細資訊

## Techniques
+ Built a web hook server using Python, deployed on Heroku. 
+ Connected postgreSQL database to store information of users and activities.
+ Used Flex Messages to customize layout and make it interactive with LINE Messaging API SDK. 

## Flow Chart


## Demo
+ 新增活動 <br/><br/>
&emsp;<img src="/README/group.gif" width=300px/> 
+ 報名活動 <br/><br/>
&emsp;<img src="/README/registration.gif" width=300px/> 
+ 開團紀錄 <br/><br/>
&emsp;<img src="/README/group_record.gif" width=300px/> 
+ 報名紀錄 <br/><br/>
&emsp;<img src="/README/registration_record.gif" width=300px/> 


## Contact
+ Author: Viggo Chang
+ E-mail: <gl4cj8686@gmail.com> 