import pymongo
from pymongo import MongoClient
import scrapy
import requests
from discord import Webhook, RequestsWebhookAdapter, Embed
from scrapy.crawler import CrawlerProcess
import json

cluster = MongoClient("insert mongo db info here")
db = cluster["chibi_scraper"]
chibiFull = db['chibi_full']

discord_update_notification = ""
webhook = Webhook.from_url(discord_update_notification,
                           adapter=RequestsWebhookAdapter())

discord_new_notification = "insert you discord webhook link here"
webhook_new = Webhook.from_url(
    discord_new_notification, adapter=RequestsWebhookAdapter())

discord_error = "insert you discord webhook link here"
webhook_error = Webhook.from_url(
    discord_error, adapter=RequestsWebhookAdapter())


discord_price = "insert you discord webhook link here"
webhook_price = Webhook.from_url(
    discord_price, adapter=RequestsWebhookAdapter())


class ChibiChopSpider(scrapy.Spider):
    name = 'chibichopshop'
    allowed_domains = ['chibichopshop.com']
    start_urls = [
        'https://chibichopshop.com/collections/good-smile-company']

    def parse(self, response):

        linkCount = 4
        myLinks = ['https://chibichopshop.com/collections/good-smile-company/products.json?limit=200&page=', 'https://chibichopshop.com/collections/nendoroid-cases/products.json?limit=200&page=',
                   'https://chibichopshop.com/collections/other-anime-merch/products.json?limit=200&page=', 'https://chibichopshop.com/collections/nendoroid-dolls/products.json?limit=200&page=']

        for j in range(linkCount):

            original_url = myLinks[j]
            global onWebPage
            onWebPage = original_url

            print("Working on link: " + original_url)

            if j == 1 or j == 2 or j == 3:
                yield scrapy.Request(original_url, self.item_check)

            elif (j == 0):
                num = int(response.xpath(
                    '//*[@id="shopify-section-collection-template"]/div/div[2]/div/span[5]/a/text()').get())

                for i in range(1, num + 1):
                    yield scrapy.Request(original_url + str(i), self.item_check)

    def item_check(self, response):

        jsonresponse = json.loads(response.text)

        # Make link

        for i in range(len(jsonresponse['products'])):
            item_id = jsonresponse['products'][i]['id']
            final_item_link = ""
            item_link_handle = jsonresponse['products'][i]['handle']

            print("Working on: " + str(item_id))

            if onWebPage == "https://chibichopshop.com/collections/good-smile-company/products.json?limit=200&page=":
                final_item_link = "https://chibichopshop.com/collections/good-smile-company/products/" + item_link_handle

            elif onWebPage == "https://chibichopshop.com/collections/nendoroid-cases/products.json?limit=200&page=":
                final_item_link = "https://chibichopshop.com/collections/nendoroid-cases/products/" + item_link_handle

            elif onWebPage == "https://chibichopshop.com/collections/other-anime-merch/products.json?limit=200&page=":
                final_item_link = "https://chibichopshop.com/collections/other-anime-merch/products/" + item_link_handle

            elif onWebPage == "https://chibichopshop.com/collections/nendoroid-dolls/products.json?limit=200&page=":
                final_item_link = "https://chibichopshop.com/collections/nendoroid-dolls/products/" + item_link_handle

            # Checks if the current item has a valid Url if not then adds it
            if chibiFull.count_documents({"_id": item_id, "URL": {"$exists": False}}) == 1:
                chibiFull.update_one({"_id": item_id}, {
                    "$set": {"URL": final_item_link}})
                print("Adding URL to: " + final_item_link)

            if chibiFull.count_documents({"_id": item_id}) == 0:
                item_name = jsonresponse['products'][i]['title']

                try:
                    image_link = jsonresponse['products'][i]['images'][0]['src']
                except:
                    print("\nNo image Available for " + item_name)
                    image_link = "N/A"

                var_dict = []
                discord_info = []

                for j in range(len(jsonresponse['products'][i]['variants'])):
                    variant_name = jsonresponse['products'][i]['variants'][j]['title']
                    variant_id = jsonresponse['products'][i]['variants'][j]['id']
                    variant_avail = jsonresponse['products'][i]['variants'][j]['available']
                    variant_price = jsonresponse['products'][i]['variants'][j]['price']
                    someDict = {"id": variant_id, "variant_name": variant_name,
                                "available": variant_avail, "price": variant_price}
                    discord_info.append(
                        "\n[ Condition: " + variant_name + " | Price: $" + variant_price + " ]")
                    var_dict.append(someDict)

                print("\n Adding: " + str(item_name))
                chibiFull.insert_one(
                    {"_id": item_id, "name": item_name, "URL": final_item_link, "image_link": image_link, "variants": var_dict})

                conditionPrices = ''.join(discord_info)
                embed_new = Embed(title="**New Item Added!**", color=0x70ACC3,
                                  description=f"[{item_name}]({final_item_link})")
                embed_new.add_field(
                    name="Condition & Price", value=conditionPrices)
                if image_link != "N/A":
                    embed_new.set_image(url=image_link)

                webhook_new.send(embed=embed_new)

            elif chibiFull.count_documents({"_id": item_id}) == 1:
                itemSearch = chibiFull.find({"_id": {"$eq": item_id}})

                for item in itemSearch:

                    for num in range(len(item["variants"])):
                        error_flag = 0

                        # Check if items are back in stock
                        try:
                            error_flag = 1
                            if item["variants"][num]["available"] == False and jsonresponse['products'][i]['variants'][num]['available'] == True:
                                print("\nUpdating available from False to True for variant " +
                                      str(num) + "\nURL: " + item["URL"])
                                arraypos = (
                                    "variants." + str(num) + ".available")
                                chibiFull.update_one({"_id": item_id}, {
                                    "$set": {arraypos: True}})
                                condition = jsonresponse['products'][i]['variants'][num]['title']
                                itemPrice = jsonresponse['products'][i]['variants'][num]['price']

                                # Discord embed for item back in stock
                                stockItemName = item["name"]
                                embed_stock = Embed(title="**Item Back in Stock!**", color=0x70ACC3,
                                                    description=f"[{stockItemName}]({final_item_link})")
                                embed_stock.add_field(name="Condition", value=str(
                                    condition + ": " + itemPrice))
                                if item["URL"] != "N/A":
                                    embed_stock.set_image(
                                        url=item["image_link"])

                                webhook.send(embed=embed_stock)

                            elif item["variants"][num]["available"] == True and jsonresponse['products'][i]['variants'][num]['available'] == False:
                                print("\nUpdating available from True to False for variant " +
                                      str(num) + "\nURL: <" + item["URL"] + ">")
                                arraypos2 = (
                                    "variants." + str(num) + ".available")
                                chibiFull.update_one({"_id": item_id}, {
                                    "$set": {arraypos2: False}})

                            # Check if price changes
                            error_flag = 2
                            if item["variants"][num]["price"] != jsonresponse['products'][i]['variants'][num]['price']:
                                print("\nUpdating price for variant " +
                                      str(num) + "\nURL: " + item["URL"])
                                arraypos3 = ("variants." + str(num) + ".price")
                                newPrice = jsonresponse['products'][i]['variants'][num]['price']
                                condition = jsonresponse['products'][i]['variants'][num]['title']

                                print(
                                    "\n\nPrice change from: " + item["variants"][num]["price"] + " to: " + newPrice)

                                # Create discord embedded message
                                priceItemName = item["name"]
                                embed_price = Embed(title="**Price Change!**", color=0x70ACC3,
                                                    description=f"[{priceItemName}]({final_item_link})")
                                embed_price.add_field(name="Old Price & Condition", value=str(
                                    condition + ": $" + item["variants"][num]["price"]))
                                embed_price.add_field(
                                    name="New Price", value="$" + str(newPrice))

                                if float(newPrice) > float(item["variants"][num]["price"]):
                                    oldPrice = float(
                                        item["variants"][num]["price"])
                                    currentPrice = float(newPrice) - oldPrice
                                    pricePercentageDiff = (
                                        (float(newPrice) - oldPrice) / oldPrice) * 100
                                    embed_price.add_field(
                                        name="\nThe Price Has Gone Up", value=f"Up ${currentPrice} which is {pricePercentageDiff:.2f}% more.")

                                elif float(newPrice) < float(item["variants"][num]["price"]):
                                    oldPrice = float(
                                        item["variants"][num]["price"])
                                    currentPrice = oldPrice - float(newPrice)
                                    pricePercentageDiff = (
                                        (oldPrice - float(newPrice)) / oldPrice) * 100
                                    embed_price.add_field(
                                        name="\nThe Price Has Gone Down", value=f"Down ${currentPrice} which is {pricePercentageDiff:.2f}% off")

                                if item["URL"] != "N/A":
                                    embed_price.set_image(
                                        url=item["image_link"])

                                webhook_price.send(embed=embed_price)

                                chibiFull.update_one({"_id": item_id}, {
                                    "$set": {arraypos3: newPrice}})

                            if item["image_link"] != 'N/A':
                                if item["image_link"] != jsonresponse['products'][i]['images'][0]['src']:
                                    print("\nUpdating available from True to False for variant " +
                                          str(num) + "\nURL: <" + item["URL"] + ">")
                                    new_image_link = jsonresponse['products'][i]['images'][0]['src']
                                    chibiFull.update_one({"_id": item_id}, {
                                        "$set": {"image_link": new_image_link}})
                        except:
                            if error_flag == 1:
                                webhook_error.send(
                                    "\nError with " + item["name"] + "\nID: " + str(item_id) + "\nIssue with current count of variants and json response count")

                                # Remove item if it has an error with variants so it can redo it
                                print("\nRemoved: " + item["name"] + "\n")
                                chibiFull.delete_one({"_id": item_id})

                            elif error_flag == 2:
                                webhook_error.send(
                                    "\nError with " + item["name"] + "\nID: " + str(item_id) + "\nIssue with checking price changes")


process = CrawlerProcess()
process.crawl(ChibiChopSpider)
process.start()
