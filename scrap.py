# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import datetime


# Send a GET request to the website and parse the HTML content
get = requests.get(
    "https://answersq.com/udemy-paid-courses-for-free-with-certificate/")
soup = BeautifulSoup(get.content, "html.parser")
ul_ele = soup.find_all("ul", class_="wp-block-list")


def get_course(keyword: str) -> dict:
    """
    Searches for courses containing the specified keyword in their titles.
    Args:
        keyword (str): The keyword to search for in course titles.
    Returns:
        dict: A dictionary where the keys are course titles containing the
        keyword, and the values are the corresponding URLs.
    """
    ret = {}
    for ul in ul_ele:
        for li_ele in ul.find_all("li"):
            for i in li_ele.find_all("a"):
                got = str(i.text)
                if keyword in got.lower():
                    ret[got] = i.get("href")

    return ret


if __name__ == "__main__":
    data = get_course("")
    with open("courses.md", "w") as f:
        # write in dd/mm/yyyy format
        f.write(
            f"## Courses Updated "
            f"{datetime.datetime.now().strftime('%d/%m/%Y')}\n"
        )
        for course, url in data.items():
            f.write(f"- [{course}]({url})\n")
