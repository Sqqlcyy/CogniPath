# /app/tasks/task_manager.py

from typing import Dict, Any

class TaskManager:
    """
    一个简单的、基于内存的后台任务管理器。
    在MVP阶段，它使用一个字典来跟踪所有任务的状态。
    在生产环境中，这里可以被替换为Redis或数据库。
    """
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_id: str, doc_id: str):
        print(f"任务管理器: 创建任务 {task_id} (文档ID: {doc_id})")
        self._tasks[task_id] = {
            "status": "PENDING",
            "progress": 0,
            "step": "任务已创建，等待执行...",
            "doc_id": doc_id,
            "result": None,
            "error": None
        }

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        return self._tasks.get(task_id)

    def update_task_progress(self, task_id: str, progress: int, step: str):
        if task_id in self._tasks:
            self._tasks[task_id]['status'] = 'PROCESSING'
            self._tasks[task_id]['progress'] = progress
            self._tasks[task_id]['step'] = step
            print(f"任务管理器: 更新任务 {task_id} -> {step} ({progress}%)")

    def set_task_completed(self, task_id: str, result: Dict):
        if task_id in self._tasks:
            self._tasks[task_id]['status'] = 'COMPLETED'
            self._tasks[task_id]['progress'] = 100
            self._tasks[task_id]['step'] = '处理完成'
            self._tasks[task_id]['result'] = result
            print(f"任务管理器: 任务 {task_id} 完成")

    def set_task_failed(self, task_id: str, error_message: str):
        if task_id in self._tasks:
            self._tasks[task_id]['status'] = 'FAILED'
            self._tasks[task_id]['progress'] = 100
            self._tasks[task_id]['step'] = '处理失败'
            self._tasks[task_id]['error'] = error_message
            print(f"任务管理器: 任务 {task_id} 失败: {error_message}")

# 创建一个全局的单例，供整个应用使用
task_manager = TaskManager()