from PySide6.QtCore import QThread, Signal, QObject, QWaitCondition, QMutex

from src.utils.detection import detect_contours


class DetectionTask:
    def __init__(self, image, original_image_id, image_part_position, label_name, params=None, confidence_threshold=0.1):
        self.image = image
        self.original_image_id = original_image_id
        self.image_part_position = image_part_position
        self.label_name = label_name
        self.params = params
        self.confidence_threshold = confidence_threshold


class DetectionWorker(QThread):
    task_finished = Signal(DetectionTask, list)

    def __init__(self, task_queue, condition, mutex):
        super().__init__()
        self.task_queue = task_queue
        self.condition = condition
        self.mutex = mutex
        self.running = True

    def run(self):
        while self.running:
            self.mutex.lock()
            if self.task_queue:
                task = self.task_queue.pop(0)
                self.mutex.unlock()
                results = detect_contours(task.image, task.confidence_threshold)
                self.task_finished.emit(task, results)
            else:
                self.condition.wait(self.mutex)
                self.mutex.unlock()

    def stop(self):
        self.running = False
        self.condition.wakeAll()


class DetectionQueue(QObject):
    task_added = Signal()
    task_completed = Signal(DetectionTask, list)

    def __init__(self):
        super().__init__()
        self.queue = []
        self.condition = QWaitCondition()
        self.mutex = QMutex()
        self.worker = DetectionWorker(self.queue, self.condition, self.mutex)
        self.worker.task_finished.connect(self.on_task_finished)
        self.worker.start()

    def add_task(self, task):
        self.mutex.lock()
        self.queue.append(task)
        self.mutex.unlock()
        self.task_added.emit()
        self.condition.wakeOne()

    def on_task_finished(self, task, results):
        self.task_completed.emit(task, results)

    def stop_worker(self):
        self.worker.stop()
