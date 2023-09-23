import json
import requests
import pandas as pd
from typing import Dict, List
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

# Global variable
NOW = datetime.now()


class TwelveData:
    __API_URL_BASE = "https://api.twelvedata.com/time_series?"

    def __init__(self, api_key, retries: int = 5):
        self.api_base_url = self.__API_URL_BASE
        self.__api_key = api_key
        self.request_timeout = 120

        self.session = requests.Session()
        retries = Retry(
            total=retries, backoff_factor=0.5, status_forcelist=[502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def __request(self, url):
        # print(url)
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode("utf-8"))
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode("utf-8"))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise

    def get_exchange_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
    ) -> dict:
        """Retrieve exchange data per day for the provided stock in a date range"""

        api_url = "{0}symbol={1}&interval=1day&start_date={2}&end_date={3}&dp=2&apikey={4}".format(
            self.api_base_url,
            (",").join(symbols),
            start_date,
            end_date,
            self.__api_key,
        )

        return self.__request(api_url)

    def get_api_usage(self):
        api_url = "https://api.twelvedata.com/api_usage?apikey={0}".format(
            self.__api_key
        )

        return self.__request(api_url)

    def get_stocks(self):
        api_url = "https://api.twelvedata.com/stocks?apikey={0}".format(self.__api_key)

        return self.__request(api_url)

    def write_json(self, data: Dict[str, str]) -> None:
        """Writes a json file with the provided dictionary"""
        with open("exchange_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=3)

    def read_json(self, json_file: str) -> Dict[str, str]:
        """Reads a json files and parses it into a dictionary"""
        with open(json_file, encoding="utf-8") as file:
            return json.load(file)

    def as_pandas(self, data: dict):
        df = pd.DataFrame()

        for stock, details in data.items():
            df_temp = pd.json_normalize(
                details,
                record_path=["values"],
                meta=[
                    ["meta", "symbol"],
                    ["meta", "currency"],
                    ["meta", "exchange_timezone"],
                    ["meta", "exchange"],
                    ["meta", "mic_code"],
                    ["meta", "type"],
                ],
            )

            df_temp.rename(
                columns={
                    old_name: old_name.split(".")[1]
                    for old_name in df_temp.columns
                    if old_name.startswith("meta")
                },
                inplace=True,
            )

            df = pd.concat([df, df_temp])

        df["extraction_date_utc"] = NOW
        df.reset_index(inplace=True, drop=True)

        return df
