## util.py
import pygame as pg
import sys
from pymunk.pygame_util import DrawOptions

background = (255, 255, 255) # white
fps = 60

def init_pygame_display(width=1000, height=600):
    """初始化Pygame显示"""
    screen = pg.display.set_mode((width, height))
    draw_options = DrawOptions(screen)
    clock = pg.time.Clock()
    return screen, draw_options, clock

def run(space, func=None, width=1000, height=600):
    """运行Pygame显示循环"""
    # 初始化Pygame显示
    screen, draw_options, clock = init_pygame_display(width, height)
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        if func:
            s = str(func())
        else:
            s = "FPS: {}".format(clock.get_fps())

        pg.display.set_caption(s)
        screen.fill(background)
        
        space.debug_draw(draw_options)
        space.step(1 / fps)

        pg.display.flip()
        clock.tick(fps)



import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import EMBEEDDING_API_KEY, EMBEEDDING_BASE_URL, EMBEEDDING_MODEL
from langchain_openai import OpenAIEmbeddings
class CasesSearch:
    def __init__(self):
        self.embedding_base_url = EMBEEDDING_BASE_URL
        self.embedding_model = EMBEEDDING_MODEL  # 尽管这里不直接使用model_name，但保留配置是好的实践
        self.embedding_api_key = EMBEEDDING_API_KEY
        self.cases_file = "success_cases/success_cases.json"

    def get_embedding(self):
        """获取文本嵌入"""
        embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            base_url=self.embedding_base_url,
            api_key=self.embedding_api_key
        )
        return embeddings
    
    def load_success_cases(self):
        """加载成功案例数据"""
        if not os.path.exists(self.cases_file):
            return []
        
        try:
            with open(self.cases_file, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            return cases
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def search_similar_cases(self, user_instruction, top_k=5):
        """
        搜索与用户指令相似的案例
        
        Args:
            user_instruction (str): 用户当前指令
            top_k (int): 返回最相似的前k个案例，默认为10
            
        Returns:
            list: 最相似的案例列表，每个案例包含完整的JSON信息
        """
        # 加载所有成功案例
        cases = self.load_success_cases()
        if not cases:
            return []
        
        # 获取嵌入模型
        embeddings = self.get_embedding()
        
        # 计算用户指令的嵌入向量
        try:
            user_vector = embeddings.embed_query(user_instruction)
        except Exception as e:
            print(f"计算用户指令嵌入时出错: {e}")
            return []
        
        # 计算所有案例的相似度
        similarities = []
        for case in cases:
            try:
                # 计算案例指令的嵌入向量
                case_vector = embeddings.embed_query(case["user_instruction"])
                
                # 计算余弦相似度
                similarity = cosine_similarity([user_vector], [case_vector])[0][0]
                similarities.append((similarity, case))
            except Exception as e:
                print(f"计算案例相似度时出错: {e}")
                continue
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前top_k个最相似的案例
        top_cases = [case for _, case in similarities[:top_k]]
        return top_cases
    
# if __name__ == "__main__":
#     cs = CasesSearch()
#     em = cs.get_embedding()
#     vector = em.embed_query("创建一个比较长的斜面，在斜面的末尾连接一个平面，平面的末尾放一个较轻的圆形，再做一个小车，矩形为车体，两个圆为轮子，将小车平稳放在该斜面上，让其自然受重力滑下，最后撞飞圆形")
#     print(vector)
#     cases = cs.search_similar_cases("创建一个比较长的斜面，在斜面的末尾连接一个平面，平面的末尾放一个较轻的圆形，再做一个小车，矩形为车体，两个圆为轮子，将小车平稳放在该斜面上，让其自然受重力滑下，最后撞飞圆形")
#     print(cases)
