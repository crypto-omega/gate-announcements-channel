#!/usr/bin/env python3
import asyncio
import aiohttp
import logging
import os
from typing import Optional, List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import telegram
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [gate-announcements-channel] - %(levelname)s - %(message)s'
)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
MAX_LEFT_ID = int(os.getenv('MAX_LEFT_ID', 5))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
LAST_ANNOUNCEMENT_ID = int(os.getenv('LAST_ANNOUNCEMENT_ID', 46450))

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID in .env file")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def fetch_gate_io_announcement(session: aiohttp.ClientSession, announcement_id: int) -> Optional[dict]:
    """获取单个Gate.io公告"""
    url = f"https://www.gate.com/zh/announcements/article/{announcement_id}"
    logging.debug(f"正在获取Gate.io公告 {announcement_id}: {url}")
    
    try:
        async with session.get(url) as response:
            logging.debug(f"Gate.io公告 {announcement_id} 响应状态: {response.status}")
            
            if response.status == 200:
                html = await response.text()
                logging.debug(f"成功获取公告 {announcement_id} 的HTML内容，长度: {len(html)}")
                
                soup = BeautifulSoup(html, 'html.parser')
                title_element = soup.find('h3')
                if title_element:
                    title = title_element.get_text(strip=True)
                    logging.debug(f"解析到公告 {announcement_id} 标题: {title}")
                    return {
                        'id': announcement_id,
                        'title': title,
                        'url': url
                    }
                else:
                    logging.warning(f"未找到公告 {announcement_id} 的标题元素")
                    logging.debug(f"公告 {announcement_id} HTML片段: {html[:500]}...")
                    return None
            elif response.status == 404:
                logging.debug(f"公告 {announcement_id} 不存在 (404)")
                return None
            else:
                logging.warning(f"获取公告 {announcement_id} 失败，状态码: {response.status}")
                return None
    except Exception as e:
        logging.error(f"获取Gate.io公告 {announcement_id} 时发生错误: {e}")
        logging.debug(f"公告 {announcement_id} 异常详情", exc_info=True)
        return None

def get_last_announcement_id() -> int:
    """从.env文件读取最新公告ID"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('LAST_ANNOUNCEMENT_ID='):
                    return int(line.split('=')[1].strip())
        return LAST_ANNOUNCEMENT_ID  # 如果没找到，返回初始值
    except Exception as e:
        logging.error(f"读取.env文件失败: {e}")
        return LAST_ANNOUNCEMENT_ID

def update_last_announcement_id(announcement_id: int):
    """更新.env文件中的最新公告ID"""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('LAST_ANNOUNCEMENT_ID='):
                lines[i] = f'LAST_ANNOUNCEMENT_ID={announcement_id}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'LAST_ANNOUNCEMENT_ID={announcement_id}\n')
        
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        logging.debug(f"已更新.env文件中的LAST_ANNOUNCEMENT_ID为: {announcement_id}")
    except Exception as e:
        logging.error(f"更新.env文件失败: {e}")

async def check_gate_io_announcements() -> List[dict]:
    """检查Gate.io新公告"""
    current_max_id = get_last_announcement_id()
    new_announcements = []
    
    logging.info(f"开始检查Gate.io公告 - 当前最大ID: {current_max_id}")
    
    async with aiohttp.ClientSession() as session:
        check_range_start = current_max_id + 1
        check_range_end = current_max_id + 11
        logging.debug(f"检查ID范围: {check_range_start} 到 {check_range_end - 1}")
        
        consecutive_missing = 0
        latest_id = current_max_id
        
        for announcement_id in range(check_range_start, check_range_end):
            logging.debug(f"检查公告ID: {announcement_id}")
            announcement = await fetch_gate_io_announcement(session, announcement_id)
            if announcement:
                new_announcements.append(announcement)
                latest_id = announcement_id
                logging.info(f"发现新公告 {announcement_id}: {announcement['title']}")
                consecutive_missing = 0
            else:
                consecutive_missing += 1
                logging.debug(f"公告ID {announcement_id} 不存在，连续缺失: {consecutive_missing}/{MAX_LEFT_ID}")
                if consecutive_missing >= MAX_LEFT_ID:
                    logging.debug(f"连续缺失 {MAX_LEFT_ID} 个公告，停止检查更高ID")
                    break
        
        # 如果找到新公告，更新.env文件中的最新ID
        if latest_id > current_max_id:
            update_last_announcement_id(latest_id)
    
    if new_announcements:
        logging.info(f"找到 {len(new_announcements)} 个新公告")
    else:
        logging.debug(f"未找到新公告")
    
    return new_announcements

async def send_to_telegram(announcement: dict) -> None:
    """发送公告到Telegram频道"""
    title = announcement['title']
    url = announcement['url']
    announcement_id = announcement['id']
    
    message_text = f"**{title}**\n\n{url}"
    
    logging.info(f"发送Gate.io公告 {announcement_id} 到Telegram: {title}")
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message_text,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        logging.info(f"[成功] Gate.io公告 {announcement_id} 已发送到 Telegram 频道")
    except Exception as e:
        logging.error(f"[错误] 发送Gate.io公告 {announcement_id} 到 Telegram 频道时发生错误: {e}")

async def monitor_gate_announcements():
    """主监控循环"""
    logging.info("开始监控Gate.io公告...")
    
    while True:
        try:
            announcements = await check_gate_io_announcements()
            
            for announcement in announcements:
                await send_to_telegram(announcement)
                await asyncio.sleep(1)  # 避免发送过快
            
            logging.info(f"检查完成，等待 {CHECK_INTERVAL} 秒后进行下次检查...")
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logging.error(f"监控过程中发生错误: {e}")
            logging.debug("监控异常详情", exc_info=True)
            await asyncio.sleep(60)  # 出错后等待1分钟再重试

async def main():
    """主函数"""
    try:
        # 测试Telegram连接
        await bot.get_me()
        logging.info("Telegram Bot连接成功")
        
        # 开始监控
        await monitor_gate_announcements()
        
    except Exception as e:
        logging.error(f"启动失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())