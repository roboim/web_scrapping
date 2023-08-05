import requests
import lxml
import fake_headers
import time
import unicodedata
from json_files_proc import make_json
from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def question():
    pages = input("\nВведите количество страниц поиска (по 20 вакансий): ")
    try:
        pages = int(pages)
        if pages <= 0:
            quit(100)
        return pages
    except:
        quit(101)

# Нужно выбрать те вакансии, у которых в описании есть ключевые слова "Django" и "Flask".

if __name__ == '__main__':
    test = 0
    time_delay = 0.3
    name_json = "vacancy.json"

    headers_gen = fake_headers.Headers(browser="firefox", os="win")
    num_vac = 0

    link = "https://hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=python+flask+django" \
           "&excluded_text=&area=2&area=1&salary=&currency_code=RUR" \
           "&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20"
    print(f"\nИнтервал между запросами к серверу по каждой вакансии: {time_delay}."
          f"\nИзменил запрос с 'python' на 'python+flask+django',для большего количества результатов,"
          f"\nно проверка ключевых навыков проводится. ")

    page_list = question()

    page=0
    while page <= page_list-1:
        search_link = link + "&page=" + str(page)
        response = requests.get(search_link, headers=headers_gen.generate())
        html_data = response.text

        hhru_main = BeautifulSoup(html_data, "lxml")

        vacancy_list_tag = hhru_main.find('div', id="a11y-main-content")
        vacancy_tags = vacancy_list_tag.find_all('div', class_="serp-item")


        vacancy_parsed = []
        for vacancy_tag in vacancy_tags:

            header_tag = vacancy_tag.find("h3")
            header_span = header_tag.find("a")
            href_tag = header_span.get("href")

            header_text = header_tag.text

            vacancy_response = requests.get(href_tag, headers=headers_gen.generate())
            vacancy = BeautifulSoup(vacancy_response.text, "lxml")

            vacancy_title_tag = vacancy.find("div", class_="vacancy-title")
            try:
                salary_tag = vacancy_title_tag.find("span", class_="bloko-header-section-2 bloko-header-section-2_lite")

                try:
                    salary = salary_tag.text
                    salary = unicodedata.normalize("NFKD", salary)
                except:
                    salary = ""
            except:
                pass

            skill_tags = vacancy.find("div",class_="bloko-tag-list")

            skills = []
            try:
                skill_els = skill_tags.find_all("span", class_="bloko-tag__section bloko-tag__section_text")
                for skill_el in skill_els:
                    s = str(skill_el.text).lower()
                    skills.append(s)
            except:
                pass

            if skills.count("django") > 0 and skills.count("flask") > 0:

                city_tag = vacancy.find('span', attrs={"data-qa": "vacancy-view-raw-address"})
                try:
                    city = city_tag.text
                    city = city.split(',')[0]
                except:
                    city = ""

                name_company_tag = vacancy.find('span', class_ ="vacancy-company-name")
                name_company = name_company_tag.find('span', class_ ="bloko-header-section-2 bloko-header-section-2_lite")
                try:
                    company = name_company.text
                    company = unicodedata.normalize("NFKD", company)
                except:
                    company = ""
                # Записать в json информацию о каждой вакансии - ссылка, вилка зп, название компании, город.
                vacancy_parsed.append(
                    {
                        "href": href_tag,
                        "salary": salary,
                        "company": company,
                        "city": city,
                        "header": header_text,
                        #"skills": skills,
                    }
                )
            num_vac += 1
            print(f"Обработано вакансий:{num_vac}")
            time.sleep(time_delay)

            if test == 1:
                if num_vac >= 3:
                    make_json(vacancy_parsed, name_json)
                    quit(999)

        page += 1

    make_json(vacancy_parsed, name_json)