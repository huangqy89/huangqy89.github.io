# Google Scholar Spider - Python版本

这是一个用于爬取Google Scholar页面的Python爬虫脚本，可以获取学者的论文信息并生成Jekyll网站所需的Markdown文件。

## 功能特点

- 🔍 异步爬取Google Scholar页面
- 📝 自动生成Jekyll Markdown文件
- 🧹 智能文本清理，解决中文编码问题
- 📊 支持批量处理多篇论文
- 🛡️ 模拟浏览器请求，避免被封
- 📈 详细的日志输出和错误处理

## 安装依赖

```bash
# 安装Python依赖包
pip install -r script/requirements.txt

# 或者直接安装
pip install aiohttp beautifulsoup4 lxml
```

## 使用方法

### 1. 爬取数据

编辑 `script/spider.py` 文件，找到最后的 `main()` 调用：

```python
# 修改为你的Google Scholar ID
asyncio.run(main("你的Scholar ID"))
```

然后运行脚本：

```bash
cd /Users/saltpi/Code/huangqy89.github.io
python script/spider.py
```

### 2. 生成Markdown文件

修改 `script/spider.py` 文件底部，注释掉爬取部分，启用Markdown生成部分：

```python
if __name__ == "__main__":
    # 注释掉爬取部分
    # asyncio.run(main("AZAiLpkAAAAJ"))
    
    # 启用Markdown文件生成
    make_md_files()
```

然后再次运行脚本：

```bash
python script/spider.py
```

## 文件说明

- `spider.py` - 主要的Python爬虫脚本
- `requirements.txt` - Python依赖包列表
- `articles.json` - 爬取的文章数据（生成后）
- `_publications/*.md` - 生成的Markdown文件（生成后）

## 主要改进

相比TypeScript/Deno版本：

1. **更好的编码处理**: 使用UTF-8编码，解决中文字符显示问题
2. **异步处理**: 使用aiohttp进行异步HTTP请求，提高爬取效率
3. **错误处理**: 更完善的异常处理和日志记录
4. **文本清理**: 智能清理特殊字符和编码错误
5. **类型安全**: 使用dataclass定义数据结构
6. **模块化设计**: 函数职责清晰，便于维护

## 注意事项

1. **请求频率**: 脚本会并发请求Google Scholar，请注意不要过于频繁
2. **IP限制**: Google Scholar可能会限制IP访问，建议适当间隔使用
3. **Scholar ID**: 需要提供正确的Google Scholar用户ID
4. **网络环境**: 需要能够访问Google Scholar的网络环境

## 故障排除

如果遇到编码问题，可以尝试：
1. 检查系统编码设置
2. 确保Python环境支持UTF-8
3. 检查网络连接和Google Scholar访问权限

## 示例输出

生成的Markdown文件格式：

```markdown
---
title: "论文标题"
collection: publications
permalink: "/publication/2023-01-01"
excerpt: "论文摘要"
date: "2023-01-01"
venue: "会议或期刊名称"
paperurl: "PDF链接"
author: "作者信息"
poster:
remark:
---
```