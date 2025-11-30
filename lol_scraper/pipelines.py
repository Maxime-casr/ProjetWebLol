import json
import os


class CollectPipeline:
    
    def __init__(self):
        self.data = {}
    
    def open_spider(self, spider):
        self.data = {}
    
    def close_spider(self, spider):
        # Create output directory if needed
        os.makedirs('data', exist_ok=True)
        
        # Write collected data to JSON file
        output_path = 'data/all_champion_builds.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        spider.logger.info(f'Saved {len(self.data)} champions to {output_path}')
    
    def process_item(self, item, spider):
        champion = item.get('champion')
        if champion:
            self.data[champion] = {
                'champion': champion,
                'popular_items': item.get('popular_items', [])
            }
        return item
