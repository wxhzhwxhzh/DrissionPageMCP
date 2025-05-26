#！/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any,Literal
import re
from pathlib import Path
from DrissionPage import Chromium,ChromiumOptions
from mcp.server.fastmcp import FastMCP,Image,Context

from DrissionPage.items import SessionElement, ChromiumElement, ShadowRoot, NoneElement, ChromiumTab, MixTab, ChromiumFrame
from DrissionPage.common import Keys


提示='''
DrissionPage MCP  是一个基于 DrissionPage 和 FastMCP 的浏览器自动化MCP server服务器，它提供了一系列强大的浏览器操作 API，让您能够轻松通过AI实现网页自动化操作。
点击元素前，需要先获取页面所有可点击元素的信息，使用get_all_clickable_elements()方法。
输入元素前，需要先获取页面所有可输入元素的信息，使用get_all_input_elements()方法。

'''



#region DrissionPageMCP
class DrissionPageMCP():
    def __init__(self):
        self.browser = None
        self.session = None
        self.current_tab = None
        self.current_frame = None
        self.current_shadow_root = None
        self.cdp_event_data = []
        self.response_listener_data=[]

    def test(self):
        return "test"
    def get_version(self)-> str:
        """ 获取版本号"""
        return "1.0.3"
    async def connect_or_open_browser(self, config: dict) -> dict:
        """
        用DrissionPage 打开或接管已打开的浏览器，参数通过字典传递。
        参数:
            config (dict): 可选键包括 、debug_port、browser_path、headless
        返回:
            dict: 浏览器信息
        """
        co = ChromiumOptions()
        co.set_local_port(config.get("debug_port", 9222))
        if config.get("browser_path"):
            co.set_browser_path(config["browser_path"])
        if config.get("headless", False):
            co.headless(True)

        self.browser = Chromium(co)
        tab = self.browser.latest_tab        

        return {
            "browser_address": self.browser._chromium_options.address,
            "latest_tab_title": tab.title,
            "latest_tab_id": tab.tab_id,
        }
    async def new_tab(self, url: str) -> str:
        """用DrissionPage 控制的浏览器,打开新标签页并 打开一个网址"""    
        tab = self.browser.new_tab(url)    
        return {"title": tab.title, "tab_id": tab.tab_id, "url": tab.url,"dom":self.getSimplifiedDomTree()}
    
    def wait(self, a:int) -> Any:
        """等待a秒"""
        self.browser.latest_tab.wait(a)
        return f"等待{a}秒成功"
    
    async def get(self,url:str)->str:
        """在当前标签页打开一个网址"""
        self.lastest_tab.get(url)
        tab=self.browser.latest_tab
        return {"title": tab.title, "tab_id": tab.tab_id, "url": tab.url,"dom":self.getSimplifiedDomTree()}
        
    
    #region 上传和下载
    def download_file(self, url: str, path: str, rename: str) -> str:
        """控制浏览器下载文件到指定路径
        
        Args:
            url (str): 文件的URL地址
            path (str): 文件保存的路径
            rename (str): 重命名文件名
        
        Returns:
            str: 下载结果信息
        """
        tab = self.lastest_tab
        result = tab.download(file_url=url, save_path=path, rename=rename)
        return str(result)
    
    def upload_file(self,  file_path: str) -> str:
        """点击当网页上的 <input type="file"> 元素触发上传文件的操作，上传file_path文件到当前网页
        
        Args:            
            file_path (str): 要上传的文件路径
        
        Returns:
            str: 上传结果信息，如果元素不存在则返回错误信息
        """
        x="//input[@type='file']"
        t:ChromiumTab=self.lastest_tab
        if e:= t(f"xpath:{x}"):
            t.set.upload_files(file_path)
            e.click(by_js=True)
            t.wait.upload_paths_inputted()
            return f"{file_path} 上传成功 {e}"
        else:
            return f"元素{x}不存在，无法触发上传文件"

        

    @property
    def lastest_tab(self) -> ChromiumTab:
        """获取最新标签页"""       
        return self.browser.latest_tab
    
    def send_enter(self) -> str:
        """向当前页面发送 enter 回车键"""
        tab = self.browser.latest_tab
        try:
            result = tab.actions.type(Keys.ENTER)
            return f"{tab.title} 网页发送 enter 回车键成功"
        except Exception as e:
            return f"{tab.title} 网页发送 enter 回车键失败"
        
    def getInputElementsInfo(self) -> list:
        """获取当前标签页的所有可进行输入操作的元素，对元素进行输入操作前优先使用这个方法"""
        tab = self.browser.latest_tab
        js_code='''
        const inputElements = Array.from(document.querySelectorAll('input, select, textarea, button'));
        return inputElements.filter(el => !el.disabled); // 排除禁用的元素
        '''
        elements = tab.run_js(js_code)
        return elements
    
    def click_by_xpath(self, xpath: str) -> dict:
        """通过xpath点击当前标签页中某个元素,最好先获取页面dom信息,再决定Xpath的写法"""
        
        locator = f"xpath:{xpath}"
        element = self.browser.latest_tab.ele(locator, timeout=3)
        result = {"locator": locator, "element": str(element), "click_result": element.click()}
        return result
    
    def click_by_containing_text(self, content: str, index: int = None) -> any:
        """
        根据包含指定文本的方式点击网页元素。
        
        参数：
            content: 要查找的文本内容。
            index: 当匹配到多个元素时指定要点击的索引，默认不指定。

        返回：
            点击结果说明，或错误提示。
        """
        
        # 获取包含指定文本的所有元素，等待最多 3 秒
        elements = self.browser.latest_tab.eles(content, timeout=3)

        # 如果没有匹配到任何元素，返回错误提示
        if len(elements) == 0:
            return f"元素{content}不存在，需要getInputElementsInfo先获取元素信息"
        
        # 如果只找到一个元素，直接点击它
        if len(elements) == 1:
            self.lastest_tab(content).click()
            return f" 点击成功"
        
        # 如果找到多个元素
        if len(elements) > 1:
            # 如果未指定 index，提示用户提供索引
            if index is None:
                return f"元素{content}存在多个，请调整 index 参数，index=0表示第一个元素，{elements}"
            else:
                # 根据指定索引点击对应的元素
                elements[index].click()
                return f" 点击成功"
  
        
    
    def input_by_xapth(self, xpath: str, input_value: str, clear_first: bool = True) -> Any:
        """通过xpath给当前标签页中某个元素输入内容，最好先判断元素是否存在
        
        Args:
            xpath (str): 元素的XPath表达式
            input_value (str): 要输入的内容
            clear_first (bool): 是否先清除已有内容，默认为True
        
        Returns:
            Any: 输入操作的结果，如果元素不存在则返回错误信息
        """
        locator = f"xpath:{xpath}"
        if e := self.browser.latest_tab.ele(locator, timeout=4):
            result = {"locator": locator, "result": e.input(input_value, clear=clear_first)}
            return result
        else:
            return f"元素{locator}不存在，需要getInputElementsInfo先获取元素信息"

    def get_body_text(self) -> str:
        """获取当前标签页的body的文本内容"""
        
        tab = self.browser.latest_tab
        body_text = tab('t:body').text
        return body_text
    def run_js(self, js_code: str) -> Any:
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
        tab = self.browser.latest_tab
        result = tab.run_js(js_code)
        return result
    
    def run_cdp( self,cmd, **cmd_args) -> Any:
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
        result=self.browser.latest_tab.run_cdp(cmd, **cmd_args)
        return result
    def listen_cdp_event(self,event_name: str) -> any:
        """设置监听CDP事件
        
         应该先运行cdp  命令 激活对应的域，比如  Network.enable
        """
        # b=Chromium(debug_port)
        def r(**event):
            self.cdp_event_data.append({"event_name": event_name, "event_data": event})

        try:
            self.browser.latest_tab.driver.set_callback(event_name, r)
            return f"CDP event callback for '{event_name}' set successfully."
        except Exception as e:
            return e

    def get_cdp_event_data(self) -> list:
        """获取CDP事件回调函数收集到的数据"""
        return self.cdp_event_data  



    #region 监听网页接收的数据包  
    
    def get_url_with_response_listener(self,
        tab_url: str,
        mimeType: Literal[
            # 文本类
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/plain",
            "text/xml",
            "text/csv",
            "application/json",
            
            # 应用类
            "application/octet-stream",
            "application/zip",
            "application/pdf",    
            "multipart/form-data",
            "application/xml",
            
            # 图片类
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "image/x-icon",
            
            # 音视频类
            "audio/mpeg",
            "audio/ogg",
            "video/mp4",
            "video/webm",
            "video/ogg"
        ],
        url_include: str = "."        
    ) -> any:
        '''
        开启一个新的标签页，设置监听，访问tab_url,
        tab_url: 被监听的标签页的url
        mimeType: 需要监听的接收的数据包的mimeType类型
        url_include: 需要监听的接收的数据包的url包含的关键字
        refresh: 是否刷新页面,
        '''
        t = self.browser.new_tab(tab_url)      

        t.run_cdp("Network.enable")

        def r(**event):
            _url = event.get("response", {}).get("url", "")
            _mimeType = event.get("response", {}).get("mimeType", "")
            
            if mimeType in _mimeType and url_include in _url:
                self.response_listener_data.append({
                    "event_name": "Network.responseReceived",
                    "event_data": event
                })
        
        t.driver.set_callback("Network.responseReceived", r)
        t.get(tab_url)
        
        return f"开启监听{tab_url}, 数据包url包含关键字：{url_include}，mimeType：{mimeType}"
    

    
    def response_listener_stop(self,clear_data:bool=False) -> str:
        """关闭监听网页发送的数据包"""
        t=self.browser.latest_tab
        t.run_cdp("Network.disable")
        if clear_data:
            self.response_listener_data = []
        return f"监听网页发送的数据包关闭成功 ,是否清空数据: {clear_data}"

    
    def get_response_listener_data(self) -> list:
        """获取监听到的数据,返回数据列表"""
        return self.response_listener_data

    def get_current_tab_screenshot(self) -> bytes:
        """
        获取当前标签页的网页截图   
        
        Returns:
            bytes: 截图的二进制数据
        """
        t:ChromiumTab=self.browser.latest_tab
        screenshot=t.get_screenshot(as_bytes='jpeg')
        return screenshot
    
    def get_current_tab_screenshot_as_file(self,path:str=".",name:str="screenshot.png") -> str:
        """
        获取当前标签页的屏幕截图并保存为文件
        
        Args:
            path (str): 截图保存路径，默认为当前目录
        
        Returns:
            str: 截图的文件路径
        """ 

        screenshot=self.browser.latest_tab.get_screenshot(path=path,name=name)
        return screenshot 
    
    def get_current_tab_info(self) -> dict:
        """获取当前标签页的信息,包括url, title,  id"""
        tab =self.browser.latest_tab
        info = {
            "url": tab.url,
            "title": tab.title,          
            "id": tab.tab_id,
        }
        return info
    
    def send_key(self, key: Literal["Enter, Backspace, HOME, END, PAGE_UP, PAGE_DOWN, DOWN, UP, LEFT, RIGHT, ESC, Ctrl+C, Ctrl+V, Ctrl+A, Delete"]) -> str:
        """向当前标签页发送特殊按键"""
        tab = self.browser.latest_tab
        k={"Enter": Keys.ENTER,
           "Backspace": Keys.BACKSPACE,
           "HOME": Keys.HOME,
           "END": Keys.END,
           "PAGE_UP": Keys.PAGE_UP,
           "PAGE_DOWN": Keys.PAGE_DOWN,          
           "DOWN": Keys.DOWN,
           "UP": Keys.UP,
           "LEFT": Keys.LEFT,
           "RIGHT": Keys.RIGHT,
           "ESC": Keys.ESCAPE,
           "Ctrl+C": Keys.CTRL_C,
           "Ctrl+V": Keys.CTRL_V,
           "Ctrl+A": Keys.CTRL_A,
           "Delete": Keys.DELETE,}
        try:
            result = tab.actions.type(k.get(key))
            return f"{tab.title} 网页发送 {key} 键成功"
        except Exception as e:
            return f"{tab.title} 网页发送 {key} 键失败"
    
    def getSimplifiedDomTree(self) -> dict:
        """获取当前标签页的简化版DOM树"""
        from CodeBox import domTreeToJson
        tab = self.browser.latest_tab
        dom_tree = tab.run_js(domTreeToJson)
        return dom_tree
 
    #region 拖动

    def move_to(self,xpath:str) -> dict:
        """鼠标移动悬停到指定xpath的元素上"""
        tab = self.browser.latest_tab
        locator = f"xpath:{xpath}"
        element = tab.ele(locator, timeout=3)
        if element:
            element.hover()
            result = {"locator": locator, "element": str(element)}
            return result
        else:
            return f"元素{locator}不存在，需要getSimplifiedDomTree先获取元素信息"
    def drag(self,xpath:str, offset_x: int, offset_y: int, duration: int = 1000) -> dict:
    
        """
        将元素拖动到指定偏移位置
        
        Args:
            xpath: 要拖动的元素xpath路径
            offset_x: x轴偏移量(像素)
            offset_y: y轴偏移量(像素)
            duration: 拖动持续时间(毫秒)，默认为1000
        
        Returns:
            dict: 包含偏移量和持续时间的字典，格式为{"offset_x": int, "offset_y": int, "duration": int}
            或 str: 当元素不存在时返回错误信息
        
        Raises:
            无显式抛出异常，但内部可能因元素不存在而返回错误信息
        """
        tab = self.browser.latest_tab
        if e:=tab.ele(f'xpath:{xpath}', timeout=3):
            tab.actions.move_to(e).wait(0.5).hold().move(offset_x, offset_y).release()
            result = {"offset_x": offset_x, "offset_y": offset_y, "duration": duration}
            return result
        else:
            return f"元素{xpath}不存在，需要getSimplifiedDomTree先获取元素信息"

#region 初始化mcp
mcp = FastMCP("DrissionPageMCP", log_level="ERROR",instructions=提示)
b=DrissionPageMCP()

mcp.add_tool(b.get_version)
mcp.add_tool(b.connect_or_open_browser)
mcp.add_tool(b.new_tab)
mcp.add_tool(b.wait)
mcp.add_tool(b.get)
mcp.add_tool(b.download_file)
mcp.add_tool(b.upload_file)
mcp.add_tool(b.send_enter)
mcp.add_tool(b.getInputElementsInfo)
mcp.add_tool(b.click_by_xpath)
mcp.add_tool(b.click_by_containing_text)
mcp.add_tool(b.input_by_xapth)
mcp.add_tool(b.get_body_text)
mcp.add_tool(b.run_js)
mcp.add_tool(b.run_cdp)
mcp.add_tool(b.listen_cdp_event)
mcp.add_tool(b.get_cdp_event_data)
mcp.add_tool(b.get_url_with_response_listener)
mcp.add_tool(b.response_listener_stop)
mcp.add_tool(b.get_response_listener_data)
mcp.add_tool(b.get_current_tab_screenshot)
mcp.add_tool(b.get_current_tab_screenshot_as_file)
mcp.add_tool(b.get_current_tab_info) 
mcp.add_tool(b.send_key)
mcp.add_tool(b.getSimplifiedDomTree) 

mcp.add_tool(b.move_to)
mcp.add_tool(b.drag)

#region 保存数据到sqlite
from ToolBox import save_dict_to_sqlite
mcp.add_tool(save_dict_to_sqlite)




def main():
    # 启动MCP服务器
    print("DrissionPage MCP server is running...")
    mcp.run(transport='stdio')   


if __name__ == "__main__":
    main()
