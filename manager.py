# -*- coding:utf-8 -*-
"""程序入口"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from iHome import get_app, db
from iHome import models

app = get_app('dev')


# 创建脚本管理器
manager = Manager(app)

# 在迁移时让app和db建立关系，参数位置不要写反了
Migrate(app, db)
# 将迁移脚本添加到脚本管理器
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    print app.url_map
    manager.run()
