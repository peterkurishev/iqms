# app/utils/network_tests.py
import asyncio
import aiohttp
import socket
import time
import subprocess
import platform
import statistics
from typing import Dict, List, Optional, Tuple
import psutil
from ping3 import ping
import dns.resolver

class NetworkTester:
    def __init__(self, test_server: str = "https://httpbin.org"):
        self.test_server = test_server
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def run_all_tests(self) -> Dict:
        """Запуск всех сетевых тестов"""
        results = {}
        
        # Основные тесты
        results.update(await self.test_latency())
        results.update(await self.test_download_speed())
        results.update(await self.test_upload_speed())
        results.update(await self.test_packet_loss())
        results.update(await self.test_jitter())
        
        # Дополнительные тесты
        results.update(self.test_dns_resolution())
        results.update(await self.get_network_info())
        results.update(self.test_mtu())
        
        return results

    async def test_latency(self, count: int = 10) -> Dict:
        """Измерение задержки (ping)"""
        latencies = []
        
        for _ in range(count):
            try:
                start_time = time.time()
                async with self.session.get(f"{self.test_server}/get", timeout=5) as response:
                    await response.read()
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # ms
                latencies.append(latency)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                latencies.append(None)
            await asyncio.sleep(0.1)
        
        # Фильтруем неудачные попытки
        successful_pings = [lat for lat in latencies if lat is not None]
        
        return {
            "latency_min": min(successful_pings) if successful_pings else None,
            "latency_max": max(successful_pings) if successful_pings else None,
            "latency_avg": statistics.mean(successful_pings) if successful_pings else None,
            "latency_median": statistics.median(successful_pings) if successful_pings else None,
            "packets_sent": count,
            "packets_received": len(successful_pings)
        }

    async def test_download_speed(self, file_size_mb: int = 10) -> Dict:
        """Тест скорости скачивания"""
        try:
            start_time = time.time()
            async with self.session.get(
                    f"{self.test_server}/bytes/{file_size_mb * 1024 * 1024}",
                timeout=30
            ) as response:
                total_bytes = 0
                async for chunk in response.content.iter_chunked(8192):
                    total_bytes += len(chunk)
            
            end_time = time.time()
            duration = end_time - start_time
            speed_mbps = (total_bytes * 8) / (duration * 1000000)  # Mbps
            
            return {
                "download_speed": round(speed_mbps, 2),
                "download_size_mb": file_size_mb,
                "download_time": round(duration, 2)
            }
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return {"download_speed": None, "download_error": True}

    async def test_upload_speed(self, file_size_mb: int = 5) -> Dict:
        """Тест скорости загрузки"""
        try:
            # Генерируем тестовые данные
            test_data = b"0" * (file_size_mb * 1024 * 1024)
            
            start_time = time.time()
            async with self.session.post(
                    f"{self.test_server}/post",
                    data=test_data,
                timeout=30
            ) as response:
                await response.json()
            
            end_time = time.time()
            duration = end_time - start_time
            speed_mbps = (len(test_data) * 8) / (duration * 1000000)  # Mbps
            
            return {
                "upload_speed": round(speed_mbps, 2),
                "upload_size_mb": file_size_mb,
                "upload_time": round(duration, 2)
            }
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return {"upload_speed": None, "upload_error": True}

    async def test_packet_loss(self, count: int = 20) -> Dict:
        """Тест потери пакетов"""
        successful = 0
        host = self.test_server.split("//")[-1].split("/")[0]
        
        for _ in range(count):
            try:
                result = ping(host, timeout=2)
                if result is not None:
                    successful += 1
            except Exception:
                pass
            await asyncio.sleep(0.2)
        
        packet_loss = ((count - successful) / count) * 100
        
        return {
            "packet_loss": round(packet_loss, 2),
            "packets_sent": count,
            "packets_received": successful
        }

    async def test_jitter(self, count: int = 20) -> Dict:
        """Измерение джиттера (вариация задержки)"""
        latencies = []
        host = self.test_server.split("//")[-1].split("/")[0]
        
        for _ in range(count):
            try:
                start_time = time.time()
                async with self.session.get(f"{self.test_server}/get", timeout=5) as response:
                    await response.read()
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                latencies.append(latency)
            except Exception:
                pass
            await asyncio.sleep(0.1)
        
        if len(latencies) > 1:
            jitter = statistics.stdev(latencies)
        else:
            jitter = 0
        
        return {
            "jitter": round(jitter, 2),
            "jitter_samples": len(latencies)
        }

    def test_dns_resolution(self, hostname: str = "google.com") -> Dict:
        """Тест скорости DNS разрешения"""
        try:
            start_time = time.time()
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(hostname)
            end_time = time.time()
            
            return {
                "dns_resolution_time": round((end_time - start_time) * 1000, 2),
                "dns_resolved_ips": [str(answer) for answer in answers]
            }
        except Exception:
            return {"dns_resolution_time": None, "dns_error": True}

    async def get_network_info(self) -> Dict:
        """Получение информации о сетевом подключении"""
        try:
            # Внешний IP
            async with self.session.get("https://api.ipify.org", timeout=5) as response:
                external_ip = await response.text()
            
            # Информация о сетевых интерфейсах
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = {
                    'ipv4': [addr.address for addr in addrs if addr.family == socket.AF_INET],
                    'ipv6': [addr.address for addr in addrs if addr.family == socket.AF_INET6]
                }
            
            return {
                "external_ip": external_ip,
                "network_interfaces": interfaces,
                "hostname": socket.gethostname()
            }
        except Exception:
            return {"network_info_error": True}

    def test_mtu(self, host: str = "8.8.8.8") -> Dict:
        """Определение MTU (Maximum Transmission Unit)"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ping", "-f", "-l", "1500", host, "-n", "1"],
                    capture_output=True, text=True, timeout=10
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "-M", "do", "-s", "1500", host],
                    capture_output=True, text=True, timeout=10
                )
            
            if "Packet needs to be fragmented" in result.stdout or "message too long" in result.stderr:
                return {"mtu": 1500, "mtu_detection": "needs_fragmentation"}
            else:
                return {"mtu": 1500, "mtu_detection": "success"}
                
        except Exception:
            return {"mtu": None, "mtu_error": True}

# Утилитарные функции
async def run_network_test(test_server: Optional[str] = None) -> Dict:
    """Основная функция для запуска тестов"""
    server = test_server or "https://httpbin.org"
    
    async with NetworkTester(server) as tester:
        results = await tester.run_all_tests()
        results["test_timestamp"] = time.time()
        results["test_server"] = server
        
        return results

def format_results(results: Dict) -> str:
    """Форматирование результатов для вывода"""
    output = []
    output.append("=== Network Test Results ===")
    
    if 'latency_avg' in results:
        output.append(f"Latency: {results['latency_avg']}ms "
                     f"(min: {results['latency_min']}ms, "
                     f"max: {results['latency_max']}ms)")
    
    if 'download_speed' in results:
        output.append(f"Download: {results['download_speed']} Mbps")
    
    if 'upload_speed' in results:
        output.append(f"Upload: {results['upload_speed']} Mbps")
    
    if 'packet_loss' in results:
        output.append(f"Packet Loss: {results['packet_loss']}%")
    
    if 'jitter' in results:
        output.append(f"Jitter: {results['jitter']}ms")
    
    return "\n".join(output)

# Для тестирования
if __name__ == "__main__":
    async def main():
        results = await run_network_test()
        print(format_results(results))
    
    asyncio.run(main())
