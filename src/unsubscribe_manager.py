#!/usr/bin/env python3
"""
Mailgun Unsubscribe Manager
自动管理 unsubscribe 列表
"""

import requests
import json
from typing import List, Optional

class UnsubscribeManager:
    """管理 Mailgun 的 unsubscribe 列表"""
    
    def __init__(self, mailgun_domain: str, api_key: str):
        self.mailgun_domain = mailgun_domain
        self.api_key = api_key
        self.base_url = f"https://api.mailgun.net/v3/{mailgun_domain}"
    
    def add_unsubscribe(self, email: str, tag: str = "*") -> bool:
        """
        添加邮箱到 unsubscribe 列表
        
        Args:
            email: 要取消订阅的邮箱
            tag: 标签（"*" 表示所有邮件）
        """
        url = f"{self.base_url}/unsubscribes"
        
        try:
            response = requests.post(
                url,
                auth=("api", self.api_key),
                data={
                    "address": email,
                    "tag": tag
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Added {email} to unsubscribe list")
                return True
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def remove_unsubscribe(self, email: str) -> bool:
        """从 unsubscribe 列表移除邮箱"""
        url = f"{self.base_url}/unsubscribes/{email}"
        
        try:
            response = requests.delete(
                url,
                auth=("api", self.api_key)
            )
            
            if response.status_code == 200:
                print(f"✅ Removed {email} from unsubscribe list")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def check_unsubscribed(self, email: str) -> bool:
        """检查邮箱是否已取消订阅"""
        url = f"{self.base_url}/unsubscribes/{email}"
        
        try:
            response = requests.get(
                url,
                auth=("api", self.api_key)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            return False
    
    def get_all_unsubscribes(self) -> List[str]:
        """获取所有已取消订阅的邮箱"""
        url = f"{self.base_url}/unsubscribes"
        
        try:
            response = requests.get(
                url,
                auth=("api", self.api_key),
                params={"limit": 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                return [item['address'] for item in data.get('items', [])]
            else:
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def filter_subscribers(self, emails: List[str]) -> List[str]:
        """
        过滤掉已取消订阅的邮箱
        
        Args:
            emails: 要检查的邮箱列表
            
        Returns:
            没有取消订阅的邮箱列表
        """
        unsubscribed = set(self.get_all_unsubscribes())
        return [email for email in emails if email not in unsubscribed]
    
    def filter_user_list(self, users: List[dict]) -> List[dict]:
        """
        过滤用户列表，移除已取消订阅的用户
        
        Args:
            users: 用户列表 [{"email": "...", ...}]
            
        Returns:
            过滤后的用户列表
        """
        unsubscribed = set(self.get_all_unsubscribes())
        return [user for user in users if user.get('email') not in unsubscribed]


def main():
    """测试脚本"""
    import sys
    from pathlib import Path
    
    # 添加父目录到路径
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import MINARA_CONFIG
    
    manager = UnsubscribeManager(
        mailgun_domain=MINARA_CONFIG['mailgun_domain'],
        api_key=MINARA_CONFIG['mailgun_api_key']
    )
    
    print("Mailgun Unsubscribe Manager")
    print("=" * 50)
    
    # 示例：获取所有已取消订阅的邮箱
    unsubscribed = manager.get_all_unsubscribes()
    print(f"\n📋 Total unsubscribed: {len(unsubscribed)}")
    for email in unsubscribed[:10]:  # 只显示前10个
        print(f"  - {email}")
    
    if len(unsubscribed) > 10:
        print(f"  ... and {len(unsubscribed) - 10} more")


if __name__ == '__main__':
    main()

