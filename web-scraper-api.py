import requests
import json
import os
import urllib.parse
import re
import time
from PIL import Image
from io import BytesIO
import numpy as np
# import pandas as pd
from deepface import DeepFace
from retinaface import RetinaFace
# from TextTron.TextTron import TextTron
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
# from google_images_search import GoogleImagesSearch
from selenium import webdriver

driver = webdriver.Chrome("E:/Officefield/Analytics/Face scrapping/chromedriver.exe")

# Get all symbols from API
def getSymbols():
    url = "https://dev-api.traderverse.io/analytics/list_stocks"
    payload = json.dumps({
        "key": "L2ykq39NTxeQ84yr",
        "market": "NYSE"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    symbols_json = response.json()

    symbols_list = []
    for index in range(len(symbols_json["records"])):
        symbols_list.append(symbols_json["records"][index]["symbol"])

    return symbols_list

# Function to remve name prefix
def removeNameTittle(name):
    prefix = ["Ms", "MS", "Mrs", "MRS", "Mr", "MR", "DR", "Dr", "Prof", "Ms.", "MS.", "Mrs.", "MRS.", "Mr.", "MR.", "DR.", "Dr.", "Prof."]
    
    person_split = name.split(" ")
    if person_split[0] in prefix:
        person_split.remove(person_split[0])
    name = " ".join(person_split)
    return name

# Get companies executive name from API
def getCompanyAndExecutiveNames(symbol):
    url = "https://dev-api.traderverse.io/source/main_fundamentals"
    payload = json.dumps({
    "symbol": symbol,
    "key": "L2ykq39NTxeQ84yr"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    
    jsonObj = response.json()
    company = jsonObj["fundamentals"]["General"]["Name"]
    officers = jsonObj["fundamentals"]["General"]["Officers"]
    officers_name_title = []
    for key in officers:
        name = officers[key]["Name"]
        title = officers[key]["Title"]
        officers_name_title.append([name, title])
    return (company, officers_name_title)

# Function to get executive images of company (list of companies symbols are required as parameters)
def getImages(symbols_list):
    for symbol in symbols_list:
        start_time = time.time()
        company_officer_tuple =  getCompanyAndExecutiveNames(symbol)
        company = company_officer_tuple[0]
        officers_list = company_officer_tuple[1]

        images_dict = {
            company: {
                "Executives": []
            } 
        }

        # Name loop
        for i, name_title in enumerate(officers_list):
            driver.get("https://www.google.com/search?q=" + removeNameTittle(name_title[0]).replace(" ", "+") + " " + company)
            driver.find_element_by_xpath("//a[text()='Images']").click()
            image_divs = driver.find_elements_by_xpath("//div[@id='islrg']/div/div")
            image_name = name_title[0].replace(".", "").replace("  ", " ")
            images_dict[company]["Executives"].append({
                            "Name": name_title[0].replace("'", "").replace('"', ""),
                            "Images": []
                        })
            total_images = driver.find_elements_by_xpath("//div[@id='islrg']/div/div")
            if len(total_images) >= 10:
                loop_range = 10
            else:
                loop_range = (len(total_images) - 1)
            for j in range(loop_range):
                try:
                    driver.find_element_by_xpath("//div[@id='islrg']/div/div[" + str(j+1) + "]/a[1]").click()
                except:
                    print("Caanot find image element: " + "//div[@id='islrg']/div/div[" + str(j+1) + "]/a[1]")
                    continue
                raw_url = driver.find_element_by_xpath("//div[@id='islrg']/div/div[" + str(j+1) + "]/a[1]").get_attribute('href')
                image_url = re.search('imgurl=(.*)&imgrefurl', urllib.parse.unquote(raw_url))
                image_url = image_url.group(1)
                if len(image_url.split(".jpg")) > 1:
                    image_url = (image_url.split(".jpg")[0] + ".jpg")
                elif len(image_url.split(".png")) > 1:
                    image_url = (image_url.split(".png")[0] + ".png")
                
                images_dict[company]["Executives"][i]["Images"].append(image_url)

        # Verify Gender of image with name prefix
        for i in range(len(images_dict[company]["Executives"])):
            print("##########################################")
            name = images_dict[company]["Executives"][i]["Name"]
            if name.split(".")[0] == "Mr":
                name_gender = "Man"
            elif name.split(".")[0] == "Ms":
                name_gender = "Woman"
            else:
                name_gender = "None"
            print("Name: " + name)
            images_dict[company]["Executives"][i]["Images File"] = []
            for url in images_dict[company]["Executives"][i]["Images"]:
                print("Url:", url)
                try:
                    response = requests.get(url, timeout=10)
                except requests.exceptions.Timeout:
                    response = requests.get(url, timeout=10)
                except:
                    print("Cannot open image url:", url)
                    images_dict[company]["Executives"][i]["Images"].remove(url)
                    continue
                print("A")
                try:
                    img = Image.open(BytesIO(response.content)).convert('RGB')
                except Exception as e:
                    print(e)
                    images_dict[company]["Executives"][i]["Images"].remove(url)
                    continue
                print("B")
                text = pytesseract.image_to_string(np.array(img))
                print("C")
                if len(text.replace("\n", "")) < 20:
                    faces = RetinaFace.extract_faces(np.array(img))
                    print("D")
                    if len(faces) == 1:
                        try:
                            result = DeepFace.analyze(np.array(img), actions = ['gender'])
                            print("E")
                            if name_gender != "None":
                                if result["gender"] == name_gender:
                                    images_dict[company]["Executives"][i]["Images File"].append({url: img})
                                else:
                                    print("Invalid")
                                    images_dict[company]["Executives"][i]["Images"].remove(url)
                                    continue
                        except Exception as e:
                            if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
                                print("No Face detected for img:", url)
                                images_dict[company]["Executives"][i]["Images"].remove(url)
                                continue
                            else:
                                print(str(e))
                                continue
                    else:
                        print("No face or multiple faces detected")
                        images_dict[company]["Executives"][i]["Images"].remove(url)
                        continue
                else:
                    print("Text detected with lenght > 20")
                    print("Text:", text.replace("\n", ""))
                    images_dict[company]["Executives"][i]["Images"].remove(url)
                    continue
        # Compare images to get most matched image

        # recursive function for trying again due to request timeout
        def recursive_funct(multi_list):
            try:
                for url1 in multi_list:
                    url1_key = list(url1.keys())[0]
                    images_dict[company]["Executives"][i]["Compare"][url1_key] = []
                    img1 = url1[url1_key]
                    for url2 in multi_list:
                        url2_key = list(url2.keys())[0]
                        if url1_key != url2_key:
                                img2 = url2[url2_key]
                                try:
                                    result = DeepFace.verify(np.array(img1), np.array(img2))
                                    print("F")
                                except Exception as e:
                                    if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
                                        print("No Face detected")
                                        continue
                                print(result["verified"])
                                if result["verified"]:
                                    images_dict[company]["Executives"][i]["Compare"][url1_key].append(url2_key)
            except:
                for url1 in multi_list:
                    url1_key = list(url1.keys())[0]
                    images_dict[company]["Executives"][i]["Compare"][url1_key] = []
                    img1 = url1[url1_key]
                    for url2 in multi_list:
                        url2_key = list(url2.keys())[0]
                        if url1_key != url2_key:
                                img2 = url2[url2_key]
                                try:
                                    result = DeepFace.verify(np.array(img1), np.array(img2))
                                    print("G")
                                except Exception as e:
                                    if str(e) == "Face could not be detected. Please confirm that the picture is a face photo or consider to set enforce_detection param to False.":
                                        print("No Face detected")
                                        continue
                                print(result["verified"])
                                if result["verified"]:
                                    images_dict[company]["Executives"][i]["Compare"][url1_key].append(url2_key)

        for i in range(len(images_dict[company]["Executives"])):
            print("##########################################")
            images_dict[company]["Executives"][i]["Compare"] = {}
            try:
                recursive_funct(images_dict[company]["Executives"][i]["Images File"])
                print("H")
            except:
                print("Error in recursive function")
                continue
        
        # Get most matched image
        best_images = []
        for i in range(len(images_dict[company]["Executives"])):
            if len(images_dict[company]["Executives"][i]["Compare"]) > 0:
                maxi = max(len(images_dict[company]["Executives"][i]["Compare"][x]) for x in images_dict[company]["Executives"][i]["Compare"])
                images_res = []
                for item in images_dict[company]["Executives"][i]["Compare"]:
                    if len(images_dict[company]["Executives"][i]["Compare"][item]) == maxi and len(images_dict[company]["Executives"][i]["Compare"][item]) > 0:
                        try:
                            response = requests.get(item, timeout=10)
                            img = Image.open(BytesIO(response.content)).convert('RGB')
                            images_res.append([images_dict[company]["Executives"][i]["Name"], item, img.size])
                        except requests.exceptions.Timeout:
                            response = requests.get(url, timeout=10)
                        except:
                            print("Continue")
                            continue
                if len(images_res) > 0:
                    best_images.append(images_res)

        # Create company directory
        dir = "E:/Officefield/Analytics/Face scrapping/Custom Automation Images/" + symbol
        
        try:
            os.mkdir(dir)
        except:
            pass
        
        # Save highest resolution image
        for img in best_images:
            for item in img:
                # if (item[2][0] + item[2][1]) == max((y[2][0] + y[2][1]) for y in img): # check for combined max (width + height)
                if item[2][1] == max(y[2][1] for y in img): # check only for max height
                    try:
                        response = requests.get(item[1], timeout=10)
                    except requests.exceptions.Timeout:
                        response = requests.get(url, timeout=10)
                    final_image = Image.open(BytesIO(response.content)).convert('RGB')
                    final_image.save(dir + "/" + item[0] + ".jpg")
                    end_time = time.time()
                    print("Total Time for " + str(symbol) + " is: " + str(end_time - start_time))
                    break

if __name__ == "__main__":
    # getImages(getSymbols()[24:])
    symbols_list = ['VZ', 'TXN', 'COP', 'ADBE', 'UPS', 'CMCSA', 'AMGN', 'CRM', 'FMX', 'MS', 'TTE', 'PM', 'SCHW', 'HON', 'QCOM', 'RTX', 'TBC', 'TBB', 'RY', 'T', 'IBM', 'DE', 'SAP', 'GS', 'CVS', 'LOW', 'UNP', 'NFLX', 'HDB', 'LMT', 'CAT', 'AMD', 'UL', 'INTC', 'ELV', 'TD', 'HSBC', 'AXP', 'BUD', 'SNY', 'EQNR', 'SPGI', 'SBUX', 'BLK', 'ADP', 'BP', 'GILD', 'INTU', 'BX']
    getImages(symbols_list)