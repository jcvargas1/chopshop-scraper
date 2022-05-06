# chopshop-scraper

This is a Python program that utilizes the Scrapy web crawling framework in order to scrape an entire *Shopify* based website for all its products and proceeds to monitor the website for **ANY** changes to the products be it stock, price, additions, etc. Only the primary Python file is here and is not displaying the PyEnv and Scrapy environment files. 

## Why?

I created this because my significant other was really into collecting and reselling specific collectible figures and loved to utilize this website to find various different products. The issue was the website does not seem to be built entirely efficient when it comes to organization so it was difficult to see what products were actually new or what products were back in stock. Since this website gets entire collectible figures and parts them out there is around 20,000 items (so far) therefore it was very time consuming for her due to the problems noted. By creating this scraper I have saved my significant other countless hours over the course of more than a year and aided her in always being ahead of everyone for buying low or new stock products.


## Tech Used

**Language/Libraries:** Python

**Services**: MongoDB Atlas (Cloud)

**Tools/Etc.** :  Scrapy, XPath, Requests, PyMongo, Discord Py/API, Bash, PyEnv, Ubuntu (using my own physical server), VS Code

## How it works

The program is ran from Ubuntu server I have located at home. Every hour on the hour the program is triggered by a Cron job and begins scraping the list of specified starter links (which are just categories on the target website). By using response and XPath I first get the total number of pages that there is so the program knows how many pages to traverse for scraping. It then proceeds to crawl every single page and luckily since this website happens to be a *Shopify* based website I can easily add */products.json?limit=200&page=* to my request and immediately have the Json version of the page. The scraper then proceeds to check if the individual products link is located in my Mongo database via a query, if it **IS NOT** located in the database it proceeds to get the specific data I want from the Json file and adds it to my cloud MongoDB collection. If the product **IS** located in my database it proceeds to check if any of the data has changed at all for the product be it stock, price, and items added (each product can have several of the same item in different conditions). If there happens to be any data that has changed it immediately will create an embedded discord message using Discord Py and proceed to send the message via webhook to the proper category in the discord server in addition to updating the correct document in the Mongo database. If any error occurs I get notified via a discord message as well and the issue is auto resolved. The database collection has more than 20,000 documents to date.

## Demo Images

![Channels](https://github.com/jcvargas1/chopshop-scraper/blob/main/chop_ex_images/channels.PNG)


![New Addition](https://github.com/jcvargas1/chopshop-scraper/blob/main/chop_ex_images/new-addition.PNG)


![Back in stock](https://github.com/jcvargas1/chopshop-scraper/blob/main/chop_ex_images/back-in-stock.PNG)


![Price Change](https://github.com/jcvargas1/chopshop-scraper/blob/main/chop_ex_images/price-change.PNG)


![Error Check](https://github.com/jcvargas1/chopshop-scraper/blob/main/chop_ex_images/error-check.PNG)






