from curl_cffi import requests
from urllib.parse import parse_qs, unquote
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MidasRWA:
    def __init__(self) -> None:
        self.BASE_API = "https://api-tg-app.midas.app"
        self.REF_CODE = "ref_b6243c03-25ae-43f0-9667-5defd6c43b9b" # U can change it with yours.
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.query_id = {}
        self.username = {}
        self.tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Midas RWA {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def extract_query_data(self, query: str):
        try:
            account = parse_qs(query).get('user', [None])[0]
            account_data = json.loads(unquote(account))
            user_id = account_data.get("id", None)
            username = account_data.get("username", "Unknown")

            return user_id, username
        except Exception as e:
            return None, None
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy=None):
        url = "https://api.ipify.org?format=json"
        proxies = {"http":proxy, "https":proxy} if proxy else None
        try:
            response = await asyncio.to_thread(requests.get, url=url, proxies=proxies, timeout=30, impersonate="chrome120", verify=False)
            response.raise_for_status()
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
    
    async def user_login(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/auth/register"
        data = json.dumps({"initData":self.query_id[user_id], "source":self.REF_CODE})
        headers = {
            **self.HEADERS[user_id],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Access Token Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None

    async def user_data(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)  
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error     :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Balance & Tickets Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def user_visited(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/visited"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.patch, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error     :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Visited Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def daily_checkin(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/streak"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Status Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def claim_checkin(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/streak"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def refferal_status(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/referral/status"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Claimable Reward Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def claim_refferal(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/referral/claim"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Reward Not Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def play_game(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/game/play"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                if response.status_code == 400:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   ●{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Tap-Tap {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                
        return None
            
    async def available_tasks(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/available"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Lists Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def perform_tasks(self, user_id: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/start/{task_id}"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)
                if response.status_code == 400:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Start Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def claim_tasks(self, user_id: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/claim/{task_id}"
        headers = {
            **self.HEADERS[user_id],
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome120", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
    
    async def process_check_connection(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if is_valid: return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(user_id)
                await asyncio.sleep(1)
                continue

            return False
            
    async def process_user_login(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(user_id, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None            

            token = await self.user_login(user_id, proxy)
            if token:
                self.tokens[user_id] = token

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} GET Access Token Success {Style.RESET_ALL}"
                )
                return True
            
            return False
            
    async def process_accounts(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(user_id, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            user = await self.user_data(user_id, proxy)
            if user:
                balance = user.get("points", 0)
                tickets = user.get("tickets", 0)
                first_visit = user.get("isFirstVisit", False)

                if first_visit:
                    await self.user_visited(user_id, proxy)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} GM {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Tickets   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tickets} Tap {Style.RESET_ALL}"
                )

            checkin = await self.daily_checkin(user_id, proxy)
            if checkin:
                streak_days = checkin.get("streakDaysCount", 0)
                is_claimable = checkin.get("claimable", False)

                if is_claimable:
                    claim = await self.claim_checkin(user_id, proxy)
                    if claim:
                        checkin_balance_reward = claim.get("nextRewards", {}).get("points", 0)
                        checkin_tickets_reward = claim.get("nextRewards", {}).get("tickets", 0)

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {streak_days} {Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin_balance_reward} GM {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}|{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin_tickets_reward} Tap {Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} Day {streak_days} {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Already Claimed{Style.RESET_ALL}"
                    )

            refferal = await self.refferal_status(user_id, proxy)
            if refferal:
                can_claim = refferal.get("canClaim", False)

                if can_claim:
                    claim = await self.claim_refferal(user_id, proxy)
                    if claim:
                        ref_balance_reward = claim.get("totalPoints", 0)
                        ref_tickets_reward = claim.get("totalTickets", 0)

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ref_balance_reward} GM{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ref_tickets_reward} Tap{Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Reward {Style.RESET_ALL}"
                    )
            
            user = await self.user_data(user_id, proxy)
            if user:
                tickets = user.get("tickets", 0)

                if tickets > 0:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Tap Games :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Available {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{tickets} Chances{Style.RESET_ALL}"
                    )

                    while tickets > 0:
                        tap_tap = await self.play_game(user_id, proxy)
                        if tap_tap: 
                            tap_reward = tap_tap.get("points", 0)
                            tickets -= 1

                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ●{Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT} Tap-Tap {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {tap_reward} GM {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}|{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {tickets} {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}Chances Left{Style.RESET_ALL}"
                            )
                        else:
                            break

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Tap Games :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Chances {Style.RESET_ALL}"
                    )

            tasks = await self.available_tasks(user_id, proxy)
            if tasks:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}")

                for task in tasks:
                    if task:
                        task_id = task.get("id")
                        title = task.get("name")
                        reward = task.get("points", 0)
                        delay = task.get("waitTime", 0)
                        status = task.get("state")

                        if status == "COMPLETED":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT} [Completed] {Style.RESET_ALL}"
                            )
                            continue

                        if status == "WAITING":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} [Waiting] {Style.RESET_ALL}"
                            )

                            start = await self.perform_tasks(user_id, task_id, proxy)
                            if start and start.get("state") == "CLAIMABLE":
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT}Start Status:{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                )

                                for remaining in range(delay, 0, -1):
                                    print(
                                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                        f"{Fore.YELLOW+Style.BRIGHT} Wait For {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{remaining}{Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT} Seconds to Claim Reward... {Style.RESET_ALL}",
                                        end="\r",
                                        flush=True
                                    )
                                    await asyncio.sleep(1)

                                claim = await self.claim_tasks(user_id, task_id, proxy)
                                if claim and claim.get("state") == "COMPLETED":
                                    self.log(
                                        f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}                                "
                                    )

                            
                        elif status == "CLAIMABLE":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT} [Claimable] {Style.RESET_ALL}"
                            )

                            claim = await self.claim_tasks(user_id, task_id, proxy)
                            if claim and claim.get("state") == "COMPLETED":
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}"
                                )

    async def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                
                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    await self.load_proxies()

                separator = "=" * 20
                for idx, query in enumerate(queries, start=1):
                    if query:
                        user_id, username = self.extract_query_data(query)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(queries)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not user_id or not username:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Query Data {Style.RESET_ALL}"
                            )
                            continue

                        self.HEADERS[user_id] = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Origin": "https://prod-tg-app.midas.app",
                            "Referer": "https://prod-tg-app.midas.app/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": FakeUserAgent().random
                        }

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Username  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
                        )

                        self.query_id[user_id] = query
                        self.username[user_id] = username
                        
                        await self.process_accounts(user_id, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*50)

                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = MidasRWA()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Midas RWA - BOT{Style.RESET_ALL}                                       "                              
        )