def scrap_data():
    import httpx
    from bs4 import BeautifulSoup


    with httpx.Client() as client:
        vacancy_categories_res = client.get("https://jobs.dou.ua/")
        csrf_token = vacancy_categories_res.cookies["csrftoken"]

        soap = BeautifulSoup(vacancy_categories_res.text, "html.parser")

        for a_tag in soap.select("a.cat-link[href]"):
            api_url = a_tag["href"].replace("?", "xhr-load/?")
            data = {"csrfmiddlewaretoken": csrf_token, "count": 0}

            while True:
                vacancies_data = client.post(
                    api_url,
                    headers={"Referer": api_url},
                    data=data
                ).json()

                vacancy_soap = BeautifulSoup(vacancies_data["html"], "html.parser")
                vacancy_blocks = vacancy_soap.select("li.l-vacancy")

                for block in vacancy_blocks:
                    vacancy_title = block.select_one("a.vt")

                    name = vacancy_title.text.strip()
                    url = vacancy_title["href"].strip()
                    company = block.select_one("strong > a").text.strip()
                    date = block.select_one("div.date").text.strip()

                if len(vacancy_blocks) < vacancies_data["num"]:
                    break
                else:
                    data["count"] += vacancies_data["num"]



scrap_data()