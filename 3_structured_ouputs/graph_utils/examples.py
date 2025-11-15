"""
그래프 시각화 사용 예제
"""

# 기본 사용법 예제
example_code = '''
# 1. 간단한 PNG 시각화 (바로 열기)
from graph_utils.visualizer import show_graph

# 그래프를 PNG로 바로 보기
show_graph(app, "reflexion_agent")


# 2. 전체 기능 사용
from graph_utils.visualizer import GraphVisualizer

# 시각화 객체 생성
viz = GraphVisualizer(output_dir="my_graphs")

# 모든 형식으로 시각화
results = viz.visualize_graph(
    compiled_graph=app,
    graph_name="reflexion_agent_v1", 
    auto_open=True,
    formats=['png', 'html', 'mermaid']
)

print(f"생성된 파일들: {results}")


# 3. 빠른 시각화
from graph_utils.visualizer import quick_visualize

# PNG만 빠르게 생성
png_path = quick_visualize(app, "test_graph")
print(f"PNG 저장됨: {png_path}")


# 4. 파일 관리
viz.list_visualizations()  # 저장된 파일들 목록
viz.clean_old_files(keep_recent=3)  # 오래된 파일 정리
'''
