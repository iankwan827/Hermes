#!/usr/bin/env python3
"""行业限制回测：对比行业限制2 vs 3 vs 无限制"""

import csv
import subprocess
from collections import defaultdict

# 行业分类（基于股票名称和常识）
INDUSTRY_MAP = {
    # 第一池
    '600961': '有色金属', '601168': '有色金属', '603993': '有色金属',
    '000426': '有色金属', '001210': '公用事业', '000737': '有色金属',
    '000973': '化工', '301500': '有色金属', '002709': '新能源',
    '002668': '家用电器', '605117': '新能源', '000408': '有色金属',
    '603156': '食品饮料', '002215': '农林牧渔', '601899': '有色金属',
    '000506': '有色金属', '001337': '有色金属', '002379': '有色金属',
    '000933': '有色金属', '605499': '食品饮料', '002027': '传媒',
    '000807': '有色金属', '300972': '商贸零售', '300573': '医药生物',
    '300444': '电力设备', '603444': '传媒', '002847': '食品饮料',
    '301358': '新能源',
    # 第二池
    '300726': '电子元器件', '300285': '电子元器件', '002842': '有色金属',
    '300031': '机械设备', '603203': '电子元器件', '300346': '电子元器件',
    '300054': '电子元器件', '301099': '电子元器件', '002138': '电子元器件',
    '300802': '电子元器件', '000823': '电子元器件', '300401': '医药生物',
    '300727': '化工', '300037': '化工', '600237': '电子元器件',
}

def get_sina_price(code):
    """从新浪获取实时价格（GBK编码）"""
    prefix = 'sh' if code.startswith('6') else 'sz'
    url = f'http://hq.sinajs.cn/list={prefix}{code}'
    cmd = ['curl', '-s', url, '-H', 'Referer: https://finance.sina.com.cn']
    result = subprocess.run(cmd, capture_output=True, timeout=10)
    if result.returncode == 0 and result.stdout:
        text = result.stdout.decode('gbk', errors='ignore')
        parts = text.split('"')
        if len(parts) > 1:
            data = parts[1].split(',')
            if len(data) > 3:
                return float(data[3])
    return None

def load_csv(path):
    stocks = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append(row)
    return stocks

def select_by_industry(stocks, max_per_industry):
    """按行业限制选股（核心逻辑）"""
    selected = []
    industry_count = defaultdict(int)
    stocks_sorted = sorted(stocks, key=lambda x: float(x.get('综合', 0)), reverse=True)
    
    for stock in stocks_sorted:
        code = stock.get('代码', '')
        industry = INDUSTRY_MAP.get(code, '未知')
        score = float(stock.get('综合', 0))
        
        if industry_count[industry] < max_per_industry:
            selected.append({
                'code': code,
                'name': stock.get('名称', ''),
                'industry': industry,
                'score': score,
                'buy_price': float(stock.get('价格', 0)),
            })
            industry_count[industry] += 1
        
        if len(selected) == 5:
            break
    
    return selected

def main():
    # 读取Week1数据
    week1_pool1 = load_csv('results/weekly_20260622_0958.csv')
    week1_pool2 = load_csv('results/pool2_20260622_1007.csv')
    
    print('=' * 80)
    print('行业限制回测分析')
    print('Week 1: 2026-06-22 (周一买入)')
    print('Week 2: 2026-07-03 (新浪实时价格)')
    print('=' * 80)
    
    for pool_name, week1_data in [('第一池(稳健)', week1_pool1), ('第二池(成长)', week1_pool2)]:
        print(f'\n{"=" * 60}')
        print(f'📊 {pool_name}')
        print(f'{"=" * 60}')
        
        for limit in [0, 2, 3]:
            limit_name = '无限制' if limit == 0 else f'行业≤{limit}'
            print(f'\n--- {limit_name} ---')
            
            portfolio = select_by_industry(week1_data, 999 if limit == 0 else limit)
            
            print(f'{"股票":<10} {"行业":<12} {"分数":>6} {"买入价":>10} {"现价":>10} {"收益":>8}')
            print('-' * 60)
            
            total_return = 0
            for p in portfolio:
                sell_price = get_sina_price(p['code'])
                if sell_price is None:
                    sell_price = p['buy_price']
                
                ret = (sell_price - p['buy_price']) / p['buy_price'] * 100
                total_return += ret
                print(f"{p['name']:<10} {p['industry']:<12} {p['score']:>6.0f} {p['buy_price']:>10.2f} {sell_price:>10.2f} {ret:>+7.2f}%")
            
            avg_return = total_return / len(portfolio) if portfolio else 0
            print('-' * 60)
            print(f"{'平均收益':>40} {avg_return:>+7.2f}%")
            
            industries = defaultdict(int)
            for p in portfolio:
                industries[p['industry']] += 1
            print(f'行业分布: {dict(industries)}')

if __name__ == '__main__':
    main()
