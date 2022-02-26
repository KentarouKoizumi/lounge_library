import requests
import json


def search_book(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

    isbn = str(isbn)

    res = requests.get(url + isbn)

    data = json.loads(res.text)

    if int(data["totalItems"]) != 0:
        ret = {"title" : data["items"][0]["volumeInfo"]["title"], "authors": ["Undefined"], "ISBN": isbn}
        if "authors" in data["items"][0]["volumeInfo"]:
            ret["authors"] = data["items"][0]["volumeInfo"]["authors"]
        return ret
    else:
        return False

if __name__ == "__main__":
    print(search_book(input("ISBNを数字だけ，ハイフン抜きで入力：\n")))