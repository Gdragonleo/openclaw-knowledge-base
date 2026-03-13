#!/usr/bin/osascript
# 微信自动发送文件脚本
# 用法: osascript wechat_send_file.applescript "联系人姓名" "/path/to/file.pdf"

on run argv
    set contactName to item 1 of argv
    set filePath to item 2 of argv
    
    tell application "WeChat"
        activate
    end tell
    
    delay 1
    
    tell application "System Events"
        tell process "WeChat"
            # 打开搜索 (Command + F)
            keystroke "f" using command down
            delay 0.5
            
            # 输入联系人姓名
            keystroke contactName
            delay 1
            
            # 按回车选择第一个结果
            keystroke return
            delay 1
            
            # 发送文件 (Command + Shift + U)
            keystroke "u" using {command down, shift down}
            delay 1
            
            # 输入文件路径 (Command + Shift + G)
            keystroke "g" using {command down, shift down}
            delay 0.5
            
            # 输入完整路径
            keystroke filePath
            delay 0.5
            
            # 确认路径
            keystroke return
            delay 0.5
            
            # 确认发送
            keystroke return
            delay 1
        end tell
    end tell
    
    return "文件发送成功"
end run
