import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class GraphVisualizer:
    """LangGraph 시각화 전용 유틸리티"""

    def __init__(self, output_dir: str = "graph_visualizations"):
        """
        초기화

        Args:
            output_dir: 시각화 파일들을 저장할 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def visualize_graph(
        self,
        compiled_graph: Any,
        graph_name: str = "graph",
        auto_open: bool = True,
        formats: list = None,
    ) -> dict:
        """
        그래프를 다양한 형식으로 시각화

        Args:
            compiled_graph: 컴파일된 LangGraph 객체
            graph_name: 그래프 이름 (파일명에 사용)
            auto_open: 생성된 파일을 자동으로 열지 여부
            formats: 생성할 형식 리스트 ['png', 'html', 'mermaid']

        Returns:
            생성된 파일 경로들을 담은 딕셔너리
        """
        if formats is None:
            formats = ['png', 'html', 'mermaid']

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{graph_name}_{timestamp}"

        results = {}

        print(f"\n🎨 '{graph_name}' 그래프 시각화 시작...")
        print("=" * 60)

        # Mermaid 코드 생성
        mermaid_code = compiled_graph.get_graph().draw_mermaid()

        if 'mermaid' in formats:
            results['mermaid'] = self._save_mermaid_text(mermaid_code, base_filename)

        if 'png' in formats:
            results['png'] = self._save_png(compiled_graph, base_filename, auto_open)

        if 'html' in formats:
            results['html'] = self._save_html(
                mermaid_code, base_filename, graph_name, auto_open
            )

        print("\n✅ 시각화 완료!")
        print(f"📁 저장 위치: {self.output_dir.absolute()}")

        return results

    def _save_mermaid_text(self, mermaid_code: str, base_filename: str) -> str:
        """Mermaid 텍스트 파일 저장"""
        filepath = self.output_dir / f"{base_filename}.mermaid"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)

        print(f"📝 Mermaid 텍스트: {filepath.name}")
        return str(filepath)

    def _save_png(
        self, compiled_graph: Any, base_filename: str, auto_open: bool
    ) -> Optional[str]:
        """PNG 이미지 파일 저장"""
        try:
            png_data = compiled_graph.get_graph().draw_mermaid_png()
            filepath = self.output_dir / f"{base_filename}.png"

            with open(filepath, 'wb') as f:
                f.write(png_data)

            print(f"🖼️ PNG 이미지: {filepath.name}")

            if auto_open:
                self._open_file(filepath)

            return str(filepath)

        except Exception as e:
            print(f"❌ PNG 생성 실패: {e}")
            print("💡 해결 방법: brew install graphviz && uv add pygraphviz")
            return None

    def _save_html(
        self, mermaid_code: str, base_filename: str, graph_name: str, auto_open: bool
    ) -> str:
        """HTML 파일 저장"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{graph_name} - LangGraph Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 40px;
            font-size: 2.8em;
            font-weight: 300;
        }}
        .graph-info {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .mermaid {{
            text-align: center;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #888;
            font-size: 0.9em;
        }}
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 0 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 {graph_name}</h1>
        <div class="graph-info">
            <span class="badge">LangGraph</span>
            <span class="badge">Reflexion Agent</span>
            <span class="badge">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
        </div>
        <div class="mermaid">
{mermaid_code}
        </div>
        <div class="footer">
            Generated by LangGraph Visualization Utils 🎨
        </div>
    </div>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'base',
            themeVariables: {{
                primaryColor: '#667eea',
                primaryTextColor: '#333',
                primaryBorderColor: '#764ba2',
                lineColor: '#666'
            }}
        }});
    </script>
</body>
</html>"""

        filepath = self.output_dir / f"{base_filename}.html"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"🌐 HTML 파일: {filepath.name}")

        if auto_open:
            self._open_file(filepath)

        return str(filepath)

    def _open_file(self, filepath: Path):
        """파일을 시스템 기본 앱으로 열기"""
        try:
            if os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', str(filepath)], check=False)
            elif os.name == 'nt':  # Windows
                os.startfile(str(filepath))
        except Exception as e:
            print(f"⚠️ 파일 자동 열기 실패: {e}")
            print(f"📂 수동으로 열어보세요: {filepath}")

    def list_visualizations(self) -> list:
        """저장된 시각화 파일들 목록 반환"""
        files = []
        for ext in ['*.png', '*.html', '*.mermaid']:
            files.extend(self.output_dir.glob(ext))

        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    def clean_old_files(self, keep_recent: int = 5):
        """오래된 시각화 파일들 정리"""
        files = self.list_visualizations()

        if len(files) > keep_recent:
            to_remove = files[keep_recent:]
            for file in to_remove:
                try:
                    file.unlink()
                    print(f"🗑️ 삭제: {file.name}")
                except Exception as e:
                    print(f"❌ 삭제 실패: {file.name} - {e}")

            print(f"✅ {len(to_remove)}개 파일 정리 완료")


def quick_visualize(
    compiled_graph: Any,
    name: str = "graph",
    show_png_only: bool = True,
    output_dir: str = "graph_visualizations",
) -> str:
    """
    빠른 그래프 시각화 (PNG만 생성하고 바로 열기)

    Args:
        compiled_graph: 컴파일된 LangGraph
        name: 그래프 이름
        show_png_only: PNG만 생성할지 여부
        output_dir: 출력 디렉토리

    Returns:
        생성된 PNG 파일 경로
    """
    visualizer = GraphVisualizer(output_dir)

    formats = ['png'] if show_png_only else ['png', 'html']
    results = visualizer.visualize_graph(
        compiled_graph=compiled_graph, graph_name=name, auto_open=True, formats=formats
    )

    return results.get('png', '')


# 편의 함수들
def show_graph(compiled_graph: Any, name: str = "graph") -> str:
    """그래프를 PNG로 바로 보기"""
    return quick_visualize(compiled_graph, name, show_png_only=True)


def save_all_formats(compiled_graph: Any, name: str = "graph") -> dict:
    """모든 형식으로 저장"""
    visualizer = GraphVisualizer()
    return visualizer.visualize_graph(compiled_graph, name, auto_open=False)
