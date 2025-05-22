# DrissionPage MCP Server

基于DrissionPage和FastMCP的浏览器自动化MCP服务器，提供丰富的浏览器操作API。

## 功能特性

- 浏览器控制：打开浏览器、管理标签页
- 元素操作：点击元素、输入文本、获取元素HTML
- JavaScript执行：在页面中执行任意JavaScript代码
- CDP协议支持：直接调用Chrome DevTools协议
- 页面导航：页面上下滚动、等待加载
- 截图功能：获取当前页面截图
- 元素转换：将HTML元素转换为DrissionPage定位表达式

## 安装

```bash
pip install -r requirements.txt
```

依赖项：
- drissionpage>=4.1.0.18
- fastmcp>=2.4.0

## 快速开始

1. 启动MCP服务器：
```bash
python main.py
```

2. 使用示例：
```python
# 打开浏览器并访问网页
browser_open("https://example.com")

# 点击页面元素
element_click("//button[@id='submit']")

# 在输入框中输入文本
element_input("//input[@name='username']", "testuser")

# 执行JavaScript
run_js("return document.title")
```

## API文档

### 浏览器控制
- `browser_open(url: str = "")`: 打开浏览器，可选指定初始URL
- `open_tab(url: str = "")`: 在新标签页打开URL

### 元素操作
- `element_click(element_xpath: str)`: 点击指定XPath元素
- `element_input(element_xpath: str, input_value: str)`: 向元素输入文本
- `get_current_tab_element_html(element_xpath: str)`: 获取元素HTML

### 页面控制
- `page_down()`: 向下翻页
- `page_up()`: 向上翻页
- `wait(a: int)`: 等待指定秒数

### 高级功能
- `run_js(js_code: str)`: 执行JavaScript代码
- `run_cdp(cmd: str, **cmd_args)`: 执行CDP协议命令
- `get_current_tab_screenshot(path: str = ".")`: 获取页面截图

## 注意事项

1. 确保已安装Chrome或Chromium浏览器
2. 首次运行时可能需要下载浏览器驱动
3. 部分功能需要浏览器支持CDP协议
4. 使用前请确保浏览器未在其他地方被占用