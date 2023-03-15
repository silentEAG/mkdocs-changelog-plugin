from typing import Dict, Any, Optional
from jinja2 import Template
from mkdocs import plugins
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.config import config_options
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
from mkdocs.utils import copy_file
import os

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR = os.path.join(PLUGIN_DIR, "templates/list.html")
EXTRA_CSS = ["css/changelog.css"]

def get_raw_log(max_count, dir):
    import subprocess
    log_info = subprocess.run(["git", "log", "--name-status", "--pretty=format:%ad%s", "--date=format:%Y-%m-%d %H:%M:%S||", f"--max-count={max_count}", f"{dir}"], shell=True, stdout=subprocess.PIPE)
    if log_info.stderr:
        print(log_info.stderr)
    log_info = log_info.stdout.decode("utf-8")
    return log_info

class ChangeFile:
    def __init__(self, status, path):
        self.status = status
        self.path = path

class ChangeItem:
    def __init__(self, date: str, message: str, files: list[ChangeFile]):
        self.date = date
        self.message = message
        self.files = files
    
    def append_file(self, file):
        self.files.append(file)

class ChangelogPlugin(plugins.BasePlugin):
    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
        ("max_count", config_options.Type(int, default=5)),
        ("file_folder", config_options.Type(str, default="docs/"))
    )

    change_list: list[ChangeItem] = []
    # source -> url
    change_map: dict[str, Page] = {}

    def print_change_list(self):
        for item in self.change_list:
            print("data: " + item.date)
            print("message: " + item.message)
            print("files: ")
            for file in item.files:
                print(file.status, file.path)
            print()

    def get_change_list(self):

        item_list = get_raw_log(self.config.get("max_count"), self.config.get("file_folder")).split("\n\n")
        for tmp_item in item_list:
            item_info = tmp_item.split("\n")
            meta = item_info[0].split("||")
            date = meta[0].strip()
            message = meta[1].strip()
            files = []
            for tmp_file in item_info[1:]:
                file_info = tmp_file.split("\t")
                if file_info.__len__() < 2:
                    continue
                status = file_info[0].strip()
                path = file_info[1].strip()
                # curretly only support markdown file
                if path.endswith(".md"):
                    files.append(ChangeFile(status, path))

            self.change_list.append(ChangeItem(date, message, files))

    def on_config(self, config: config_options.Config, **kwargs) -> Dict[str, Any]:
        self.get_change_list()
        config["extra_css"] = EXTRA_CSS + config["extra_css"]

    def on_post_build(self, config: Dict[str, Any], **kwargs):
        for file in EXTRA_CSS:
            dest_file_path = os.path.join(config["site_dir"], file)
            src_file_path = os.path.join(PLUGIN_DIR, file)
            assert os.path.exists(src_file_path)
            copy_file(src_file_path, dest_file_path)

    def on_page_markdown(self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> Optional[str]:
        self.change_map[self.config.get("file_folder") + page.file.src_uri] = page
    
    def format_changelog(self):
        with open(TEMPLATE_DIR, "r", encoding="utf-8") as f:
            template = Template(f.read())
            return template.render(change_list=self.change_list, change_map=self.change_map)

    def on_page_context(
            self, context: Dict[str, Any], *, page: Page, config: MkDocsConfig, nav
    ):
        if page.meta.get("changelog"):
            context['page'].content += self.format_changelog()
            return context
# test
if __name__ == "__main__":
    plugin = ChangelogPlugin()
    plugin.get_change_list()
    plugin.print_change_list()
    