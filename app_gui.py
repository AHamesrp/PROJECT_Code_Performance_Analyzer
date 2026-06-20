import sys
from pathlib import Path
import threading
import traceback
import json

# Garantir que o diretório raiz esteja no path ao executar diretamente
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from services.repo_manager import RepoManager
from services.git_analyzer import GitAnalyzer
from services.metrics_calculator import MetricsCalculator
from services.non_ai_analyzer import NonAIAnalyzer
from services.ai_analyzer import AIAnalyzer
from config import settings


class AnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Code Performance Analyzer")
        self.geometry("820x700")
        self.resizable(False, False)

        self.repo_manager = RepoManager()
        self.git_analyzer = GitAnalyzer()
        self.ai_analyzer = AIAnalyzer(settings.ANTHROPIC_API_KEY)

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Code Performance Analyzer", font=(None, 18, "bold"))
        title.pack(anchor="w")

        description = ttk.Label(
            frame,
            text="Digite a URL do repositório Git e clique em Start para rodar a análise.",
            wraplength=780,
            foreground="#444"
        )
        description.pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(frame)
        form.pack(fill="x")

        ttk.Label(form, text="URL do repositório:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(form, width=90)
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.url_entry.insert(0, "https://github.com/AHamesrp/academia_fabiano_lp.git")

        options = ttk.Frame(form)
        options.grid(row=2, column=0, sticky="w")
        self.detailed_var = tk.BooleanVar(value=False)
        self.detailed_checkbox = ttk.Checkbutton(options, text="Análise detalhada (IA)", variable=self.detailed_var)
        self.detailed_checkbox.pack(side="left")

        self.start_button = ttk.Button(options, text="Start", command=self.on_start)
        self.start_button.pack(side="left", padx=(14, 0))

        self.status_label = ttk.Label(frame, text="Pronto para iniciar a análise.", foreground="#1155cc")
        self.status_label.pack(anchor="w", pady=(12, 0))

        self.results_frame = ttk.LabelFrame(frame, text="Results", padding=12)
        self.results_frame.pack(fill="both", expand=True, pady=(16, 0))

        self.summary_text = scrolledtext.ScrolledText(self.results_frame, height=10, wrap="word", state="disabled")
        self.summary_text.pack(fill="both", expand=False, pady=(0, 10))

        self.commits_text = scrolledtext.ScrolledText(self.results_frame, height=12, wrap="word", state="disabled")
        self.commits_text.pack(fill="both", expand=True, pady=(0, 10))

        self.raw_text = scrolledtext.ScrolledText(self.results_frame, height=12, wrap="word", state="disabled")
        self.raw_text.pack(fill="both", expand=True)

    def on_start(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL inválida", "Informe uma URL de repositório Git válida.")
            return

        self.start_button.config(state="disabled")
        self.status_label.config(text="Executando análise...", foreground="#1f4e79")
        self.clear_results()

        thread = threading.Thread(target=self.run_analysis, args=(url, self.detailed_var.get()), daemon=True)
        thread.start()

    def clear_results(self):
        for widget in (self.summary_text, self.commits_text, self.raw_text):
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            widget.config(state="disabled")

    def run_analysis(self, url: str, detailed: bool):
        try:
            repo = self.repo_manager.clone_or_update(url)
            repo_info = self.git_analyzer.get_repository_info(repo)
            commits = self.git_analyzer.get_commits_with_files(repo, limit=50)

            repo_path = str(repo.working_dir)
            for commit in commits:
                try:
                    try:
                        repo.git.checkout(commit.get("full_sha") or commit.get("sha"))
                    except Exception:
                        repo.git.checkout(commit.get("sha"))

                    complexity, _ = MetricsCalculator.calculate_complexity(repo_path)
                except Exception:
                    complexity = 0.0
                commit["complexity"] = complexity

            report = NonAIAnalyzer.generate_text_report(commits, repo_info)
            non_ai_degradations = NonAIAnalyzer.detect_degradations(commits)
            analysis_data = {
                "repository_url": repo_info.get("url", url),
                "repository_name": repo_info.get("name", "Unknown"),
                "total_commits": len(commits),
                "analysis_status": "completed",
                "degradations_found": len(non_ai_degradations),
                "commits": commits,
                "report": report
            }

            ai_report = None
            if detailed:
                ai_analysis = self.ai_analyzer.analyze_performance_degradation(commits, repo_info)
                ai_report = ai_analysis.get("analysis")
                degradation_points = ai_analysis.get("degradation_points", [])
                if not degradation_points:
                    degradation_points = non_ai_degradations
                analysis_data["ai_analysis"] = ai_report
                analysis_data["degradations_found"] = len(degradation_points)
                analysis_data["degradation_points"] = degradation_points

            self.after(0, self.display_results, analysis_data)
        except Exception as exc:
            error_msg = f"Erro durante a análise: {exc}"
            self.after(0, self.show_error, error_msg, traceback.format_exc())
        finally:
            try:
                self.repo_manager.cleanup(repo)
            except Exception:
                pass
            self.after(0, self.finish_analysis)

    def display_results(self, data):
        summary = (
            f"Repositório: {data.get('repository_name')}\n"
            f"URL: {data.get('repository_url')}\n"
            f"Commits analisados: {data.get('total_commits')}\n"
            f"Status: {data.get('analysis_status')}\n"
            f"Degradações identificadas: {data.get('degradations_found')}\n"
        )
        if data.get('ai_analysis'):
            summary += f"AI Analysis: disponível\n"

        self.summary_text.config(state="normal")
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state="disabled")

        commit_lines = []
        for commit in data.get('commits', [])[:12]:
            commit_lines.append(
                f"SHA: {commit.get('sha')}\n"
                f"Mensagem: {commit.get('message')}\n"
                f"Autor: {commit.get('author')}\n"
                f"Complexidade: {commit.get('complexity', 0):.2f}\n"
                f"Linhas alteradas: +{commit.get('lines_added')}/-{commit.get('lines_removed')}\n"
                f"Arquivos modificados: {commit.get('files_changed')}\n"
                "────────────────────────────────────────\n"
            )
        self.commits_text.config(state="normal")
        self.commits_text.insert(tk.END, "".join(commit_lines))
        self.commits_text.config(state="disabled")

        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        self.raw_text.config(state="normal")
        self.raw_text.insert(tk.END, raw_json)
        self.raw_text.config(state="disabled")

    def show_error(self, message, details=""):
        self.status_label.config(text=message, foreground="#b00020")
        messagebox.showerror("Erro", message + "\n\n" + details)

    def finish_analysis(self):
        self.start_button.config(state="normal")
        self.status_label.config(text="Análise finalizada.", foreground="#116611")


if __name__ == "__main__":
    app = AnalyzerApp()
    app.mainloop()
