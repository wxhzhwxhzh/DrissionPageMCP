
#！/usr/bin/env python3
# -*- coding: utf-8 -*-
# mcp程序说明：通过DrissionPage这个库控制浏览器进行各种网页自动化操作

# 调试  npx -y @modelcontextprotocol/inspector uv run D:\\test10\\DrssionPageMCP\\main.py
'''
# mcp配置
"DrissionPageMCP": {
      "command": "python",
      "args": [        
        "D:\\test10\\DrssionPageMCP\\main.py"
      ]
    }

'''

from typing import Any
import re
from DrissionPage import Chromium,ChromiumOptions
from mcp.server.fastmcp import FastMCP

from DrissionPage.items import SessionElement, ChromiumElement, ShadowRoot, NoneElement, ChromiumTab, MixTab, ChromiumFrame
from DrissionPage.common import Keys

# Initialize FastMCP server
mcp = FastMCP("DrissionPageMCP", log_level="ERROR")

# Browser:Chromium=None
class DP:
    browser:Chromium=None
    cdp_event_data=[]
    Drissionpage_python_code=None

def browser_info(b:Chromium) -> dict:
    """获取浏览器的信息"""
    a={'browser_address':b._chromium_options.address,
       "latest_tab_title":b.latest_tab.title,
       "latest_tab_id":b.latest_tab.tab_id,
       }
    return a

@mcp.tool()
def convert_elemnet_to_drissionpage(element: str) -> str:
    """把元素转换为drissionpage格式的字符串"""
    e= Use.raw(element)
    return e 

@mcp.tool()
def connect_or_open_browser(params: dict) -> int:
    """
    用DrissionPage 打开或者接管已打开的浏览器，参数通过字典传递。如果url不为空则打开指定网址。

    参数:
        params (dict): 包含以下可选键的字典：
            - url (str, 可选): 要打开的网址。如果未提供则不自动打开页面。
            - debug_port (int, 可选): 调试端口，默认9222。
            - browser_path (str, 可选): 浏览器可执行文件路径。
            - headless (bool, 可选): 是否以无头模式启动浏览器，默认False。
            - use_system_user_path (bool, 可选): 是否使用系统默认用户配置，默认False。

    返回:
        int: 浏览器信息（由browser_info函数返回）。
    """
    """用DrissionPage 控制接管浏览器，参数通过字典传递。如果url不为空则打开指定网址"""
    url = params.get("url")
    debug_port = params.get("debug_port", 9222)
    browser_path = params.get("browser_path")
    headless = params.get("headless", False)
    use_system_user_path = params.get("use_system_user_path", False)

    co = ChromiumOptions()
    co.set_local_port(debug_port)
    if browser_path:
        co.set_browser_path(browser_path)
    if headless:
        co.headless(True)
    if use_system_user_path:
        co.use_system_user_path(True)

    b = Chromium(co)
    tab = b.latest_tab
    DP.browser = b
    if url:
        tab.get(url)

    return browser_info(b)

@mcp.tool()
def new_tab(url: str="") -> int:
    """用DrissionPage 控制的浏览器 打开一个网址"""    
    t=DP.browser.new_tab( url)    
    return f'{t.title} {t.tab_id} {t.url} 已经打开'

@mcp.tool()
def download_file(url: str, path: str, rename: str ) -> str:
    """下载文件到指定路径
    
    Args:
        url (str): 文件的URL地址
        path (str): 文件保存的路径
        rename (str, optional): 重命名文件名.
    
    Returns:
        str: 下载结果信息
    """
    tab = DP.browser.latest_tab
    result = tab.download(file_url=url, save_path=path, rename=rename)
    
    
    return result

@mcp.tool()

def send_enter() -> str:
    """向当前页面发送 enter 回车键"""
    
    tab=DP.browser.latest_tab
    try:
        result=tab.actions.type(Keys.ENTER)
        return f"{tab.title} 网页发送 enter 回车键成功"
    except Exception as e:
        return f"{tab.title} 网页发送 enter 回车键失败"


@mcp.tool()
def is_element_exist(element_xpath: str, content_include_keyword: str) -> str:
    """通过xpath或者文本节点是否包含关键词判断标签页中某个元素是否存在"""
    
    xpath_locator = f"xpath:{element_xpath}"
    
    if elements := DP.browser.latest_tab.eles(xpath_locator, timeout=2):
        return elements
    if elements := DP.browser.latest_tab.eles(content_include_keyword, timeout=2):
        return elements
    
    return "没找到元素"


@mcp.tool()
def element_click(element_xpath: str) -> Any:
    """通过xpath点击标签页中某个元素,最好先判断元素是否存在"""
    
    l=f"xpath:{element_xpath}"
    e=DP.browser.latest_tab.ele(l)
    result={"locator":l,"element":e,"click_result":e.click()}
    return result



@mcp.tool()
def element_input(element_xpath: str,input_value: str) -> Any:
    """通过xpath给标签页中某个元素输入内容，最好先判断元素是否存在"""
    # b=Chromium(debug_port)
    locator=f"xpath:{element_xpath}"
    e=DP.browser.latest_tab.ele(locator)
    result={"locator":locator,"result":e.input(input_value)}
    return result


@mcp.tool()
def get_current_tab_element_html(element_xpath: str) -> str:
    """获取当前标签页的某个元素的html"""
    # b=Chromium(debug_port)
    elem=DP.browser.latest_tab.ele(f"xpath:{element_xpath}")
    if elem:
        return elem.run_js('return this.outerHTML')
    else:
        return "No element found"
    

@mcp.tool()
def run_js(js_code: str) -> Any:
    """
    在当前标签页中运行JavaScript代码并返回执行结果
    查找网页元素，获取元素信息，操作网页元素优先使用这个方法
    
    Args:
        
        js_code (str): 要执行的JavaScript代码
    
    Returns:
        Any: JavaScript代码执行结果
    
    Note:
        想要获取执行的js代码的返回值，可以在js_code中使用return语句。
        想要获取异步函数的返回值，可以参考下面代码
        return (async (url) => {
    const response = await fetch(url);
    const data = await response.json();    
    return data;
     })("https://www.baidu.com/");
    """
    
    # b=Chromium(debug_port)

    result=DP.browser.latest_tab.run_js(js_code)
    return result
@mcp.tool()
def run_cdp( cmd, **cmd_args) -> Any:
    """在当前标签页中运行谷歌CDP协议代码并获取结果
    
    Args:
        
        cmd: CDP协议命令
        **cmd_args: CDP命令参数
    
    Returns:
        Any: CDP命令执行结果
    
    Note:
        举例1说明 run_cdp('Page.stopLoading')
        举例2说明 run_cdp('Page.navigate', url='https://example.com')
    """
    """在当前标签页中运行谷歌CDP协议代码并获取结果"""
    # b=Chromium(debug_port)
    result=DP.browser.latest_tab.run_cdp(cmd, **cmd_args)
    return result

@mcp.tool()
def on_cdp_event(event_name: str) -> any:
    """设置监听CDP事件
    
    应该先运行cdp  命令 激活对应的域，比如  Network.enable
    """
    # b=Chromium(debug_port)
    def r(**event):
        DP.cdp_event_data.append({"event_name": event_name, "event_data": event})

    try:
        DP.browser.latest_tab.driver.set_callback(event_name, r)
        return f"CDP event callback for '{event_name}' set successfully."
    except Exception as e:
        return e
    
@mcp.tool()
def get_cdp_event_data() -> list:
    """获取CDP事件回调函数收集到的数据"""
    return DP.cdp_event_data    


@mcp.tool()
def get_current_tab_screenshot(path:str=".") -> bytes:
    """
    获取当前标签页的屏幕截图
    
    Args:
        path (str): 截图保存路径，默认为当前目录
    
    Returns:
        bytes: 截图的二进制数据
    """
    """获取当前标签页的屏幕截图 """
    # b=Chromium(debug_port)
    screenshot=DP.browser.latest_tab.get_screenshot(path=path)
    return screenshot 

@mcp.tool()
def get_current_tab_info(debug_port: int) -> int:
    """获取当前标签页的信息,包括url, title,  id"""
    b=Chromium(debug_port)
    tab=b.latest_tab
    info={
        "url":tab.url,
        "title":tab.title,          
        "id":tab.tab_id,
    }
    return info

@mcp.tool()
def get_tab_list(debug_port: int) -> list:
    """获取当前浏览器的所有标签页的信息,包括url, title,  id"""
    b=Chromium(debug_port)
    tabs=b.get_tabs
    tab_list=[]
    for tab in tabs:
        info={
            "url":tab.url,
            "title":tab.title,          
            "id":tab.id,
        }
        tab_list.append(info)
    return tab_list




@mcp.tool()
def page_down( ) -> Any:
    """向当前标签页发送按键 page_down"""
    
    tab=DP.browser.latest_tab
    result=tab.actions.type(Keys.PAGE_DOWN)
    return result

@mcp.tool()
def page_up( ) -> Any:
    """向当前标签页发送按键 page_up"""
    
    tab=DP.browser.latest_tab
    result=tab.actions.type(Keys.PAGE_UP)
    return result

@mcp.tool()
def arrow_down( ) -> Any:
    """向当前标签页发送按键 arrow_down"""
    
    tab=DP.browser.latest_tab
    result=tab.actions.type(Keys.DOWN)
    return result
@mcp.tool()
def arrow_up( ) -> Any:
    """向当前标签页发送按键 arrow_up"""
    
    tab=DP.browser.latest_tab
    result=tab.actions.type(Keys.UP)
    return result

@mcp.tool()
def wait(a:int) -> Any:
    """网页等待a秒"""
    
    tab=DP.browser.latest_tab
    result=tab.wait(a)
    return result

@mcp.tool()
def get_dom_tree(depth:int) -> str:
    """获取当前标签页的DOM树结构信息
    
    Args:
        depth (int): 指定获取DOM树的深度
        
    Returns:
        str: 返回DOM树的JSON结构数据
    """
    """获取当前标签页的DOM树的信息"""
    
    tab=DP.browser.latest_tab
    tab.run_cdp("DOM.enable")
    # 获取DOM树
    result=tab.run_cdp("DOM.getDocument",depth=2)
    return result

@mcp.tool()
def query_elements_by_tagname(tagname:str) -> list:
    """获取当前标签页中所有指定标签名的元素
    
    Args:
        tagname (str): 标签名，例如 'div'
        
    Returns:
        list: 返回符合条件的元素列表
    """
    """获取当前标签页中所有指定标签名的元素"""
    
    tab=DP.browser.latest_tab
    elements=tab.eles(f'tag:{tagname}')
    return elements
@mcp.tool()
def get_input_elements_info() -> list:
    """获取当前标签页中所有input元素标签的信息,定位元素时优先使用"""    
    tab=DP.browser.latest_tab
    elements=tab.eles('t:input')    
    return elements

@mcp.tool()
def get_button_elements_info() -> list:
    """获取当前标签页中所有button元素标签的信息,定位元素时优先使用 """
    tab=DP.browser.latest_tab
    elements=tab.eles('t:button')    
    return elements

'''获取当前标签页中所有a元素标签的信息,定位元素时优先使用'''
@mcp.tool()
def get_a_elements_info() -> list:
    """获取当前标签页中所有a元素标签的信息,定位元素时优先使用"""
    
    tab=DP.browser.latest_tab
    elements=tab.eles('t:a')
    return elements

@mcp.tool()
def get_elements_by_tagname(tagname: str) -> list:
    """获取当前标签页中所有某个元素标签的信息,定位元素时优先使用 ，参数是tagname"""
    
    tab=DP.browser.latest_tab
    elements=tab.eles(f'tag:{tagname}')
    return elements

# 根据关键词，获取当前标签中的所有文本节点包含这个关键词的元素列表，返回元素列表
@mcp.tool()
def get_elements_by_keyword(keyword: str) -> list:
    """根据关键词获取当前标签页中包含该关键词的文本节点的所有元素列表  定位元素时优先使用
    
    Args:
        keyword (str): 要搜索的关键词
        
    Returns:
        list: 返回包含关键词的元素列表
    """
    tab = DP.browser.latest_tab
    # 获取所有文本节点
    text_nodes = tab('t:body').eles(keyword)
    # 筛选包含关键词的文本节点

    return text_nodes


class Use:
    @staticmethod
    def extract_text(s):
        # 直接使用正则表达式提取并返回结果
        return ''.join(re.findall(r'(?<=>)(.+?)(?=<)', s))

    @staticmethod
    def extract_attrs_value(input_string):
        # 直接返回匹配结果
        return re.findall(r'"[^"]+"', input_string)

    @staticmethod
    def extract_attrs_name(input_string):
        # 改进正则表达式以更精确地匹配属性名
        return re.findall(r'\b\w+(?==")', input_string)

    @staticmethod
    def extract_innertext(input_string):
        # 使用正则表达式简化内部文本提取
        match = re.search(r'>(.*?)<', input_string)
        return match.group(1) if match else ''

    @staticmethod
    def raw(input_str):
        input_str = input_str.strip()
        tag_name_match = re.match(r'<(\w+)', input_str)
        tag_name = tag_name_match.group(1) if tag_name_match else ''
        
        tag_attr_values = Use.extract_attrs_value(input_str)
        tag_attr_names = Use.extract_attrs_name(input_str)
        
        attr_all = ''.join([f'@@{name}={value}' for name, value in zip(tag_attr_names, tag_attr_values)])
        attr_all = attr_all.replace('"', '')
        
        txt = Use.extract_text(input_str)
        tag_txt = f'@@text()={txt}' if txt else ''
        
        transformed_str = f'tag:{tag_name}{attr_all}{tag_txt}'
        print(transformed_str)
        return transformed_str
    

def main():
    # 启动MCP服务器
    print("DrissionPage MCP server is running...")
    mcp.run(transport='stdio')   


if __name__ == "__main__":
    main()
