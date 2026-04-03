# temporary_dir/

短暂文件目录。

推荐按 session 隔离写入：`temporary_dir/<session_id>/...`。

适合放置：
- 临时 Python 脚本
- 管道输出 JSON/TXT/MD
- 调试期间的一次性中间文件

不要把正式的 Concept / Task / Pack 放在这里。session 删除时，对应子目录会被自动清理。
