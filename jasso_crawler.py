# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

jasso_url = "https://www.sas.jasso.go.jp/ac/HenkanJohoServlet"
df_header = [# 基本項目
             "Name", "PublicOrPrivate", "Area/Prefecture",
             "SchoolClass", "NumStudent",
             "NumBorrower", "NumNewBorrowerH27",
             # H27返還等状況
             "NumExitLendingH22toH26",
             "NumPostponeSchoolH27_ExitLendingH22toH26",
             "NumPostponeGeneralH27_ExitLendingH22toH26",
             "NumReductionH27_ExitLendingH22toH26",
             "NumPaidUpH27_ExitLendingH22toH26",
             "NumDelayedOver1DayH27_ExitLendingH22toH26",
             "RatioDelayedOver1DayH27_ExitLendingH22toH26",
             "NumDelayedOver3MonthsH27_ExitLendingH22toH26",
             "RatioDelayedOver3MonthsH27_ExitLendingH22toH26",
             # 各年度延滞者割合
             "RatioDelayedOver3MonthsH23_ExitLendingH22",
             "RatioDelayedOver3MonthsH24_ExitLendingH23",
             "RatioDelayedOver3MonthsH25_ExitLendingH24",
             "RatioDelayedOver3MonthsH26_ExitLendingH25",
             "RatioDelayedOver3MonthsH27_ExitLendingH26",
             "NumExitLendingH26",
             "NumDelayedOver3MonthsH27_ExitLendingH26",
             # 過去5年間延滞比率推移
             "RatioDelayedOver3MonthsH25_ExitLendingH20toH24",
             "RatioDelayedOver3MonthsH26_ExitLendingH21toH25",
             "NumExitLendingH21toH25",
             "NumDelayedOver3MonthsH26_ExitLendingH21toH25"]

dropdown_menu_ids = ["select-kokosiKbn", "select-sgsGksyuCd",
                     "select-gakoTikiCd", "select-gakoBg"]


def get_num_of_dropdown_item(soup, id):
    return len(soup.find(id=id).find_all("option"))


def data_cleaning(string):
    if "- - -" in string or "***" in string:
        return np.nan

    if string[-1] == "人":
        return int(string[:-2].replace(",", ""))
    elif string[-1] == "％":
        return float(string[:-2]) * 0.01
    else:
        return string


class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.data_list = []

    def __extract_data(self, soup):
        selected_items = [string.strip()
                          for (bool, string)
                          in zip(["selected" in str(x) for x in soup.find_all("option")],
                                 [x.string for x in soup.find_all("option")])
                          if bool]

        table_list = [pd.read_html(str(table)) for table in soup.find_all(class_="content-table")]
        first_table = table_list[0][0]
        data = [# 基本項目
                first_table.ix[0,1], selected_items[0], selected_items[2],
                first_table.ix[0,3], first_table.ix[2,2],
                first_table.ix[2,4], first_table.ix[2,6],
                # H27返還等状況
                first_table.ix[4,2], first_table.ix[4,4], first_table.ix[4,6], first_table.ix[4,8],
                first_table.ix[5,1], first_table.ix[6,1], first_table.ix[6,3], first_table.ix[6,5],
                first_table.ix[6,7],
                # 各年度延滞者割合
                first_table.ix[10,0], first_table.ix[10,1], first_table.ix[10,2],
                first_table.ix[10, 3], first_table.ix[10,4], first_table.ix[10,5], first_table.ix[10,6],
                # 過去5年間延滞比率推移
                first_table.ix[14, 0], first_table.ix[14,1], first_table.ix[14,2], first_table.ix[14,3]
                ]
        return pd.Series(data, index=df_header)

    def select_items(self, level, num):
        if level < 4:
            for i in range(num):
                if i > 0:  # 「未選択」を回避
                    select_dropdown_menu = Select(self.driver.find_element_by_id(dropdown_menu_ids[level]))
                    select_dropdown_menu.select_by_index(i)
                    time.sleep(1) # 負荷軽減
                    if level == 3:
                        driver.find_element_by_id("search-btn").click()  # 「情報抽出」をクリック
                        soup = BeautifulSoup(driver.page_source, "lxml")
                        self.data_list.append(self.__extract_data(soup))
                    else:
                        soup = BeautifulSoup(driver.page_source, "lxml")
                        num_next = get_num_of_dropdown_item(soup, dropdown_menu_ids[level + 1])
                        self.select_items(level+1, num_next)

    def fetch(self):
        soup = BeautifulSoup(driver.page_source, "lxml")
        num0 = get_num_of_dropdown_item(soup, dropdown_menu_ids[0])
        level = 0
        self.select_items(level, num0)

    def to_frame(self):
        return pd.DataFrame(self.data_list).applymap(data_cleaning)


if __name__ == '__main__':
    driver = webdriver.PhantomJS()
    driver.get(jasso_url)
    crawler = Crawler(driver)
    crawler.fetch()
    df = crawler.to_frame()
    df.to_csv("jasso_utf8.csv", index=False)