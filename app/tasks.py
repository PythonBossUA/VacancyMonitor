import logging
import httpx
from datetime import date as datetime_date
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from django.db import IntegrityError, DatabaseError, transaction
from app.models import Company, Vacancy

logger = logging.getLogger(__name__)


MONTHS = {
    "січня": 1,
    "лютого": 2,
    "березня": 3,
    "квітня": 4,
    "травня": 5,
    "червня": 6,
    "липня": 7,
    "серпня": 8,
    "вересня": 9,
    "жовтня": 10,
    "листопада": 11,
    "грудня": 12,
}


def scrap_data():
    current_year = datetime_date.today().year

    client = httpx.Client(timeout=30.0, follow_redirects=True)

    with transaction.atomic():
        Vacancy.objects.all().delete()
        Company.objects.all().delete()

        try:
            try:
                vacancy_categories_res = client.get("https://jobs.dou.ua/")
                vacancy_categories_res.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP помилка при завантаженні головної сторінки: {e.response.status_code}"
                )
                return
            except httpx.RequestError as e:
                logger.error(f"Помилка мережі при завантаженні головної сторінки: {e}")
                return

            csrf_token = vacancy_categories_res.cookies.get("csrftoken")
            if not csrf_token:
                logger.error("Не вдалося отримати CSRF токен з cookies")
                return

            soap = BeautifulSoup(vacancy_categories_res.text, "html.parser")

            for a_tag in soap.select("a.cat-link[href]"):
                api_url = a_tag["href"].replace("?", "xhr-load/?")

                category = (
                    parse_qs(
                        urlparse(api_url).query
                    ).get("category")
                )
                if isinstance(category, list):
                    category = category[0]

                data = {"csrfmiddlewaretoken": csrf_token, "count": 0}

                logger.info(f"Початок парсингу категорії: {api_url}")

                while True:
                    try:
                        response = client.post(
                            api_url, headers={"Referer": api_url}, data=data
                        )
                        response.raise_for_status()
                        vacancies_data = response.json()
                    except httpx.HTTPStatusError as e:
                        logger.error(
                            f"HTTP помилка для {api_url}: {e.response.status_code}"
                        )
                        break
                    except httpx.RequestError as e:
                        logger.error(f"Помилка мережі для {api_url}: {e}")
                        break
                    except ValueError as e:
                        logger.error(f"Невалідний JSON для {api_url}: {e}")
                        break

                    try:
                        html_content = vacancies_data.get("html", "")
                        if not html_content:
                            logger.warning(f"Порожній HTML для {api_url}")
                            break

                        vacancy_soap = BeautifulSoup(html_content, "html.parser")
                        vacancy_blocks = vacancy_soap.select("li.l-vacancy")
                    except Exception as e:
                        logger.error(f"Помилка парсингу HTML для {api_url}: {e}")
                        break

                    vacancies_objects = []

                    for block in vacancy_blocks:
                        try:
                            vacancy_title = block.select_one("a.vt")
                            if not vacancy_title:
                                logger.warning(
                                    "Знайдено блок без заголовка вакансії, пропущено"
                                )
                                continue

                            name = vacancy_title.text.strip()
                            url = vacancy_title["href"].strip().rsplit("?")[0]

                            company_el = block.select_one("strong > a")
                            company = (
                                company_el.text.strip() if company_el else "Unknown"
                            )

                            raw_date_el = block.select_one("div.date")
                            raw_date = raw_date_el.text.strip() if raw_date_el else ""

                            day, _, month = raw_date.partition(" ")
                            date = datetime_date(year=current_year, month=MONTHS[month], day=int(day))

                            if not name or not url:
                                logger.warning(
                                    f"Пропущено вакансію: відсутнє ім'я або URL"
                                )
                                continue

                            company_object, created = Company.objects.get_or_create(
                                name=company
                            )
                            if created:
                                logger.debug(f"Створено нову компанію: {company}")

                            vacancies_objects.append(
                                Vacancy(
                                    name=name,
                                    url=url,
                                    company=company_object,
                                    publication_date=date,
                                    category=category
                                )
                            )

                        except Exception as e:
                            logger.error(f"Помилка обробки блоку вакансії: {e}")
                            continue

                    try:
                        if vacancies_objects:
                            Vacancy.objects.bulk_create(
                                vacancies_objects, ignore_conflicts=True
                            )
                            logger.info(
                                f"Збережено {len(vacancies_objects)} вакансій для {api_url}"
                            )
                    except (IntegrityError, DatabaseError) as e:
                        logger.error(f"Помилка бази даних при збереженні: {e}")
                    except Exception as e:
                        logger.error(f"Непередбачувана помилка при збереженні: {e}")

                    if vacancies_data.get("last"):
                        break
                    else:
                        data["count"] += vacancies_data.get("num", 0)

        except Exception as e:
            logger.exception(f"Критична помилка в scrap_data: {e}")
        finally:
            client.close()

scrap_data()