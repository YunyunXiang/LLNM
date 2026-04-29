#模型文字示意图
import os
from graphviz import Digraph

# ==========================================
# 请确保 Graphviz 安装路径正确
# ==========================================
os.environ["PATH"] += os.pathsep + r'D:\Models\Graphviz\bin'

# 创建流程图
dot = Digraph('Model_Pipeline', comment='Thyroid Lymph Node Metastasis Prediction')

# 【核心优化点 1】：调整全局图属性
# ranksep 控制各阶段（横向）之间的距离，值越小箭头越短
# nodesep 控制同一阶段内（纵向）节点之间的距离
dot.attr(rankdir='LR', ranksep='0.6', nodesep='0.4', dpi='300')

# 【核心优化点 2】：大幅提升字体大小，去掉 size 限制
dot.attr('node', shape='box', style='filled, rounded', 
         fontname='Arial Bold', fontsize='14', margin='0.2')
dot.attr('edge', fontsize='12', arrowsize='0.8')

# 第一阶段：数据输入
with dot.subgraph(name='cluster_0') as c:
    c.attr(label='Phase 1: Data Input Layer', color='#1976D2', fontcolor='#1976D2', fontsize='16', fontname='Arial Bold')
    c.node('Ori', 'Ultrasound ROI\nImages', fillcolor='#E3F2FD')
    c.node('Gra', 'Grayscale Images', fillcolor='#E3F2FD')
    c.node('Clin', 'Clinical Data\nM1: DTC_min/Size/Calcification\nM2: TPO-Ab\nM3: BRAF V600E', fillcolor='#E3F2FD')
    c.node('CLAHE', 'Pre-processing\n(CLAHE)', fillcolor='#E3F2FD')
    c.edge('Ori', 'Gra')
    c.edge('Gra', 'CLAHE')

# 第二阶段：特征工程
with dot.subgraph(name='cluster_1') as c:
    c.attr(label='Phase 2: Feature Engineering', color='#388E3C', fontcolor='#388E3C', fontsize='16', fontname='Arial Bold')
    c.node('Rad', 'Radiomics Features\n(190 Dimensions)', fillcolor='#E8F5E9')
    c.node('Img_Proc', 'Image Path:\nScalers & SelectKBest(30)', fillcolor='#E8F5E9')
    c.node('Clin_Proc', 'Clinical Path:\nScalers & Weighting', fillcolor='#E8F5E9')
    
    c.edge('CLAHE', 'Rad')
    c.edge('Rad', 'Img_Proc')
    c.edge('Clin', 'Clin_Proc')

# 第三阶段：模型训练
with dot.subgraph(name='cluster_2') as c:
    c.attr(label='Phase 3: Modeling & Validation', color='#7B1FA2', fontcolor='#7B1FA2', fontsize='16', fontname='Arial Bold')
    c.node('Fusion', 'Feature Concatenation\n(Vector Fusion)', fillcolor='#F3E5F5')
    c.node('Models', 'Machine Learning Models:\nRF, SVM, XGBoost, LR, KNN', fillcolor='#F3E5F5', peripheries='2') # peripheries=2 双边框表示重点
    
    c.edge('Img_Proc', 'Fusion')
    c.edge('Clin_Proc', 'Fusion')
    c.edge('Fusion', 'Models', label='5-Fold CV')

# 第四阶段：评估与解释
with dot.subgraph(name='cluster_3') as c:
    c.attr(label='Phase 4: Output & Interpretation', color='#E64A19', fontcolor='#E64A19', fontsize='16', fontname='Arial Bold')
    c.node('Metrics', 'Performance Metrics:\nAUC, F1, Sen, Spe', fillcolor='#FFF3E0')
    c.node('SHAP', 'Interpretability:\nSHAP Analysis', fillcolor='#FFF3E0')
    
    c.edge('Models', 'Metrics')
    c.edge('Models', 'SHAP')

# 保存并导出
file_name = 'optimized_pipeline'
try:
    output_path = dot.render(file_name, format='png', cleanup=True)
    abs_path = os.path.abspath(output_path)
    print(f"--- 成功 ---")
    print(f"图片已生成，字体已放大，间距已缩短。")
    print(f"路径: {abs_path}")
    os.startfile(abs_path) 
except Exception as e:
    print(f"生成失败: {e}")