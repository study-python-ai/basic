"""
🎨 그래프 시각화 유틸리티 사용 예제
"""

from reflexion_graph_clean import app
from graph_utils import show_graph, GraphVisualizer, quick_visualize


def demo_quick_visualization():
    """빠른 시각화 데모 - PNG만 생성해서 바로 열기"""
    print("🚀 빠른 시각화 데모")
    show_graph(app, "demo_reflexion")


def demo_full_visualization():
    """전체 시각화 데모 - 모든 형식 생성"""
    print("🎨 전체 시각화 데모")
    
    # 시각화 객체 생성 (커스텀 폴더)
    viz = GraphVisualizer(output_dir="demo_graphs")
    
    # 모든 형식으로 시각화
    results = viz.visualize_graph(
        compiled_graph=app,
        graph_name="reflexion_demo",
        auto_open=True,  # 생성된 파일들을 자동으로 열기
        formats=['png', 'html', 'mermaid']
    )
    
    print(f"\n📂 생성된 파일들:")
    for format_type, file_path in results.items():
        if file_path:
            print(f"  {format_type.upper()}: {file_path}")


def demo_multiple_graphs():
    """여러 그래프 시각화 예제"""
    print("📊 여러 그래프 시각화")
    
    viz = GraphVisualizer(output_dir="multi_graphs")
    
    # 같은 그래프를 다른 이름으로 여러 개 저장
    graph_variants = [
        ("reflexion_v1", ['png']),
        ("reflexion_v2", ['html']),
        ("reflexion_final", ['png', 'html', 'mermaid'])
    ]
    
    for name, formats in graph_variants:
        print(f"\n🔄 '{name}' 생성 중...")
        viz.visualize_graph(
            compiled_graph=app,
            graph_name=name,
            auto_open=False,  # 자동 열기 비활성화
            formats=formats
        )
    
    # 저장된 파일들 목록
    print(f"\n📁 저장된 파일들:")
    files = viz.list_visualizations()
    for file in files[:10]:  # 최근 10개만 표시
        print(f"  📄 {file.name}")


def demo_file_management():
    """파일 관리 기능 데모"""
    print("🗂️ 파일 관리 데모")
    
    viz = GraphVisualizer(output_dir="temp_graphs")
    
    # 여러 개 파일 생성
    for i in range(5):
        quick_visualize(app, f"test_{i}", output_dir="temp_graphs")
    
    print(f"\n📊 생성된 파일 수: {len(viz.list_visualizations())}")
    
    # 오래된 파일들 정리 (최근 2개만 보관)
    viz.clean_old_files(keep_recent=2)
    
    print(f"🧹 정리 후 파일 수: {len(viz.list_visualizations())}")


if __name__ == "__main__":
    print("🎯 그래프 시각화 유틸리티 데모")
    print("=" * 50)
    
    demos = [
        ("1. 빠른 시각화", demo_quick_visualization),
        ("2. 전체 시각화", demo_full_visualization), 
        ("3. 다중 그래프", demo_multiple_graphs),
        ("4. 파일 관리", demo_file_management)
    ]
    
    for title, demo_func in demos:
        choice = input(f"\n{title} 실행하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            print(f"\n{title} 시작...")
            demo_func()
            print(f"{title} 완료!")
        
    print("\n✅ 모든 데모 종료!")