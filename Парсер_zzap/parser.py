import os
import time
import pandas as pd
import xml.etree.ElementTree as ET
import json
from collections import Counter
import random
import requests
from requests.adapters import HTTPAdapter
import ssl
import urllib3
import certifi

print("[DEBUG] Запущен улучшенный zzap_api_client с полным охватом поиска")
print(">>> ИСПРАВЛЕНЫ ПРОБЛЕМЫ С ПАГИНАЦИЕЙ И ПОИСКОМ <<<")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



# Создаем класс адаптера с более гибкими настройками SSL
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # Создаем контекст SSL, который принимает более широкий набор шифров
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.set_ciphers('DEFAULT@SECLEVEL=1')  # Снижаем уровень безопасности для совместимости
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)



TYPE_SEARCH_DESC = {
    10: "Запрошенный номер (спецпредложения)",
    13: "Запрошенный номер",
    21: "Замены (спецпредложения)",
    31: "Замены",
    50: "Запрошенный номер (недостоверные предложения)",
    34: "Деталь, как составляющие",
    54: "Детали, как составляющие (недостоверные предложения)",
    14: "Запрошенный номер б/у и уценка",
    15: "Результат поиска по б/у и уценка"
}


class ZZapAPIClient:
    BASE_URL = "https://api.zzap.pro/webservice/datasharing.asmx"

    def __init__(self, token: str):
        self.token = token
        self.session = self._create_robust_session()

    def _create_robust_session(self):
        """Создает сессию с устойчивыми настройками."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

        # Используем SSL-адаптер
        adapter = SSLAdapter()
        session.mount("https://", adapter)
        session.verify = certifi.where()
        return session

    def _make_request_with_retries(self, url: str, payload: dict, max_retries: int = 5) -> dict:
        """Выполняется запрос с обработкой ошибок и повторами."""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = min(10 * (attempt + 1), 60)
                    print(f"    [ПОВТОР {attempt + 1}] Ждем {delay}с...")
                    time.sleep(delay)
                else:
                    time.sleep(random.randint(2, 5))

                response = self.session.post(url, data=payload, timeout=90)

                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.text)
                        data = json.loads(root.text)
                        return data
                    except Exception as parse_error:
                        print(f"    [ПАРСИНГ] Ошибка парсинга ответа: {parse_error}")
                        continue
                elif response.status_code == 429:
                    print(f"    [ЛИМИТ] Превышен лимит запросов, ждем 3 минуты...")
                    time.sleep(180)
                    continue
                elif response.status_code in [522, 524, 502, 503, 504]:
                    print(f"    [СЕРВЕР] Ошибка сервера {response.status_code}")
                    continue
                else:
                    print(f"    [HTTP] Ошибка {response.status_code}: {response.text}")
                    continue

            except requests.exceptions.ReadTimeout:
                print(f"    [ТАЙМАУТ] Попытка {attempt + 1} - таймаут чтения")
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"    [СОЕДИНЕНИЕ] Попытка {attempt + 1} - ошибка соединения: {e}")
                continue
            except Exception as e:
                print(f"    [ИСКЛЮЧЕНИЕ] Попытка {attempt + 1} - {e}")
                continue

        print(f"    [ПРОВАЛ] Все {max_retries} попыток неудачны")
        return {}

    def _comprehensive_light_search(self, article_number: str, class_man: str = "", search_text: str = None) -> list:
        """ИСПРАВЛЕННЫЙ поиск через GetSearchResultLight с правильной пагинацией"""
        all_items = []
        type_requests = ["0", "4"]  # 0-все предложения, 4-любые
        for type_request in type_requests:
            print(f"  [LIGHT] type_request={type_request}")
            row_start = 0
            max_per_request = 500
            max_pages = 20
            for page in range(max_pages):
                url = f"{self.BASE_URL}/GetSearchResultLight"
                payload = {
                    "login": "", "password": "",
                    "partnumber": article_number,
                    "search_text": search_text if search_text else article_number,
                    "class_man": class_man,
                    "row_count": str(max_per_request),
                    "row_start": str(row_start),
                    "type_request": type_request,
                    "code_region": "0", "api_key": self.token
                }
                try:
                    data = self._make_request_with_retries(url, payload)
                    if not data or data.get("error"):
                        if data.get("error"): print(f"    [LIGHT] API ошибка: {data['error']}")
                        break

                    items = data.get("table", [])
                    if not items:
                        print(f"    [LIGHT] type_request={type_request}, страница {page + 1}: нет результатов")
                        break

                    all_items.extend(items)
                    print(f"    [LIGHT] type_request={type_request}, страница {page + 1}: +{len(items)} предложений")

                    if len(items) < max_per_request:
                        print(f"    [LIGHT] type_request={type_request}: достигнута последняя страница")
                        break
                    row_start += max_per_request
                except Exception as e:
                    print(f"    [LIGHT] Критическая ошибка на странице {page + 1}: {e}")
                    break
        return all_items

    def _comprehensive_v3_search(self, article_number: str, class_man: str = "", search_text: str = None) -> list:
        """ИСПРАВЛЕННЫЙ поиск через GetSearchResultV3 с правильной пагинацией"""
        all_items = []
        type_requests = [0, 4]  # 0-все предложения, 4-любые
        for type_request in type_requests:
            print(f"  [V3] type_request={type_request}")
            row_start = 0
            max_per_request = 500
            max_pages = 20
            for page in range(max_pages):
                url = f"{self.BASE_URL}/GetSearchResultV3"
                payload = {
                    "login": "", "password": "",
                    "partnumber": article_number,
                    "search_text": search_text if search_text else article_number,
                    "class_man": class_man,
                    "row_count": str(max_per_request),
                    "row_start": str(row_start),
                    "type_request": str(type_request),
                    "code_region": "0", "api_key": self.token
                }
                try:
                    data = self._make_request_with_retries(url, payload)
                    if not data or data.get("error"):
                        if data.get("error"): print(f"    [V3] API ошибка: {data['error']}")
                        break

                    items = data.get("table", [])
                    if not items:
                        print(f"    [V3] type_request={type_request}, страница {page + 1}: нет результатов")
                        break

                    all_items.extend(items)
                    print(f"    [V3] type_request={type_request}, страница {page + 1}: +{len(items)} предложений")

                    if len(items) < max_per_request:
                        print(f"    [V3] type_request={type_request}: достигнута последняя страница")
                        break
                    row_start += max_per_request
                except Exception as e:
                    print(f"    [V3] Критическая ошибка на странице {page + 1}: {e}")
                    break
        return all_items

    def get_search_suggest_comprehensive(self, article_number: str) -> list:
        """УЛУЧШЕННЫЙ поиск через подсказки с пагинацией"""
        all_suggestions = []
        type_requests = ["0", "1", "2"]
        for type_request in type_requests:
            print(f"  [ПОДСКАЗКИ] type_request={type_request}")
            url = f"{self.BASE_URL}/GetSearchSuggestV3"
            payload = {
                "login": "", "password": "",
                "search_text": article_number,
                "type_request": type_request,
                "row_count": "100", "row_start": "0",
                "api_key": self.token
            }
            try:
                data = self._make_request_with_retries(url, payload, max_retries=2)
                if data and not data.get("error"):
                    suggestions = data.get("table", [])
                    if suggestions:
                        all_suggestions.extend(suggestions)
                        print(f"    [ПОДСКАЗКИ] type_request={type_request}: +{len(suggestions)}")
            except Exception as e:
                print(f"    [ПОДСКАЗКИ] Ошибка: {e}")
        return all_suggestions

    def _search_alternatives(self, article_number: str, class_man: str = "") -> list:
        """Поиск альтернативных вариантов номера"""
        all_items = []
        alternatives = self._generate_alternative_numbers(article_number)
        for alt_number in alternatives:
            if alt_number.lower() != article_number.lower():
                print(f"  [АЛЬТЕРНАТИВА] Поиск: {alt_number}")
                items = self._single_light_search(alt_number, class_man, "4")
                if items:
                    print(f"    [АЛЬТЕРНАТИВА] {alt_number}: +{len(items)}")
                    all_items.extend(items)
        return all_items

    def _single_light_search(self, article_number: str, class_man: str, type_request: str) -> list:
        """Одиночный поиск через Light без пагинации (для альтернативных номеров)"""
        url = f"{self.BASE_URL}/GetSearchResultLight"
        payload = {
            "login": "", "password": "",
            "partnumber": article_number, "search_text": article_number,
            "class_man": class_man, "row_count": "200",
            "row_start": "0", "type_request": type_request,
            "code_region": "0", "api_key": self.token
        }
        try:
            data = self._make_request_with_retries(url, payload, max_retries=2)
            if data and not data.get("error"):
                return data.get("table", [])
        except Exception as e:
            print(f"    [ОДИНОЧНЫЙ ПОИСК] Ошибка: {e}")
        return []

    def get_comprehensive_search(self, article_number: str, class_man: str = "", search_text: str = None) -> dict:
        """ИСПРАВЛЕННЫЙ комплексный поиск с правильной пагинацией"""
        all_items = []
        seen_keys = set()

        def add_unique_items(items_to_add):
            count = 0
            for item in items_to_add:
                key = self._generate_item_key(item)
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_items.append(item)
                    count += 1
            return count

        print(f"\n{'=' * 80}\n[КОМПЛЕКСНЫЙ ПОИСК] Артикул: {article_number}\n{'=' * 80}")

        print("\n[ЭТАП 1] GetSearchResultLight...")
        light_items = self._comprehensive_light_search(article_number, class_man, search_text)
        added_count = add_unique_items(light_items)
        print(f"[LIGHT] Добавлено {added_count} уникальных предложений")

        print("\n[ЭТАП 2] GetSearchResultV3...")
        v3_items = self._comprehensive_v3_search(article_number, class_man, search_text)
        added_count = add_unique_items(v3_items)
        print(f"[V3] Добавлено новых {added_count} предложений")

        print("\n[ЭТАП 3] Поиск через подсказки...")
        suggestions = self.get_search_suggest_comprehensive(article_number)
        added_count = add_unique_items(suggestions)
        print(f"[ПОДСКАЗКИ] Добавлено новых {added_count} предложений")

        print("\n[ЭТАП 4] Поиск альтернативных вариантов...")
        alt_items = self._search_alternatives(article_number, class_man)
        added_count = add_unique_items(alt_items)
        print(f"[АЛЬТЕРНАТИВЫ] Добавлено новых {added_count} предложений")

        print(f"\n{'=' * 80}\n[ИТОГО] Найдено {len(all_items)} уникальных предложений\n{'=' * 80}")
        self._print_detailed_statistics(all_items)
        return {"articles": all_items}

    def _generate_alternative_numbers(self, article_number: str) -> list:
        """Генерирует альтернативные варианты номера"""
        clean_number = ''.join(filter(str.isalnum, article_number)).upper()
        alternatives = {article_number.upper(), clean_number}
        return list(alternatives)

    def _generate_item_key(self, item: dict) -> tuple:
        """Генерирует уникальный ключ для предложения (кортеж) для большей надежности."""
        return (
            item.get('class_user'), item.get('partnumber'), item.get('class_man'),
            item.get('priceV2'), item.get('descr_delivery'), item.get('location')
        )

    def _print_detailed_statistics(self, items: list):
        if not items:
            print("[СТАТИСТИКА] Предложения не найдены")
            return

        type_counter = Counter(item.get('type_search') for item in items)
        brand_counter = Counter(item.get('class_man') for item in items if item.get('class_man'))
        supplier_counter = Counter(item.get('class_user') for item in items if item.get('class_user'))

        print(f"\n[ДЕТАЛЬНАЯ СТАТИСТИКА]")
        print(f"Всего предложений: {len(items)}")

        print(f"\n[ТИПЫ ПОИСКА]")
        for type_search, count in type_counter.most_common():
            desc = TYPE_SEARCH_DESC.get(int(type_search) if str(type_search).isdigit() else type_search, "Неизвестно")
            print(f"  {type_search} ({desc}): {count}")

        print(f"\n[БРЕНДЫ] (топ 10)")
        for brand, count in brand_counter.most_common(10):
            print(f"  {brand}: {count}")

        print(f"\n[ПОСТАВЩИКИ] (топ 10)")
        for supplier, count in supplier_counter.most_common(10):
            print(f"  {supplier}: {count}")


def process_excel_file(input_path: str, output_path: str, token: str) -> None:
    """Читает articules.xlsx, ищет каждый артикул и сохраняет результат."""
    client = ZZapAPIClient(token)
    print(f"[НАЧАЛО] Обработка файла {input_path}")
    try:
        df = pd.read_excel(input_path)
    except FileNotFoundError:
        print(f"[ОШИБКА] Не удалось найти файл: {input_path}")
        return
    except Exception as e:
        print(f"[ОШИБКА] Не удалось открыть {input_path}: {e}")
        return

    article_col = next(
        (c for c in df.columns if any(k in str(c).lower() for k in ("артикул", "номер", "article", "number"))),
        df.columns[0])
    print(f"[СТОЛБЕЦ] Используется «{article_col}»")

    result_rows = []
    for idx, art in enumerate(df[article_col].astype(str).str.strip(), 1):
        if not art or art.lower() in ("nan", "none"):
            continue
        try:
            items = client.get_comprehensive_search(art).get("articles", [])
            if not items:
                result_rows.append({"Номер": art, "Цена": "НЕ НАЙДЕНО"})
                continue

            for itm in items:
                result_rows.append({
                    "Номер": art,
                    "Цена": itm.get("priceV2", ""),
                    "Производитель": itm.get("class_man", ""),
                    "Наименование": itm.get("descr") or itm.get("description", ""),
                    "Срок": itm.get("descr_delivery", ""),
                    "Продавец": itm.get("class_user", ""),
                    "Регион": itm.get("location", ""),
                    "Наличие": itm.get("descr_qtyV2", "Под заказ")
                })
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] запрос для {art}: {e}")
            result_rows.append({"Номер": art, "Цена": f"ОШИБКА: {e}"})

    columns = ["Номер", "Цена", "Производитель", "Наименование", "Срок", "Продавец", "Регион", "Наличие"]
    pd.DataFrame(result_rows).to_excel(output_path, index=False)
    print(f"\n[ГОТОВО] Данные сохранены в «{output_path}»")


def test_single_article(token: str):
    """Тестирование на одном артикуле"""
    client = ZZapAPIClient(token)
    article = "620455CA0A"  # Тестовый артикул
    print("=" * 80 + "\nТЕСТИРОВАНИЕ НА ОДНОМ АРТИКУЛЕ\n" + "=" * 80)
    result = client.get_comprehensive_search(article)
    articles = result.get('articles', [])
    if articles:
        df = pd.DataFrame(articles)
        df.to_excel("test_result.xlsx", index=False)
        print(f"[ТЕСТ] Результат сохранен в test_result.xlsx")


if __name__ == "__main__":
    api_token = "MBmE7rdJlQjqwrFS3grO5h0t7D6deGi6ZBQuTropgAW5qGSbaIMfKGX9znZ"

    if not api_token:
        print("[ОШИБКА] API-ключ не найден. Проверьте .env файл или переменную в коде.")
    else:
        input_file = "articules.xlsx"
        output_file = "articules_result.xlsx"
        if os.path.exists(input_file):
            print(f"[ОСНОВНОЙ РЕЖИМ] Найден файл {input_file}. Запускается обработка...")
            process_excel_file(input_file, output_file, api_token)
        else:
            print(f"[ТЕСТОВЫЙ РЕЖИМ] Файл {input_file} не найден. Запускается тест...")
            test_single_article(api_token)