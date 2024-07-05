from requests import get, post
from urllib.parse import unquote
from colorama import Fore
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Literal
from os import system as sys
from platform import system as s_name
from time import sleep
from random import randint, uniform
from decimal import Decimal, getcontext
from itertools import cycle
getcontext().prec = 10

from Core.Tools.HPV_Getting_File_Paths import HPV_Get_Accounts
from Core.Tools.HPV_User_Agent import HPV_User_Agent
from Core.Tools.HPV_Proxy import HPV_Proxy_Checker

from Core.Config.HPV_Config import *







class HPV_LimeCoin:
    '''
    AutoBot Ferma /// HPV
    ---------------------
    [1] - `Получение ежедневной награды`
    
    [2] - `Улучшение бустов`
        [2.1] - `Попытка улучшить буст 'Сила клика' (урон за один тап)`
        
        [2.2] - `Попытка улучшить буст 'Лимит энергии' (максимальная ёмкость энергии)`
    
    [3] - `Получение кол-ва бустов и их активация`
    
    [4] - `Беспрерывное тапанье под бусты, до истечения дневного лимита`
    
    [5] - `Ожидание 24 часа`
    
    [6] - `Повторение действий через 24 часа`
    '''



    def __init__(self, Name: str, URL: str, Proxy: dict) -> None:
        self.Name = Name                   # Ник аккаунта
        self.Token = self.URL_Clean(URL)   # Уникальная ссылка-токен для авторизации в mini app
        self.Proxy = Proxy                 # Прокси (при наличии)
        self.UA = HPV_User_Agent()         # Генерация уникального User Agent



    def URL_Clean(self, URL: str) -> str:
        '''Очистка уникальной ссылки от лишних элементов'''

        try:
            return unquote(URL.split('#tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        except:
            return ''



    def Current_Time(self) -> str:
        '''Текущее время'''

        return Fore.BLUE + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'



    def Logging(self, Type: Literal['Success', 'Warning', 'Error'], Name: str, Smile: str, Text: str) -> None:
        '''Логирование'''

        with Console_Lock:
            COLOR = Fore.GREEN if Type == 'Success' else Fore.YELLOW if Type == 'Warning' else Fore.RED # Цвет текста
            DIVIDER = Fore.BLACK + ' | '   # Разделитель

            Time = self.Current_Time()     # Текущее время
            Name = Fore.MAGENTA + Name     # Ник аккаунта
            Smile = COLOR + str(Smile)     # Смайлик
            Text = COLOR + Text            # Текст лога

            print(Time + DIVIDER + Smile + DIVIDER + Text + DIVIDER + Name)



    def Get_Power(self) -> dict:
        '''Получение информации о текущем мощности майнинга'''

        URL = 'https://raw.githubusercontent.com/A-KTO-Tbl/LimeCoin/main/Core/Config/HPV_Click_Info.json'

        try:
            return {'Status': True, 'Power': get(URL).json()['Click']}
        except:
            return {'Status': False}



    def Get_Info(self) -> dict:
        '''Получение информации об игроке'''

        URL = 'https://api.limecoin.online/user/info/'
        Headers = {'Accept': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://webapp.limecoin.online', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://webapp.limecoin.online/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            HPV = get(URL, headers=Headers, proxies=self.Proxy).json()

            Balance = HPV['coins'] # Текущий баланс
            Boost = 2 - HPV['activated_boosts'] # Кол-во активированных бустов, 0 - если доступно 2, 1 - если доступен 1, 2 - если доступно 0
            Click_LVL = HPV['level'] # Уровень силы клика
            Limit_LVL = HPV['clicks_limit_level'] # Уровень лимита энергии

            return {'Status': True, 'Balance': Balance, 'Boost': Boost, 'Click_LVL': Click_LVL, 'Limit_LVL': Limit_LVL}
        except:
            return {'Status': False}



    def Clicks_Completed(self) -> int:
        '''Получение информации о том, сколько тапов уже произведено'''

        URL = 'https://api.limecoin.online/points/clicks/'
        Headers = {'Connection': 'keep-alive', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'Accept': 'application/json', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://limecoin-prod.b-cdn.net', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://limecoin-prod.b-cdn.net/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            return get(URL, headers=Headers, proxies=self.Proxy).json()['clicks']
        except:
            pass



    def Day_Limit(self) -> int:
        '''Лимит текущего дня'''

        URL = 'https://api.limecoin.online/points/clicks/limit/'
        Headers = {'Accept': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://webapp.limecoin.online', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://webapp.limecoin.online/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            return get(URL, headers=Headers, proxies=self.Proxy).json()['limit']
        except:
            pass



    def Daily_Reward(self) -> dict:
        '''Получение ежедневной награды'''

        URL = 'https://api.limecoin.online/user/daily_login_rewards/'
        Headers = {'Accept': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://webapp.limecoin.online', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://webapp.limecoin.online/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            Daily_Reward = get(URL, headers=Headers, proxies=self.Proxy).json()['daily_rewards']

            for Day in list(reversed(Daily_Reward)):
                if Day['is_completed']:
                    _Day = Day['day'] # Какой по счёту день
                    _Coins = Day['reward_coins'] # Полученное кол-во монет за сегодняшний день
                    return {'Day': _Day, 'Coins': _Coins}
        except:
            pass



    def Boost_Activation(self) -> bool:
        '''Активация буста'''

        URL = 'https://api.limecoin.online/points/boost/activate/'
        Headers = {'Accept': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://webapp.limecoin.online', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://webapp.limecoin.online/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            post(URL, headers=Headers, proxies=self.Proxy)
            return True
        except:
            return False



    def Clicks(self, Power: str) -> None:
        '''Совершение тапов'''

        URL = 'https://api.limecoin.online/points/receive/'
        Headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-platform': '"Android"', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'Origin': 'https://webapp.limecoin.online', 'X-Requested-With': 'org.telegram.plus', 'Referer': 'https://webapp.limecoin.online/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        Total_Clicks = randint(45, 65) # Кол-во нажатий за раз
        Coins_For_Clicks = float(Decimal(Power) * Decimal(self.Get_Info()['Click_LVL']) * Decimal('50')) # Кол-во полученных монет за раз

        try:
            post(URL, headers=Headers, json={'clicks': Total_Clicks, 'points': Coins_For_Clicks}, proxies=self.Proxy)
            self.Logging('Success', self.Name, '🟢', 'Тап совершён!')
        except:
            self.Logging('Error', self.Name, '🔴', 'Не удалось тапнуть!')



    def Update_Boosts(self, UP_Type: Literal['Click_LVL', 'Limit_LVL']) -> bool:
        '''Обновление бустов'''

        URL = 'https://api.limecoin.online/levels/increase/' if UP_Type == 'Click_LVL' else 'https://api.limecoin.online/levels/clicks_limit/increase/'
        Headers = {'Connection': 'keep-alive', 'Content-Length': '0', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'Accept': 'application/json', 'sec-ch-ua-mobile': '?1', 'Authorization': f'Bearer {self.Token}', 'User-Agent': self.UA, 'sec-ch-ua-platform': '"Android"', 'Origin': 'https://limecoin-prod.b-cdn.net', 'X-Requested-With': 'org.telegram.plus', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://limecoin-prod.b-cdn.net/', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            post(URL, headers=Headers, proxies=self.Proxy)
            return True
        except:
            return False



    def Run(self) -> None:
        '''Активация бота'''

        while True:
            # try:
                if self.Get_Info()['Status']:
                    self.Logging('Success', self.Name, '🟢', 'Инициализация успешна!')
                    INFO = self.Get_Info()


                    Balance = INFO['Balance'] # Баланс
                    Boost = INFO['Boost'] # Кол-во активированных бустов
                    Click_LVL = INFO['Click_LVL'] # Уровень силы клика
                    Limit_LVL = INFO['Limit_LVL'] # Уровень лимита энергии
                    Power_INFO = self.Get_Power() # Получение информации о текущем мощности майнинга


                    Daily_Reward = self.Daily_Reward() # Получение ежедневной награды
                    self.Logging('Success', self.Name, '🎁', f'Ежедневная награда получена! День: {Daily_Reward["Day"]} (+{Daily_Reward["Coins"]})')


                    self.Logging('Success', self.Name, '💰', f'Текущий баланс: {Balance}')
                    Changes = 0 # Сколько произошло изменений


                    # Улучшение буста `Сила клика` (урон за один тап)
                    if Click_LVL < MAX_CLICK_LVL:
                        if self.Update_Boosts('Click_LVL'):
                            self.Logging('Success', self.Name, '⚡️', 'Буст `Сила клика` улучшен!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание

                    # Улучшение буста `Лимит энергии` (максимальная ёмкость энергии)
                    if Limit_LVL < MAX_LIMIT_LVL:
                        if self.Update_Boosts('Limit_LVL'):
                            self.Logging('Success', self.Name, '⚡️', 'Буст `Лимит энергии` улучшен!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание


                    # Если произошли какие-либо изменения, апгрейд бустов и/или апгрейд босса
                    if Changes:
                        self.Logging('Success', self.Name, '💰', f'Текущий баланс: {self.Get_Info()["Balance"]}')


                    # Получение кол-ва бустов и их активация
                    if Boost > 0:
                        if Power_INFO['Status']:
                            self.Logging('Success', self.Name, '🚀', f'Бустов доступно: {Boost}!')
                            for _ in range(Boost):
                                if self.Boost_Activation(): # Активация буста
                                    for _ in range(45):
                                        self.Clicks(Power_INFO['Power']) # Совершение тапов
                                        sleep(uniform(0.22, 0.33)) # Промежуточное ожидание

                            self.Logging('Success', self.Name, '💰', f'Текущий баланс: {self.Get_Info()["Balance"]}')


                    # Беспрерывное тапанье, до истечения дневного лимита
                    while True:
                        sleep(uniform(0.33, 0.44)) # Промежуточное ожидание
                        self.Clicks(Power_INFO['Power']) # Совершение тапов
                        if self.Clicks_Completed() >= self.Day_Limit():
                            break


                    self.Logging('Success', self.Name, '💰', f'Текущий баланс: {self.Get_Info()["Balance"]}')

                    Waiting = 87_000 # Значение времени в секундах для ожидания
                    Waiting_STR = (datetime.now() + timedelta(seconds=Waiting)).strftime('%Y-%m-%d %H:%M:%S') # Значение времени в читаемом виде

                    self.Logging('Warning', self.Name, '⏳', f'Следующий старт сбора монет: {Waiting_STR}!')

                    sleep(Waiting) # Ожидание 24 часа

                else: # Если аутентификация не успешна
                    self.Logging('Error', self.Name, '🔴', 'Ошибка инициализации!')
                    sleep(randint(33, 66)) # Ожидание от 33 до 66 секунд
            # except:
            #     pass







if __name__ == '__main__':
    sys('cls') if s_name() == 'Windows' else sys('clear')

    Console_Lock = Lock()
    Proxy = HPV_Proxy_Checker()

    def Start_Thread(Account, URL, Proxy = None):
        LimeCoin = HPV_LimeCoin(Account, URL, Proxy)
        LimeCoin.Run()

    for Account, URL in HPV_Get_Accounts().items():
        if Proxy:
            Proxy = cycle(Proxy)
            Thread(target=Start_Thread, args=(Account, URL, next(Proxy),)).start()
        else:
            Thread(target=Start_Thread, args=(Account, URL,)).start()







