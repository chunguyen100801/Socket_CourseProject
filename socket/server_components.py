# File bao gồm các thành phần thuộc server, luôn đi kèm với server.py

import pip._vendor.requests as requests
import json
from datetime import datetime
from dateutil.parser import parse

'''
CÁC GIÁ TRỊ MẶC ĐỊNH, KHÔNG ĐƯỢC THAY ĐỔI
'''
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Mzk2NDgwMDcsImlhdCI6MTYzODM1MjAwNywic2NvcGUiOiJleGNoYW5nZV9yYXRlIiwicGVybWlzc2lvbiI6MH0.-olG9A8hV20ojuW62TKwgyVXs5xAby_hBGFq-FvrTVw'
url = 'https://vapi.vnappmob.com/api/v2/exchange_rate/vcb'
params = {'api_key': key}
headers = {'Accept': 'application/json'}


def getDataFromAPI():
    '''Lấy data từ api và ghi dữ liệu lấy được vào file data.json'''

    # Lấy data từ api
    response = requests.get(url, params=params, headers=headers)
    
    # Kiểm tra status code
    # status code = 200, server kết nối được tới api, ngược lại thì không
    if (response.status_code != 200):
        return False

    data = response.json()

    # Lấy thời gian hiện tại
    data["date_time"] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    write_json(data)
    return True


def write_json(new_data, filename='data.json'):
    '''Ghi dữ liệu {new_data} vào file data.json'''

    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["exchange_history"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=2)


def find_currency(currency, date):
    '''Tìm dữ liệu {currency} của vào ngày {date} và trả về {exchange_data} kiểu dictionary'''

    #Mở file data.json
    f = open('data.json')
    data = json.load(f)

    exchange_data = {}

    exchange_list = data["exchange_history"]
    length = len(exchange_list)

    for i in range(length):
        if (exchange_list[i]["date_time"].find(date) != -1) and (i == (length - 1)):
            exchange_data = find_currency_helper(currency, exchange_list[i])
            break
        elif exchange_list[i]["date_time"].find(date) != (-1) and exchange_list[i+1]["date_time"].find(date) == -1:
            exchange_data = find_currency_helper(currency, exchange_list[i])
            break

    # print(exchange_data)

    return exchange_data

def find_currency_helper(currency, exchange_list):
    '''Trợ giúp hàm {find_currency}'''
    exchange_data = {}
    for item in exchange_list["results"]:
        if currency == item["currency"]:
            exchange_data = {
                "date_time": exchange_list["date_time"],
                "results": {
                    "currency": item["currency"],
                    "buy_cash": item["buy_cash"],
                    "buy_transfer": item["buy_transfer"],
                    "sell": item["sell"]
                }
            }
            return exchange_data
    return exchange_data


def dictToDataSendClient(dict_data):
    '''Chuyển đổi dictionary {dict_data} sang dạng list cho client {exchange_data_list}'''

    exchange_data_list = []
    exchange_data_list.append("    %s" %dict_data["date_time"])

    currency_data = "     - Currency: %s" % dict_data["results"]["currency"]
    exchange_data_list.append(currency_data)

    buy_cash_data = "     - Buy cash: %s" % dict_data["results"]["buy_cash"]
    exchange_data_list.append(buy_cash_data)

    buy_transfer_data = "     - Buy transfer: %s" % dict_data["results"]["buy_transfer"]
    exchange_data_list.append(buy_transfer_data)

    sell_data = "     - Sell: %s" % dict_data["results"]["sell"]
    exchange_data_list.append(sell_data)

    return exchange_data_list


def saveUserHistory(user_name, new_data, filename='users_history.json'):
    '''
    Lưu dữ liệu user tìm kiếm vào file users_history.json
    Arguments: tên người dùng {user_name}, data người dùng tìm kiếm {new_data} 
    '''
    # Biến check kiểm tra có tồn tại user_name trong users_history.json hay không
    # Nếu có check = True
    check = False
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        users_data = file_data["users_history"]
        for user in users_data:
            if user["name"] == user_name:
                check = True
                user["history"].append(new_data)
                file.seek(0)
                json.dump(file_data, file, indent=2)

        # Không thấy tên người dùng
        # Bắt đầu tạo lịch sử người dùng mới
        if check == False:
            new_user = {
                "name": user_name,
                "history": [
                    new_data
                ]
            }
            users_data.append(new_user)
            file.seek(0)
            json.dump(file_data, file, indent=2)

def findUserHistory(user_name, filename='users_history.json'):
    '''Tìm kiếm lịch sử người dùng thông qua biến {user_name}'''
    history_data = []
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        users_data = file_data["users_history"]
        for user in users_data:
            if user["name"] == user_name:
                history_data = convertUserHistoryData(user["history"])
                
    # print(history_data)
    return history_data

def convertUserHistoryData(user_history_data):
    '''Chuyển đổi {user_history_data} từ kiểu dictionary sang kiểu list'''
    history_data = []
    for item in user_history_data:
        new_data = dictToDataSendClient(item)
        history_data.append(new_data)

    return history_data

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

