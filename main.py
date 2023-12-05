import json
import time
from threading import Thread
from datetime import datetime, timedelta


class Storage:
    def _dumps(self, val):
        return json.dumps({k: str(v) for k, v in val.items()})

    def load(self):
        with open("res", "r") as res_file:
            string = res_file.read()
            if not string:
                return {}
            res_dict = json.loads(string)
            for k, v in res_dict.items():
                v = v.split(".")[0]
                t = datetime.strptime(v, "%H:%M:%S")
                res_dict[k] = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return res_dict

    def save(self, values):
        with open("res", "w") as res_file:
            res_file.write(self._dumps(values))


class Interface:
    results = {}

    def __init__(self, values):
        self.results = values
        self._in_progress = False

    def _show_tasks(self):
        for k, v in sorted(self.results.items(), key=lambda v: v[0]):
            print(v, "\t", k)

    def _suggest_tasks(self, val):
        task_list = [k for k in self.results.keys() if k.startswith(val)]
        task_list.append(val)
        return iter(task_list)

    def _select_task(self):
        self._show_tasks()
        while True:
            current_task = input(" > ")
            if not current_task:
                return None
            found_list = self._suggest_tasks(current_task)
            while next_found_task := next(found_list, None):
                if input(f" ? {next_found_task} ") == 'y':
                    return next_found_task

    def _show_delta(self):
        time_start = datetime.now()
        while self._in_progress:
            delta = datetime.now() - time_start
            print(f" o {delta}", end='\r')
            time.sleep(1)

    def show(self):
        while selected_task := self._select_task():
            self._in_progress = True
            time_start = datetime.now()
            counter_thread = Thread(target=self._show_delta)
            counter_thread.start()
            input()
            self._in_progress = False
            self.results[selected_task] = self.results.get(selected_task, timedelta())
            self.results[selected_task] += datetime.now() - time_start


class App:
    def __init__(self):
        self.storage = Storage()

    def run(self):
        interface = Interface(self.storage.load())
        interface.show()
        self.storage.save(interface.results)


if __name__ == "__main__":
    App().run()
