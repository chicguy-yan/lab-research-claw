## 前端bug
前端只能在一个 workspace 里面新建会话，但是无法切换 workspace，所以需要增加哎 workspace 的功能（我发现控制平面六大文件没有办法实现）

控制平面的六个文件没有显示，这是作为跨workspace 的系统级别的，如果要修改要怎么办呢？

所有的前端都是按照 md 文件展示的，我在想对于普通农用户

layer1、2、3记忆文件无法在前端修改。

trace 的json 字段原本是想让 agent 定期读取 sessions 和 tool call 来反思用户在某一闭环场景（目前那三类的闭环场景）的 best practices 然后沉淀为 skill 的。

我觉得必须要加上可以@对应的文件的办法

## 0314
工具调用消息太长，希望可以折叠